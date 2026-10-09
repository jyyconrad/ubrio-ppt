#!/usr/bin/env python3
"""Preflight a content SVG: expand icons, input gate, native slots, color warnings."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from drawingml.pipeline import validate_svg_drawingml  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate SVG DrawingML without converting to PPTX")
    parser.add_argument("--svg", required=True)
    parser.add_argument("--mode", choices=("fast", "full"), default="fast")
    parser.add_argument("--native-data")
    parser.add_argument("--assets-dir")
    parser.add_argument("--allow-framework-chrome", action="store_true")
    parser.add_argument("--palette-json", help="optional style_manifest snapshot JSON")
    args = parser.parse_args(argv)
    svg_path = Path(args.svg)
    native = None
    if args.native_data:
        native = json.loads(Path(args.native_data).read_text(encoding="utf-8"))
    snapshot = None
    if args.palette_json:
        snapshot = json.loads(Path(args.palette_json).read_text(encoding="utf-8"))
    report = validate_svg_drawingml(
        svg_path=svg_path,
        mode=args.mode,
        allow_framework_chrome=args.allow_framework_chrome,
        native_data=native,
        style_manifest_snapshot=snapshot,
        assets_dir=Path(args.assets_dir) if args.assets_dir else svg_path.parent,
    )
    public = {
        key: value
        for key, value in report.items()
        if key not in {"expanded_svg", "stripped_svg"}
    }
    json.dump(public, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    return 0 if report.get("ok") else 2


if __name__ == "__main__":
    raise SystemExit(main())
