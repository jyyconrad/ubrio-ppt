"""SVG geometry and native data slots shared by reference compositions."""

from __future__ import annotations

import math
import xml.etree.ElementTree as ET

NS = "http://www.w3.org/2000/svg"
ET.register_namespace("", NS)
BLUE = "#082B66"
MID = "#1559A5"
LIGHT = "#EFF4FA"
INK = "#172438"
LINE = "#CDD5DF"
TEAL = "#138D98"
PURPLE = "#65458D"
FONT = "Noto Sans CJK SC"


def _attrs(values):
    return {k.replace("_", "-"): str(v) for k, v in values.items() if v is not None}


def wrap(value, width, size):
    """Wrap at character boundaries using conservative CJK advance widths."""
    output = []
    for paragraph in str(value).split("\n"):
        line, advance = "", 0.0
        for char in paragraph:
            step = size * (1.0 if ord(char) > 255 else 0.56)
            if line and advance + step > width:
                if char in "，。；：！？、）》】" and len(line) > 1:
                    last = line[-1]
                    output.append(line[:-1])
                    line = last
                    advance = size * (1.0 if ord(last) > 255 else 0.56)
                else:
                    output.append(line)
                    line, advance = "", 0.0
            line += char
            advance += step
        output.append(line)
    return output


class Svg:
    def __init__(self, width=1280, height=720):
        self.width, self.height = width, height
        self.root = ET.Element(f"{{{NS}}}svg", {
            "width": str(width), "height": str(height),
            "viewBox": f"0 0 {width} {height}",
            "data-native-data-ref": "native-data.json",
        })
        self.native = {"version": 1, "charts": [], "tables": []}

    def node(self, tag, **attrs):
        return ET.SubElement(self.root, f"{{{NS}}}{tag}", _attrs(attrs))

    def rect(self, x, y, w, h, fill=LIGHT, stroke=LINE, radius=5, **attrs):
        return self.node("rect", x=x, y=y, width=w, height=h,
                         fill=fill, stroke=stroke, rx=radius, **attrs)

    def circle(self, x, y, r, fill=BLUE, stroke="none", **attrs):
        return self.node("circle", cx=x, cy=y, r=r, fill=fill, stroke=stroke, **attrs)

    def line(self, x1, y1, x2, y2, color=BLUE, width=1.2, dashed=False):
        return self.node("line", x1=x1, y1=y1, x2=x2, y2=y2,
                         stroke=color, stroke_width=width,
                         stroke_dasharray="5 4" if dashed else None)

    def poly(self, points, fill=BLUE, stroke="none", **attrs):
        return self.node("polygon", points=" ".join(f"{x},{y}" for x, y in points),
                         fill=fill, stroke=stroke, **attrs)

    def path(self, d, fill="none", stroke=BLUE, width=2, dashed=False):
        return self.node("path", d=d, fill=fill, stroke=stroke, stroke_width=width,
                         stroke_dasharray="5 4" if dashed else None)

    def text(self, x, y, value, size=16, color=INK, bold=False, width=None,
             anchor="start", leading=None, role=None, max_lines=None):
        lines = wrap(value, width, size) if width else str(value).split("\n")
        if max_lines is not None:
            if not isinstance(max_lines, int) or isinstance(max_lines, bool) or max_lines < 1:
                raise ValueError("Text capacity must be a positive line count")
            if len(lines) > max_lines:
                raise ValueError(f"text exceeds {max_lines}-line capacity: {str(value)[:100]!r}")
        element = self.node("text", x=x, y=y, fill=color,
                            font_family=FONT, font_size=size,
                            font_weight="700" if bold else "400",
                            text_anchor=anchor, data_role=role, data_max_lines=max_lines)
        for index, line in enumerate(lines):
            tspan = ET.SubElement(element, f"{{{NS}}}tspan", {
                "x": str(x), "dy": str(0 if index == 0 else (leading or size * 1.4))
            })
            tspan.text = line
        return len(lines) * (leading or size * 1.4)

    def arrow(self, x1, y1, x2, y2, color=BLUE, width=2, dashed=False, both=False):
        self.line(x1, y1, x2, y2, color, width, dashed)
        theta = math.atan2(y2 - y1, x2 - x1)
        for x, y, angle in [(x2, y2, theta)] + ([(x1, y1, theta + math.pi)] if both else []):
            length = max(7, width * 3)
            self.poly([(x, y),
                       (x - length * math.cos(angle - 0.45), y - length * math.sin(angle - 0.45)),
                       (x - length * math.cos(angle + 0.45), y - length * math.sin(angle + 0.45))], color)

    def icon(self, name, x, y, size=34, color=BLUE, disc=False, disc_color=None):
        if disc:
            self.circle(x + size / 2, y + size / 2, size / 2 + 8, disc_color or BLUE)
            color = "#FFFFFF"
        return self.node("g", data_icon_id=name, data_icon_box=f"{x} {y} {size} {size}",
                         data_icon_color=color, data_icon_container="none", data_icon_inset="0.05")

    def number(self, x, y, value, radius=17):
        self.circle(x, y, radius)
        self.text(x, y + 6, value, 18, "#FFFFFF", True, anchor="middle")

    def title(self, value, subtitle=None, size=42, color=BLUE, x=26, y=61):
        advance = sum(1.0 if ord(char) > 255 else 0.56 for char in str(value))
        fitted = min(size, (self.width - x - 26) / max(advance, 1))
        if fitted < 26:
            raise ValueError("Title exceeds the reference's single-line capacity; shorten the judgment.")
        self.text(x, y, value, fitted, color, True)
        if subtitle:
            self.text(28, 92, subtitle, 17, INK, width=self.width - 56)

    def header(self, x, y, w, value, h=30, color=BLUE, size=19):
        self.rect(x, y, w, h, color, "none", 3)
        self.text(x + w / 2, y + h * 0.73, value, size, "#FFFFFF", True, anchor="middle")

    def band(self, value, y=658, h=42):
        self.header(24, y, self.width - 48, value, h, size=18)

    def bullets(self, x, y, items, width, size=16, gap=9, color=INK):
        position = y
        for value in items:
            position += self.text(x, position, str(value), size, color, width=width) + gap
        return position

    def ribbon(self, x, y, w, h, value, number=None, color=BLUE, size=18):
        self.poly([(x, y), (x + w - 14, y), (x + w, y + h / 2),
                   (x + w - 14, y + h), (x, y + h)], color)
        if number is not None:
            self.circle(x + 21, y + h / 2, 13, "#FFFFFF")
            self.text(x + 21, y + h / 2 + 5, number, 15, color, True, anchor="middle")
        self.text(x + w / 2 + (9 if number is not None else 0), y + h * 0.71,
                  value, size, "#FFFFFF", True, anchor="middle")

    def table(self, slot_id, x, y, w, h, columns, rows, widths=None, font_size=10.5, column_styles=None, row_heights=None, show_header=True):
        self.rect(x, y, w, h, "#FFFFFF", LINE, 0,
                  id=slot_id, data_role="native-table-slot", data_slot_id=slot_id,
                  data_x=x, data_y=y, data_w=w, data_h=h)
        self.native["tables"].append({
            "slot_id": slot_id, "columns": columns, "rows": rows,
            "show_header": show_header,
            "column_widths": widths or [],
            "column_styles": column_styles or [],
            "row_heights": row_heights or [],
            "style": {"font_size": font_size, "font_face": FONT,
                      "header_fill": BLUE, "header_text_color": "#FFFFFF",
                      "body_fill": LIGHT, "text_color": INK},
        })

    def chart(self, slot_id, x, y, w, h, labels, series, kind="bar", fmt="0", options=None):
        variant = "sparkline" if (options or {}).get("sparkline") is True else (
            "micro" if w < 320 or h < 200 else None)
        self.rect(x, y, w, h, "#FFFFFF", "none", 0,
                  id=slot_id, data_role="native-chart-slot", data_slot_id=slot_id,
                  data_x=x, data_y=y, data_w=w, data_h=h,
                  data_native_chart_variant=variant)
        axis = {"format": fmt}
        if kind == "bar":
            axis["minimum"] = 0
        self.native["charts"].append({
            "slot_id": slot_id, "kind": kind, "labels": labels, "series": series,
            "colors": [BLUE, "#A8BEDF"] if kind == "line" else ["#A8BEDF", BLUE],
            "point_colors": (["#A8BEDF"] * (len(labels) - 1) + [BLUE]) if kind == "bar" and len(series) == 1 else [],
            "style": {"font_face": FONT, "axis_text_color": INK, "grid_color": LINE},
            "options": {"show_title": False, "legend": len(series) > 1, "data_labels": True,
                        "value_axis": axis, **(options or {})},
        })

    def finish(self):
        return ET.tostring(self.root, encoding="unicode"), self.native
