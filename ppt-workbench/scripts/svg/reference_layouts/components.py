"""Data-only component scenes derived from the reference compositions."""

from __future__ import annotations

import copy
import json
from pathlib import Path
import xml.etree.ElementTree as ET

from .common import BLUE, INK, LIGHT, LINE, Svg

ROOT = Path(__file__).resolve().parents[3]
CATALOG = ROOT / "assets" / "components" / "blue-dense"
FIXED_LAYOUT_KEYS = {"x", "y", "w", "h", "width", "height", "icon", "color",
                     "milestone_icon", "left_icon", "right_icon", "value_size", "font_size",
                     "radius", "rotation", "style", "box", "reference_line"}
STRUCTURAL_KEYS = FIXED_LAYOUT_KEYS | {"id", "from", "to", "source", "target", "source_id", "target_id",
                                      "owner_id", "input_id", "kind", "format"}


def catalog():
    items = []
    for path in sorted(CATALOG.glob("*-components.json")):
        items.extend(json.loads(path.read_text(encoding="utf-8"))["components"])
    ids = [item["id"] for item in items]
    if len(ids) != len(set(ids)):
        raise ValueError("Component ids must be unique")
    return {item["id"]: item for item in items}


def _blank(value, key=""):
    if key in STRUCTURAL_KEYS:
        return copy.deepcopy(value)
    if isinstance(value, dict):
        return {key: _blank(item, key) for key, item in value.items()}
    if isinstance(value, list):
        return [_blank(item) for item in value]
    if isinstance(value, bool):
        return False
    if isinstance(value, (int, float)):
        return 0
    return "" if isinstance(value, str) else None


def _business_data(value):
    if isinstance(value, dict):
        return {key: _business_data(item) for key, item in value.items() if not _fixed_key(key, value)}
    if isinstance(value, list):
        return [_business_data(item) for item in value]
    return copy.deepcopy(value)


def _bind(template, data):
    if isinstance(template, dict):
        return {key: copy.deepcopy(value) if _fixed_key(key, template) else _bind(value, data[key])
                for key, value in template.items()}
    if isinstance(template, list):
        return [_bind(value, actual) for value, actual in zip(template, data)]
    return copy.deepcopy(data)


def _fixed_key(key, parent):
    return key in FIXED_LAYOUT_KEYS or (key == "kind" and ("series" in parent or "values" in parent))


def _no_unknown(data, shape, path="component.data"):
    if isinstance(shape, dict):
        extra = set(data) - set(shape)
        if extra:
            raise ValueError(f"{path}: undeclared component fields {sorted(extra)}")
        for key, value in shape.items():
            _no_unknown(data[key], value, f"{path}.{key}")
    elif isinstance(shape, list):
        for index, value in enumerate(shape):
            _no_unknown(data[index], value, f"{path}[{index}]")


def data_contract(value):
    if isinstance(value, dict):
        return {"type": "object", "properties": {key: data_contract(item) for key, item in value.items()},
                "required": list(value), "additionalProperties": False}
    if isinstance(value, list):
        return {"type": "array", "minItems": len(value), "maxItems": len(value),
                "prefixItems": [data_contract(item) for item in value]}
    if isinstance(value, bool):
        return {"type": "boolean"}
    if isinstance(value, (int, float)):
        return {"type": "number"}
    if isinstance(value, str):
        return {"type": "string", **({"minLength": 1} if value.strip() else {})}
    return {}


def example(component):
    if component.get("source_kind") == "adjacent_variant":
        return copy.deepcopy(component["example_data"])
    from build_reference_page import resources
    _, defaults, _ = resources()
    source = defaults[component["reference_id"]]
    return {key: _business_data(source[key]) for key in component["fields"]}


def _path_commands(value):
    from drawingml.adapter import import_svg_to_pptx_module
    import_svg_to_pptx_module()
    from svg_to_pptx.drawingml_paths import normalize_path_commands, parse_svg_path, svg_path_to_absolute
    return normalize_path_commands(svg_path_to_absolute(parse_svg_path(value)))


def _bounds(node):
    tag = node.tag.rsplit("}", 1)[-1]
    attrs = node.attrib
    if "data-icon-box" in attrs:
        x, y, w, h = map(float, attrs["data-icon-box"].split())
        return x, y, x + w, y + h
    if tag == "rect":
        x, y = float(attrs.get("x", 0)), float(attrs.get("y", 0))
        return x, y, x + float(attrs["width"]), y + float(attrs["height"])
    if tag in {"circle", "ellipse"}:
        x, y = float(attrs["cx"]), float(attrs["cy"])
        rx, ry = float(attrs.get("rx", attrs.get("r", 0))), float(attrs.get("ry", attrs.get("r", 0)))
        return x - rx, y - ry, x + rx, y + ry
    if tag == "line":
        x1, y1, x2, y2 = [float(attrs[key]) for key in ("x1", "y1", "x2", "y2")]
        return min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2)
    if tag in {"polygon", "polyline", "path"}:
        if tag == "path":
            numbers = [number for command in _path_commands(attrs.get("d", "")) for number in command.args]
        else:
            numbers = list(map(float, attrs["points"].replace(",", " ").split()))
        if not numbers:
            return None
        xs, ys = numbers[::2], numbers[1::2]
        return min(xs), min(ys), max(xs), max(ys)
    if tag == "text":
        size = float(attrs.get("font-size", 16))
        x, y = float(attrs.get("x", 0)), float(attrs.get("y", 0))
        lines = list(node) or [node]
        boxes = []
        for line in lines:
            if line is not node:
                x = float(line.get("x", x))
                y = float(line.get("y", y)) + float(line.get("dy", 0))
            text = "".join(line.itertext())
            if not text.strip():
                continue
            width = sum(size * (1 if ord(char) > 255 else 0.56) for char in text)
            shift = {"middle": width / 2, "end": width}.get(attrs.get("text-anchor"), 0)
            boxes.append((x - shift, y - size, x - shift + width, y + size * 0.3))
        if boxes:
            return min(b[0] for b in boxes), min(b[1] for b in boxes), max(b[2] for b in boxes), max(b[3] for b in boxes)
    return None


def _translate(node, dx, dy):
    for item in node.iter():
        attrs = item.attrib
        for key in ("x", "cx", "x1", "x2", "data-x"):
            if key in attrs:
                attrs[key] = str(float(attrs[key]) + dx)
        for key in ("y", "cy", "y1", "y2", "data-y"):
            if key in attrs:
                attrs[key] = str(float(attrs[key]) + dy)
        if "data-icon-box" in attrs:
            x, y, w, h = map(float, attrs["data-icon-box"].split())
            attrs["data-icon-box"] = f"{x + dx} {y + dy} {w} {h}"
        if "points" in attrs:
            numbers = list(map(float, attrs["points"].replace(",", " ").split()))
            attrs["points"] = " ".join(f"{x + dx},{y + dy}" for x, y in zip(numbers[::2], numbers[1::2]))
        if "d" in attrs:
            commands = _path_commands(attrs["d"])
            parts = []
            for command in commands:
                values = [value + (dx if index % 2 == 0 else dy) for index, value in enumerate(command.args)]
                parts.append(command.cmd + " " + " ".join(map(str, values)))
            attrs["d"] = " ".join(parts)


def build_scene(component_id, data):
    component = catalog()[component_id]
    from build_reference_page import _check_content, resources
    shape = example(component)
    _check_content(data, shape, path="component.data")
    _no_unknown(data, shape)
    if component.get("source_kind") == "adjacent_variant":
        svg, native = fishbone(data)
        return svg, native, {"component_id": component_id, "source_kind": "adjacent_variant"}
    renderers, defaults, _ = resources()
    content = _blank(defaults[component["reference_id"]])
    for key, value in data.items():
        content[key] = _bind(defaults[component["reference_id"]][key], value)
    source, native = renderers[component["reference_id"]](content)
    root = ET.fromstring(source)
    x, y, width, height = component["box"]
    scene = Svg(width, height)
    scene.root.set("data-component-id", component_id)
    selected_slots, rejected = set(), []
    for node in root:
        bounds = _bounds(node)
        if bounds is None:
            continue
        left, top, right, bottom = bounds
        contained = left >= x - 5 and top >= y - 5 and right <= x + width + 5 and bottom <= y + height + 5
        if not contained:
            if node.tag.rsplit("}", 1)[-1] == "text" and "".join(node.itertext()).strip():
                anchor_x, anchor_y = float(node.get("x", 0)), float(node.get("y", 0))
                if x - 5 <= anchor_x <= x + width + 5 and y - 5 <= anchor_y <= y + height + 5:
                    raise ValueError(f"{component_id}: text exceeds component capacity: "
                                     f"{''.join(node.itertext())[:100]!r}")
            if right > x and left < x + width and bottom > y and top < y + height:
                rejected.append({"tag": node.tag.rsplit("}", 1)[-1], "bounds": bounds,
                                 "text": "".join(node.itertext())[:100]})
            continue
        clone = copy.deepcopy(node)
        _translate(clone, -x, -y)
        scene.root.append(clone)
        if clone.get("data-role", "").startswith("native-"):
            selected_slots.add(clone.get("id"))
    for bucket in ("charts", "tables", "images", "sankeys"):
        scene.native[bucket] = [copy.deepcopy(item) for item in native.get(bucket, []) if item.get("slot_id") in selected_slots]
    for kind, bucket in (("chart", "charts"), ("table", "tables")):
        expected = sum(item["count"] for item in component.get("native_objects", [])
                       if item["type"] == kind)
        actual = len(scene.native[bucket])
        if actual != expected:
            raise ValueError(f"{component_id}: declared native {kind} count {expected}, "
                             f"but component bounds selected {actual}")
    svg, sidecar = scene.finish()
    report = {"component_id": component_id, "reference_id": component["reference_id"],
              "box": component["box"], "data_fields": component["fields"],
              "selected_elements": len(scene.root), "native_slots": sorted(selected_slots),
              "excluded_boundary_elements": rejected, "visual_review": "not_performed"}
    return svg, sidecar, report


def compose(instances, width=1280, height=720):
    scene = Svg(width, height)
    reports, ids = [], set()
    for instance in instances:
        instance_id = instance["id"]
        if instance_id in ids:
            raise ValueError("Component instance ids must be unique")
        ids.add(instance_id)
        svg, native, report = build_scene(instance["component_id"], instance["data"])
        root = ET.fromstring(svg)
        dx, dy = float(instance.get("x", 0)), float(instance.get("y", 0))
        if dx < 0 or dy < 0 or dx + float(root.get("width")) > width or dy + float(root.get("height")) > height:
            raise ValueError(f"{instance_id}: component does not fit; use its fixed dimensions or a declared smaller variant")
        slot_ids = {}
        for node in root:
            clone = copy.deepcopy(node)
            _translate(clone, dx, dy)
            clone.set("data-instance-id", instance_id)
            for item in clone.iter():
                if item.get("id"):
                    old_id = item.get("id")
                    new_id = f"{instance_id}-{old_id}"
                    item.set("id", new_id)
                    if item.get("data-slot-id"):
                        item.set("data-slot-id", new_id)
                    slot_ids[old_id] = new_id
            scene.root.append(clone)
        for bucket in ("charts", "tables", "images", "sankeys"):
            scene.native.setdefault(bucket, [])
            for item in native.get(bucket, []):
                item = copy.deepcopy(item)
                item["slot_id"] = slot_ids[item["slot_id"]]
                scene.native[bucket].append(item)
        reports.append({"instance_id": instance_id, **report})
    svg, native = scene.finish()
    return svg, native, reports


def fishbone(data):
    scene = Svg(1180, 400)
    scene.arrow(30, 200, 1030, 200, BLUE, 4)
    scene.rect(1035, 158, 140, 84, LIGHT, BLUE, 4)
    scene.text(1105, 192, data["effect"], 17, BLUE, True, width=120, anchor="middle")
    for index, category in enumerate(data["categories"]):
        upper, column = index < 3, index % 3
        bx = 125 + column * 300
        by = 62 if upper else 338
        joint_x, joint_y = bx + 125, 200
        scene.line(bx, by, joint_x, joint_y, BLUE, 2)
        scene.rect(bx - 60, 15 if upper else 353, 210, 32, BLUE, "none", 2)
        scene.text(bx + 45, 38 if upper else 376, category["label"], 17, "#FFFFFF", True, anchor="middle")
        for row, cause in enumerate(category["causes"]):
            fraction = (row + 1) / 4
            px = bx + fraction * (joint_x - bx)
            py = by + fraction * (joint_y - by)
            scene.line(px - 108, py, px, py, LINE, 1.5)
            scene.text(px - 107, py - 6, cause, 13, INK, width=115, role="diagram")
    scene.text(30, 394, data["boundary"], 11, INK, width=960, role="source")
    return scene.finish()
