#!/usr/bin/env python3
"""Compile a content SVG to editable native DrawingML PPTX, then overlay slots."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from drawingml.pipeline import render_svg_drawingml  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="expand → validate → strip placeholders → native PPTX → overlay"
    )
    parser.add_argument("--svg", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--native-data")
    parser.add_argument("--assets-dir")
    parser.add_argument("--palette-json")
    parser.add_argument("--canvas-format", choices=("ppt169", "auto"), default="ppt169",
                        help="auto preserves the SVG canvas, including 3:2 and 2:1 references")
    args = parser.parse_args(argv)
    snapshot = None
    if args.palette_json:
        snapshot = json.loads(Path(args.palette_json).read_text(encoding="utf-8"))
    native = Path(args.native_data) if args.native_data else None
    result = render_svg_drawingml(
        svg_path=args.svg,
        output=args.output,
        native_data=native,
        assets_dir=args.assets_dir,
        style_manifest_snapshot=snapshot,
        canvas_format=args.canvas_format,
    )
    public = {
        key: value
        for key, value in result.items()
        if key not in {"expanded_svg", "stripped_svg"}
    }
    json.dump(public, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    return 0 if result.get("ok") else 2


if __name__ == "__main__":
    raise SystemExit(main())
