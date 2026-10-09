#!/usr/bin/env python3
"""Inspect SVG layers (id/tag/child_count/text excerpt). Pure ElementTree."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from xml.etree import ElementTree as ET

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from drawingml.authoring import inspect_svg_layers, validate_svg_string_for_authoring  # noqa: E402


def inspect_svg_layers_from_text(
    svg: str,
    *,
    include_text_excerpt: bool = True,
) -> tuple[list[dict], list[dict]]:
    ok, issue = validate_svg_string_for_authoring(svg)
    if not ok:
        raise ValueError((issue or {}).get("message") or "invalid svg")
    return inspect_svg_layers(ET.fromstring(svg), include_text_excerpt=include_text_excerpt)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="List SVG layer ids for patch_svg_layer")
    parser.add_argument("--svg", required=True)
    parser.add_argument("--no-excerpt", action="store_true")
    args = parser.parse_args(argv)
    svg = Path(args.svg).read_text(encoding="utf-8")
    layers, warnings = inspect_svg_layers_from_text(svg, include_text_excerpt=not args.no_excerpt)
    json.dump({"ok": True, "layers": layers, "warnings": warnings}, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
