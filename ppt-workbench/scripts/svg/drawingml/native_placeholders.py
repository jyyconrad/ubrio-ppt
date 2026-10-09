"""SVG native slot 占位内容治理：转换前剥离 slot 组内占位文字并做几何自检。

背景：native chart/table/image slot 的最终内容由渲染后 overlay 在 slot box 原位
叠加（`svg_native_chart_overlay` 等）。模型按语料在 slot 分组内保留的占位说明、
外框内标题等 `<text>`，转换时会变成真实 DrawingML 文字形状，再被原生图表/表格
盖住或透底串行——“嵌入图表后位置和内容挤占串行”的直接来源。

约定（与 `layout-native-chart-slot.md` 语料契约一致）：
- slot 分组内的 `<text>` 一律视为“仅供 SVG 预览理解”的占位说明，转换前确定性
  移除，不进入最终 PPTX；真实标题/洞察/来源必须写在 slot 分组外并预留空间。
- slot 分组内标记 ``data-preview-only="true"`` 的微图/微表预览组会整体移除；
  未标记的外框和底板仍保留。
- slot box 必须完整落在画布内（越界是确定性缺陷，blocking）；图表 slot 过小、
  剥离后仍有外部文字锚点落入 slot box 时给出 warning，交模型修复。

与 text_autoscale 相同，本 pass 只改写送入 vendor converter 的副本，不触碰
会话原始 SVG 文件。
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import Any

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


def _parse_viewbox(root: ET.Element) -> tuple[float, float]:
    raw = (root.get("viewBox") or root.get("viewbox") or "").split()
    if len(raw) >= 4:
        try:
            return float(raw[2]), float(raw[3])
        except ValueError:
            pass
    return 1280.0, 720.0


SVG_NS = "http://www.w3.org/2000/svg"

# 画布越界容差（SVG px）：浮点坐标误差与描边宽度不算越界。
_CANVAS_BOUNDS_TOLERANCE = 2.0
# 判定外部文字锚点落入 slot box 的内缩余量，贴边标注不误报。
_TEXT_OVERLAP_INSET = 8.0
# 图表可读的最小 slot 尺寸（1280x720 坐标系）：低于该值坐标轴/图例挤压不可读。
_CHART_SLOT_MIN_WIDTH = 320.0
_CHART_SLOT_MIN_HEIGHT = 200.0
_MICRO_CHART_SLOT_MIN_WIDTH = 140.0
_MICRO_CHART_SLOT_MIN_HEIGHT = 80.0
_SPARKLINE_SLOT_MIN_WIDTH = 140.0
_SPARKLINE_SLOT_MIN_HEIGHT = 48.0
_STRIPPED_SAMPLE_LIMIT = 5
_STRIPPED_SAMPLE_TEXT_LIMIT = 40


@dataclass(frozen=True)
class NativeSlotPlaceholderReport:
    """剥离与几何自检结果；``applied`` 为 True 时调用方应改用返回的 SVG。"""

    applied: bool
    stripped_count: int
    stripped_samples: tuple[dict[str, str], ...]
    blocking_issues: tuple[dict[str, Any], ...]
    warnings: tuple[dict[str, Any], ...]
    stripped_preview_count: int = 0


_EMPTY_REPORT = NativeSlotPlaceholderReport(
    applied=False,
    stripped_count=0,
    stripped_samples=(),
    blocking_issues=(),
    warnings=(),
    stripped_preview_count=0,
)


@dataclass(frozen=True)
class _SlotInfo:
    element: ET.Element
    kind: str
    slot_id: str
    box: tuple[float, float, float, float] | None
    variant: str | None


def strip_native_slot_placeholder_texts(
    svg_content: str,
) -> tuple[str, NativeSlotPlaceholderReport]:
    """剥离 slot 组内占位 `<text>` 并返回几何自检报告。

    SVG 解析失败时原样返回（格式问题由 input_gate 负责拦截），报告为空。
    """

    try:
        root = ET.fromstring(svg_content)
    except ET.ParseError:
        return svg_content, _EMPTY_REPORT

    slots = _collect_slots(root)
    if not slots:
        return svg_content, _EMPTY_REPORT

    viewbox = _parse_viewbox(root)
    parent_map = {child: parent for parent in root.iter() for child in parent}

    stripped_preview_count = 0
    for slot in slots:
        for preview in _top_level_preview_elements(slot.element, parent_map):
            parent = parent_map.get(preview)
            if parent is None:
                continue
            parent.remove(preview)
            stripped_preview_count += 1

    # 预览组移除后重新建立父映射，避免继续处理已脱离树的占位文字。
    parent_map = {child: parent for parent in root.iter() for child in parent}

    stripped_samples: list[dict[str, str]] = []
    stripped_count = 0
    for slot in slots:
        for text_element in _descendant_texts(slot.element):
            parent = parent_map.get(text_element)
            if parent is None:
                continue
            content = _text_content(text_element)
            if len(stripped_samples) < _STRIPPED_SAMPLE_LIMIT and content:
                stripped_samples.append(
                    {
                        "slot_id": slot.slot_id,
                        "text": content[:_STRIPPED_SAMPLE_TEXT_LIMIT],
                    }
                )
            parent.remove(text_element)
            stripped_count += 1

    blocking_issues = _diagnose_out_of_canvas(slots, viewbox)
    warnings = [
        *_diagnose_chart_slot_size(slots),
        *_diagnose_surviving_text_overlap(root, slots),
    ]

    report = NativeSlotPlaceholderReport(
        applied=stripped_count > 0 or stripped_preview_count > 0,
        stripped_count=stripped_count,
        stripped_samples=tuple(stripped_samples),
        blocking_issues=tuple(blocking_issues),
        warnings=tuple(warnings),
        stripped_preview_count=stripped_preview_count,
    )
    if not report.applied:
        return svg_content, report
    ET.register_namespace("", SVG_NS)
    ET.register_namespace("xlink", "http://www.w3.org/1999/xlink")
    return ET.tostring(root, encoding="unicode"), report


def native_slot_placeholder_payload(
    report: NativeSlotPlaceholderReport,
) -> dict[str, Any]:
    """conversion_report / validate warnings 使用的紧凑载荷。"""

    payload: dict[str, Any] = {
        "stripped_text_count": report.stripped_count,
    }
    if report.stripped_samples:
        payload["stripped_samples"] = [dict(item) for item in report.stripped_samples]
    if report.stripped_preview_count:
        payload["stripped_preview_count"] = report.stripped_preview_count
    if report.warnings:
        payload["warnings"] = [dict(item) for item in report.warnings]
    return payload


def _collect_slots(root: ET.Element) -> tuple[_SlotInfo, ...]:
    slots: list[_SlotInfo] = []
    for element in root.iter():
        attrs = element.attrib
        if _is_chart_slot(attrs):
            kind = "chart"
        elif _is_table_slot(attrs):
            kind = "table"
        elif _is_sankey_slot(attrs):
            # 桑基槽同样是原生内容独占区：组内占位文字剥离 + 越界 blocking 一致适用。
            kind = "sankey"
        elif _is_image_slot(attrs):
            kind = "image"
        else:
            continue
        slot_id = str(attrs.get("id") or f"{kind}-slot-{len(slots) + 1}")
        slots.append(
            _SlotInfo(
                element=element,
                kind=kind,
                slot_id=slot_id,
                box=_attr_box(attrs),
                variant=(str(attrs.get("data-native-chart-variant") or "").strip() or None),
            )
        )
    return tuple(slots)


def _attr_box(attrs: dict[str, str]) -> tuple[float, float, float, float] | None:
    values = (
        _float_or_none(attrs.get("data-x") or attrs.get("x")),
        _float_or_none(attrs.get("data-y") or attrs.get("y")),
        _float_or_none(attrs.get("data-w") or attrs.get("width")),
        _float_or_none(attrs.get("data-h") or attrs.get("height")),
    )
    if any(value is None for value in values):
        return None
    x, y, w, h = (float(value) for value in values if value is not None)
    if w <= 0 or h <= 0:
        return None
    return x, y, w, h


def _descendant_texts(element: ET.Element) -> tuple[ET.Element, ...]:
    return tuple(
        candidate
        for candidate in element.iter()
        if candidate is not element and _local_name(candidate.tag) == "text"
    )


def _top_level_preview_elements(
    slot: ET.Element,
    parent_map: dict[ET.Element, ET.Element],
) -> tuple[ET.Element, ...]:
    """返回 slot 内最外层 preview-only 元素，嵌套预览只计一次。"""

    previews: list[ET.Element] = []
    for candidate in slot.iter():
        if candidate is slot or candidate.attrib.get("data-preview-only") != "true":
            continue
        ancestor = parent_map.get(candidate)
        nested = False
        while ancestor is not None and ancestor is not slot:
            if ancestor.attrib.get("data-preview-only") == "true":
                nested = True
                break
            ancestor = parent_map.get(ancestor)
        if not nested:
            previews.append(candidate)
    return tuple(previews)


def _local_name(tag: Any) -> str:
    text = str(tag)
    return text.rsplit("}", 1)[-1] if "}" in text else text


def _text_content(element: ET.Element) -> str:
    return "".join(element.itertext()).strip()


def _diagnose_out_of_canvas(
    slots: tuple[_SlotInfo, ...],
    viewbox: tuple[float, float],
) -> list[dict[str, Any]]:
    width, height = viewbox
    issues: list[dict[str, Any]] = []
    for slot in slots:
        if slot.box is None:
            continue
        x, y, w, h = slot.box
        if (
            x >= -_CANVAS_BOUNDS_TOLERANCE
            and y >= -_CANVAS_BOUNDS_TOLERANCE
            and x + w <= width + _CANVAS_BOUNDS_TOLERANCE
            and y + h <= height + _CANVAS_BOUNDS_TOLERANCE
        ):
            continue
        issues.append(
            {
                "code": "NATIVE_SLOT_BOX_OUT_OF_CANVAS",
                "message": (
                    f"native {slot.kind} slot 越出画布：box=({x:g},{y:g},{w:g},{h:g})，"
                    f"画布为 {width:g}x{height:g}。"
                ),
                "slot_id": slot.slot_id,
                "box": {"x": x, "y": y, "w": w, "h": h},
                "canvas": {"width": width, "height": height},
                "fix_hint": "调整 data-x/data-y/data-w/data-h，让 slot 完整落在画布内并与相邻内容留出间距。",
            }
        )
    return issues


def _diagnose_chart_slot_size(slots: tuple[_SlotInfo, ...]) -> list[dict[str, Any]]:
    warnings: list[dict[str, Any]] = []
    for slot in slots:
        if slot.kind != "chart" or slot.box is None:
            continue
        _x, _y, w, h = slot.box
        is_micro = (slot.variant or "").lower() == "micro"
        is_sparkline = (slot.variant or "").lower() == "sparkline"
        min_width = (
            _SPARKLINE_SLOT_MIN_WIDTH if is_sparkline else (
                _MICRO_CHART_SLOT_MIN_WIDTH if is_micro else _CHART_SLOT_MIN_WIDTH)
        )
        min_height = (
            _SPARKLINE_SLOT_MIN_HEIGHT if is_sparkline else (
                _MICRO_CHART_SLOT_MIN_HEIGHT if is_micro else _CHART_SLOT_MIN_HEIGHT)
        )
        if w >= min_width and h >= min_height:
            continue
        warnings.append(
            {
                "code": "NATIVE_CHART_SLOT_TOO_SMALL",
                "message": (
                    f"chart slot {slot.slot_id} 尺寸 {w:g}x{h:g} 偏小，坐标轴与图例会挤压不可读；"
                    f"建议不小于 {min_width:g}x{min_height:g}。"
                ),
                "slot_id": slot.slot_id,
                "box": {"x": _x, "y": _y, "w": w, "h": h},
            }
        )
    return warnings


def _diagnose_surviving_text_overlap(
    root: ET.Element,
    slots: tuple[_SlotInfo, ...],
) -> list[dict[str, Any]]:
    """剥离后仍存活的 `<text>` 锚点若落入 slot box，最终会被原生内容盖住。"""

    boxed_slots = [slot for slot in slots if slot.box is not None]
    if not boxed_slots:
        return []
    warnings: list[dict[str, Any]] = []
    for element in root.iter():
        if _local_name(element.tag) != "text":
            continue
        # transform 定位的文本锚点无法用 x/y 直接判定，保守跳过。
        if element.attrib.get("transform"):
            continue
        x = _float_or_none(element.attrib.get("x"))
        y = _float_or_none(element.attrib.get("y"))
        if x is None or y is None:
            continue
        for slot in boxed_slots:
            bx, by, bw, bh = slot.box  # type: ignore[misc]
            if (
                bx + _TEXT_OVERLAP_INSET <= x <= bx + bw - _TEXT_OVERLAP_INSET
                and by + _TEXT_OVERLAP_INSET <= y <= by + bh - _TEXT_OVERLAP_INSET
            ):
                warnings.append(
                    {
                        "code": "NATIVE_SLOT_TEXT_OVERLAP",
                        "message": (
                            f"文字「{_text_content(element)[:_STRIPPED_SAMPLE_TEXT_LIMIT]}」"
                            f"锚点 ({x:g},{y:g}) 落在 native {slot.kind} slot {slot.slot_id} 区域内，"
                            "渲染后会被原生内容覆盖或透底串行。"
                        ),
                        "slot_id": slot.slot_id,
                        "anchor": {"x": x, "y": y},
                        "fix_hint": "把标题/洞察/来源移到 slot box 之外（上方或下方预留行），slot box 只留给原生内容。",
                    }
                )
                break
    return warnings


def _float_or_none(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(str(value).strip())
    except ValueError:
        return None
