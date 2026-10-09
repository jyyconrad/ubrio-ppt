#!/usr/bin/env python3
"""Check that a page SVG actually draws its declared dominant shape."""
from __future__ import annotations

import argparse
import json
import math
import xml.etree.ElementTree as ET


def _local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _role(elem: ET.Element) -> str:
    return (elem.get("data-role") or "").strip()


def _texts(elem: ET.Element) -> list[ET.Element]:
    return [node for node in elem.iter() if _local(node.tag) == "text" and _content(node)]


def _content(elem: ET.Element) -> str:
    return "".join(elem.itertext()).strip()


def _panel_box(panel: ET.Element) -> tuple[float, float, float, float] | None:
    if any(node.get("transform") for node in panel.iter()):
        return None
    rect = next((node for node in panel.iter() if _local(node.tag) == "rect"), None)
    if rect is None:
        return None
    try:
        bounds = tuple(float(rect.get(key, "0")) for key in ("x", "y", "width", "height"))
    except ValueError:
        return None
    if not all(math.isfinite(value) for value in bounds) or bounds[2] <= 0 or bounds[3] <= 0:
        return None
    return bounds


def check_shape_picture(dominant: str, svg: str) -> list[str]:
    missing: list[str] = []
    try:
        root = ET.fromstring(svg)
    except ET.ParseError:
        return ["svg_parse"]

    if dominant == "左右对照":
        panels = [elem for elem in root.iter() if _role(elem) == "comparison-panel"]
        tables = [elem for elem in root.iter() if _role(elem) == "native-table-slot"]
        if len(panels) != 2 or any(
            not any(len(_content(node)) >= 8 for node in _texts(panel)) for panel in panels
        ):
            missing.append("comparison_collapsed_to_table" if tables else "comparison_panels")
        if len(panels) == 2:
            boxes = [_panel_box(panel) for panel in panels]
            if any(box is None for box in boxes):
                missing.append("comparison_panel_geometry")
            else:
                left, right = sorted(boxes, key=lambda box: box[0])
                overlap = min(left[1] + left[3], right[1] + right[3]) - max(left[1], right[1])
                if left[0] + left[2] > right[0] or overlap < min(left[3], right[3]) / 2:
                    missing.append("comparison_not_side_by_side")

    if dominant == "流程断点":
        steps = [elem for elem in root.iter() if _role(elem) == "process-step"]
        if len(steps) < 3 or any(
            not any(len(_content(node)) >= 8 for node in _texts(step)) for step in steps
        ):
            missing.append("process_step_sentence")

    for panel in root.iter():
        if _role(panel) != "evidence-panel":
            continue
        rect = next((node for node in panel.iter() if _local(node.tag) == "rect"), None)
        if rect is None:
            continue
        try:
            top = float(rect.get("y") or 0)
            height = float(rect.get("height") or rect.get("h") or 0)
        except ValueError:
            continue
        if height < 220:
            continue
        baselines: list[float] = []
        for node in _texts(panel):
            try:
                baselines.append(float(node.get("y") or 0))
            except ValueError:
                continue
        if baselines and max(baselines) < top + 0.4 * height:
            missing.append("panel_text_top_heavy")
    return missing


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dominant", required=True)
    parser.add_argument("--svg", required=True)
    args = parser.parse_args()
    svg = open(args.svg, encoding="utf-8").read()
    missing = check_shape_picture(args.dominant, svg)
    print(json.dumps({"ok": not missing, "missing": missing}, ensure_ascii=False))
    return 0 if not missing else 2


if __name__ == "__main__":
    raise SystemExit(main())
