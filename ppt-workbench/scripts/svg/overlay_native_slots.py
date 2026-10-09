"""Overlay native chart/table/sankey/image slots onto a PPTX with python-pptx.

SVG holds geometry; native-data.json holds charts[] / tables[] / sankeys[] /
images[]. Never write charts[].kind=sankey|combo|bubble. Sankey is a
geometric overlay (or an explicit fallback), not a chart kind. Images are
local PNG/JPEG only; never SVG <image href>.
"""

from __future__ import annotations

import argparse
import copy
import json
import math
import sys
import xml.etree.ElementTree as ET
from contextlib import suppress
from pathlib import Path
from typing import Any

from pptx import Presentation
from pptx.chart.data import CategoryChartData
from pptx.dml.color import RGBColor
from pptx.enum.chart import XL_CHART_TYPE, XL_LABEL_POSITION, XL_MARKER_STYLE, XL_TICK_LABEL_POSITION
from pptx.enum.dml import MSO_LINE_DASH_STYLE
from pptx.enum.shapes import MSO_AUTO_SHAPE_TYPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.oxml.xmlchemy import OxmlElement
from pptx.util import Inches, Pt

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

import search_icons as _icon_lib  # noqa: E402

CANVAS = (1280.0, 720.0)
SLIDE_IN = (13.333, 7.5)
CHART_MIN = (320.0, 200.0)
MICRO_MIN = (140.0, 80.0)
SPARKLINE_MIN = (140.0, 48.0)
UNSUPPORTED_KINDS = frozenset({"sankey", "combo", "bubble"})
SUPPORTED_KINDS = frozenset({"bar", "line", "pie", "waterfall", "radar"})
KIND_ALIASES = {"trend": "line", "timeseries": "line", "column": "bar"}
WATERFALL_COLORS = {"increase": "#22C55E", "decrease": "#EF4444", "total": "#64748B"}
SANKEY_PALETTE = ("#3B82F6", "#22C55E", "#F59E0B", "#8B5CF6", "#EF4444", "#14B8A6")
CHART_TYPE_MAP = {
    "bar": XL_CHART_TYPE.COLUMN_CLUSTERED,
    "line": XL_CHART_TYPE.LINE_MARKERS,
    "pie": XL_CHART_TYPE.PIE,
    "waterfall": XL_CHART_TYPE.COLUMN_STACKED,
    "radar": XL_CHART_TYPE.RADAR,
}
XLINK_HREF = "{http://www.w3.org/1999/xlink}href"
RASTER_SUFFIXES = {".png", ".jpg", ".jpeg"}


def diagnose_native_slots(
    svg_text: str,
    native_data: dict[str, Any] | None,
    assets_dir: Path | None = None,
) -> dict[str, Any]:
    """Return blocking issues and warnings for SVG slots + sidecar JSON."""

    issues: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    try:
        root = ET.fromstring(svg_text)
    except ET.ParseError as exc:
        return {
            "ok": False,
            "issues": [{"code": "SVG_PARSE_ERROR", "message": str(exc)}],
            "warnings": [],
        }
    viewbox = _parse_viewbox(root)
    native = native_data if isinstance(native_data, dict) else {}
    asset_roots = _asset_roots(assets_dir)
    for chart in native.get("charts") or []:
        if not isinstance(chart, dict):
            continue
        kind = _declared_kind(chart)
        if kind in UNSUPPORTED_KINDS or kind not in SUPPORTED_KINDS:
            issues.append(
                {
                    "code": "NATIVE_CHART_SLOT_UNSUPPORTED_TYPE",
                    "message": (
                        f"native chart slot kind='{kind}' 不是受支持的原生图表类型。"
                        "支持 bar / line / pie / trend / waterfall / radar；"
                        "never charts[].kind=sankey（桑基走 native-sankey-slot / sankeys[]）。"
                    ),
                    "slot_id": str(chart.get("slot_id") or chart.get("id") or ""),
                    "severity": "error",
                }
            )
    _diagnose_svg_image_elements(root, viewbox, issues)
    for element in root.iter():
        attrs = element.attrib
        if _is_chart_slot(attrs):
            _diagnose_chart_slot(element, attrs, native, viewbox, issues, warnings)
        elif _is_table_slot(attrs):
            _diagnose_table_slot(element, attrs, native, viewbox, issues, warnings)
        elif _is_sankey_slot(attrs):
            _diagnose_sankey_slot(element, attrs, native, viewbox, issues, warnings)
        elif _is_image_slot(attrs):
            _diagnose_image_slot(element, attrs, native, viewbox, issues, warnings, asset_roots)
    return {"ok": not issues, "issues": issues, "warnings": warnings}


def overlay_native_slots(
    *,
    svg_text: str,
    native_data: dict[str, Any] | None,
    output: Path,
    pptx_path: Path | None = None,
    slide_index: int = 0,
    assets_dir: Path | None = None,
) -> dict[str, Any]:
    """Write python-pptx charts/tables/sankey/images into output PPTX."""

    presentation, slide = _open_or_create(pptx_path, slide_index)
    viewbox = _parse_viewbox(ET.fromstring(svg_text))
    native = native_data if isinstance(native_data, dict) else {}
    asset_roots = _asset_roots(assets_dir)
    chart_count = 0
    table_count = 0
    sankey_count = 0
    image_count = 0
    sankey_fallback = None
    root = ET.fromstring(svg_text)
    for element in root.iter():
        attrs = element.attrib
        if _is_chart_slot(attrs):
            if _add_chart(slide, attrs, native, viewbox):
                chart_count += 1
        elif _is_table_slot(attrs):
            if _add_table(slide, attrs, native, viewbox):
                table_count += 1
        elif _is_sankey_slot(attrs):
            applied, fallback = _add_sankey(slide, attrs, native, viewbox)
            if applied:
                sankey_count += 1
            elif fallback:
                sankey_fallback = fallback
        elif _is_image_slot(attrs):
            if _add_image(slide, attrs, native, viewbox, asset_roots):
                image_count += 1
    presentation.save(str(output))
    return {
        "ok": True,
        "applied": True,
        "chart_count": chart_count,
        "table_count": table_count,
        "sankey_count": sankey_count,
        "image_count": image_count,
        "sankey_fallback": sankey_fallback,
        "output": str(output),
    }


def _diagnose_chart_slot(
    element: ET.Element,
    attrs: dict[str, str],
    native: dict[str, Any],
    viewbox: tuple[float, float],
    issues: list[dict[str, Any]],
    warnings: list[dict[str, Any]],
) -> None:
    slot_id = _slot_id(attrs, f"chart-slot-{len(issues) + 1}")
    meta = _merge(_slot_json(attrs, "data-chart-slot"), _external(native, "charts", slot_id))
    kind = _declared_kind(meta, attrs.get("data-chart-type"))
    sparkline_error = _sparkline_error(meta, kind)
    options = meta.get("options") if isinstance(meta.get("options"), dict) else {}
    if attrs.get("data-native-chart-variant") == "sparkline" and options.get("sparkline") is not True:
        sparkline_error = "sparkline slot requires explicit native sparkline options"
    if sparkline_error:
        issues.append({"code": "NATIVE_SPARKLINE_INVALID", "message": sparkline_error,
                       "slot_id": slot_id, "severity": "error"})
    if kind in UNSUPPORTED_KINDS or kind not in SUPPORTED_KINDS:
        issues.append(
            {
                "code": "NATIVE_CHART_SLOT_UNSUPPORTED_TYPE",
                "message": (
                    f"native chart slot kind='{kind}' 不是受支持的原生图表类型。"
                    "支持 bar / line / pie / trend / waterfall；never charts[].kind=sankey。"
                ),
                "slot_id": slot_id,
                "severity": "error",
            }
        )
    elif kind == "waterfall":
        if not _waterfall_segments(meta):
            issues.append(
                {
                    "code": "NATIVE_CHART_SLOT_MISSING_DATA",
                    "message": "native waterfall slot 缺少 segments。",
                    "slot_id": slot_id,
                    "severity": "error",
                }
            )
    elif not _chart_series(meta):
        issues.append(
            {
                "code": "NATIVE_CHART_SLOT_MISSING_DATA",
                "message": "native chart slot 在 native-data JSON 中缺少匹配 slot_id 的 chart 数据。",
                "slot_id": slot_id,
                "severity": "error",
            }
        )
    box = _slot_box_px(attrs, meta)
    variant = "sparkline" if options.get("sparkline") is True and not sparkline_error else (
        None if sparkline_error else attrs.get("data-native-chart-variant"))
    _diagnose_box(slot_id, box, viewbox, issues, warnings, kind="chart", variant=variant)
    _diagnose_in_slot_text(element, slot_id, warnings)


def _diagnose_table_slot(
    element: ET.Element,
    attrs: dict[str, str],
    native: dict[str, Any],
    viewbox: tuple[float, float],
    issues: list[dict[str, Any]],
    warnings: list[dict[str, Any]],
) -> None:
    slot_id = _slot_id(attrs, f"table-slot-{len(issues) + 1}")
    meta = _merge(_slot_json(attrs, "data-table-slot"), _external(native, "tables", slot_id))
    if not _table_rows(meta):
        issues.append(
            {
                "code": "NATIVE_TABLE_SLOT_MISSING_DATA",
                "message": "native table slot 在 native-data JSON 中缺少匹配 slot_id 的 table 数据。",
                "slot_id": slot_id,
                "severity": "error",
            }
        )
    _diagnose_box(slot_id, _slot_box_px(attrs, meta), viewbox, issues, warnings, kind="table")
    _diagnose_in_slot_text(element, slot_id, warnings)


def _diagnose_sankey_slot(
    element: ET.Element,
    attrs: dict[str, str],
    native: dict[str, Any],
    viewbox: tuple[float, float],
    issues: list[dict[str, Any]],
    warnings: list[dict[str, Any]],
) -> None:
    slot_id = _slot_id(attrs, f"sankey-slot-{len(issues) + 1}")
    meta = _merge(_slot_json(attrs, "data-sankey-slot"), _external(native, "sankeys", slot_id))
    if not _sankey_flows(meta):
        issues.append(
            {
                "code": "NATIVE_SANKEY_SLOT_MISSING_DATA",
                "message": "native sankey slot 在 native-data JSON 中缺少匹配 slot_id 的 flows 数据。",
                "slot_id": slot_id,
                "severity": "error",
            }
        )
    _diagnose_box(slot_id, _slot_box_px(attrs, meta), viewbox, issues, warnings, kind="sankey")
    _diagnose_in_slot_text(element, slot_id, warnings)


def _diagnose_svg_image_elements(
    root: ET.Element,
    viewbox: tuple[float, float],
    issues: list[dict[str, Any]],
) -> None:
    for element in root.iter():
        if element.tag.rsplit("}", 1)[-1] != "image":
            continue
        href = (element.get("href") or element.get(XLINK_HREF) or "").strip()
        if href:
            issues.append(
                {
                    "code": "SVG_IMAGE_HREF_FORBIDDEN",
                    "message": "内容 SVG 禁止 <image href>；证据图走 native-image-slot + 本地 asset_key。",
                    "slot_id": element.get("id") or "",
                    "severity": "error",
                }
            )
        box = _element_box_px(element.attrib)
        if box is not None and _is_near_full_page(box, viewbox):
            issues.append(
                {
                    "code": "SVG_FULL_PAGE_IMAGE_FORBIDDEN",
                    "message": "整页照片走 deck-framework.json，不要在内容 SVG 画满页 <image>。",
                    "slot_id": element.get("id") or "",
                    "severity": "error",
                }
            )


def _diagnose_image_slot(
    element: ET.Element,
    attrs: dict[str, str],
    native: dict[str, Any],
    viewbox: tuple[float, float],
    issues: list[dict[str, Any]],
    warnings: list[dict[str, Any]],
    asset_roots: list[Path],
) -> None:
    slot_id = _slot_id(attrs, f"image-slot-{len(issues) + 1}")
    meta = _merge(_slot_json(attrs, "data-image-slot"), _external(native, "images", slot_id))
    box = _slot_box_px(attrs, meta)
    if box is not None and _is_near_full_page(box, viewbox):
        issues.append(
            {
                "code": "SVG_FULL_PAGE_IMAGE_FORBIDDEN",
                "message": "整页底板写 deck-framework.json，禁止 1280x720 native-image-slot。",
                "slot_id": slot_id,
                "severity": "error",
            }
        )
    if _has_preview_url(meta):
        issues.append(
            {
                "code": "NATIVE_IMAGE_SLOT_PREVIEW_URL_FORBIDDEN",
                "message": "images[] 禁止 previewUrl；只用本地 asset_key。",
                "slot_id": slot_id,
                "severity": "error",
            }
        )
    if _remote_image_refs(meta):
        issues.append(
            {
                "code": "NATIVE_IMAGE_SLOT_UNCONTROLLED_EXTERNAL_URL",
                "message": "native image slot 禁止远程 URL / /v1/files；只用本地 PNG/JPEG。",
                "slot_id": slot_id,
                "severity": "error",
            }
        )
        _diagnose_box(slot_id, box, viewbox, issues, warnings, kind="image")
        _diagnose_in_slot_text(element, slot_id, warnings)
        return
    if _local_image_path(meta, asset_roots) is None:
        issues.append(
            {
                "code": "NATIVE_IMAGE_SLOT_MISSING_DATA",
                "message": "native image slot 缺少匹配 slot_id 的本地 images[].asset_key。",
                "slot_id": slot_id,
                "severity": "error",
            }
        )
    _diagnose_box(slot_id, box, viewbox, issues, warnings, kind="image")
    _diagnose_in_slot_text(element, slot_id, warnings)


def _diagnose_box(
    slot_id: str,
    box: tuple[float, float, float, float] | None,
    viewbox: tuple[float, float],
    issues: list[dict[str, Any]],
    warnings: list[dict[str, Any]],
    *,
    kind: str,
    variant: str | None = None,
) -> None:
    if box is None:
        return
    x, y, w, h = box
    vw, vh = viewbox
    if x < -2 or y < -2 or x + w > vw + 2 or y + h > vh + 2:
        issues.append(
            {
                "code": "NATIVE_SLOT_BOX_OUT_OF_CANVAS",
                "message": "slot box 越出 1280x720 画布。",
                "slot_id": slot_id,
                "severity": "error",
            }
        )
    if kind != "chart":
        return
    variant = (variant or "").lower()
    min_w, min_h = SPARKLINE_MIN if variant == "sparkline" else (
        MICRO_MIN if variant == "micro" else CHART_MIN)
    if w < min_w or h < min_h:
        warnings.append(
            {
                "code": "NATIVE_CHART_SLOT_TOO_SMALL",
                "message": f"chart slot 小于 {int(min_w)}x{int(min_h)}。",
                "slot_id": slot_id,
                "severity": "warning",
            }
        )


def _diagnose_in_slot_text(element: ET.Element, slot_id: str, warnings: list[dict[str, Any]]) -> None:
    texts = [
        "".join(child.itertext()).strip()
        for child in element.iter()
        if child.tag.rsplit("}", 1)[-1] == "text" and "".join(child.itertext()).strip()
    ]
    if not texts:
        return
    warnings.append(
        {
            "code": "NATIVE_SLOT_PLACEHOLDER_TEXTS_WILL_BE_REMOVED",
            "message": "slot 组内 <text> 渲染时会剥离；标题/来源必须写在组外。",
            "slot_id": slot_id,
            "severity": "warning",
        }
    )
    if any("占位" not in text for text in texts):
        warnings.append(
            {
                "code": "NATIVE_SLOT_TEXT_OVERLAP",
                "message": "slot 组内非占位文字会被原生图盖住，移到 box 上方 28–40px 或下方 ≥36px。",
                "slot_id": slot_id,
                "severity": "warning",
            }
        )


def _sparkline_error(meta: dict[str, Any], kind: str) -> str | None:
    options = meta.get("options") if isinstance(meta.get("options"), dict) else {}
    enabled = options.get("sparkline", False)
    if not isinstance(enabled, bool):
        return "sparkline must be a boolean"
    if not enabled:
        return None
    series = _chart_series(meta)
    if kind != "line" or len(series) != 1 or not 2 <= len(series[0]["values"]) <= 12:
        return "sparkline requires one native line series with 2..12 categories"
    if options.get("reference_line") or options.get("target") is not None or options.get("legend") is True or options.get("axes") is True:
        return "sparkline has no axes, legend or reference series; use a regular chart for those"
    return None


def _add_chart(slide: Any, attrs: dict[str, str], native: dict[str, Any], viewbox: tuple[float, float]) -> bool:
    slot_id = _slot_id(attrs, "chart-slot")
    meta = _merge(_slot_json(attrs, "data-chart-slot"), _external(native, "charts", slot_id))
    kind = _declared_kind(meta, attrs.get("data-chart-type"))
    sparkline_error = _sparkline_error(meta, kind)
    options = meta.get("options") if isinstance(meta.get("options"), dict) else {}
    if attrs.get("data-native-chart-variant") == "sparkline" and options.get("sparkline") is not True:
        sparkline_error = "sparkline slot requires explicit native sparkline options"
    if sparkline_error:
        raise ValueError(sparkline_error)
    box = _slot_box_in(attrs, meta, viewbox, slide)
    if box is None or kind in UNSUPPORTED_KINDS or kind not in SUPPORTED_KINDS:
        return False
    if kind == "waterfall":
        return _add_waterfall_chart(slide, meta, box)
    series = _chart_series(meta)
    if not series:
        return False
    actual_count = len(series)
    options = meta.get("options") if isinstance(meta.get("options"), dict) else {}
    dashed_indices = options.get("dashed_series_indices", [])
    if not isinstance(dashed_indices, list) or any(
        not isinstance(index, int) or isinstance(index, bool) or not 0 <= index < actual_count
        for index in dashed_indices
    ):
        raise ValueError("dashed_series_indices must be an array of existing series indices")
    target = options.get("target")
    valid_target = isinstance(target, (int, float)) and not isinstance(target, bool) and math.isfinite(target)
    target_category = options.get("target_category") if kind == "bar" and valid_target else None
    if target_category and actual_count == 1:
        series[0]["labels"] = [*series[0]["labels"], str(target_category)]
        series[0]["values"] = [*series[0]["values"], target]
    reference = valid_target and kind in {"bar", "line"} and bool(options.get("reference_line"))
    if reference:
        series.append({"name": str(options.get("reference_label") or "目标 / 阈值"),
                       "labels": list(series[0]["labels"]), "values": [target] * len(series[0]["labels"])})
    chart_data = CategoryChartData()
    chart_data.categories = list(series[0]["labels"])
    for item in series:
        chart_data.add_series(item["name"], list(item["values"]))
    chart_type = CHART_TYPE_MAP[kind]
    options = meta.get("options") if isinstance(meta.get("options"), dict) else {}
    radar_fill_index = options.get("radar_fill_series_index") if kind == "radar" else None
    if radar_fill_index is not None:
        if not isinstance(radar_fill_index, int) or isinstance(radar_fill_index, bool) or not 0 <= radar_fill_index < actual_count:
            raise ValueError("radar_fill_series_index must identify an existing radar series")
        radar_transparency = float(options.get("radar_fill_transparency", 65))
        if not 0 <= radar_transparency <= 100:
            raise ValueError("radar_fill_transparency must be between 0 and 100")
        chart_type = XL_CHART_TYPE.RADAR_FILLED
    shape = slide.shapes.add_chart(chart_type, *box, chart_data)
    chart = shape.chart
    if reference and kind == "bar":
        _move_reference_series_to_line_plot(chart, actual_count)
    chart.has_title = bool(_option(meta, "show_title"))
    with suppress(Exception):
        chart.has_legend = bool(_option(meta, "legend", default=actual_count > 1))
    _style_chart_text(chart, meta)
    _style_chart_colors(chart, series, meta.get("colors") if isinstance(meta.get("colors"), list) else [])
    for index in dashed_indices:
        chart.series[index].format.line.dash_style = MSO_LINE_DASH_STYLE.DASH
    if radar_fill_index is not None:
        for index, item in enumerate(chart.series):
            if index != radar_fill_index:
                item.format.fill.background()
                continue
            item.format.fill.solid()
            item.format.fill.fore_color.rgb = _rgb(str(options.get("radar_fill_color") or "#A8BEDF"))
            color = item._element.find("./" + qn("c:spPr") + "/" + qn("a:solidFill") + "/" + qn("a:srgbClr"))
            alpha = OxmlElement("a:alpha")
            alpha.set("val", str(round((100 - radar_transparency) * 1000)))
            color.append(alpha)
    point_colors = meta.get("point_colors")
    if actual_count == 1 and isinstance(point_colors, list) and point_colors:
        if target_category:
            point_colors = [point_colors[0]] * (len(series[0]["labels"]) - 1) + [point_colors[-1]]
        for point, color in zip(chart.series[0].points, point_colors):
            point.format.fill.solid()
            point.format.fill.fore_color.rgb = _rgb(str(color))
    if kind == "bar" and any(value < 0 for item in series[:actual_count] for value in item["values"]):
        chart.category_axis.tick_label_position = XL_TICK_LABEL_POSITION.LOW
        for index, item in enumerate(series[:actual_count]):
            native_series = chart.series[index]
            native_series.invert_if_negative = False
            for point_index, value in enumerate(item["values"]):
                if value >= 0:
                    continue
                # LibreOffice reads point inversion before the series setting.
                point = native_series.points[point_index].format.element
                invert = point.find(qn("c:invertIfNegative"))
                if invert is None:
                    invert = OxmlElement("c:invertIfNegative")
                    point.insert(1, invert)
                invert.set("val", "0")
    if kind == "line":
        for item in chart.series:
            item.marker.style = XL_MARKER_STYLE.CIRCLE
            item.marker.size = 4
    if reference:
        threshold = chart.series[actual_count]
        threshold.format.line.color.rgb = _rgb(str(options.get("reference_color") or "#91A0B6"))
        threshold.format.line.width = Pt(1)
        threshold.format.line.dash_style = MSO_LINE_DASH_STYLE.DASH
        threshold.marker.style = XL_MARKER_STYLE.NONE
        labels = OxmlElement("c:dLbls")
        delete = OxmlElement("c:delete")
        delete.set("val", "1")
        labels.append(delete)
        category = threshold._element.find(qn("c:cat"))
        if category is not None:
            category.addprevious(labels)
        else:
            threshold._element.append(labels)
    _style_chart_area_none(chart)
    if options.get("sparkline") is True:
        chart.has_legend = False
        # Axis-free trends reserve room for real point labels inside short rows.
        plot_area = chart._chartSpace.find(".//" + qn("c:plotArea"))
        layout = plot_area.find(qn("c:layout"))
        if layout is None:
            layout = OxmlElement("c:layout")
            plot_area.insert(0, layout)
        manual = OxmlElement("c:manualLayout")
        for tag, value in (("layoutTarget", "inner"), ("xMode", "factor"), ("yMode", "factor"),
                           ("wMode", "factor"), ("hMode", "factor"),
                           ("x", "0.04"), ("y", "0.16"), ("w", "0.92"), ("h", "0.58")):
            child = OxmlElement("c:" + tag)
            child.set("val", value)
            manual.append(child)
        layout.append(manual)
    return True


def _move_reference_series_to_line_plot(chart: Any, series_index: int) -> None:
    """Keep a constant threshold as an editable line on the same native axes."""
    bar = chart._chartSpace.find(".//" + qn("c:barChart"))
    series = chart.series[series_index]._element
    bar.remove(series)
    for child in list(series):
        if child.tag in {qn("c:invertIfNegative"), qn("c:shape")}:
            series.remove(child)
    line = OxmlElement("c:lineChart")
    grouping = OxmlElement("c:grouping")
    grouping.set("val", "standard")
    line.append(grouping)
    line.append(series)
    for axis in bar.findall(qn("c:axId")):
        line.append(copy.deepcopy(axis))
    bar.addnext(line)


def _add_waterfall_chart(slide: Any, meta: dict[str, Any], box: tuple[Any, Any, Any, Any]) -> bool:
    segments = _waterfall_segments(meta)
    if not segments:
        return False
    base, delta, point_colors, labels = _waterfall_values(segments)
    chart_data = CategoryChartData()
    chart_data.categories = labels
    chart_data.add_series("__waterfall_base__", base)
    chart_data.add_series("__waterfall_delta__", delta)
    shape = slide.shapes.add_chart(CHART_TYPE_MAP["waterfall"], *box, chart_data)
    chart = shape.chart
    chart.has_title = bool(_option(meta, "show_title"))
    with suppress(Exception):
        chart.has_legend = False
    _style_chart_text(chart, meta)
    series = list(getattr(chart, "series", []))
    if len(series) >= 2:
        with suppress(Exception):
            series[0].format.fill.background()
        with suppress(Exception):
            series[0].format.line.fill.background()
        for index, point in enumerate(series[1].points):
            color = point_colors[index] if index < len(point_colors) else point_colors[-1]
            with suppress(Exception):
                point.format.fill.solid()
                point.format.fill.fore_color.rgb = _rgb(color)
        _add_waterfall_ser_lines(chart)
    _style_chart_area_none(chart)
    return True


def _add_image(
    slide: Any,
    attrs: dict[str, str],
    native: dict[str, Any],
    viewbox: tuple[float, float],
    asset_roots: list[Path],
) -> bool:
    slot_id = _slot_id(attrs, "image-slot")
    meta = _merge(_slot_json(attrs, "data-image-slot"), _external(native, "images", slot_id))
    box = _slot_box_in(attrs, meta, viewbox, slide)
    path = _local_image_path(meta, asset_roots)
    if box is None or path is None:
        return False
    if _is_near_full_page(_slot_box_px(attrs, meta), viewbox):
        return False
    slide.shapes.add_picture(str(path), *box)
    return True


def _add_table(slide: Any, attrs: dict[str, str], native: dict[str, Any], viewbox: tuple[float, float]) -> bool:
    slot_id = _slot_id(attrs, "table-slot")
    meta = _merge(_slot_json(attrs, "data-table-slot"), _external(native, "tables", slot_id))
    rows = _table_rows(meta)
    box = _slot_box_in(attrs, meta, viewbox, slide)
    if not rows or box is None:
        return False
    columns = max(len(row) for row in rows)
    table = slide.shapes.add_table(len(rows), columns, *box).table
    has_header = meta.get("show_header", True)
    if not isinstance(has_header, bool):
        raise ValueError("show_header must be a boolean")
    table.first_row = has_header
    style = meta.get("style") if isinstance(meta.get("style"), dict) else {}
    column_styles = meta.get("column_styles") if isinstance(meta.get("column_styles"), list) else []
    widths = meta.get("column_widths")
    if isinstance(widths, list) and len(widths) == columns and all(isinstance(v, (int, float)) and v > 0 for v in widths):
        total = sum(widths)
        for index, value in enumerate(widths):
            table.columns[index].width = int(box[2] * value / total)
    heights = meta.get("row_heights")
    if isinstance(heights, list) and len(heights) == len(rows) and all(isinstance(v, (int, float)) and v > 0 for v in heights):
        total = sum(heights)
        for index, value in enumerate(heights):
            table.rows[index].height = int(box[3] * value / total)
    for row_index, row in enumerate(rows):
        for col_index in range(columns):
            cell = table.cell(row_index, col_index)
            cell.text = row[col_index] if col_index < len(row) else ""
            cell_style = style
            if col_index < len(column_styles) and isinstance(column_styles[col_index], dict):
                cell_style = {**style, **column_styles[col_index]}
            _style_table_cell(cell, row_index=row_index if has_header else -1, style=cell_style)
    return True


def _add_sankey(
    slide: Any,
    attrs: dict[str, str],
    native: dict[str, Any],
    viewbox: tuple[float, float],
) -> tuple[bool, dict[str, Any] | None]:
    slot_id = _slot_id(attrs, "sankey-slot")
    meta = _merge(_slot_json(attrs, "data-sankey-slot"), _external(native, "sankeys", slot_id))
    flows = _sankey_flows(meta)
    box = _slot_box_in(attrs, meta, viewbox, slide)
    if not flows or box is None:
        return False, None
    try:
        nodes, ribbons = _solve_sankey(_inches_tuple(box), flows)
        if not nodes:
            return False, {
                "reason": "sankey_geometry_empty",
                "slot_id": slot_id,
                "message": "explicit fallback: sankey geometry empty; never charts[].kind=sankey",
            }
        for ribbon in ribbons:
            _add_ribbon(slide, ribbon)
        for node in nodes:
            _add_sankey_node(slide, node)
        return True, None
    except Exception as exc:  # noqa: BLE001 - explicit fallback, never silent kind=sankey
        return False, {
            "reason": "sankey_overlay_failed",
            "slot_id": slot_id,
            "message": f"explicit fallback: {exc}; never charts[].kind=sankey",
        }


def _style_chart_text(chart: Any, meta: dict[str, Any]) -> None:
    style = meta.get("style") if isinstance(meta.get("style"), dict) else {}
    axis_color = _rgb(str(style.get("axis_text_color") or "#334155"))
    legend_color = _rgb(str(style.get("legend_text_color") or style.get("axis_text_color") or "#334155"))
    grid_color = style.get("grid_color")
    font_face = str(style.get("font_face") or "Microsoft YaHei")
    for axis_name in ("category_axis", "value_axis"):
        with suppress(Exception):
            axis = getattr(chart, axis_name)
            axis.tick_labels.font.size = Pt(9)
            axis.tick_labels.font.name = font_face
            axis.tick_labels.font.color.rgb = axis_color
    with suppress(Exception):
        if getattr(chart, "legend", None) is not None:
            chart.legend.font.size = Pt(9)
            chart.legend.font.name = font_face
            chart.legend.font.color.rgb = legend_color
    if grid_color:
        with suppress(Exception):
            chart.value_axis.has_major_gridlines = True
            chart.value_axis.major_gridlines.format.line.color.rgb = _rgb(str(grid_color))
    options = meta.get("options") if isinstance(meta.get("options"), dict) else {}
    axis_options = options.get("value_axis", meta.get("value_axis", {}))
    if isinstance(axis_options, dict):
        with suppress(Exception):
            if axis_options.get("format"):
                chart.value_axis.tick_labels.number_format = str(axis_options["format"])
            if axis_options.get("minimum") is not None:
                chart.value_axis.minimum_scale = float(axis_options["minimum"])
            if axis_options.get("maximum") is not None:
                chart.value_axis.maximum_scale = float(axis_options["maximum"])
            if axis_options.get("labels") is False:
                chart.value_axis.tick_label_position = XL_TICK_LABEL_POSITION.NONE
    if options.get("category_labels") is False:
        with suppress(Exception):
            chart.category_axis.tick_label_position = XL_TICK_LABEL_POSITION.NONE
    if _option(meta, "axes", default=True) is False or options.get("sparkline") is True:
        for axis_name in ("category_axis", "value_axis"):
            with suppress(Exception):
                axis = getattr(chart, axis_name)
                axis.visible = False
                axis.has_major_gridlines = False
    if _option(meta, "data_labels", default=False):
        with suppress(Exception):
            plot = chart.plots[0]
            plot.has_data_labels = True
            plot.data_labels.show_value = True
            plot.data_labels.font.name = font_face
            plot.data_labels.font.size = Pt(9)
            plot.data_labels.font.color.rgb = axis_color
            if options.get("data_label_wrap") is False or options.get("sparkline") is True:
                body = plot._element.find("./" + qn("c:dLbls") + "/" + qn("c:txPr") + "/" + qn("a:bodyPr"))
                if body is not None:
                    body.set("wrap", "none")
            positions = {"above": XL_LABEL_POSITION.ABOVE, "below": XL_LABEL_POSITION.BELOW,
                         "center": XL_LABEL_POSITION.CENTER}
            label_position = options.get("data_label_position", "below" if options.get("sparkline") is True else None)
            if label_position in positions:
                plot.data_labels.position = positions[label_position]
            if isinstance(axis_options, dict) and axis_options.get("format"):
                plot.data_labels.number_format = str(axis_options["format"])
            if options.get("data_label_layout") == "staggered":
                is_bar = meta.get("kind") == "bar"
                label_positions = ((XL_LABEL_POSITION.OUTSIDE_END, XL_LABEL_POSITION.INSIDE_END)
                                   if is_bar else (XL_LABEL_POSITION.ABOVE, XL_LABEL_POSITION.BELOW))
                for series in list(plot.series)[:len(_chart_series(meta))]:
                    for index, point in enumerate(series.points):
                        label = point.data_label
                        # The final focus bar keeps its label outside the dark fill.
                        position_index = ((len(series.points) - 1 - index) % 2
                                          if is_bar else index % 2)
                        label.position = label_positions[position_index]
                        label.font.name = font_face
                        label.font.size = Pt(9)
                        label.font.color.rgb = axis_color
                        # Individual label overrides do not reliably inherit format and wrapping.
                        label_element = label._dLbl
                        number_format = label_element.find(qn("c:numFmt"))
                        if number_format is None:
                            number_format = OxmlElement("c:numFmt")
                            label_element.insert(1, number_format)
                        number_format.set("formatCode", plot.data_labels.number_format)
                        number_format.set("sourceLinked", "0")
                        body = label_element.find("./" + qn("c:txPr") + "/" + qn("a:bodyPr"))
                        if body is not None:
                            body.set("wrap", "none")


def _style_chart_colors(chart: Any, series_spec: list[dict[str, Any]], extra_colors: list[Any]) -> None:
    colors = [item.get("color") for item in series_spec if item.get("color")]
    colors.extend(str(color) for color in extra_colors if str(color).strip())
    if not colors:
        return
    chart_series = list(getattr(chart, "series", []))
    for index, series in enumerate(chart_series):
        color = colors[index % len(colors)]
        with suppress(Exception):
            series.format.fill.solid()
            series.format.fill.fore_color.rgb = _rgb(str(color))
        with suppress(Exception):
            series.format.line.color.rgb = _rgb(str(color))
        if len(chart_series) == 1:
            for point_index, point in enumerate(series.points):
                point_color = colors[point_index % len(colors)]
                with suppress(Exception):
                    point.format.fill.solid()
                    point.format.fill.fore_color.rgb = _rgb(str(point_color))


def _style_chart_area_none(chart: Any) -> None:
    with suppress(Exception):
        chart_space = chart._chartSpace  # noqa: SLF001
        existing = chart_space.find(qn("c:spPr"))
        if existing is not None:
            for child in list(existing):
                existing.remove(child)
            sp_pr = existing
        else:
            sp_pr = chart_space.makeelement(qn("c:spPr"), {})
            chart_el = chart_space.find(qn("c:chart"))
            if chart_el is not None:
                chart_el.addnext(sp_pr)
            else:
                chart_space.append(sp_pr)
        from lxml import etree

        etree.SubElement(sp_pr, qn("a:noFill"))
        line = etree.SubElement(sp_pr, qn("a:ln"))
        etree.SubElement(line, qn("a:noFill"))


def _add_waterfall_ser_lines(chart: Any) -> None:
    with suppress(Exception):
        plots = getattr(chart, "plots", None)
        if not plots:
            return
        bar_chart = plots[0]._element  # noqa: SLF001
        if bar_chart.find(qn("c:serLines")) is not None:
            return
        from lxml import etree

        ser_lines = bar_chart.makeelement(qn("c:serLines"), {})
        sp_pr = etree.SubElement(ser_lines, qn("c:spPr"))
        line = etree.SubElement(sp_pr, qn("a:ln"))
        line.set("w", "9525")
        solid = etree.SubElement(line, qn("a:solidFill"))
        color = etree.SubElement(solid, qn("a:srgbClr"))
        color.set("val", "808080")
        first_ax = bar_chart.find(qn("c:axId"))
        if first_ax is not None:
            first_ax.addprevious(ser_lines)
        else:
            bar_chart.append(ser_lines)


def _style_table_cell(cell: Any, *, row_index: int, style: dict[str, Any]) -> None:
    font_size = float(style.get("font_size") or 11)
    text_color = str(
        (style.get("header_text_color") if row_index == 0 else style.get("text_color")) or "#0F172A"
    )
    fill = style.get("header_fill") if row_index == 0 else style.get("body_fill")
    if fill == "none":
        cell.fill.background()
    elif fill:
        cell.fill.solid()
        cell.fill.fore_color.rgb = _rgb(str(fill))
    with suppress(Exception):
        cell.vertical_anchor = MSO_ANCHOR.MIDDLE
    for side in ("left", "right", "top", "bottom"):
        margin = style.get(f"margin_{side}_pt")
        if isinstance(margin, (int, float)) and margin >= 0:
            setattr(cell, f"margin_{side}", Pt(margin))
    for paragraph in cell.text_frame.paragraphs:
        paragraph.alignment = PP_ALIGN.CENTER if row_index == 0 else PP_ALIGN.LEFT
        for run in paragraph.runs:
            font_face = str(style.get("font_face") or "Microsoft YaHei")
            run.font.name = font_face
            properties = run._r.get_or_add_rPr()
            east_asian = properties.find(qn("a:ea"))
            if east_asian is None:
                east_asian = properties.makeelement(qn("a:ea"))
                properties.append(east_asian)
            east_asian.set("typeface", font_face)
            run.font.size = Pt(font_size)
            run.font.bold = row_index == 0 or bool(style.get("bold"))
            run.font.color.rgb = _rgb(text_color)


def _solve_sankey(
    box: tuple[float, float, float, float],
    flows: list[tuple[str, str, float]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    order: list[str] = []
    for source, target, _value in flows:
        for name in (source, target):
            if name not in order:
                order.append(name)
    layer = dict.fromkeys(order, 0)
    for _ in range(len(order)):
        changed = False
        for source, target, _value in flows:
            if layer[target] < layer[source] + 1:
                layer[target] = layer[source] + 1
                changed = True
        if not changed:
            break
    inflow = dict.fromkeys(order, 0.0)
    outflow = dict.fromkeys(order, 0.0)
    for source, target, value in flows:
        outflow[source] += value
        inflow[target] += value
    throughput = {name: max(inflow[name], outflow[name], 0.0) for name in order}
    columns: dict[int, list[str]] = {}
    for name in order:
        columns.setdefault(layer[name], []).append(name)
    max_layer = max(layer.values()) if layer else 0
    max_column_value = max(sum(throughput[n] for n in col) for col in columns.values())
    if max_column_value <= 0:
        return [], []
    x, y, w, h = box
    node_gap = 0.04 * h
    max_nodes = max(len(col) for col in columns.values())
    value_scale = (h - node_gap * max(max_nodes - 1, 0)) / max_column_value
    node_w = min(0.18, w / (max_layer + 1) / 3 if max_layer else 0.18)
    node_rect: dict[str, tuple[float, float, float, float]] = {}
    nodes: list[dict[str, Any]] = []
    for layer_index, col in sorted(columns.items()):
        column_value = sum(throughput[n] for n in col)
        column_height = column_value * value_scale + node_gap * max(len(col) - 1, 0)
        cursor_y = y + max((h - column_height) / 2.0, 0.0)
        span = w - node_w
        node_x = x if max_layer == 0 else x + span * (layer_index / max_layer)
        for name in col:
            height = max(throughput[name] * value_scale, 0.08)
            node_rect[name] = (node_x, cursor_y, node_w, height)
            nodes.append(
                {
                    "name": name,
                    "layer": layer_index,
                    "max_layer": max_layer,
                    "box": node_rect[name],
                    "color": SANKEY_PALETTE[layer_index % len(SANKEY_PALETTE)],
                }
            )
            cursor_y += height + node_gap
    out_offset: dict[str, float] = {}
    in_offset: dict[str, float] = {}
    ribbons: list[dict[str, Any]] = []
    for source, target, value in flows:
        sx, sy, sw, _sh = node_rect[source]
        tx, ty, _tw, _th = node_rect[target]
        thickness = value * value_scale
        s_top = sy + out_offset.get(source, 0.0)
        t_top = ty + in_offset.get(target, 0.0)
        out_offset[source] = out_offset.get(source, 0.0) + thickness
        in_offset[target] = in_offset.get(target, 0.0) + thickness
        ribbons.append(
            {
                "corners": (
                    (sx + sw, s_top),
                    (sx + sw, s_top + thickness),
                    (tx, t_top + thickness),
                    (tx, t_top),
                ),
                "color": SANKEY_PALETTE[layer[source] % len(SANKEY_PALETTE)],
            }
        )
    return nodes, ribbons


def _add_ribbon(slide: Any, ribbon: dict[str, Any]) -> None:
    corners = [(Inches(x), Inches(y)) for x, y in ribbon["corners"]]
    builder = slide.shapes.build_freeform(corners[0][0], corners[0][1], scale=1.0)
    builder.add_line_segments(corners[1:], close=True)
    shape = builder.convert_to_shape()
    shape.fill.solid()
    shape.fill.fore_color.rgb = _rgb(ribbon["color"])
    with suppress(Exception):
        sp_pr = shape._element.spPr  # noqa: SLF001
        solid = sp_pr.find(qn("a:solidFill"))
        srgb = None if solid is None else solid.find(qn("a:srgbClr"))
        if srgb is not None:
            srgb.append(srgb.makeelement(qn("a:alpha"), {"val": "42000"}))
    with suppress(Exception):
        shape.line.fill.background()


def _add_sankey_node(slide: Any, node: dict[str, Any]) -> None:
    x, y, w, h = node["box"]
    shape = slide.shapes.add_shape(MSO_AUTO_SHAPE_TYPE.RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    shape.fill.solid()
    shape.fill.fore_color.rgb = _rgb(node["color"])
    with suppress(Exception):
        shape.line.fill.background()
    label_w, label_h = 1.35, 0.3
    center_y = y + h / 2.0 - label_h / 2.0
    if node["layer"] >= node["max_layer"]:
        left = max(x - label_w - 0.05, 0.0)
        align = PP_ALIGN.RIGHT
    else:
        left = x + w + 0.05
        align = PP_ALIGN.LEFT
    box = slide.shapes.add_textbox(Inches(left), Inches(center_y), Inches(label_w), Inches(label_h))
    frame = box.text_frame
    frame.word_wrap = True
    with suppress(Exception):
        frame.vertical_anchor = MSO_ANCHOR.MIDDLE
    paragraph = frame.paragraphs[0]
    paragraph.alignment = align
    run = paragraph.add_run()
    run.text = node["name"]
    run.font.size = Pt(9)
    run.font.name = "Microsoft YaHei"
    run.font.color.rgb = _rgb("#0F172A")


def _open_or_create(pptx_path: Path | None, slide_index: int) -> tuple[Any, Any]:
    if pptx_path is not None and pptx_path.is_file():
        presentation = Presentation(str(pptx_path))
        if not presentation.slides:
            slide = presentation.slides.add_slide(presentation.slide_layouts[6])
            return presentation, slide
        index = min(max(slide_index, 0), len(presentation.slides) - 1)
        return presentation, presentation.slides[index]
    presentation = Presentation()
    presentation.slide_width = Inches(SLIDE_IN[0])
    presentation.slide_height = Inches(SLIDE_IN[1])
    layout = presentation.slide_layouts[6]
    slide = presentation.slides.add_slide(layout)
    return presentation, slide


def _is_chart_slot(attrs: dict[str, str]) -> bool:
    return attrs.get("data-native-chart") == "true" or attrs.get("data-role") == "native-chart-slot"


def _is_table_slot(attrs: dict[str, str]) -> bool:
    return attrs.get("data-native-table") == "true" or attrs.get("data-role") == "native-table-slot"


def _is_sankey_slot(attrs: dict[str, str]) -> bool:
    return attrs.get("data-native-sankey") == "true" or attrs.get("data-role") == "native-sankey-slot"


def _is_image_slot(attrs: dict[str, str]) -> bool:
    return (
        attrs.get("data-native-image") == "true"
        or attrs.get("data-role") == "native-image-slot"
        or "data-image-slot" in attrs
    )


def _slot_id(attrs: dict[str, str], fallback: str) -> str:
    return str(attrs.get("id") or fallback)


def _slot_json(attrs: dict[str, str], key: str) -> dict[str, Any]:
    raw = attrs.get(key)
    if not raw:
        return {}
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        return {}
    return parsed if isinstance(parsed, dict) else {}


def _external(native: dict[str, Any], key: str, slot_id: str) -> dict[str, Any]:
    collection = native.get(key)
    if not isinstance(collection, list):
        return {}
    for item in collection:
        if not isinstance(item, dict):
            continue
        candidate = item.get("slot_id") or item.get("id") or item.get("slot")
        if str(candidate or "") == slot_id:
            return dict(item)
    return {}


def _merge(inline: dict[str, Any], external: dict[str, Any]) -> dict[str, Any]:
    return {**inline, **external}


def _declared_kind(meta: dict[str, Any], attr_kind: str | None = None) -> str:
    raw = str(meta.get("kind") or meta.get("chart_type") or attr_kind or "bar").strip().lower()
    if raw in KIND_ALIASES:
        return KIND_ALIASES[raw]
    return raw


def _chart_series(meta: dict[str, Any]) -> list[dict[str, Any]]:
    labels = [str(item) for item in (meta.get("labels") or [])] if isinstance(meta.get("labels"), list) else []
    raw = meta.get("series")
    if not isinstance(raw, list):
        data = meta.get("data")
        if isinstance(data, list) and data:
            series_labels = []
            values = []
            for item in data:
                if isinstance(item, dict):
                    series_labels.append(str(item.get("label") or item.get("name") or ""))
                    values.append(float(item.get("value") or 0))
            return [{"name": "Series 1", "labels": series_labels, "values": values, "color": None}]
        return []
    series: list[dict[str, Any]] = []
    for index, item in enumerate(raw):
        if not isinstance(item, dict):
            continue
        item_labels = [str(label) for label in item.get("labels")] if isinstance(item.get("labels"), list) else labels
        values = item.get("values")
        if not isinstance(values, list) or len(values) != len(item_labels):
            continue
        series.append(
            {
                "name": str(item.get("name") or item.get("label") or f"Series {index + 1}"),
                "labels": item_labels,
                "values": [float(value) for value in values],
                "color": item.get("color"),
            }
        )
    return series


def _waterfall_segments(meta: dict[str, Any]) -> list[dict[str, Any]]:
    raw = meta.get("segments")
    if not isinstance(raw, list):
        return []
    labels = [str(item) for item in meta.get("labels")] if isinstance(meta.get("labels"), list) else []
    segments: list[dict[str, Any]] = []
    for index, item in enumerate(raw):
        if not isinstance(item, dict):
            continue
        kind = str(item.get("type") or item.get("kind") or "").strip().lower()
        delta = item.get("delta")
        if kind not in {"total", "increase", "decrease"}:
            if delta is None:
                kind = "total"
            else:
                kind = "increase" if float(delta) >= 0 else "decrease"
        label = item.get("label") or item.get("name")
        if label is None and index < len(labels):
            label = labels[index]
        segments.append(
            {
                "kind": kind,
                "label": str(label or f"段{index + 1}"),
                "value": None if item.get("value") is None else float(item.get("value")),
                "delta": None if delta is None else float(delta),
            }
        )
    return segments


def _waterfall_values(
    segments: list[dict[str, Any]],
) -> tuple[list[float], list[float], list[str], list[str]]:
    running = 0.0
    base: list[float] = []
    delta: list[float] = []
    colors: list[str] = []
    labels: list[str] = []
    for segment in segments:
        labels.append(segment["label"])
        if segment["kind"] == "increase":
            magnitude = abs(segment["delta"] or 0.0)
            base.append(running)
            delta.append(magnitude)
            running += magnitude
            colors.append(WATERFALL_COLORS["increase"])
        elif segment["kind"] == "decrease":
            magnitude = abs(segment["delta"] or 0.0)
            running -= magnitude
            base.append(running)
            delta.append(magnitude)
            colors.append(WATERFALL_COLORS["decrease"])
        else:
            if segment["value"] is not None:
                running = float(segment["value"])
            base.append(0.0)
            delta.append(running)
            colors.append(WATERFALL_COLORS["total"])
    return base, delta, colors, labels


def _table_rows(meta: dict[str, Any]) -> list[tuple[str, ...]]:
    columns = tuple(str(item) for item in meta.get("columns")) if isinstance(meta.get("columns"), list) else ()
    raw = meta.get("rows") or meta.get("data")
    if not isinstance(raw, list):
        return []
    rows: list[tuple[str, ...]] = []
    for row in raw:
        if isinstance(row, dict):
            cells = row.get("cells")
            if isinstance(cells, list):
                rows.append(tuple(str(cell) for cell in cells))
            elif columns:
                rows.append(tuple(str(row.get(column, "")) for column in columns))
        elif isinstance(row, list):
            rows.append(tuple(str(cell) for cell in row))
    if columns and meta.get("show_header", True):
        rows.insert(0, columns)
    return rows


def _sankey_flows(meta: dict[str, Any]) -> list[tuple[str, str, float]]:
    raw = meta.get("flows")
    if not isinstance(raw, list):
        return []
    flows: list[tuple[str, str, float]] = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        source = item.get("source") or item.get("from")
        target = item.get("target") or item.get("to")
        value = item.get("value") or item.get("weight")
        try:
            numeric = float(value)
        except (TypeError, ValueError):
            continue
        if source is None or target is None or numeric <= 0:
            continue
        flows.append((str(source), str(target), numeric))
    return flows


def _option(meta: dict[str, Any], key: str, default: bool = False) -> bool:
    style = meta.get("style") if isinstance(meta.get("style"), dict) else {}
    if isinstance(style.get(key), bool):
        return bool(style[key])
    options = meta.get("options") if isinstance(meta.get("options"), dict) else style.get("options")
    if isinstance(options, dict) and isinstance(options.get(key), bool):
        return bool(options[key])
    return default


def _slot_box_px(attrs: dict[str, str], meta: dict[str, Any]) -> tuple[float, float, float, float] | None:
    raw = meta.get("box")
    attr_values = (
        _float(attrs.get("data-x") or attrs.get("x")),
        _float(attrs.get("data-y") or attrs.get("y")),
        _float(attrs.get("data-w") or attrs.get("width")),
        _float(attrs.get("data-h") or attrs.get("height")),
    )
    if not any(value is None for value in attr_values):
        values = attr_values
    elif isinstance(raw, dict):
        values = (
            _float(raw.get("x")),
            _float(raw.get("y")),
            _float(raw.get("w") or raw.get("width")),
            _float(raw.get("h") or raw.get("height")),
        )
    else:
        values = attr_values
    if any(value is None for value in values):
        return None
    x, y, w, h = (float(value) for value in values)  # type: ignore[union-attr]
    if w <= 0 or h <= 0:
        return None
    return x, y, w, h


def _slot_box_in(
    attrs: dict[str, str],
    meta: dict[str, Any],
    viewbox: tuple[float, float],
    slide: Any | None = None,
) -> tuple[Any, Any, Any, Any] | None:
    box = _slot_box_px(attrs, meta)
    if box is None:
        return None
    x, y, w, h = box
    slide_size = SLIDE_IN
    if slide is not None:
        presentation = slide.part.package.presentation_part.presentation
        slide_size = (presentation.slide_width.inches, presentation.slide_height.inches)
    sx = slide_size[0] / viewbox[0]
    sy = slide_size[1] / viewbox[1]
    return Inches(x * sx), Inches(y * sy), Inches(w * sx), Inches(h * sy)


def _inches_tuple(box: tuple[Any, Any, Any, Any]) -> tuple[float, float, float, float]:
    return tuple(value.inches if hasattr(value, "inches") else float(value) for value in box)  # type: ignore[return-value]


def _parse_viewbox(root: ET.Element) -> tuple[float, float]:
    raw = (root.get("viewBox") or "").split()
    if len(raw) == 4:
        with suppress(ValueError):
            return float(raw[2]), float(raw[3])
    return CANVAS


def _element_box_px(attrs: dict[str, str]) -> tuple[float, float, float, float] | None:
    values = (
        _float(attrs.get("x") or attrs.get("data-x")),
        _float(attrs.get("y") or attrs.get("data-y")),
        _float(attrs.get("width") or attrs.get("data-w")),
        _float(attrs.get("height") or attrs.get("data-h")),
    )
    if any(value is None for value in values):
        return None
    x, y, w, h = (float(value) for value in values)  # type: ignore[union-attr]
    if w <= 0 or h <= 0:
        return None
    return x, y, w, h


def _is_near_full_page(
    box: tuple[float, float, float, float] | None,
    viewbox: tuple[float, float],
) -> bool:
    if box is None:
        return False
    x, y, w, h = box
    vw, vh = viewbox
    return x <= vw * 0.02 and y <= vh * 0.02 and w >= vw * 0.96 and h >= vh * 0.96


def _is_remote_image_ref(value: Any) -> bool:
    text = str(value or "").strip().lower()
    return text.startswith(("http://", "https://", "/v1/files"))


def _has_preview_url(meta: dict[str, Any]) -> bool:
    return bool(str(meta.get("previewUrl") or meta.get("preview_url") or "").strip())


def _remote_image_refs(meta: dict[str, Any]) -> list[str]:
    hits: list[str] = []
    for key in ("asset_key", "key", "path", "file", "url", "src", "href", "previewUrl", "preview_url"):
        value = meta.get(key)
        if _is_remote_image_ref(value):
            hits.append(str(value))
    return hits


def _asset_roots(assets_dir: Path | None) -> list[Path]:
    roots: list[Path] = []
    if assets_dir is not None:
        roots.append(Path(assets_dir))
    roots.append(Path.cwd())
    seen: list[Path] = []
    for root in roots:
        resolved = root.resolve()
        if resolved not in seen:
            seen.append(resolved)
    return seen


def _local_image_path(meta: dict[str, Any], asset_roots: list[Path]) -> Path | None:
    candidates: list[str] = []
    for key in ("asset_key", "key", "path", "file"):
        value = meta.get(key)
        if isinstance(value, str) and value.strip():
            candidates.append(value.strip())
    url = meta.get("url")
    if isinstance(url, str) and url.strip() and not _is_remote_image_ref(url):
        candidates.append(url.strip())
    for raw in candidates:
        if _is_remote_image_ref(raw):
            continue
        path = Path(raw)
        options = [path] if path.is_absolute() else [root / path for root in asset_roots]
        for option in options:
            if option.is_file() and option.suffix.lower() in RASTER_SUFFIXES:
                return option
    return None


def _float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _rgb(value: str) -> RGBColor:
    text = str(value or "334155").strip().lstrip("#")
    if len(text) != 6:
        text = "334155"
    return RGBColor(int(text[0:2], 16), int(text[2:4], 16), int(text[4:6], 16))


def _resolve_native_data(svg_path: Path, svg_text: str, native_arg: str | None) -> tuple[dict[str, Any] | None, Path | None, list[dict[str, Any]]]:
    issues: list[dict[str, Any]] = []
    candidates: list[Path] = []
    if native_arg:
        candidates.append(Path(native_arg))
    try:
        root = ET.fromstring(svg_text)
        ref = (root.get("data-native-data-ref") or "").strip()
        if ref:
            ref_path = Path(ref)
            candidates.append(ref_path if ref_path.is_absolute() else svg_path.parent / ref_path)
    except ET.ParseError:
        pass
    candidates.append(svg_path.parent / "native-data.json")
    for path in candidates:
        if path.is_file():
            return json.loads(path.read_text(encoding="utf-8")), path, issues
    issues.append(
        {
            "code": "NATIVE_DATA_FILE_NOT_FOUND",
            "message": "missing native-data.json (Ubrio save_file → write this sidecar next to source.svg)",
            "severity": "error",
        }
    )
    return None, None, issues


def expand_page_icons(svg_text: str, icons_root: Path | None = None) -> dict[str, Any]:
    """Inline data-icon-id slots; unknown icon_id is blocking."""

    result = _icon_lib.expand_svg_icon_slots(
        svg_text,
        icons_root=icons_root or _icon_lib.default_icons_root(),
    )
    return {
        "ok": result.ok,
        "svg": result.svg,
        "expanded_count": result.expanded_count,
        "issues": result.issues,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate/overlay native chart/table/sankey/image slots with python-pptx")
    parser.add_argument("--svg", required=True, help="source.svg with native-*-slot geometry")
    parser.add_argument("--native-data", help="native-data.json (default: data-native-data-ref or sibling)")
    parser.add_argument("--pptx", help="existing PPTX to overlay; omit to create a blank 13.333x7.5 slide")
    parser.add_argument("--output", help="output PPTX path")
    parser.add_argument("--validate-only", action="store_true")
    parser.add_argument("--slide-index", type=int, default=0)
    parser.add_argument("--assets-dir", help="directory for images[].asset_key (default: SVG parent)")
    parser.add_argument("--write-expanded", help="write SVG after expanding data-icon-id slots")
    args = parser.parse_args(argv)
    svg_path = Path(args.svg)
    svg_text = svg_path.read_text(encoding="utf-8")
    icon_report = expand_page_icons(svg_text)
    native_data, _native_path, file_issues = _resolve_native_data(svg_path, svg_text, args.native_data)
    assets_dir = Path(args.assets_dir) if args.assets_dir else svg_path.parent
    report = diagnose_native_slots(svg_text, native_data, assets_dir=assets_dir)
    report["issues"] = list(icon_report["issues"]) + file_issues + report["issues"]
    report["icon_expanded_count"] = icon_report["expanded_count"]
    report["ok"] = not report["issues"]
    if icon_report["ok"] and args.write_expanded:
        Path(args.write_expanded).write_text(icon_report["svg"], encoding="utf-8")
        report["expanded_svg"] = str(Path(args.write_expanded))
    if args.validate_only:
        json.dump(report, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")
        return 0 if report["ok"] else 2
    if not args.output:
        parser.error("--output is required unless --validate-only")
    if not report["ok"]:
        json.dump(report, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")
        return 2
    result = overlay_native_slots(
        svg_text=svg_text,
        native_data=native_data,
        output=Path(args.output),
        pptx_path=Path(args.pptx) if args.pptx else None,
        slide_index=args.slide_index,
        assets_dir=assets_dir,
    )
    result["issues"] = report["issues"]
    result["warnings"] = report["warnings"]
    result["icon_expanded_count"] = report["icon_expanded_count"]
    json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
