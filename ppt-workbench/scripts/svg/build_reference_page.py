#!/usr/bin/env python3
"""Bind explicit business content to one editable reference composition."""

from __future__ import annotations

import argparse
import copy
import json
import math
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT / "assets" / "visual-references" / "blue-dense" / "catalog.json"


def resources():
    from reference_layouts import mechanism_layouts, rd_layouts
    renderers = {**rd_layouts.RENDERERS, **mechanism_layouts.RENDERERS}
    defaults = {**rd_layouts.DEFAULTS, **mechanism_layouts.DEFAULTS}
    schemas = {**rd_layouts.SCHEMAS, **mechanism_layouts.SCHEMAS}
    renderers["R31"] = _crop_dashboard
    defaults["R31"] = copy.deepcopy(defaults["R10"])
    schemas["R31"] = {**schemas["R10"], "canvas": "1280x640", "derived_from": "R10",
                      "layout_reason": "同源看板的2:1放大裁切视图，不能重新排版或改数据。"}
    return renderers, defaults, schemas


def _crop_dashboard(content):
    from reference_layouts.rd_layouts import RENDERERS
    svg, native = RENDERERS["R10"](content)
    root = ET.fromstring(svg)
    root.set("width", "1280")
    root.set("height", "640")
    root.set("viewBox", "0 0 1280 640")
    # DrawingML has no viewport clipping; omit or shorten shapes outside the crop.
    crop_bottom = 639.0
    for node in list(root):
        tag = node.tag.rsplit("}", 1)[-1]
        y = float(node.get("y", node.get("cy", "0")))
        if y >= crop_bottom:
            root.remove(node)
        elif tag == "rect" and y + float(node.get("height", "0")) > crop_bottom:
            node.set("height", str(crop_bottom - y))
        elif tag in {"polygon", "circle"}:
            if tag == "circle":
                radius = float(node.get("r", "0"))
                if y + radius <= crop_bottom:
                    continue
                center_x = float(node.get("cx", "0"))
                points = [(center_x + radius * math.cos(index * math.tau / 96),
                           y + radius * math.sin(index * math.tau / 96))
                          for index in range(96)]
                node.tag = "{http://www.w3.org/2000/svg}polygon"
                for field in ("cx", "cy", "r"):
                    node.attrib.pop(field, None)
                node.set("data-cropped-circle", "true")
            else:
                numbers = [float(value) for value in node.get("points", "").replace(",", " ").split()]
                points = list(zip(numbers[::2], numbers[1::2]))
            clipped = []
            if points:
                previous = points[-1]
                for current in points:
                    previous_inside, current_inside = previous[1] <= crop_bottom, current[1] <= crop_bottom
                    if previous_inside != current_inside:
                        fraction = (crop_bottom - previous[1]) / (current[1] - previous[1])
                        clipped.append((previous[0] + fraction * (current[0] - previous[0]), crop_bottom))
                    if current_inside:
                        clipped.append(current)
                    previous = current
            area = abs(sum(first[0] * second[1] - second[0] * first[1]
                           for first, second in zip(clipped, clipped[1:] + clipped[:1]))) / 2
            if len(clipped) < 3 or area < 0.1:
                root.remove(node)
            else:
                node.set("points", " ".join(f"{x},{y}" for x, y in clipped))
    return ET.tostring(root, encoding="unicode"), native


def _check_content(actual, example, path="content"):
    """Reject missing cells before a renderer can silently use fixture defaults."""
    if isinstance(example, dict):
        if not isinstance(actual, dict):
            raise ValueError(f"{path}: expected object")
        missing = set(example) - set(actual)
        if missing:
            raise ValueError(f"{path}: missing explicit fields {sorted(missing)}")
        for key, value in example.items():
            _check_content(actual[key], value, f"{path}.{key}")
    elif isinstance(example, list):
        if not isinstance(actual, list) or len(actual) != len(example):
            raise ValueError(f"{path}: reference requires {len(example)} items")
        for index, value in enumerate(example):
            _check_content(actual[index], value, f"{path}[{index}]")
    elif isinstance(example, bool):
        if not isinstance(actual, bool):
            raise ValueError(f"{path}: expected boolean value")
    elif isinstance(example, (int, float)):
        if not isinstance(actual, (int, float)) or isinstance(actual, bool):
            raise ValueError(f"{path}: expected numeric value")
        if not math.isfinite(actual):
            raise ValueError(f"{path}: expected finite numeric value")
    elif example is not None and not isinstance(actual, type(example)):
        raise ValueError(f"{path}: expected {type(example).__name__}")
    elif isinstance(example, str) and example.strip() and not actual.strip():
        raise ValueError(f"{path}: required business text is empty")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--list", action="store_true")
    parser.add_argument("--describe")
    parser.add_argument("--reference-id")
    parser.add_argument("--content", type=Path)
    parser.add_argument("--example", action="store_true", help="explicitly use authorized synthetic fixture")
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--render", action="store_true")
    args = parser.parse_args()
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))["items"]
    if args.list:
        print(json.dumps(catalog, ensure_ascii=False, indent=2))
        return 0
    renderers, defaults, schemas = resources()
    reference_id = args.describe or args.reference_id
    if reference_id not in renderers:
        parser.error("provide a valid --describe or --reference-id from --list")
    record = next(item for item in catalog if item["id"] == reference_id)
    if args.describe:
        payload = {**record, "schema": schemas[reference_id],
                   "content_fields": list(defaults[reference_id]),
                   "reference_path": str(CATALOG.parent / "all32" / record["file"])}
        if args.example:
            payload["synthetic_example"] = defaults[reference_id]
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0
    if args.output_dir is None:
        parser.error("--output-dir is required for generation")
    if args.content:
        content = json.loads(args.content.read_text(encoding="utf-8"))
        _check_content(content, defaults[reference_id])
    elif args.example:
        content = copy.deepcopy(defaults[reference_id])
    else:
        parser.error("provide explicit --content; --example is only for authorized synthetic examples")
    svg, native = renderers[reference_id](content)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "source.svg").write_text(svg, encoding="utf-8")
    (args.output_dir / "native-data.json").write_text(json.dumps(native, ensure_ascii=False, indent=2), encoding="utf-8")
    (args.output_dir / "content.json").write_text(json.dumps(content, ensure_ascii=False, indent=2), encoding="utf-8")
    report = {"reference_id": reference_id, "reference_file": record["file"],
              "content_mode": "explicit" if args.content else "synthetic_example",
              "schema": schemas[reference_id], "visual_review": "not_performed"}
    if args.render:
        from drawingml.pipeline import render_svg_drawingml
        result = render_svg_drawingml(svg_path=args.output_dir / "source.svg",
                                     output=args.output_dir / "page.pptx",
                                     native_data=native, canvas_format="auto")
        report["render"] = {k: v for k, v in result.items() if k not in {"expanded_svg", "stripped_svg"}}
    (args.output_dir / "composition-report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if not args.render or report["render"]["ok"] else 2


if __name__ == "__main__":
    sys.exit(main())
