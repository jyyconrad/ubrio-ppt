"""从结构化 JSON 生成模板系列中的复杂可编辑 SVG 组合组件。"""

from __future__ import annotations

import argparse
import html
import json
import math
import re
from collections.abc import Callable
from contextvars import ContextVar
from pathlib import Path
from typing import Any

W, H = 1280, 720
SCHEMA_VERSION = "series_composite_svg/v1"
FONT = "Microsoft YaHei, Arial"
COMPONENT_MANIFEST_VERSION = "component-manifest/v1"

_OVERFLOW_EVENTS: ContextVar[list[dict[str, Any]] | None] = ContextVar(
    "series_composite_overflow_events",
    default=None,
)


class SpecError(ValueError):
    """输入不满足组件合同。"""


SERIES_THEMES: dict[str, dict[str, str]] = {
    "rd_efficiency_blue": {
        "surface": "#FFFFFF",
        "surface_alt": "#EDF4FB",
        "title_text": "#102A43",
        "body_text": "#334E68",
        "muted_text": "#627D98",
        "accent": "#155A9C",
        "accent_alt": "#2F80C0",
        "contrast": "#18A999",
        "risk": "#C64B55",
        "border": "#C9D8E6",
    },
    "blue_summary_pyramid": {
        "surface": "#FFFFFF",
        "surface_alt": "#EAF2FA",
        "title_text": "#17324D",
        "body_text": "#3D5266",
        "muted_text": "#6B7F93",
        "accent": "#2367A2",
        "accent_alt": "#4F94C9",
        "contrast": "#E6A23C",
        "risk": "#C45353",
        "border": "#CAD8E5",
    },
    "blue_green_diagnostic": {
        "surface": "#FFFFFF",
        "surface_alt": "#EEF7F5",
        "title_text": "#12344D",
        "body_text": "#34505F",
        "muted_text": "#6B7F86",
        "accent": "#1F6F9E",
        "accent_alt": "#20A486",
        "contrast": "#20A486",
        "risk": "#C44C58",
        "border": "#CADDE0",
    },
    "violet_quarterly_overview": {
        "surface": "#FFFFFF",
        "surface_alt": "#F3EFF9",
        "title_text": "#37214F",
        "body_text": "#554366",
        "muted_text": "#806F8E",
        "accent": "#5A2A82",
        "accent_alt": "#8A5BB2",
        "contrast": "#D39C38",
        "risk": "#C6536A",
        "border": "#D9CDE3",
    },
    "violet_calendar": {
        "surface": "#FFFFFF",
        "surface_alt": "#F5F0FA",
        "title_text": "#3A2352",
        "body_text": "#584565",
        "muted_text": "#806E8C",
        "accent": "#62308B",
        "accent_alt": "#9769BA",
        "contrast": "#C79A35",
        "risk": "#C24D67",
        "border": "#DACEE4",
    },
    "violet_planning_5w1h": {
        "surface": "#FFFFFF",
        "surface_alt": "#F3EDF8",
        "title_text": "#3B2255",
        "body_text": "#594667",
        "muted_text": "#81718E",
        "accent": "#5B2784",
        "accent_alt": "#8E5CB2",
        "contrast": "#D5A33F",
        "risk": "#BE4C68",
        "border": "#D7C9E1",
    },
    "violet_improvement": {
        "surface": "#FFFFFF",
        "surface_alt": "#F5F0F9",
        "title_text": "#3A2252",
        "body_text": "#564463",
        "muted_text": "#806E8C",
        "accent": "#5D2A86",
        "accent_alt": "#8D5CB1",
        "contrast": "#A66FC7",
        "risk": "#C14F6B",
        "border": "#D8CCE2",
    },
    "violet_performance": {
        "surface": "#FFFFFF",
        "surface_alt": "#F2ECF7",
        "title_text": "#361F4D",
        "body_text": "#554262",
        "muted_text": "#7C6B88",
        "accent": "#4D1F73",
        "accent_alt": "#7C4AA0",
        "contrast": "#D3A23F",
        "risk": "#C04F69",
        "border": "#D5C8DF",
    },
    "violet_achievements": {
        "surface": "#FFFFFF",
        "surface_alt": "#F4EEF8",
        "title_text": "#351E4C",
        "body_text": "#544060",
        "muted_text": "#7D6A88",
        "accent": "#54247C",
        "accent_alt": "#8351A8",
        "contrast": "#C99536",
        "risk": "#C24E68",
        "border": "#D7C9E0",
    },
}


PATTERN_CONTRACTS: dict[str, str] = {
    "phased_roadmap_matrix": "stages 2-4",
    "diagnostic_insight_grid": "issues 2-4",
    "shared_source_platform_value": "platforms 2-4, values 2-4",
    "stage_mechanism_scorecard": "stages 3-7, mechanisms 1-2, metrics 2-4",
    "operating_model_blueprint": "enablers 2, layers 3-5, collaborations 1-2, values 3-5",
    "retrospect_outlook_pyramid": "periods 3, pyramid_layers 3",
    "duotone_problem_improve": "problems 2-4, responses 2-4",
    "calendar_summary_rail": "months 3-6, events 1-8, summaries 1-3",
    "target_action_timeline": "periods 4-6",
    "north_star_kpi_roof": "principles 3, metrics 3-5",
    "arrow_ribbon_metrics": "items 3-6",
    "highlight_matrix_core": "items 4, core_labels 4",
    "sectioned_evidence_dashboard": "sections 1-2, cards per section 2-3, optional closure steps 3-5",
    "native_chart_panel": "one primary bar/line chart with 2-12 labels and 1-3 series",
    "insight_text_card": "one insight card with 1-3 evidence-backed bullets",
    "chart_insight_card": "one card with one chart/table/metric/icon fact and one insight",
    "full_width_rect_step_flow": "steps 3-6, optional terminal action",
}


def _esc(value: Any) -> str:
    return html.escape(str(value if value is not None else ""), quote=True)


def _slug(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9_-]+", "-", value.strip()).strip("-")
    return slug or "item"


def _list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def _dict(value: Any, *, field: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise SpecError(f"{field} must be an object")
    return value


def _items(
    data: dict[str, Any],
    field: str,
    minimum: int,
    maximum: int,
) -> list[Any]:
    items = _list(data.get(field))
    if not minimum <= len(items) <= maximum:
        raise SpecError(f"{field} must contain {minimum}-{maximum} items")
    return items


def _exact_items(data: dict[str, Any], field: str, count: int) -> list[Any]:
    items = _list(data.get(field))
    if len(items) != count:
        raise SpecError(f"{field} must contain exactly {count} items")
    return items


def _region(
    spec: dict[str, Any],
    *,
    minimum_width: float = 640,
    minimum_height: float = 300,
) -> tuple[float, float, float, float]:
    raw = spec.get("region") or {"x": 72, "y": 112, "w": 1136, "h": 520}
    if not isinstance(raw, dict):
        raise SpecError("region must be an object")
    try:
        x = float(raw.get("x", 72))
        y = float(raw.get("y", 112))
        w = float(raw.get("w", 1136))
        h = float(raw.get("h", 520))
    except (TypeError, ValueError) as exc:
        raise SpecError("region values must be numeric") from exc
    if w < minimum_width or h < minimum_height:
        raise SpecError(
            f"region must be at least {minimum_width:g}x{minimum_height:g}"
        )
    if x < 0 or y < 0 or x + w > W or y + h > H:
        raise SpecError("region must stay inside the 1280x720 canvas")
    return x, y, w, h


def _theme(spec: dict[str, Any]) -> dict[str, str]:
    series_id = str(spec.get("series_id") or "rd_efficiency_blue")
    if series_id not in SERIES_THEMES:
        raise SpecError(f"unknown series_id: {series_id}")
    theme = dict(SERIES_THEMES[series_id])
    overrides = spec.get("theme") or {}
    if not isinstance(overrides, dict):
        raise SpecError("theme must be an object")
    for key, value in overrides.items():
        if key in theme and isinstance(value, str) and value.strip():
            theme[key] = value.strip()
    return theme


def _wrap(value: Any, width: int, lines: int) -> list[str]:
    text = str(value or "").strip()
    if not text:
        return []
    chunks: list[str] = []
    current = ""
    for char in text:
        if len(current) >= width:
            chunks.append(current)
            current = ""
        current += char
    if current:
        chunks.append(current)
    original_chunks = list(chunks)
    if len(chunks) > lines:
        chunks = chunks[:lines]
        chunks[-1] = chunks[-1][:-1] + "…"
        events = _OVERFLOW_EVENTS.get()
        if events is not None:
            events.append(
                {
                    "id": f"text-overflow-{len(events) + 1}",
                    "kind": "text_clamped",
                    "original_text": text,
                    "rendered_text": "".join(chunks),
                    "original_line_count": len(original_chunks),
                    "max_chars_per_line": width,
                    "max_lines": lines,
                }
            )
    return chunks


def _text(
    x: float,
    y: float,
    value: Any,
    *,
    size: float,
    fill: str,
    weight: int = 400,
    anchor: str = "start",
    max_chars: int = 16,
    max_lines: int = 2,
    line_height: float | None = None,
) -> str:
    lines = _wrap(value, max_chars, max_lines)
    if not lines:
        return ""
    line_height = line_height or size * 1.35
    tspans = []
    for index, line in enumerate(lines):
        dy = 0 if index == 0 else line_height
        tspans.append(f'<tspan x="{x:.1f}" dy="{dy:.1f}">{_esc(line)}</tspan>')
    return (
        f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" '
        f'fill="{_esc(fill)}" font-family="{FONT}" font-size="{size:.1f}" '
        f'font-weight="{weight}">{"".join(tspans)}</text>'
    )


def _rect(
    x: float,
    y: float,
    w: float,
    h: float,
    *,
    fill: str,
    stroke: str = "none",
    rx: float = 0,
    opacity: float | None = None,
) -> str:
    opacity_attr = "" if opacity is None else f' fill-opacity="{opacity:.3f}"'
    return (
        f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" '
        f'rx="{rx:.1f}" fill="{_esc(fill)}" stroke="{_esc(stroke)}"{opacity_attr}/>'
    )


def _circle(cx: float, cy: float, r: float, *, fill: str, stroke: str = "none") -> str:
    return (
        f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" '
        f'fill="{_esc(fill)}" stroke="{_esc(stroke)}"/>'
    )


def _line(
    x1: float,
    y1: float,
    x2: float,
    y2: float,
    *,
    stroke: str,
    width: float = 1,
    dash: str | None = None,
) -> str:
    dash_attr = "" if dash is None else f' stroke-dasharray="{dash}"'
    return (
        f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
        f'stroke="{_esc(stroke)}" stroke-width="{width:.1f}"{dash_attr}/>'
    )


def _polygon(points: list[tuple[float, float]], *, fill: str, stroke: str = "none") -> str:
    point_text = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    return f'<polygon points="{point_text}" fill="{_esc(fill)}" stroke="{_esc(stroke)}"/>'


def _polyline(
    points: list[tuple[float, float]],
    *,
    stroke: str,
    width: float = 1,
) -> str:
    point_text = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    return (
        f'<polyline points="{point_text}" fill="none" '
        f'stroke="{_esc(stroke)}" stroke-width="{width:.1f}"/>'
    )


def _badge(cx: float, cy: float, label: Any, theme: dict[str, str], *, fill: str | None = None) -> str:
    color = fill or theme["accent"]
    return "".join(
        (
            _circle(cx, cy, 18, fill=theme["surface"], stroke=color),
            _circle(cx, cy, 14, fill=color),
            _text(
                cx,
                cy + 5,
                label,
                size=12,
                fill=theme["surface"],
                weight=700,
                anchor="middle",
                max_chars=3,
                max_lines=1,
            ),
        )
    )


def _section_title(
    x: float,
    y: float,
    w: float,
    title: str,
    theme: dict[str, str],
) -> str:
    if not title:
        return ""
    return "".join(
        (
            _rect(x, y, 7, 34, fill=theme["accent"], rx=3),
            _text(x + 20, y + 26, title, size=22, fill=theme["title_text"], weight=700, max_chars=34, max_lines=1),
            _line(x, y + 44, x + w, y + 44, stroke=theme["border"]),
        )
    )


def _metric_card(
    x: float,
    y: float,
    w: float,
    h: float,
    item: Any,
    theme: dict[str, str],
    *,
    index: int,
) -> str:
    data = item if isinstance(item, dict) else {"title": str(item)}
    label = data.get("metric_label") or data.get("title") or f"指标{index}"
    value = data.get("metric_value") or data.get("value") or "-"
    detail = data.get("detail") or data.get("note") or ""
    value_size = 28 if h >= 110 else 24
    value_y = y + min(62, h * 0.58)
    return (
        f'<g id="metric-{index}">'
        + _rect(x, y, w, h, fill=theme["surface"], stroke=theme["border"], rx=6)
        + _circle(x + 18, y + 19, 4, fill=theme["accent"])
        + _text(x + 30, y + 24, label, size=12, fill=theme["muted_text"], max_chars=12, max_lines=1)
        + _text(x + 18, value_y, value, size=value_size, fill=theme["accent"], weight=800, max_chars=9, max_lines=1)
        + _text(x + 18, y + h - 10, detail, size=10, fill=theme["body_text"], max_chars=15, max_lines=1)
        + "</g>"
    )


def _body_region(spec: dict[str, Any]) -> tuple[float, float, float, float, str, dict[str, str]]:
    # normalize_spec 已按 pattern 校验最小尺寸；渲染阶段只读取归一后的区域。
    x, y, w, h = _region(spec, minimum_width=0, minimum_height=0)
    theme = _theme(spec)
    title = str(spec.get("title") or "").strip()
    title_markup = _section_title(x, y, w, title, theme)
    if title:
        y += 58
        h -= 58
    return x, y, w, h, title_markup, theme


def _render_phased_roadmap(spec: dict[str, Any]) -> str:
    data = _dict(spec.get("data"), field="data")
    stages = _items(data, "stages", 2, 4)
    x, y, w, h, heading, theme = _body_region(spec)
    gap = 14
    col_w = (w - gap * (len(stages) - 1)) / len(stages)
    rail_y = y + 32
    card_y = y + 62
    card_h = h - 62
    node_centers = [
        x + index * (col_w + gap) + col_w / 2 for index in range(len(stages))
    ]
    parts = [heading]
    for start, end in zip(node_centers[:-1], node_centers[1:], strict=True):
        parts.append(_line(start + 22, rail_y, end - 22, rail_y, stroke=theme["accent"], width=4))
    for index, raw in enumerate(stages, start=1):
        item = _dict(raw, field=f"stages[{index - 1}]")
        cx = x + (index - 1) * (col_w + gap)
        parts.append(f'<g id="stage-{index}">')
        parts.append(_circle(cx + col_w / 2, rail_y, 22, fill=theme["surface"], stroke=theme["accent"]))
        parts.append(_text(cx + col_w / 2, rail_y + 5, index, size=13, fill=theme["accent"], weight=800, anchor="middle", max_chars=2, max_lines=1))
        parts.append(_rect(cx, card_y, col_w, card_h, fill=theme["surface"], stroke=theme["border"], rx=7))
        parts.append(_rect(cx, card_y, col_w, 44, fill=theme["accent"], rx=7))
        parts.append(_text(cx + 16, card_y + 27, item.get("label"), size=16, fill=theme["surface"], weight=700, max_chars=10, max_lines=1))
        parts.append(_text(cx + col_w - 14, card_y + 27, item.get("window"), size=11, fill=theme["surface"], anchor="end", max_chars=9, max_lines=1))
        rows = (
            ("目标", item.get("goal")),
            ("动作", " / ".join(str(value) for value in _list(item.get("actions")))),
            ("产出", " / ".join(str(value) for value in _list(item.get("outputs")))),
            ("风险", item.get("risk")),
        )
        row_h = (card_h - 44) / 4
        for row_index, (label, value) in enumerate(rows):
            ry = card_y + 44 + row_index * row_h
            if row_index:
                parts.append(_line(cx, ry, cx + col_w, ry, stroke=theme["border"]))
            parts.append(_rect(cx + 10, ry + 10, 42, 22, fill=theme["surface_alt"], rx=3))
            parts.append(_text(cx + 31, ry + 26, label, size=11, fill=theme["accent"], weight=700, anchor="middle", max_chars=3, max_lines=1))
            parts.append(_text(cx + 62, ry + 26, value, size=11, fill=theme["body_text"], max_chars=max(10, int(col_w / 13)), max_lines=2))
        parts.append("</g>")
    return "".join(parts)


def _render_diagnostic_grid(spec: dict[str, Any]) -> str:
    data = _dict(spec.get("data"), field="data")
    issues = _items(data, "issues", 2, 4)
    x, y, w, h, heading, theme = _body_region(spec)
    cols = 2 if len(issues) > 2 else len(issues)
    rows = math.ceil(len(issues) / cols)
    gap = 14
    card_w = (w - gap * (cols - 1)) / cols
    card_h = (h - gap * (rows - 1)) / rows
    parts = [heading]
    for index, raw in enumerate(issues, start=1):
        item = _dict(raw, field=f"issues[{index - 1}]")
        col = (index - 1) % cols
        row = (index - 1) // cols
        cx = x + col * (card_w + gap)
        cy = y + row * (card_h + gap)
        rail_w = min(112, card_w * 0.23)
        body_w = card_w - rail_w
        parts.append(f'<g id="issue-{index}">')
        parts.append(_rect(cx, cy, card_w, card_h, fill=theme["surface"], stroke=theme["border"], rx=7))
        parts.append(_rect(cx, cy, body_w, 40, fill=theme["accent"], rx=7))
        parts.append(_badge(cx + 24, cy + 20, f"{index:02d}", theme, fill=theme["accent_alt"]))
        parts.append(_text(cx + 52, cy + 25, item.get("title"), size=15, fill=theme["surface"], weight=700, max_chars=14, max_lines=1))
        rows_data = (
            ("现象", item.get("symptoms")),
            ("根因", item.get("causes")),
            ("方案", item.get("responses")),
        )
        row_h = (card_h - 40) / 3
        for row_index, (label, values) in enumerate(rows_data):
            ry = cy + 40 + row_index * row_h
            if row_index:
                parts.append(_line(cx, ry, cx + body_w, ry, stroke=theme["border"]))
            tone = theme["contrast"] if label == "方案" else theme["accent"]
            parts.append(_rect(cx + 10, ry + 10, 48, 22, fill=tone, rx=3))
            parts.append(_text(cx + 34, ry + 26, label, size=11, fill=theme["surface"], weight=700, anchor="middle", max_chars=3, max_lines=1))
            text = "；".join(str(value) for value in _list(values))
            parts.append(_text(cx + 68, ry + 25, text, size=11, fill=theme["body_text"], max_chars=max(12, int(body_w / 14)), max_lines=2))
        parts.append(_rect(cx + body_w, cy, rail_w, card_h, fill=theme["surface_alt"], rx=7))
        parts.append(_text(cx + body_w + rail_w / 2, cy + 31, "INSIGHT", size=10, fill=theme["accent"], weight=700, anchor="middle", max_chars=8, max_lines=1))
        parts.append(_text(cx + body_w + rail_w / 2, cy + card_h * 0.43, item.get("insight"), size=12, fill=theme["title_text"], weight=700, anchor="middle", max_chars=max(5, int(rail_w / 13)), max_lines=4))
        parts.append("</g>")
    return "".join(parts)


def _render_shared_source(spec: dict[str, Any]) -> str:
    data = _dict(spec.get("data"), field="data")
    source = _dict(data.get("source"), field="source")
    platforms = _items(data, "platforms", 2, 4)
    common = _items(data, "common_capabilities", 2, 5)
    values = _items(data, "values", 2, 4)
    x, y, w, h, heading, theme = _body_region(spec)
    top_h = h * 0.48
    source_w = w * 0.18
    arrow_w = 46
    platforms_x = x + source_w + arrow_w
    platforms_w = w - source_w - arrow_w
    gap = 12
    card_w = (platforms_w - gap * (len(platforms) - 1)) / len(platforms)
    parts = [heading]
    parts.append('<g id="shared-source">')
    parts.append(_rect(x, y, source_w, top_h, fill=theme["accent"], rx=8))
    parts.append(_text(x + source_w / 2, y + 42, source.get("title"), size=17, fill=theme["surface"], weight=700, anchor="middle", max_chars=10, max_lines=2))
    for index, item in enumerate(_list(source.get("items"))[:3]):
        parts.append(_text(x + 18, y + 92 + index * 38, f"• {item}", size=12, fill=theme["surface"], max_chars=14, max_lines=1))
    arrow_y = y + top_h / 2
    parts.append(_polygon([(x + source_w + 8, arrow_y - 16), (platforms_x - 10, arrow_y - 16), (platforms_x, arrow_y), (platforms_x - 10, arrow_y + 16), (x + source_w + 8, arrow_y + 16)], fill=theme["accent_alt"]))
    parts.append("</g>")
    for index, raw in enumerate(platforms, start=1):
        item = _dict(raw, field=f"platforms[{index - 1}]")
        cx = platforms_x + (index - 1) * (card_w + gap)
        parts.append(f'<g id="platform-{index}">')
        parts.append(_rect(cx, y, card_w, top_h, fill=theme["surface"], stroke=theme["border"], rx=8))
        parts.append(_rect(cx, y, card_w, 40, fill=theme["accent_alt"], rx=8))
        parts.append(_text(cx + card_w / 2, y + 26, item.get("title"), size=15, fill=theme["surface"], weight=700, anchor="middle", max_chars=11, max_lines=1))
        for cap_index, cap in enumerate(_list(item.get("capabilities"))[:3]):
            parts.append(_text(cx + 18, y + 82 + cap_index * 42, f"• {cap}", size=12, fill=theme["body_text"], max_chars=max(9, int(card_w / 13)), max_lines=1))
        parts.append("</g>")
    rail_y = y + top_h + 12
    rail_h = 44
    parts.append('<g id="common-capability-rail">')
    parts.append(_rect(x, rail_y, w, rail_h, fill=theme["surface_alt"], stroke=theme["border"], rx=6))
    item_w = w / len(common)
    for index, item in enumerate(common):
        if index:
            parts.append(_line(x + index * item_w, rail_y + 10, x + index * item_w, rail_y + rail_h - 10, stroke=theme["border"]))
        parts.append(_text(x + (index + 0.5) * item_w, rail_y + 28, item, size=12, fill=theme["accent"], weight=700, anchor="middle", max_chars=max(5, int(item_w / 13)), max_lines=1))
    parts.append("</g>")
    metrics_y = rail_y + rail_h + 12
    metrics_h = h - (metrics_y - y)
    metric_w = (w - gap * (len(values) - 1)) / len(values)
    for index, item in enumerate(values, start=1):
        parts.append(_metric_card(x + (index - 1) * (metric_w + gap), metrics_y, metric_w, metrics_h, item, theme, index=index))
    return "".join(parts)


def _render_stage_scorecard(spec: dict[str, Any]) -> str:
    data = _dict(spec.get("data"), field="data")
    stages = _items(data, "stages", 3, 7)
    mechanisms = _items(data, "mechanisms", 1, 2)
    metrics = _items(data, "metrics", 2, 4)
    x, y, w, h, heading, theme = _body_region(spec)
    stage_h = h * 0.26
    stage_w = w / len(stages)
    parts = [heading]
    for index, raw in enumerate(stages, start=1):
        item = raw if isinstance(raw, dict) else {"title": str(raw)}
        sx = x + (index - 1) * stage_w
        tip = min(18, stage_w * 0.16)
        points = [(sx, y), (sx + stage_w - tip, y), (sx + stage_w, y + stage_h / 2), (sx + stage_w - tip, y + stage_h), (sx, y + stage_h)]
        if index > 1:
            points.insert(0, (sx + tip, y + stage_h / 2))
        fill = theme["accent"] if index % 2 else theme["accent_alt"]
        parts.append(f'<g id="stage-{index}">')
        parts.append(_polygon(points, fill=fill, stroke=theme["surface"]))
        parts.append(_text(sx + stage_w / 2, y + stage_h * 0.43, item.get("title"), size=13, fill=theme["surface"], weight=700, anchor="middle", max_chars=max(5, int(stage_w / 13)), max_lines=2))
        parts.append("</g>")
    mech_y = y + stage_h + 14
    mech_h = h * 0.30
    gap = 14
    mech_w = (w - gap * (len(mechanisms) - 1)) / len(mechanisms)
    for index, raw in enumerate(mechanisms, start=1):
        item = raw if isinstance(raw, dict) else {"title": str(raw)}
        mx = x + (index - 1) * (mech_w + gap)
        parts.append(f'<g id="mechanism-{index}">')
        parts.append(_rect(mx, mech_y, mech_w, mech_h, fill=theme["surface_alt"], stroke=theme["border"], rx=7))
        parts.append(_badge(mx + 28, mech_y + 30, index, theme, fill=theme["contrast"]))
        parts.append(_text(mx + 56, mech_y + 27, item.get("title"), size=15, fill=theme["title_text"], weight=700, max_chars=20, max_lines=1))
        parts.append(_text(mx + 20, mech_y + 66, item.get("detail"), size=12, fill=theme["body_text"], max_chars=max(18, int(mech_w / 13)), max_lines=3))
        parts.append("</g>")
    metrics_y = mech_y + mech_h + 14
    metrics_h = h - (metrics_y - y)
    metric_w = (w - gap * (len(metrics) - 1)) / len(metrics)
    for index, item in enumerate(metrics, start=1):
        parts.append(_metric_card(x + (index - 1) * (metric_w + gap), metrics_y, metric_w, metrics_h, item, theme, index=index))
    return "".join(parts)


def _render_operating_model(spec: dict[str, Any]) -> str:
    data = _dict(spec.get("data"), field="data")
    north_star = str(data.get("north_star") or "").strip()
    if not north_star:
        raise SpecError("north_star is required")
    enablers = _exact_items(data, "enablers", 2)
    layers = _items(data, "layers", 3, 5)
    collaborations = _items(data, "collaborations", 1, 2)
    values = _items(data, "values", 3, 5)
    x, y, w, h, heading, theme = _body_region(spec)
    value_h = h * 0.20
    body_h = h - value_h - 12
    side_w = w * 0.22
    center_x = x + side_w + 12
    center_w = w - side_w * 2 - 24
    roof_h = body_h * 0.18
    enable_h = body_h * 0.17
    layer_h = (body_h - roof_h - enable_h - 16) / len(layers)
    parts = [heading]
    roof_points = [(center_x + center_w * 0.12, y + roof_h), (center_x + center_w / 2, y), (center_x + center_w * 0.88, y + roof_h)]
    parts.append('<g id="north-star">')
    parts.append(_polygon(roof_points, fill=theme["accent"]))
    parts.append(_text(center_x + center_w / 2, y + roof_h * 0.72, north_star, size=18, fill=theme["surface"], weight=800, anchor="middle", max_chars=16, max_lines=1))
    parts.append("</g>")
    enabler_y = y + roof_h + 6
    for index, item in enumerate(enablers, start=1):
        ex = center_x + (index - 1) * (center_w / 2 + 4)
        ew = center_w / 2 - 4
        parts.append(f'<g id="enabler-{index}">')
        parts.append(_rect(ex, enabler_y, ew, enable_h, fill=theme["accent_alt" if index == 2 else "accent"], rx=6))
        parts.append(_text(ex + ew / 2, enabler_y + enable_h * 0.60, item, size=15, fill=theme["surface"], weight=700, anchor="middle", max_chars=12, max_lines=1))
        parts.append("</g>")
    layer_y = enabler_y + enable_h + 8
    for index, raw in enumerate(layers, start=1):
        item = raw if isinstance(raw, dict) else {"title": str(raw), "items": []}
        ly = layer_y + (index - 1) * layer_h
        parts.append(f'<g id="layer-{index}">')
        parts.append(_rect(center_x, ly, center_w, layer_h - 5, fill=theme["surface"], stroke=theme["border"], rx=5))
        parts.append(_rect(center_x, ly, center_w * 0.22, layer_h - 5, fill=theme["surface_alt"], rx=5))
        parts.append(_text(center_x + center_w * 0.11, ly + layer_h * 0.54, item.get("title"), size=13, fill=theme["accent"], weight=700, anchor="middle", max_chars=8, max_lines=1))
        detail = " · ".join(str(value) for value in _list(item.get("items"))[:3])
        parts.append(_text(center_x + center_w * 0.25, ly + layer_h * 0.54, detail, size=11, fill=theme["body_text"], max_chars=max(16, int(center_w / 12)), max_lines=1))
        parts.append("</g>")
    parts.append('<g id="collaboration-rail">')
    parts.append(_rect(x, y, side_w, body_h, fill=theme["surface_alt"], stroke=theme["border"], rx=7))
    parts.append(_text(x + side_w / 2, y + 32, "架构原则", size=14, fill=theme["accent"], weight=700, anchor="middle", max_chars=8, max_lines=1))
    parts.append(_text(x + 18, y + 72, "纵向分层明确能力边界\n横向协同打通价值链", size=12, fill=theme["body_text"], max_chars=13, max_lines=4))
    right_x = x + w - side_w
    parts.append(_rect(right_x, y, side_w, body_h, fill=theme["surface"], stroke=theme["border"], rx=7))
    parts.append(_text(right_x + side_w / 2, y + 32, "横向协同", size=14, fill=theme["accent"], weight=700, anchor="middle", max_chars=8, max_lines=1))
    for index, item in enumerate(collaborations, start=1):
        cy = y + 64 + (index - 1) * ((body_h - 70) / len(collaborations))
        parts.append(_badge(right_x + 32, cy + 18, index, theme, fill=theme["contrast"]))
        parts.append(_text(right_x + 60, cy + 22, item, size=12, fill=theme["title_text"], weight=700, max_chars=12, max_lines=2))
        parts.append(_line(right_x + 28, cy + 46, right_x + side_w - 22, cy + 46, stroke=theme["border"], dash="4 4"))
    parts.append("</g>")
    metrics_y = y + body_h + 12
    gap = 8
    metric_w = (w - gap * (len(values) - 1)) / len(values)
    for index, item in enumerate(values, start=1):
        parts.append(_metric_card(x + (index - 1) * (metric_w + gap), metrics_y, metric_w, value_h, item, theme, index=index))
    return "".join(parts)


def _render_retrospect_pyramid(spec: dict[str, Any]) -> str:
    data = _dict(spec.get("data"), field="data")
    periods = _exact_items(data, "periods", 3)
    layers = _exact_items(data, "pyramid_layers", 3)
    x, y, w, h, heading, theme = _body_region(spec)
    gap = 14
    col_w = (w - gap * 2) / 3
    conclusion_h = 48
    card_h = h - conclusion_h - 12
    parts = [heading]
    for index, raw in enumerate(periods, start=1):
        item = _dict(raw, field=f"periods[{index - 1}]")
        cx = x + (index - 1) * (col_w + gap)
        fill = theme["surface_alt"] if index == 2 else theme["surface"]
        parts.append(f'<g id="period-{index}">')
        parts.append(_rect(cx, y, col_w, card_h, fill=fill, stroke=theme["border"], rx=7))
        parts.append(_rect(cx, y, col_w, 42, fill=theme["accent" if index == 2 else "accent_alt"], rx=7))
        parts.append(_text(cx + 18, y + 27, item.get("title"), size=15, fill=theme["surface"], weight=700, max_chars=12, max_lines=1))
        parts.append(_text(cx + col_w - 18, y + 72, item.get("metric"), size=30, fill=theme["accent"], weight=800, anchor="end", max_chars=8, max_lines=1))
        if index == 2:
            base_y = y + card_h - 36
            pyramid_w = col_w * 0.72
            heights = [42, 46, 52]
            current_y = base_y
            for layer_index, layer in enumerate(reversed(layers), start=1):
                layer_w = pyramid_w * (1 - (layer_index - 1) * 0.18)
                lx = cx + (col_w - layer_w) / 2
                current_y -= heights[layer_index - 1]
                parts.append(_polygon([(lx, current_y + heights[layer_index - 1]), (lx + layer_w, current_y + heights[layer_index - 1]), (lx + layer_w * 0.82, current_y), (lx + layer_w * 0.18, current_y)], fill=theme["accent" if layer_index % 2 else "accent_alt"]))
                parts.append(_text(cx + col_w / 2, current_y + heights[layer_index - 1] * 0.62, layer, size=11, fill=theme["surface"], weight=700, anchor="middle", max_chars=10, max_lines=1))
        else:
            for bullet_index, bullet in enumerate(_list(item.get("bullets"))[:3]):
                parts.append(_text(cx + 20, y + 126 + bullet_index * 46, f"• {bullet}", size=12, fill=theme["body_text"], max_chars=max(12, int(col_w / 13)), max_lines=2))
        parts.append("</g>")
    conclusion_y = y + card_h + 12
    parts.append('<g id="conclusion-band">')
    parts.append(_rect(x, conclusion_y, w, conclusion_h, fill=theme["accent"], rx=6))
    parts.append(_text(x + w / 2, conclusion_y + 31, data.get("conclusion"), size=15, fill=theme["surface"], weight=700, anchor="middle", max_chars=36, max_lines=1))
    parts.append("</g>")
    return "".join(parts)


def _render_duotone(spec: dict[str, Any]) -> str:
    data = _dict(spec.get("data"), field="data")
    problems = _items(data, "problems", 2, 4)
    responses = _items(data, "responses", 2, 4)
    x, y, w, h, heading, theme = _body_region(spec)
    center_w = w * 0.34
    side_w = (w - center_w) / 2
    cy = y + h / 2
    r = min(center_w * 0.34, h * 0.28)
    parts = [heading]
    parts.append('<g id="duotone-core">')
    parts.append(_circle(x + side_w + center_w * 0.38, cy, r, fill=theme["accent"]))
    parts.append(_circle(x + side_w + center_w * 0.62, cy, r, fill=theme["accent_alt"]))
    parts.append(_text(x + side_w + center_w * 0.38, cy - 8, "存在不足", size=18, fill=theme["surface"], weight=800, anchor="middle", max_chars=6, max_lines=2))
    parts.append(_text(x + side_w + center_w * 0.62, cy - 8, "改进措施", size=18, fill=theme["surface"], weight=800, anchor="middle", max_chars=6, max_lines=2))
    parts.append(_polygon([(x + w / 2 - 12, cy - 14), (x + w / 2 + 14, cy), (x + w / 2 - 12, cy + 14)], fill=theme["surface"]))
    parts.append(_text(x + w / 2, cy + r + 38, data.get("center_label"), size=13, fill=theme["title_text"], weight=700, anchor="middle", max_chars=16, max_lines=1))
    parts.append("</g>")
    for side, items, color in (("problem", problems, theme["accent"]), ("response", responses, theme["accent_alt"])):
        sx = x if side == "problem" else x + side_w + center_w
        row_h = h / len(items)
        for index, raw in enumerate(items, start=1):
            item = raw if isinstance(raw, dict) else {"title": str(raw)}
            row_y = y + (index - 1) * row_h
            text_x = sx + 18 if side == "problem" else sx + 44
            badge_x = sx + side_w - 24 if side == "problem" else sx + 22
            anchor = "start"
            parts.append(f'<g id="{side}-{index}">')
            parts.append(_line(sx + 12, row_y + row_h - 8, sx + side_w - 12, row_y + row_h - 8, stroke=theme["border"], dash="4 4"))
            parts.append(_badge(badge_x, row_y + 24, index, theme, fill=color))
            parts.append(_text(text_x, row_y + 22, item.get("title"), size=14, fill=theme["title_text"], weight=700, anchor=anchor, max_chars=14, max_lines=1))
            parts.append(_text(text_x, row_y + 49, item.get("detail"), size=11, fill=theme["body_text"], anchor=anchor, max_chars=max(12, int(side_w / 13)), max_lines=2))
            parts.append("</g>")
    return "".join(parts)


def _render_calendar(spec: dict[str, Any]) -> str:
    data = _dict(spec.get("data"), field="data")
    months = _items(data, "months", 3, 6)
    events = _items(data, "events", 1, 8)
    summaries = _items(data, "summaries", 1, 3)
    x, y, w, h, heading, theme = _body_region(spec)
    rail_w = w * 0.25
    calendar_w = w - rail_w - 16
    header_h = 42
    col_w = calendar_w / len(months)
    row_h = (h - header_h) / max(4, len(events))
    parts = [heading, '<g id="calendar-grid">']
    parts.append(_rect(x, y, calendar_w, h, fill=theme["surface"], stroke=theme["border"], rx=6))
    for index, month in enumerate(months):
        cx = x + index * col_w
        parts.append(_rect(cx, y, col_w, header_h, fill=theme["accent" if index % 2 == 0 else "accent_alt"]))
        parts.append(_text(cx + col_w / 2, y + 27, month, size=13, fill=theme["surface"], weight=700, anchor="middle", max_chars=6, max_lines=1))
        if index:
            parts.append(_line(cx, y, cx, y + h, stroke=theme["border"]))
    for index, raw in enumerate(events, start=1):
        event = _dict(raw, field=f"events[{index - 1}]")
        start = int(event.get("start", 0))
        end = int(event.get("end", start))
        if start < 0 or end < start or end >= len(months):
            raise SpecError(f"events[{index - 1}] start/end outside months")
        ex = x + start * col_w + 8
        ew = (end - start + 1) * col_w - 16
        ey = y + header_h + (index - 1) * row_h + 8
        parts.append(f'<g id="event-{index}">')
        parts.append(_rect(ex, ey, ew, min(32, row_h - 8), fill=theme["surface_alt"], stroke=theme["accent_alt"], rx=5))
        parts.append(_text(ex + 12, ey + 21, event.get("title"), size=11, fill=theme["title_text"], weight=700, max_chars=max(8, int(ew / 13)), max_lines=1))
        parts.append("</g>")
    parts.append("</g>")
    rail_x = x + calendar_w + 16
    summary_h = (h - 12 * (len(summaries) - 1)) / len(summaries)
    parts.append('<g id="summary-rail">')
    for index, raw in enumerate(summaries, start=1):
        item = raw if isinstance(raw, dict) else {"title": str(raw)}
        sy = y + (index - 1) * (summary_h + 12)
        parts.append(_rect(rail_x, sy, rail_w, summary_h, fill=theme["surface_alt"], stroke=theme["border"], rx=6))
        parts.append(_badge(rail_x + 28, sy + 30, index, theme, fill=theme["accent"]))
        parts.append(_text(rail_x + 56, sy + 27, item.get("title"), size=14, fill=theme["title_text"], weight=700, max_chars=12, max_lines=1))
        parts.append(_text(rail_x + 18, sy + 64, item.get("detail"), size=11, fill=theme["body_text"], max_chars=max(12, int(rail_w / 13)), max_lines=3))
    parts.append("</g>")
    return "".join(parts)


def _render_target_timeline(spec: dict[str, Any]) -> str:
    data = _dict(spec.get("data"), field="data")
    periods = _items(data, "periods", 4, 6)
    x, y, w, h, heading, theme = _body_region(spec)
    gap = 10
    col_w = (w - gap * (len(periods) - 1)) / len(periods)
    rail_y = y + 30
    card_y = y + 58
    card_h = h - 58
    node_centers = [
        x + index * (col_w + gap) + col_w / 2 for index in range(len(periods))
    ]
    parts = [heading]
    for start, end in zip(node_centers[:-1], node_centers[1:], strict=True):
        parts.append(_line(start + 24, rail_y, end - 24, rail_y, stroke=theme["accent"], width=5))
    parts.append(_line(node_centers[-1] + 24, rail_y, x + w - 12, rail_y, stroke=theme["accent"], width=5))
    parts.append(_polygon([(x + w - 12, rail_y - 11), (x + w, rail_y), (x + w - 12, rail_y + 11)], fill=theme["accent"]))
    for index, raw in enumerate(periods, start=1):
        item = _dict(raw, field=f"periods[{index - 1}]")
        cx = x + (index - 1) * (col_w + gap)
        emphasized = bool(item.get("emphasis"))
        card_fill = theme["accent"] if emphasized else theme["surface"]
        text_fill = theme["surface"] if emphasized else theme["body_text"]
        parts.append(f'<g id="period-{index}">')
        parts.append(_circle(cx + col_w / 2, rail_y, 24, fill=theme["accent" if emphasized else "surface"], stroke=theme["accent"]))
        parts.append(_text(cx + col_w / 2, rail_y + 5, item.get("label"), size=12, fill=theme["surface" if emphasized else "accent"], weight=700, anchor="middle", max_chars=4, max_lines=1))
        parts.append(_rect(cx, card_y, col_w, card_h, fill=card_fill, stroke=theme["border"], rx=5))
        rows = (
            ("目标", item.get("goal")),
            ("行动计划", " / ".join(str(value) for value in _list(item.get("actions")))),
            ("结果评估", item.get("result")),
        )
        row_h = card_h / 3
        for row_index, (label, value) in enumerate(rows):
            ry = card_y + row_index * row_h
            if row_index:
                parts.append(_line(cx + 10, ry, cx + col_w - 10, ry, stroke=theme["surface" if emphasized else "border"], dash="3 3"))
            pill_fill = theme["surface"] if emphasized else theme["accent"]
            pill_text = theme["accent"] if emphasized else theme["surface"]
            parts.append(_rect(cx + 10, ry + 10, min(72, col_w - 20), 22, fill=pill_fill, rx=3))
            parts.append(_text(cx + 18, ry + 26, label, size=10, fill=pill_text, weight=700, max_chars=6, max_lines=1))
            parts.append(_text(cx + 12, ry + 53, value, size=10, fill=text_fill, max_chars=max(8, int(col_w / 12)), max_lines=3))
        parts.append("</g>")
    return "".join(parts)


def _render_north_star(spec: dict[str, Any]) -> str:
    data = _dict(spec.get("data"), field="data")
    north_star = str(data.get("north_star") or "").strip()
    if not north_star:
        raise SpecError("north_star is required")
    principles = _exact_items(data, "principles", 3)
    metrics = _items(data, "metrics", 3, 5)
    x, y, w, h, heading, theme = _body_region(spec)
    roof_h = h * 0.27
    roof_w = w * 0.46
    roof_x = x + (w - roof_w) / 2
    parts = [heading, '<g id="north-star-roof">']
    parts.append(_polygon([(roof_x, y + roof_h), (roof_x + roof_w / 2, y), (roof_x + roof_w, y + roof_h)], fill=theme["surface_alt"], stroke=theme["accent"]))
    parts.append(_text(x + w / 2, y + roof_h * 0.55, north_star, size=24, fill=theme["accent"], weight=800, anchor="middle", max_chars=16, max_lines=1))
    parts.append(_text(x + w / 2, y + roof_h * 0.78, data.get("subtitle"), size=12, fill=theme["body_text"], anchor="middle", max_chars=24, max_lines=1))
    parts.append("</g>")
    principle_y = y + roof_h + 8
    principle_h = 42
    principle_w = w / 3
    for index, item in enumerate(principles, start=1):
        px = x + (index - 1) * principle_w
        parts.append(_rect(px, principle_y, principle_w - 2, principle_h, fill=theme["accent" if index != 2 else "accent_alt"]))
        parts.append(_text(px + principle_w / 2, principle_y + 27, item, size=13, fill=theme["surface"], weight=700, anchor="middle", max_chars=12, max_lines=1))
    metrics_y = principle_y + principle_h + 10
    conclusion_h = 42
    metrics_h = h - (metrics_y - y) - conclusion_h - 10
    gap = 10
    metric_w = (w - gap * (len(metrics) - 1)) / len(metrics)
    for index, item in enumerate(metrics, start=1):
        mx = x + (index - 1) * (metric_w + gap)
        data_item = item if isinstance(item, dict) else {"title": str(item)}
        notch = min(24, metric_w * 0.14)
        parts.append(f'<g id="metric-{index}">')
        parts.append(_polygon([(mx, metrics_y), (mx + metric_w, metrics_y), (mx + metric_w, metrics_y + metrics_h), (mx + notch, metrics_y + metrics_h), (mx, metrics_y + metrics_h - notch)], fill=theme["accent"], stroke=theme["surface"]))
        parts.append(_text(mx + metric_w / 2, metrics_y + metrics_h * 0.43, data_item.get("metric_value") or data_item.get("value"), size=30, fill=theme["surface"], weight=800, anchor="middle", max_chars=8, max_lines=1))
        parts.append(_text(mx + metric_w / 2, metrics_y + metrics_h * 0.68, data_item.get("metric_label") or data_item.get("title"), size=12, fill=theme["surface"], anchor="middle", max_chars=max(7, int(metric_w / 13)), max_lines=2))
        parts.append("</g>")
    conclusion_y = metrics_y + metrics_h + 10
    parts.append(_rect(x, conclusion_y, w, conclusion_h, fill=theme["accent"], rx=4))
    parts.append(_text(x + w / 2, conclusion_y + 27, data.get("conclusion"), size=14, fill=theme["surface"], weight=700, anchor="middle", max_chars=38, max_lines=1))
    return "".join(parts)


def _render_arrow_ribbon(spec: dict[str, Any]) -> str:
    data = _dict(spec.get("data"), field="data")
    items = _items(data, "items", 3, 6)
    x, y, w, h, heading, theme = _body_region(spec)
    gap = 10
    col_w = (w - gap * (len(items) - 1)) / len(items)
    ribbon_h = h * 0.34
    metric_h = h * 0.25
    detail_y = y + ribbon_h + 14
    detail_h = h - ribbon_h - metric_h - 28
    metric_y = y + h - metric_h
    parts = [heading]
    for index, raw in enumerate(items, start=1):
        item = raw if isinstance(raw, dict) else {"title": str(raw)}
        cx = x + (index - 1) * (col_w + gap)
        tip = min(28, col_w * 0.18)
        parts.append(f'<g id="ribbon-{index}">')
        parts.append(_polygon([(cx, y), (cx + col_w - tip, y), (cx + col_w, y + ribbon_h / 2), (cx + col_w - tip, y + ribbon_h), (cx, y + ribbon_h)], fill=theme["accent" if index % 2 else "accent_alt"]))
        parts.append(_text(cx + col_w / 2 - tip / 3, y + ribbon_h * 0.43, item.get("title"), size=14, fill=theme["surface"], weight=700, anchor="middle", max_chars=max(7, int(col_w / 12)), max_lines=2))
        parts.append(_text(cx + col_w / 2 - tip / 3, y + ribbon_h * 0.76, f"PART {index:02d}", size=11, fill=theme["surface"], weight=700, anchor="middle", max_chars=8, max_lines=1))
        parts.append(_line(cx + col_w / 2, y + ribbon_h, cx + col_w / 2, detail_y - 4, stroke=theme["border"], dash="3 3"))
        parts.append(_text(cx + 8, detail_y + 22, item.get("detail"), size=10, fill=theme["body_text"], max_chars=max(8, int(col_w / 12)), max_lines=max(2, int(detail_h / 18))))
        parts.append(_rect(cx, metric_y, col_w, metric_h, fill=theme["surface_alt"], rx=5))
        parts.append(_text(cx + col_w / 2, metric_y + metric_h * 0.39, item.get("metric_label"), size=11, fill=theme["title_text"], weight=700, anchor="middle", max_chars=max(7, int(col_w / 13)), max_lines=2))
        parts.append(_text(cx + col_w / 2, metric_y + metric_h * 0.78, item.get("metric_value"), size=25, fill=theme["accent"], weight=800, anchor="middle", max_chars=8, max_lines=1))
        parts.append("</g>")
    return "".join(parts)


def _render_highlight_matrix(spec: dict[str, Any]) -> str:
    data = _dict(spec.get("data"), field="data")
    items = _exact_items(data, "items", 4)
    labels = _exact_items(data, "core_labels", 4)
    x, y, w, h, heading, theme = _body_region(spec)
    center_w = w * 0.34
    center_x = x + (w - center_w) / 2
    card_w = (w - center_w - 28) / 2
    card_h = (h - 14) / 2
    positions = (
        (x, y),
        (x, y + card_h + 14),
        (x + w - card_w, y),
        (x + w - card_w, y + card_h + 14),
    )
    parts = [heading]
    for index, (raw, (cx, cy)) in enumerate(zip(items, positions, strict=True), start=1):
        item = _dict(raw, field=f"items[{index - 1}]")
        parts.append(f'<g id="highlight-{index}">')
        parts.append(_rect(cx, cy, card_w, card_h, fill=theme["surface"], stroke=theme["border"], rx=6))
        badge_x = cx + 22 if index <= 2 else cx + card_w - 22
        parts.append(_badge(badge_x, cy + 24, f"{index:02d}", theme, fill=theme["accent"]))
        parts.append(_text(cx + card_w / 2, cy + 31, item.get("title"), size=14, fill=theme["title_text"], weight=700, anchor="middle", max_chars=16, max_lines=1))
        parts.append(_text(cx + 18, cy + 68, "具体工作", size=11, fill=theme["accent"], weight=700, max_chars=6, max_lines=1))
        parts.append(_text(cx + 18, cy + 91, item.get("work"), size=11, fill=theme["body_text"], max_chars=max(13, int(card_w / 13)), max_lines=2))
        parts.append(_text(cx + 18, cy + 134, "取得成果", size=11, fill=theme["accent"], weight=700, max_chars=6, max_lines=1))
        parts.append(_text(cx + 18, cy + 157, item.get("result"), size=11, fill=theme["body_text"], max_chars=max(13, int(card_w / 13)), max_lines=2))
        parts.append("</g>")
    center_cx = center_x + center_w / 2
    center_cy = y + h / 2
    radius = min(center_w * 0.22, h * 0.17)
    offsets = ((-radius, -radius), (radius, -radius), (-radius, radius), (radius, radius))
    parts.append('<g id="highlight-core">')
    for index, (label, (dx, dy)) in enumerate(zip(labels, offsets, strict=True), start=1):
        fill = theme["accent" if index % 2 else "accent_alt"]
        parts.append(_circle(center_cx + dx, center_cy + dy, radius * 0.86, fill=fill))
        parts.append(_text(center_cx + dx, center_cy + dy + 4, label, size=14, fill=theme["surface"], anchor="middle", max_chars=6, max_lines=2))
    parts.append("</g>")
    return "".join(parts)


def _required_text(value: Any, *, field: str) -> str:
    text = str(value or "").strip()
    if not text:
        raise SpecError(f"{field} is required")
    return text


def _numeric_values(value: Any, *, field: str, expected: int) -> list[float]:
    values = _list(value)
    if len(values) != expected:
        raise SpecError(f"{field} must contain exactly {expected} values")
    result: list[float] = []
    for index, item in enumerate(values):
        try:
            result.append(float(item))
        except (TypeError, ValueError) as exc:
            raise SpecError(f"{field}[{index}] must be numeric") from exc
    return result


def _evidence_slot_id(
    visual: dict[str, Any],
    *,
    section_index: int,
    card_index: int,
    suffix: str,
) -> str:
    fallback = f"evidence-card-{section_index}-{card_index}-{suffix}"
    return _slug(str(visual.get("slot_id") or fallback))


def _micro_chart_preview(
    slot_id: str,
    x: float,
    y: float,
    w: float,
    h: float,
    visual: dict[str, Any],
    theme: dict[str, str],
) -> str:
    labels = _list(visual.get("labels"))
    if not 2 <= len(labels) <= 5:
        raise SpecError("micro chart labels must contain 2-5 items")
    series = _list(visual.get("series"))
    if len(series) != 1 or not isinstance(series[0], dict):
        raise SpecError("micro chart series must contain exactly one object")
    values = _numeric_values(
        series[0].get("values"),
        field="micro chart series[0].values",
        expected=len(labels),
    )
    chart_kind = str(visual.get("chart_kind") or visual.get("kind_name") or "bar")
    if chart_kind not in {"bar", "line"}:
        raise SpecError("micro chart chart_kind must be bar or line")

    pad_x = 12.0
    pad_top = 10.0
    pad_bottom = 17.0
    plot_x = x + pad_x
    plot_y = y + pad_top
    plot_w = max(24.0, w - pad_x * 2)
    plot_h = max(18.0, h - pad_top - pad_bottom)
    low = min(0.0, min(values))
    high = max(values)
    span = high - low or 1.0
    parts = [f'<g id="{slot_id}-preview" data-preview-only="true">']
    parts.append(_line(plot_x, plot_y + plot_h, plot_x + plot_w, plot_y + plot_h, stroke=theme["border"]))
    if chart_kind == "bar":
        gap = max(4.0, plot_w * 0.035)
        bar_w = max(7.0, (plot_w - gap * (len(values) + 1)) / len(values))
        for index, value in enumerate(values):
            normalized = (value - low) / span
            bar_h = max(4.0, plot_h * normalized)
            bx = plot_x + gap + index * (bar_w + gap)
            fill = theme["accent"] if index == len(values) - 1 else theme["accent_alt"]
            parts.append(_rect(bx, plot_y + plot_h - bar_h, bar_w, bar_h, fill=fill, rx=2))
    else:
        if len(values) == 1:
            points = [(plot_x + plot_w / 2, plot_y + plot_h / 2)]
        else:
            points = [
                (
                    plot_x + index * plot_w / (len(values) - 1),
                    plot_y + plot_h - plot_h * ((value - low) / span),
                )
                for index, value in enumerate(values)
            ]
        parts.append(_polyline(points, stroke=theme["accent"], width=2.2))
        for px, py in points:
            parts.append(_circle(px, py, 3.2, fill=theme["surface"], stroke=theme["accent"]))
    label_step = plot_w / len(labels)
    for index, label in enumerate(labels):
        parts.append(
            _text(
                plot_x + label_step * (index + 0.5),
                y + h - 4,
                label,
                size=7,
                fill=theme["muted_text"],
                anchor="middle",
                max_chars=4,
                max_lines=1,
            )
        )
    parts.append("</g>")
    return "".join(parts)


def _chart_panel_payload(
    chart: dict[str, Any],
    theme: dict[str, str],
) -> tuple[str, list[str], list[dict[str, Any]]]:
    chart_kind = str(chart.get("kind") or chart.get("chart_kind") or "bar")
    if chart_kind not in {"bar", "line"}:
        raise SpecError("native chart panel kind must be bar or line")
    labels = [str(item) for item in _list(chart.get("labels"))]
    if not 2 <= len(labels) <= 12:
        raise SpecError("native chart panel labels must contain 2-12 items")
    raw_series = _list(chart.get("series"))
    if not 1 <= len(raw_series) <= 3:
        raise SpecError("native chart panel series must contain 1-3 items")
    series: list[dict[str, Any]] = []
    palette = (theme["accent"], theme["contrast"], theme["accent_alt"])
    for index, raw in enumerate(raw_series):
        item = _dict(raw, field=f"native chart panel series[{index}]")
        values = _numeric_values(
            item.get("values"),
            field=f"native chart panel series[{index}].values",
            expected=len(labels),
        )
        series.append(
            {
                "name": _required_text(
                    item.get("name"),
                    field=f"native chart panel series[{index}].name",
                ),
                "values": values,
                "color": str(item.get("color") or palette[index]),
            }
        )
    return chart_kind, labels, series


def _chart_panel_preview(
    slot_id: str,
    x: float,
    y: float,
    w: float,
    h: float,
    chart: dict[str, Any],
    theme: dict[str, str],
) -> str:
    chart_kind, labels, series = _chart_panel_payload(chart, theme)
    all_values = [value for item in series for value in item["values"]]
    low = min(0.0, min(all_values))
    high = max(all_values)
    span = high - low or 1.0
    pad_left = 36.0
    pad_right = 18.0
    pad_top = 18.0
    pad_bottom = 34.0
    plot_x = x + pad_left
    plot_y = y + pad_top
    plot_w = max(120.0, w - pad_left - pad_right)
    plot_h = max(100.0, h - pad_top - pad_bottom)
    parts = [f'<g id="{slot_id}-preview" data-preview-only="true">']
    for index in range(5):
        gy = plot_y + plot_h * index / 4
        parts.append(
            _line(
                plot_x,
                gy,
                plot_x + plot_w,
                gy,
                stroke=theme["border"],
                width=0.8,
            )
        )
    if chart_kind == "bar":
        category_w = plot_w / len(labels)
        group_w = category_w * 0.72
        bar_gap = min(5.0, group_w * 0.06)
        bar_w = max(4.0, (group_w - bar_gap * (len(series) - 1)) / len(series))
        for label_index in range(len(labels)):
            group_x = plot_x + label_index * category_w + (category_w - group_w) / 2
            for series_index, item in enumerate(series):
                value = item["values"][label_index]
                normalized = (value - low) / span
                bar_h = max(3.0, plot_h * normalized)
                bx = group_x + series_index * (bar_w + bar_gap)
                parts.append(
                    _rect(
                        bx,
                        plot_y + plot_h - bar_h,
                        bar_w,
                        bar_h,
                        fill=item["color"],
                        rx=1.5,
                    )
                )
    else:
        for item in series:
            points = [
                (
                    plot_x + index * plot_w / max(1, len(labels) - 1),
                    plot_y + plot_h - plot_h * ((value - low) / span),
                )
                for index, value in enumerate(item["values"])
            ]
            parts.append(_polyline(points, stroke=item["color"], width=2.4))
            for px, py in points:
                parts.append(
                    _circle(px, py, 3.0, fill=theme["surface"], stroke=item["color"])
                )
    label_step = max(1, math.ceil(len(labels) / 8))
    for index, label in enumerate(labels):
        if index % label_step and index != len(labels) - 1:
            continue
        lx = (
            plot_x + (index + 0.5) * plot_w / len(labels)
            if chart_kind == "bar"
            else plot_x + index * plot_w / max(1, len(labels) - 1)
        )
        parts.append(
            _text(
                lx,
                y + h - 8,
                label,
                size=8,
                fill=theme["muted_text"],
                anchor="middle",
                max_chars=6,
                max_lines=1,
            )
        )
    parts.append("</g>")
    return "".join(parts)


def _micro_table_preview(
    slot_id: str,
    x: float,
    y: float,
    w: float,
    h: float,
    visual: dict[str, Any],
    theme: dict[str, str],
) -> str:
    columns = _list(visual.get("columns"))
    rows = _list(visual.get("rows"))
    if not 2 <= len(columns) <= 3:
        raise SpecError("micro table columns must contain 2-3 items")
    if not 2 <= len(rows) <= 4:
        raise SpecError("micro table rows must contain 2-4 items")
    for index, row in enumerate(rows):
        if not isinstance(row, list) or len(row) != len(columns):
            raise SpecError(f"micro table rows[{index}] must match columns")
    cell_w = w / len(columns)
    cell_h = h / (len(rows) + 1)
    parts = [f'<g id="{slot_id}-preview" data-preview-only="true">']
    parts.append(_rect(x, y, w, cell_h, fill=theme["accent"], rx=2))
    for col_index, column in enumerate(columns):
        cx = x + col_index * cell_w
        if col_index:
            parts.append(_line(cx, y, cx, y + h, stroke=theme["border"]))
        parts.append(_text(cx + cell_w / 2, y + cell_h * 0.67, column, size=7, fill=theme["surface"], weight=700, anchor="middle", max_chars=5, max_lines=1))
    for row_index, row in enumerate(rows, start=1):
        ry = y + row_index * cell_h
        parts.append(_line(x, ry, x + w, ry, stroke=theme["border"]))
        for col_index, value in enumerate(row):
            parts.append(_text(x + col_index * cell_w + cell_w / 2, ry + cell_h * 0.67, value, size=7, fill=theme["body_text"], anchor="middle", max_chars=5, max_lines=1))
    parts.append("</g>")
    return "".join(parts)


def _render_evidence_visual(
    visual: dict[str, Any],
    *,
    section_index: int,
    card_index: int,
    x: float,
    y: float,
    w: float,
    h: float,
    theme: dict[str, str],
) -> str:
    kind = str(visual.get("kind") or "metric")
    if kind == "native_chart":
        slot_id = _evidence_slot_id(
            visual,
            section_index=section_index,
            card_index=card_index,
            suffix="chart",
        )
        chart_kind = str(visual.get("chart_kind") or "bar")
        return "".join(
            (
                f'<g id="{slot_id}" data-role="native-chart-slot" data-native-chart="true" '
                f'data-native-chart-variant="micro" data-chart-type="{_esc(chart_kind)}" '
                f'data-x="{x:.1f}" data-y="{y:.1f}" data-w="{w:.1f}" data-h="{h:.1f}">',
                _rect(x, y, w, h, fill=theme["surface"], stroke=theme["border"], rx=4),
                _micro_chart_preview(slot_id, x, y, w, h, visual, theme),
                "</g>",
            )
        )
    if kind == "native_table":
        slot_id = _evidence_slot_id(
            visual,
            section_index=section_index,
            card_index=card_index,
            suffix="table",
        )
        return "".join(
            (
                f'<g id="{slot_id}" data-role="native-table-slot" data-native-table="true" '
                f'data-x="{x:.1f}" data-y="{y:.1f}" data-w="{w:.1f}" data-h="{h:.1f}">',
                _rect(x, y, w, h, fill=theme["surface"], stroke=theme["border"], rx=4),
                _micro_table_preview(slot_id, x, y, w, h, visual, theme),
                "</g>",
            )
        )
    if kind == "metric":
        value = _required_text(visual.get("value"), field="metric visual.value")
        label = _required_text(visual.get("label"), field="metric visual.label")
        return "".join(
            (
                _rect(x, y, w, h, fill=theme["surface_alt"], stroke=theme["border"], rx=4),
                _text(x + w / 2, y + h * 0.48, value, size=min(30, h * 0.32), fill=theme["accent"], weight=800, anchor="middle", max_chars=8, max_lines=1),
                _text(x + w / 2, y + h * 0.73, label, size=10, fill=theme["body_text"], anchor="middle", max_chars=max(8, int(w / 12)), max_lines=2),
            )
        )
    if kind == "icon_fact":
        icon_label = str(visual.get("icon_label") or "证").strip()[:2]
        detail = _required_text(visual.get("detail"), field="icon_fact visual.detail")
        return "".join(
            (
                _rect(x, y, w, h, fill=theme["surface_alt"], stroke=theme["border"], rx=4),
                _circle(x + w * 0.30, y + h / 2, min(26, h * 0.24), fill=theme["accent"]),
                _text(x + w * 0.30, y + h / 2 + 5, icon_label, size=12, fill=theme["surface"], weight=700, anchor="middle", max_chars=2, max_lines=1),
                _text(x + w * 0.47, y + h * 0.42, detail, size=10, fill=theme["body_text"], max_chars=max(8, int(w / 20)), max_lines=3),
            )
        )
    raise SpecError(f"unsupported evidence visual kind: {kind}")


def _render_evidence_card(
    card: dict[str, Any],
    *,
    section_index: int,
    card_index: int,
    x: float,
    y: float,
    w: float,
    h: float,
    theme: dict[str, str],
) -> str:
    title = _required_text(card.get("title"), field="evidence card.title")
    meaning = _required_text(card.get("meaning"), field="evidence card.meaning")
    insight = _required_text(card.get("insight"), field="evidence card.insight")
    highlight = card.get("highlight") or {}
    if not isinstance(highlight, dict):
        raise SpecError("evidence card.highlight must be an object")
    highlight_value = _required_text(
        highlight.get("value"),
        field="evidence card.highlight.value",
    )
    visual = _dict(card.get("visual"), field="evidence card.visual")
    insight_h = 38.0
    visual_y = y + 92.0
    visual_h = max(80.0, h - 92.0 - insight_h - 8.0)
    parts = [f'<g id="evidence-card-{section_index}-{card_index}">']
    parts.append(_rect(x, y, w, h, fill=theme["surface"], stroke=theme["border"], rx=6))
    parts.append(_badge(x + 22, y + 23, f"{card_index:02d}", theme))
    parts.append(_text(x + 45, y + 28, title, size=12, fill=theme["title_text"], weight=700, max_chars=max(8, int(w / 13)), max_lines=1))
    parts.append(_text(x + 12, y + 60, highlight.get("prefix"), size=9, fill=theme["body_text"], max_chars=7, max_lines=1))
    parts.append(_text(x + w / 2, y + 64, highlight_value, size=21, fill=theme["accent"], weight=800, anchor="middle", max_chars=10, max_lines=1))
    parts.append(_text(x + w - 12, y + 60, highlight.get("suffix"), size=9, fill=theme["muted_text"], anchor="end", max_chars=7, max_lines=1))
    parts.append(_text(x + w / 2, y + 84, meaning, size=9, fill=theme["body_text"], anchor="middle", max_chars=max(10, int(w / 10)), max_lines=1))
    parts.append(
        _render_evidence_visual(
            visual,
            section_index=section_index,
            card_index=card_index,
            x=x + 8,
            y=visual_y,
            w=w - 16,
            h=visual_h,
            theme=theme,
        )
    )
    insight_y = y + h - insight_h
    parts.append(_rect(x, insight_y, w, insight_h, fill=theme["surface_alt"], rx=4))
    parts.append(_circle(x + 17, insight_y + insight_h / 2, 9, fill=theme["accent"]))
    parts.append(_text(x + 17, insight_y + insight_h / 2 + 4, "洞", size=8, fill=theme["surface"], weight=700, anchor="middle", max_chars=1, max_lines=1))
    parts.append(_text(x + 31, insight_y + insight_h / 2 + 4, insight, size=9, fill=theme["title_text"], weight=700, max_chars=max(10, int((w - 39) / 9)), max_lines=1))
    parts.append("</g>")
    return "".join(parts)


def _render_dashboard_closure(
    closure: dict[str, Any],
    *,
    x: float,
    y: float,
    w: float,
    h: float,
    theme: dict[str, str],
    group_id: str = "evidence-dashboard-closure",
    max_steps: int = 5,
) -> str:
    title = _required_text(closure.get("title"), field="closure.title")
    steps = _items(closure, "steps", 3, max_steps)
    action_raw = closure.get("action")
    action = _dict(action_raw, field="closure.action") if action_raw is not None else None
    action_title = (
        _required_text(action.get("title"), field="closure.action.title")
        if action
        else ""
    )
    action_detail = (
        _required_text(action.get("detail"), field="closure.action.detail")
        if action
        else ""
    )
    title_h = 30.0
    action_w = min(190.0, w * 0.20) if action else 0.0
    step_gap = 8.0
    action_gap = 28.0 if action else 0.0
    chain_w = w - action_w - action_gap
    step_w = (chain_w - step_gap * (len(steps) - 1)) / len(steps)
    card_y = y + title_h + 8.0
    card_h = h - title_h - 8.0
    if step_w < 105 or card_h < 82:
        raise SpecError("rect step flow region is too small for readable content")
    parts = [f'<g id="{_slug(group_id)}">']
    parts.append(_line(x, y + 13, x + w * 0.31, y + 13, stroke=theme["accent"], width=1.5))
    parts.append(_text(x + w / 2, y + 20, title, size=15, fill=theme["title_text"], weight=700, anchor="middle", max_chars=28, max_lines=1))
    parts.append(_line(x + w * 0.69, y + 13, x + w, y + 13, stroke=theme["accent"], width=1.5))
    for index, raw in enumerate(steps, start=1):
        step = _dict(raw, field=f"closure.steps[{index - 1}]")
        sx = x + (index - 1) * (step_w + step_gap)
        parts.append(f'<g id="closure-step-{index}">')
        parts.append(_rect(sx, card_y, step_w, card_h, fill=theme["surface_alt"], stroke=theme["border"], rx=5))
        parts.append(_rect(sx, card_y, step_w, 27, fill=theme["accent"], rx=5))
        parts.append(_badge(sx + 18, card_y + 14, index, theme, fill=theme["accent"]))
        parts.append(_text(sx + 38, card_y + 19, step.get("title"), size=9, fill=theme["surface"], weight=700, max_chars=max(6, int(step_w / 11)), max_lines=1))
        icon_label = str(step.get("icon_label") or index).strip()[:2]
        parts.append(_circle(sx + step_w / 2, card_y + 49, 13, fill=theme["surface"], stroke=theme["accent"]))
        parts.append(_text(sx + step_w / 2, card_y + 53, icon_label, size=8, fill=theme["accent"], weight=700, anchor="middle", max_chars=2, max_lines=1))
        parts.append(_text(sx + 8, card_y + card_h - 11, step.get("detail"), size=8, fill=theme["body_text"], max_chars=max(7, int(step_w / 8)), max_lines=2))
        parts.append("</g>")
        if index < len(steps):
            arrow_x = sx + step_w + step_gap / 2
            parts.append(_polygon([(arrow_x - 3, card_y + card_h / 2 - 5), (arrow_x + 4, card_y + card_h / 2), (arrow_x - 3, card_y + card_h / 2 + 5)], fill=theme["accent"]))
    if action:
        action_x = x + w - action_w
        parts.append('<g id="closure-action">')
        parts.append(_rect(action_x, card_y, action_w, card_h, fill=theme["surface"], stroke=theme["accent"], rx=6))
        parts.append(_rect(action_x, card_y, action_w, 27, fill=theme["accent"], rx=6))
        parts.append(_text(action_x + action_w / 2, card_y + 19, action_title, size=10, fill=theme["surface"], weight=700, anchor="middle", max_chars=10, max_lines=1))
        parts.append(_circle(action_x + 31, card_y + 56, 17, fill=theme["accent"]))
        parts.append(_polyline([(action_x + 22, card_y + 56), (action_x + 28, card_y + 62), (action_x + 40, card_y + 48)], stroke=theme["surface"], width=3))
        parts.append(_text(action_x + 57, card_y + 53, action_detail, size=9, fill=theme["body_text"], max_chars=max(9, int((action_w - 67) / 9)), max_lines=3))
        parts.append("</g>")
    parts.append("</g>")
    return "".join(parts)


def _render_chart_insight_card(spec: dict[str, Any]) -> str:
    data = _dict(spec.get("data"), field="data")
    card = _dict(data.get("card"), field="data.card")
    x, y, w, h, heading, theme = _body_region(spec)
    if w < 240 or h < 250:
        raise SpecError("chart insight card region must be at least 240x250")
    return "".join(
        (
            heading,
            '<g id="chart-insight-card">',
            _render_evidence_card(
                card,
                section_index=1,
                card_index=1,
                x=x,
                y=y,
                w=w,
                h=h,
                theme=theme,
            ),
            "</g>",
        )
    )


def _render_native_chart_panel(spec: dict[str, Any]) -> str:
    data = _dict(spec.get("data"), field="data")
    chart = _dict(data.get("chart"), field="data.chart")
    chart_title = _required_text(chart.get("title"), field="data.chart.title")
    source = _required_text(chart.get("source"), field="data.chart.source")
    chart_kind, _labels, series = _chart_panel_payload(chart, _theme(spec))
    x, y, w, h, heading, theme = _body_region(spec)
    if w < 520 or h < 320:
        raise SpecError("native chart panel region must be at least 520x320")
    slot_id = _slug(str(chart.get("slot_id") or "primary-chart"))
    slot_y = y + 44.0
    slot_h = h - 76.0
    legend_text = " / ".join(str(item["name"]) for item in series)
    return "".join(
        (
            heading,
            '<g id="native-chart-panel">',
            _rect(x, y, w, h, fill=theme["surface"], stroke=theme["border"], rx=6),
            _text(x + 18, y + 27, chart_title, size=15, fill=theme["title_text"], weight=700, max_chars=max(18, int(w / 15)), max_lines=1),
            _text(x + w - 18, y + 27, legend_text, size=9, fill=theme["muted_text"], anchor="end", max_chars=max(12, int(w / 18)), max_lines=1),
            f'<g id="{slot_id}" data-role="native-chart-slot" data-native-chart="true" '
            f'data-chart-type="{_esc(chart_kind)}" data-x="{x + 8:.1f}" '
            f'data-y="{slot_y:.1f}" data-w="{w - 16:.1f}" data-h="{slot_h:.1f}">',
            _rect(x + 8, slot_y, w - 16, slot_h, fill=theme["surface"], stroke=theme["border"], rx=4),
            _chart_panel_preview(slot_id, x + 8, slot_y, w - 16, slot_h, chart, theme),
            "</g>",
            _text(x + 14, y + h - 10, f"来源：{source}", size=8, fill=theme["muted_text"], max_chars=max(24, int(w / 10)), max_lines=1),
            "</g>",
        )
    )


def _render_insight_text_card(spec: dict[str, Any]) -> str:
    data = _dict(spec.get("data"), field="data")
    card = _dict(data.get("card"), field="data.card")
    title = _required_text(card.get("title"), field="data.card.title")
    bullets = _items(card, "bullets", 1, 3)
    x, y, w, h, heading, theme = _body_region(spec)
    if w < 240 or h < 120:
        raise SpecError("insight text card region must be at least 240x120")
    tone = str(card.get("tone") or "insight")
    tone_color = {
        "insight": theme["accent"],
        "risk": theme["risk"],
        "action": theme["contrast"],
        "neutral": theme["accent_alt"],
    }.get(tone)
    if tone_color is None:
        raise SpecError("insight text card tone must be insight, risk, action or neutral")
    metric = card.get("metric")
    if metric is not None and not isinstance(metric, dict):
        raise SpecError("insight text card metric must be an object")
    footer = str(card.get("footer") or "").strip()
    header_h = 42.0
    footer_h = 24.0 if footer else 0.0
    body_h = h - header_h - footer_h
    if body_h < len(bullets) * 24 + 10:
        raise SpecError("insight text card region is too small for readable bullets")
    parts = [heading, '<g id="insight-text-card">']
    parts.append(_rect(x, y, w, h, fill=theme["surface"], stroke=theme["border"], rx=6))
    parts.append(_rect(x, y, 6, h, fill=tone_color, rx=3))
    parts.append(_circle(x + 26, y + 21, 11, fill=tone_color))
    parts.append(_text(x + 26, y + 25, str(card.get("icon_label") or "洞")[:2], size=8, fill=theme["surface"], weight=700, anchor="middle", max_chars=2, max_lines=1))
    title_width = w - 64 - (100 if metric else 0)
    parts.append(_text(x + 44, y + 27, title, size=13, fill=theme["title_text"], weight=700, max_chars=max(8, int(title_width / 13)), max_lines=1))
    if isinstance(metric, dict):
        value = _required_text(metric.get("value"), field="data.card.metric.value")
        label = str(metric.get("label") or "").strip()
        parts.append(_text(x + w - 14, y + 24, value, size=18, fill=tone_color, weight=800, anchor="end", max_chars=8, max_lines=1))
        if label:
            parts.append(_text(x + w - 14, y + 38, label, size=7, fill=theme["muted_text"], anchor="end", max_chars=8, max_lines=1))
    row_h = body_h / len(bullets)
    for index, bullet in enumerate(bullets, start=1):
        cy = y + header_h + row_h * (index - 0.5)
        parts.append(_circle(x + 24, cy - 3, 3.5, fill=tone_color))
        parts.append(_text(x + 36, cy + 1, bullet, size=10, fill=theme["body_text"], max_chars=max(14, int((w - 50) / 10)), max_lines=2))
    if footer:
        footer_y = y + h - footer_h
        parts.append(_rect(x + 6, footer_y, w - 6, footer_h, fill=theme["surface_alt"], rx=3))
        parts.append(_text(x + 16, footer_y + 16, footer, size=8, fill=theme["muted_text"], max_chars=max(18, int((w - 30) / 9)), max_lines=1))
    parts.append("</g>")
    return "".join(parts)


def _render_full_width_rect_step_flow(spec: dict[str, Any]) -> str:
    data = _dict(spec.get("data"), field="data")
    steps = _items(data, "steps", 3, 6)
    normalized_data = dict(data)
    normalized_data["steps"] = steps
    x, y, w, h, heading, theme = _body_region(spec)
    if w < 620 or h < 125:
        raise SpecError("full width rect step flow region must be at least 620x125")
    return "".join(
        (
            heading,
            _render_dashboard_closure(
                normalized_data,
                x=x,
                y=y,
                w=w,
                h=h,
                theme=theme,
                group_id="full-width-rect-step-flow",
                max_steps=6,
            ),
        )
    )


def _render_sectioned_evidence_dashboard(spec: dict[str, Any]) -> str:
    data = _dict(spec.get("data"), field="data")
    sections = _items(data, "sections", 1, 2)
    closure_raw = data.get("closure")
    closure = _dict(closure_raw, field="closure") if closure_raw is not None else None
    x, y, w, h, heading, theme = _body_region(spec)
    closure_gap = 12.0 if closure else 0.0
    closure_h = min(156.0, h * 0.32) if closure else 0.0
    section_h = h - closure_h - closure_gap
    section_gap = 16.0
    section_w = (w - section_gap * (len(sections) - 1)) / len(sections)
    parts = [heading, '<g id="sectioned-evidence-dashboard">']
    for section_index, raw in enumerate(sections, start=1):
        section = _dict(raw, field=f"sections[{section_index - 1}]")
        title = _required_text(section.get("title"), field=f"sections[{section_index - 1}].title")
        cards = _items(section, "cards", 2, 3)
        sx = x + (section_index - 1) * (section_w + section_gap)
        header_h = 42.0
        inner_pad = 10.0
        card_gap = 8.0
        card_w = (section_w - inner_pad * 2 - card_gap * (len(cards) - 1)) / len(cards)
        card_y = y + header_h + 8.0
        card_h = section_h - header_h - 18.0
        if card_w < 145 or card_h < 210:
            raise SpecError("sectioned evidence cards are too small for readable content")
        parts.append(f'<g id="section-{section_index}">')
        parts.append(_rect(sx, y, section_w, section_h, fill=theme["surface_alt"], stroke=theme["border"], rx=7))
        icon_label = str(section.get("icon_label") or section_index).strip()[:2]
        pill_w = min(section_w * 0.62, max(170.0, len(title) * 18.0 + 58.0))
        pill_x = sx + (section_w - pill_w) / 2
        parts.append(_rect(pill_x, y + 7, pill_w, 30, fill=theme["accent"], rx=5))
        parts.append(_circle(pill_x + 20, y + 22, 10, fill=theme["surface"], stroke=theme["surface"]))
        parts.append(_text(pill_x + 20, y + 26, icon_label, size=8, fill=theme["accent"], weight=700, anchor="middle", max_chars=2, max_lines=1))
        parts.append(_text(pill_x + 38, y + 27, title, size=13, fill=theme["surface"], weight=700, max_chars=max(10, int((pill_w - 48) / 13)), max_lines=1))
        for card_index, card_raw in enumerate(cards, start=1):
            card = _dict(card_raw, field=f"sections[{section_index - 1}].cards[{card_index - 1}]")
            cx = sx + inner_pad + (card_index - 1) * (card_w + card_gap)
            parts.append(
                _render_evidence_card(
                    card,
                    section_index=section_index,
                    card_index=card_index,
                    x=cx,
                    y=card_y,
                    w=card_w,
                    h=card_h,
                    theme=theme,
                )
            )
        parts.append("</g>")
    if closure:
        parts.append(
            _render_dashboard_closure(
                closure,
                x=x,
                y=y + section_h + closure_gap,
                w=w,
                h=closure_h,
                theme=theme,
            )
        )
    parts.append("</g>")
    return "".join(parts)


def _append_evidence_card_native_data(
    native_data: dict[str, Any],
    card: dict[str, Any],
    *,
    section_index: int,
    card_index: int,
    theme: dict[str, str],
) -> None:
    visual = _dict(card.get("visual") or {"kind": "metric"}, field="card.visual")
    kind = str(visual.get("kind") or "metric")
    if kind == "native_chart":
        labels = _list(visual.get("labels"))
        if not 2 <= len(labels) <= 5:
            raise SpecError("micro chart labels must contain 2-5 items")
        raw_series = _list(visual.get("series"))
        if len(raw_series) != 1 or not isinstance(raw_series[0], dict):
            raise SpecError("micro chart series must contain exactly one object")
        series = _dict(raw_series[0], field="micro chart series[0]")
        values = _numeric_values(
            series.get("values"),
            field="micro chart series[0].values",
            expected=len(labels),
        )
        chart_kind = str(visual.get("chart_kind") or "bar")
        if chart_kind not in {"bar", "line"}:
            raise SpecError("micro chart chart_kind must be bar or line")
        color = str(series.get("color") or theme["accent"])
        slot_id = _evidence_slot_id(
            visual,
            section_index=section_index,
            card_index=card_index,
            suffix="chart",
        )
        native_data["charts"].append(
            {
                "slot_id": slot_id,
                "kind": chart_kind,
                "title": str(visual.get("title") or card.get("title") or ""),
                "labels": [str(label) for label in labels],
                "series": [
                    {
                        "name": str(
                            series.get("name") or card.get("title") or "指标"
                        ),
                        "values": values,
                        "color": color,
                    }
                ],
                "colors": [color],
                "source": str(visual.get("source") or ""),
                "insight": str(
                    visual.get("insight") or card.get("insight") or ""
                ),
                "style": {
                    "axis_text_color": theme["muted_text"],
                    "legend_text_color": theme["muted_text"],
                    "grid_color": theme["border"],
                },
                "options": {
                    "legend": False,
                    "show_title": False,
                    "value_axis": {
                        "format": str(visual.get("value_format") or "0")
                    },
                },
            }
        )
    elif kind == "native_table":
        columns = _list(visual.get("columns"))
        rows = _list(visual.get("rows"))
        if not 2 <= len(columns) <= 3:
            raise SpecError("micro table columns must contain 2-3 items")
        if not 2 <= len(rows) <= 4:
            raise SpecError("micro table rows must contain 2-4 items")
        for row_index, row in enumerate(rows):
            if not isinstance(row, list) or len(row) != len(columns):
                raise SpecError(f"micro table rows[{row_index}] must match columns")
        slot_id = _evidence_slot_id(
            visual,
            section_index=section_index,
            card_index=card_index,
            suffix="table",
        )
        native_data["tables"].append(
            {
                "slot_id": slot_id,
                "title": str(visual.get("title") or card.get("title") or ""),
                "columns": [str(column) for column in columns],
                "rows": [[str(cell) for cell in row] for row in rows],
                "style": {
                    "font_size": 7,
                    "header_fill": theme["accent"],
                    "body_fill": theme["surface"],
                    "text_color": theme["body_text"],
                    "header_text_color": theme["surface"],
                },
            }
        )


def _native_data_from_normalized_spec(spec: dict[str, Any]) -> dict[str, Any]:
    """把局部组合组件中的原生 slot 数据提取为 renderer 可消费的 sidecar。"""

    native_data: dict[str, Any] = {"version": 1, "charts": [], "tables": []}
    pattern = spec["pattern"]
    if pattern not in {
        "sectioned_evidence_dashboard",
        "native_chart_panel",
        "chart_insight_card",
    }:
        return native_data

    data = _dict(spec.get("data"), field="data")
    theme = _theme(spec)
    if pattern == "native_chart_panel":
        chart = _dict(data.get("chart"), field="data.chart")
        chart_kind, labels, series = _chart_panel_payload(chart, theme)
        slot_id = _slug(str(chart.get("slot_id") or "primary-chart"))
        native_data["charts"].append(
            {
                "slot_id": slot_id,
                "kind": chart_kind,
                "title": str(chart.get("title") or ""),
                "labels": labels,
                "series": series,
                "colors": [str(item["color"]) for item in series],
                "source": str(chart.get("source") or ""),
                "insight": str(chart.get("insight") or ""),
                "data_unit": str(chart.get("data_unit") or ""),
                "style": {
                    "axis_text_color": theme["muted_text"],
                    "legend_text_color": theme["muted_text"],
                    "grid_color": theme["border"],
                },
                "options": {
                    "legend": len(series) > 1,
                    "show_title": False,
                    "value_axis": {
                        "format": str(chart.get("value_format") or "0")
                    },
                },
            }
        )
        return native_data
    if pattern == "chart_insight_card":
        card = _dict(data.get("card"), field="data.card")
        _append_evidence_card_native_data(
            native_data,
            card,
            section_index=1,
            card_index=1,
            theme=theme,
        )
        return native_data

    sections = _items(data, "sections", 1, 2)
    for section_index, section_raw in enumerate(sections, start=1):
        section = _dict(section_raw, field=f"sections[{section_index - 1}]")
        cards = _items(section, "cards", 2, 3)
        for card_index, card_raw in enumerate(cards, start=1):
            card = _dict(
                card_raw,
                field=f"sections[{section_index - 1}].cards[{card_index - 1}]",
            )
            _append_evidence_card_native_data(
                native_data,
                card,
                section_index=section_index,
                card_index=card_index,
                theme=theme,
            )
    return native_data


def native_data_from_spec(spec: dict[str, Any]) -> dict[str, Any]:
    """公开 helper：从结构化输入生成可与 SVG 同目录保存的 native-data。"""

    return _native_data_from_normalized_spec(normalize_spec(spec))


RENDERERS: dict[str, Callable[[dict[str, Any]], str]] = {
    "phased_roadmap_matrix": _render_phased_roadmap,
    "diagnostic_insight_grid": _render_diagnostic_grid,
    "shared_source_platform_value": _render_shared_source,
    "stage_mechanism_scorecard": _render_stage_scorecard,
    "operating_model_blueprint": _render_operating_model,
    "retrospect_outlook_pyramid": _render_retrospect_pyramid,
    "duotone_problem_improve": _render_duotone,
    "calendar_summary_rail": _render_calendar,
    "target_action_timeline": _render_target_timeline,
    "north_star_kpi_roof": _render_north_star,
    "arrow_ribbon_metrics": _render_arrow_ribbon,
    "highlight_matrix_core": _render_highlight_matrix,
    "sectioned_evidence_dashboard": _render_sectioned_evidence_dashboard,
    "native_chart_panel": _render_native_chart_panel,
    "insight_text_card": _render_insight_text_card,
    "chart_insight_card": _render_chart_insight_card,
    "full_width_rect_step_flow": _render_full_width_rect_step_flow,
}


def normalize_spec(spec: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(spec, dict):
        raise SpecError("spec must be an object")
    schema_version = str(spec.get("schema_version") or SCHEMA_VERSION)
    if schema_version != SCHEMA_VERSION:
        raise SpecError(f"schema_version must be {SCHEMA_VERSION}")
    pattern = str(spec.get("pattern") or "").strip()
    if pattern not in RENDERERS:
        raise SpecError(f"unknown pattern: {pattern or '<empty>'}")
    normalized = json.loads(json.dumps(spec, ensure_ascii=False))
    normalized["schema_version"] = SCHEMA_VERSION
    normalized["pattern"] = pattern
    normalized.setdefault("series_id", "rd_efficiency_blue")
    region_minimums = {
        "native_chart_panel": (520.0, 320.0),
        "insight_text_card": (240.0, 120.0),
        "chart_insight_card": (240.0, 250.0),
        "full_width_rect_step_flow": (620.0, 125.0),
    }
    minimum_width, minimum_height = region_minimums.get(pattern, (640.0, 300.0))
    normalized["region"] = dict(
        zip(
            ("x", "y", "w", "h"),
            _region(
                normalized,
                minimum_width=minimum_width,
                minimum_height=minimum_height,
            ),
            strict=True,
        )
    )
    _theme(normalized)
    _dict(normalized.get("data"), field="data")
    return normalized


def _svg_document(
    normalized: dict[str, Any],
    body: str,
    *,
    native_data_ref: str | None = None,
) -> str:
    pattern = normalized["pattern"]
    series_id = str(normalized.get("series_id") or "rd_efficiency_blue")
    resolved_native_data_ref = str(
        native_data_ref or normalized.get("native_data_ref") or ""
    ).strip()
    native_data_attr = (
        f' data-native-data-ref="{_esc(resolved_native_data_ref)}"'
        if resolved_native_data_ref
        else ""
    )
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
        f'viewBox="0 0 {W} {H}"{native_data_attr}>'
        f'<g id="series-composite" data-series="{_esc(series_id)}" '
        'data-component-scope="content-region">'
        f'<g id="pattern-{_slug(pattern)}">{body}</g>'
        "</g></svg>"
    )


def build_svg(spec: dict[str, Any]) -> str:
    normalized = normalize_spec(spec)
    body = RENDERERS[normalized["pattern"]](normalized)
    return _svg_document(normalized, body)


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SpecError(f"cannot read JSON spec: {path}") from exc
    if not isinstance(value, dict):
        raise SpecError("spec root must be an object")
    return value


def main() -> int:
    parser = argparse.ArgumentParser(description="Build reusable template-series SVG composites")
    parser.add_argument("--spec", required=True, type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--native-output", type=Path)
    parser.add_argument("--write-normalized", type=Path)
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args()
    try:
        spec = _read_json(args.spec)
        normalized = normalize_spec(spec)
        # 调用 renderer 完成 pattern-specific 容量校验；validate-only 不落 SVG。
        body = RENDERERS[normalized["pattern"]](normalized)
        if args.write_normalized:
            args.write_normalized.parent.mkdir(parents=True, exist_ok=True)
            args.write_normalized.write_text(
                json.dumps(normalized, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
        if not args.validate_only:
            if args.output is None:
                raise SpecError("--output is required unless --validate-only is used")
            args.output.parent.mkdir(parents=True, exist_ok=True)
            native_data_ref = args.native_output.name if args.native_output else None
            svg = _svg_document(
                normalized,
                body,
                native_data_ref=native_data_ref,
            )
            args.output.write_text(svg, encoding="utf-8")
            if args.native_output:
                args.native_output.parent.mkdir(parents=True, exist_ok=True)
                args.native_output.write_text(
                    json.dumps(
                        _native_data_from_normalized_spec(normalized),
                        ensure_ascii=False,
                        indent=2,
                    )
                    + "\n",
                    encoding="utf-8",
                )
        print(
            json.dumps(
                {
                    "ok": True,
                    "schema_version": SCHEMA_VERSION,
                    "pattern": normalized["pattern"],
                    "series_id": normalized["series_id"],
                    "output": str(args.output) if args.output else None,
                    "native_output": (
                        str(args.native_output) if args.native_output else None
                    ),
                },
                ensure_ascii=False,
            )
        )
        return 0
    except SpecError as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
