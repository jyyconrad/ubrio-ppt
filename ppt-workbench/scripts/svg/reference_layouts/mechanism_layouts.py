"""Reference-specific mechanism layouts R16-R30 and R32.

The functions reproduce the visible composition grammar of the supplied screenshots while
keeping all business text and data replaceable through ``content``.  Values in DEFAULTS are
explicitly synthetic proposals or samples, never claims copied from the source artwork.
"""

from __future__ import annotations

import copy
import math

from .common import BLUE, INK, LINE, MID, PURPLE, Svg, wrap

PALE = "#F7F9FC"
MUTED = "#66758A"
GREEN = "#24846B"
ORANGE = "#E57C25"
SOFT_BLUE = "#DCE8F7"

ICONS = [
    "target",
    "users",
    "search",
    "chart-bar-increasing",
    "shield-check",
    "lightbulb",
    "alarm-clock",
    "file-text",
    "database",
    "refresh-ccw",
    "scale",
    "handshake",
    "box",
    "message-circle",
    "brain-circuit",
    "wrench",
]


class MechanismSvg(Svg):
    """Apply the mechanism-page typography contract at the drawing boundary."""

    _ROLE_FLOORS = {"body": 15.0, "diagram": 12.0, "source": 11.0}

    def text(
        self,
        x,
        y,
        value,
        size=16,
        color=INK,
        bold=False,
        width=None,
        anchor="start",
        leading=None,
        role=None,
        max_lines=None,
    ):
        semantic_role = role or "body"
        if semantic_role not in self._ROLE_FLOORS:
            raise ValueError(f"unsupported mechanism text role: {semantic_role}")
        resolved_size = max(float(size), self._ROLE_FLOORS[semantic_role])
        resolved_leading = max(float(leading), resolved_size * 1.22) if leading else None
        return super().text(
            x,
            y,
            value,
            resolved_size,
            color,
            bold,
            width,
            anchor,
            resolved_leading,
            semantic_role,
            max_lines,
        )

    def bullets(self, x, y, items, width, size=15, gap=9, color=INK, role="body"):
        position = y
        for value in items:
            position += self.text(x, position, str(value), size, color, width=width, role=role) + gap
        return position

    def ribbon(self, x, y, w, h, value, number=None, color=BLUE, size=18):
        self.poly(
            [(x, y), (x + w - 14, y), (x + w, y + h / 2), (x + w - 14, y + h), (x, y + h)],
            color,
        )
        if number is not None:
            self.circle(x + 21, y + h / 2, 13, "#FFFFFF")
            self.text(x + 21, y + h / 2 + 5, number, 15, color, True, anchor="middle", role="diagram")
        self.text(
            x + w / 2 + (9 if number is not None else 0),
            y + h * 0.71,
            value,
            size,
            "#FFFFFF",
            True,
            anchor="middle",
            role="diagram",
        )


def _content(ref_id, content):
    data = copy.deepcopy(DEFAULTS[ref_id])
    data.update(content or {})
    return data


def _panel(s, x, y, w, h, title=None, fill="#FFFFFF", color=BLUE):
    s.rect(x, y, w, h, fill, LINE, 4)
    if title:
        s.header(x, y, w, title, 28, color=color, size=14)


def _icon_label(s, icon, x, y, title, note="", w=150, size=14, disc=True, color=BLUE):
    s.icon(icon, x, y, 28, "#FFFFFF" if disc else color, disc=disc, disc_color=color)
    s.text(x + 46, y + 15, title, size, INK, True, width=w - 46, role="diagram")
    if note:
        s.text(x + 46, y + 38, note, 15, MUTED, width=w - 46, leading=18, role="body")


def _mini_card(s, x, y, w, h, title, lines, icon="target", fill="#FFFFFF", color=BLUE):
    s.rect(x, y, w, h, fill, LINE, 4)
    s.icon(icon, x + 10, y + 10, 25, color)
    s.text(x + 42, y + 25, title, 13, color, True, width=w - 52, role="diagram")
    s.bullets(x + 13, y + 48, lines, w - 26, 15, 3, role="body")


def _flow_cards(s, items, x, y, w, h, reverse=False, color=BLUE, notes=True):
    n = len(items)
    cw = w / n
    for i, item in enumerate(items):
        xx = x + i * cw
        icon = item.get("icon", ICONS[i % len(ICONS)])
        s.circle(xx + cw / 2, y + 26, 22, color)
        s.icon(icon, xx + cw / 2 - 14, y + 12, 28, "#FFFFFF")
        s.number(xx + 15, y + 7, str(i + 1), 10)
        s.text(
            xx + cw / 2,
            y + 61,
            item["name"],
            12,
            INK,
            True,
            width=cw - 10,
            anchor="middle",
            role="diagram",
        )
        if notes:
            s.text(
                xx + cw / 2,
                y + 82,
                item.get("note", ""),
                9,
                MUTED,
                width=cw - 16,
                anchor="middle",
                leading=12,
                role="body",
            )
        if i < n - 1:
            if reverse:
                s.arrow(xx + cw + 4, y + 27, xx + cw - 23, y + 27, color, 2)
            else:
                s.arrow(xx + cw - 20, y + 27, xx + cw + 2, y + 27, color, 2)


def _network(s, nodes, edges, positions, color=BLUE, dashed_edges=()):
    for index, (a, b) in enumerate(edges):
        ax, ay = positions[a]
        bx, by = positions[b]
        s.arrow(ax, ay, bx, by, color, 1.1, dashed=index in dashed_edges)
    for index, node in enumerate(nodes):
        x, y = positions[index]
        s.circle(x, y, 15, "#FFFFFF", color, stroke_width=2)
        s.text(x, y + 4, str(node), 12, color, True, anchor="middle", width=44, role="diagram")


def _quadrant(s, x, y, w, h, quadrants, x_label, y_label):
    s.rect(x, y, w, h, "#FFFFFF", LINE, 0)
    s.line(x + w / 2, y, x + w / 2, y + h, LINE, 1.2, True)
    s.line(x, y + h / 2, x + w, y + h / 2, LINE, 1.2, True)
    fills = ["#E6EEF9", "#D0E0F3", "#F2F5F9", "#DFE8F4"]
    for i, item in enumerate(quadrants):
        xx = x + (i % 2) * w / 2
        yy = y + (i // 2) * h / 2
        s.rect(xx + 5, yy + 5, w / 2 - 10, h / 2 - 10, fills[i], "none", 3)
        s.text(xx + 15, yy + 28, item["name"], 14, BLUE, True, width=w / 2 - 30, role="diagram")
        s.bullets(xx + 15, yy + 51, item.get("lines", []), w / 2 - 30, 15, 4, role="body")
    if x_label:
        s.text(x + w / 2, y + h + 23, x_label, 12, INK, True, anchor="middle", role="diagram")
        s.arrow(x, y + h + 4, x + w, y + h + 4, BLUE, 1.5)
    if y_label:
        s.text(x - 40, y + h / 2, y_label, 12, INK, True, anchor="middle", role="diagram")
        s.arrow(x - 5, y + h, x - 5, y, BLUE, 1.5)


def _curve_arrow(
    s, d, end_x, end_y, tangent_x, tangent_y, color=BLUE, width=2, dashed=False, role=None
):
    """Draw a curved connector with a visible arrowhead at its terminal tangent."""
    path = s.path(d, stroke=color, width=width, dashed=dashed)
    if role:
        path.set("data-role", role)
    theta = math.atan2(end_y - tangent_y, end_x - tangent_x)
    length = max(8, width * 3.4)
    s.poly(
        [
            (end_x, end_y),
            (
                end_x - length * math.cos(theta - 0.45),
                end_y - length * math.sin(theta - 0.45),
            ),
            (
                end_x - length * math.cos(theta + 0.45),
                end_y - length * math.sin(theta + 0.45),
            ),
        ],
        color,
    )


def _arc_arrow(s, cx, cy, radius, start, end, color=BLUE, width=2, dashed=False, role=None):
    """Approximate a short circular arc with a cubic curve and add an arrowhead."""
    delta = end - start
    k = 4 / 3 * math.tan(delta / 4)
    x1, y1 = cx + radius * math.cos(start), cy + radius * math.sin(start)
    x2, y2 = cx + radius * math.cos(end), cy + radius * math.sin(end)
    c1x, c1y = x1 - k * radius * math.sin(start), y1 + k * radius * math.cos(start)
    c2x, c2y = x2 + k * radius * math.sin(end), y2 - k * radius * math.cos(end)
    _curve_arrow(
        s,
        f"M{x1:.2f} {y1:.2f} C{c1x:.2f} {c1y:.2f} {c2x:.2f} {c2y:.2f} {x2:.2f} {y2:.2f}",
        x2,
        y2,
        c2x,
        c2y,
        color,
        width,
        dashed,
        role,
    )


def _solid_arrow(s, x1, y, x2, height=18, color=BLUE, role=None):
    shaft = max(8, height * 0.46)
    head = min(18, max(10, x2 - x1))
    node = s.poly(
        [
            (x1, y - shaft / 2),
            (x2 - head, y - shaft / 2),
            (x2 - head, y - height / 2),
            (x2, y),
            (x2 - head, y + height / 2),
            (x2 - head, y + shaft / 2),
            (x1, y + shaft / 2),
        ],
        color,
        data_role=role,
    )
    return node


def _stacked_text(
    s,
    x,
    y,
    value,
    width,
    size=12,
    color=INK,
    bold=False,
    anchor="start",
    leading=15,
    max_lines=None,
    role="body",
):
    resolved_size = max(float(size), MechanismSvg._ROLE_FLOORS[role])
    resolved_leading = max(float(leading), resolved_size * 1.22)
    lines = wrap(value, width, resolved_size)
    if max_lines is not None and len(lines) > max_lines:
        raise ValueError(f"text exceeds {max_lines}-line capacity: {str(value)[:100]!r}")
    for index, line in enumerate(lines):
        s.text(x, y + index * resolved_leading, line, resolved_size, color, bold, anchor=anchor, role=role)
    return len(lines)


def render_r16(content):
    d = _content("R16", content)
    s = MechanismSvg()
    s.title(d["title"], d["subtitle"], 35, color="#10131D")
    _panel(s, 18, 108, 548, 248, d["cycle_title"])
    # A continuous 2x2 grid is the visible operating model, not four floating notes.
    s.rect(28, 141, 528, 205, "#FFFFFF", LINE, 0)
    s.rect(291, 141, 1.5, 205, LINE, "none", 0, data_role="vitality-quadrant-divider")
    s.rect(28, 243, 528, 1.5, LINE, "none", 0, data_role="vitality-quadrant-divider")
    cx, cy = 292, 243
    s.circle(cx, cy, 58, "#FFFFFF", BLUE, stroke_width=3)
    s.text(
        cx,
        cy - 4,
        d["cycle_center"],
        16,
        BLUE,
        True,
        width=95,
        anchor="middle",
        leading=19,
    )
    pts = [(40, 155), (365, 155), (365, 257), (40, 257)]
    for i, item in enumerate(d["cycle"]):
        x, y = pts[i]
        s.icon(item["icon"], x, y, 38, "#FFFFFF", disc=True, disc_color=BLUE)
        s.text(x + 48, y + 14, item["name"], 12.5, BLUE, True, width=145, max_lines=1, role="diagram")
        s.bullets(x + 48, y + 36, item["actions"], 145, 10.5, 3)
    for a, b in [
        ((cx, 171), (349, 205)),
        ((349, 245), (cx, 293)),
        ((cx, 293), (235, 245)),
        ((235, 205), (cx, 171)),
    ]:
        s.arrow(*a, *b, BLUE, 2.4)
    _panel(s, 585, 108, 677, 248, d["decline_title"])
    step_w = 125
    for i, item in enumerate(d["decline"]):
        x = 602 + i * 129
        s.number(x + 12, 151, str(i + 1), 10)
        s.circle(x + 63, 170, 24, "#FFFFFF", BLUE, stroke_width=2)
        s.icon(item["icon"], x + 47, 154, 32, BLUE)
        s.text(x + 63, 211, item["name"], 12, BLUE, True, width=step_w, anchor="middle", max_lines=2, role="diagram")
        s.bullets(x + 7, 245, item["lines"], step_w - 14, 10.2, 3)
        if i < 4:
            s.arrow(x + 102, 170, x + 126, 170, BLUE, 2)
    cols = [(18, 372, 390, 323), (425, 372, 430, 323), (872, 372, 390, 323)]
    _panel(s, *cols[0], d["defense_title"])
    for i, item in enumerate(d["defenses"]):
        yy = 414 + i * 65
        defense_icons = ["shield-check", "scale", "file-text", "refresh-ccw"]
        s.icon(defense_icons[i], 34, yy, 28, "#FFFFFF", disc=True, disc_color=BLUE)
        s.text(82, yy + 14, item["name"], 12.5, BLUE, True, width=120, max_lines=1, role="diagram")
        s.text(202, yy + 14, item["definition"], 10.5, INK, width=188, max_lines=2)
        s.text(82, yy + 36, f"{item['owner']}｜{item['artifact']}｜{item['practice']}", 12, MUTED, width=308, max_lines=2, role="diagram")
    _panel(s, *cols[1], d["curve_title"])
    s.rect(452, 438, 2, 216, BLUE, "none", 0, data_role="vitality-curve-axis")
    s.rect(452, 652, 386, 2, BLUE, "none", 0, data_role="vitality-curve-axis")
    s.path(
        "M458 558 C550 500 650 505 720 520 C792 537 812 591 836 646",
        stroke=BLUE,
        width=3,
    )
    s.line(690, 412, 690, 654, MUTED, 1, True)
    s.text(545, 423, "活力扩张", 15, BLUE, True)
    s.text(720, 423, "守成衰退", 15, MUTED, True)
    s.bullets(452, 454, d["curve_growth"], 190, 10.5, 3)
    s.bullets(704, 454, d["curve_decline"], 130, 10.5, 3)
    signal_lines = ["分水岭信号｜" + d["curve_signals"][0],
                    " / ".join(d["curve_signals"][1:])]
    if any(len(wrap(line, 380, 12)) != 1 for line in signal_lines):
        raise ValueError("R16 curve signals exceed the fixed two-line capacity")
    s.text(452, 664, "\n".join(signal_lines), 12, MUTED,
           width=380, max_lines=2, role="diagram")
    _panel(s, *cols[2], d["signals_title"])
    for i, item in enumerate(d["signals"]):
        yy = 410 + i * 44
        s.icon(ICONS[(i + 5) % len(ICONS)], 885, yy, 24, BLUE)
        s.text(920, yy + 12, item["name"], 12, BLUE, True, width=115, max_lines=1, role="diagram")
        s.text(1035, yy + 12, item["meaning"], 10, INK, width=205, max_lines=1)
        s.text(920, yy + 29, item["source"], 11, MUTED, width=320, max_lines=1, role="source")
    return s.finish()


def render_r17(content):
    d = _content("R17", content)
    result_title = str(d["result_title"]).strip()
    if "\n" in result_title or len(result_title) > 6:
        raise ValueError("R17 result_title exceeds the fixed single-line 6-character capacity")
    s = MechanismSvg()
    s.title(d["title"], d["subtitle"], 35, color="#10131D")
    for i, item in enumerate(d["steps"]):
        step_x = 25 + i * 205
        s.ribbon(step_x, 108, 207, 34, item["name"], str(i + 1), size=13)
        s.rect(step_x, 142, 205, 94, "#FFFFFF", LINE, 0)
        if i:
            s.rect(step_x, 148, 1, 80, LINE, "none", 0, stroke_dasharray="4 3")
        s.icon(item["icon"], step_x + 82, 151, 34, BLUE, disc=True)
        s.text(
            step_x + 102,
            208,
            item["note"],
            10,
            INK,
            width=175,
            anchor="middle",
            leading=13,
        )
    s.path("M1235 225 L1235 250 L115 250 L115 238", stroke=BLUE, width=1.5)
    s.arrow(115, 238, 115, 224, BLUE, 1.5)
    _panel(s, 24, 270, 600, 420)
    s.text(36, 292, d["compare_title"], 12, MUTED, width=575, role="diagram")
    s.rect(35, 302, 278, 367, "#F2F5F8", LINE, 0, data_role="comparison-column")
    s.rect(337, 302, 275, 367, "#EAF1FA", LINE, 0, data_role="comparison-column")
    s.header(35, 302, 278, "竞争对手导向｜Inside-Out", 32, "#6C82A1", 12)
    s.header(337, 302, 275, "客户痴迷｜Outside-In", 32, BLUE, 12)
    for i, row in enumerate(d["comparison"]):
        y = 334 + i * 67
        s.rect(35, y, 278, 67, "#F2F5F8", LINE, 0)
        s.rect(337, y, 275, 67, "#EAF1FA", LINE, 0)
        left_icon = s.icon(ICONS[(i + 2) % len(ICONS)], 45, y + 19, 24, "#6C82A1")
        left_icon.set("data-role", "comparison-row-icon")
        right_icon = s.icon("shield-check", 347, y + 19, 24, BLUE)
        right_icon.set("data-role", "comparison-row-icon")
        s.text(78, y + 24, row["inside"], 12, INK, True, width=220, max_lines=1, role="diagram")
        _stacked_text(s, 78, y + 48, row["inside_note"], 220, 15, MUTED, leading=16, max_lines=2, role="body")
        s.text(380, y + 24, row["outside"], 12, BLUE, True, width=217, max_lines=1, role="diagram")
        _stacked_text(s, 380, y + 48, row["outside_note"], 217, 15, INK, leading=16, max_lines=2, role="body")
    s.circle(325, 501, 22, BLUE)
    s.text(325, 506, "VS", 12, "#FFFFFF", True, anchor="middle", role="diagram")
    _panel(s, 646, 270, 616, 240)
    radar = d["radar"]
    dimension_labels = [item["label"] for item in radar["dimension_notes"]]
    if radar["labels"] != dimension_labels:
        raise ValueError("R17 radar labels must match dimension_notes labels in the same order")
    for series in radar["series"]:
        for value in series["values"]:
            if (
                not isinstance(value, (int, float))
                or isinstance(value, bool)
                or not math.isfinite(value)
                or not 0 <= value <= 5
            ):
                raise ValueError("R17 radar values must be finite and remain within the fixed 0..5 scale")
    s.text(666, 294, d["radar_title"], 15, INK, True, width=230, max_lines=1, role="body")
    legend_x = [915, 1000, 1085]
    legend_colors = [BLUE, MID, "#8DA2BE"]
    for index, series in enumerate(radar["series"]):
        line = s.node(
            "line",
            x1=legend_x[index],
            y1=289,
            x2=legend_x[index] + 23,
            y2=289,
            stroke=legend_colors[index],
            stroke_width=2.5,
            stroke_dasharray="5 4" if index == 2 else None,
            data_role="radar-series-legend",
        )
        _ = line
        s.text(legend_x[index] + 29, 294, series["name"], 12, legend_colors[index], True, role="diagram")
    s.chart(
        "r17-radar",
        820,
        342,
        240,
        150,
        radar["labels"],
        radar["series"],
        kind="radar",
        fmt="0.0",
        options={
            "data_labels": False,
            "legend": False,
            "category_labels": False,
            "value_axis": {"minimum": 0, "maximum": 5, "format": "0.0", "labels": False},
            "radar_fill_series_index": 1,
            "radar_fill_transparency": 65,
            "dashed_series_indices": [2],
        },
    )
    dimension_slots = [
        (830, 304, 220, "middle", 940, 342),
        (1072, 342, 176, "start", 1060, 370),
        (1072, 407, 176, "start", 1060, 420),
        (660, 407, 150, "start", 820, 420),
        (660, 342, 150, "start", 820, 370),
    ]
    for item, (x, y, width, anchor, line_x, line_y) in zip(radar["dimension_notes"], dimension_slots):
        s.line(line_x, line_y, x + width / 2 if anchor == "middle" else x, y + 8, "#8DA2BE", 1)
        marker = s.rect(x, y, width, 43, "#FFFFFF", "none", 0, data_role="radar-dimension-note")
        _ = marker
        s.text(x if anchor == "start" else x + width / 2, y + 14, f"{item['label']}｜{item['english']}", 12, BLUE, True, width=width, anchor=anchor, max_lines=1, role="diagram")
        s.text(x if anchor == "start" else x + width / 2, y + 35, item["note"], 15, INK, width=width, anchor=anchor, max_lines=1, role="body")
    s.text(850, 507, d["radar_note"], 15, MUTED, width=280, max_lines=1, role="body")
    _panel(s, 646, 510, 616, 180)
    s.text(660, 529, d["action_title"], 12, MUTED, width=570, role="diagram")
    for i, item in enumerate(d["actions"]):
        x = 660 + i * 152
        header = s.rect(x, 545, 140, 29, BLUE, "none", 1, data_role="action-stage-header")
        _ = header
        english = ["Voice", "Insight", "Action"][i]
        s.text(x + 70, 565, f"{i + 1}. {item['name']}｜{english}", 12, "#FFFFFF", True, width=126, anchor="middle", role="diagram")
        s.rect(x, 574, 140, 96, PALE, LINE, 0)
        for line_index, line in enumerate(item["lines"]):
            yy = 590 + line_index * 19
            icon = s.icon(ICONS[(i * 4 + line_index) % len(ICONS)], x + 8, yy - 10, 15, BLUE)
            icon.set("data-role", "action-body-icon")
            s.text(x + 29, yy, line, 12, INK, width=102, max_lines=1, role="diagram")
        if i < 2:
            _solid_arrow(s, x + 141, 608, x + 153, 18, BLUE, "solid-stage-arrow")
    _solid_arrow(s, 1104, 608, 1138, 18, BLUE, "solid-stage-arrow")
    s.circle(1184, 610, 45, "#FFFFFF", BLUE, stroke_width=3)
    s.icon("users", 1171, 589, 26, BLUE)
    s.text(1184, 598, result_title, 12.5, BLUE, True, width=78, anchor="middle", max_lines=1, role="diagram")
    s.text(1184, 627, "\n".join(d["result_lines"]), 12, INK, width=76, anchor="middle", leading=15, max_lines=2, role="diagram")
    _arc_arrow(s, 1184, 610, 55, -2.5, -0.35, BLUE, 2.2)
    _arc_arrow(s, 1184, 610, 55, 0.55, 2.65, BLUE, 2.2)
    _curve_arrow(
        s,
        "M1150 665 C1040 700 805 700 730 672 L730 660",
        730,
        660,
        730,
        672,
        BLUE,
        1.8,
        True,
        "voice-return-arrow",
    )
    return s.finish()


def render_r18(content):
    d = _content("R18", content)
    s = MechanismSvg()
    s.title(d["title"], d["subtitle"], 34, color="#10131D")
    step_w = 166
    for i, item in enumerate(d["steps"]):
        x = 48 + i * 174
        s.number(x, 118, str(i + 1), 11)
        s.icon(item["icon"], x + 39, 104, 34, BLUE, disc=True)
        s.text(x + 77, 158, item["name"], 12, BLUE, True, width=step_w - 10, anchor="middle", max_lines=2, role="diagram")
        s.bullets(x + 8, 188, item["questions"], step_w - 16, 10.2, 2)
        if i < 6:
            s.arrow(x + 164, 120, x + 140, 120, BLUE, 2)
    s.rect(20, 270, 345, 342, "#FFFFFF", "#7D90AA", 0, stroke_dasharray="7 5", data_role="dashed-system-frame")
    s.header(20, 270, 345, d["forward"]["title"], 28, BLUE, 14)
    for i, item in enumerate(d["forward"]["nodes"]):
        x = 48 + i * 77
        s.icon(item["icon"], x, 315, 28, BLUE, disc=True)
        s.text(x + 14, 370, item["name"], 12, BLUE, True, width=68, anchor="middle", max_lines=1, role="diagram")
        _stacked_text(s, x + 14, 390, item["note"], 68, 12, MUTED, anchor="middle", max_lines=3)
        if i < 3:
            s.arrow(x + 38, 330, x + 62, 330, BLUE, 1.5)
    s.rect(36, 458, 313, 138, "#F1F4F8", "none", 0, data_role="system-summary-strip")
    s.bullets(50, 482, d["forward"]["points"], 280, 12, 9)
    s.poly([(365, 406), (390, 441), (365, 476)], BLUE)
    s.rect(390, 255, 500, 370, "#FFFFFF", LINE, 0, stroke_width=1.8, data_role="document-paper")
    s.header(
        390,
        255,
        500,
        f"{d['document']['label']}｜{d['document']['title']}",
        32,
        BLUE,
        14,
    )
    for i, item in enumerate(d["document"]["facts"]):
        _icon_label(
            s,
            item["icon"],
            410,
            303 + i * 59,
            item["name"],
            item["value"],
            220,
            11.5,
            False,
        )
    for i, q in enumerate(d["document"]["questions"]):
        s.text(650, 310 + i * 59, f"Q{i + 1}  {q}", 15, BLUE, True, width=215, max_lines=2, role="body")
        s.line(650, 346 + i * 59, 855, 346 + i * 59, LINE, 1, True)
    s.poly([(890, 406), (915, 441), (890, 476)], BLUE)
    s.rect(915, 270, 345, 342, "#FFFFFF", "#7D90AA", 0, stroke_dasharray="7 5", data_role="dashed-system-frame")
    s.header(915, 270, 345, d["backward"]["title"], 28, BLUE, 14)
    for i, item in enumerate(d["backward"]["nodes"]):
        x = 943 + i * 77
        s.icon(item["icon"], x, 315, 28, BLUE, disc=True)
        s.text(x + 14, 370, item["name"], 12, BLUE, True, width=68, anchor="middle", max_lines=1, role="diagram")
        _stacked_text(s, x + 14, 390, item["note"], 68, 12, MUTED, anchor="middle", max_lines=3)
        if i < 3:
            s.arrow(x + 38, 330, x + 62, 330, BLUE, 1.5)
    s.rect(931, 458, 313, 138, "#EAF1FA", "none", 0, data_role="system-summary-strip")
    s.bullets(945, 482, d["backward"]["points"], 280, 12, 9)
    s.header(20, 636, 140, "决策门", 62, BLUE, 18)
    s.rect(160, 636, 1100, 62, "#EDF3FA", LINE, 0, data_role="continuous-gate-track")
    for i, gate in enumerate(d["gates"]):
        x = 182 + i * 177
        s.poly([(x, 667), (x + 29, 638), (x + 58, 667), (x + 29, 696)], BLUE)
        s.text(x + 29, 672, f"G{i + 1}", 12, "#FFFFFF", True, anchor="middle", role="diagram")
        s.text(x + 66, 653, gate["name"], 12, BLUE, True, width=100, max_lines=1, role="diagram")
        rule = gate["rule"]
        if len(wrap(rule, 100, 15)) > 1 and " " in rule:
            prefix, qualifier = rule.split(" ", 1)
            if any(len(wrap(part, 100, 15)) > 1 for part in (prefix, qualifier)):
                raise ValueError("R18 gate rule exceeds the fixed two-line capacity")
            rule = prefix + "\n" + qualifier
        rule_lines = wrap(rule, 100, 15)
        if len(rule_lines) > 1 and len(rule_lines[-1].strip()) == 1:
            raise ValueError("R18 gate rule leaves a single-character line; use a shorter complete rule")
        s.text(x + 66, 672, rule, 15, MUTED, width=100, max_lines=2, role="body")
        if i < len(d["gates"]) - 1:
            s.arrow(x + 168, 667, x + 175, 667, MUTED, 1.2, True)
    return s.finish()


def render_r19(content):
    d = _content("R19", content)
    s = MechanismSvg()
    s.title(d["title"], d["subtitle"], 35, color="#10131D")
    _panel(s, 20, 105, 300, 500, d["compare_title"])
    for i, row in enumerate(d["comparison"]):
        y = 155 + i * 135
        s.rect(32, 140 + i * 150, 276, 150, "#FFFFFF" if i % 2 == 0 else "#F5F7FA", LINE, 0, data_role="continuous-comparison-row")
        _icon_label(
            s,
            ICONS[i + 3],
            38,
            y,
            row["linear"],
            " / ".join(row["linear_points"]),
            125,
            12,
        )
        s.arrow(166, y + 22, 190, y + 22, MID, 2)
        s.text(205, y + 15, row["system"], 12, BLUE, True, width=95, role="diagram")
        s.text(205, y + 39, " / ".join(row["system_points"]), 15, MUTED, width=95, role="body")
    cx, cy, radius = 650, 345, 220
    for i, item in enumerate(d["flywheel"]):
        a = -math.pi / 2 + i * 2 * math.pi / 8
        b = -math.pi / 2 + (i + 1) * 2 * math.pi / 8
        x, y = cx + radius * math.cos(a), cy + radius * math.sin(a)
        _arc_arrow(s, cx, cy, radius - 4, a + 0.12, b - 0.12, BLUE, 4.5, role="flywheel-arc")
        s.number(x, y, str(i + 1), 13)
        icon_y = y + (55 if i == 0 else 22)
        driver_y = y + (30 if i == 0 else (22 if i == 1 else (23 if i == 4 else 8)))
        s.icon(item["icon"], x - 10, icon_y, 20, MID)
        label_x = x if i == 4 else x + (18 if x < cx else -18)
        label_y = y + (2 if i == 1 else (-30 if i == 4 else -12))
        label_anchor = "middle" if i == 4 else ("start" if x < cx else "end")
        s.text(
            label_x,
            label_y,
            item["name"],
            12,
            BLUE,
            True,
            width=118,
            anchor=label_anchor,
            role="diagram",
        )
        s.text(
            label_x,
            driver_y,
            item["driver"],
            15,
            MUTED,
            width=118,
            anchor=label_anchor,
            max_lines=2,
            role="body",
        )
    s.circle(cx, cy, 68, BLUE)
    s.text(
        cx,
        cy - 10,
        d["center"],
        16,
        "#FFFFFF",
        True,
        width=115,
        anchor="middle",
        leading=20,
    )
    upper, lower = d["inner_loops"]
    _curve_arrow(s, "M590 309 C548 214 748 212 710 311", 710, 311, 748, 212, MID, 1.8, True)
    s.rect(557, 226, 186, 49, "#FFFFFF", "none", 2)
    s.text(650, 239, upper["name"], 12, BLUE, True, width=165, anchor="middle", max_lines=1, role="diagram")
    s.text(650, 257, upper["note"], 15, MUTED, width=175, anchor="middle", max_lines=2, role="body")
    _curve_arrow(s, "M710 381 C752 480 548 482 590 381", 590, 381, 548, 482, MID, 1.8, True)
    s.rect(557, 431, 186, 49, "#FFFFFF", "none", 2)
    s.text(650, 444, lower["name"], 12, BLUE, True, width=165, anchor="middle", max_lines=1, role="diagram")
    s.text(650, 462, lower["note"], 15, MUTED, width=175, anchor="middle", max_lines=2, role="body")
    _panel(s, 980, 105, 282, 500, d["levers_title"])
    for i, item in enumerate(d["levers"]):
        y = 137 + i * 112
        s.rect(994, y, 254, 112, "#FFFFFF" if i % 2 == 0 else PALE, LINE, 0, data_role="continuous-lever-row")
        s.icon(item["icon"], 1006, y + 17, 36, "#FFFFFF", disc=True, disc_color=BLUE)
        s.text(1058, y + 29, item["name"], 15, BLUE, True, width=174, max_lines=1)
        for line_index, line in enumerate(item["effects"]):
            s.text(1058, y + 49 + line_index * 16, f"• {line}", 12, INK, width=174, max_lines=1, role="diagram")
        s.text(1058, y + 103, "待验：" + item["hypothesis"], 15, MUTED, width=174, max_lines=1, role="body")
    parts = d["formula"]
    for i, part in enumerate(parts):
        x = 25 + i * 305
        fill = BLUE if i == len(parts) - 1 else "#FFFFFF"
        stroke = BLUE if i == len(parts) - 1 else LINE
        s.rect(x, 624, 270, 72, fill, stroke, 2, data_role="formula-result" if i == len(parts) - 1 else "formula-factor")
        s.icon(part["icon"], x + 12, 642, 28, "#FFFFFF" if i == len(parts) - 1 else BLUE)
        s.text(x + 50, 648, part["name"], 12, "#FFFFFF" if i == len(parts) - 1 else BLUE, True, width=205, role="diagram")
        s.text(x + 50, 674, " / ".join(part["lines"]), 12, "#FFFFFF" if i == len(parts) - 1 else INK, width=205, role="diagram")
        if i < len(parts) - 1:
            s.text(x + 287, 671, "×" if i < 2 else "=", 28, BLUE, True, anchor="middle")
    return s.finish()


def render_r20(content):
    d = _content("R20", content)
    s = MechanismSvg()
    s.title(d["title"], d["subtitle"], 35, color="#10131D")
    for i, item in enumerate(d["steps"]):
        s.ribbon(72 + i * 238, 100, 220, 44, item["name"], str(i + 1), size=15)
        icon = s.icon(["search", "database", "users", "wrench", "file-text"][i], 82 + i * 238, 153, 28, BLUE)
        icon.set("data-role", "process-step-icon")
        _stacked_text(
            s,
            120 + i * 238,
            166,
            "\n".join(item["notes"]),
            164,
            15,
            INK,
            leading=18,
            max_lines=2,
            role="body",
        )
    x, y, w, h = 130, 218, 1115, 448
    s.arrow(x - 20, y + h, x - 20, y, BLUE, 2)
    s.arrow(x, y + h + 10, x + w, y + h + 10, BLUE, 2)
    s.text(42, 244, "影响程度", 14, BLUE, True, role="diagram")
    s.text(58, 330, "高", 16, BLUE, True)
    s.text(58, 575, "低", 16, BLUE, True)
    s.text(x + w / 2, 690, "可逆性", 15, BLUE, True, anchor="middle")
    s.text(x + 70, 698, "不可逆", 12, INK, role="diagram")
    s.text(x + w - 100, 698, "可逆", 12, INK, role="diagram")
    cell_w, cell_h = (w - 12) / 2, (h - 12) / 2
    s.rect(x + cell_w + 4.5, y, 3, h, BLUE, "none", 0, data_role="shared-matrix-axis")
    s.rect(x, y + cell_h + 4.5, w, 3, BLUE, "none", 0, data_role="shared-matrix-axis")
    for i, q in enumerate(d["quadrants"]):
        xx = x + (i % 2) * (cell_w + 12)
        yy = y + (i // 2) * (cell_h + 12)
        gutter_w = 29
        s.table(
            f"r20-q{i + 1}",
            xx + gutter_w,
            yy,
            cell_w - gutter_w,
            cell_h,
            [q["name"], "建议"],
            [[r["field"], r["value"]] for r in q["rows"]],
            [0.25, 0.75],
            9.5,
        )
        row_h = cell_h / 6
        for row_index, icon_name in enumerate(["box", "users", "search", "alarm-clock", "refresh-ccw"]):
            icon = s.icon(icon_name, xx + 6, yy + row_h * (row_index + 1) + row_h / 2 - 8, 16, BLUE)
            icon.set("data-role", "matrix-row-icon")
    return s.finish()


def render_r21(content):
    d = _content("R21", content)
    s = MechanismSvg()
    s.title(d["title"], d["subtitle"], 34, color="#10131D")
    s.text(640, 96, d["model"], 16, BLUE, True, anchor="middle")
    _panel(s, 26, 124, 548, 266, d["before_title"])
    _panel(s, 706, 124, 548, 266, d["after_title"])
    for phase, start_x in ((d["before"], 38), (d["after"], 718)):
        for i, item in enumerate(phase):
            x = start_x + i * 132
            s.rect(x, 164, 122, 205, "#FFFFFF", LINE, 2)
            s.number(x + 17, 179, str(i + 1), 10)
            s.icon(item["icon"], x + 41, 178, 32, "#FFFFFF", disc=True, disc_color=BLUE)
            s.text(x + 61, 241, item["name"], 12, BLUE, True, width=108, anchor="middle", max_lines=2, role="diagram")
            for line_index, line in enumerate(item["lines"]):
                s.text(x + 3, 274 + line_index * 22, line, 15, INK, width=116, max_lines=1, role="body")
            if i < 3:
                s.arrow(x + 122, 266, x + 132, 266, BLUE, 1.8)
    s.poly(
        [(610, 124), (670, 124), (690, 257), (670, 390), (610, 390), (590, 257)], BLUE
    )
    s.icon("scale", 616, 174, 48, "#FFFFFF")
    s.text(640, 270, "决策关口", 15, "#FFFFFF", True, anchor="middle")
    s.text(640, 297, "基于证据授权", 15, "#FFFFFF", anchor="middle", role="body")
    _panel(s, 26, 396, 548, 130, d["bad_path"]["title"], fill="#F6F7F9", color="#5F7392")
    _panel(s, 706, 396, 548, 130, d["good_path"]["title"])
    for path, start_x, color in ((d["bad_path"], 40, "#7084A3"), (d["good_path"], 720, BLUE)):
        for i, item in enumerate(path["nodes"]):
            x = start_x + i * 130
            s.rect(x, 438, 118, 70, "#FFFFFF", color, 1, data_role="path-node-panel")
            s.icon(item["icon"], x + 8, 451, 25, color)
            s.text(x + 41, 472, item["name"], 12, color, True, width=68, max_lines=2, role="diagram")
            if i < 3:
                _solid_arrow(s, x + 118, 473, x + 130, 13, color)
    s.circle(640, 462, 28, BLUE)
    s.text(640, 468, "VS", 13, "#FFFFFF", True, anchor="middle", role="diagram")
    s.header(26, 547, 110, "四项规则", 135, BLUE, 17)
    for i, item in enumerate(d["rules"]):
        x = 150 + i * 277
        s.rect(x, 558, 266, 112, "#FFFFFF", LINE, 0)
        s.icon(item["icon"], x + 12, 574, 42, "#FFFFFF", disc=True, disc_color=BLUE)
        s.text(x + 70, 588, f"{i + 1}. {item['name']}", 15, BLUE, True, width=180, max_lines=1)
        for line_index, line in enumerate(item["lines"]):
            yy = 616 + line_index * 23
            s.circle(x + 75, yy - 4, 3.5, BLUE, data_role="rule-line")
            s.text(x + 87, yy, line, 15, INK, width=158, max_lines=1, role="body")
    s.poly(
        [(26, 686), (42, 672), (1238, 672), (1254, 686), (1238, 700), (42, 700)],
        BLUE,
        data_role="arrow-closing-band",
    )
    s.text(640, 692, d["closing"], 15, "#FFFFFF", True, width=1160, anchor="middle", role="body")
    return s.finish()


def render_r22(content):
    d = _content("R22", content)
    s = MechanismSvg()
    s.title(d["title"], d["subtitle"], 35, color="#10131D")
    for i, item in enumerate(d["chain"]):
        x = 24 + i * 207
        _mini_card(
            s,
            x,
            110,
            192,
            125,
            item["name"],
            [item["artifact"], "Owner: " + item["owner"]],
            item["icon"],
            "#FFFFFF",
        )
        if i < 5:
            s.arrow(x + 192, 210, x + 207, 210, BLUE, 2)
    s.line(55, 247, 1230, 247, BLUE, 4)
    for i in range(6):
        s.circle(120 + i * 207, 247, 8, BLUE)
    s.header(24, 274, 150, "单线程责任链", 138, BLUE, 17)
    s.header(24, 426, 150, "矩阵式漂移", 138, "#6983A8", 17)
    lane_start, lane_end = 210, 1240
    s.rect(lane_start, 274, lane_end - lane_start, 138, "#EEF4FA", LINE, 0, data_role="swimlane-background")
    s.rect(lane_start, 426, lane_end - lane_start, 138, "#F3F5F8", LINE, 0, data_role="swimlane-background")
    for i in range(1, 6):
        xx = lane_start + i * (lane_end - lane_start) / 6
        s.rect(xx, 278, 1, 130, LINE, "none", 0, data_role="swimlane-divider")
        s.rect(xx, 430, 1, 130, LINE, "none", 0, data_role="swimlane-divider")
    s.arrow(lane_start, 310, lane_end, 310, BLUE, 2.4)
    for i, item in enumerate(d["chain"]):
        x = 185 + i * 176
        s.circle(x + 78, 310, 8, BLUE)
        s.text(x + 78, 345, item["result"], 12, BLUE, True, width=145, anchor="middle", role="diagram")
        for line_index, line in enumerate(item["result_lines"]):
            s.text(x + 78, 369 + line_index * 22, line, 15, INK, anchor="middle", role="body")
        s.circle(x + 78, 458, 8, "#B7C3D3")
        s.text(x + 78, 485, item["drift"], 12, MUTED, True, width=145, anchor="middle", role="diagram")
        for line_index, line in enumerate(item["drift_lines"]):
            s.text(x + 78, 509 + line_index * 22, line, 15, MUTED, anchor="middle", role="body")
        if i < 5:
            source_x, target_x = x + 78, x + 254
            left_gutter, right_gutter = source_x + 76, target_x - 76
            s.path(
                f"M{source_x + 8} 458 L{left_gutter} 468 L{left_gutter} 554 "
                f"L{right_gutter} 468 L{target_x - 8} 458",
                stroke="#A8B4C5",
                width=1.35,
                dashed=True,
            )
            s.path(
                f"M{source_x + 8} 458 L{left_gutter} 468 L{right_gutter} 554 "
                f"L{right_gutter} 468 L{target_x - 8} 458",
                stroke="#A8B4C5",
                width=1.35,
                dashed=True,
            )
    _panel(s, 24, 566, 1238, 97, d["charter_title"])
    for i, item in enumerate(d["charter"]):
        x = 34 + i * 245
        s.rect(x, 594, 238, 62, "#FFFFFF", LINE, 0, data_role="charter-column")
        s.icon(item["icon"], x + 10, 602, 18, "#FFFFFF", disc=True, disc_color=BLUE)
        s.text(x + 44, 612, item["name"], 12, BLUE, True, width=188, max_lines=1, role="diagram")
        for line_index, line in enumerate(item["lines"]):
            s.text(x + 44, 632 + line_index * 18, line, 15, INK, width=188, max_lines=1, role="body")
    s.band(d["closing"], 674, 26)
    return s.finish()


def render_r23(content):
    d = _content("R23", content)
    expected_counts = (8, 20)
    resolved_counts = []
    for index, spec in enumerate(d["networks"]):
        raw_count = spec["count"]
        if isinstance(raw_count, str):
            normalized = raw_count.strip()
            if normalized.endswith("人"):
                normalized = normalized[:-1].strip()
            if not normalized.isdigit():
                raise ValueError(f"R23 network {index + 1} people count must be an integer or '<n>人'")
            raw_count = int(normalized)
        if isinstance(raw_count, bool) or not isinstance(raw_count, int):
            raise ValueError(f"R23 network {index + 1} people count must be an integer or '<n>人'")
        resolved_counts.append(raw_count)
    neutral_networks = all(not spec["label"].strip() for spec in d["networks"])
    if resolved_counts == [0, 0] and neutral_networks:
        # Component extraction blanks unrelated business fields; node counts are fixed
        # structural slots and may be restored without introducing business facts.
        resolved_counts = list(expected_counts)
    if tuple(resolved_counts) != expected_counts:
        raise ValueError(
            f"R23 fixed network slots require 8 and 20 people; received {resolved_counts[0]} and {resolved_counts[1]}"
        )
    s = MechanismSvg()
    s.title(d["title"], d["subtitle"], 35, color="#10131D")
    _panel(s, 18, 104, 400, 334, d["formula_title"])
    s.text(90, 190, d["formula"], 34, BLUE, True)
    s.text(255, 185, d["formula_note"], 15, INK, width=150, max_lines=3, role="body")
    for i, metric in enumerate(d["metrics"]):
        x = 38 + i * 195
        s.rect(x, 247, 160, 142, "#FFFFFF", BLUE if i else "#7187A8", 0)
        s.icon("users", x + 12, 261, 34, BLUE if i else "#7187A8")
        s.text(x + 55, 278, metric["name"], 12, BLUE, True, width=92, role="diagram")
        s.text(x + 80, 341, metric["value"], 38, BLUE, True, anchor="middle", width=145)
        s.text(x + 80, 374, metric["calc"], 12, MUTED, anchor="middle", role="diagram")
    s.circle(218, 318, 22, BLUE)
    s.text(218, 323, "VS", 12, "#FFFFFF", True, anchor="middle", role="diagram")
    s.rect(36, 397, 365, 28, BLUE, "none", 0)
    s.text(218, 416, d["formula_note"], 12, "#FFFFFF", True, width=340, anchor="middle", role="diagram")
    _panel(s, 438, 104, 360, 334, d["network_title"])
    for network_index, (offset, spec, count) in enumerate(
        [(0, d["networks"][0], resolved_counts[0]), (180, d["networks"][1], resolved_counts[1])]
    ):
        cx, cy = 528 + offset, 252
        edge_count = count * (count - 1) // 2
        count_label = f"{count} 人｜{edge_count} 条关系"
        s.rect(cx - 82, 141, 164, 27, BLUE if offset else "#7187A8", "none", 0, data_role="network-header")
        s.text(cx, 160, count_label, 12, "#FFFFFF", True, width=150, anchor="middle", role="diagram")
        positions = [
            (
                cx + 76 * math.cos(i * 2 * math.pi / count),
                cy + 76 * math.sin(i * 2 * math.pi / count),
            )
            for i in range(count)
        ]
        edge_path = " ".join(
            f"M{positions[i][0]:.1f} {positions[i][1]:.1f} L{positions[j][0]:.1f} {positions[j][1]:.1f}"
            for i in range(count)
            for j in range(i + 1, count)
        )
        edge_group = s.path(edge_path, stroke="#A9B8CB", width=0.45)
        edge_group.set("data-role", "communication-network-edges")
        edge_group.set("data-network-index", str(network_index))
        edge_group.set("data-edge-count", str(edge_count))
        for x, y in positions:
            node = s.circle(x, y, 7, BLUE)
            node.set("data-role", "communication-network-node")
            node.set("data-network-index", str(network_index))
            s.icon("users", x - 5, y - 5, 10, "#FFFFFF")
        s.rect(cx - 82, 360, 164, 50, PALE, LINE, 0)
        s.text(cx, 380, spec["label"], 12, BLUE, True, anchor="middle", width=150, role="diagram")
        s.text(cx, 400, "连接数随团队规模快速增加", 12, MUTED, anchor="middle", width=150, role="diagram")
    _panel(s, 818, 104, 444, 334, d["behavior_title"])
    for side, (title, rows, color) in enumerate(
        [
            (d["large_title"], d["large_rows"], "#7187A8"),
            (d["small_title"], d["small_rows"], BLUE),
        ]
    ):
        x = 830 + side * 214
        s.header(x, 137, 204, title, 29, color, 12)
        for i, row in enumerate(rows):
            _icon_label(
                s,
                row["icon"],
                x + 8,
                180 + i * 59,
                row["name"],
                row["note"],
                190,
                10,
                False,
                color,
            )
    _panel(s, 18, 452, 1244, 195, d["canvas_title"])
    for i, item in enumerate(d["canvas"]):
        x = 30 + i * 204
        s.rect(x, 494, 194, 130, PALE, LINE, 4)
        s.icon(item["icon"], x + 10, 504, 25, BLUE)
        s.text(x + 43, 520, f"{i + 1}. {item['name']}", 13, BLUE, True, width=140, role="diagram")
        s.text(x + 10, 544, item["question"], 15, INK, True, width=174, role="body")
        for line_index, line in enumerate(item["lines"]):
            s.text(x + 10, 569 + line_index * 19, line, 15, INK, width=174, max_lines=1, role="body")
    principle_label_w = 120
    principle_start = 154
    principle_column_w = (1262 - principle_start) / 5
    s.header(18, 657, principle_label_w, "设计原则", 28, BLUE, 14)
    for i, p in enumerate(d["principles"]):
        x = principle_start + principle_column_w * (i + 0.5)
        icon = s.icon(["target", "database", "scale", "handshake", "shield-check"][i], x - 12, 648, 24, BLUE)
        icon.set("data-role", "principle-icon")
        s.text(x, 680, p["name"], 12, BLUE, True, anchor="middle", role="diagram")
        s.text(x, 699, p["note"], 15, MUTED, anchor="middle", width=200, max_lines=1, role="body")
    return s.finish()


def render_r24(content):
    d = _content("R24", content)
    s = MechanismSvg()
    s.title(d["title"], d["subtitle"], 35, color="#10131D")
    # Original uses downward-nested half ellipses: each outer scope visibly contains the inner one.
    x0, y0 = 35, 120
    fills = ["#EEF3F9", "#DFE9F5", "#C9D9EC", "#AFC6E1", "#7297C2", BLUE]
    for i, scope in enumerate(d["scopes"]):
        w = 425 - i * 58
        h = 317 - i * 40
        x = x0 + i * 29
        y = y0 + i * 40
        s.path(
            f"M{x} {y + h} A{w / 2} {h} 0 0 1 {x + w} {y + h} L{x + w} {y + h + 2} L{x} {y + h + 2} Z",
            fill=fills[i],
            stroke="#FFFFFF",
            width=1.5,
        )
    for i, scope in enumerate(d["scopes"]):
        # Paint labels after every layer so inner fills cannot cover outer labels.
        color = "#FFFFFF" if i > 3 else BLUE
        s.text(
            247,
            136 + i * 40,
            f"{scope['english']}｜{scope['chinese']}",
            12,
            color,
            True,
            anchor="middle",
            width=230,
            max_lines=1,
            role="diagram",
        )
        s.root[-1].set("data-layout-role", "scope-name")
        s.text(
            247,
            151 + i * 40,
            scope["note"],
            12,
            color,
            anchor="middle",
            width=230,
            max_lines=1,
            role="diagram",
        )
        s.root[-1].set("data-layout-role", "scope-explanation")
    s.arrow(486, 185, 486, 430, BLUE, 3)
    s.text(495, 270, "责任边界\n向外延伸", 12, BLUE, True, width=38, leading=18, role="diagram")
    s.table(
        "r24-mindset",
        535,
        120,
        718,
        345,
        d["mindset_columns"],
        d["mindset_rows"],
        [0.22, 0.39, 0.39],
        10,
        column_styles=[{"margin_left_pt": 24}],
    )
    for i, icon_name in enumerate(["alarm-clock", "search", "database", "scale", "shield-check"]):
        icon = s.icon(icon_name, 543, 194 + i * 57.5, 24, BLUE)
        icon.set("data-role", "mindset-row-icon")
    _panel(s, 20, 490, 780, 205, d["journey_title"])
    for i, item in enumerate(d["journey"]):
        x = 35 + i * 125
        s.poly(
            [(x, 527), (x + 112, 527), (x + 128, 548), (x + 112, 570), (x, 570)],
            "#FFFFFF",
            LINE,
            stroke_width=1,
        )
        icon = s.icon(ICONS[i], x + 10, 536, 24, BLUE)
        icon.set("data-role", "journey-step-icon")
        s.text(x + 74, 553, f"{i + 1}. {item['name']}", 12, BLUE, True, anchor="middle", role="diagram")
        for line_index, line in enumerate(item["actions"]):
            s.text(x + 9, 590 + line_index * 21, f"• {line}", 12, INK, role="diagram")
    s.poly(
        [(35, 657), (765, 657), (788, 674), (765, 691), (35, 691)],
        "#DDE9F7",
        BLUE,
        stroke_width=1,
        data_role="journey-direction-band",
    )
    s.text(400, 679, "视野扩大 → 主动识别 → 构建方案 → 执行度量 → 沉淀复制", 12, BLUE, True, anchor="middle", role="diagram")
    _panel(s, 825, 490, 428, 205, d["checklist_title"])
    for i, item in enumerate(d["checklist"]):
        y = 527 + i * 30
        s.rect(840, y, 17, 17, "#FFFFFF", BLUE, 0)
        s.icon(item["icon"], 867, y - 3, 23, BLUE)
        s.text(899, y + 12, item["question"], 15, INK, width=205, role="body")
        s.text(1115, y + 12, item["check"], 12, MUTED, width=120, role="diagram")
    s.header(838, 674, 402, d["checklist_note"], 18, BLUE, 12)
    return s.finish()


def render_r25(content):
    d = _content("R25", content)
    s = MechanismSvg()
    s.title(d["title"], d["subtitle"], 34, color="#10131D")
    stage_boxes = {
        "input": (25, 145, 195, 36, 42),
        "owner": (230, 145, 150, 36, 42),
        "experience": (415, 150, 180, 43, 51),
        "behavior": (620, 150, 180, 43, 51),
        "output": (825, 160, 180, 49, 64),
        "financial": (1030, 150, 220, 55, 64),
    }
    for x, w, label in [
        (25, 355, "Input｜可控投入"),
        (415, 180, "Experience｜客户体验"),
        (620, 180, "Behavior｜客户行为"),
        (825, 180, "Output｜业务产出"),
        (1030, 220, "Financial Result｜结果"),
    ]:
        s.ribbon(x, 100, w, 30, label, color=BLUE, size=12)
    for start, end in [(380, 415), (595, 620), (800, 825), (1005, 1030)]:
        s.arrow(start + 5, 115, end - 5, 115, BLUE, 1.6)
    s.text(35, 142, "投入因子", 12, BLUE, True, role="diagram")
    s.text(240, 142, "主要 Owner / 工件", 12, BLUE, True, role="diagram")
    bounds = {}
    groups = {
        "input": d["input_factors"],
        "owner": d["owners"],
        "experience": d["experience"],
        "behavior": d["behavior"],
        "output": d["output"],
        "financial": d["financial"],
    }
    for group, items in groups.items():
        x, y0, w, h, step = stage_boxes[group]
        for index, _item in enumerate(items):
            bounds[(group, index)] = (x, y0 + index * step, w, h)
    for edge in d["network_edges"]:
        source = bounds[(edge["from"][0], edge["from"][1])]
        target = bounds[(edge["to"][0], edge["to"][1])]
        s.arrow(
            source[0] + source[2],
            source[1] + source[3] / 2,
            target[0],
            target[1] + target[3] / 2,
            "#9AA8BA" if edge.get("indirect") else BLUE,
            0.8 if edge.get("indirect") else 1.3,
            edge.get("indirect", False),
        )
    fx, fy, fw, fh, fstep = stage_boxes["financial"]
    s.rect(fx, fy, fw, fstep * len(d["financial"]), "#FFFFFF", BLUE, 6, stroke_width=2)
    for index in range(1, len(d["financial"])):
        s.line(
            fx + 12, fy + index * fstep, fx + fw - 12, fy + index * fstep, LINE, 1, True
        )
    for group, items in groups.items():
        for index, item in enumerate(items):
            x, y, w, h = bounds[(group, index)]
            if group == "financial":
                s.icon(item["icon"], x + w / 2 - 14, y + 5, 28, BLUE)
                s.text(
                    x + w / 2,
                    y + 49,
                    item["name"],
                    12.5,
                    BLUE,
                    True,
                    anchor="middle",
                    width=w - 24,
                    role="diagram",
                )
                continue
            dark = group == "input"
            if dark:
                s.poly(
                    [(x, y), (x + w - 16, y), (x + w, y + h / 2), (x + w - 16, y + h), (x, y + h)],
                    BLUE,
                    data_role="input-arrow-node",
                )
            else:
                s.rect(x, y, w, h, PALE, LINE, 3)
            if group != "owner":
                s.icon(item["icon"], x + 7, y + 7, 22, "#FFFFFF" if dark else BLUE)
                text_x = x + 35
            else:
                text_x = x + 9
            s.text(
                text_x,
                y + 16,
                item["name"],
                12.5,
                "#FFFFFF" if dark else BLUE,
                True,
                width=w - (text_x - x) - 6,
                role="diagram",
            )
            if item.get("note"):
                s.text(
                    text_x,
                    y + 31,
                    item["note"],
                    10.5,
                    "#FFFFFF" if dark else MUTED,
                    width=w - (text_x - x) - 6,
                    role="body",
                )
    s.table(
        "r25-metrics",
        25,
        430,
        1226,
        250,
        d["table_columns"],
        d["table_rows"],
        [0.13, 0.18, 0.23, 0.09, 0.13, 0.11, 0.13],
        9.8,
        column_styles=[{"body_fill": BLUE, "text_color": "#FFFFFF", "bold": True}],
    )
    s.text(26, 696, d["footnote"], 11, MUTED, width=1200, role="source")
    return s.finish()


def render_r26(content):
    d = _content("R26", content)
    s = MechanismSvg()
    s.title(d["title"], d["subtitle"], 35, color="#10131D")
    _panel(s, 25, 100, 375, 480, d["matrix_title"])
    quad_colors = [BLUE, "#1F5B9E", "#7094BE", "#A8BED8"]
    quad_icons = ["lightbulb", "box", "file-text", "wrench"]
    for i, item in enumerate(d["quadrants"]):
        x = 58 + (i % 2) * 160
        y = 150 + (i // 2) * 176
        s.rect(x, y, 148, 164, quad_colors[i], "#FFFFFF", 1)
        icon = s.icon(quad_icons[i], x + 12, y + 12, 34, "#FFFFFF")
        icon.set("data-role", "strong-quadrant-icon")
        s.text(x + 55, y + 35, item["name"], 12, "#FFFFFF", True, width=82, max_lines=2, role="diagram")
        for line_index, line in enumerate(item["lines"]):
            s.text(x + 14, y + 75 + line_index * 22, f"• {line}", 12, "#FFFFFF", role="diagram")
    s.arrow(58, 493, 366, 493, BLUE, 1.5)
    s.arrow(49, 474, 49, 145, BLUE, 1.5)
    s.text(210, 516, "方案不确定性 →", 12, BLUE, True, anchor="middle", role="diagram")
    s.text(10, 322, "客户", 12, BLUE, True, role="diagram")
    s.text(10, 340, "价值", 12, BLUE, True, role="diagram")
    s.text(55, 544, d["matrix_note"], 12, MUTED, width=320, leading=15, role="diagram")
    _panel(s, 420, 100, 440, 480, d["cycle_title"])
    cx, cy = 640, 330
    boxes = [
        (572, 137),
        (704, 215),
        (704, 395),
        (572, 475),
        (440, 395),
        (440, 215),
    ]
    for i, (item, (x, y)) in enumerate(zip(d["cycle"], boxes)):
        _mini_card(
            s,
            x,
            y,
            136,
            78,
            f"{i + 1}. {item['name']}",
            [item["artifact"], item["note"]],
            item["icon"],
            "#FFFFFF",
        )
    _curve_arrow(s, "M708 174 C748 174 779 189 790 215", 790, 215, 779, 189, BLUE, 2)
    _curve_arrow(s, "M840 293 C855 322 855 371 840 395", 840, 395, 855, 371, BLUE, 2)
    _curve_arrow(s, "M772 473 C750 506 723 516 708 516", 708, 516, 723, 516, BLUE, 2)
    _curve_arrow(s, "M572 516 C535 516 488 506 470 473", 470, 473, 488, 506, BLUE, 2)
    _curve_arrow(s, "M440 434 C422 398 422 287 440 254", 440, 254, 422, 287, BLUE, 2)
    _curve_arrow(s, "M508 215 C525 188 548 174 572 174", 572, 174, 548, 174, BLUE, 2, True)
    s.poly(
        [(cx, cy - 48), (cx + 48, cy), (cx, cy + 48), (cx - 48, cy)],
        "#FFFFFF",
        BLUE,
        stroke_width=2,
    )
    s.text(cx, cy - 4, d["decision"], 12, BLUE, True, width=75, anchor="middle", role="diagram")
    _curve_arrow(s, "M640 282 L640 240 L576 240", 576, 240, 592, 240, BLUE, 1.8)
    s.text(640, 228, "是｜放大/终止", 12, BLUE, True, width=112, anchor="middle", max_lines=1, role="diagram")
    s.root[-1].set("data-layout-role", "decision-branch-label")
    s.root[-1].set("data-clearance", "dedicated")
    s.arrow(cx - 35, cy + 35, 576, 414, MID, 1.8)
    s.text(535, 389, "否｜学习回流", 12, MID, True, width=96, anchor="middle", max_lines=1, role="diagram")
    s.root[-1].set("data-layout-role", "decision-branch-label")
    s.root[-1].set("data-clearance", "dedicated")
    _panel(s, 880, 100, 375, 480, d["metrics_title"])
    for i, item in enumerate(d["metrics"]):
        y = 145 + i * 98
        s.rect(900, y, 75, 75, BLUE, "none", 2)
        s.icon(item["icon"], 919, y + 19, 37, "#FFFFFF")
        s.text(995, y + 22, item["name"], 13, BLUE, True, width=220, role="diagram")
        s.text(995, y + 45, f"{item['baseline']} → {item['sample']}", 18, INK, True)
        s.text(995, y + 67, item["note"], 15, MUTED, width=225, role="body")
    s.header(25, 603, 120, "风险护栏", 95, BLUE, 16)
    for i, item in enumerate(d["guardrails"]):
        x = 155 + i * 275
        s.rect(x, 603, 270, 95, "#FFFFFF", LINE, 0, data_role="guardrail-column")
        s.icon(item["icon"], x + 12, 620, 38, "#FFFFFF", disc=True, disc_color=BLUE)
        s.text(x + 66, 632, item["name"], 12, BLUE, True, width=185, role="diagram")
        s.text(x + 66, 653, "\n".join(item["lines"]), 12, INK, width=185, leading=15, max_lines=3, role="diagram")
    return s.finish()


def render_r27(content):
    d = _content("R27", content)
    s = MechanismSvg()
    s.title(d["title"], d["subtitle"], 34, color="#10131D")
    x, y, table_h = 18, 138, 370
    widths = [142, 122, 205, 85, 132, 68, 135, 91]
    flow_x = x
    for title, width in zip(d["flow"], widths):
        ribbon_w, ribbon_y, ribbon_h = width + 2, 99, 34
        s.poly(
            [
                (flow_x, ribbon_y),
                (flow_x + ribbon_w - 14, ribbon_y),
                (flow_x + ribbon_w, ribbon_y + ribbon_h / 2),
                (flow_x + ribbon_w - 14, ribbon_y + ribbon_h),
                (flow_x, ribbon_y + ribbon_h),
            ],
            BLUE,
        )
        if title.strip():
            label_parts = [part.strip() for part in title.split("｜")]
            if len(label_parts) != 2 or not all(label_parts):
                raise ValueError("R27 flow labels require complete English and Chinese text")
            label_x = flow_x + width / 2
            label_w = max(width - 16, 75)
            s.text(label_x, 111, label_parts[0], 12, "#FFFFFF", True, width=label_w, anchor="middle", max_lines=1, role="diagram")
            s.text(label_x, 127, label_parts[1], 12, "#FFFFFF", True, width=label_w, anchor="middle", max_lines=1, role="diagram")
        flow_x += width
    table_rows = [
        [
            f"{row['goal']}\n{row['goal_definition']}",
            f"{row['metric']}\n目标 {row['target_label']}",
            "",
            f"{row['variance']}  {row['direction']}\n{row['relative']}",
            "\n".join(row["causes"]),
            row["owner"],
            row["action"],
            row["review"],
        ]
        for row in d["rows"]
    ]
    s.table(
        "r27-wbr-main",
        x,
        y,
        sum(widths),
        table_h,
        d["table_columns"],
        table_rows,
        [width / sum(widths) for width in widths],
        10.2,
        column_styles=[{"body_fill": "none", "margin_left_pt": 32}],
        row_heights=[0.25, 1, 1, 1, 1, 1],
    )
    main_table = s.native["tables"][-1]
    main_table["style"].update(
        {
            "header_fill": "#FFFFFF",
            "header_text_color": BLUE,
            "margin_top_pt": 1,
            "margin_bottom_pt": 1,
        }
    )
    header_h = table_h * 0.25 / 5.25
    body_h = (table_h - header_h) / len(d["rows"])
    trend_x = x + widths[0] + widths[1]
    for ri, row in enumerate(d["rows"]):
        yy = y + header_h + body_h * ri
        s.icon(
            row["icon"],
            x + 7,
            yy + body_h / 2 - 13,
            24,
            "#FFFFFF",
            disc=True,
            disc_color=BLUE,
        )
        s.chart(
            f"r27-trend-{ri + 1}",
            trend_x + 5,
            yy + 4,
            widths[2] - 10,
            body_h - 8,
            row["weeks"],
            [{"name": "实际", "values": row["values"]}],
            kind="line",
            fmt=row["format"],
            options={
                "sparkline": True,
                "data_labels": True,
                "data_label_wrap": False,
                "data_label_position": "below",
            },
        )
    _panel(s, 1015, 99, 247, 409, d["mechanism_title"])
    for i, item in enumerate(d["mechanisms"]):
        y = 142 + i * 60
        s.number(1043, y + 13, str(i + 1), 10)
        s.text(1063, y + 14, item["name"], 12, BLUE, True, width=115, max_lines=1, role="diagram")
        s.text(1063, y + 35, item["note"], 15, INK, width=115, max_lines=2, role="body")
        icon = s.icon(item["icon"], 1208, y + 4, 30, BLUE)
        icon.set("data-role", "mechanism-right-icon")
    s.table(
        "r27-anomalies",
        18,
        512,
        430,
        178,
        d["anomaly_columns"],
        d["anomalies"],
        [0.24, 0.16, 0.14, 0.16, 0.3],
        9.8,
    )
    _panel(s, 465, 512, 533, 178, d["root_title"])
    root_pos = [
        (475, 604),
        (570, 564),
        (570, 638),
        (680, 548),
        (680, 582),
        (680, 616),
        (680, 650),
        (828, 548),
        (828, 582),
        (828, 616),
        (828, 650),
    ]
    for i, label in enumerate(d["root_nodes"]):
        x1, y1 = root_pos[i]
        node_w = 90 if i < 7 else 132
        s.rect(x1, y1, node_w, 27, PALE, LINE, 2)
        s.text(x1 + node_w / 2, y1 + 17, label, 12, INK, anchor="middle", width=node_w - 8, max_lines=1, role="diagram")
    for a, b in d["root_edges"]:
        s.line(
            root_pos[a][0] + (90 if a < 7 else 132),
            root_pos[a][1] + 12,
            root_pos[b][0],
            root_pos[b][1] + 12,
            MUTED,
            1,
        )
    s.table(
        "r27-thresholds",
        1015,
        512,
        247,
        178,
        d["threshold_columns"],
        d["thresholds"],
        [0.6, 0.4],
        9.8,
    )
    s.text(20, 701, d["footnote"], 11, MUTED, width=1230, max_lines=1, role="source")
    return s.finish()


def render_r28(content):
    d = _content("R28", content)
    s = MechanismSvg()
    s.title(d["title"], d["subtitle"], 35, color="#10131D")
    # Paper silhouette with folded corners anchors the six-section memo.
    paper = s.poly(
        [(25, 100), (690, 100), (716, 126), (716, 690), (25, 690)],
        "#FFFFFF",
        "#AAB7C8",
        stroke_width=2,
    )
    paper.set("data-role", "document-paper")
    s.poly([(690, 100), (690, 126), (716, 126)], "#E7EDF5", LINE, data_role="paper-fold")
    s.poly([(25, 664), (51, 690), (25, 690)], "#E7EDF5", LINE, data_role="paper-fold")
    s.text(65, 132, "六段结构", 12, BLUE, True, role="diagram")
    s.text(190, 132, "内容要点", 12, BLUE, True, role="diagram")
    s.text(565, 132, "边注", 12, BLUE, True, role="diagram")
    for i, sec in enumerate(d["sections"]):
        y = 150 + i * 86
        if i:
            s.line(38, y - 8, 700, y - 8, LINE, 1, True)
        s.rect(42, y, 132, 64, BLUE, "none", 3)
        s.icon(sec["icon"], 53, y + 15, 30, "#FFFFFF")
        s.text(93, y + 28, sec["name"], 12, "#FFFFFF", True, width=73, role="diagram")
        for line_index, line in enumerate(sec["points"]):
            s.text(192, y + 15 + line_index * 18, line, 15, INK, width=345, max_lines=1, role="body")
        for line_index, line in enumerate(sec["questions"]):
            s.text(560, y + 15 + line_index * 20, line, 15, MUTED, width=138, max_lines=1, role="body")
        if i < 5:
            s.arrow(108, y + 65, 108, y + 83, BLUE, 1.4)
    s.table(
        "r28-compare",
        775,
        105,
        480,
        330,
        d["compare_columns"],
        d["compare_rows"],
        [0.25, 0.36, 0.39],
        9.5,
    )
    for i, icon_name in enumerate(["file-text", "scale", "alarm-clock", "message-circle"]):
        icon = s.icon(icon_name, 744, 192 + i * 66, 26, BLUE)
        icon.set("data-role", "compare-row-icon")
    _panel(s, 740, 455, 515, 235, d["meeting_title"])
    for i, item in enumerate(d["meeting"]):
        x = 752 + i * 124
        s.rect(x, 488, 114, 184, "#F7F9FC", LINE, 0, data_role="meeting-step-panel")
        s.icon(item["icon"], x + 34, 500, 42, BLUE)
        s.text(x + 55, 548, item["name"], 12, BLUE, True, anchor="middle", width=105, role="diagram")
        s.text(x + 55, 568, item["duration"], 12, MUTED, anchor="middle", role="diagram")
        cursor_y = 594
        for line in item["lines"]:
            s.circle(x + 8, cursor_y - 4, 3, BLUE)
            used = _stacked_text(
                s, x + 17, cursor_y, line, 91, 15, INK, leading=18, max_lines=2, role="body"
            )
            cursor_y += used * 18 + 5
        if i < 3:
            s.arrow(x + 106, 521, x + 121, 521, BLUE, 2)
    return s.finish()


def render_r29(content):
    d = _content("R29", content)
    option_names = d["option_names"]
    if option_names == ["", ""]:
        option_names = DEFAULTS["R29"]["option_names"]
    if len(option_names) != 2 or any(not str(name).strip() or len(str(name).strip()) > 8 for name in option_names):
        raise ValueError("R29 option_names requires two non-empty names of at most 8 characters")
    s = MechanismSvg()
    s.title(d["title"], d["subtitle"], 35, color="#10131D")
    s.header(28, 92, 120, "长期视角", 60, BLUE, 17)
    _flow_cards(s, d["timeline"], 165, 95, 1080, 110, notes=True)
    _panel(s, 28, 220, 585, 285, d["matrix_title"])
    grid_x, grid_y, grid_w, grid_h = 145, 282, 440, 190
    s.rect(grid_x, 254, grid_w / 2, 30, BLUE, "none", 0, data_role="matrix-column-header")
    s.rect(grid_x + grid_w / 2, 254, grid_w / 2, 30, MID, "none", 0, data_role="matrix-column-header")
    s.text(grid_x + grid_w / 4, 275, "可逆", 12, "#FFFFFF", True, anchor="middle", role="diagram")
    s.text(grid_x + grid_w * 0.75, 275, "不可逆", 12, "#FFFFFF", True, anchor="middle", role="diagram")
    s.rect(70, grid_y, 70, grid_h / 2, BLUE, "none", 0, data_role="matrix-row-header")
    s.rect(70, grid_y + grid_h / 2, 70, grid_h / 2, "#7187A8", "none", 0, data_role="matrix-row-header")
    s.text(105, grid_y + grid_h / 4 + 5, "行动", 12, "#FFFFFF", True, anchor="middle", role="diagram")
    s.text(105, grid_y + grid_h * 0.75 + 5, "不行动", 12, "#FFFFFF", True, anchor="middle", role="diagram")
    s.rect(grid_x, grid_y, grid_w, grid_h, "#FFFFFF", LINE, 0)
    s.line(grid_x + grid_w / 2, grid_y, grid_x + grid_w / 2, grid_y + grid_h, LINE, 1.2, True)
    s.line(grid_x, grid_y + grid_h / 2, grid_x + grid_w, grid_y + grid_h / 2, LINE, 1.2, True)
    fills = ["#E6EEF9", "#D0E0F3", "#F2F5F9", "#DFE8F4"]
    for i, item in enumerate(d["quadrants"]):
        xx = grid_x + (i % 2) * grid_w / 2
        yy = grid_y + (i // 2) * grid_h / 2
        s.rect(xx + 5, yy + 5, grid_w / 2 - 10, grid_h / 2 - 10, fills[i], "none", 3)
        s.text(xx + 15, yy + 24, item["name"], 14, BLUE, True, width=grid_w / 2 - 30, role="diagram")
        for line_index, line in enumerate(item["lines"]):
            s.text(xx + 15, yy + 49 + line_index * 18, line, 15, INK, width=grid_w / 2 - 30, max_lines=1, role="body")
    _panel(s, 633, 220, 619, 285, d["score_title"])
    s.text(690, 271, "维度", 12, MUTED, True, role="diagram")
    s.text(785, 271, "评估要点", 12, MUTED, True, role="diagram")
    s.text(1040, 271, "共同 1–5 量尺", 12, MUTED, True, anchor="middle", role="diagram")
    s.text(1172, 271, f"橙={option_names[0]}｜蓝={option_names[1]}", 12, MUTED, width=150, anchor="middle", max_lines=1, role="diagram")
    for i, item in enumerate(d["scores"]):
        y = 292 + i * 36
        s.icon(item["icon"], 650, y - 6, 25, BLUE)
        s.text(683, y + 10, item["name"], 12, BLUE, True, width=88, role="diagram")
        s.text(775, y + 10, item.get("criterion", "评估要点"), 15, INK, width=135, max_lines=1, role="body")
        scale_x, scale_w = 920, 245
        s.rect(scale_x, y, scale_w, 13, "#E7EDF5", "none", 0)
        s.rect(scale_x, y, scale_w / 5 * item["trial"], 13, MID, "none", 0)
        marker_x = scale_x + scale_w / 5 * item["expand"]
        s.node(
            "line",
            x1=marker_x,
            y1=y - 4,
            x2=marker_x,
            y2=y + 17,
            stroke=ORANGE,
            stroke_width=3,
            data_role="score-marker",
        )
        s.circle(scale_x + scale_w / 5 * item["trial"], y + 6.5, 4, BLUE, data_role="score-trial-marker")
        s.text(1184, y + 10, str(item["expand"]), 12, ORANGE, True, width=20, max_lines=1, role="diagram")
        s.text(1212, y + 10, str(item["trial"]), 12, BLUE, True, width=20, max_lines=1, role="diagram")
    for tick in range(1, 6):
        tick_x = 920 + 245 / 5 * tick
        s.text(tick_x, 474, str(tick), 12, MUTED, anchor="middle", role="diagram")
    s.text(652, 497, d["score_note"], 12, MUTED, width=570, role="diagram")
    s.header(28, 530, 120, "两条路径", 162, BLUE, 16)
    for ri, path in enumerate(d["paths"]):
        y = 542 + ri * 76
        for x, node, dark in [
            (170, path["choice"], True),
            (335, path["investment"], False),
        ]:
            s.rect(x, y + 5, 135, 54, BLUE if dark else PALE, BLUE if dark else LINE, 3)
            s.text(
                x + 67,
                y + 27,
                node["name"],
                12,
                "#FFFFFF" if dark else BLUE,
                True,
                anchor="middle",
                width=118,
                role="diagram",
            )
            s.text(
                x + 67,
                y + 46,
                node["note"],
                15,
                "#FFFFFF" if dark else MUTED,
                anchor="middle",
                width=118,
                role="body",
            )
        s.arrow(305, y + 32, 332, y + 32, BLUE, 1.5)
        for bi, branch in enumerate(path["branches"]):
            by = y + bi * 31
            s.node(
                "line",
                x1=470,
                y1=y + 32,
                x2=505,
                y2=by + 14,
                stroke=BLUE,
                stroke_width=2.2,
                data_role="probability-branch",
            )
            s.poly([(505, by + 14), (495, by + 9), (496, by + 19)], BLUE)
            s.rect(510, by, 115, 28, "#E7EFF9", LINE, 3)
            s.text(
                567,
                by + 18,
                branch["probability"],
                12,
                BLUE,
                True,
                anchor="middle",
                width=104,
                role="diagram",
            )
            s.arrow(625, by + 14, 648, by + 14, BLUE, 1.2)
            s.rect(650, by, 125, 28, PALE, LINE, 3)
            s.text(
                712,
                by + 18,
                branch["result"],
                12,
                BLUE,
                True,
                anchor="middle",
                width=114,
                role="diagram",
            )
        s.rect(800, y, 440, 72, "#FFFFFF", LINE, 2)
        s.text(814, y + 17, "未来回望", 12, BLUE, True, role="diagram")
        for line_index, line in enumerate(path["reflection"]):
            s.text(814, y + 34 + line_index * 17, line, 15, INK, width=410, max_lines=1, role="body")
    return s.finish()


def render_r30(content):
    d = _content("R30", content)
    s = MechanismSvg()
    s.title(d["title"], d["subtitle"], 34, color="#10131D")
    cx, cy = 390, 330
    s.circle(cx, cy, 118, "none", "#7EA0C8", stroke_width=5, data_role="principle-ring")
    s.circle(cx, cy, 96, "none", MID, stroke_width=2.5, data_role="principle-ring")
    s.circle(cx, cy, 74, BLUE)
    s.text(
        cx,
        cy - 10,
        d["center"],
        17,
        "#FFFFFF",
        True,
        width=115,
        anchor="middle",
        leading=20,
    )
    cards = [(65, 105), (450, 105), (20, 270), (475, 270), (80, 440), (445, 440)]
    anchors = []
    ring_angles = [-2.25, -0.9, math.pi, 0, 2.25, 0.9]
    for i, item in enumerate(d["principles"]):
        x, y = cards[i]
        s.rect(x, y, 260, 138, "#FFFFFF", LINE, 1)
        s.icon(item["icon"], x + 12, y + 16, 48, "#FFFFFF", disc=True, disc_color=BLUE)
        s.text(x + 78, y + 38, item["name"], 15, BLUE, True, width=164, max_lines=1)
        s.text(x + 78, y + 67, "• " + "\n• ".join(item["lines"]), 12, INK, width=164, leading=18, max_lines=3, role="diagram")
        ax = x + (260 if x < cx else 0)
        ay = y + 69
        anchors.append((ax, ay))
        angle = ring_angles[i]
        rx, ry = cx + 118 * math.cos(angle), cy + 118 * math.sin(angle)
        s.line(cx, cy, rx, ry, "#A8BED8", 1.1)
        s.line(rx, ry, ax, ay, BLUE, 2)
        s.circle(rx, ry, 8, "#FFFFFF", BLUE, stroke_width=3, data_role="principle-ring-node")
    s.header(22, 580, 690, d["lifecycle_title"], 24, BLUE, 13)
    for i, item in enumerate(d["lifecycle"]):
        x = 28 + i * 113
        s.ribbon(x, 610, 116, 28, item["name"], str(i + 1), size=9.5)
        icon = s.icon(ICONS[(i + 1) % len(ICONS)], x + 7, 646, 19, BLUE)
        icon.set("data-role", "lifecycle-step-icon")
        s.text(x + 31, 656, item["note"], 15, INK, width=78, max_lines=2, leading=17, role="body")
    s.poly([(28, 680), (676, 680), (706, 690), (676, 700), (28, 700)], "#DCE8F7", BLUE, data_role="lifecycle-direction-band")
    s.text(360, 695, d["lifecycle_conclusion"], 12, BLUE, True, width=625, anchor="middle", max_lines=1, role="diagram")
    s.table(
        "r30-mechanisms",
        776,
        102,
        482,
        588,
        d["table_columns"],
        d["table_rows"],
        [0.18, 0.28, 0.25, 0.29],
        9.5,
    )
    table_row_h = 588 / 7
    for i, item in enumerate(d["principles"]):
        icon = s.icon(item["icon"], 748, 102 + table_row_h * (i + 1) + table_row_h / 2 - 10, 20, BLUE)
        icon.set("data-role", "principle-table-icon")
    return s.finish()


def render_r32(content):
    d = _content("R32", content)
    s = MechanismSvg(1080, 720)
    s.text(540, 48, d["title"], 38, "#10131D", True, anchor="middle")
    s.text(540, 78, d["subtitle"], 15, INK, anchor="middle")
    _panel(s, 14, 92, 190, 480, d["pipeline_title"])
    for i, item in enumerate(d["inputs"]):
        _mini_card(
            s, 30, 126 + i * 52, 158, 44, item["name"], [], item["icon"], "#FFFFFF"
        )
    s.rect(106, 214, 6, 326, MID, "none", 0, data_role="pipeline-mainline")
    s.header(26, 250, 166, "实体抽取分层流水线", 28, BLUE, 11)
    for i, item in enumerate(d["pipeline"]):
        y = 280 + i * 35
        s.rect(30, y, 158, 28, "#FFFFFF", LINE, 3)
        s.icon(item["icon"], 38, y + 4, 20, BLUE)
        s.text(66, y + 19, item["name"], 12, INK, width=110, role="diagram")
        if i < 6:
            s.arrow(109, y + 28, 109, y + 34, BLUE, 1.4)
    for index, line in enumerate(d["pipeline_note"].splitlines()):
        s.text(28, 543 + index * 18, line, 15, MUTED, width=165, role="body")
    s.rect(235, 94, 805, 376, "#FFFFFF", "#8797AE", 12, stroke_dasharray="6 4")
    s.text(638, 113, d["graph_title"], 15, BLUE, True, anchor="middle")
    card_specs = [
        (255, 126, 180, "short", BLUE, "blue"),
        (495, 126, 220, "long", GREEN, "teal"),
        (775, 126, 220, "reason", "#1F5B9E", "blue"),
    ]
    for x, y, w, key, color, color_role in card_specs:
        mem = d["memories"][key]
        card = s.rect(x, y, w, 328, "#FFFFFF", color, 7, stroke_width=2)
        card.set("data-layout-role", "memory-card")
        card.set("data-memory-key", key)
        card.set("data-color-role", color_role)
        s.icon(mem["icon"], x + 12, y + 12, 38, "#FFFFFF", disc=True, disc_color=color)
        s.text(x + 60, y + 32, mem["title"], 17, color, True, width=w - 72, max_lines=1)
        s.text(x + 60, y + 53, mem["definition"], 15, MUTED, width=w - 72, leading=18, max_lines=2, role="body")
        step = 29 if len(mem["items"]) > 6 else 34
        for i, item in enumerate(mem["items"]):
            yy = y + 86 + i * step
            row = s.rect(x + 12, yy, w - 24, step - 5, PALE, LINE, 2)
            row.set("data-role", "memory-item")
            row.set("data-memory-key", key)
            s.icon(item["icon"], x + 18, yy + 4, 18, color)
            s.text(x + 44, yy + 18, item["name"], 12, INK, width=w - 58, role="diagram")
        band_fill = {"short": "#E7F0FA", "long": "#E8F5F0", "reason": "#E7F0FA"}[key]
        band = s.rect(x + 10, y + 293, w - 20, 27, band_fill, "none", 1, data_role="memory-note-band")
        band.set("data-memory-key", key)
        s.text(
            x + 12,
            y + 311,
            mem["note"],
            15,
            color,
            True,
            width=w - 24,
            anchor="start",
            role="body",
            max_lines=1,
        )
    s.arrow(438, 282, 492, 282, BLUE, 1.5, both=True)
    s.text(
        465, 258, "提取实体\n补充约束", 12, BLUE, anchor="middle", width=52, leading=15, role="diagram"
    )
    s.arrow(718, 282, 772, 282, GREEN, 1.5, both=True)
    s.text(
        745, 258, "业务事实\n证据支撑", 12, GREEN, anchor="middle", width=54, leading=15, role="diagram"
    )
    s.path("M885 455 L885 476 L345 476 L345 455", stroke=BLUE, width=1.6)
    s.text(615, 486, "生成回答 / 接收反馈", 12, BLUE, True, anchor="middle", role="diagram")
    _panel(s, 205, 500, 625, 174, d["relations_title"])
    for ri, chain in enumerate(d["relations"]):
        y = 535 + ri * 41
        x = 222
        usable_w = 591
        node_widths = [max(84, min(130, sum(12 if ord(char) > 255 else 6.72
                                         for char in str(node["node"])) + 32)) for node in chain]
        gap = (usable_w - sum(node_widths)) / max(1, len(chain) - 1)
        if gap < 64:
            raise ValueError("R32 relation chain labels require at least 64px of inter-node clearance")
        for ni, (node, node_w) in enumerate(zip(chain, node_widths)):
            color = ((BLUE, GREEN, GREEN),
                     (BLUE, PURPLE, PURPLE, BLUE),
                     (BLUE, BLUE, BLUE))[ri][ni]
            node_fill = {BLUE: "#EAF2FA", GREEN: "#E8F5F0", PURPLE: "#F1EDF8"}[color]
            relation_node = s.rect(x, y, node_w, 26, node_fill, color, 3)
            relation_node.set("data-role", "relation-node")
            relation_node.set("data-relation-row", str(ri))
            icon_name = (("message-square", "box", "file-text"),
                         ("message-square", "workflow", "wrench", "file-text"),
                         ("scale", "message-square", "thumbs-up"))[ri][ni]
            icon = s.icon(icon_name, x + 6, y + 5, 16, color)
            icon.set("data-role", "relation-node-icon")
            s.text(
                x + 26, y + 17, node["node"], 12, color, True,
                width=node_w - 30, max_lines=1, role="diagram"
            )
            if node.get("relation"):
                s.arrow(x + node_w, y + 13, x + node_w + gap, y + 13, color, 1.2)
                s.text(
                    x + node_w + gap / 2,
                    y + 10,
                    node["relation"],
                    12,
                    INK,
                    anchor="middle",
                    width=max(1, gap - 8),
                    max_lines=1,
                    role="diagram",
                )
                s.root[-1].set("data-layout-role", "relation-label")
                s.root[-1].set("data-relation-row", str(ri))
            x += node_w + gap
    _panel(s, 840, 500, 226, 174, d["governance_title"], fill="#FFF7ED", color=ORANGE)
    s.icon("shield-check", 1031, 507, 22, "#FFFFFF")
    for index, item in enumerate(d["governance"]):
        s.circle(856, 535 + index * 18, 2.5, ORANGE)
        s.text(866, 540 + index * 18, item, 15, INK, width=188, max_lines=1, role="body")
    s.rect(850, 628, 206, 38, "#FFF1DF", "none", 2)
    for index, line in enumerate(d["protection"].splitlines()):
        s.text(858, 642 + index * 12, line, 12, ORANGE, True, width=190, max_lines=1, role="diagram")
    s.header(50, 676, 980, d["core_idea"], 24, BLUE, 13)
    core_icon = s.icon("lightbulb", 68, 679, 18, "#FFFFFF")
    core_icon.set("data-role", "core-idea-icon")
    return s.finish()


DEFAULTS = {
    "R16": {
        "title": "客户驱动与小步验证，维护组织活力",
        "subtitle": "机制示意｜不表示风险已经发生",
        "cycle_title": "持续活力模型",
        "cycle_center": "客户价值\n运行模型",
        "cycle": [
            {
                "name": "客户任务",
                "icon": "users",
                "actions": ["回访真实任务", "定义完成标准", "记录体验差距"],
            },
            {
                "name": "外部变化",
                "icon": "search",
                "actions": ["扫描政策趋势", "复核竞争变化", "更新约束假设"],
            },
            {
                "name": "分级决策",
                "icon": "scale",
                "actions": ["按影响授权", "限时形成选择", "保留复核入口"],
            },
            {
                "name": "小规模实验",
                "icon": "lightbulb",
                "actions": ["小样本验证", "容许受控失败", "用证据迭代"],
            },
        ],
        "decline_title": "活力衰退的五步假设链",
        "decline": [
            {"name": "流程代替结果", "lines": ["关注流程合规", "过程指标优先", "客户完成被忽略"], "icon": "file-text"},
            {"name": "层级增加", "lines": ["职责边界交叠", "资源等待变长", "协调成本上升"], "icon": "users"},
            {"name": "决策延迟", "lines": ["信息层层过滤", "反馈难以还原", "行动窗口错失"], "icon": "alarm-clock"},
            {"name": "创新减少", "lines": ["试验数量下降", "范围持续收缩", "失败惩罚放大"], "icon": "lightbulb"},
            {
                "name": "价值下降",
                "lines": ["任务完成受损", "满意度停滞", "替代选择增加"],
                "icon": "chart-bar-increasing",
            },
        ],
        "defense_title": "四项防御机制",
        "defenses": [
            {"name": "客户回访", "definition": "持续贴近客户真实任务", "owner": "产品负责人", "artifact": "访谈纪要", "practice": "双周复核"},
            {"name": "结果复核", "definition": "用客户完成替代过程完成", "owner": "业务负责人", "artifact": "结果核对表", "practice": "逐项签收"},
            {"name": "趋势扫描", "definition": "把外部变化转成约束假设", "owner": "战略组", "artifact": "趋势周报", "practice": "月度更新"},
            {"name": "授权试验", "definition": "限定预算、期限和回退边界", "owner": "委员会", "artifact": "边界清单", "practice": "到期复盘"},
        ],
        "curve_title": "组织活力曲线（示意）",
        "curve_growth": ["客户驱动", "快速迭代", "外部洞察优先", "决策高速度"],
        "curve_decline": ["内部流程驱动", "反馈迟缓", "洞察滞后", "试错受限"],
        "curve_signals": ["会议时间持续增加", "跨团队周期变长", "创新项目数量下降"],
        "signals_title": "六项预警信号与复核来源",
        "signals": [
            {"name": "会议增加", "meaning": "讨论替代现场决策", "source": "来源：会议台账"},
            {"name": "审批变长", "meaning": "问题到行动周期拉长", "source": "来源：流程时长"},
            {"name": "过程指标独大", "meaning": "内部完成遮蔽客户结果", "source": "来源：WBR"},
            {"name": "试验数下降", "meaning": "学习窗口持续收缩", "source": "来源：实验账本"},
            {"name": "跨组层级增加", "meaning": "接口和协调成本上升", "source": "来源：组织接口"},
            {"name": "满意度停滞", "meaning": "任务体验没有改善", "source": "来源：客户样本"},
        ],
    },
    "R17": {
        "title": "从客户任务出发，把体验差距转成验证行动",
        "subtitle": "2026 年 20 位合成访谈样本｜重点验证便利与速度",
        "steps": [
            {"name": "客户任务", "note": "真实场景与预期结果", "icon": "users"},
            {"name": "痛点", "note": "哪里不够好或不可用", "icon": "search"},
            {"name": "理想体验", "note": "无约束时希望怎样完成", "icon": "goal"},
            {"name": "方案", "note": "围绕客户价值设计", "icon": "lightbulb"},
            {"name": "度量", "note": "用关键指标验收", "icon": "chart-bar-increasing"},
            {"name": "反馈", "note": "复核并持续迭代", "icon": "refresh-ccw"},
        ],
        "compare_title": "Inside-Out 与 Outside-In 五维对照",
        "comparison": [
            {"inside": "跟随竞品｜复制功能", "inside_note": "追踪对手动作，容易忽略真实任务", "outside": "从任务出发｜理解真实目标", "outside_note": "从客户场景、阻碍和完成标准找机会"},
            {"inside": "功能罗列｜完成开发", "inside_note": "以交付功能作为结束条件", "outside": "验收价值｜验证任务完成", "outside_note": "用完成率、时长与质量验证结果"},
            {"inside": "促销差异｜价格驱动", "inside_note": "靠折扣和短期活动制造差异", "outside": "体验差异｜便利与速度", "outside_note": "用更省心、更可靠的体验形成选择"},
            {"inside": "被动接受｜流程迁就", "inside_note": "要求客户适应内部流程和限制", "outside": "主动选择｜更省心可靠", "outside_note": "围绕客户任务主动改造关键接触点"},
            {"inside": "短期销售｜一次转化", "inside_note": "只追踪当期转化与排名", "outside": "长期满意｜持续复购", "outside_note": "关注长期任务完成、信任与复购"},
        ],
        "radar_title": "客户价值五维雷达",
        "radar": {
            "labels": ["选择", "价格", "便利", "速度", "信任"],
            "dimension_notes": [
                {"label": "选择", "english": "Selection", "note": "丰富度、相关性、可得性"},
                {"label": "价格", "english": "Price", "note": "透明度、总成本、价值感"},
                {"label": "便利", "english": "Convenience", "note": "易用、低摩擦、可自助"},
                {"label": "速度", "english": "Speed", "note": "响应、履约、问题解决"},
                {"label": "信任", "english": "Trust", "note": "可靠、安全、预期一致"},
            ],
            "series": [
                {"name": "理想", "values": [4.8, 4.5, 4.7, 4.6, 4.9]},
                {"name": "当前", "values": [3.8, 3.7, 3.2, 3.4, 4.1]},
                {"name": "样本方案", "values": [3.5, 3.8, 3.6, 3.7, 4.0]},
            ],
        },
        "radar_note": "后一组为样本方案，不代表行业平均。",
        "action_title": "从声音到行动的闭环",
        "actions": [
            {
                "name": "倾听",
                "icon": "message-circle",
                "lines": ["客户评价与反馈", "客服与售后咨询", "站内行为数据", "调研与访谈"],
            },
            {"name": "洞察", "icon": "search", "lines": ["需求与痛点识别", "模式与趋势分析", "机会优先级排序", "客户细分洞察"]},
            {"name": "行动", "icon": "lightbulb", "lines": ["产品与体验创新", "流程与运营优化", "沟通与价值传递", "度量与迭代改进"]},
        ],
        "result_title": "客户价值提升",
        "result_lines": ["客户更满意", "业务更忠诚"],
    },
    "R18": {
        "title": "先写客户结果与证据，再决定产品方案和投入",
        "subtitle": "Working Backwards｜8 周可逆试验建议",
        "steps": [
            {"name": "客户任务", "questions": ["谁是目标客户？", "在什么场景完成任务？", "什么结果才算完成？"], "icon": "users"},
            {"name": "未满足问题", "questions": ["当前哪里不足？", "为什么仍不够好？", "失败代价是什么？"], "icon": "search"},
            {"name": "成功条件", "questions": ["理想体验是什么？", "客户怎样判断完成？", "关键约束是什么？"], "icon": "target"},
            {"name": "新闻稿草案", "questions": ["先写客户结果", "说明价值与证据", "避免功能先行"], "icon": "file-text"},
            {"name": "方案假设", "questions": ["产品边界是什么？", "价值主张是什么？", "怎样验证差异？"], "icon": "box"},
            {"name": "FAQ及风险", "questions": ["列出反例", "定义失败条件", "准备回退路线"], "icon": "shield-check"},
            {"name": "试验批准", "questions": ["路线是否清楚？", "预算是否受控？", "谁签字与复盘？"], "icon": "goal"},
        ],
        "forward": {
            "title": "内部能力出发（顺向）",
            "nodes": [
                {"name": "技术", "note": "从技术或资源出发", "icon": "wrench"},
                {"name": "产品", "note": "定义功能与边界", "icon": "box"},
                {"name": "营销", "note": "制定卖点与传播", "icon": "message-circle"},
                {"name": "客户", "note": "被动接受价值", "icon": "users"},
            ],
            "points": ["方案先行，问题后置", "验证成本与风险偏高", "可能偏离真实任务"],
        },
        "document": {
            "title": "一页客户结果说明",
            "label": "PR / FAQ 核心工件",
            "facts": [
                {"name": "对象", "value": "20 个小型商户", "icon": "users"},
                {"name": "任务", "value": "首次完成配置", "icon": "target"},
                {"name": "当前", "value": "中位 32 分钟", "icon": "alarm-clock"},
                {
                    "name": "目标",
                    "value": "TARGET ≤20 分钟",
                    "icon": "chart-bar-increasing",
                },
                {"name": "限制", "value": "不含迁移", "icon": "shield-check"},
            ],
            "questions": [
                "客户获得什么结果？",
                "为什么现在值得做？",
                "如何工作与验证？",
                "与现有方案有何不同？",
                "风险和回退是什么？",
            ],
        },
        "backward": {
            "title": "客户结果倒推（反向）",
            "nodes": [
                {"name": "客户", "note": "从任务与场景出发", "icon": "users"},
                {"name": "体验", "note": "定义完成后的样子", "icon": "goal"},
                {"name": "产品", "note": "清晰产品边界与取舍", "icon": "box"},
                {"name": "能力", "note": "构建支撑体验的能力", "icon": "wrench"},
            ],
            "points": ["从结果定义产品边界", "先证据后资源投入", "优先暴露风险与约束"],
        },
        "gates": [
            {"name": "问题真实", "rule": "20 人样本"},
            {"name": "体验达标", "rule": "16/20 独立完成"},
            {"name": "价值可信", "rule": "完成≤20分钟"},
            {"name": "产品清晰", "rule": "限制明确"},
            {"name": "能力就绪", "rule": "预算≤30万"},
            {"name": "可规模化", "rule": "产品/质量双签"},
        ],
    },
    "R19": {
        "title": "客户价值、规模与成本形成八节点循环",
        "subtitle": "机制示意｜每段杠杆均需单独验证",
        "compare_title": "线性活动与复利系统",
        "comparison": [
            {
                "linear": "一次促销",
                "linear_points": ["短期触达", "单点投入"],
                "system": "持续体验",
                "system_points": ["复用增强", "客户积累"],
            },
            {
                "linear": "孤立动作",
                "linear_points": ["部门割裂", "协作成本"],
                "system": "接口协作",
                "system_points": ["环环相扣", "边际改善"],
            },
            {
                "linear": "一次回报",
                "linear_points": ["活动结束", "能力未留"],
                "system": "学习积累",
                "system_points": ["假设沉淀", "持续迭代"],
            },
        ],
        "flywheel": [
            {"name": "更低使用门槛", "driver": "配置更简单", "icon": "arrow-down"},
            {"name": "更好首次体验", "driver": "首轮成功", "icon": "users"},
            {"name": "更多有效使用", "driver": "任务完成", "icon": "chart-bar-increasing"},
            {"name": "更多合作供给", "driver": "接口开放", "icon": "handshake"},
            {"name": "更丰富方案", "driver": "组合增加", "icon": "box"},
            {"name": "更好持续体验", "driver": "质量稳定", "icon": "shield-check"},
            {"name": "业务留存增长", "driver": "持续使用", "icon": "refresh-ccw"},
            {"name": "更低单位成本", "driver": "规模复用", "icon": "database"},
        ],
        "center": "客户价值与\n持续使用",
        "inner_loops": [
            {"name": "使用—供给增强回路", "note": "有效使用吸引供给，供给反过来扩展任务覆盖"},
            {"name": "选择—体验增强回路", "note": "方案选择增加，持续体验改善后带来更多使用"},
        ],
        "levers_title": "四个杠杆点与待验假设",
        "levers": [
            {
                "name": "门槛",
                "icon": "target",
                "effects": ["减少配置步骤", "降低学习成本", "提高首次完成"],
                "hypothesis": "向导能改善完成率",
            },
            {
                "name": "选择",
                "icon": "box",
                "effects": ["覆盖更多任务", "降低搜寻成本", "增加方案适配"],
                "hypothesis": "组合可提升采用",
            },
            {
                "name": "便利",
                "icon": "alarm-clock",
                "effects": ["缩短等待", "提高确定性", "减少服务成本"],
                "hypothesis": "自动化缩短时长",
            },
            {
                "name": "信任",
                "icon": "shield-check",
                "effects": ["降低风险", "提高留存", "支持长期运营"],
                "hypothesis": "证据提升信任",
            },
        ],
        "formula": [
            {"name": "客户价值", "icon": "users", "lines": ["更低门槛", "更好体验"]},
            {
                "name": "有效规模",
                "icon": "chart-bar-increasing",
                "lines": ["更多使用", "更多供给"],
            },
            {"name": "服务效率", "icon": "wrench", "lines": ["复用自动化", "单位成本"]},
            {
                "name": "长期增长",
                "icon": "refresh-ccw",
                "lines": ["机制示意", "不承诺必然"],
            },
        ],
    },
    "R20": {
        "title": "先判断影响与可逆性，再匹配决策成本",
        "subtitle": "时限和审批级均为建议",
        "steps": [
            {"name": "识别", "notes": ["明确问题与目标", "界定范围约束"]},
            {"name": "分类", "notes": ["判断可逆性", "评估影响"]},
            {"name": "授权", "notes": ["匹配审批级", "明确资源上限"]},
            {"name": "行动", "notes": ["按证据推进", "小步试验"]},
            {"name": "复盘", "notes": ["检验结果", "更新标准"]},
        ],
        "quadrants": [
            {
                "name": "不可逆 × 高影响",
                "rows": [
                    {"field": "典型事项", "value": "厂房扩建"},
                    {"field": "审批级", "value": "管理委员会"},
                    {"field": "证据", "value": "需求与财务情景"},
                    {"field": "时间", "value": "建议 6 周评审"},
                    {"field": "复盘", "value": "里程碑复盘"},
                ],
            },
            {
                "name": "可逆 × 高影响",
                "rows": [
                    {"field": "典型事项", "value": "两产品线试点"},
                    {"field": "审批级", "value": "事业部"},
                    {"field": "证据", "value": "样本结果与回退演练"},
                    {"field": "时间", "value": "建议 2 周评审"},
                    {"field": "复盘", "value": "每周"},
                ],
            },
            {
                "name": "不可逆 × 低影响",
                "rows": [
                    {"field": "典型事项", "value": "部门制度固定"},
                    {"field": "审批级", "value": "部门负责人"},
                    {"field": "证据", "value": "影响与例外清单"},
                    {"field": "时间", "value": "建议 1 周"},
                    {"field": "复盘", "value": "每月"},
                ],
            },
            {
                "name": "可逆 × 低影响",
                "rows": [
                    {"field": "典型事项", "value": "局部界面试验"},
                    {"field": "审批级", "value": "产品 Owner"},
                    {"field": "证据", "value": "任务样本"},
                    {"field": "时间", "value": "建议 2 天"},
                    {"field": "复盘", "value": "结束复盘"},
                ],
            },
        ],
    },
    "R21": {
        "title": "决策前充分讨论，决定后按承诺执行",
        "subtitle": "新证据始终保留复核入口",
        "model": "共同事实 → 充分争论 → 明确批准 → 承诺执行 → 持续验证",
        "before_title": "阶段一：决策前（充分争论）",
        "after_title": "阶段二：决策后（坚决执行）",
        "before": [
            {"name": "共享事实", "lines": ["定义问题与范围", "标出关键假设", "暴露潜在风险", "避免群体思维"], "icon": "file-text"},
            {"name": "说明分歧", "lines": ["鼓励激烈反对", "提出反例观点", "预演反对意见", "争取共识承担"], "icon": "message-circle"},
            {"name": "给出反例", "lines": ["依赖数据与事实", "区分事实与观点", "量化影响与假设", "按证据分级"], "icon": "search"},
            {"name": "比较选项", "lines": ["生成多种选项", "比较优劣取舍", "明确取舍理由", "形成推荐方案"], "icon": "scale"},
        ],
        "after": [
            {"name": "资源签收", "lines": ["理解决策意图", "统一方向语言", "澄清关键要点", "凝聚团队合力"], "icon": "handshake"},
            {"name": "执行", "lines": ["决策者担责", "团队承担结果", "主动解决问题", "不推诿不甩锅"], "icon": "wrench"},
            {"name": "度量", "lines": ["全力以赴投入", "不打折不观望", "优先资源保障", "克服困难达成"], "icon": "chart-bar-increasing"},
            {"name": "复盘调整", "lines": ["设定成功指标", "持续跟踪数据", "评估实际结果", "反馈驱动迭代"], "icon": "refresh-ccw"},
        ],
        "bad_path": {
            "title": "伪共识路径：反复推翻但不给新证据",
            "nodes": [
                {"name": "表面同意", "icon": "users"},
                {"name": "私下质疑", "icon": "search"},
                {"name": "执行打折", "icon": "wrench"},
                {"name": "结果失真", "icon": "chart-bar-increasing"},
            ],
        },
        "good_path": {
            "title": "有效争论路径：依约执行并主动暂停",
            "nodes": [
                {"name": "记录异议", "icon": "message-circle"},
                {"name": "形成决议", "icon": "scale"},
                {"name": "全力执行", "icon": "wrench"},
                {"name": "结果可证", "icon": "chart-bar-increasing"},
            ],
        },
        "rules": [
            {
                "name": "异议留记录",
                "icon": "file-text",
                "lines": ["针对观点与证据", "保留反例"],
            },
            {
                "name": "批准人明确",
                "icon": "users",
                "lines": ["权衡取舍", "决议即时生效"],
            },
            {
                "name": "执行边界不漂移",
                "icon": "target",
                "lines": ["不消极折扣", "主动清障"],
            },
            {
                "name": "新证据触发复核",
                "icon": "refresh-ccw",
                "lines": ["用事实复核", "质量优先"],
            },
        ],
        "closing": "敢于决策前说不同意见，也愿意在决策后承担执行责任",
    },
    "R22": {
        "title": "一个结果由一名负责人闭合，防止职责漂移",
        "subtitle": "六段责任链与权责边界建议",
        "chain": [
            {
                "name": "发现客户问题",
                "artifact": "客户问题单",
                "owner": "产品",
                "icon": "search",
                "result": "单一问题",
                "result_lines": ["全员对齐同一问题", "优先级无冲突"],
                "drift": "多目标冲突",
                "drift_lines": ["多个目标并行", "优先级互相挤压"],
            },
            {
                "name": "明确成功条件",
                "artifact": "成功条件卡",
                "owner": "业务",
                "icon": "target",
                "result": "唯一成功标准",
                "result_lines": ["一人拍板结果定义", "标准可核验"],
                "drift": "多人解释",
                "drift_lines": ["多人同时负责", "责任被分散"],
            },
            {
                "name": "组织资源",
                "artifact": "资源签收表",
                "owner": "负责人",
                "icon": "users",
                "result": "专属团队",
                "result_lines": ["稳定服务该使命", "容量不挪用"],
                "drift": "资源争夺",
                "drift_lines": ["团队兼顾多任务", "响应不断切换"],
            },
            {
                "name": "执行验证",
                "artifact": "试验记录",
                "owner": "项目",
                "icon": "wrench",
                "result": "验证可控",
                "result_lines": ["输入和护栏聚焦", "固定节奏推进"],
                "drift": "共享资源",
                "drift_lines": ["资源被多方争用", "保障不足"],
            },
            {
                "name": "跟踪结果",
                "artifact": "结果仪表盘",
                "owner": "分析",
                "icon": "chart-bar-increasing",
                "result": "结果可核对",
                "result_lines": ["输入结果同源", "持续改善"],
                "drift": "指标混乱",
                "drift_lines": ["输入指标不聚焦", "难以驱动"],
            },
            {
                "name": "沉淀改善",
                "artifact": "复盘记录",
                "owner": "平台",
                "icon": "refresh-ccw",
                "result": "结果可复制",
                "result_lines": ["结果与责任强绑定", "复盘可追踪"],
                "drift": "责任模糊",
                "drift_lines": ["结果归属难界定", "复盘慢"],
            },
        ],
        "charter_title": "Leader Charter：负责人五项权责",
        "charter": [
            {
                "name": "决策权",
                "icon": "scale",
                "lines": ["对方向/方案/取舍有最终权", "跨组决策不受阻"],
            },
            {
                "name": "专属投入",
                "icon": "users",
                "lines": ["负责人全程投入", "团队容量不挪用"],
            },
            {
                "name": "端到端范围",
                "icon": "target",
                "lines": ["从问题定义到结果交付", "对全链路负责"],
            },
            {
                "name": "成功度量",
                "icon": "chart-bar-increasing",
                "lines": ["输入与结果指标公开", "按固定节奏评审"],
            },
            {
                "name": "升级路径",
                "icon": "refresh-ccw",
                "lines": ["阻塞可升级到更高层", "对象与时限明确"],
            },
        ],
        "closing": "一条责任线贯穿始终：一人全责 → 一队专属 → 一套资源 → 一组指标 → 一个结果",
    },
    "R23": {
        "title": "小团队降低协作复杂度，清晰接口比减员更关键",
        "subtitle": "关系数仅为全连接假设下的示意",
        "formula_title": "沟通复杂度随规模平方增长",
        "formula": "n(n−1) / 2",
        "formula_note": "n 为团队人数；每增加一人，潜在双向链路增加 n−1 条。",
        "metrics": [
            {"name": "8 人团队", "value": "28", "calc": "8×7/2"},
            {"name": "20 人团队", "value": "190", "calc": "20×19/2"},
        ],
        "network_title": "组织网络密度对比",
        "networks": [
            {"count": 8, "label": "8 人全连接（28）"},
            {"count": 20, "label": "20 人全连接（190）"},
        ],
        "behavior_title": "大团队问题与小队收益",
        "large_title": "大团队",
        "small_title": "两支 8 人小队",
        "large_rows": [
            {"name": "会议更多", "note": "同步成本高", "icon": "alarm-clock"},
            {"name": "交接增多", "note": "信息损耗", "icon": "refresh-ccw"},
            {"name": "角色模糊", "note": "责任分散", "icon": "users"},
            {"name": "决策缓慢", "note": "等待共识", "icon": "scale"},
        ],
        "small_rows": [
            {"name": "目标清晰", "note": "一个客户目标", "icon": "target"},
            {"name": "接口清晰", "note": "单一接口", "icon": "handshake"},
            {"name": "自有指标", "note": "结果可核验", "icon": "chart-bar-increasing"},
            {"name": "快速迭代", "note": "缩短反馈", "icon": "refresh-ccw"},
        ],
        "canvas_title": "Team Design Canvas｜12 周试点提案",
        "canvas": [
            {
                "name": "使命",
                "question": "解决什么？",
                "icon": "target",
                "lines": ["首次配置", "客户独立完成", "证据可核"],
            },
            {
                "name": "客户",
                "question": "服务谁？",
                "icon": "users",
                "lines": ["小型商户", "首次使用", "同类任务"],
            },
            {
                "name": "输入",
                "question": "获得什么？",
                "icon": "box",
                "lines": ["需求工件", "批准资源", "权限边界"],
            },
            {
                "name": "输出",
                "question": "交付什么？",
                "icon": "file-text",
                "lines": ["可用方案", "测试报告", "回退记录"],
            },
            {
                "name": "机制",
                "question": "如何合作？",
                "icon": "handshake",
                "lines": ["单一 Owner", "接口签收", "每周复核"],
            },
            {
                "name": "护栏",
                "question": "不能突破什么？",
                "icon": "shield-check",
                "lines": ["质量门", "隐私门", "预算门"],
            },
        ],
        "principles": [
            {"name": "目标单一", "note": "共同围绕客户任务"},
            {"name": "接口清晰", "note": "交接有签收标准"},
            {"name": "授权匹配", "note": "责任与资源一致"},
            {"name": "证据同源", "note": "结果可重算复核"},
            {"name": "异常可停", "note": "触线立即暂停"},
        ],
    },
    "R24": {
        "title": "责任范围从任务延伸到客户与长期价值",
        "subtitle": "授权边界必须与责任范围同步清晰",
        "scopes": [
            {"english": "Long-Term Value", "chinese": "长期价值", "note": "为未来创造持续价值"},
            {"english": "Company", "chinese": "组织", "note": "组织健康与可持续"},
            {"english": "Business", "chinese": "业务", "note": "业务结果与增长"},
            {"english": "Customer", "chinese": "客户", "note": "客户体验与价值"},
            {"english": "My Team", "chinese": "我的团队", "note": "团队目标与能力"},
            {"english": "My Task", "chinese": "我的任务", "note": "可交付结果"},
        ],
        "mindset_columns": ["维度", "租用式思维", "担当式思维"],
        "mindset_rows": [
            ["时间视野", "关注本期任务完成", "兼顾长期能力与价值"],
            ["问题响应", "被动响应、等待指令", "主动定义并预防问题"],
            ["资源使用", "只用授权范围资源", "为结果争取必要资源"],
            ["取舍判断", "局部指标优先", "客户与整体价值优先"],
            ["问责方式", "对任务结果负责", "对结果、影响和改进负责"],
        ],
        "journey_title": "Owner Journey｜从任务到影响",
        "journey": [
            {"name": "扩大视野", "actions": ["理解业务全景", "识别上下游"]},
            {"name": "主动识别", "actions": ["深入客户数据", "找到根因"]},
            {"name": "构建方案", "actions": ["设定目标路径", "比较取舍"]},
            {"name": "争取资源", "actions": ["跨组协作", "获得授权"]},
            {"name": "执行度量", "actions": ["高标准交付", "用数据复核"]},
            {"name": "沉淀复制", "actions": ["固化机制", "扩大影响"]},
        ],
        "checklist_title": "决策前五问",
        "checklist": [
            {
                "question": "长期影响是什么？",
                "check": "未来 3–5 年仍正确？",
                "icon": "alarm-clock",
            },
            {
                "question": "客户获得什么？",
                "check": "是否真正提升结果？",
                "icon": "users",
            },
            {
                "question": "业务影响是什么？",
                "check": "增长、成本、效率？",
                "icon": "chart-bar-increasing",
            },
            {
                "question": "代价是否可逆？",
                "check": "投入与回退成本？",
                "icon": "refresh-ccw",
            },
            {
                "question": "谁承担最终结果？",
                "check": "授权与问责一致？",
                "icon": "target",
            },
        ],
        "checklist_note": "跨部门资源未明确授权时仍须批准",
    },
    "R25": {
        "title": "输入指标连接客户与业务结果，关系需要持续检验",
        "subtitle": "连接线为待验证机制，不是因果估计",
        "input_factors": [
            {"name": "接口完备", "note": "契约可签收", "icon": "handshake"},
            {"name": "测试覆盖", "note": "条件有证据", "icon": "shield-check"},
            {"name": "有效模块", "note": "可用且稳定", "icon": "box"},
            {"name": "数据完备", "note": "来源可追溯", "icon": "database"},
            {"name": "交付节奏", "note": "签收时点明确", "icon": "alarm-clock"},
            {"name": "问题闭环", "note": "异常有 Owner", "icon": "refresh-ccw"},
        ],
        "owners": [
            {"name": "架构负责人", "note": "接口清单"},
            {"name": "质量负责人", "note": "测试记录"},
            {"name": "平台负责人", "note": "模块目录"},
            {"name": "数据负责人", "note": "来源索引"},
            {"name": "PMO", "note": "签收时间戳"},
            {"name": "业务负责人", "note": "异常复盘"},
        ],
        "experience": [
            {"name": "交付等待", "note": "签收到可执行", "icon": "alarm-clock"},
            {"name": "问题定位", "note": "证据链清楚", "icon": "search"},
            {"name": "验收稳定", "note": "质量门一致", "icon": "shield-check"},
            {"name": "方案适配", "note": "满足任务约束", "icon": "target"},
            {"name": "服务体验", "note": "反馈及时闭合", "icon": "users"},
        ],
        "behavior": [
            {"name": "模块采用", "note": "实际引用", "icon": "box"},
            {"name": "复购意愿", "note": "持续选择", "icon": "refresh-ccw"},
            {"name": "反馈参与", "note": "主动回流", "icon": "message-circle"},
            {"name": "按期签收", "note": "减少返工", "icon": "file-text"},
            {"name": "规则遵循", "note": "门禁不绕过", "icon": "scale"},
        ],
        "output": [
            {"name": "按期项目", "note": "里程碑完成", "icon": "target"},
            {"name": "留存客户", "note": "持续使用", "icon": "users"},
            {"name": "可复用资产", "note": "证据齐全", "icon": "database"},
            {"name": "质量结果", "note": "阻断项清零", "icon": "shield-check"},
        ],
        "financial": [
            {
                "name": "长期价值",
                "note": "客户与能力积累",
                "icon": "chart-bar-increasing",
            },
            {"name": "经营韧性", "note": "风险下保持交付", "icon": "shield-check"},
            {"name": "投资回报", "note": "价值与投入匹配", "icon": "scale"},
            {"name": "持续增长", "note": "选择空间扩大", "icon": "refresh-ccw"},
        ],
        "network_edges": [
            *[{"from": ["input", i], "to": ["owner", i]} for i in range(6)],
            {"from": ["owner", 0], "to": ["experience", 0]},
            {"from": ["owner", 0], "to": ["experience", 1], "indirect": True},
            {"from": ["owner", 1], "to": ["experience", 2]},
            {"from": ["owner", 1], "to": ["experience", 4]},
            {"from": ["owner", 2], "to": ["experience", 0]},
            {"from": ["owner", 2], "to": ["experience", 3]},
            {"from": ["owner", 3], "to": ["experience", 1]},
            {"from": ["owner", 3], "to": ["experience", 3], "indirect": True},
            {"from": ["owner", 4], "to": ["experience", 0]},
            {"from": ["owner", 4], "to": ["experience", 4]},
            {"from": ["owner", 5], "to": ["experience", 2]},
            {"from": ["owner", 5], "to": ["experience", 4]},
            {"from": ["experience", 0], "to": ["behavior", 0]},
            {"from": ["experience", 0], "to": ["behavior", 3]},
            {"from": ["experience", 1], "to": ["behavior", 2]},
            {"from": ["experience", 2], "to": ["behavior", 3]},
            {"from": ["experience", 2], "to": ["behavior", 4]},
            {"from": ["experience", 3], "to": ["behavior", 0], "indirect": True},
            {"from": ["experience", 3], "to": ["behavior", 1]},
            {"from": ["experience", 4], "to": ["behavior", 1]},
            {"from": ["experience", 4], "to": ["behavior", 2]},
            {"from": ["behavior", 0], "to": ["output", 0]},
            {"from": ["behavior", 0], "to": ["output", 2]},
            {"from": ["behavior", 1], "to": ["output", 1]},
            {"from": ["behavior", 2], "to": ["output", 2], "indirect": True},
            {"from": ["behavior", 3], "to": ["output", 0]},
            {"from": ["behavior", 4], "to": ["output", 3]},
            {"from": ["output", 0], "to": ["financial", 0]},
            {"from": ["output", 0], "to": ["financial", 2]},
            {"from": ["output", 1], "to": ["financial", 2]},
            {"from": ["output", 1], "to": ["financial", 3]},
            {"from": ["output", 2], "to": ["financial", 0], "indirect": True},
            {"from": ["output", 2], "to": ["financial", 1]},
            {"from": ["output", 3], "to": ["financial", 1]},
            {"from": ["output", 3], "to": ["financial", 3]},
        ],
        "table_columns": [
            "指标类型",
            "定义",
            "典型指标举例",
            "衡量频率",
            "主要 Owner",
            "可行动性",
            "管理目的",
        ],
        "table_rows": [
            [
                "Input Metrics\n输入指标",
                "可直接控制的投入或能力建设",
                "接口完备、测试覆盖、有效模块、数据完备",
                "日/周",
                "架构/质量/平台",
                "高",
                "驱动体验与行为改善",
            ],
            [
                "Guardrail Metrics\n护栏指标",
                "监控风险并保护长期价值",
                "质量阻断、隐私事件、回退能力、合规偏差",
                "日/周",
                "质量/安全/合规",
                "中—高",
                "防止短期行为损害客户",
            ],
            [
                "Outcome Metrics\n结果指标",
                "最终业务与财务结果",
                "按期项目、客户留存、服务成本、项目毛利",
                "月/季",
                "业务/财务",
                "低",
                "评价战略与经营成效",
            ],
        ],
        "footnote": "实线=直接待验关系；虚线=间接待验关系。业务不同，强度和路径可能变化。",
    },
    "R26": {
        "title": "实验组合先分风险，学习循环必须有停机条件",
        "subtitle": "两组合成样本各 20 人，不宣称统计显著",
        "matrix_title": "创新组合矩阵",
        "quadrants": [
            {"name": "配置向导", "lines": ["价值高", "不确定性低", "优先小试"]},
            {"name": "整体重构", "lines": ["价值高", "不确定性高", "先验关键风险"]},
            {"name": "按钮文案", "lines": ["价值低", "不确定性低", "低资源快验"]},
            {"name": "复杂定制", "lines": ["价值低", "不确定性高", "暂缓并复核"]},
        ],
        "matrix_note": "价值与成本均为当前判断；先做可逆试验，再更新组合。",
        "cycle_title": "实验学习循环",
        "cycle": [
            {"name": "假设", "artifact": "假设单", "note": "可检验的问题", "icon": "lightbulb"},
            {"name": "最小方案", "artifact": "原型", "note": "最小范围实现", "icon": "box"},
            {"name": "实验设计", "artifact": "样本方案", "note": "分层与随机化", "icon": "wrench"},
            {"name": "指标观测", "artifact": "结果表", "note": "收集并判断", "icon": "chart-bar-increasing"},
            {"name": "学习", "artifact": "判断记录", "note": "证伪与新假设", "icon": "search"},
            {"name": "放大/终止", "artifact": "批准或终止记录", "note": "按阈值决策", "icon": "refresh-ccw"},
        ],
        "decision": "是否达到\n成功标准？",
        "metrics_title": "关键指标梯",
        "metrics": [
            {
                "name": "首次完成率",
                "baseline": "70%",
                "sample": "85%",
                "note": "20 人样本",
                "icon": "target",
            },
            {
                "name": "完成时长",
                "baseline": "32 分钟",
                "sample": "24 分钟",
                "note": "中位数",
                "icon": "alarm-clock",
            },
            {
                "name": "错误率",
                "baseline": "20%",
                "sample": "10%",
                "note": "关键错误",
                "icon": "shield-check",
            },
            {
                "name": "满意度",
                "baseline": "3.2",
                "sample": "3.8",
                "note": "5 分制",
                "icon": "users",
            },
        ],
        "guardrails": [
            {
                "name": "可逆试验",
                "lines": ["预算≤30万", "期限8周", "回退演练"],
                "icon": "refresh-ccw",
            },
            {
                "name": "护栏指标",
                "lines": ["严重隐私=0", "错误>15%暂停", "质量批准"],
                "icon": "shield-check",
            },
            {
                "name": "样本窗口",
                "lines": ["每组20人", "统一任务", "保留失败样本"],
                "icon": "users",
            },
            {
                "name": "复盘沉淀",
                "lines": ["记录假设", "证据与反例", "批准后扩样"],
                "icon": "database",
            },
        ],
    },
    "R27": {
        "title": "固定指标与固定节奏，让异常在结果形成前暴露",
        "subtitle": "WBR 合成示例｜只看异常、明确行动、闭环跟踪",
        "flow": [
            "Goals｜目标",
            "Input Metrics｜输入",
            "Actual vs Target｜实绩",
            "Variance｜差异",
            "Root Cause｜根因",
            "Owner｜负责人",
            "Action｜行动",
            "Next Review｜复盘",
        ],
        "table_columns": [
            "目标",
            "输入指标",
            "W-5  W-4  W-3  W-2  W-1  W0",
            "差异",
            "根因",
            "Owner",
            "行动",
            "复盘",
        ],
        "rows": [
            {
                "icon": "handshake",
                "goal": "接口完备",
                "goal_definition": "接口契约可签收",
                "metric": "有契约模块占比",
                "target": 85,
                "target_label": "85%",
                "weeks": ["W-5", "W-4", "W-3", "W-2", "W-1", "W0"],
                "values": [52, 58, 64, 69, 75, 78],
                "format": '0"%"',
                "variance": "−7pp",
                "direction": "▼",
                "relative": "相对目标 −8.2%",
                "causes": ["15 个缺说明", "版本签收延迟"],
                "owner": "架构负责人",
                "action": "补齐接口契约\n抽查 10 项",
                "review": "10/02",
            },
            {
                "icon": "shield-check",
                "goal": "验证覆盖",
                "goal_definition": "测试证据覆盖条件",
                "metric": "条件覆盖率",
                "target": 85,
                "target_label": "85%",
                "weeks": ["W-5", "W-4", "W-3", "W-2", "W-1", "W0"],
                "values": [68, 70, 73, 74, 76, 76],
                "format": '0"%"',
                "variance": "−9pp",
                "direction": "▼",
                "relative": "相对目标 −10.6%",
                "causes": ["8 个无记录", "样本条件漏项"],
                "owner": "质量负责人",
                "action": "补测阻断项\n冻结记录",
                "review": "10/02",
            },
            {
                "icon": "alarm-clock",
                "goal": "交付等待",
                "goal_definition": "跨组交付更快",
                "metric": "签收至可执行天数",
                "target": 3.0,
                "target_label": "≤3 天",
                "weeks": ["W-5", "W-4", "W-3", "W-2", "W-1", "W0"],
                "values": [4.5, 4.3, 4.1, 3.9, 3.7, 3.6],
                "format": "0.0",
                "variance": "+0.6d",
                "direction": "▲",
                "relative": "高于目标 20%",
                "causes": ["接口反复确认", "资源签收滞后"],
                "owner": "PMO",
                "action": "单一入口\n限时签收",
                "review": "10/09",
            },
            {
                "icon": "box",
                "goal": "模块采用",
                "goal_definition": "复用真实发生",
                "metric": "实际引用率",
                "target": 40,
                "target_label": "40%",
                "weeks": ["W-5", "W-4", "W-3", "W-2", "W-1", "W0"],
                "values": [28, 31, 33, 35, 34, 34],
                "format": '0"%"',
                "variance": "−6pp",
                "direction": "▼",
                "relative": "相对目标 −15%",
                "causes": ["文档不完整", "检索命中偏低"],
                "owner": "平台负责人",
                "action": "补索引与示例\n复核引用",
                "review": "10/09",
            },
            {
                "icon": "users",
                "goal": "客户验收",
                "goal_definition": "验收无阻断",
                "metric": "无阻断项目占比",
                "target": 90,
                "target_label": "90%",
                "weeks": ["W-5", "W-4", "W-3", "W-2", "W-1", "W0"],
                "values": [72, 75, 78, 77, 80, 82],
                "format": '0"%"',
                "variance": "−8pp",
                "direction": "▼",
                "relative": "相对目标 −8.9%",
                "causes": ["质量门执行不一", "问题定位较慢"],
                "owner": "业务负责人",
                "action": "统一门禁\n异常 12h 上报",
                "review": "10/16",
            },
        ],
        "mechanism_title": "WBR 六项机制",
        "mechanisms": [
            {"name": "相同定义", "note": "统一字段口径\n统一更新粒度", "icon": "file-text"},
            {"name": "固定节奏", "note": "每周更新模板\n会前冻结数据", "icon": "alarm-clock"},
            {"name": "只看异常", "note": "聚焦偏差趋势\n正常项快速略过", "icon": "search"},
            {
                "name": "不讲故事",
                "note": "事实证据先行\n根因单独验证",
                "icon": "chart-bar-increasing",
            },
            {"name": "明确行动", "note": "单一 Owner\n明确截止日期", "icon": "target"},
            {"name": "闭环追踪", "note": "下次核对结果\n未闭环继续跟踪", "icon": "refresh-ccw"},
        ],
        "anomaly_columns": ["指标", "差异", "方向", "阈值", "备注"],
        "anomalies": [
            ["接口完备", "−7pp", "↓", "−5pp", "需整改"],
            ["验证覆盖", "−9pp", "↓", "−5pp", "需整改"],
            ["等待天数", "+0.6d", "↑", "+0.5d", "需整改"],
            ["模块采用", "−6pp", "↓", "−5pp", "需整改"],
        ],
        "root_title": "根因树：模块采用低于目标",
        "root_nodes": [
            "采用率−6pp",
            "检索命中−2pp",
            "工件不全−4pp",
            "标签缺失",
            "示例不足",
            "接口说明缺",
            "测试证据缺",
            "补元数据",
            "补示例",
            "补契约",
            "补记录",
        ],
        "root_edges": [
            [0, 1],
            [0, 2],
            [1, 3],
            [1, 4],
            [2, 5],
            [2, 6],
            [3, 7],
            [4, 8],
            [5, 9],
            [6, 10],
        ],
        "threshold_columns": ["指标类型", "建议阈值"],
        "thresholds": [
            ["规模类", "±5%"],
            ["比率类", "±5pp"],
            ["效率类", "±0.5d"],
            ["质量类", "阻断即停"],
        ],
        "footnote": "数据截至 W0 周日；所有数值为授权合成样本，不代表真实经营结果。",
    },
    "R28": {
        "title": "用六段备忘录建立共同事实，会议只做澄清与决策",
        "subtitle": "时间分配为建议",
        "sections": [
            {
                "name": "背景",
                "icon": "file-text",
                "points": ["两条产品线需求与约束", "相关数据及口径", "成功指标与约束"],
                "questions": ["事实是否一致？", "有哪些限制？"],
            },
            {
                "name": "问题",
                "icon": "search",
                "points": ["是否直接扩建", "范围与时点", "决策需要什么证据"],
                "questions": ["不解决会怎样？", "何时必须决定？"],
            },
            {
                "name": "洞察",
                "icon": "lightbulb",
                "points": ["收益证据仍不足", "失败代价较高", "可逆试点可换证据"],
                "questions": ["本质矛盾是什么？", "哪些洞察改变选择？"],
            },
            {
                "name": "选项",
                "icon": "scale",
                "points": ["直接扩建", "先做试点", "维持现状"],
                "questions": ["还有别的选项？", "假设能否验证？"],
            },
            {
                "name": "建议",
                "icon": "target",
                "points": ["先做 12 周试点", "预算上限 120 万", "产品/质量双签"],
                "questions": ["为何现在选择它？", "成功如何衡量？"],
            },
            {
                "name": "证据与风险",
                "icon": "shield-check",
                "points": ["样本局限", "回退路径", "预算与质量门"],
                "questions": ["证据充分吗？", "如何及早应对？"],
            },
        ],
        "compare_columns": ["维度", "演示文稿", "叙事备忘录"],
        "compare_rows": [
            ["信息密度", "每页信息少、跨页补充", "完整信息可独立阅读"],
            ["逻辑完整", "依赖讲者串联", "按逻辑链展开并留痕"],
            ["阅读节奏", "被动接收", "静读、回看、可复核"],
            ["讨论质量", "易从表态开始", "聚焦证据与取舍"],
        ],
        "meeting_title": "会议推进：先异步理解，再高质量讨论",
        "meeting": [
            {
                "name": "静读",
                "duration": "10 分钟",
                "icon": "file-text",
                "lines": ["标注问题", "先形成理解"],
            },
            {
                "name": "澄清",
                "duration": "10 分钟",
                "icon": "search",
                "lines": ["只问事实口径", "补齐约束"],
            },
            {
                "name": "比较",
                "duration": "20 分钟",
                "icon": "message-circle",
                "lines": ["比较选项", "讨论风险"],
            },
            {
                "name": "决议",
                "duration": "10 分钟",
                "icon": "shield-check",
                "lines": ["记录选择与理由", "Owner/截止/停机"],
            },
        ],
    },
    "R29": {
        "title": "长期影响与失败代价一起比较，先用试点换证据",
        "subtitle": "评分为合成主观示意，不等于投资回报",
        "timeline": [
            {"name": "当前约束", "note": "事实与资源边界", "icon": "users"},
            {
                "name": "12 周结果",
                "note": "形成样本证据",
                "icon": "chart-bar-increasing",
            },
            {"name": "1 年能力", "note": "机制与团队积累", "icon": "database"},
            {"name": "3 年选择空间", "note": "保留增长与回退", "icon": "goal"},
            {"name": "未来回望", "note": "检验今天是否后悔", "icon": "search"},
        ],
        "matrix_title": "行动 × 可逆性遗憾矩阵",
        "quadrants": [
            {
                "name": "可逆行动",
                "lines": ["策略：快速验证", "例：小试失败可回退", "代价：有限成本"],
            },
            {
                "name": "不可逆行动",
                "lines": ["策略：补情景证据", "例：扩建需求未证实", "代价：长期固定"],
            },
            {
                "name": "可逆不行动",
                "lines": ["策略：设复核期限", "例：暂缓局部试验", "代价：错过学习"],
            },
            {
                "name": "不可逆不行动",
                "lines": ["策略：比较机会代价", "例：错过一次性窗口", "代价：机会沉没"],
            },
        ],
        "score_title": "两选项五维评分",
        "option_names": ["直接扩建", "可逆试点"],
        "scores": [
            {"name": "客户收益", "criterion": "任务完成改善", "icon": "users", "expand": 4, "trial": 4},
            {
                "name": "长期能力",
                "criterion": "机制与团队积累",
                "icon": "chart-bar-increasing",
                "expand": 5,
                "trial": 4,
            },
            {"name": "现金压力", "criterion": "预算占用与承压", "icon": "scale", "expand": 1, "trial": 4},
            {"name": "回退能力", "criterion": "失败后的可恢复性", "icon": "refresh-ccw", "expand": 1, "trial": 5},
            {"name": "证据充分", "criterion": "样本与反例覆盖", "icon": "search", "expand": 2, "trial": 4},
        ],
        "score_note": "两方案均使用 1–5 分共同量尺；等权合计仅用于展开讨论，不代表 ROI。",
        "paths": [
            {
                "choice": {"name": "选择试点", "note": "可逆行动"},
                "investment": {"name": "投入上限", "note": "120 万元"},
                "branches": [
                    {"probability": "p 成功", "result": "扩样 / 再批准"},
                    {"probability": "1−p 未达", "result": "回退 / 保留证据"},
                ],
                "reflection": [
                    "尝试后获得客户证据",
                    "即使失败仍可回退",
                    "超预算或质量阻断即停",
                ],
            },
            {
                "choice": {"name": "选择暂缓", "note": "保留现金"},
                "investment": {"name": "观察窗口", "note": "约定复核"},
                "branches": [
                    {"probability": "q 机会出现", "result": "重评 / 启动试点"},
                    {"probability": "1−q 消失", "result": "结束 / 记录理由"},
                ],
                "reflection": [
                    "暂缓保住当前资源",
                    "须说明是否错过机会",
                    "p/q 未知，不填概率数字",
                ],
            },
        ],
    },
    "R30": {
        "title": "原则落到行为、反例和机制，才能进入组织日常",
        "subtitle": "拟制度｜用于两支跨职能小队试点",
        "center": "组织原则\n操作系统",
        "principles": [
            {
                "name": "客户价值",
                "icon": "users",
                "lines": ["访问真实任务", "衡量客户结果", "关注长期影响"],
            },
            {
                "name": "承担结果",
                "icon": "target",
                "lines": ["闭合异常", "明确单一 Owner", "持续改进"],
            },
            {
                "name": "深入事实",
                "icon": "search",
                "lines": ["核对来源", "追问根因", "记录反例"],
            },
            {
                "name": "快速验证",
                "icon": "lightbulb",
                "lines": ["小步试验", "设停机条件", "用证据扩围"],
            },
            {
                "name": "简化协作",
                "icon": "handshake",
                "lines": ["明确接口", "减少等待", "固定节奏"],
            },
            {
                "name": "守住质量",
                "icon": "shield-check",
                "lines": ["阻断即停", "安全优先", "质量签字"],
            },
        ],
        "lifecycle_title": "原则嵌入人才与业务生命周期",
        "lifecycle": [
            {"name": "招聘", "note": "识别客户任务意识"},
            {"name": "面试", "note": "行为证据问答"},
            {"name": "入组决策", "note": "确认责任边界"},
            {"name": "晋升", "note": "核查长期影响"},
            {"name": "绩效", "note": "核对事实与行动"},
            {"name": "领导力复制", "note": "培训并审核机制"},
        ],
        "lifecycle_conclusion": "原则贯穿选人、用人、评价与复制，并以可观察行为持续校准",
        "table_columns": ["原则", "可观察行为", "反例", "机制"],
        "table_rows": [
            [
                "客户价值",
                "访问真实任务；衡量结果；查看失败任务",
                "只猜需求；追逐报表",
                "访谈工件；客户结果表",
            ],
            [
                "承担结果",
                "闭合异常；单一 Owner；异常有签字",
                "只转交邮件；责任分散",
                "责任签收；升级路径",
            ],
            [
                "深入事实",
                "核对数据；保留来源；来源能重算",
                "只看结论；忽略反例",
                "来源抽查；复算记录",
            ],
            [
                "快速验证",
                "小步试验；设停止线；小试能回退",
                "未经证据扩围；直接上线",
                "试点门；回退演练",
            ],
            [
                "简化协作",
                "明确接口；固定节奏；接口有版本",
                "扩大会议；重复审批",
                "接口协议；版本签收",
            ],
            [
                "守住质量",
                "暂停阻断；双签确认；阻断先停",
                "进度压过安全；隐瞒异常",
                "质量签字；阻断清单",
            ],
        ],
    },
    "R32": {
        "title": "Agent 三层记忆架构",
        "subtitle": "任务、知识与推理连接成可追溯 Context Graph",
        "pipeline_title": "输入与抽取",
        "inputs": [
            {"name": "用户问题 / 对话消息", "icon": "message-circle"},
            {"name": "政策文档 / 业务工件", "icon": "file-text"},
        ],
        "pipeline": [
            {"name": "实体识别", "icon": "search"},
            {"name": "域规则补全", "icon": "file-text"},
            {"name": "歧义澄清", "icon": "message-circle"},
            {"name": "置信合并", "icon": "chart-bar-increasing"},
            {"name": "归一", "icon": "target"},
            {"name": "关系抽取", "icon": "handshake"},
            {"name": "来源绑定", "icon": "database"},
        ],
        "pipeline_note": "先低成本识别实体\n再用域规则补全约束\n最后绑定来源",
        "graph_title": "Context Graph / 记忆图谱",
        "memories": {
            "short": {
                "title": "短期记忆",
                "definition": "记住刚发生了什么",
                "icon": "alarm-clock",
                "items": [
                    {"name": "User", "icon": "users"},
                    {"name": "Session", "icon": "users"},
                    {"name": "Message", "icon": "message-circle"},
                    {"name": "Intent", "icon": "target"},
                    {"name": "Constraint", "icon": "shield-check"},
                ],
                "note": "保持当前任务不断线",
            },
            "long": {
                "title": "长期记忆",
                "definition": "记住业务世界稳定存在什么",
                "icon": "database",
                "items": [
                    {"name": "Product", "icon": "box"},
                    {"name": "Policy", "icon": "file-text"},
                    {"name": "Region", "icon": "target"},
                    {"name": "Channel", "icon": "handshake"},
                    {"name": "Condition", "icon": "scale"},
                    {"name": "Restriction", "icon": "shield-check"},
                    {"name": "DocumentChunk", "icon": "file-text"},
                ],
                "note": "沉淀对象、规则与来源",
            },
            "reason": {
                "title": "推理记忆",
                "definition": "记住 Agent 为什么这么做",
                "icon": "brain-circuit",
                "items": [
                    {"name": "ReasoningTrace", "icon": "brain-circuit"},
                    {"name": "ToolCall", "icon": "wrench"},
                    {"name": "Evidence", "icon": "file-text"},
                    {"name": "Decision", "icon": "scale"},
                    {"name": "Answer", "icon": "message-circle"},
                    {"name": "Feedback", "icon": "refresh-ccw"},
                ],
                "note": "记录决策轨迹与复盘",
            },
        },
        "relations_title": "关键关系链（最小可用版本）",
        "relations": [
            [
                {"node": "Message", "relation": "MENTIONS"},
                {"node": "Entity", "relation": "SUPPORTED_BY"},
                {"node": "DocumentChunk"},
            ],
            [
                {"node": "Message", "relation": "TRIGGERED"},
                {"node": "ReasoningTrace", "relation": "CALLED"},
                {"node": "ToolCall", "relation": "RETURNED"},
                {"node": "Evidence"},
            ],
            [
                {"node": "Decision", "relation": "PRODUCED"},
                {"node": "Answer", "relation": "GOT"},
                {"node": "Feedback"},
            ],
        ],
        "governance_title": "治理价值",
        "governance": [
            "实体可归一、去重、关联",
            "规则与偏好分离治理",
            "答案追溯到证据版本",
            "定位失败链与工具调用",
            "反馈进入人工复核",
        ],
        "protection": "保护：按权限检索\n用户/会话隔离\n日志脱敏",
        "core_idea": "把聊天记录变成上下文，把知识文档变成实体关系，把模型回答变成可追溯决策链。",
    },
}


RENDERERS = {
    "R16": render_r16,
    "R17": render_r17,
    "R18": render_r18,
    "R19": render_r19,
    "R20": render_r20,
    "R21": render_r21,
    "R22": render_r22,
    "R23": render_r23,
    "R24": render_r24,
    "R25": render_r25,
    "R26": render_r26,
    "R27": render_r27,
    "R28": render_r28,
    "R29": render_r29,
    "R30": render_r30,
    "R32": render_r32,
}


_SEMANTICS = {
    "title": "结论先行的页面主张；必须能回答本页业务问题。",
    "subtitle": "证据边界、样本口径或建议属性，不重复标题。",
    "steps": "顶部流程的阶段名称、说明与图标；维持原顺序和方向。",
    "rows": "表格或诊断明细；每行应是可比较且口径一致的完整记录。",
    "columns": "结构列及列内节点；列序表达因果、阶段或记忆类型。",
    "edges": "节点之间的直接或间接关系；不可按线性流程替代。",
    "comparison": "同一维度上的成对差异；两侧文本粒度应一致。",
    "metrics": "名称、基线、样本或计算口径；样本不得写成已验证结果。",
    "chart": "原生图表数据；series 保留名称和值数组。",
    "table": "原生表格数据；首行与各列语义保持稳定。",
    "note": "解释、限制或来源口径，字号低于结论但不可省略。",
}


def _value_contract(name, value):
    if isinstance(value, list):
        contract = {
            "type": "array",
            "min_capacity": len(value),
            "semantic": _SEMANTICS.get(name, "保持默认值所示的信息角色与视觉容量。"),
        }
        if value:
            contract["items"] = _value_contract("item", value[0])
        return contract
    if isinstance(value, dict):
        return {
            "type": "object",
            "min_capacity": len(value),
            "semantic": _SEMANTICS.get(
                name, "组合字段必须共同支撑该组件，不可只填标题。"
            ),
            "fields": {
                key: _value_contract(key, child) for key, child in value.items()
            },
        }
    if isinstance(value, bool):
        kind = "boolean"
    elif isinstance(value, (int, float)):
        kind = "number"
    else:
        kind = "string"
    return {
        "type": kind,
        "min_capacity": 1,
        "semantic": _SEMANTICS.get(name, "按默认示例的内容角色填写，保持相近长度。"),
    }


LAYOUT_CONTRACTS = {
    "R16": {
        "business_question": "组织如何保持客户驱动，并识别从活力走向迟缓的早期信号？",
        "reading_order": [
            "标题与证据边界",
            "左上四象限循环",
            "右上五步衰退链",
            "左下防御机制",
            "中下活力曲线",
            "右下预警信号",
        ],
        "layout_reason": "左循环说明健康机制，右链说明退化方向，下方三栏分别给出防御、趋势和可观察信号，形成模型—风险—行动闭环。",
        "text_roles": {
            "headline": "结论",
            "cycle": "健康运行机制",
            "decline": "风险假设",
            "defense": "责任动作与工件",
            "signals": "监测项与来源",
        },
        "preserve_relations": [
            "四项循环必须闭合",
            "五步衰退必须单向",
            "曲线必须区分上升与衰退",
            "信号须与复核来源成对",
        ],
    },
    "R17": {
        "business_question": "怎样把客户声音转成可验证的体验改进？",
        "reading_order": [
            "六步闭环",
            "左下五维对照",
            "右上雷达差距",
            "右下倾听—洞察—行动回流",
        ],
        "layout_reason": "顶部先建立闭环方法，左侧纠正思维方式，右侧用雷达暴露差距并落到行动，阅读重心由框架转向证据。",
        "text_roles": {
            "steps": "客户闭环",
            "comparison": "方法差异",
            "radar": "三组样本轮廓",
            "actions": "证据到行动",
        },
        "preserve_relations": [
            "第六步反馈必须回到第一步",
            "五维对照逐行对应",
            "雷达保留三组序列",
            "行动结束回到客户价值",
        ],
    },
    "R18": {
        "business_question": "投入开发前，如何先定义客户结果、证据与批准门？",
        "reading_order": [
            "顶部七步逆推",
            "左右顺向/反向思维",
            "中央客户结果文档",
            "底部六个决策门",
        ],
        "layout_reason": "中央大文档是决策锚点，左右楔形把两种思维压向同一工件，底部门将抽象方法转为逐关验收。",
        "text_roles": {
            "steps": "逆推问题链",
            "document": "客户结果真源",
            "sides": "两种推导逻辑",
            "gates": "最低验收条件",
        },
        "preserve_relations": [
            "顶部按从结果向投入的逆向阅读",
            "中心文档宽度最大",
            "左右箭头均指向文档",
            "六门按顺序连接",
        ],
    },
    "R19": {
        "business_question": "哪些可控杠杆能让客户价值、规模和成本形成持续循环？",
        "reading_order": [
            "左侧线性/复利对照",
            "中央八节点主回路与双小回路",
            "右侧四杠杆",
            "底部机制公式",
        ],
        "layout_reason": "飞轮占据视觉中心以表达系统性，左侧解释为何单点动作不足，右侧标注可操作杠杆，底部把机制压缩成管理语言。",
        "text_roles": {
            "comparison": "一次性与复利差异",
            "flywheel": "八段主机制",
            "levers": "局部杠杆与假设",
            "formula": "机制摘要",
        },
        "preserve_relations": [
            "八节点首尾闭合",
            "两条虚线小回路保留",
            "杠杆必须含影响与待验假设",
            "公式不得写成确定性因果",
        ],
    },
    "R20": {
        "business_question": "决策的审批、证据和复盘成本应如何匹配影响与可逆性？",
        "reading_order": [
            "顶部五步分类流程",
            "纵向影响轴",
            "横向可逆轴",
            "四象限原生表格",
        ],
        "layout_reason": "先给决策动作，再用双轴矩阵定位事项；四格保持相同五字段，便于逐项比较决策成本。",
        "text_roles": {
            "steps": "判断流程",
            "axes": "分类维度",
            "quadrants": "审批与证据规则",
        },
        "preserve_relations": [
            "影响轴高低方向完整",
            "可逆轴左右方向完整",
            "四格各保留五字段",
            "表格须为原生数据槽",
        ],
    },
    "R21": {
        "business_question": "如何兼顾决策前的充分争论与决策后的稳定执行？",
        "reading_order": [
            "决策前四步",
            "中央授权关口",
            "决策后四步",
            "双路径对照",
            "四项规则",
            "底部承诺",
        ],
        "layout_reason": "中央关口把争论和执行分成两个阶段；中部双路径展示行为后果；规则区给出可执行边界。",
        "text_roles": {
            "before": "共同事实与分歧",
            "gate": "批准边界",
            "after": "签收、执行和复盘",
            "paths": "负向/正向行为链",
            "rules": "操作准则",
        },
        "preserve_relations": [
            "左右阶段经中央关口连接",
            "双路径同层对照",
            "新证据可触发复核",
            "底部口号为行为收口",
        ],
    },
    "R22": {
        "business_question": "一个跨部门结果如何由单一负责人沿全链路闭合？",
        "reading_order": [
            "顶部六段定义卡",
            "中部六节点单线程泳道",
            "下部六节点矩阵漂移泳道",
            "底部五项权责与责任收束条",
        ],
        "layout_reason": "同一横坐标对应同一责任阶段，上泳道表现顺畅传递，下泳道以交叉虚线呈现责任漂移，底部再明确授权。",
        "text_roles": {
            "chain": "阶段、工件、Owner",
            "single": "理想结果",
            "matrix": "常见漂移",
            "charter": "权责边界",
        },
        "preserve_relations": [
            "六阶段横坐标对齐",
            "上下各六节点均保留标题和两行解释",
            "单线程实线连续且有方向",
            "矩阵泳道保留交叉虚线",
            "五项权责各保留两条说明",
            "底部责任链收束条不可省略",
        ],
    },
    "R23": {
        "business_question": "怎样通过小团队和接口设计降低协作复杂度？",
        "reading_order": [
            "左上公式与数值",
            "中上两张网络图",
            "右上行为对照",
            "下部团队画布",
            "底部原则",
        ],
        "layout_reason": "公式给出规模效应，网络图直观呈现密度差异，行为区解释业务后果，画布承接到团队设计。",
        "text_roles": {
            "formula": "假设与计算",
            "networks": "关系密度证据",
            "behavior": "组织表现",
            "canvas": "团队设计字段",
        },
        "preserve_relations": [
            "8 人与 20 人网络密度明显不同，并对应 28 / 190 条关系",
            "关系数与公式一致",
            "团队画布保留使命/客户/输入/输出/机制/护栏六列",
            "数值只作全连接示意",
        ],
    },
    "R24": {
        "business_question": "管理者的责任应扩展到哪些范围，授权边界如何同步？",
        "reading_order": [
            "左上向下嵌套责任范围",
            "右上五维思维表",
            "左下六步成长路线",
            "右下五问清单",
        ],
        "layout_reason": "嵌套半椭圆表现责任由任务向长期价值外扩，表格解释观念变化，底部路线和清单提供行动与门禁。",
        "text_roles": {
            "scopes": "责任范围层级",
            "mindset": "租用式/担当式对照",
            "journey": "成长动作",
            "checklist": "决策前校验",
        },
        "preserve_relations": [
            "责任层必须向下收束嵌套",
            "六层各自保留英文名、中文名与责任解释",
            "五维逐行对照",
            "六步路线有顺序",
            "清单保留复选框语义",
        ],
    },
    "R25": {
        "business_question": "哪些输入指标通过客户体验与行为连接业务和财务结果？",
        "reading_order": [
            "顶部五段箭头",
            "投入因子与 Owner 双列",
            "体验—行为—业务—财务多对多网络",
            "底部指标口径表",
        ],
        "layout_reason": "多列网络而非漏斗用于表达一对多和多对多机制；底部表格补足定义、工件、频率与 Owner，防止关系图失去可操作性。",
        "text_roles": {
            "columns": "五类指标节点",
            "edges": "直接/间接待验关系",
            "financial_value": "长期结果",
            "table": "指标治理口径",
        },
        "preserve_relations": [
            "五列顺序固定",
            "保留投入6+Owner6、体验5、行为5、业务4、财务终值4及完整多对多关系",
            "四项财务终值置于同一高长框并以虚线分隔",
            "五段栏头之间保留方向箭头",
            "实虚线语义不同",
            "底部3×7表格必须为原生数据槽且首列为深蓝导航",
        ],
    },
    "R26": {
        "business_question": "如何按客户价值与方案不确定性配置实验，并设置学习和停机机制？",
        "reading_order": [
            "左侧 2×2 组合矩阵",
            "中部实验循环与判断分支",
            "右侧指标梯",
            "底部护栏",
        ],
        "layout_reason": "三栏分别回答做什么、怎样学、如何判断；底部全宽护栏约束所有实验。",
        "text_roles": {
            "quadrants": "组合选择",
            "cycle": "实验工件链",
            "decision": "达标/不达标分支",
            "metrics": "小样本结果",
            "guardrails": "预算、时间、隐私、停机",
        },
        "preserve_relations": [
            "矩阵双轴完整",
            "六步循环含放大/终止并必须回流",
            "判断分支含达标与未达标",
            "护栏横跨三栏",
        ],
    },
    "R27": {
        "business_question": "WBR 如何在结果形成前发现偏差、定位根因并闭环整改？",
        "reading_order": [
            "顶部八列 WBR 导航带",
            "左侧五行八字段原生 WBR 表",
            "右侧机制说明",
            "左下异常表",
            "中下根因树",
            "右下阈值表",
        ],
        "layout_reason": "大表承载逐指标事实与微趋势，右侧固定复盘规则；底部从异常筛选进入根因展开和阈值校准。",
        "text_roles": {
            "rows": "指标周度记录",
            "microcharts": "六周趋势",
            "mechanisms": "复盘纪律",
            "anomalies": "异常摘要",
            "root": "根因与动作树",
            "thresholds": "触发条件",
        },
        "preserve_relations": [
            "顶部八列导航与主表列线对齐",
            "五行指标与五个单实际序列微折线对应",
            "每条趋势保留六周实际数值，目标值留在目标与偏差字段",
            "第一列保留圆形图标、目标和目标定义",
            "偏差保留数值、单位、方向和相对变动",
            "异常必须来自主表且保留四行",
            "根因树至少十节点",
            "Owner、行动、复盘日期不得缺失",
        ],
    },
    "R28": {
        "business_question": "怎样用完整备忘录建立共同事实，并让会议聚焦决策？",
        "reading_order": [
            "左侧折角纸张六段备忘录",
            "右上四维对照表",
            "右下四步会议流程",
        ],
        "layout_reason": "纸张形态强化连续叙事，边注迫使作者自问；右侧先说明载体差异，再给出会议节奏。",
        "text_roles": {
            "sections": "六段正文与作者自问",
            "compare": "载体差异",
            "meeting": "时间盒和输出",
        },
        "preserve_relations": [
            "六段纵向箭头连续",
            "每段含三条内容和两条边注",
            "右上保持表格语义",
            "会议四步依次连接",
        ],
    },
    "R29": {
        "business_question": "面对长期选择，怎样同时比较收益、失败代价和回退能力？",
        "reading_order": [
            "顶部五节点长期链",
            "左中遗憾矩阵",
            "右中五维评分",
            "底部两条路径",
        ],
        "layout_reason": "时间链把视角拉长；矩阵与评分从两种角度比较选项；路径推演将评分还原为可观察后果。",
        "text_roles": {
            "timeline": "时间视角",
            "quadrants": "行动/不行动遗憾",
            "scores": "两选项主观评分",
            "paths": "条件化情景推演",
        },
        "preserve_relations": [
            "时间链注明推演性质",
            "两组选项用同一五维评分",
            "评分不冒充 ROI",
            "两条路径保留 p/1−p 与 q/1−q 互斥分支及未来回望",
        ],
    },
    "R30": {
        "business_question": "组织原则如何转成可观察行为、反例和日常机制？",
        "reading_order": [
            "左侧中心原则与六张放射卡",
            "左下人才生命周期",
            "右侧六行机制表",
        ],
        "layout_reason": "放射网表达原则互相制约，表格把抽象词转成可观察行为和机制，生命周期说明落地载体。",
        "text_roles": {
            "principles": "原则与行为定义",
            "network": "互相制约",
            "table": "行为/反例/机制",
            "lifecycle": "制度嵌入点",
        },
        "preserve_relations": [
            "六原则连接中心并保留中间节点",
            "机制表逐行对应原则",
            "六步生命周期保持顺序",
            "关系图与表格不可互相替代",
        ],
    },
    "R32": {
        "business_question": "Agent 如何把当前任务、稳定知识与推理轨迹连接成可追溯决策链？",
        "reading_order": [
            "左侧输入与七步抽取",
            "中央三层记忆",
            "层间双向关系与回流",
            "底部三条关系链",
            "右下治理价值",
            "核心思想条",
        ],
        "layout_reason": "3:2 画布把抽取管线置于左侧入口，中央三色高卡强调记忆职责分离，底部关系链给出最小图谱语法，橙色治理区承接可审计价值。",
        "text_roles": {
            "pipeline": "实体与来源处理",
            "memories": "短期/长期/推理对象",
            "relations": "带动词的关系三元组",
            "governance": "治理价值与保护",
        },
        "preserve_relations": [
            "画布保持 3:2",
            "记忆主列蓝/青绿/蓝；关系链实体与文档青绿、推理轨迹与工具调用紫，其余蓝；治理区橙",
            "三层记忆标题下保留各自职责定义",
            "短期与长期、长期与推理为双向",
            "推理反馈回流短期",
            "三条关系链必须保留独立节点和关系动词",
            "Message→ReasoningTrace→ToolCall→Evidence 四节点链不可把 ToolCall 降为边标签",
            "治理区保持橙色",
        ],
    },
}


SCHEMAS = {
    ref_id: {
        "type": "object",
        "business_question": LAYOUT_CONTRACTS[ref_id]["business_question"],
        "reading_order": LAYOUT_CONTRACTS[ref_id]["reading_order"],
        "layout_reason": LAYOUT_CONTRACTS[ref_id]["layout_reason"],
        "text_roles": LAYOUT_CONTRACTS[ref_id]["text_roles"],
        "preserve_relations": LAYOUT_CONTRACTS[ref_id]["preserve_relations"],
        "fields": {
            name: _value_contract(name, value)
            for name, value in DEFAULTS[ref_id].items()
        },
    }
    for ref_id in RENDERERS
}
