#!/usr/bin/env python3
"""Write a complete 1280x720 content SVG, then run a fast local gate."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from drawingml.pipeline import write_svg_file  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Write source.svg and fast-validate the content layer")
    parser.add_argument("--output", required=True, help="destination source.svg")
    parser.add_argument("--svg-file", help="read SVG from this file instead of stdin")
    parser.add_argument("--layout-decision", help="optional layout-decision.v1 JSON")
    parser.add_argument("--no-validate", action="store_true")
    args = parser.parse_args(argv)
    if args.svg_file:
        svg_text = Path(args.svg_file).read_text(encoding="utf-8")
    else:
        svg_text = sys.stdin.read()
    layout = None
    if args.layout_decision:
        layout = json.loads(Path(args.layout_decision).read_text(encoding="utf-8"))
    result = write_svg_file(
        output=args.output,
        svg_text=svg_text,
        validate=not args.no_validate,
        layout_decision=layout,
    )
    json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    return 0 if result.get("ok") else 2


if __name__ == "__main__":
    raise SystemExit(main())
