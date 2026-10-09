#!/usr/bin/env python3
"""Build one editable native radar, line, or bar chart from business data."""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any

_SVG_DIR = Path(__file__).resolve().parent
_SCRIPTS_DIR = _SVG_DIR.parent
for _path in (_SVG_DIR, _SCRIPTS_DIR):
    if str(_path) not in sys.path:
        sys.path.insert(0, str(_path))

from drawingml.pipeline import render_svg_drawingml  # noqa: E402
from inspect_pptx import inspect as inspect_pptx  # noqa: E402
from reference_layouts.common import BLUE, INK, LINE, PURPLE, TEAL, Svg  # noqa: E402

KINDS = ("radar", "line", "bar")
DEFAULT_NUMBER_FORMAT = "0.##"
TOP_LEVEL_FIELDS = frozenset(
    {
        "title",
        "labels",
        "series",
        "unit",
        "period",
        "source",
        "limitation",
        "scale",
        "target",
        "number_format",
    }
)
REQUIRED_FIELDS = frozenset(
    {"title", "labels", "series", "unit", "period", "source", "limitation"}
)
TEXT_CAPACITY = {
    "title": 32,
    "unit": 16,
    "period": 24,
    "source": 72,
    "limitation": 78,
    "label": 12,
    "series.name": 18,
    "target.label": 18,
    "number_format": 24,
}
CATEGORY_CAPACITY = {
    "radar": (3, 8),
    "line": (2, 12),
    "bar": (1, 10),
}
SERIES_CAPACITY = (1, 4)
CHART_PALETTE = (BLUE, TEAL, PURPLE, "#D97706")

DESCRIPTION = {
    "artifact_kind": "component",
    "supported_kinds": list(KINDS),
    "invocation": "--kind radar|line|bar --content data.json --output-dir dir",
    "data_contract": {
        "required": sorted(REQUIRED_FIELDS),
        "optional": ["number_format"],
        "radar_required": {"scale": {"required": ["minimum", "maximum"]}},
        "line_or_bar_optional": {"target": {"required": ["value", "label"]}},
        "series": {"required": ["name", "values"]},
        "missing_values": "rejected; never converted to zero",
        "number_format_default": DEFAULT_NUMBER_FORMAT,
    },
    "capacity": {
        "categories": {kind: {"minimum": low, "maximum": high}
                       for kind, (low, high) in CATEGORY_CAPACITY.items()},
        "series": {"minimum": SERIES_CAPACITY[0], "maximum": SERIES_CAPACITY[1]},
        "text_characters": TEXT_CAPACITY,
    },
    "outputs": [
        "content.json",
        "source.svg",
        "native-data.json",
        "page.pptx",
        "native-chart-report.json",
    ],
    "scope": "Reusable native chart component; it is not a complete business slide or deck.",
}


class ContentError(ValueError):
    """Raised when business input does not satisfy the bounded chart contract."""


def _reject_unknown(value: dict[str, Any], allowed: set[str] | frozenset[str], path: str) -> None:
    unknown = sorted(set(value) - set(allowed))
    if unknown:
        raise ContentError(f"{path}: unknown fields {unknown}")


def _require_fields(value: dict[str, Any], required: set[str] | frozenset[str], path: str) -> None:
    missing = sorted(set(required) - set(value))
    if missing:
        raise ContentError(f"{path}: missing required fields {missing}")


def _text(value: Any, path: str, capacity: int) -> str:
    if not isinstance(value, str):
        raise ContentError(f"{path}: must be a string")
    normalized = value.strip()
    if not normalized:
        raise ContentError(f"{path}: must be non-empty")
    if any(character in normalized for character in "\r\n\t"):
        raise ContentError(f"{path}: line breaks and tabs are not supported")
    if len(normalized) > capacity:
        raise ContentError(f"{path}: text exceeds {capacity}-character capacity")
    return normalized


def _number(value: Any, path: str) -> int | float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        if value is None:
            raise ContentError(f"{path}: missing values are not supported")
        raise ContentError(f"{path}: must be a finite number and bool is not accepted")
    if not math.isfinite(value):
        raise ContentError(f"{path}: must be finite")
    return value


def validate_content(kind: str, raw: Any) -> dict[str, Any]:
    """Validate and normalize the public business-only input."""

    if kind not in KINDS:
        raise ContentError(f"kind: choose one of {', '.join(KINDS)}")
    if not isinstance(raw, dict):
        raise ContentError("content: must be a JSON object")
    _reject_unknown(raw, TOP_LEVEL_FIELDS, "content")
    _require_fields(raw, REQUIRED_FIELDS, "content")

    normalized: dict[str, Any] = {
        field: _text(raw[field], field, TEXT_CAPACITY[field])
        for field in ("title", "unit", "period", "source", "limitation")
    }
    normalized["number_format"] = _text(
        raw.get("number_format", DEFAULT_NUMBER_FORMAT),
        "number_format",
        TEXT_CAPACITY["number_format"],
    )

    labels = raw["labels"]
    if not isinstance(labels, list):
        raise ContentError("labels: must be an array")
    low, high = CATEGORY_CAPACITY[kind]
    if not low <= len(labels) <= high:
        raise ContentError(f"labels: {kind} requires {low}..{high} categories")
    normalized["labels"] = [
        _text(label, f"labels[{index}]", TEXT_CAPACITY["label"])
        for index, label in enumerate(labels)
    ]

    raw_series = raw["series"]
    if not isinstance(raw_series, list):
        raise ContentError("series: must be an array")
    if not SERIES_CAPACITY[0] <= len(raw_series) <= SERIES_CAPACITY[1]:
        raise ContentError(
            f"series: requires {SERIES_CAPACITY[0]}..{SERIES_CAPACITY[1]} series"
        )
    series: list[dict[str, Any]] = []
    for series_index, item in enumerate(raw_series):
        path = f"series[{series_index}]"
        if not isinstance(item, dict):
            raise ContentError(f"{path}: must be an object")
        _reject_unknown(item, {"name", "values"}, path)
        _require_fields(item, {"name", "values"}, path)
        values = item["values"]
        if not isinstance(values, list):
            raise ContentError(f"{path}.values: must be an array")
        if len(values) != len(normalized["labels"]):
            raise ContentError(
                f"{path}.values: length {len(values)} does not match labels length "
                f"{len(normalized['labels'])}"
            )
        series.append(
            {
                "name": _text(item["name"], f"{path}.name", TEXT_CAPACITY["series.name"]),
                "values": [
                    _number(value, f"{path}.values[{value_index}]")
                    for value_index, value in enumerate(values)
                ],
            }
        )
    normalized["series"] = series

    if kind == "radar":
        if "target" in raw:
            raise ContentError("target: supported only for line and bar")
        scale = raw.get("scale")
        if not isinstance(scale, dict):
            raise ContentError("scale: radar requires an object with minimum and maximum")
        _reject_unknown(scale, {"minimum", "maximum"}, "scale")
        _require_fields(scale, {"minimum", "maximum"}, "scale")
        minimum = _number(scale["minimum"], "scale.minimum")
        maximum = _number(scale["maximum"], "scale.maximum")
        if minimum >= maximum:
            raise ContentError("scale: minimum must be less than maximum")
        for series_index, item in enumerate(series):
            for value_index, value in enumerate(item["values"]):
                if not minimum <= value <= maximum:
                    raise ContentError(
                        f"series[{series_index}].values[{value_index}]: radar value {value} "
                        f"is outside scale {minimum}..{maximum}"
                    )
        normalized["scale"] = {"minimum": minimum, "maximum": maximum}
    else:
        if "scale" in raw:
            raise ContentError("scale: supported only for radar")
        if "target" in raw:
            target = raw["target"]
            if not isinstance(target, dict):
                raise ContentError("target: must be an object")
            _reject_unknown(target, {"value", "label"}, "target")
            _require_fields(target, {"value", "label"}, "target")
            normalized["target"] = {
                "value": _number(target["value"], "target.value"),
                "label": _text(
                    target["label"], "target.label", TEXT_CAPACITY["target.label"]
                ),
            }
    return normalized


def build_scene(kind: str, content: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    """Use the shared Svg.chart builder and fixed component geometry."""

    scene = Svg(width=1280, height=720)
    scene.text(
        64,
        68,
        content["title"],
        size=36,
        color=BLUE,
        bold=True,
        width=1152,
        max_lines=1,
    )
    scene.text(
        64,
        106,
        f"单位：{content['unit']} | 期间：{content['period']}",
        size=15,
        color=INK,
        width=1152,
        max_lines=1,
    )
    options: dict[str, Any] = {}
    if kind == "radar":
        options = {
            "data_labels": False,
            "value_axis": {
                "format": content["number_format"],
                "minimum": content["scale"]["minimum"],
                "maximum": content["scale"]["maximum"],
            },
        }
        if len(content["series"]) >= 2:
            options.update(
                {"radar_fill_series_index": 1, "radar_fill_transparency": 65}
            )
    elif kind == "bar":
        values = [value for item in content["series"] for value in item["values"]]
        if "target" in content:
            values.append(content["target"]["value"])
        minimum_value = min(values)
        minimum = 0
        if minimum_value < 0:
            span = max([0, *values]) - minimum_value
            step = 10 ** math.floor(math.log10(span)) / 10
            minimum = math.floor((minimum_value - span * 0.1) / step) * step
        axis: dict[str, Any] = {"format": content["number_format"], "minimum": minimum}
        if values and max(values) < 0:
            axis["maximum"] = 0
        options = {"value_axis": axis}
    elif len(content["series"]) > 1:
        options = {"data_labels": False}
    if kind in {"line", "bar"} and "target" in content:
        options.update(
            {
                "legend": True,
                "target": content["target"]["value"],
                "reference_line": True,
                "reference_label": content["target"]["label"],
            }
        )
        format_code = content["number_format"].replace('"%"', "")
        scaled_percent = "%" in format_code
        target_value = content["target"]["value"] * (100 if scaled_percent else 1)
        target_text = format(target_value, ".12g") + ("%" if scaled_percent else "")
        unit_suffix = (
            "" if scaled_percent
            else f" {content['unit']}"
        )
        scene.text(
            64,
            134,
            f"参考值：{target_text}{unit_suffix}",
            size=14,
            color=INK,
            width=1152,
            max_lines=1,
            role="chart",
        )
    scene.chart(
        "native-chart",
        64,
        156,
        1152,
        438,
        content["labels"],
        content["series"],
        kind=kind,
        fmt=content["number_format"],
        options=options,
    )
    scene.line(64, 618, 1216, 618, color=LINE, width=1)
    scene.text(
        64,
        646,
        f"来源：{content['source']}",
        size=13,
        color=INK,
        width=1152,
        max_lines=1,
        role="source",
    )
    scene.text(
        64,
        678,
        f"口径与限制：{content['limitation']}",
        size=13,
        color=INK,
        width=1152,
        max_lines=1,
        role="source",
    )
    svg, native = scene.finish()
    native["charts"][-1]["colors"] = list(CHART_PALETTE[: len(content["series"])])
    return svg, native


def _write_json(path: Path, payload: Any) -> None:
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False),
        encoding="utf-8",
    )


def build(kind: str, content_path: Path, output_dir: Path) -> dict[str, Any]:
    raw = json.loads(content_path.read_text(encoding="utf-8"))
    content = validate_content(kind, raw)
    svg, native = build_scene(kind, content)
    output_dir.mkdir(parents=True, exist_ok=True)
    content_output = output_dir / "content.json"
    svg_output = output_dir / "source.svg"
    native_output = output_dir / "native-data.json"
    pptx_output = output_dir / "page.pptx"
    report_output = output_dir / "native-chart-report.json"
    _write_json(content_output, content)
    svg_output.write_text(svg, encoding="utf-8")
    _write_json(native_output, native)

    render = render_svg_drawingml(
        svg_path=svg_output,
        native_data=native,
        output=pptx_output,
        canvas_format="auto",
        artifact_kind="component",
    )
    render_summary = {
        key: value
        for key, value in render.items()
        if key not in {"expanded_svg", "stripped_svg"}
    }
    if not render.get("ok"):
        report = {
            "status": "blocked",
            "kind": kind,
            "artifact_kind": "component",
            "render": render_summary,
            "native_object_status": {
                "source": "inspect_pptx",
                "status": "not_inspected",
            },
            "visual_review": "not_performed",
            "powerpoint_roundtrip": "not_performed",
        }
        _write_json(report_output, report)
        return report

    inspection = inspect_pptx(pptx_output)
    charts = [
        chart
        for page in inspection.get("pages", [])
        for chart in page.get("charts", [])
    ]
    native_verified = (
        inspection.get("structure_passed") is True
        and len(charts) == 1
        and charts[0].get("embedded_workbook") is True
    )
    report = {
        "status": "structurally_verified" if native_verified else "blocked",
        "kind": kind,
        "artifact_kind": "component",
        "render": render_summary,
        "native_object_status": {
            "source": "inspect_pptx",
            "status": "verified" if native_verified else "failed",
            "chart_count": len(charts),
            "embedded_workbook": bool(charts and charts[0].get("embedded_workbook")),
        },
        "inspection": inspection,
        "visual_review": inspection.get("visual_review", "not_performed"),
        "powerpoint_roundtrip": inspection.get("powerpoint_roundtrip", "not_performed"),
        "scope": DESCRIPTION["scope"],
    }
    _write_json(report_output, report)
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--describe", action="store_true")
    parser.add_argument("--kind", choices=KINDS)
    parser.add_argument("--content", type=Path)
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args(argv)
    if args.describe:
        print(json.dumps(DESCRIPTION, ensure_ascii=False, indent=2))
        return 0
    if args.kind is None or args.content is None or args.output_dir is None:
        parser.error("--kind, --content, and --output-dir are required")
    try:
        report = build(args.kind, args.content, args.output_dir)
    except (ValueError, OSError) as exc:
        print(
            json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False),
            file=sys.stderr,
        )
        return 2
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["status"] == "structurally_verified" else 2


if __name__ == "__main__":
    raise SystemExit(main())
