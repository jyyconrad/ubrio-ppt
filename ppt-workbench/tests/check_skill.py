"""Quality gate for the integrated ppt-workbench skill tree."""

from __future__ import annotations

import hashlib
import json
import os
import re
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = (
    "SKILL.md",
    "references/materials/guide.md",
    "references/outline/guide.md",
    "references/generate/guide.md",
    "references/generate/capability-map.md",
    "references/generate/methods/gold-pages.md",
    "references/generate/gates/evidence-claim.md",
    "scripts/svg/check_deck.py",
    "scripts/svg/gates/plain_language.py",
    "references/generate/methods/icon-embed.md",
    "scripts/svg/search_icons.py",
    "references/generate/methods/image-owners.md",
    "references/generate/gold-examples-catalog.json",
    "references/merge-export/guide.md",
    "scripts/extract_materials.py",
    "scripts/svg/overlay_native_slots.py",
    "scripts/svg/write_svg.py",
    "scripts/svg/validate_svg_drawingml.py",
    "scripts/svg/render_svg_drawingml.py",
    "scripts/validate_deck_contract.py",
    "references/generate/methods/authoring-and-checks.md",
    "scripts/native.cjs",
    "scripts/inspect_pptx.py",
    "scripts/merge_export.py",
    "assets/examples/cases.json",
    "tests/verify_examples.py",
)


def _files(folder: Path) -> list[Path]:
    ignored = {"node_modules", ".venv", "__pycache__", ".pytest_cache", ".DS_Store"}
    return [
        path
        for path in folder.rglob("*")
        if path.is_file() and not any(part in ignored for part in path.relative_to(folder).parts)
    ]


def _check_original_copy(source_root: Path, relative: str, copied: str) -> list[str]:
    source = source_root / relative
    target = ROOT / copied
    if not source.exists() or not target.exists():
        return [f"missing original comparison path: {source} or {target}"]
    source_files = {path.relative_to(source) for path in _files(source)}
    target_files = {path.relative_to(target) for path in _files(target)}
    # The integrated skill exposes each historical module as a reference guide.
    # Keep the source entry byte-identical while allowing the intentional name
    # change from the old module SKILL.md to the local GUIDE.md.
    if Path("SKILL.md") in source_files and Path("GUIDE.md") in target_files:
        source_files.remove(Path("SKILL.md"))
        target_files.remove(Path("GUIDE.md"))
        source_files.add(Path("GUIDE.md"))
        target_files.add(Path("GUIDE.md"))
    errors = []
    if source_files != target_files:
        errors.append(f"original file set differs: {copied}")
    for path in source_files & target_files:
        source_path = source / ("SKILL.md" if path == Path("GUIDE.md") and (source / "SKILL.md").exists() else path)
        target_path = target / path
        if hashlib.sha256(source_path.read_bytes()).digest() != hashlib.sha256(target_path.read_bytes()).digest():
            errors.append(f"original bytes differ: {copied}/{path}")
    return errors


def check() -> dict:
    errors: list[str] = []
    warnings: list[str] = []
    for relative in REQUIRED:
        if not (ROOT / relative).exists():
            errors.append(f"missing required path: {relative}")
    if (ROOT / "modules").exists():
        errors.append("obsolete modules directory remains")

    frontmatter = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    if not re.search(r"^name: ppt-workbench$", frontmatter, re.M):
        errors.append("invalid skill name")
    if not re.search(r"^description: .+", frontmatter, re.M):
        errors.append("missing skill description")

    for path in ROOT.rglob("*.md"):
        if any(part in {"node_modules", ".venv"} for part in path.parts):
            continue
        content = path.read_text(encoding="utf-8", errors="ignore")
        if "/Users/" in content and "references/original" not in str(path):
            warnings.append(f"private path mention: {path.relative_to(ROOT)}")
        for target in re.findall(r"\[[^\]]*\]\(([^)]+)\)", content):
            target = target.strip("<>").split(' "', 1)[0]
            if not target or target.startswith("#") or urlsplit(target).scheme:
                continue
            resolved = (path.parent / unquote(target.split("#", 1)[0])).resolve()
            if not resolved.is_relative_to(ROOT):
                errors.append(f"link escapes skill: {path.relative_to(ROOT)} -> {target}")
            elif not resolved.exists():
                errors.append(f"broken link: {path.relative_to(ROOT)} -> {target}")

    source_text = os.environ.get("PPT_WORKBENCH_SOURCE_ROOT")
    if source_text:
        source_root = Path(source_text).resolve()
        comparisons = (
            ("backend/resources/agent-content/skills/file-processing", "references/materials/original/file-processing"),
            ("backend/resources/agent-content/skills/content-writing", "references/outline/original/content-writing"),
            ("backend/resources/agent-content/skills/slide-authoring", "references/generate/original/slide-authoring"),
            ("backend/resources/agent-content/skills/slide-generation-core", "references/generate/original/slide-generation-core"),
            ("backend/resources/agent-content/skills/layout-intelligence", "references/generate/original/layout-intelligence"),
        )
        for source, copied in comparisons:
            errors.extend(_check_original_copy(source_root, source, copied))

    return {
        "root": str(ROOT),
        "required_paths": len(REQUIRED),
        "errors": errors,
        "warnings": warnings,
        "checks_passed": not errors,
    }


if __name__ == "__main__":
    report = check()
    print(json.dumps(report, ensure_ascii=False, indent=2))
    raise SystemExit(0 if report["checks_passed"] else 2)
