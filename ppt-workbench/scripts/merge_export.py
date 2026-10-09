#!/usr/bin/env python3
"""Select, reorder, duplicate and merge PPTX slides; export PPTX to PDF/PNG."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
import posixpath
from pathlib import Path
from pathlib import PurePosixPath
from urllib.parse import unquote, urlsplit
from xml.etree import ElementTree

from pptx import Presentation


class ToolError(RuntimeError):
    pass


MAX_ZIP_MEMBERS = 10_000
MAX_COMPRESSED_BYTES = 256 * 1024 * 1024
MAX_EXPANDED_BYTES = 1024 * 1024 * 1024
MAX_SELECTED_PAGES = 2_000
UNSUPPORTED_RELATIONSHIP_MARKERS = ("/oleObject", "/video", "/audio")
PNG_OUTPUT_NAME = re.compile(r"slide-\d+\.png")
RELATIONSHIP_NAMESPACE = "http://schemas.openxmlformats.org/package/2006/relationships"
CONTENT_TYPES_NAMESPACE = "http://schemas.openxmlformats.org/package/2006/content-types"
ORPHAN_NOTES_SLIDE = re.compile(r"ppt/notesSlides/notesSlide\d+\.xml")
ORPHAN_ROOT_SLIDE = re.compile(r"ppt/slides/slide\d+\.xml")


def _resolve(name: str, explicit: str | None, candidates: tuple[str, ...]) -> str:
    if explicit:
        path = shutil.which(explicit) or explicit
        if Path(path).is_file():
            return str(Path(path).resolve())
        raise ToolError(f"{name} not found: {explicit}")
    for candidate in candidates:
        path = shutil.which(candidate)
        if path:
            return path
        if Path(candidate).is_file():
            return candidate
    raise ToolError(f"{name} not found; install the declared dependency or pass its path")


def _output_path(value: str, overwrite: bool) -> Path:
    path = Path(value).expanduser().resolve()
    if path.exists() and not overwrite:
        raise ToolError(f"output exists (use --overwrite only with explicit authorization): {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def _publish_file(staged: Path, output: Path, overwrite: bool) -> None:
    if overwrite:
        os.replace(staged, output)
        return
    try:
        os.link(staged, output)
    except FileExistsError as exc:
        raise ToolError(f"output appeared during conversion; refusing to overwrite: {output}") from exc
    staged.unlink()


def _validate_png_output_dir(output_dir: Path, input_path: Path, overwrite: bool) -> None:
    if output_dir.suffix:
        raise ToolError("PNG output must be a directory path")
    if output_dir == input_path or output_dir in input_path.parents:
        raise ToolError("PNG output directory must not contain the input PPTX")
    if not output_dir.exists():
        return
    if not overwrite:
        raise ToolError(f"output exists (use --overwrite only with explicit authorization): {output_dir}")
    if not output_dir.is_dir():
        raise ToolError(f"PNG output exists and is not a directory: {output_dir}")
    unrelated = [entry.name for entry in output_dir.iterdir() if not entry.is_file() or not PNG_OUTPUT_NAME.fullmatch(entry.name)]
    if unrelated:
        preview = ", ".join(sorted(unrelated)[:5])
        raise ToolError(f"PNG output directory contains unrelated files; refusing replacement: {preview}")


def _inspect_package(archive: zipfile.ZipFile, path: Path) -> None:
    members = archive.infolist()
    if len(members) > MAX_ZIP_MEMBERS:
        raise ToolError(f"PPTX has too many ZIP members ({len(members)} > {MAX_ZIP_MEMBERS}): {path}")
    compressed = sum(member.compress_size for member in members)
    expanded = sum(member.file_size for member in members)
    if compressed > MAX_COMPRESSED_BYTES or expanded > MAX_EXPANDED_BYTES:
        raise ToolError(
            f"PPTX exceeds size bounds (compressed={compressed}, expanded={expanded}): {path}"
        )
    names = {member.filename for member in members}
    if "ppt/vbaProject.bin" in names:
        raise ToolError(f"macro-enabled content is not accepted: {path}")
    media_extensions = {".mp4", ".mov", ".avi", ".mp3", ".wav", ".m4a"}
    if any(
        name.startswith("ppt/media/") and Path(name).suffix.lower() in media_extensions
        for name in names
    ):
        raise ToolError(f"audio/video media is outside the supported static scope: {path}")
    for member in members:
        if not member.filename.endswith(".rels"):
            continue
        try:
            root = ElementTree.fromstring(archive.read(member))
        except ElementTree.ParseError as exc:
            raise ToolError(f"invalid relationship XML in {path}: {member.filename}") from exc
        for relationship in root:
            relation_type = relationship.attrib.get("Type", "")
            if relationship.attrib.get("TargetMode") == "External":
                raise ToolError(f"external relationship is outside the supported static scope: {path}")
            if any(marker in relation_type for marker in UNSUPPORTED_RELATIONSHIP_MARKERS):
                raise ToolError(f"OLE/audio/video relationship is outside the supported static scope: {path}")


def _relationship_owner(rels_path: str) -> str | None:
    if rels_path == "_rels/.rels":
        return ""
    marker = "/_rels/"
    if marker not in rels_path or not rels_path.endswith(".rels"):
        return None
    parent, filename = rels_path.split(marker, 1)
    return str(PurePosixPath(parent) / filename.removesuffix(".rels"))


def _resolve_relationship_target(owner: str, target: str) -> str:
    parsed = urlsplit(target)
    if parsed.scheme or parsed.netloc:
        raise ToolError(f"unexpected external relationship target: {target}")
    target_path = unquote(parsed.path)
    base = "" if target_path.startswith("/") else posixpath.dirname(owner)
    resolved = posixpath.normpath(posixpath.join(base, target_path.lstrip("/")))
    if resolved == ".." or resolved.startswith("../") or resolved.startswith("/"):
        raise ToolError(f"relationship target escapes package root: {target}")
    return resolved


def _relationships(archive: zipfile.ZipFile, rels_path: str) -> list[tuple[str, str]]:
    owner = _relationship_owner(rels_path)
    if owner is None:
        return []
    try:
        root = ElementTree.fromstring(archive.read(rels_path))
    except ElementTree.ParseError as exc:
        raise ToolError(f"invalid relationship XML: {rels_path}") from exc
    relationships: list[tuple[str, str]] = []
    for relationship in root.findall(f"{{{RELATIONSHIP_NAMESPACE}}}Relationship"):
        if relationship.attrib.get("TargetMode") == "External":
            continue
        target = relationship.attrib.get("Target")
        if target:
            relationships.append((owner, _resolve_relationship_target(owner, target)))
    return relationships


def _rels_path_for_part(part: str) -> str:
    path = PurePosixPath(part)
    return str(path.parent / "_rels" / f"{path.name}.rels")


def _reachable_parts(archive: zipfile.ZipFile) -> set[str]:
    names = set(archive.namelist())
    reachable: set[str] = set()
    pending = [target for _, target in _relationships(archive, "_rels/.rels")]
    while pending:
        part = pending.pop()
        if part in reachable or part not in names:
            continue
        reachable.add(part)
        rels_path = _rels_path_for_part(part)
        if rels_path in names:
            reachable.add(rels_path)
            pending.extend(target for _, target in _relationships(archive, rels_path))
    reachable.add("_rels/.rels")
    return reachable


def _remove_content_type_overrides(content: bytes, removed: set[str]) -> bytes:
    root = ElementTree.fromstring(content)
    for override in list(root.findall(f"{{{CONTENT_TYPES_NAMESPACE}}}Override")):
        if override.attrib.get("PartName", "").lstrip("/") in removed:
            root.remove(override)
    ElementTree.register_namespace("", CONTENT_TYPES_NAMESPACE)
    return ElementTree.tostring(root, encoding="utf-8", xml_declaration=True)


def _cleanup_orphan_root_slides(path: Path) -> list[str]:
    with zipfile.ZipFile(path) as archive:
        names = set(archive.namelist())
        reachable = _reachable_parts(archive)
        orphan_slides = {
            name for name in names if ORPHAN_ROOT_SLIDE.fullmatch(name) and name not in reachable
        }
        removed_parts = set(orphan_slides)
        for slide in orphan_slides:
            rels_path = _rels_path_for_part(slide)
            if rels_path not in names:
                continue
            for _, target in _relationships(archive, rels_path):
                if ORPHAN_NOTES_SLIDE.fullmatch(target) and target not in reachable:
                    removed_parts.add(target)
        removed = removed_parts | {
            _rels_path_for_part(part) for part in removed_parts if _rels_path_for_part(part) in names
        }
        if not removed:
            return []
        entries = [(info, archive.read(info)) for info in archive.infolist() if info.filename not in removed]
    with tempfile.NamedTemporaryFile(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent, delete=False
    ) as handle:
        rewritten = Path(handle.name)
    try:
        with zipfile.ZipFile(rewritten, "w") as output:
            for info, content in entries:
                if info.filename == "[Content_Types].xml":
                    content = _remove_content_type_overrides(content, removed_parts)
                output.writestr(info, content)
        os.replace(rewritten, path)
    finally:
        rewritten.unlink(missing_ok=True)
    return sorted(removed)


def _validate_all_relationship_targets(path: Path) -> None:
    with zipfile.ZipFile(path) as archive:
        names = set(archive.namelist())
        for rels_path in sorted(name for name in names if name.endswith(".rels")):
            owner = _relationship_owner(rels_path)
            if owner is None:
                continue
            if owner and owner not in names:
                raise ToolError(f"relationship part has no owner: {rels_path} -> {owner}")
            for _, target in _relationships(archive, rels_path):
                if target not in names:
                    raise ToolError(f"missing relationship target: {rels_path} -> {target}")


def _select_root_template(pages: list[dict[str, object]]) -> str:
    paths = list(dict.fromkeys(str(page["path"]) for page in pages))
    for path_text in paths:
        with zipfile.ZipFile(path_text) as archive:
            if any(
                name.startswith("ppt/notesMasters/notesMaster") and name.endswith(".xml")
                for name in archive.namelist()
            ):
                return path_text
    return paths[0]


def _inspect_pptx(path: Path) -> tuple[int, tuple[int, int]]:
    if not path.is_file() or path.suffix.lower() != ".pptx":
        raise ToolError(f"input must be an existing .pptx file: {path}")
    try:
        with zipfile.ZipFile(path) as archive:
            _inspect_package(archive, path)
        deck = Presentation(str(path))
    except ToolError:
        raise
    except Exception as exc:
        raise ToolError(f"cannot read PPTX (damaged, encrypted, or unsupported): {path}: {exc}") from exc
    return len(deck.slides), (deck.slide_width, deck.slide_height)


def _parse_page_spec(spec: str, count: int) -> list[int]:
    if spec.lower() == "all":
        return list(range(count))
    pages: list[int] = []
    for token in spec.split(","):
        token = token.strip()
        if not token:
            raise ToolError(f"empty page token in selection: {spec}")
        if "-" in token:
            start_text, end_text = token.split("-", 1)
            start, end = int(start_text), int(end_text)
            if start < 1 or end > count:
                raise ToolError(f"page selection out of range 1-{count}: {token}")
            if start > end:
                raise ToolError(f"descending range is not supported; list pages explicitly: {token}")
            if end - start + 1 > MAX_SELECTED_PAGES:
                raise ToolError(
                    f"page range exceeds limit ({end - start + 1} > {MAX_SELECTED_PAGES}): {token}"
                )
            pages.extend(range(start - 1, end))
        else:
            page = int(token)
            if page < 1 or page > count:
                raise ToolError(f"page selection out of range 1-{count}: {token}")
            pages.append(page - 1)
    if any(index < 0 or index >= count for index in pages):
        raise ToolError(f"page selection out of range 1-{count}: {spec}")
    return pages


def _selection_plan(values: list[str] | None) -> tuple[list[dict[str, object]], tuple[int, int]]:
    if not values:
        raise ToolError("at least one --input FILE[:PAGES] is required")
    requested: list[dict[str, object]] = []
    expected_size: tuple[int, int] | None = None
    for value in values:
        file_text, separator, page_spec = value.rpartition(":")
        if not separator or not file_text.lower().endswith(".pptx"):
            file_text, page_spec = value, "all"
        path = Path(file_text).expanduser().resolve()
        count, size = _inspect_pptx(path)
        if expected_size is None:
            expected_size = size
        elif size != expected_size:
            raise ToolError(
                f"slide dimension mismatch: {path} is {size}, expected {expected_size}; no implicit scaling"
            )
        for index in _parse_page_spec(page_spec, count):
            requested.append(
                {"path": str(path), "source_page": index + 1, "output_page": len(requested) + 1}
            )
    if not requested or expected_size is None:
        raise ToolError("selection contains no pages")
    if len(requested) > MAX_SELECTED_PAGES:
        raise ToolError(f"selection exceeds page limit ({len(requested)} > {MAX_SELECTED_PAGES})")
    return requested, expected_size


def preflight(args: argparse.Namespace) -> dict[str, object]:
    pages, size = _selection_plan(args.input)
    return {
        "operation": "preflight",
        "merge_available": True,
        "slides": len(pages),
        "slide_size_emu": {"width": size[0], "height": size[1]},
        "pages": pages,
    }


def merge(args: argparse.Namespace) -> dict[str, object]:
    pages, expected_size = _selection_plan(args.input)
    output = _output_path(args.output, args.overwrite)
    if output.suffix.lower() != ".pptx":
        raise ToolError("merged output must end in .pptx")
    node = _resolve("Node.js", args.node, ("node",))
    script = Path(__file__).with_name("merge_pptx.cjs").resolve()
    package_root = script.parent.parent
    if not (package_root / "node_modules" / "pptx-automizer").is_dir():
        raise ToolError(
            "pptx-automizer is not installed in this skill; run the pinned local package install first"
        )
    input_paths = {Path(str(page["path"])).resolve() for page in pages}
    if output in input_paths:
        raise ToolError("output must not be the same path as any input, even with --overwrite")
    with tempfile.TemporaryDirectory(prefix=".pptx-automizer-", dir=output.parent) as temp_text:
        staged_output = Path(temp_text) / "merged.pptx"
        job = Path(temp_text) / "job.json"
        job.write_text(
            json.dumps(
                {
                    "pages": pages,
                    "root": _select_root_template(pages),
                    "output": str(staged_output),
                }
            ),
            encoding="utf-8",
        )
        completed = subprocess.run(
            [node, str(script), str(job)],
            cwd=package_root,
            capture_output=True,
            text=True,
            timeout=args.timeout,
            check=False,
        )
        if completed.returncode != 0 or not staged_output.is_file():
            detail = (completed.stderr or completed.stdout).strip()[-1500:]
            raise ToolError(f"pptx-automizer merge failed (exit {completed.returncode}): {detail}")
        removed_orphans = _cleanup_orphan_root_slides(staged_output)
        _validate_all_relationship_targets(staged_output)
        count, size = _inspect_pptx(staged_output)
        if count != len(pages) or size != expected_size:
            raise ToolError("merged output failed page-count or dimension verification")
        _publish_file(staged_output, output, args.overwrite)
    return {
        "operation": "merge",
        "output": str(output),
        "slides": count,
        "engine": "pptx-automizer@0.9.3",
        "removed_orphan_parts": removed_orphans,
    }


def _convert_to_pdf(input_path: Path, output: Path, soffice: str, timeout: int) -> None:
    with tempfile.TemporaryDirectory(prefix="ppt-export-") as temp_text:
        temp = Path(temp_text)
        profile = temp / "profile"
        command = [
            soffice,
            "--headless",
            "--nologo",
            "--nodefault",
            "--nolockcheck",
            "--norestore",
            f"-env:UserInstallation={profile.as_uri()}",
            "--convert-to",
            "pdf:impress_pdf_Export",
            "--outdir",
            str(temp),
            str(input_path),
        ]
        completed = subprocess.run(command, capture_output=True, text=True, timeout=timeout, check=False)
        generated = temp / f"{input_path.stem}.pdf"
        if completed.returncode != 0 or not generated.is_file():
            detail = (completed.stderr or completed.stdout).strip()[-1000:]
            raise ToolError(f"LibreOffice PDF export failed (exit {completed.returncode}): {detail}")
        shutil.move(str(generated), output)


def _pdf_page_count(path: Path) -> int:
    try:
        from pypdf import PdfReader
    except ImportError as exc:
        raise ToolError(
            "optional PDF verification dependency is missing; install requirements-export.txt"
        ) from exc
    return len(PdfReader(str(path)).pages)


def export(args: argparse.Namespace) -> dict[str, object]:
    input_path = Path(args.input).expanduser().resolve()
    count, _ = _inspect_pptx(input_path)
    if args.backend != "libreoffice":
        raise ToolError(
            "no conversion backend selected; use the host's existing Office/export capability, "
            "or explicitly opt into the optional route with --backend libreoffice"
        )
    if args.format == "pdf":
        output = _output_path(args.output, args.overwrite)
        if output.suffix.lower() != ".pdf":
            raise ToolError("PDF output must end in .pdf")
        soffice = _resolve(
            "LibreOffice soffice",
            args.soffice,
            ("/Applications/LibreOffice.app/Contents/MacOS/soffice", "soffice", "libreoffice"),
        )
        with tempfile.TemporaryDirectory(prefix=".ppt-pdf-", dir=output.parent) as temp_text:
            staged = Path(temp_text) / "output.pdf"
            _convert_to_pdf(input_path, staged, soffice, args.timeout)
            actual_pages = _pdf_page_count(staged)
            if actual_pages != count:
                raise ToolError(f"PDF export produced {actual_pages} pages for {count} slides")
            _publish_file(staged, output, args.overwrite)
        return {"operation": "export", "format": "pdf", "output": str(output), "pages": count}

    output_dir = Path(args.output).expanduser().resolve()
    output_dir.parent.mkdir(parents=True, exist_ok=True)
    _validate_png_output_dir(output_dir, input_path, args.overwrite)
    soffice = _resolve(
        "LibreOffice soffice",
        args.soffice,
        ("/Applications/LibreOffice.app/Contents/MacOS/soffice", "soffice", "libreoffice"),
    )
    pdftoppm = _resolve("Poppler pdftoppm", args.pdftoppm, ("pdftoppm",))
    with tempfile.TemporaryDirectory(prefix=".ppt-png-", dir=output_dir.parent) as temp_text:
        staging = Path(temp_text) / "pages"
        staging.mkdir()
        pdf = Path(temp_text) / "source.pdf"
        _convert_to_pdf(input_path, pdf, soffice, args.timeout)
        if _pdf_page_count(pdf) != count:
            raise ToolError("intermediate PDF page count does not match the PPTX")
        prefix = staging / "slide"
        command = [pdftoppm, "-png", "-r", str(args.dpi), str(pdf), str(prefix)]
        completed = subprocess.run(command, capture_output=True, text=True, timeout=args.timeout, check=False)
        if completed.returncode != 0:
            raise ToolError(f"PNG export failed: {(completed.stderr or completed.stdout).strip()[-1000:]}")
        staged_files = sorted(staging.glob("slide-*.png"))
        if len(staged_files) != count:
            raise ToolError(f"PNG export produced {len(staged_files)} files for {count} slides")
        backup = Path(temp_text) / "previous-output"
        if output_dir.exists():
            output_dir.rename(backup)
        try:
            staging.rename(output_dir)
        except Exception:
            if backup.exists() and not output_dir.exists():
                backup.rename(output_dir)
            raise
        if backup.exists():
            shutil.rmtree(backup)
    files = sorted(str(path) for path in output_dir.glob("slide-*.png"))
    return {"operation": "export", "format": "png", "output": str(output_dir), "pages": count, "files": files}


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description=__doc__)
    subparsers = root.add_subparsers(dest="command", required=True)
    preflight_parser = subparsers.add_parser(
        "preflight", help="read-only PPTX inspection and ordered page-selection plan"
    )
    preflight_parser.add_argument(
        "--input", action="append", help="FILE[:PAGES], 1-based; repeat inputs/pages in output order"
    )
    preflight_parser.set_defaults(run=preflight)

    merge_parser = subparsers.add_parser("merge", help="select/reorder/duplicate/merge PPTX pages")
    merge_parser.add_argument(
        "--input", action="append", help="FILE[:PAGES], 1-based; repeat in required output order"
    )
    merge_parser.add_argument("--output", required=True)
    merge_parser.add_argument("--overwrite", action="store_true")
    merge_parser.add_argument("--node")
    merge_parser.add_argument("--timeout", type=int, default=180)
    merge_parser.set_defaults(run=merge)

    export_parser = subparsers.add_parser("export", help="export a PPTX independently to PDF or PNG")
    export_parser.add_argument("--input", required=True)
    export_parser.add_argument("--format", choices=("pdf", "png"), required=True)
    export_parser.add_argument("--backend", choices=("libreoffice",))
    export_parser.add_argument("--output", required=True)
    export_parser.add_argument("--dpi", type=int, default=144)
    export_parser.add_argument("--overwrite", action="store_true")
    export_parser.add_argument("--soffice")
    export_parser.add_argument("--pdftoppm")
    export_parser.add_argument("--timeout", type=int, default=180)
    export_parser.set_defaults(run=export)
    return root


def main() -> int:
    try:
        result = parser().parse_args()
        print(json.dumps(result.run(result), ensure_ascii=False, indent=2))
        return 0
    except (ToolError, ValueError, subprocess.TimeoutExpired) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
