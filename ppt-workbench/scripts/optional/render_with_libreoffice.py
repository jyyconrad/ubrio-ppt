"""Optional LibreOffice/Poppler preview branch, independent of native authoring."""

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from inspect_pptx import inspect  # noqa: E402


def render(source, output, soffice="soffice", pdftoppm="pdftoppm", timeout=120):
    source, output = Path(source).resolve(), Path(output).resolve()
    if output.exists():
        raise ValueError("Preview output directory already exists; choose a new destination")
    inspection = inspect(source, allow_image_slide=True)
    if inspection["errors"]:
        raise ValueError("PPTX failed structural preflight: " + "; ".join(inspection["errors"]))
    office, poppler = shutil.which(soffice), shutil.which(pdftoppm)
    host_office = Path("/Applications/LibreOffice.app/Contents/MacOS/soffice")
    if sys.platform == "darwin" and soffice == "soffice" and host_office.is_file():
        office = str(host_office)
    if not office or not poppler:
        raise ValueError("Optional LibreOffice/Poppler route unavailable; use an existing host preview capability")
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="ppt-render-", dir=output.parent) as temp:
        root = Path(temp)
        src, generated, profile = root / "input.pptx", root / "output", root / "profile"
        generated.mkdir()
        shutil.copyfile(source, src)
        subprocess.run([office, f"-env:UserInstallation={profile.as_uri()}", "--headless", "--convert-to",
                        "pdf:impress_pdf_Export", "--outdir", str(generated), str(src)],
                       check=True, capture_output=True, timeout=timeout)
        pdf = generated / "input.pdf"
        if not pdf.is_file() or pdf.stat().st_size < 100:
            raise ValueError("Office did not produce a valid PDF")
        subprocess.run([poppler, "-png", "-r", "120", str(pdf), str(generated / "slide")],
                       check=True, capture_output=True, timeout=timeout)
        images = sorted(generated.glob("slide-*.png"))
        if len(images) != inspection["page_count"] or any(p.stat().st_size < 100 for p in images):
            raise ValueError("Preview image count or content is invalid")
        version = subprocess.run([office, "--version"], check=True, capture_output=True, text=True, timeout=15).stdout.strip()
        pdf.rename(generated / "slides.pdf")
        result = {"source_sha256": inspection["sha256"], "page_count": len(images), "renderer": version,
                  "visual_review": "not_performed", "powerpoint_roundtrip": "not_performed"}
        (generated / "render.json").write_text(json.dumps(result, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
        output.mkdir()
        for item in generated.iterdir():
            shutil.copyfile(item, output / item.name)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--soffice", default="soffice")
    parser.add_argument("--pdftoppm", default="pdftoppm")
    parser.add_argument("--timeout", type=int, default=120)
    args = parser.parse_args()
    try:
        print(json.dumps(render(args.input, args.output_dir, args.soffice, args.pdftoppm, args.timeout), ensure_ascii=False))
        return 0
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        print(f"Rendering incomplete: {type(exc).__name__}; check dependencies, input and output permissions", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
