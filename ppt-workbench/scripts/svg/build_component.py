#!/usr/bin/env python3
"""Build or compose fixed complex components by replacing only business data."""

import argparse
import json
import xml.etree.ElementTree as ET
from pathlib import Path

from reference_layouts.components import catalog, compose, data_contract, example
from reference_layouts.common import INK, Svg

CONTEXT_FIELDS = ("period", "population", "source", "limitation")
EXAMPLE_CONTEXT = {"period": "合成期次，非真实日期", "population": "授权合成输入，非真实业务样本",
                   "source": "本技能授权合成示例", "limitation": "仅校准组件结构，不代表真实经营结果"}


def split_context(raw):
    if not isinstance(raw, dict):
        raise ValueError("component content must be an object")
    data = {key: value for key, value in raw.items() if key != "evidence_context"}
    if "evidence_context" not in raw:
        raise ValueError("component content requires evidence_context; mark inapplicable or unknown business context explicitly")
    context = raw["evidence_context"]
    if not isinstance(context, dict) or set(context) != set(CONTEXT_FIELDS):
        raise ValueError(f"evidence_context requires only {CONTEXT_FIELDS}")
    for field in CONTEXT_FIELDS:
        if not isinstance(context[field], str) or not context[field].strip() or "\n" in context[field]:
            raise ValueError(f"evidence_context.{field} must be nonempty single-line business text")
    return data, {field: context[field].strip() for field in CONTEXT_FIELDS}


def attach_context(svg, context, *, baseline):
    if context is None:
        return svg
    root = ET.fromstring(svg)
    width = float(root.get("width", "1280"))
    height = float(root.get("height", "720"))
    if baseline + 17 > height:
        raise ValueError("evidence_context does not fit below the fixed component")
    caption = Svg(width, height)
    caption.text(24, baseline,
                 f"期间：{context['period']} | 样本：{context['population']} | 来源：{context['source']}",
                 11, INK, width=width - 48, role="source", max_lines=1)
    caption.text(24, baseline + 14, f"口径与限制：{context['limitation']}",
                 11, INK, width=width - 48, role="source", max_lines=1)
    root.extend(caption.root)
    return ET.tostring(root, encoding="unicode")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--list", action="store_true")
    parser.add_argument("--family")
    parser.add_argument("--describe")
    parser.add_argument("--component-id")
    source = parser.add_mutually_exclusive_group()
    source.add_argument("--content", type=Path)
    source.add_argument("--composition", type=Path)
    source.add_argument("--example", action="store_true")
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--render", action="store_true")
    args = parser.parse_args()
    components = catalog()
    if args.list:
        fields = ("id", "name", "family", "reference_id", "business_question", "capacity", "native_objects")
        items = [item for item in components.values() if not args.family or item["family"] == args.family]
        print(json.dumps([{key: item[key] for key in fields} for item in items], ensure_ascii=False, indent=2))
        return 0
    if args.describe:
        record = {**components[args.describe], "data_fields": list(example(components[args.describe]))}
        record["data_contract"] = data_contract(example(components[args.describe]))
        record["data_contract"]["properties"]["evidence_context"] = data_contract(EXAMPLE_CONTEXT)
        record["data_contract"]["required"].append("evidence_context")
        record["required_business_fields"] = ["evidence_context"]
        if args.example:
            record["synthetic_example"] = {**example(components[args.describe]), "evidence_context": EXAMPLE_CONTEXT}
        print(json.dumps(record, ensure_ascii=False, indent=2))
        return 0
    if args.output_dir is None:
        parser.error("--output-dir is required")
    if args.composition:
        data = json.loads(args.composition.read_text(encoding="utf-8"))
        composition, context = split_context(data)
        height = composition.get("height", 720)
        svg, native, reports = compose(composition["instances"], composition.get("width", 1280), height)
        svg = attach_context(svg, context, baseline=height - 24)
    else:
        if args.component_id not in components:
            parser.error("Choose a component from --list")
        if args.content:
            data = json.loads(args.content.read_text(encoding="utf-8"))
        elif args.example:
            data = {**example(components[args.component_id]), "evidence_context": EXAMPLE_CONTEXT}
        else:
            parser.error("Provide complete --content; --example requires authorization for synthetic data")
        component = components[args.component_id]
        component_data, context = split_context(data)
        _, _, w, h = component["box"]
        svg, native, reports = compose([{"id": "component", "component_id": args.component_id,
                                        "x": (1280 - w) / 2, "y": (720 - h) / 2, "data": component_data}])
        svg = attach_context(svg, context, baseline=(720 + h) / 2 + 22)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "source.svg").write_text(svg, encoding="utf-8")
    (args.output_dir / "native-data.json").write_text(json.dumps(native, ensure_ascii=False, indent=2), encoding="utf-8")
    (args.output_dir / "content.json").write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    report = {"components": reports, "content_mode": "synthetic_example" if args.example else "explicit",
              "evidence_context": context}
    if args.render:
        from drawingml.pipeline import render_svg_drawingml
        result = render_svg_drawingml(svg_path=args.output_dir / "source.svg", native_data=native,
                                     output=args.output_dir / "page.pptx", canvas_format="auto",
                                     artifact_kind="page" if args.composition else "component")
        report["render"] = {key: value for key, value in result.items() if key not in {"expanded_svg", "stripped_svg"}}
    (args.output_dir / "component-report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if not args.render or report["render"]["ok"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
