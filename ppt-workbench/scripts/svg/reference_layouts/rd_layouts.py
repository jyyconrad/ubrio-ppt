"""Editable R01-R15 reference compositions for the blue dense report family.

Each renderer mirrors one inspected screenshot's visible composition while
keeping all business text and native chart/table data replaceable.
"""

from __future__ import annotations

from copy import deepcopy
import re
from typing import Any

from .common import BLUE, INK, LIGHT, LINE, MID, PURPLE, TEAL, Svg, wrap


WHITE = "#FFFFFF"
PALE = "#F7F9FC"
SKY = "#DCE9F8"
GREEN = "#EAF6EE"
GREY = "#8A929E"
SOFT_LINE = "#DEE5ED"


def _deep_merge(base: dict[str, Any], patch: dict[str, Any] | None) -> dict[str, Any]:
    result = deepcopy(base)
    for key, value in (patch or {}).items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = deepcopy(value)
    return result


def _content(reference_id: str, content: dict[str, Any] | None) -> dict[str, Any]:
    return _deep_merge(DEFAULTS[reference_id], content)


def _rd_title(svg: Svg, value: str, subtitle: str | None = None, size: float = 42,
              *, line: str = "none", line_y: float = 84) -> None:
    svg.title(value, subtitle, size)
    if line == "short_blue":
        svg.line(28, line_y, 98, line_y, BLUE, 3)
        svg.line(98, line_y, 1248, line_y, SOFT_LINE, 1)
    elif line == "full_hairline":
        svg.line(28, line_y, 1248, line_y, SOFT_LINE, 1)


def _section(svg: Svg, y: float, label: str, x: float = 32, w: float = 1216,
             *, label_width: float | None = None, line_left: float | None = None,
             line_right: float | None = None, box_fill: str = WHITE) -> None:
    line_start = x if line_left is None else line_left
    line_end = x + w if line_right is None else line_right
    box_w = label_width or min(360, max(160, len(label) * 20 + 30))
    box_x = x + (w - box_w) / 2
    svg.line(line_start, y, box_x - 10, y, BLUE, 1.2)
    svg.line(box_x + box_w + 10, y, line_end, y, BLUE, 1.2)
    svg.rect(box_x, y - 17, box_w, 34, box_fill, "none", 0)
    svg.text(x + w / 2, y + 8, label, 21, BLUE, True, anchor="middle")


def _bar_section_heading(svg: Svg, x: float, y: float, w: float, value: str) -> None:
    svg.rect(x, y - 22, 6, 30, BLUE, "none", 0)
    svg.text(x + 18, y, value, 20, BLUE, True)
    label_w = min(330, max(150, len(value) * 20 + 18))
    svg.line(x + 18 + label_w, y - 7, x + w, y - 7, SOFT_LINE, 1)


def _icon_backplate(svg: Svg, icon: str, x: float, y: float, size: float,
                    *, style: str = "circle", accent: str = BLUE) -> None:
    if style == "square":
        svg.rect(x, y, size, size, accent, "none", 7)
        svg.icon(icon, x + size * 0.22, y + size * 0.22, size * 0.56, WHITE)
    elif style == "halo":
        svg.circle(x + size / 2, y + size / 2, size / 2, LIGHT)
        svg.circle(x + size / 2, y + size / 2, size * 0.34, accent)
        svg.icon(icon, x + size * 0.28, y + size * 0.28, size * 0.44, WHITE)
    else:
        svg.circle(x + size / 2, y + size / 2, size / 2, accent)
        svg.icon(icon, x + size * 0.24, y + size * 0.24, size * 0.52, WHITE)


def _text_advance(value: str, size: float) -> float:
    return sum(size * (1.0 if ord(char) > 255 else 0.56) for char in str(value))


def _result_value(svg: Svg, x: float, y: float, value: str, *, width: float,
                  size: float = 30, role: str = "diagram") -> None:
    """Render an explicit before→after contract without guessing business semantics."""
    if "→" not in value:
        svg.text(x, y, value, size, BLUE, True, width=width,
                 max_lines=1, role=role)
        return
    if value.count("→") != 1:
        raise ValueError("result value must contain at most one 'before→after' connector")
    before, after = [part.strip() for part in value.split("→", 1)]
    match = re.fullmatch(r"([+\-≤≥]?\d[\d,.]*)(.*)", after)
    after_number, unit = (match.group(1), match.group(2)) if match else (after, "")
    before_size = max(20, size - 6)
    arrow_size = max(17, size - 9)
    unit_size = max(12, size - 15)
    required = (_text_advance(before, before_size) + _text_advance("→", arrow_size)
                + _text_advance(after_number, size) + _text_advance(unit, unit_size) + 24)
    if required > width:
        raise ValueError(f"result value exceeds fixed {size}px slot: {value!r}")
    cursor = x
    svg.text(cursor, y, before, before_size, GREY, True, role=role, max_lines=1)
    cursor += _text_advance(before, before_size) + 7
    svg.text(cursor, y, "→", arrow_size, GREY, True, role=role, max_lines=1)
    cursor += _text_advance("→", arrow_size) + 7
    svg.text(cursor, y, after_number, size, BLUE, True, role=role, max_lines=1)
    cursor += _text_advance(after_number, size) + 4
    if unit:
        svg.text(cursor, y, unit, unit_size, BLUE, True, role=role, max_lines=1)


def _focus_value(svg: Svg, x: float, y: float, value: str, *, width: float,
                 size: float = 28, role: str = "diagram") -> None:
    """Separate an optional qualifier and unit from one numeric focus."""
    match = re.fullmatch(r"(.*?)([+\-≤≥]?\d[\d,.]*)(.*)", value.strip())
    if not match:
        svg.text(x, y, value, size, BLUE, True, width=width,
                 max_lines=1, role=role)
        return
    qualifier, number, unit = match.groups()
    side_size = 12
    required = (_text_advance(qualifier, 15) + _text_advance(number, size)
                + _text_advance(unit, side_size) + (5 if qualifier else 0)
                + (4 if unit else 0))
    if required > width:
        raise ValueError(f"focus value exceeds fixed {size}px slot: {value!r}")
    cursor = x
    if qualifier:
        svg.text(cursor, y, qualifier, 15, GREY, True, role=role, max_lines=1)
        cursor += _text_advance(qualifier, 15) + 5
    svg.text(cursor, y, number, size, BLUE, True, role=role, max_lines=1)
    cursor += _text_advance(number, size) + 4
    if unit:
        svg.text(cursor, y, unit, side_size, BLUE, True, role=role, max_lines=1)


def _metric_summary(svg: Svg, x: float, y: float, value: str, *, width: float) -> None:
    """Emphasize only explicit current/target/reference or threshold summaries."""
    arrow_match = re.fullmatch(
        r"(当前)([+\-≤≥]?\d[\d,.]*)([^→\s]*)\s*→\s*(目标|参考)([+\-≤≥]?\d[\d,.]*)(.*)",
        value.strip(),
    )
    if arrow_match:
        left_label, left_number, left_unit, right_label, right_number, right_unit = arrow_match.groups()
        pieces = [
            (left_label, 12, GREY, False),
            (left_number, 20, BLUE, True),
            (left_unit, 12, BLUE, True),
            ("→", 14, GREY, True),
            (right_label, 12, GREY, False),
            (right_number, 20, BLUE, True),
            (right_unit, 12, BLUE, True),
        ]
    elif "阈值" in value:
        threshold_match = re.fullmatch(r"(.+?)([+\-≤≥]?\d[\d,.]*)(.*)", value.strip())
        if not threshold_match:
            svg.text(x, y, value, 12, INK, width=width, leading=16, role="chart")
            return
        label, number, unit = threshold_match.groups()
        pieces = [
            (label, 12, GREY, False),
            (number, 20, BLUE, True),
            (unit, 12, BLUE, True),
        ]
    else:
        svg.text(x, y, value, 12, INK, width=width, leading=16, role="chart")
        return
    required = sum(_text_advance(text, size) for text, size, _, _ in pieces)
    required += 3 * (len(pieces) - 1)
    if required > width:
        raise ValueError(f"metric summary exceeds fixed focus slot: {value!r}")
    cursor = x
    for index, (text, size, color, bold) in enumerate(pieces):
        svg.text(cursor, y, text, size, color, bold, role="chart", max_lines=1)
        cursor += _text_advance(text, size)
        if index < len(pieces) - 1:
            cursor += 3


def _icon_label(svg: Svg, icon: str, x: float, y: float, label: str,
                text: str, width: float, accent: str = BLUE, size: float = 15) -> None:
    svg.icon(icon, x, y - 8, 30, accent)
    svg.text(x + 42, y + 8, label, 15, accent, True, width=width - 42)
    svg.text(x + 42, y + 31, text, size, INK, width=width - 42, leading=size * 1.3)


def _bounded_multiline(svg: Svg, x: float, y: float, value: str, *, width: float,
                       size: float, color: str, anchor: str, leading: float,
                       max_lines: int, role: str) -> None:
    lines = wrap(value, width, size)
    if len(lines) > max_lines:
        raise ValueError(f"text exceeds {max_lines}-line capacity: {str(value)[:100]!r}")
    for index, line in enumerate(lines):
        svg.text(x, y + index * leading, line, size, color,
                 anchor=anchor, width=width, max_lines=1, role=role)


def _metric_card(svg: Svg, x: float, y: float, w: float, h: float, item: dict[str, Any],
                 accent: str = BLUE) -> None:
    svg.rect(x, y, w, h, WHITE, LINE, 4)
    svg.icon(item.get("icon", "chart-bar"), x + 18, y + 24, 36, WHITE, True, accent)
    svg.text(x + 70, y + 31, item["label"], 15, INK, True, width=w - 82, max_lines=1)
    _result_value(svg, x + 18, y + 99, item["value"], width=w - 36,
                  size=max(28, item.get("value_size", 28)))
    if item.get("detail"):
        svg.rect(x + 8, y + h - 36, w - 16, 36, LIGHT, "none", 0)
        svg.text(x + 18, y + h - 13, item["detail"], 15, accent, True, width=w - 36,
                 max_lines=1)


def _flow_arrow(svg: Svg, x: float, y: float, w: float, h: float, label: str,
                number: int, color: str = BLUE, icon: str | None = None,
                *, label_inside: bool = True) -> None:
    svg.poly([(x, y), (x + w - 22, y), (x + w, y + h / 2),
              (x + w - 22, y + h), (x, y + h), (x + 16, y + h / 2)], color)
    svg.circle(x + 28, y + h / 2, 15, WHITE)
    svg.text(x + 28, y + h / 2 + 5, str(number), 14, color, True,
             anchor="middle", role="process")
    if icon:
        svg.icon(icon, x + 52, y + h / 2 - 14, 28, WHITE)
    if label_inside:
        svg.text(x + w / 2 + (22 if icon else 10), y + h / 2 + 6,
                 label, 15, WHITE, True, anchor="middle", role="process")


def _diagnosis_rows(svg: Svg, x: float, y: float, w: float, rows: list[dict[str, Any]],
                    row_h: float = 58) -> None:
    for index, row in enumerate(rows):
        yy = y + index * row_h
        fill = GREEN if index == len(rows) - 1 else (LIGHT if index == 0 else WHITE)
        svg.rect(x, yy, w, row_h, fill, LINE, 0)
        svg.icon(row["icon"], x + 14, yy + 14, 28, TEAL if index == len(rows) - 1 else BLUE)
        svg.text(x + 52, yy + 25, row["label"], 13.5,
                 TEAL if index == len(rows) - 1 else BLUE, True, role="diagram")
        if row.get("items"):
            max_items = 3 if index == len(rows) - 1 else 2
            for line_index, text in enumerate(row["items"][:max_items]):
                svg.text(x + 142, yy + 20 + line_index * 21, "• " + text,
                         12, INK, width=w - 152, role="diagram")
        else:
            svg.text(x + 142, yy + 24, row["text"], 12.5, INK,
                     width=w - 152, leading=16, role="diagram")


def _loop_arrows(svg: Svg, x1: float, y: float, x2: float, color: str = BLUE) -> None:
    """Draw two editable curved connectors to communicate a feedback loop."""
    mid = (x1 + x2) / 2
    svg.path(f"M {x1} {y} Q {mid} {y - 30} {x2} {y}", "none", color, 2)
    svg.poly([(x2, y), (x2 - 10, y - 5), (x2 - 8, y + 5)], color)
    svg.path(f"M {x2} {y + 18} Q {mid} {y + 48} {x1} {y + 18}", "none", color, 2)
    svg.poly([(x1, y + 18), (x1 + 10, y + 13), (x1 + 8, y + 23)], color)


def render_r01(content: dict[str, Any] | None = None):
    c = _content("R01", content)
    svg = Svg()
    _rd_title(svg, c["title"])
    svg.line(28, 82, 98, 82, BLUE, 3)
    svg.text(38, 116, c["stage_heading"], 19, BLUE, True)
    step_y = [183, 157, 131]
    xs = [42, 432, 822]
    colors = ["#0C438C", "#1559A5", "#0B397B"]
    svg.poly([(42, 378), (42, 173), (392, 173), (452, 147),
              (782, 147), (842, 121), (1182, 121), (1182, 378)], PALE)
    svg.line(417, 220, 417, 371, SOFT_LINE, 1)
    svg.line(807, 194, 807, 371, SOFT_LINE, 1)
    for i, stage in enumerate(c["stages"]):
        x, y = xs[i], step_y[i]
        svg.line(x + 20, y - 10, x + 350, y - 10, colors[i], 4)
        if i < 2:
            svg.line(x + 350, y - 10, xs[i + 1] + 20, step_y[i + 1] - 10, colors[i], 4)
        svg.number(x + 42, y + 31, f"0{i + 1}", 20)
        svg.text(x + 86, y + 37, stage["label"], 17, BLUE, True, width=250)
        for j, item in enumerate(stage["items"]):
            _icon_label(svg, item["icon"], x + 24, y + 68 + j * 44, "", item["text"], 320, size=15)
    svg.text(38, 407, c["trend_heading"], 19, BLUE, True)
    for i, item in enumerate(c["trends"]):
        x = 38 + i * 408
        svg.rect(x, 429, 390, 126, WHITE, SOFT_LINE, 3)
        _icon_backplate(svg, item["icon"], x + 21, 450, 54)
        svg.text(x + 96, 463, item["label"], 18, BLUE, True)
        svg.text(x + 96, 494, item["text"], 15, INK, width=270, leading=19, max_lines=3)
    svg.rect(32, 570, 1216, 126, BLUE, "none", 5)
    svg.icon("target", 52, 599, 42, WHITE)
    svg.text(106, 621, c["bottom_label"], 18, WHITE, True, width=110)
    for i, item in enumerate(c["bottom"]):
        x = 225 + i * 335
        if i:
            svg.line(x - 20, 586, x - 20, 680, "#6D88AD", 1, True)
        svg.rect(x + 38, 590, 112, 31, WHITE, "none", 14)
        svg.icon(item["icon"], x, 590, 32, WHITE)
        svg.text(x + 94, 611, item["label"], 15, BLUE, True, anchor="middle")
        svg.text(x + 48, 647, item["text"], 15, WHITE, width=270, leading=19, max_lines=3)
    return svg.finish()


def render_r02(content: dict[str, Any] | None = None):
    c = _content("R02", content)
    svg = Svg()
    _rd_title(svg, c["title"], line="short_blue", line_y=83)
    svg.rect(34, 110, 455, 507, WHITE, LINE, 5)
    _section(svg, 137, c["triangle_heading"], 60, 405)
    # Three straight-edged directional blocks wrap a small central aperture.
    responsibility_blocks = [
        {
            "points": [(202, 252), (265, 220), (328, 252),
                       (370, 334), (265, 398), (160, 334)],
            "color": "#0D59C4", "label": (265, 270),
            "body": (265, 300, 210, "middle"),
            "node": (265, 195), "line": (265, 226, 265, 239),
        },
        {
            "points": [(160, 337), (228, 378), (228, 431), (265, 442),
                       (265, 548), (157, 548), (105, 500), (103, 406)],
            "color": TEAL, "label": (176, 430),
            "body": (132, 458, 126, "start"),
            "node": (85, 474), "line": (113, 462, 151, 449),
        },
        {
            "points": [(370, 337), (302, 378), (302, 431), (265, 442),
                       (265, 548), (373, 548), (425, 500), (427, 406)],
            "color": "#0A438E", "label": (354, 430),
            "body": (272, 458, 126, "start"),
            "node": (445, 474), "line": (417, 462, 379, 449),
        },
    ]
    for block, item in zip(responsibility_blocks, c["triangle"]):
        svg.poly(block["points"], block["color"], WHITE, stroke_width=5)
        label_x, label_y = block["label"]
        body_x, body_y, body_w, body_anchor = block["body"]
        svg.text(label_x, label_y, item["label"], 18, WHITE, True,
                 anchor="middle", width=body_w, max_lines=1)
        _bounded_multiline(svg, body_x, body_y, item["text"], width=body_w,
                           size=15, color=WHITE, anchor=body_anchor, leading=19,
                           max_lines=3, role="diagram")
    svg.poly([(265, 346), (300, 430), (230, 430)],
             WHITE, WHITE, stroke_width=1)
    for block, item in zip(responsibility_blocks, c["triangle"]):
        x1, y1, x2, y2 = block["line"]
        node_x, node_y = block["node"]
        svg.line(x1, y1, x2, y2, SOFT_LINE, 2)
        svg.circle(node_x, node_y, 31, WHITE, LINE, stroke_width=1.5)
        svg.icon(item["icon"], node_x - 18, node_y - 18, 36, BLUE)
    headings = [(c["groups"][0], 112), (c["groups"][1], 365)]
    colors = [BLUE, TEAL, PURPLE]
    for group, y in headings:
        svg.rect(515, y, 730, 225, WHITE, SOFT_LINE, 4)
        _section(svg, y + 23, group["label"], 515, 730, label_width=210)
        for i, item in enumerate(group["items"]):
            x = 522 + i * 242
            svg.rect(x, y + 48, 222, 160, WHITE, LINE, 4)
            svg.icon(item["icon"], x + 18, y + 65, 34, WHITE, True, colors[i])
            svg.text(x + 69, y + 82, item["label"], 16, colors[i], True, width=140)
            _bounded_multiline(svg, x + 22, y + 122, item["text"], width=178,
                               size=15, color=INK, anchor="start", leading=19,
                               max_lines=3, role="body")
            svg.rect(x, y + 204, 222, 4, colors[i], "none", 0)
    band_x, band_y, band_w, band_h = 34, 627, 1214, 68
    segment_w = band_w / 3
    for i, item in enumerate(c["principles"]):
        x = band_x + i * segment_w
        svg.rect(x, band_y, segment_w, band_h, WHITE, "none", 0)
        if i:
            svg.line(x, band_y + 10, x, band_y + band_h - 10, SOFT_LINE, 1)
        _icon_backplate(svg, item["icon"], x + 18, 638, 34, accent=colors[i])
        svg.text(x + 67, 654, item["label"], 15, colors[i], True)
        svg.text(x + 67, 682, item["text"], 15, INK, width=segment_w - 82, max_lines=1)
    svg.rect(band_x, band_y, band_w, band_h, "none", SOFT_LINE, 3)
    return svg.finish()


def render_r03(content: dict[str, Any] | None = None):
    c = _content("R03", content)
    svg = Svg()
    _rd_title(svg, c["title"], c["subtitle"], 40, line="short_blue", line_y=127)
    svg.arrow(76, 170, 1215, 170, BLUE, 2)
    card_w = 378
    for i, stage in enumerate(c["stages"]):
        x = 40 + i * 406
        svg.number(x + card_w / 2 - 24, 170, f"0{i + 1}", 18)
        svg.icon(stage["milestone_icon"], x + card_w / 2 + 8, 151, 38,
                 WHITE, True, [BLUE, MID, BLUE][i])
        svg.rect(x, 202, card_w, 424, WHITE, SOFT_LINE, 3)
        svg.header(x, 202, card_w, stage["label"], 38, [BLUE, MID, BLUE][i], 16)
        row_specs = [("target", "核心目标", stage["target"], 68),
                     ("list-checks", "重点动作", stage["actions"], 104),
                     ("chart-bar", "阶段产出", stage["outputs"], 118),
                     ("shield-alert", "避坑提示", stage["risk"], 96)]
        yy = 240
        for icon, label, text, rh in row_specs:
            svg.rect(x, yy, card_w, rh, WHITE if yy % 2 else PALE, LINE, 0)
            svg.icon(icon, x + 18, yy + 17, 30, WHITE, True, BLUE)
            svg.text(x + 61, yy + 36, label, 14, BLUE, True, role="process")
            svg.line(x + 142, yy + 8, x + 142, yy + rh - 8, SOFT_LINE, 1)
            if isinstance(text, list):
                for line_index, line in enumerate(text):
                    svg.text(x + 158, yy + 27 + line_index * 20, line, 12.5, INK,
                             width=188, role="process")
            else:
                svg.text(x + 158, yy + 28, text, 12.5, INK, width=188,
                         leading=17, role="process")
            if label == "阶段产出":
                svg.text(x + 348, yy + rh - 16, stage["focus"], 30, MID, True,
                         anchor="end", role="process", max_lines=1)
            yy += rh
    svg.rect(40, 649, 1200, 46, LIGHT, LINE, 3)
    svg.icon("lightbulb", 57, 656, 28, WHITE, True, BLUE)
    svg.text(98, 678, c["value_label"], 15, BLUE, True)
    for i, text in enumerate(c["value_steps"]):
        x = 190 + i * 350
        svg.text(x, 678, text, 15, INK, width=280)
        if i < 2:
            svg.arrow(x + 280, 670, x + 325, 670, MID, 3)
    return svg.finish()


def render_r04(content: dict[str, Any] | None = None):
    c = _content("R04", content)
    svg = Svg()
    _rd_title(svg, c["title"], line="short_blue", line_y=88)
    svg.rect(62, 141, 1156, 78, LIGHT, "none", 0)
    svg.icon("file-chart-column", 84, 160, 34, WHITE, True, BLUE)
    svg.text(134, 185, c["background_label"], 17, BLUE, True)
    for i, item in enumerate(c["background"]):
        x = 300 + i * 298
        if i:
            svg.line(x - 20, 140, x - 20, 190, LINE, 1)
        svg.text(x, 181, "•  " + item, 15, INK, width=255, leading=19)
    _section(svg, 247, c["actions_heading"], 60, 1160)
    for i, item in enumerate(c["actions"]):
        x = 62 + i * 294
        svg.rect(x, 273, 258, 148, WHITE, SOFT_LINE, 2)
        svg.rect(x, 273, 38, 38, BLUE, "none", 0)
        svg.text(x + 19, 298, f"0{i + 1}", 15, WHITE, True, anchor="middle")
        _icon_backplate(svg, item["icon"], x + 18, 322, 56, style="square")
        svg.text(x + 102, 313, item["label"], 16, BLUE, True, width=136)
        svg.text(x + 102, 340, item["input"], 12.5, GREY, width=142,
                 max_lines=1, role="process")
        svg.text(x + 102, 365, item["action"], 12.5, INK, True, width=142,
                 max_lines=1, role="process")
        svg.text(x + 102, 390, item["output"], 12.5, BLUE, width=142,
                 max_lines=1, role="process")
        if i < 3:
            svg.circle(x + 272, 347, 13, MID)
            svg.text(x + 272, 352, ">", 15, WHITE, True, anchor="middle")
    _section(svg, 450, c["results_heading"], 60, 1160)
    for i, item in enumerate(c["results"]):
        _metric_card(svg, 62 + i * 235, 473, 218, 153, item)
    svg.rect(24, 635, 1232, 61, BLUE, "none", 4)
    _icon_backplate(svg, "target", 40, 643, 45, accent=MID)
    svg.text(102, 673, c["experience"], 18, WHITE, True, width=1125, max_lines=1)
    return svg.finish()


def render_r05(content: dict[str, Any] | None = None):
    c = _content("R05", content)
    svg = Svg()
    _rd_title(svg, c["title"], line="short_blue", line_y=88)
    for i, item in enumerate(c["issues"]):
        col, row = i % 2, i // 2
        x, y = 48 + col * 604, 129 + row * 282
        svg.rect(x, y, 580, 268, WHITE, SOFT_LINE, 3)
        svg.rect(x, y, 58, 56, BLUE, "none", 2)
        svg.text(x + 29, y + 37, f"0{i + 1}", 20, WHITE, True, anchor="middle")
        svg.text(x + 78, y + 36, item["label"], 18, BLUE, True, width=360)
        _diagnosis_rows(svg, x + 8, y + 58, 414, item["rows"], 64)
        svg.line(x + 442, y + 73, x + 442, y + 248, LINE, 1, True)
        _icon_backplate(svg, item["icon"], x + 474, y + 84, 56, style="halo")
        svg.text(x + 502, y + 161, "Insight", 15, INK, anchor="middle")
        svg.text(x + 502, y + 199, item["insight"], 15, BLUE, True,
                 anchor="middle", width=125, leading=18)
    return svg.finish()


def render_r06(content: dict[str, Any] | None = None):
    c = _content("R06", content)
    svg = Svg()
    _rd_title(svg, c["title"])
    for i, group in enumerate(c["metric_groups"]):
        x = 48 + i * 404
        svg.rect(x, 126, 382, 294, WHITE, LINE, 0)
        svg.poly([(x, 126), (x + 55, 126), (x + 47, 168), (x, 168)], BLUE)
        svg.text(x + 24, 155, f"0{i + 1}", 17, WHITE, True, anchor="middle")
        svg.text(x + 82, 154, group["label"], 18, BLUE, True)
        for j, item in enumerate(group["items"]):
            yy = 177 + j * 80
            if j:
                svg.line(x + 18, yy - 12, x + 364, yy - 12, LINE, 1)
            _icon_backplate(svg, item["icon"], x + 15, yy - 2, 40, style="halo")
            svg.line(x + 64, yy - 4, x + 64, yy + 55, SOFT_LINE, 1)
            svg.text(x + 78, yy + 16, item["label"], 14, INK, True,
                     width=202, role="diagram")
            definition_width = 270 if not item.get("value") else 220
            svg.text(x + 78, yy + 41, item["text"], 12.5, INK,
                     width=definition_width, leading=15, max_lines=2, role="diagram")
            if item.get("value"):
                svg.text(x + 337, yy + 22, item["value"], 16, MID, True,
                         anchor="end", role="diagram")
    _section(svg, 455, c["results_heading"], 50, 1180)
    for i, item in enumerate(c["results"]):
        x = 48 + i * 404
        svg.rect(x, 480, 382, 198, WHITE, LINE, 4)
        _icon_backplate(svg, item["icon"], x + 20, 503, 76)
        svg.text(x + 118, 516, item["label"], 15, INK, True, width=235)
        _result_value(svg, x + 118, 554, item["primary"], width=235, size=30)
        svg.text(x + 118, 584, item["secondary_label"], 12, GREY, width=235,
                 role="diagram")
        _result_value(svg, x + 118, 613, item["secondary"], width=235, size=24)
        svg.text(x + 118, 638, item["sample"], 11.5, INK, width=235,
                 role="source-note")
        svg.line(x + 22, 646, x + 360, 646, LINE, 1)
        svg.text(x + 191, 669, item["insight"], 15, BLUE, True, anchor="middle")
    return svg.finish()


def render_r07(content: dict[str, Any] | None = None):
    c = _content("R07", content)
    svg = Svg()
    _rd_title(svg, c["title"], line="short_blue", line_y=88)
    for gi, group in enumerate(c["metric_groups"]):
        x = 50 + gi * 615
        svg.header(x, 108, 580, group["label"], 42, BLUE, 17)
        for j, item in enumerate(group["items"]):
            yy = 160 + j * 84
            svg.rect(x, yy, 580, 72, WHITE, LINE, 3)
            svg.icon(item["icon"], x + 18, yy + 17, 30, BLUE)
            svg.text(x + 65, yy + 25, item["label"], 14, INK, True, width=180, role="diagram")
            svg.text(x + 65, yy + 51, item["definition"], 12, GREY, width=210, role="diagram")
            svg.text(x + 302, yy + 27, item["value"], 19, MID, True, anchor="middle", width=120, role="diagram")
            svg.text(x + 302, yy + 53, item["reference"], 12, INK, anchor="middle", width=120, role="diagram")
            svg.rect(x + 430, yy, 150, 72, LIGHT, LINE, 2)
            svg.text(x + 445, yy + 27, "洞察", 12, BLUE, True, role="diagram")
            svg.text(x + 445, yy + 52, item["insight"], 12, INK, width=120, role="diagram")
    svg.rect(50, 425, 1195, 255, WHITE, LINE, 5)
    svg.text(72, 458, c["case_heading"], 18, BLUE, True)
    for i, item in enumerate(c["case_steps"]):
        x = 68 + i * 293
        svg.header(x, 477, 254, item["label"], 36, BLUE, 15)
        svg.number(x + 23, 495, str(i + 1), 13)
        if item.get("chart"):
            svg.chart(f"r07-case-{i+1}", x + 10, 522, 140, 112,
                      item["chart"]["labels"], item["chart"]["series"],
                      item["chart"].get("kind", "bar"), item["chart"].get("format", "0"))
            svg.text(x + 160, 552, item["text"], 12, INK, width=80,
                     leading=17, role="process")
            _focus_value(svg, x + 143, 620, item.get("value", ""),
                         width=110, size=28, role="process")
        else:
            for line_index, text in enumerate(item["items"][:3]):
                svg.number(x + 30, 548 + line_index * 38, str(line_index + 1), 10)
                svg.text(x + 50, 552 + line_index * 38, text, 12, INK,
                         width=190, role="process")
        if i < 3:
            svg.poly([(x + 262, 540), (x + 278, 570), (x + 262, 600)], MID)
    return svg.finish()


def render_r08(content: dict[str, Any] | None = None):
    c = _content("R08", content)
    svg = Svg()
    _rd_title(svg, c["title"])
    _section(svg, 120, c["methods_heading"], 35, 1210)
    for i, item in enumerate(c["methods"]):
        x = 36 + i * 307
        svg.rect(x, 134, 290, 150, WHITE, LINE, 3)
        svg.rect(x, 134, 35, 35, BLUE, "none", 0)
        svg.text(x + 17, 158, f"0{i+1}", 14, WHITE, True, anchor="middle", role="diagram")
        _icon_backplate(svg, item["icon"], x + 22, 170, 58, style="square")
        svg.text(x + 103, 170, item["label"], 17, INK, True, width=165)
        svg.text(x + 103, 202, item["text"], 15, INK, width=165, leading=19, max_lines=2)
        svg.text(x + 103, 260, item["boundary"], 11, GREY, width=165, role="source-note")
    _section(svg, 316, c["metrics_heading"], 35, 1210)
    for i, item in enumerate(c["metrics"]):
        x = 36 + i * 410
        svg.rect(x, 334, 390, 128, WHITE, LINE, 3)
        _icon_backplate(svg, item["icon"], x + 17, 351, 58, style="halo")
        svg.text(x + 95, 365, item["label"], 16, INK, True)
        _result_value(svg, x + 95, 404, item["value"], width=145, size=25)
        svg.text(x + 246, 397, item["definition"], 15, INK, width=126, max_lines=2)
        svg.text(x + 95, 446, "洞察：" + item["insight"], 15, BLUE, True, width=280)
    _section(svg, 490, c["case_heading"], 35, 1210)
    svg.rect(36, 509, 1210, 171, WHITE, LINE, 3)
    for i, label in enumerate(c["case"]["labels"]):
        yy = 509 + i * 42
        svg.rect(36, yy, 99, 42, BLUE, "none", 0)
        svg.text(85, yy + 27, label, 13, WHITE, True, anchor="middle", role="diagram")
    _icon_backplate(svg, c["case"]["icon"], 151, 528, 66, style="halo")
    svg.text(238, 548, c["case"]["description"], 15, INK, width=208, leading=19, max_lines=2)
    for i, item in enumerate(c["case"]["metrics"]):
        x = 485 + i * 185
        svg.line(x - 18, 526, x - 18, 624, LINE, 1)
        svg.text(x, 552, item["label"], 12, INK, width=165, role="diagram")
        svg.text(x, 602, item["value"], 25, BLUE, True, width=165, role="diagram")
    svg.text(166, 665, c["case"]["insight"] + "｜限制：" + c["case"]["status"], 15, BLUE, True, width=1030)
    return svg.finish()


def render_r09(content: dict[str, Any] | None = None):
    c = _content("R09", content)
    svg = Svg()
    _rd_title(svg, c["title"])
    _bar_section_heading(svg, 42, 121, 1152, c["architecture_heading"])
    store = c["store"]
    svg.rect(44, 190, 228, 257, WHITE, BLUE, 6)
    svg.rect(44, 190, 228, 73, BLUE, MID, 4, stroke_width=2)
    svg.icon(store["icon"], 60, 208, 38, WHITE)
    svg.text(112, 223, store["label"], 15, WHITE, True, width=140, leading=19)
    for j, value in enumerate(store["items"]):
        svg.text(63, 292 + j * 34, "• " + value, 13, INK, width=190, role="diagram")
    for i, platform in enumerate(c["platforms"]):
        x = 360 + i * 291
        svg.rect(x, 190, 252, 257, WHITE, LINE, 6)
        svg.rect(x + 12, 203, 228, 58, BLUE, MID, 3, stroke_width=2)
        svg.icon(platform["icon"], x + 26, 217, 30, WHITE)
        svg.text(x + 76, 237, platform["label"], 15, WHITE, True, width=150)
        for j, value in enumerate(platform["items"]):
            svg.text(x + 28, 291 + j * 34, "• " + value, 12, INK,
                     width=200, role="diagram")
    for left, right in [(272, 350), (612, 650), (903, 949)]:
        svg.circle((left + right) / 2, 319, 18, LIGHT)
        svg.arrow(left + 8, 319, right - 8, 319, MID, 4, both=True)
    svg.rect(360, 458, 834, 39, LIGHT, "none", 0)
    for i, value in enumerate(c["capabilities"]):
        svg.text(485 + i * 190, 483, value, 13.5, BLUE, True,
                 anchor="middle", role="diagram")
        if i < 3:
            svg.line(572 + i * 190, 466, 572 + i * 190, 490, BLUE, 1)
    _bar_section_heading(svg, 42, 519, 1152, c["cases_heading"])
    for i, item in enumerate(c["cases"]):
        x = 44 + i * 405
        svg.rect(x, 535, 380, 170, WHITE, LINE, 5)
        _icon_backplate(svg, item["icon"], x + 20, 553, 56)
        svg.text(x + 96, 564, item["label"], 15, INK, True, width=170)
        _result_value(svg, x + 208, 592, item["value"], width=150, size=28)
        svg.line(x + 20, 620, x + 360, 620, LINE, 1)
        svg.text(x + 22, 648, "洞察：" + item["insight"], 15, BLUE, True, width=330)
        svg.text(x + 22, 680, item["detail"], 15, INK, width=330, max_lines=2)
    return svg.finish()


def render_r10(content: dict[str, Any] | None = None):
    c = _content("R10", content)
    svg = Svg()
    _rd_title(svg, c["title"], line="short_blue", line_y=82)
    groups = [(c["chart_groups"][0], 24), (c["chart_groups"][1], 650)]
    for group, gx in groups:
        svg.header(gx + 195, 90, 218, group["label"], 40, BLUE, 17)
        svg.line(gx, 110, gx + 180, 110, BLUE, 1)
        svg.line(gx + 430, 110, gx + 606, 110, BLUE, 1)
        for i, item in enumerate(group["items"]):
            categories = [*item["labels"]]
            if item.get("target_category"):
                categories.append(item["target_category"])
            for category in categories:
                if "\n" in str(category) or _text_advance(category, 1) > 3:
                    raise ValueError(f"R10 micro chart category exceeds fixed capacity "
                                     f"of 3 display units: {category!r}")
            x = gx + i * 203
            svg.rect(x, 143, 190, 326, WHITE, LINE, 4)
            svg.number(x + 24, 171, f"0{i+1}", 14)
            svg.text(x + 54, 174, item["label"], 13.5, INK, True,
                     width=122, role="chart")
            _metric_summary(svg, x + 16, 208, item["summary"], width=162)
            svg.chart(f"r10-chart-{group['id']}-{i+1}", x + 12, 253, 166, 153,
                      item["labels"], [{"name": item["label"], "values": item["values"]}],
                      item.get("kind", "line"), item.get("format", "0"),
                      {"legend": False, "target": item.get("target"),
                       "target_category": item.get("target_category"),
                       "reference_line": bool(item.get("reference_line")),
                       "data_label_layout": "staggered", "data_label_wrap": False})
            svg.rect(x + 8, 419, 174, 40, LIGHT, "none", 0)
            svg.icon("lightbulb", x + 13, 428, 18, BLUE)
            svg.text(x + 38, 443, item["insight"], 12, BLUE, True,
                     width=136, role="chart")
    _section(svg, 520, c["diagnosis_heading"], 22, 1235)
    colors = ["#E3EDF9", "#D3E3F5", "#BFD5EF", "#9DBDE4", "#6E9ED7"]
    for i, item in enumerate(c["diagnosis"]):
        x = 26 + i * 196
        top_w = 178 - i * 16
        svg.ribbon(x, 541, 170, 31, item["label"], i + 1, BLUE, 15)
        left_top = x + (180 - top_w) / 2
        right_top = x + 180 - (180 - top_w) / 2
        bottom_w = max(36, top_w - 80)
        left_bottom = x + (180 - bottom_w) / 2
        right_bottom = x + (180 + bottom_w) / 2
        left_split = left_top + (left_bottom - left_top) * 0.48
        right_split = right_top + (right_bottom - right_top) * 0.48
        svg.poly([(left_top, 577), (right_top, 577),
                  (right_split, 638), (left_split, 638)], colors[i], LINE)
        svg.poly([(left_split, 639), (right_split, 639),
                  (right_bottom, 704), (left_bottom, 704)], colors[i], "none")
        svg.icon(item["icon"], x + 70, 588, 40, BLUE)
        _bounded_multiline(svg, x + 90, 650, item["text"], width=150,
                           size=12, color=INK, anchor="middle", leading=16,
                           max_lines=2, role="diagram")
        if i < 4:
            svg.poly([(x + 174, 604), (x + 190, 618), (x + 174, 632),
                      (x + 179, 618)], BLUE)
    svg.rect(1025, 541, 230, 98, WHITE, LINE, 4)
    svg.rect(1025, 640, 230, 64, WHITE, LINE, 4)
    svg.header(1025, 541, 230, c["closure"]["label"], 36, BLUE, 15)
    svg.icon("circle-check-big", 1048, 582, 38, WHITE, True, BLUE)
    for line_index, line in enumerate(c["closure"]["actions"]):
        svg.text(1108, 590 + line_index * 18, "• " + line, 12, INK,
                 width=124, role="diagram")
    svg.rect(1038, 665, 204, 32, LIGHT, "none", 0)
    svg.text(1048, 686, c["closure"]["review"], 11, BLUE, True,
             width=180, role="source-note")
    return svg.finish()


def render_r11(content: dict[str, Any] | None = None):
    c = _content("R11", content)
    svg = Svg()
    _rd_title(svg, c["title"], size=38, line="short_blue", line_y=88)
    _section(svg, 122, c["functions_heading"], 42, 755)
    for i, item in enumerate(c["functions"]):
        x = 40 + i * 192
        svg.rect(x, 142, 180, 144, WHITE, LINE, 4)
        _icon_backplate(svg, item["icon"], x + 12, 153, 50, style="halo", accent=MID)
        svg.text(x + 69, 176, item["label"], 15, BLUE, True, width=100)
        for j, value in enumerate(item["items"]):
            svg.text(x + 66, 207 + j * 22, "• " + value, 12, INK,
                     width=108, role="diagram")
    _section(svg, 320, c["comparison_heading"], 42, 755)
    panels = [(c["comparison"][0], 42, GREY), (c["comparison"][1], 430, MID)]
    for panel, x, color in panels:
        svg.rect(x, 340, 330, 274, WHITE, color, 5)
        svg.header(x + 58, 340, 214, panel["label"], 34, color, 15)
        for i, row in enumerate(panel["rows"]):
            yy = 389 + i * 68
            svg.icon(row["icon"], x + 18, yy, 34, WHITE, True, color)
            svg.text(x + 68, yy + 15, row["label"], 13.5, color, True, role="diagram")
            for line_index, line in enumerate(row["items"]):
                svg.text(x + 68, yy + 35 + line_index * 18, line, 12, INK,
                         width=238, role="diagram")
    svg.poly([(384, 458), (420, 490), (384, 522)], MID)
    svg.rect(830, 198, 410, 450, WHITE, LINE, 5)
    svg.header(830, 198, 410, c["case"]["label"], 44, BLUE, 17)
    for i, item in enumerate(c["case"]["metrics"]):
        yy = 262 + i * 118
        svg.rect(842, yy, 386, 108, WHITE, "none", 0)
        svg.icon(item["icon"], 855, yy + 20, 46, BLUE)
        svg.text(925, yy + 22, item["label"], 15, INK, True)
        svg.text(925, yy + 72, item["value"], max(29, item.get("value_size", 29)), BLUE, True, width=155)
        svg.line(1090, yy + 13, 1090, yy + 94, LINE, 1)
        svg.icon(item.get("insight_icon", "target"), 1110, yy + 26, 28, BLUE)
        svg.text(1146, yy + 35, "洞察", 12.5, BLUE, True, role="diagram")
        svg.text(1146, yy + 63, item["insight"], 12, INK, width=70,
                 leading=16, role="diagram")
    svg.rect(42, 635, 755, 55, LIGHT, "none", 4)
    for i, item in enumerate(c["bottom_metrics"]):
        x = 65 + i * 362
        svg.icon(item["icon"], x, 647, 30, BLUE)
        svg.text(x + 42, 665, item["label"], 12.5, INK, True, role="diagram")
        svg.text(x + 174, 672, item["value"], 28, BLUE, True)
    return svg.finish()


def render_r12(content: dict[str, Any] | None = None):
    c = _content("R12", content)
    svg = Svg()
    _rd_title(svg, c["title"], size=38, line="full_hairline", line_y=82)
    svg.rect(38, 89, 1192, 175, WHITE, LINE, 3)
    svg.header(38, 89, 245, c["architecture_heading"], 38, BLUE, 17)
    levels = c["levels"]
    widths = [245, 365, 485]
    ys = [94, 145, 196]
    colors = ["#8FB1DE", "#3C74C6", BLUE]
    for i, level in enumerate(levels):
        w = widths[i]
        x = 259 + (485 - w) / 2
        y = ys[i]
        color_w = min(180, w * 0.52)
        svg.poly([(x + 30, y), (x + color_w, y), (x + color_w + 22, y + 44),
                  (x, y + 44)], colors[i])
        svg.icon(level["icon"], x + 45, y + 7, 30, WHITE)
        name_x = x + color_w - 10
        svg.poly([(name_x, y), (x + w - 24, y), (x + w, y + 22),
                  (x + w - 24, y + 44), (name_x + 22, y + 44)], PALE, LINE)
        svg.text((name_x + x + w) / 2, y + 29, level["label"], 16, BLUE, True,
                 anchor="middle", role="diagram")
        svg.line(x + w + 12, y + 22, 790, y + 22, GREY, 1, True)
        svg.circle(797, y + 22, 4, BLUE)
        svg.text(820, y + 28, level["explanation"], 13, INK, width=370, role="diagram")
    svg.header(35, 289, 575, c["root_heading"], 39, BLUE, 16)
    svg.header(635, 289, 610, c["actions_heading"], 39, BLUE, 16)
    svg.table("r12-root-table", 95, 328, 515, 163,
              ["层级", "观察证据"],
              [[item["label"], item["text"]] for item in c["roots"]],
              [0.25, 0.75], 12, row_heights=[1, 1, 1], show_header=False)
    for i, item in enumerate(c["roots"]):
        yy = 328 + i * 54.3
        svg.rect(35, yy, 60, 54.3, WHITE, LINE, 0)
        svg.icon(item["icon"], 51, yy + 13, 28, BLUE)
    for i, item in enumerate(c["actions"]):
        yy = 335 + i * 54
        svg.rect(650, yy, 42, 38, BLUE, "none", 2)
        svg.text(671, yy + 26, f"0{i+1}", 15, WHITE, True, anchor="middle")
        svg.poly([(699, yy), (719, yy + 19), (699, yy + 38)], PALE)
        svg.text(734, yy + 24, item, 15, INK, width=480)
    svg.rect(34, 503, 50, 186, BLUE, "none", 3)
    svg.text(59, 558, c["data_heading"], 17, WHITE, True, anchor="middle", width=26, leading=22)
    for i, item in enumerate(c["data"]):
        x = 95 + i * 385
        svg.rect(x, 503, 368, 186, WHITE, LINE, 4)
        svg.icon(item["icon"], x + 22, 534, 52, BLUE)
        svg.text(x + 100, 542, item["label"], 15, INK, True, width=235)
        _result_value(svg, x + 100, 598, item["value"], width=235, size=32)
        svg.line(x + 20, 636, x + 348, 636, LINE, 1)
        svg.text(x + 100, 670, "洞察：" + item["insight"], 15, BLUE, True, width=235)
    return svg.finish()


def render_r13(content: dict[str, Any] | None = None):
    c = _content("R13", content)
    svg = Svg()
    _rd_title(svg, c["title"])
    svg.text(35, 111, c["flow_heading"], 18, BLUE, True)
    colors = ["#092D68", "#0D3D83", "#13509D", "#1D64B5", "#3A7CC8", "#72A0D8", "#A7C3E7"]
    for i, item in enumerate(c["flow"]):
        x = 36 + i * 170
        _flow_arrow(svg, x, 130, 190, 65, item["label"], i + 1,
                    colors[i], item["icon"], label_inside=False)
        svg.text(x + 90, 218, item["label"], 16, BLUE, True,
                 anchor="middle", width=150, role="process")
        svg.text(x + 90, 243, item["artifact"], 12.5, INK, True,
                 anchor="middle", width=150, role="process")
        svg.text(x + 90, 265, item["action"], 12, INK,
                 anchor="middle", width=150, role="process")
        svg.text(x + 90, 282, "Owner " + item["owner"], 12, GREY,
                 anchor="middle", role="process")
    svg.text(35, 318, c["logic_heading"], 18, BLUE, True)
    svg.rect(35, 332, 614, 132, WHITE, LINE, 3)
    svg.icon("git-merge", 55, 350, 48, WHITE, True, MID)
    svg.text(125, 366, c["parallel"]["label"], 17, BLUE, True)
    svg.text(125, 400, c["parallel"]["text"], 12.5, INK,
             width=210, role="diagram")
    # Gantt-like evidence: one serial lane and three staggered parallel lanes.
    for i, width in enumerate([46, 52, 42, 58, 45, 36, 42]):
        svg.rect(360 + i * 34, 350, width, 11, "#A5AAB2", "none", 0)
    for row in range(3):
        for col in range(3):
            svg.rect(360 + col * 56 + row * 20, 382 + row * 14, 46, 10, MID, "none", 0)
    svg.rect(520, 397, 114, 50, LIGHT, "none", 3)
    svg.text(577, 428, c["parallel"]["value"], 21, BLUE, True, anchor="middle", width=104)
    svg.rect(672, 332, 573, 132, WHITE, LINE, 3)
    svg.icon("shield-check", 694, 350, 48, WHITE, True, BLUE)
    svg.text(765, 366, c["cost_curve"]["label"], 17, BLUE, True)
    svg.text(765, 400, c["cost_curve"]["text"], 12.5, INK,
             width=205, role="diagram")
    svg.chart("r13-cost-curve", 972, 340, 245, 108,
              c["cost_curve"]["labels"],
              [{"name": "修改成本倍率", "values": c["cost_curve"]["values"]}],
              "line", "0x", {"legend": False})
    svg.text(35, 500, c["results_heading"], 18, BLUE, True)
    for i, item in enumerate(c["results"]):
        x = 35 + i * 290
        svg.rect(x, 512, 275, 176, WHITE, LINE, 3)
        svg.number(x + 30, 540, str(i + 1), 14)
        svg.text(x + 62, 542, item["label"], 15, BLUE, True)
        _result_value(svg, x + 22, 590, item["value"], width=230, size=32)
        svg.chart(f"r13-result-{i+1}", x + 50, 601, 175, 80,
                  item["labels"], [{"name": item["label"], "values": item["values"]}],
                  item.get("kind", "bar"), item.get("format", "0"),
                  {"legend": False})
    svg.header(922, 492, 323, c["insights_heading"], 34, BLUE, 15)
    for i, item in enumerate(c["insights"]):
        yy = 531 + i * 51
        svg.icon(item["icon"], 938, yy + 6, 26, WHITE, True, MID)
        svg.text(978, yy + 18, item["label"], 15, BLUE, True)
        svg.text(978, yy + 39, item["text"], 15, INK, width=242)
    return svg.finish()


def render_r14(content: dict[str, Any] | None = None):
    c = _content("R14", content)
    svg = Svg()
    _rd_title(svg, c["title"])
    svg.rect(42, 112, 1194, 270, WHITE, LINE, 5)
    svg.header(42, 112, 200, c["environment_heading"], 40, BLUE, 15)
    for i, item in enumerate(c["environment"]):
        yy = 169 + i * 64
        _icon_backplate(svg, item["icon"], 58, yy - 5, 44, style="halo")
        svg.text(115, yy + 17, item["label"], 15, INK, True)
        svg.line(250, yy - 3, 250, yy + 35, SOFT_LINE, 1)
        svg.text(274, yy + 17, item["value"], 15, INK, width=185)
        if i < 2:
            svg.line(58, yy + 47, 455, yy + 47, LINE, 1)
    svg.chart("r14-cycle-chart", 510, 176, 320, 174,
              c["chart"]["labels"], [{"name": c["chart"]["label"], "values": c["chart"]["values"]}],
              "bar", "0月", {"legend": False})
    svg.text(690, 155, c["chart"]["label"], 13.5, INK, True,
             anchor="middle", role="chart")
    svg.arrow(852, 196, 930, 264, BLUE, 5)
    svg.text(892, 301, c["chart"]["change"], 25, BLUE, True, anchor="middle")
    svg.header(1035, 132, 92, "洞察", 34, BLUE, 15)
    svg.icon("lightbulb", 1053, 187, 45, BLUE)
    svg.text(1081, 269, c["insight"], 18, BLUE, True, anchor="middle", width=230, leading=24)
    svg.header(42, 394, 256, c["bottlenecks_heading"], 39, BLUE, 15)
    for i, item in enumerate(c["bottlenecks"]):
        x = 42 + i * 299
        svg.rect(x, 433, 299, 190, WHITE, LINE, 0)
        _icon_backplate(svg, item["icon"], x + 18, 448, 60, style="halo")
        svg.text(x + 92, 468, item["label"], 17, INK, True, width=180)
        svg.text(x + 92, 505, item["text"], 15, INK, width=180,
                 leading=19, max_lines=2)
        svg.line(x + 24, 552, x + 275, 552, LINE, 1)
        svg.text(x + 150, 596, item["value"], 25, BLUE, True, anchor="middle", width=250)
    svg.rect(24, 623, 1232, 75, BLUE, "none", 4)
    _icon_backplate(svg, "target", 42, 631, 58, style="square", accent=MID)
    svg.text(126, 668, c["positioning"], 18, WHITE, True, width=1090, max_lines=1)
    return svg.finish()


def render_r15(content: dict[str, Any] | None = None):
    c = _content("R15", content)
    svg = Svg()
    _rd_title(svg, c["title"], c["subtitle"], 36)
    svg.rect(18, 136, 214, 424, WHITE, LINE, 4)
    svg.header(18, 136, 214, c["overview"]["label"], 40, BLUE, 16)
    for gi, group in enumerate(c["overview"]["groups"]):
        yy = 198 + gi * 168
        svg.icon(group["icon"], 36, yy, 28, BLUE)
        svg.text(78, yy + 17, group["label"], 15, BLUE, True)
        for j, value in enumerate(group["items"]):
            svg.text(40, yy + 52 + j * 24, "• " + value, 15, INK, width=168)
    # Roof, two wings, and four stacked operating layers reproduce the central house.
    svg.poly([(286, 196), (582, 125), (878, 196)], BLUE)
    svg.text(582, 169, c["roof"]["label"], 19, WHITE, True,
             anchor="middle", role="diagram")
    svg.text(582, 190, c["roof"]["text"], 12, WHITE,
             anchor="middle", role="diagram")
    svg.rect(308, 211, 550, 59, WHITE, LINE, 4)
    svg.text(419, 235, c["wings"][0]["label"], 16, BLUE, True,
             anchor="middle", role="diagram")
    svg.text(419, 256, c["wings"][0]["text"], 12, INK,
             anchor="middle", role="diagram")
    svg.icon("refresh-cw", 554, 219, 40, BLUE)
    svg.text(746, 235, c["wings"][1]["label"], 16, BLUE, True,
             anchor="middle", role="diagram")
    svg.text(746, 256, c["wings"][1]["text"], 12, INK,
             anchor="middle", role="diagram")
    svg.arrow(286, 293, 286, 522, BLUE, 2.5, both=True)
    svg.text(257, 346, c["vertical_left"], 12, BLUE, True,
             anchor="middle", width=24, leading=15, role="diagram")
    svg.arrow(878, 293, 878, 522, BLUE, 2.5, both=True)
    svg.text(907, 346, c["vertical_right"], 12, BLUE, True,
             anchor="middle", width=24, leading=15, role="diagram")
    for i, layer in enumerate(c["layers"]):
        yy = 284 + i * 62
        svg.rect(308, yy, 550, 53, WHITE, LINE, 3)
        svg.rect(294, yy + 10, 24, 33, BLUE, "none", 2)
        svg.text(306, yy + 33, str(i + 1), 13, WHITE, True,
                 anchor="middle", role="diagram")
        svg.icon(layer["icon"], 333, yy + 12, 28, BLUE)
        svg.text(374, yy + 29, layer["label"], 16, BLUE, True,
                 width=125, role="diagram")
        svg.text(508, yy + 24, layer["text"], 13, INK,
                 width=220, role="diagram")
        svg.text(736, yy + 14, "\n".join(layer["attributes"]), 12, INK,
                 width=106, leading=15, role="diagram")
    svg.rect(944, 136, 318, 424, WHITE, LINE, 4)
    svg.header(944, 136, 318, c["collaboration_heading"], 40, BLUE, 16)
    for i, item in enumerate(c["collaborations"]):
        yy = 190 + i * 174
        svg.rect(960, yy, 286, 157, WHITE, LINE, 3)
        svg.text(1103, yy + 27, item["label"], 15, BLUE, True, anchor="middle")
        svg.icon(item["left_icon"], 990, yy + 47, 34, BLUE)
        svg.icon(item["right_icon"], 1182, yy + 47, 34, BLUE)
        _loop_arrows(svg, 1041, yy + 56, 1165, BLUE)
        svg.text(1103, yy + 104, item["text"], 12, INK,
                 anchor="middle", width=240, role="diagram")
        svg.text(1103, yy + 139, item["flow"], 12, INK,
                 anchor="middle", width=250, role="diagram")
    svg.rect(18, 582, 916, 113, WHITE, LINE, 4)
    svg.rect(18, 582, 60, 113, BLUE, "none", 3)
    svg.text(48, 620, c["targets_heading"], 16, WHITE, True, anchor="middle", width=24, leading=21)
    for i, item in enumerate(c["targets"]):
        x = 95 + i * 166
        svg.icon(item["icon"], x, 602, 32, BLUE)
        svg.text(x + 42, 617, item["label"], 12, INK, True,
                 width=102, role="diagram")
        svg.text(x + 42, 652, item["value"], 24, BLUE, True,
                 width=102, role="diagram")
        svg.text(x + 42, 682, item["note"], 11, GREY,
                 width=102, role="source-note")
    svg.rect(950, 582, 312, 113, BLUE, "none", 4)
    svg.text(970, 610, c["core"]["label"], 15, WHITE, True)
    core_parts = c["core"]["text"].split("，")
    for line_index, line in enumerate(core_parts):
        suffix = "，" if line_index < len(core_parts) - 1 else ""
        svg.text(970, 640 + line_index * 20, line + suffix, 15, WHITE, width=270)
    return svg.finish()


DEFAULTS: dict[str, dict[str, Any]] = {
    "R01": {
        "title": "从效率提升到能力建设，构建可持续的效能增长引擎",
        "stage_heading": "一、三层价值总结：从短期见效到长期竞争力",
        "stages": [
            {"label": "短期价值（0—6月）", "items": [
                {"icon": "clock-3", "text": "减少评审等待，缩短交付周期"},
                {"icon": "database", "text": "统一研发数据，建立共同口径"},
                {"icon": "chart-bar", "text": "消除重复劳动，释放团队产能"}]},
            {"label": "中期价值（6—18月）", "items": [
                {"icon": "package", "text": "沉淀可复用模块与接口契约"},
                {"icon": "chart-no-axes-combined", "text": "提高单位投入产出与复用率"},
                {"icon": "shield-check", "text": "统一研发规范与质量门禁"}]},
            {"label": "长期价值（18月以上）", "items": [
                {"icon": "rocket", "text": "支撑多产品线持续演进"},
                {"icon": "network", "text": "形成跨业务可复制的能力底座"},
                {"icon": "gem", "text": "同样投入创造更多客户价值"}]},
        ],
        "trend_heading": "二、行业演进趋势：驱动研发效能持续跃迁",
        "trends": [
            {"icon": "brain-circuit", "label": "智能辅助设计", "text": "工程师审查生成方案\n把创造力投入关键判断"},
            {"icon": "users", "label": "用户参与验证", "text": "试用反馈进入需求版本\n用真实任务检验价值"},
            {"icon": "workflow", "label": "供应链前置协同", "text": "设计时校验工艺与供货\n前置暴露制造和供应风险"},
        ],
        "bottom_label": "三、终局认知",
        "bottom": [
            {"icon": "lightbulb", "label": "核心理念", "text": "把重复劳动转为可复用资产"},
            {"icon": "chart-no-axes-combined", "label": "实施路径", "text": "流程治理消除浪费，数据检验效果"},
            {"icon": "trophy", "label": "最终目标", "text": "同样投入形成更多可验证客户价值"},
        ],
    },
    "R02": {
        "title": "铁三角推进组织，激励机制与人才能力三位一体",
        "triangle_heading": "铁三角推进组织",
        "triangle": [
            {"icon": "briefcase-business", "label": "业务端", "text": "对客户结果负责\n验收价值与收益"},
            {"icon": "clipboard-pen-line", "label": "方法端", "text": "管理流程与门禁\n制定标准和复盘"},
            {"icon": "code-xml", "label": "技术端", "text": "维护工具与数据\n保障平台稳定"},
        ],
        "groups": [
            {"label": "配套激励机制", "items": [
                {"icon": "boxes", "label": "模块共享激励", "text": "按审核引用奖励\n复用记录可核验\n不按上传数量"},
                {"icon": "chart-no-axes-combined", "label": "效能提升激励", "text": "以质量为守门\n改善证据双签\n避免短期冲量"},
                {"icon": "shield-check", "label": "质量反向挂钩", "text": "依据证据追责\n阻断项先关闭\n不只看报表"}]},
            {"label": "人才能力建设", "items": [
                {"icon": "badge-check", "label": "流程能力认证", "text": "分层训练\n用工件实操\n以门禁验收"},
                {"icon": "monitor-cog", "label": "工具实操训练", "text": "掌握协同工具\n按流程留痕\n复盘真实任务"},
                {"icon": "users-round", "label": "跨职能项目轮岗", "text": "轮岗参与试点\n理解上下游\n形成共同语言"}]},
        ],
        "principles": [
            {"icon": "target", "label": "目标一致", "text": "围绕客户结果，指标同向"},
            {"icon": "link", "label": "资源协同", "text": "授权与约束配套，持续改进"},
            {"icon": "scan-search", "label": "行为可验", "text": "用工件和门禁核对承诺"},
        ],
    },
    "R03": {
        "title": "分阶段推进，循序渐进实现效能跃迁",
        "subtitle": "从基础规范到精益深化，再到经营度量；任一质量门失败即暂停扩围",
        "stages": [
            {"label": "第一阶段·基础规范期（0—6月）", "milestone_icon": "clipboard-list", "focus": "10模块",
             "target": "统一口径、梳理流程、首批10模块",
             "actions": ["梳理研发流程与门禁", "统一指标字典", "上线模块编码与检索"],
             "outputs": ["指标字典 / 风险清单", "退出：3部门会签", "10模块通过测试"],
             "risk": "口径争议；Owner：运营/架构"},
            {"label": "第二阶段·精益深化期（7—12月）", "milestone_icon": "chart-no-axes-combined", "focus": "连续3月",
             "target": "推广模块、打通测试、选择2条产品线",
             "actions": ["通用模块平台落地", "并行评审与测试", "数字工具链深度集成"],
             "outputs": ["复用包 / 接口日志", "连续3月数据可追溯", "严重质量事故为0"],
             "risk": "个性化越界；Owner：平台/质量"},
            {"label": "第三阶段·智能升级期（13—18月）", "milestone_icon": "brain-circuit", "focus": "10项责任",
             "target": "经营度量、治理优化、机制复盘",
             "actions": ["收益口径核对", "10项指标责任归属", "机制修订并留痕"],
             "outputs": ["收益核对表 / 机制修订", "财务确认口径", "转型委员会批准继续"],
             "risk": "目标不得提前写成实绩"},
        ],
        "value_label": "总体价值",
        "value_steps": ["统一规范，夯实数据与流程基础", "形成可复制的精益体系", "经营度量驱动长期演进"],
    },
    "R04": {
        "title": "周期12→9个月，一次验证通过率76%→89%",
        "background_label": "项目背景",
        "background": ["24个项目、4季度、3部门", "重复设计与评审滞后", "测试等待影响交付"],
        "actions_heading": "核心升级举措",
        "actions": [
            {"icon": "layers", "label": "标准模块库", "input": "统一模块分层与编码", "action": "冻结接口、评审入库", "output": "版本与责任全程可追溯"},
            {"icon": "workflow", "label": "并行评审", "input": "需求包与质量门禁", "action": "研发、质量同步评审", "output": "形成风险清单与结论"},
            {"icon": "monitor-check", "label": "自动测试", "input": "脚本、用例与数据集", "action": "按门禁自动执行", "output": "日志与结果自动归档"},
            {"icon": "gauge", "label": "异常周会", "input": "异常单与责任证据", "action": "周会对齐并限时闭环", "output": "复核签字与改进记录"},
        ],
        "results_heading": "量化成效（Q1→Q4，合成案例）",
        "results": [
            {"icon": "clock-3", "label": "平均研发周期", "value": "12.0→9.0月", "value_size": 20, "detail": "交付节奏改善"},
            {"icon": "shield-check", "label": "一次验证通过率", "value": "76%→89%", "detail": "质量门前置"},
            {"icon": "blocks", "label": "模块复用率", "value": "34%→62%", "detail": "复用资产增长"},
            {"icon": "coins", "label": "单项目研发成本", "value": "520→448万", "detail": "财务台账口径"},
            {"icon": "users", "label": "人均完成项目", "value": "1.6→2.0项", "detail": "投入全时当量"},
        ],
        "experience": "核心经验：动作与指标分别归账；同步改善不等于单项工具的因果贡献",
    },
    "R05": {
        "title": "识别共性卡点，破解组织与机制障碍",
        "issues": [
            {"label": "卡点一：需求反复", "icon": "target", "rows": [
                {"icon": "eye", "label": "表层现象", "items": ["6/20份缺验收条件", "4份需求未签收"]},
                {"icon": "search", "label": "深层根因", "items": ["待核实：任务未澄清", "待核实：Owner不清"]},
                {"icon": "lightbulb", "label": "应对方案", "items": ["产品组补验收条件", "质量组核可测性"]}], "insight": "先定验收\n再做方案"},
            {"label": "卡点二：评审拖延", "icon": "shield-check", "rows": [
                {"icon": "eye", "label": "表层现象", "items": ["20次平均等待4天", "6次关键人员不齐"]},
                {"icon": "search", "label": "深层根因", "items": ["待核实：窗口不固定", "待核实：资源冲突"]},
                {"icon": "lightbulb", "label": "应对方案", "items": ["PMO固定评审窗口", "设置关键人替补"]}], "insight": "资源窗口\n可见"},
            {"label": "卡点三：复用受阻", "icon": "chart-no-axes-combined", "rows": [
                {"icon": "eye", "label": "表层现象", "items": ["15/40模块缺接口", "8个无测试记录"]},
                {"icon": "search", "label": "深层根因", "items": ["待核实：契约不足", "待核实：发布门缺项"]},
                {"icon": "lightbulb", "label": "应对方案", "items": ["架构组补接口", "质量组补验证"]}], "insight": "复用依赖\n契约"},
            {"label": "卡点四：数据矛盾", "icon": "network", "rows": [
                {"icon": "eye", "label": "表层现象", "items": ["3部门使用3种口径", "2份报表单位不同"]},
                {"icon": "search", "label": "深层根因", "items": ["待核实：字典缺失", "待核实：来源未绑定"]},
                {"icon": "lightbulb", "label": "应对方案", "items": ["运营统一字典", "财务核对单位"]}], "insight": "口径先于\n看板"},
        ],
    },
    "R06": {
        "title": "局部工具作业提速：5→2天，18→7小时",
        "metric_groups": [
            {"label": "效率指标", "items": [
                {"icon": "calendar-clock", "label": "周期达成率", "value": "94%", "text": "实际周期 ÷ 计划周期\n衡量计划偏差"},
                {"icon": "calendar-check", "label": "按期交付率", "value": "", "text": "按期项目 ÷ 到期项目\n衡量交付稳定性"},
                {"icon": "timer", "label": "等待工时占比", "value": "", "text": "等待工时 ÷ 总工时\n识别流程停滞"}]},
            {"label": "质量指标", "items": [
                {"icon": "badge-check", "label": "首次通过率", "value": "", "text": "首次通过项 ÷ 首次测试项\n衡量一次做对"},
                {"icon": "bug", "label": "生产缺陷密度", "value": "", "text": "缺陷数 ÷ 检验件数\n衡量量产质量"},
                {"icon": "shield-check", "label": "关闭后复发", "value": "", "text": "复发异常 ÷ 已关闭异常\n衡量闭环有效性"}]},
            {"label": "投入指标", "items": [
                {"icon": "coins", "label": "单项目研发费用", "value": "", "text": "研发费用 ÷ 完成项目\n衡量项目投入"},
                {"icon": "users", "label": "人均完成项目", "value": "", "text": "完成项目 ÷ 研发FTE\n衡量人员产出"},
                {"icon": "database", "label": "有效模块引用", "value": "", "text": "有效引用 ÷ 可用模块\n衡量资产复用"}]},
        ],
        "results_heading": "数字化工具升级后的成效（局部作业，不外推总体收益）",
        "results": [
            {"icon": "messages-square", "label": "需求协同", "primary": "5天→2天", "secondary_label": "完整签收率", "secondary": "70%→95%", "sample": "同季度20次变更", "insight": "版本签收可追溯"},
            {"icon": "monitor-check", "label": "自动测试", "primary": "18小时→7小时", "secondary_label": "可重复脚本", "secondary": "24→40项", "sample": "同一组40脚本", "insight": "日志和结果同源"},
            {"icon": "search-check", "label": "版本定位", "primary": "90→25分钟", "secondary_label": "来源工件", "secondary": "6→10项", "sample": "10个异常单", "insight": "定位证据可复核"},
        ],
    },
    "R07": {
        "title": "延期26天暴露评审缺口，后续TARGET≤12天/项目",
        "metric_groups": [
            {"label": "1. 交付节奏指标体系", "items": [
                {"icon": "calendar-check", "label": "交付率", "definition": "按期项目 / 到期项目", "value": "Q4 83%", "reference": "目标90%", "insight": "核对到期项目"},
                {"icon": "gauge", "label": "周期达成率", "definition": "实际周期 / 计划周期", "value": "Q4 94%", "reference": "健康≤100%", "insight": "计划口径一致"},
                {"icon": "repeat-2", "label": "需求变更率", "definition": "签收后变更 / 总需求", "value": "Q4 11%", "reference": "阈值≤15%", "insight": "签收版本为准"}]},
            {"label": "2. 工作负荷指标体系", "items": [
                {"icon": "layers", "label": "在制项目数", "definition": "同时进行中的项目", "value": "8个", "reference": "当前快照", "insight": "控制并行负荷"},
                {"icon": "hourglass", "label": "评审等待", "definition": "提交至开始评审", "value": "3.5天", "reference": "当前快照", "insight": "缺固定窗口"},
                {"icon": "list-end", "label": "测试队列", "definition": "排队至开始执行", "value": "2.0天", "reference": "当前快照", "insight": "监测资源拥堵"}]},
        ],
        "case_heading": "3. 延期案例：B项目比承诺延期26天（合成案例）",
        "case_steps": [
            {"label": "现象", "text": "三个不重叠区间", "value": "延期26天", "value_size": 17, "chart": {"labels": ["返工", "器件", "规格"], "series": [{"name": "天数", "values": [9, 10, 7]}], "kind": "bar", "format": "0天"}},
            {"label": "待核实解释", "items": ["接口测试缺前置评审", "证书门可能缺失", "需求Owner入口不清"]},
            {"label": "优化动作", "items": ["质量/工艺进入立项评审", "试制前完成证书清单", "签收版本限定变更入口"]},
            {"label": "验证目标", "text": "后续6项目", "value": "≤12天/项", "value_size": 16, "chart": {"labels": ["当前", "TARGET"], "series": [{"name": "延期", "values": [26, 12]}], "kind": "bar", "format": "0天"}},
        ],
    },
    "R08": {
        "title": "连接件9→5种、单价18→15元，收益待财务确认",
        "methods_heading": "1. 面向成本的设计方法",
        "methods": [
            {"icon": "combine", "label": "零件归并", "text": "共用件统一编码", "boundary": "边界：性能保持一致"},
            {"icon": "factory", "label": "可制造性评审", "text": "生产前会签装配条件", "boundary": "边界：风险清单闭合"},
            {"icon": "boxes", "label": "模块复用", "text": "冻结复用版本与接口", "boundary": "边界：验证证据齐全"},
            {"icon": "hand-coins", "label": "采购协同", "text": "同规格合并询价", "boundary": "边界：供应风险已核"},
        ],
        "metrics_heading": "2. 成本效能度量指标",
        "metrics": [
            {"icon": "chart-bar", "label": "单机BOM成本", "value": "860→792元", "definition": "案例BOM", "insight": "只比较同一配置"},
            {"icon": "coins", "label": "单项目研发成本", "value": "520→448万", "definition": "财务台账", "insight": "研发直接经济贡献"},
            {"icon": "lightbulb", "label": "重复料号", "value": "480→310个", "definition": "主数据记录", "insight": "创新成本效率"},
        ],
        "case_heading": "3. 实践案例：A产品连接件归并（合成案例）",
        "case": {"labels": ["设计动作", "成本成效", "投入产出", "洞察"], "icon": "scan-line",
                 "description": "A产品连接件归并\n验证4项装配条件",
                 "metrics": [{"label": "连接件种类", "value": "9→5种"}, {"label": "采购单价", "value": "18→15元"},
                             {"label": "理论年差额", "value": "30万元"}, {"label": "年使用量", "value": "10万件"}],
                 "status": "尚待完整年度兑现", "insight": "财务核实付、质量核性能、采购核风险后再扩围"},
    },
    "R09": {
        "title": "一库三平台连接业务工件，协同效果用同样任务验证",
        "architecture_heading": "“一库三平台”双向互通架构",
        "store": {"icon": "database", "label": "研发主数据资源库", "items": ["物料 / 模块 / 知识 / 规则", "稳定ID与版本", "来源与责任人", "禁止文件名作唯一标识"]},
        "platforms": [
            {"icon": "monitor", "label": "协同设计平台", "items": ["版本签收", "接口契约", "设计工件追溯", "稳定ID回写"]},
            {"icon": "flask-conical", "label": "仿真测试平台", "items": ["用例调度", "结果采集", "验证日志归档", "失败证据回写"]},
            {"icon": "clipboard-check", "label": "项目管理平台", "items": ["计划与风险", "交付门禁", "任务状态同步", "工件引用回写"]},
        ],
        "capabilities": ["标准统一", "数据互通", "流程贯通", "协同高效"],
        "cases_heading": "试点价值（同样任务前后比较，合成样本）",
        "cases": [
            {"icon": "users", "label": "12次跨部门交接", "value": "6→3天", "insight": "接口统一", "detail": "稳定ID减少人工搬运与等待"},
            {"icon": "monitor-dot", "label": "20次数据查询", "value": "45→15分", "insight": "管理可追溯", "detail": "查询范围与任务保持一致"},
            {"icon": "graduation-cap", "label": "8名新人定位工件", "value": "100→65分", "insight": "知识可复用", "detail": "同题任务验证，不外推总体效率"},
        ],
    },
    "R10": {
        "title": "六项指标兼顾效率与质量，整改落到五层证据",
        "chart_groups": [
            {"id": "eff", "label": "效率类指标体系", "items": [
                {"label": "交付率", "summary": "当前83% → 目标90%", "labels": ["Q1", "Q2", "Q3", "Q4"], "values": [67, 67, 83, 83], "kind": "bar", "format": "0\"%\"", "target": 90, "target_category": "目标", "insight": "交付准时性提升"},
                {"label": "周期达成率", "summary": "实际周期 / 计划周期", "labels": ["Q1", "Q2", "Q3", "Q4"], "values": [118, 108, 99, 94], "kind": "line", "format": "0\"%\"", "target": 100, "reference_line": True, "insight": "计划偏差收窄"},
                {"label": "需求变更率", "summary": "健康阈值≤15%", "labels": ["Q1", "Q2", "Q3", "Q4"], "values": [19, 16, 13, 11], "kind": "line", "format": "0\"%\"", "target": 15, "reference_line": True, "insight": "签收条件更清晰"}]},
            {"id": "quality", "label": "质量类指标体系", "items": [
                {"label": "首次验证通过率", "summary": "首轮通过项 / 总验证项", "labels": ["Q1", "Q2", "Q3", "Q4"], "values": [76, 81, 86, 89], "kind": "bar", "format": "0\"%\"", "target": 90, "insight": "一次做对率提升"},
                {"label": "千行代码缺陷", "summary": "当前1.0 → 参考0.8", "labels": ["Q1", "Q2", "Q3", "Q4"], "values": [1.9, 1.6, 1.3, 1.0], "kind": "bar", "format": "0.0", "target": 0.8, "target_category": "参考值", "reference_line": True, "insight": "质量标杆看齐"},
                {"label": "量产初期不良", "summary": "前三个月制程不良", "labels": ["第1月", "第2月", "第3月"], "values": [2.4, 1.8, 1.2], "kind": "line", "format": "0.0\"%\"", "target": 1.0, "insight": "研发质量试金石"}]},
        ],
        "diagnosis_heading": "偏差根因拆解：接口验证失败的五层证据链",
        "diagnosis": [
            {"icon": "circle-alert", "label": "现象层", "text": "接口验证失败\n同版本重复整改"},
            {"icon": "settings", "label": "执行层", "text": "边界测试未覆盖\n权限工况未达标"},
            {"icon": "workflow", "label": "流程层", "text": "器件确认滞后\n开模后才发现"},
            {"icon": "users", "label": "机制层", "text": "质量/工艺未参评\n关键风险未会签"},
            {"icon": "target", "label": "根因层", "text": "跨部门门禁缺失\n责任批准不闭合"},
        ],
        "closure": {"label": "整改闭环", "actions": ["补齐评审参与人", "补齐器件证书清单", "补齐闭环签字"],
                    "review": "复核：下季度失败项与总延期"},
    },
    "R11": {
        "title": "异常关闭9.2→5.4天，设计变更等待5→2天",
        "functions_heading": "需求管理平台四大功能",
        "functions": [
            {"icon": "network", "label": "需求追踪", "items": ["输入：需求版本", "输出：签收记录", "全链路追溯"]},
            {"icon": "tags", "label": "计划协同", "items": ["输入：里程碑", "输出：责任计划", "跨组同步"]},
            {"icon": "chart-pie", "label": "风险预警", "items": ["输入：异常信号", "输出：责任工单", "24小时建单"]},
            {"icon": "route", "label": "质量门禁", "items": ["输入：验证证据", "输出：门禁结论", "失败重开"]},
        ],
        "comparison_heading": "传统模式与数字化闭环对照",
        "comparison": [
            {"label": "传统模式（线性传导）", "rows": [
                {"icon": "users", "label": "传导链路长", "items": ["需求口头传递", "计划个人维护"]},
                {"icon": "crosshair", "label": "优先级模糊", "items": ["异常月底总结", "价值难排序"]},
                {"icon": "circle-question-mark", "label": "没有后验证", "items": ["质量末端检验", "经验留在个人"]}]},
            {"label": "数字化闭环（平台驱动）", "rows": [
                {"icon": "zap", "label": "直连用户", "items": ["需求版本签收", "统一里程碑"]},
                {"icon": "clipboard-check", "label": "数据驱动", "items": ["异常24小时建单", "价值排序"]},
                {"icon": "chart-no-axes-combined", "label": "闭环验证", "items": ["分阶段验证", "审核后入库"]}]},
        ],
        "case": {"label": "实战案例：异常闭环（合成案例）", "metrics": [
            {"icon": "clock-3", "label": "异常平均关闭", "value": "9.2→5.4天", "value_size": 24, "insight": "18个异常"},
            {"icon": "chart-no-axes-combined", "label": "设计变更等待", "value": "5→2天", "value_size": 27, "insight": "范围独立"},
            {"icon": "database", "label": "按期交付", "value": "4/6→5/6", "insight": "6个项目"}]},
        "bottom_metrics": [
            {"icon": "target", "label": "异常周期", "value": "9.2→5.4天"},
            {"icon": "user-round", "label": "等待时长", "value": "5→2天"},
        ],
    },
    "R12": {
        "title": "模块复用34%→57%，准备耗时16→10天",
        "architecture_heading": "三级模块架构体系",
        "levels": [
            {"icon": "puzzle", "label": "业务能力", "explanation": "面向具体场景的差异化能力"},
            {"icon": "boxes", "label": "标准模块", "explanation": "跨项目复用的产品与接口模块"},
            {"icon": "database", "label": "公共基础", "explanation": "算法、工具链、规范和主数据"},
        ],
        "root_heading": "早期复用率低的根因拆解",
        "roots": [
            {"icon": "network", "label": "契约层", "text": "40模块中15个缺接口说明"},
            {"icon": "file-check", "label": "验证层", "text": "8个模块没有测试记录"},
            {"icon": "git-compare-arrows", "label": "版本层", "text": "6个模块发生版本冲突；类别可重叠"},
        ],
        "actions_heading": "落地举措",
        "actions": ["补齐接口契约并明确责任人", "质量组抽样确认10项测试证据", "冻结发布版本；失败项不得发布"],
        "data_heading": "实战数据",
        "data": [
            {"icon": "refresh-cw", "label": "12项目模块复用率", "value": "34%→57%", "insight": "同试点观察"},
            {"icon": "chart-no-axes-combined", "label": "准备耗时", "value": "16→10天", "insight": "不推断完整因果"},
            {"icon": "bug", "label": "首轮集成缺陷", "value": "22→14个", "insight": "样本边界明确"},
        ],
    },
    "R13": {
        "title": "并行方案15→10周，等待TARGET 4→2天",
        "flow_heading": "七阶段流程设计",
        "flow": [
            {"label": "需求", "icon": "users", "artifact": "验收条件", "action": "澄清客户任务", "owner": "产品"},
            {"label": "概念", "icon": "lightbulb", "artifact": "方案记录", "action": "评估可行性", "owner": "方案"},
            {"label": "设计", "icon": "clipboard-check", "artifact": "冻结图纸", "action": "锁定接口", "owner": "架构"},
            {"label": "试制", "icon": "settings", "artifact": "样机", "action": "并行试制", "owner": "制造"},
            {"label": "验证", "icon": "scan-search", "artifact": "测试报告", "action": "关闭问题", "owner": "质量"},
            {"label": "发布", "icon": "factory", "artifact": "发布清单", "action": "签收门禁", "owner": "项目"},
            {"label": "复盘", "icon": "refresh-cw", "artifact": "资产条目", "action": "沉淀复用", "owner": "平台"}],
        "logic_heading": "流程效能提升逻辑",
        "parallel": {"label": "并行工程压缩等待", "text": "串行A/B/C共15周；接口评审后并行总10周（方案示意）", "value": "15→10周"},
        "cost_curve": {"label": "门禁前置降低修改成本", "text": "阶段越晚，说明用修改成本倍率越高", "labels": ["需求", "概念", "设计", "试制", "验证", "发布", "复盘"], "values": [1, 2, 4, 8, 16, 32, 64]},
        "results_heading": "目标成效（TARGET，尚未发生）",
        "results": [
            {"label": "等待时间", "value": "4→2天", "labels": ["当前", "目标"], "values": [4, 2], "kind": "bar", "format": "0天"},
            {"label": "模块复用率", "value": "34%→55%", "labels": ["当前", "目标"], "values": [34, 55], "kind": "bar", "format": "0"},
            {"label": "首次通过率", "value": "76%→85%", "labels": ["当前", "目标"], "values": [76, 85], "kind": "line", "format": "0"}],
        "insights_heading": "关键洞察",
        "insights": [
            {"icon": "target", "label": "前置条件决定并行", "text": "接口评审后才可重叠"},
            {"icon": "gauge", "label": "晚变更放大返工", "text": "倍率仅为方案假设"},
            {"icon": "chart-no-axes-combined", "label": "目标需证据复核", "text": "TARGET不得写成实绩"}],
    },
    "R14": {
        "title": "上市窗口14→10个月，四个内部瓶颈要求体系升级",
        "environment_heading": "1. 外部变化（合成样本）",
        "environment": [
            {"icon": "clock-arrow-down", "label": "上市窗口", "value": "14→12→10个月"},
            {"icon": "chart-bar", "label": "需求变更占比", "value": "12%→17%→23%"},
            {"icon": "user-round", "label": "软件需求占比", "value": "25%→34%→43%"}],
        "chart": {"label": "承诺上市窗口主比较（单位：月）", "labels": ["2023", "2025"], "values": [14, 10], "change": "缩短29%"},
        "insight": "压缩等待不能牺牲验收",
        "bottlenecks_heading": "2. 内部四大瓶颈",
        "bottlenecks": [
            {"icon": "split", "label": "目标不一致", "text": "部门指标冲突，取舍缺少共同结果", "value": "统一结果指标"},
            {"icon": "hourglass", "label": "流程等待", "text": "评审排队，关键资源窗口不固定", "value": "固定评审窗口"},
            {"icon": "layers", "label": "资产分散", "text": "同名不同版本，复用风险难识别", "value": "稳定ID与版本"},
            {"icon": "clipboard-list", "label": "度量缺失", "text": "工时口径不统一，结果不可比较", "value": "先统一字典"}],
        "positioning": "3. 体系升级定位：在质量底线下打通研发协同，优先修复接口与责任",
    },
    "R15": {
        "title": "用户价值为核心，四层管理与横向协同形成完整责任链",
        "subtitle": "构建“一核两翼四层 + 研产销全链路协同”的研发效能管理体系",
        "overview": {"label": "体系总览", "groups": [
            {"icon": "target", "label": "核心架构逻辑", "items": ["中心为客户任务", "两翼为方法与工具", "纵向四层管理", "横向研产销协同"]},
            {"icon": "network", "label": "核心设计原则", "items": ["价值导向", "分层适配", "数据驱动", "质量门禁"]}]},
        "roof": {"label": "用户价值创造", "text": "客户任务可完成｜交付可追溯｜风险可控制"},
        "wings": [{"label": "精益研发方法（左翼）", "text": "流程 / 质量 / 改善"}, {"label": "数字化工具链（右翼）", "text": "数据 / 平台 / 自动采集"}],
        "vertical_left": "纵向分层管理颗粒度",
        "vertical_right": "横向研产销全链路协同",
        "layers": [
            {"icon": "compass", "label": "战略解码层", "text": "目标 → 资源 → 准入", "attributes": ["目标对齐", "资源协同", "准入清晰"]},
            {"icon": "clipboard-check", "label": "项目运营层", "text": "计划 → 风险 → 交付", "attributes": ["过程可视", "风险可控", "交付可期"]},
            {"icon": "boxes", "label": "工程能力层", "text": "架构 → 模块 → 验证", "attributes": ["能力沉淀", "资产复用", "验证闭环"]},
            {"icon": "database", "label": "基础支撑层", "text": "工具 → 规范 → 人才", "attributes": ["统一支撑", "规范落地", "人才保障"]}],
        "collaboration_heading": "横向协同机制",
        "collaborations": [
            {"label": "研发 ↔ 市场", "left_icon": "users", "right_icon": "code-xml", "text": "用户需求直达研发，反馈驱动迭代", "flow": "需求洞察 → 签收 → 验证 → 迭代"},
            {"label": "研发 ↔ 制造", "left_icon": "factory", "right_icon": "code-xml", "text": "可制造性前置，缩短试制周期", "flow": "设计输入 → DFM评审 → 工艺验证"}],
        "targets_heading": "价值目标",
        "targets": [
            {"icon": "timer", "label": "交接时长", "value": "≤3天", "note": "TARGET"},
            {"icon": "shield-check", "label": "首轮通过", "value": "≥90%", "note": "TARGET"},
            {"icon": "database", "label": "数据完备", "value": "≥95%", "note": "TARGET"},
            {"icon": "chart-pie", "label": "模块复用", "value": "≥60%", "note": "TARGET"},
            {"icon": "user-round-check", "label": "客户验收", "value": "无阻断", "note": "TARGET"}],
        "core": {"label": "核心判断", "text": "只有工件、责任与门禁连接起来，平台才具备可验收边界。"},
    },
}


def _f(field_type: str, semantic: str, *, min_items: int | None = None,
       item_fields: str | None = None) -> dict[str, Any]:
    value: dict[str, Any] = {"type": field_type, "required": True, "semantic": semantic}
    if min_items is not None:
        value["min_items"] = min_items
    if item_fields:
        value["item_fields"] = item_fields
    return value


def _schema(*, business_question: str, reading_order: list[str], layout_reason: str,
            text_roles: dict[str, str], preserve_relations: list[str],
            component_judgement: list[str], fields: dict[str, Any],
            source_band: dict[str, Any] | None = None) -> dict[str, Any]:
    schema = {
        "canvas": "1280x720",
        "evidence_scope": "visual-only reference screenshot; editable reconstruction",
        "business_question": business_question,
        "reading_order": reading_order,
        "layout_reason": layout_reason,
        "text_roles": text_roles,
        "preserve_relations": preserve_relations,
        "component_judgement": component_judgement,
        "fields": fields,
    }
    if source_band is not None:
        schema["source_band"] = source_band
    return schema


SCHEMAS: dict[str, dict[str, Any]] = {
    "R01": _schema(
        business_question="研发体系升级在短、中、长期分别创造什么价值，外部趋势如何支持终局判断？",
        reading_order=["结论标题", "三期价值阶梯", "三项趋势证据", "理念/路径/终局收口"],
        layout_reason="三张阶段卡随时间向右抬升，直接编码价值递进；趋势横排承接外部驱动；深蓝底栏把观察压成管理判断。",
        text_roles={"title": "主张", "stages": "分期价值证据", "trends": "外部驱动解释", "bottom": "结论与行动方向"},
        preserve_relations=["三阶段必须保持左低右高的连续阶梯", "每阶段固定三条价值", "底栏三段分别回答理念、路径、终局"],
        component_judgement=["阶段使用同高信息卡加抬升折线，不用普通三卡", "趋势用图标说明卡", "最终判断使用深色连续带"],
        fields={"title": _f("string", "结论型标题"), "stage_heading": _f("string", "阶段区说明"),
                "stages": _f("array", "短中长期三阶段", min_items=3, item_fields="label + items[3]{icon,text}"),
                "trend_heading": _f("string", "趋势区说明"), "trends": _f("array", "三项趋势", min_items=3, item_fields="icon,label,text"),
                "bottom_label": _f("string", "底部结论标签"), "bottom": _f("array", "理念/路径/终局", min_items=3, item_fields="icon,label,text")}),
    "R02": _schema(
        business_question="跨部门转型由谁共同负责，激励与人才机制如何让三方长期协同？",
        reading_order=["总主张", "左侧铁三角职责", "右上三项激励", "右下三项能力", "底部三原则"],
        layout_reason="左侧大三瓣结构先明确业务/方法/技术的共担关系，右侧六卡把组织机制拆成激励与能力两类，底栏用同色语义回扣。",
        text_roles={"triangle": "责任主体与职责", "groups": "配套机制", "principles": "组织设计结论"},
        preserve_relations=["铁三角必须三瓣相扣并中心留白", "蓝/青/紫跨激励、能力、原则保持一致编码", "右侧必须两排三列"],
        component_judgement=["责任关系用多边形三瓣而非并列卡", "机制条目用六张卡", "原则用底部轻量总结带"],
        fields={"title": _f("string", "组织主张"), "triangle_heading": _f("string", "责任图区标题"),
                "triangle": _f("array", "三方责任", min_items=3, item_fields="icon,label,text"),
                "groups": _f("array", "激励与能力两组", min_items=2, item_fields="label + items[3]{icon,label,text}"),
                "principles": _f("array", "三条收口原则", min_items=3, item_fields="icon,label,text")}),
    "R03": _schema(
        business_question="十八个月路线如何分期，每期做什么、交付什么、满足什么条件才能继续？",
        reading_order=["标题与总路线", "横向三节点", "三张四层明细卡", "底部价值演进"],
        layout_reason="横向节点先给时间顺序，三张同高卡按目标/动作/产出/风险完整展开，避免把路线压成只有节点的时间轴。",
        text_roles={"title": "路线主张", "subtitle": "门禁前提", "stages": "可执行阶段合同", "value_steps": "阶段价值递进"},
        preserve_relations=["三卡严格同宽同高", "每卡固定四层", "阶段节点与对应卡中心对齐", "退出条件写入产出层"],
        component_judgement=["阶段轴表达顺序", "明细卡表达治理合同", "底部箭头表达能力演进"],
        fields={"title": _f("string", "路线结论"), "subtitle": _f("string", "质量门与暂停规则"),
                "stages": _f("array", "三阶段明细", min_items=3, item_fields="label,milestone_icon,focus,target,actions[3],outputs[3],risk"),
                "value_label": _f("string", "价值区标签"), "value_steps": _f("array", "三阶段价值", min_items=3, item_fields="string")}),
    "R04": _schema(
        business_question="项目为什么要改、采取了哪四项治理动作、结果指标出现了什么变化？",
        reading_order=["数字结论标题", "三条背景证据", "四项升级动作", "五项量化结果", "经验收口"],
        layout_reason="一条背景带压缩上下文，四卡用箭头组成动作链，五张结果卡扩大数值权重，深色底栏限制因果表述。",
        text_roles={"background": "问题背景", "actions": "干预动作", "results": "前后比较证据", "experience": "解释边界"},
        preserve_relations=["固定1条背景+4动作+5结果", "动作从左到右连接", "结果必须含指标名、前后值和洞察", "经验全宽压轴"],
        component_judgement=["动作卡适合串联", "结果卡适合突出数字", "不把背景拆成独立大卡"],
        fields={"title": _f("string", "结果主张"), "background_label": _f("string", "背景标签"),
                "background": _f("array", "背景证据", min_items=3, item_fields="string"), "actions_heading": _f("string", "动作区标题"),
                "actions": _f("array", "四项治理动作", min_items=4, item_fields="icon,label,input,action,output"), "results_heading": _f("string", "结果区标题"),
                "results": _f("array", "五项量化结果", min_items=5, item_fields="icon,label,value,detail"), "experience": _f("string", "经验及因果边界")}),
    "R05": _schema(
        business_question="四类共性卡点各自表现在哪里、根因假设是什么、由谁如何验证整改？",
        reading_order=["总问题", "左上到右下四张诊断卡", "每卡现象→根因→方案", "右侧Insight"],
        layout_reason="2×2让四类问题等权比较；每卡内部三层把诊断和应对串起来；右侧独立洞察把复杂文本压成一句判断。",
        text_roles={"issues.label": "问题定义", "rows": "现象/假设/行动", "insight": "管理结论"},
        preserve_relations=["每卡三层次序不可变", "方案层使用绿色语义", "洞察区必须与诊断行分隔", "四卡同尺寸"],
        component_judgement=["诊断内容用分层卡", "洞察用独立图标区", "不合并成四个问题摘要"],
        fields={"title": _f("string", "诊断主题"), "issues": _f("array", "四类卡点", min_items=4, item_fields="label,icon,rows[3]{icon,label,items[2]},insight")}),
    "R06": _schema(
        business_question="效率、质量和投入分别用什么口径衡量，三个工具升级是否留下可核验证据？",
        reading_order=["结论标题", "上部三列九项指标", "下部三项工具结果", "每卡洞察"],
        layout_reason="上部3×3先统一度量语言，下部三张大卡再展示局部作业前后值，使指标口径与工具结果清楚分层。",
        text_roles={"metric_groups": "定义与口径", "results": "局部实测证据", "insight": "可追溯结论"},
        preserve_relations=["三类指标各三行并严格对齐", "下部每卡必须两组数值/范围", "标题数字不能替代样本边界"],
        component_judgement=["口径用行式指标组", "前后对比用大数值结果卡", "不使用统一九卡网格"],
        fields={"title": _f("string", "度量主张"), "metric_groups": _f("array", "效率/质量/投入三组", min_items=3, item_fields="label + items[3]{icon,label,value,text}"),
                "results_heading": _f("string", "工具结果说明"), "results": _f("array", "三项工具升级", min_items=3, item_fields="icon,label,primary,secondary_label,secondary,sample,insight")}),
    "R07": _schema(
        business_question="交付节奏和工作负荷是否同时健康，典型延期怎样从现象走到验证目标？",
        reading_order=["数字结论", "两组各三项指标", "案例现象", "根因假设", "动作", "验证目标"],
        layout_reason="上半双栏把结果指标与过程负荷并置，下半四步楔形流程用单一案例证明如何闭环，形成体系证据+案例证据。",
        text_roles={"metric_groups": "体系指标", "case_steps": "案例证据链", "value": "结果或TARGET"},
        preserve_relations=["上部必须左右两组各三行", "每行保留洞察块", "案例必须四步并由楔形连接", "首尾保留微图和大数值"],
        component_judgement=["指标体系用对齐行", "案例用流程卡", "现象/成效使用原生图表"],
        fields={"title": _f("string", "结果与问题主张"), "metric_groups": _f("array", "两组指标", min_items=2, item_fields="label + items[3]{icon,label,definition,value,reference,insight}"),
                "case_heading": _f("string", "案例标题与范围"), "case_steps": _f("array", "现象到验证四步", min_items=4, item_fields="label + chart/text/value 或 items")}),
    "R08": _schema(
        business_question="降本应从哪些设计动作进入，用哪些互不混算的指标衡量，案例何时可以扩围？",
        reading_order=["总判断", "四项方法", "三项度量", "案例动作与三项证据", "扩围条件"],
        layout_reason="三层横向分带依次回答方法、度量、案例；方法用大图标识别，指标用定义卡，案例用左标签+右数值形成业务账本感。",
        text_roles={"methods": "降本手段", "metrics": "互斥度量口径", "case": "合成案例与扩围门"},
        preserve_relations=["必须四方法+三指标+一案例条", "三类成本指标不得相加", "案例底部洞察贯穿全宽"],
        component_judgement=["方法用图标说明卡", "指标用定义卡", "案例用复合数据条而非普通卡"],
        fields={"title": _f("string", "成本主张"), "methods_heading": _f("string", "方法区标题"), "methods": _f("array", "四类设计降本方法", min_items=4, item_fields="icon,label,text,boundary"),
                "metrics_heading": _f("string", "度量区标题"), "metrics": _f("array", "三项独立度量", min_items=3, item_fields="icon,label,value,definition,insight"),
                "case_heading": _f("string", "案例标题"), "case": _f("object", "案例动作、数值与扩围条件", item_fields="labels[4],icon,description,metrics[4],status,insight")}),
    "R09": _schema(
        business_question="统一主数据如何与设计、测试、项目平台双向连接，试点价值如何用同样任务证明？",
        reading_order=["协同主张", "左侧一库", "右侧三平台与双向箭头", "四项能力带", "三项试点价值"],
        layout_reason="左一库右三平台体现源与消费方的系统关系，双向箭头强调回写；底部三案例将架构价值转为可核验任务结果。",
        text_roles={"store/platforms": "系统边界与工件", "capabilities": "架构能力", "cases": "任务级证据"},
        preserve_relations=["一库不是第四个平台卡", "库与平台、平台之间保留双向连接", "底部固定三张价值卡", "数值不得外推总体效率"],
        component_judgement=["架构用关系图", "能力用细带", "价值用案例证据卡"],
        fields={"title": _f("string", "架构价值主张"), "architecture_heading": _f("string", "架构区标题"), "store": _f("object", "统一主数据源", item_fields="icon,label,items[4]"),
                "platforms": _f("array", "三类业务平台", min_items=3, item_fields="icon,label,items[4]"), "capabilities": _f("array", "四项互通能力", min_items=4, item_fields="string"),
                "cases_heading": _f("string", "试点证据说明"), "cases": _f("array", "三项同题任务结果", min_items=3, item_fields="icon,label,value,insight,detail")}),
    "R10": _schema(
        business_question="效率与质量六项趋势是否改善，一次偏差应怎样沿五层证据定位并闭环？",
        reading_order=["评估主张", "左三效率微图", "右三质量微图", "五层诊断链", "整改闭环"],
        layout_reason="六个同规格微图支持横向比较，底部五层由表象逐步深入根因，再用独立闭环卡把诊断转成行动。",
        text_roles={"chart_groups": "趋势证据", "diagnosis": "原因层级", "closure": "整改与复核"},
        preserve_relations=["六个原生微图保持两组各三张", "目标线/阈值写入图表数据", "诊断必须现象→执行→流程→机制→根因", "整改卡在链路右端"],
        component_judgement=["趋势必须用原生图表", "根因链用收窄梯形", "闭环用独立确认卡"],
        source_band={"x": 32, "y": 470, "w": 1216, "h": 26,
                     "max_lines": 2, "font_size": 11},
        fields={"title": _f("string", "综合评估主张"), "chart_groups": _f("array", "效率与质量两组图表；每项labels[N]与values[N]同长且N≥3；bar可用target_category追加目标柱，bar/line可用reference_line生成同轴参考线", min_items=2, item_fields="id,label,items[3]{label,summary,labels[N],values[N],kind,format,target,target_category?,reference_line?,insight}"),
                "diagnosis_heading": _f("string", "案例范围"), "diagnosis": _f("array", "五层证据链", min_items=5, item_fields="icon,label,text"),
                "closure": _f("object", "整改工件与复核", item_fields="label,actions[3],review")}),
    "R11": _schema(
        business_question="需求管理平台如何把分散传导改造成闭环，实践证据是否覆盖投入、验证和价值？",
        reading_order=["结果主张", "左上四功能", "左中传统→闭环对照", "右侧三项实践证据", "底部两项量化结果"],
        layout_reason="左侧先说明平台能力与机制变化，右侧窄高案例面板连续放三项大数值，形成方案解释与结果证据的主次分栏。",
        text_roles={"functions": "平台输入输出", "comparison": "机制迁移", "case": "实践证据", "bottom_metrics": "两项量化改善结果"},
        preserve_relations=["四功能固定横排", "灰色传统模式指向蓝色闭环模式", "右侧案例固定三行证据", "底部两项指标以大数值收口"],
        component_judgement=["功能用紧凑卡", "模式变化用对照面板+箭头", "实践结果用垂直证据面板"],
        fields={"title": _f("string", "需求治理主张"), "functions_heading": _f("string", "能力区标题"),
                "functions": _f("array", "平台四功能", min_items=4, item_fields="icon,label,items[3]"), "comparison_heading": _f("string", "对照区标题"),
                "comparison": _f("array", "传统与闭环两模式", min_items=2, item_fields="label,rows[3]{icon,label,items[2]}"),
                "case": _f("object", "案例证据", item_fields="label,metrics[3]{icon,label,value,insight}"), "bottom_metrics": _f("array", "两项量化结果：指标名与带单位的实际值、目标或前后值；证据不足时显式待验证", min_items=2, item_fields="icon,label,value")}),
    "R12": _schema(
        business_question="模块复用为何失败，三级架构、根因和落地举措如何共同支撑试点数据？",
        reading_order=["复用结论", "三级金字塔及引线解释", "左根因表", "右编号举措", "底部三项试点数据"],
        layout_reason="金字塔表达基础→标准→业务的依赖层级，中部左右对照把问题与动作配对，底部大数值显示同一试点的观察结果。",
        text_roles={"levels": "能力层级", "roots": "缺口证据", "actions": "治理动作", "data": "试点观察"},
        preserve_relations=["三级必须保持上窄下宽", "每层右侧保留引线说明", "根因与举措同层并列", "数据固定三卡并标样本边界"],
        component_judgement=["层级用金字塔", "根因/举措用表格式分栏", "结果用大数值卡"],
        fields={"title": _f("string", "模块复用主张"), "architecture_heading": _f("string", "架构区标题"),
                "levels": _f("array", "三级模块架构", min_items=3, item_fields="icon,label,explanation"), "root_heading": _f("string", "根因区标题"),
                "roots": _f("array", "三类根因", min_items=3, item_fields="icon,label,text"), "actions_heading": _f("string", "行动区标题"),
                "actions": _f("array", "三项落地举措", min_items=3, item_fields="string"), "data_heading": _f("string", "试点区标签"),
                "data": _f("array", "三项试点数据", min_items=3, item_fields="icon,label,value,insight")}),
    "R13": _schema(
        business_question="七个研发环节各交付什么，怎样用并行工程和前置门禁缩短等待并降低修改成本？",
        reading_order=["流程主张", "七阶段连续箭头", "左并行甘特", "右成本曲线", "三项目标", "三条洞察"],
        layout_reason="顶部七段箭头给完整主流程，中部用两个机制图解释为何提效，底部目标卡与洞察栏把机制转成验收项。",
        text_roles={"flow": "阶段/工件/Owner", "parallel/cost_curve": "机制证据", "results": "目标值", "insights": "管理判断"},
        preserve_relations=["七阶段连续且由深至浅", "阶段必须同时显示工件和Owner", "中部必须是甘特对照+指数成本曲线", "底部三卡右侧三洞察"],
        component_judgement=["流程用箭头带", "并行逻辑用甘特几何", "成本逻辑用原生曲线", "目标用微图卡"],
        fields={"title": _f("string", "流程价值主张"), "flow_heading": _f("string", "流程区标题"), "flow": _f("array", "七阶段", min_items=7, item_fields="label,icon,artifact,action,owner"),
                "logic_heading": _f("string", "机制区标题"), "parallel": _f("object", "串并行机制", item_fields="label,text,value"),
                "cost_curve": _f("object", "晚改成本曲线", item_fields="label,text,labels[6],values[6]"), "results_heading": _f("string", "目标区标题"),
                "results": _f("array", "三项TARGET", min_items=3, item_fields="label,value,labels,values,kind,format"), "insights_heading": _f("string", "洞察区标题"),
                "insights": _f("array", "三条关键洞察", min_items=3, item_fields="icon,label,text")}),
    "R14": _schema(
        business_question="外部变化怎样压缩交付窗口，内部四大瓶颈为何要求体系升级？",
        reading_order=["体系升级主张", "上部三条环境证据", "中央主柱图", "右侧洞察", "下部四瓶颈", "定位结论"],
        layout_reason="上半用一个主柱图形成强视觉焦点，左侧补充环境证据，右侧给判断；下半四列瓶颈把外因传导到内部升级动作。",
        text_roles={"environment": "环境证据", "chart": "核心变化", "insight": "外部判断", "bottlenecks": "内部因果", "positioning": "体系定位"},
        preserve_relations=["中央只保留一个主图", "三条其他序列压成左证据行", "四瓶颈等宽且包含动作判断", "底部结论全宽"],
        component_judgement=["核心趋势用原生柱图", "环境补充用行式证据", "瓶颈用四列卡", "定位用深色带"],
        fields={"title": _f("string", "环境与升级主张"), "environment_heading": _f("string", "环境区标题"),
                "environment": _f("array", "三条环境序列摘要", min_items=3, item_fields="icon,label,value"), "chart": _f("object", "中央主图", item_fields="label,labels,values,change"),
                "insight": _f("string", "环境判断"), "bottlenecks_heading": _f("string", "瓶颈区标题"),
                "bottlenecks": _f("array", "四个内部瓶颈", min_items=4, item_fields="icon,label,text,value"), "positioning": _f("string", "体系升级定位")}),
    "R15": _schema(
        business_question="以用户价值为核心的研发体系如何分层，精益与数字两翼怎样连接市场和制造并形成验收目标？",
        reading_order=["总主张与副标题", "左侧体系说明", "中央屋顶→两翼→四层", "两侧纵横箭头", "右侧两个协同回路", "底部五目标与核心判断"],
        layout_reason="中央屋顶式架构把用户价值置顶，两翼说明方法和工具，四层说明治理颗粒度；左右侧栏分别承担原则和跨部门协同，底部把复杂架构落到验收指标。",
        text_roles={"overview": "架构解释与原则", "roof": "最终价值", "wings": "两类赋能", "layers": "治理层级", "collaborations": "横向闭环", "targets": "验收目标", "core": "判断收口"},
        preserve_relations=["中央必须保持屋顶+两翼+四层", "纵向层级和横向协同双箭头都要保留", "右侧必须两个双向回路", "底部五项目标与右侧核心洞察并列"],
        component_judgement=["用户价值用屋顶", "方法/工具用两翼", "管理责任用四层横条", "市场/制造用循环卡", "目标用指标带"],
        fields={"title": _f("string", "架构主张"), "subtitle": _f("string", "体系定义"), "overview": _f("object", "左侧说明", item_fields="label,groups[2]{icon,label,items[4]}"),
                "roof": _f("object", "用户价值屋顶", item_fields="label,text"), "wings": _f("array", "精益与数字两翼", min_items=2, item_fields="label,text"),
                "vertical_left": _f("string", "纵向治理轴"), "vertical_right": _f("string", "横向协同轴"), "layers": _f("array", "四层管理架构", min_items=4, item_fields="icon,label,text,attributes[3]"),
                "collaboration_heading": _f("string", "协同区标题"), "collaborations": _f("array", "市场与制造两个回路", min_items=2, item_fields="label,left_icon,right_icon,text,flow"),
                "targets_heading": _f("string", "价值目标标签"), "targets": _f("array", "五项TARGET", min_items=5, item_fields="icon,label,value,note"),
                "core": _f("object", "核心判断", item_fields="label,text")}),
}


RENDERERS = {
    "R01": render_r01,
    "R02": render_r02,
    "R03": render_r03,
    "R04": render_r04,
    "R05": render_r05,
    "R06": render_r06,
    "R07": render_r07,
    "R08": render_r08,
    "R09": render_r09,
    "R10": render_r10,
    "R11": render_r11,
    "R12": render_r12,
    "R13": render_r13,
    "R14": render_r14,
    "R15": render_r15,
}


__all__ = ["DEFAULTS", "SCHEMAS", "RENDERERS"]
