#!/usr/bin/env python3
"""Patch one SVG layer by id: replace/append/insert_before/insert_after/remove."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from drawingml.authoring import SvgAuthoringPatchError, patch_svg_layer_text  # noqa: E402
from drawingml.pipeline import write_svg_file  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Patch a unique SVG layer id")
    parser.add_argument("--svg", required=True)
    parser.add_argument("--layer-id", required=True)
    parser.add_argument(
        "--operation",
        required=True,
        choices=("replace", "append", "insert_before", "insert_after", "remove"),
    )
    parser.add_argument("--fragment", help="svg_fragment XML (not required for remove)")
    parser.add_argument("--anchor-layer-id")
    parser.add_argument("--output", help="write patched SVG here (default: overwrite --svg)")
    parser.add_argument("--no-validate", action="store_true")
    args = parser.parse_args(argv)
    original = Path(args.svg).read_text(encoding="utf-8")
    try:
        patched, summary = patch_svg_layer_text(
            original,
            layer_id=args.layer_id,
            operation=args.operation,
            svg_fragment=args.fragment,
            anchor_layer_id=args.anchor_layer_id,
        )
    except SvgAuthoringPatchError as exc:
        json.dump(
            {"ok": False, "code": exc.code, "message": exc.message},
            sys.stdout,
            ensure_ascii=False,
            indent=2,
        )
        sys.stdout.write("\n")
        return 2
    dest = Path(args.output) if args.output else Path(args.svg)
    result = write_svg_file(output=dest, svg_text=patched, validate=not args.no_validate)
    result["patch"] = summary
    json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    return 0 if result.get("ok") else 2


if __name__ == "__main__":
    raise SystemExit(main())
