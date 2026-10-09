"""Build fixed SVG pages from a small structured spec.

This helper is intentionally narrower than ``build_gold_svg_page.py``. It keeps
cover, agenda, simple introduction, and sparse photo-dark interlude pages on a
fixed SVG route so weak models only provide slots instead of hand-authoring coordinates.
"""

from __future__ import annotations

import argparse
import html
import json
import re
from pathlib import Path
from typing import Any

W, H = 1280, 720
FONT = "Microsoft YaHei, Arial"
SERIF_FONT = "Noto Serif SC, Source Han Serif SC, Songti SC, Microsoft YaHei, serif"
SANS_FONT = "Noto Sans SC, Microsoft YaHei, Arial, sans-serif"
SCHEMA_VERSION = "fixed_svg_page/v1"
SAFE_X, SAFE_Y, SAFE_W, SAFE_H = 94, 74, 1091, 573
AGENDA_PREFIX_RE = re.compile(
    r"^\s*(?:第\s*)?(?:0?[1-9]|[1-9]\d)\s*(?:[.)）、:：-]\s*|\s+|(?=[\u4e00-\u9fff]))"
)
CHINESE_AGENDA_PREFIX_RE = re.compile(
    r"^\s*(?:第\s*)?[一二三四五六七八九十]{1,3}\s*(?:[.)）、:：-]\s*|\s+)"
)
HEX_COLOR_RE = re.compile(r"^#[0-9A-Fa-f]{3}(?:[0-9A-Fa-f]{3})?(?:[0-9A-Fa-f]{2})?$")

THEMES: dict[str, dict[str, str]] = {
    "business_blue": {
        "background": "#F8FAFC",
        "surface": "#FFFFFF",
        "surface_alt": "#F4F7FB",
        "title_text": "#0F172A",
        "body_text": "#334155",
        "muted_text": "#64748B",
        "accent": "#2563EB",
        "accent2": "#0EA5E9",
        "border": "#D9E2EC",
    },
    "dark_business": {
        "background": "#0D1117",
        "surface": "#0F2438",
        "surface_alt": "#132D46",
        "title_text": "#FFFFFF",
        "body_text": "#D8E7FF",
        "muted_text": "#8CA3C7",
        "accent": "#45D1FF",
        "accent2": "#A7F3D0",
        "border": "#2B4C7E",
    },
    "tech_dark": {
        "background": "#07111F",
        "surface": "#0F172A",
        "surface_alt": "#111827",
        "title_text": "#F8FAFC",
        "body_text": "#CBD5E1",
        "muted_text": "#94A3B8",
        "accent": "#6366F1",
        "accent2": "#22D3EE",
        "border": "#334155",
    },
    "deepseek_dark": {
        "background": "#07111F",
        "surface": "#07111F",
        "surface_alt": "#0B1F35",
        "title_text": "#F8FAFC",
        "body_text": "#D8E7FF",
        "muted_text": "#9FB3D1",
        "accent": "#4CC9F0",
        "accent2": "#7DD3FC",
        "border": "#27496D",
    },
    "literary_documentary_cn": {
        "background": "#0B0F14",
        "surface": "#111827",
        "surface_alt": "#1F2937",
        "title_text": "#FFFFFF",
        "body_text": "#F5F1E8",
        "muted_text": "#D6C8B8",
        "accent": "#A16207",
        "accent2": "#E7D2A4",
        "border": "#8A6A3E",
    },
}
TOKEN_ALIASES = {
    "background-color": "background",
    "background_color": "background",
    "background_fallback": "background",
    "title_text-color": "title_text",
    "title_text_color": "title_text",
    "body_text-color": "body_text",
    "body_text_color": "body_text",
    "accent-color": "accent",
    "accent_color": "accent",
    "primary": "accent",
    "muted_text-color": "muted_text",
    "muted_text_color": "muted_text",
    "muted": "muted_text",
    "neutral": "muted_text",
    "surface-color": "surface",
    "surface_color": "surface",
    "border-color": "border",
    "border_color": "border",
}
FIXED_PAGE_DEFAULT_REF_ALIASES = {
    "background-color-ref": "background",
    "title_text-color-ref": "title_text",
    "body_text-color-ref": "body_text",
    "accent-color-ref": "accent",
    "muted_text-color-ref": "muted_text",
    "surface-color-ref": "surface",
    "border-color-ref": "border",
}


def _esc(value: Any) -> str:
    return html.escape(str(value or ""), quote=True)


def _dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _tokens(spec: dict[str, Any]) -> dict[str, str]:
    theme_id = str(spec.get("theme_id") or "business_blue")
    tokens = dict(THEMES.get(theme_id, THEMES["business_blue"]))
    framework_theme = _dict(_dict(spec.get("deck_framework")).get("theme"))
    style_manifest = _dict(spec.get("style_manifest") or spec.get("style_manifest_snapshot"))
    style_sources = [
        _dict(style_manifest.get("palette")),
        _dict(style_manifest.get("theme_tokens")),
        _dict(style_manifest.get("tokens")),
        style_manifest,
    ]
    for source in (framework_theme, *style_sources, spec.get("visual_tokens"), spec):
        _apply_token_source(tokens, source)
    _apply_fixed_page_object_defaults(tokens, style_manifest)
    return tokens


def _apply_token_source(tokens: dict[str, str], source: Any) -> None:
    if not isinstance(source, dict):
        return
    for raw_key, value in source.items():
        key = TOKEN_ALIASES.get(str(raw_key), str(raw_key))
        if key in tokens and isinstance(value, str) and HEX_COLOR_RE.match(value.strip()):
            tokens[key] = value.strip().upper()


def _apply_fixed_page_object_defaults(tokens: dict[str, str], style_manifest: dict[str, Any]) -> None:
    fixed_defaults = _dict(_dict(style_manifest.get("object_defaults")).get("fixed_page"))
    if not fixed_defaults:
        return
    palette = _dict(style_manifest.get("palette"))
    palette_tokens = dict(tokens)
    _apply_token_source(palette_tokens, palette)
    for raw_key, raw_ref in fixed_defaults.items():
        target = FIXED_PAGE_DEFAULT_REF_ALIASES.get(str(raw_key))
        if target is None or not isinstance(raw_ref, str):
            continue
        ref = TOKEN_ALIASES.get(raw_ref.strip(), raw_ref.strip())
        value = palette_tokens.get(ref)
        if value and HEX_COLOR_RE.match(value):
            tokens[target] = value


def _text(value: Any, default: str = "") -> str:
    if isinstance(value, str):
        cleaned = value.strip()
        return cleaned or default
    return default


def _number(value: Any, default: float) -> float:
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value.strip())
        except ValueError:
            return default
    return default


def _items(spec: dict[str, Any]) -> list[dict[str, str]]:
    raw_items = spec.get("items")
    if not isinstance(raw_items, list):
        raw_items = []
    normalized: list[dict[str, str]] = []
    for item in raw_items:
        if isinstance(item, str):
            title = item.strip()
            subtitle = ""
        elif isinstance(item, dict):
            title = _text(item.get("title") or item.get("label"))
            children = item.get("children") or item.get("childrens")
            if isinstance(children, list):
                subtitle = " / ".join(str(child).strip() for child in children[:3] if str(child).strip())
            else:
                subtitle = _text(item.get("description") or item.get("subtitle"))
        else:
            continue
        if title:
            normalized.append({"title": _strip_agenda_number(title), "subtitle": subtitle})
    return normalized


def _strip_agenda_number(title: str) -> str:
    """Remove model-supplied agenda numbering; SVG generator owns final indexes."""

    cleaned = AGENDA_PREFIX_RE.sub("", title, count=1)
    cleaned = CHINESE_AGENDA_PREFIX_RE.sub("", cleaned, count=1)
    return cleaned.strip() or title.strip()


def _text_units(text: str) -> float:
    units = 0.0
    for char in text:
        if char.isspace():
            units += 0.35
        elif ord(char) < 128:
            units += 0.58
        else:
            units += 1.0
    return units


def _wrap(text: str, max_units: float, max_lines: int, *, ellipsis: bool = True) -> list[str]:
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return []
    lines: list[str] = []
    current = ""
    current_units = 0.0
    for char in text:
        char_units = _text_units(char)
        if current and current_units + char_units > max_units:
            lines.append(current.rstrip())
            current = ""
            current_units = 0.0
            if len(lines) >= max_lines:
                break
        current += char
        current_units += char_units
    if current and len(lines) < max_lines:
        lines.append(current.rstrip())
    if ellipsis and len(lines) == max_lines and len("".join(lines)) < len(text):
        lines[-1] = lines[-1].rstrip("，。；、 ") + "..."
    return lines


def _agenda_columns(count: int) -> int:
    if count <= 6:
        return 1
    if count <= 12:
        return 2
    return 3


def _agenda_gap(rows: int, columns: int) -> float:
    base_gap = 18 if columns == 1 else 14 if columns == 2 else 10
    if rows >= 12:
        base_gap = min(base_gap, 5)
    elif rows >= 8:
        base_gap = min(base_gap, 8)
    return float(base_gap)


def _agenda_font_size(row_h: float, columns: int, count: int) -> int:
    if columns == 1:
        preferred = 24 if count <= 4 else 23
    elif columns == 2:
        preferred = 22 if count <= 8 else 20
    else:
        preferred = 19 if count <= 18 else 17 if count <= 24 else 15
    return max(10, min(preferred, int(row_h * 0.42)))


def _agenda_layout(count: int, *, has_subtitle: bool) -> dict[str, float | int]:
    columns = _agenda_columns(count)
    rows = (count + columns - 1) // columns
    list_top = 189 if has_subtitle else 176
    # 固定页最终还会叠加框架层页码/页脚；目录内容只使用 760px 以上区域。
    list_bottom = 568 if columns == 1 and count >= 5 else 594
    gap_y = _agenda_gap(rows, columns)
    if rows > 1:
        max_gap = max(2.0, (list_bottom - list_top) * 0.18 / (rows - 1))
        gap_y = min(gap_y, max_gap)
    row_h = (list_bottom - list_top - max(rows - 1, 0) * gap_y) / rows
    col_gap = 0 if columns == 1 else 67 if columns == 2 else 38
    col_w = (SAFE_W - (columns - 1) * col_gap) / columns
    title_font = _agenda_font_size(row_h, columns, count)
    number_font = max(12, min(26, title_font + 4))
    number_gap = 86 if columns == 1 else 69 if columns == 2 else 51
    text_y = min(max(22.0, row_h * 0.5), row_h - title_font * 0.35)
    max_title_lines = 2 if row_h >= title_font * 2.55 else 1
    title_units = max(8.0, (col_w - number_gap - 18) / max(title_font, 1))
    return {
        "columns": columns,
        "rows": rows,
        "list_top": list_top,
        "gap_y": gap_y,
        "row_h": row_h,
        "col_gap": col_gap,
        "col_w": col_w,
        "title_font": title_font,
        "number_font": number_font,
        "number_gap": number_gap,
        "text_y": text_y,
        "max_title_lines": max_title_lines,
        "title_units": title_units,
    }


def _text_block(
    *,
    x: float,
    y: float,
    lines: list[str],
    fill: str,
    size: int,
    weight: int = 400,
    line_gap: int = 1,
    attrs: str = "",
    font: str = FONT,
) -> list[str]:
    out: list[str] = []
    for index, line in enumerate(lines):
        yy = y + index * (size + line_gap)
        out.append(
            f'<text x="{x:.1f}" y="{yy:.1f}" fill="{fill}" '
            f'font-family="{font}" font-size="{size}" font-weight="{weight}"{attrs}>'
            f"{_esc(line)}</text>"
        )
    return out


def _fixed_variant(spec: dict[str, Any]) -> str:
    return _text(
        spec.get("variant")
        or spec.get("layout_variant")
        or spec.get("background_variant_ref")
        or spec.get("visual_polarity")
    )


def _photo_dark_role(kind: str) -> str:
    if kind == "section_divider":
        return "fixed-section-divider"
    if kind == "closing":
        return "fixed-closing"
    return "fixed-photo-dark-cover"


def _photo_dark_safe_region(spec: dict[str, Any], *, kind: str, align: str) -> dict[str, float]:
    raw = spec.get("title_safe_region")
    if isinstance(raw, dict):
        x = _number(raw.get("x"), 128)
        y = _number(raw.get("y"), 188)
        w = _number(raw.get("w"), 900)
        h = _number(raw.get("h"), 330)
    elif align == "left":
        x, y, w, h = 128.0, 186.0, 790.0, 330.0
    elif kind == "closing":
        x, y, w, h = 180.0, 214.0, 920.0, 300.0
    else:
        x, y, w, h = 160.0, 206.0, 960.0, 330.0
    x = max(72.0, min(x, W - 180.0))
    y = max(92.0, min(y, H - 220.0))
    w = max(360.0, min(w, W - x - 72.0))
    h = max(180.0, min(h, H - y - 92.0))
    return {"x": x, "y": y, "w": w, "h": h}


def build_photo_dark_serif_svg(spec: dict[str, Any], *, kind: str) -> str:
    """Build sparse fixed content for deck_framework-owned photo_dark pages."""

    tokens = _tokens(spec)
    title = _text(spec.get("title"), "未命名主题")
    subtitle = _text(spec.get("subtitle") or spec.get("tagline"))
    kicker = _text(spec.get("kicker") or spec.get("chapter_label") or spec.get("meta"))
    quote = _text(spec.get("quote_text") or spec.get("quote"))
    align = _text(spec.get("title_align"), "center" if kind in {"cover", "closing"} else "left")
    if align not in {"left", "center"}:
        align = "center"
    region = _photo_dark_safe_region(spec, kind=kind, align=align)
    title_units = _text_units(title)
    title_size = 58 if title_units <= 18 else 52 if title_units <= 34 else 46
    max_units = max(12.0, region["w"] / (title_size * 0.92))
    title_lines = _wrap(title, max_units, 3)
    anchor = ' text-anchor="middle"' if align == "center" else ""
    text_x = region["x"] + region["w"] / 2 if align == "center" else region["x"]
    accent_w = 118.0 if kind != "closing" else 82.0
    accent_x = text_x - accent_w / 2 if align == "center" else region["x"]
    role = _photo_dark_role(kind)

    parts = [
        (
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1280 720" '
            'data-layout-family="photo_dark_serif">'
        ),
        f'<g id="fixed-photo-dark-content" data-role="{role}">',
        f'<rect x="{accent_x:.1f}" y="{region["y"]:.1f}" width="{accent_w:.1f}" height="4" rx="0" fill="{tokens["accent"]}"/>',
    ]
    y = region["y"] + 42
    if kicker:
        parts.extend(
            _text_block(
                x=text_x,
                y=y,
                lines=_wrap(kicker, max(10.0, region["w"] / 15), 1),
                fill=tokens["muted_text"],
                size=16,
                weight=700,
                attrs=anchor,
                font=SANS_FONT,
            )
        )
        y += 84
    parts.extend(
        _text_block(
            x=text_x,
            y=y,
            lines=title_lines,
            fill=tokens["title_text"],
            size=title_size,
            weight=800,
            line_gap=12,
            attrs=anchor,
            font=SERIF_FONT,
        )
    )
    y += len(title_lines) * (title_size + 12) + 24
    if subtitle:
        parts.extend(
            _text_block(
                x=text_x,
                y=y,
                lines=_wrap(subtitle, max(18.0, region["w"] / 18), 2),
                fill=tokens["body_text"],
                size=22,
                weight=500,
                line_gap=8,
                attrs=anchor,
                font=SERIF_FONT,
            )
        )
    if quote:
        quote_y = min(region["y"] + region["h"] + 70, 612)
        parts.extend(
            _text_block(
                x=text_x,
                y=quote_y,
                lines=_wrap(quote, max(20.0, region["w"] / 17), 2),
                fill=tokens["muted_text"],
                size=18,
                weight=500,
                line_gap=8,
                attrs=anchor,
                font=SERIF_FONT,
            )
        )
    parts.append("</g></svg>")
    return "\n".join(parts)


def build_cover_svg(spec: dict[str, Any]) -> str:
    tokens = _tokens(spec)
    title = _text(spec.get("title"), "未命名主题")
    subtitle = _text(spec.get("subtitle") or spec.get("tagline"))
    meta = _text(spec.get("meta"))
    title_units = _text_units(title)
    title_size = 60 if title_units <= 22 else 54 if title_units <= 40 else 46
    title_lines = _wrap(title, max(18, 980 / (title_size * 0.92)), 3)
    subtitle_y = 264 + len(title_lines) * (title_size + 14) + 30

    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1280 720">',
        '<g id="fixed-cover-content" data-role="fixed-cover">',
        f'<rect x="109" y="147" width="973" height="374" rx="0" fill="{tokens["surface"]}" '
        f'stroke="{tokens["border"]}" stroke-width="2"/>',
        f'<rect x="154" y="195" width="134" height="6" rx="0" fill="{tokens["accent"]}"/>',
    ]
    parts.extend(
        _text_block(
            x=154,
            y=264,
            lines=title_lines,
            fill=tokens["title_text"],
            size=title_size,
            weight=700,
            line_gap=14,
        )
    )
    if subtitle:
        parts.extend(
            _text_block(
                x=157,
                y=subtitle_y,
                lines=_wrap(subtitle, 46, 2),
                fill=tokens["body_text"],
                size=26,
                weight=500,
                line_gap=8,
            )
        )
    if meta:
        parts.extend(
            _text_block(
                x=157,
                y=min(subtitle_y + 96 if subtitle else subtitle_y, 472),
                lines=_wrap(meta, 54, 1),
                fill=tokens["muted_text"],
                size=18,
                weight=400,
            )
        )
    parts.append("</g></svg>")
    return "\n".join(parts)


def build_agenda_svg(spec: dict[str, Any]) -> str:
    tokens = _tokens(spec)
    title = _text(spec.get("title"), "目录")
    subtitle = _text(spec.get("subtitle"))
    items = _items(spec)
    if not items:
        items = [{"title": "议程项待补", "subtitle": ""}]

    count = len(items)
    layout = _agenda_layout(count, has_subtitle=bool(subtitle))
    columns = int(layout["columns"])
    rows = int(layout["rows"])
    list_top = float(layout["list_top"])
    gap_y = float(layout["gap_y"])
    row_h = float(layout["row_h"])
    col_gap = float(layout["col_gap"])
    col_w = float(layout["col_w"])
    number_gap = float(layout["number_gap"])
    title_font = int(layout["title_font"])
    number_font = int(layout["number_font"])
    title_units = float(layout["title_units"])
    max_title_lines = int(layout["max_title_lines"])
    text_y = float(layout["text_y"])

    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1280 720">',
        '<g id="fixed-agenda-content" data-role="fixed-agenda">',
    ]
    parts.extend(
        _text_block(
            x=94,
            y=94,
            lines=_wrap(title, 36, 2),
            fill=tokens["title_text"],
            size=42,
            weight=700,
        )
    )
    parts.append(f'<rect x="94" y="118" width="96" height="5" rx="0" fill="{tokens["accent"]}"/>')
    if subtitle:
        parts.extend(
            _text_block(
                x=94,
                y=150,
                lines=_wrap(subtitle, 64, 1),
                fill=tokens["muted_text"],
                size=18,
            )
        )
    for index, item in enumerate(items):
        column = index // rows
        row = index % rows
        x = SAFE_X + column * (col_w + col_gap)
        y = list_top + row * (row_h + gap_y)
        number = f"{index + 1:02d}"
        parts.append(
            f'<g id="agenda-item-{index + 1}" data-role="agenda-item" '
            f'transform="translate({x:.1f},{y:.1f})">'
        )
        parts.append(f'<line x1="0" y1="0" x2="{col_w:.1f}" y2="0" stroke="{tokens["border"]}" stroke-width="2"/>')
        parts.append(
            f'<text x="22" y="{text_y:.1f}" fill="{tokens["accent"]}" '
            f'font-family="{FONT}" font-size="{number_font}" font-weight="700" '
            f'data-role="agenda-number">{number}</text>'
        )
        title_lines = _wrap(item["title"], title_units, max_title_lines)
        parts.extend(
            _text_block(
                x=number_gap,
                y=text_y,
                lines=title_lines,
                fill=tokens["title_text"],
                size=title_font,
                weight=700,
                line_gap=6 if columns < 3 else 4,
                attrs=' data-role="agenda-title"',
            )
        )
        if item["subtitle"] and columns == 1 and count < 5 and row_h >= 82 and len(title_lines) == 1:
            parts.extend(
                _text_block(
                    x=number_gap,
                    y=53,
                    lines=_wrap(item["subtitle"], 62, 1),
                    fill=tokens["muted_text"],
                    size=15,
                )
            )
        parts.append("</g>")
    parts.append("</g></svg>")
    return "\n".join(parts)


def build_introduction_svg(spec: dict[str, Any]) -> str:
    """Build a bounded 2-4 item introduction page without free-form geometry."""

    tokens = _tokens(spec)
    title = _text(spec.get("title"), "介绍")
    subtitle = _text(spec.get("subtitle"))
    items = _items(spec)
    if not 2 <= len(items) <= 4:
        raise ValueError("introduction fixed pages require 2 to 4 items")

    columns = len(items) if len(items) <= 3 else 2
    rows = 1 if len(items) <= 3 else 2
    gap_x = 22.0
    gap_y = 22.0
    grid_top = 208.0 if subtitle else 186.0
    grid_bottom = 594.0
    card_w = (SAFE_W - (columns - 1) * gap_x) / columns
    card_h = (grid_bottom - grid_top - (rows - 1) * gap_y) / rows
    item_title_size = 25 if columns <= 2 else 22
    item_body_size = 18 if rows == 1 else 16

    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1280 720">',
        '<g id="fixed-introduction-content" data-role="fixed-introduction">',
    ]
    parts.extend(
        _text_block(
            x=94,
            y=94,
            lines=_wrap(title, 36, 2),
            fill=tokens["title_text"],
            size=42,
            weight=700,
        )
    )
    parts.append(
        f'<rect x="94" y="118" width="96" height="5" rx="0" fill="{tokens["accent"]}"/>'
    )
    if subtitle:
        parts.extend(
            _text_block(
                x=94,
                y=154,
                lines=_wrap(subtitle, 64, 1),
                fill=tokens["muted_text"],
                size=18,
            )
        )

    for index, item in enumerate(items):
        row = index // columns
        column = index % columns
        x = SAFE_X + column * (card_w + gap_x)
        y = grid_top + row * (card_h + gap_y)
        parts.append(
            f'<g id="introduction-item-{index + 1}" data-role="introduction-item" '
            f'transform="translate({x:.1f},{y:.1f})">'
        )
        parts.append(
            f'<rect x="0" y="0" width="{card_w:.1f}" height="{card_h:.1f}" rx="12" '
            f'fill="{tokens["surface"]}" stroke="{tokens["border"]}" stroke-width="1"/>'
        )
        parts.append(f'<circle cx="32" cy="34" r="10" fill="{tokens["accent"]}"/>')
        parts.extend(
            _text_block(
                x=56,
                y=43,
                lines=_wrap(item["title"], max(10.0, (card_w - 82) / item_title_size), 2),
                fill=tokens["title_text"],
                size=item_title_size,
                weight=700,
                line_gap=6,
            )
        )
        if item["subtitle"]:
            parts.extend(
                _text_block(
                    x=30,
                    y=96 if rows == 1 else 88,
                    lines=_wrap(
                        item["subtitle"],
                        max(12.0, (card_w - 60) / item_body_size),
                        4 if rows == 1 else 2,
                    ),
                    fill=tokens["body_text"],
                    size=item_body_size,
                    weight=400,
                    line_gap=8,
                )
            )
        parts.append("</g>")
    parts.append("</g></svg>")
    return "\n".join(parts)


def build_fixed_svg_page(spec: dict[str, Any]) -> str:
    kind = _text(spec.get("kind") or spec.get("page_archetype"), "agenda")
    variant = _fixed_variant(spec)
    if kind in {"section_divider", "closing"} or variant in {"photo_dark_serif", "dark_photo_interlude"}:
        if kind not in {"cover", "section_divider", "closing"}:
            raise ValueError("photo_dark_serif fixed pages must be cover, section_divider, or closing")
        svg = build_photo_dark_serif_svg(spec, kind=kind)
    elif kind not in {"cover", "agenda", "introduction"}:
        raise ValueError("kind must be cover, agenda, introduction, section_divider, or closing")
    elif kind == "cover":
        svg = build_cover_svg(spec)
    elif kind == "introduction":
        svg = build_introduction_svg(spec)
    else:
        svg = build_agenda_svg(spec)
    font_family = _dict(spec.get("typography")).get("font_family")
    if font_family:
        svg = re.sub(r'font-family="[^"]*"', lambda match: f'font-family="{_esc(font_family)}"', svg)
    return svg


def build_template(kind: str) -> dict[str, Any]:
    if kind in {"section_divider", "closing"}:
        return {
            "schema_version": SCHEMA_VERSION,
            "kind": kind,
            "variant": "photo_dark_serif",
            "theme_id": "literary_documentary_cn",
            "kicker": "第一部分" if kind == "section_divider" else "尾声",
            "title": "回到命运，也回到自己",
            "subtitle": "章节转场只保留一句推进判断",
            "quote_text": "不是逃离命运，而是在命运中形成自己。" if kind == "closing" else "",
        }
    if kind == "cover":
        return {
            "schema_version": SCHEMA_VERSION,
            "kind": "cover",
            "theme_id": "business_blue",
            "title": "Ubrio 工作总结",
            "subtitle": "单页生成链路升级阶段汇报",
            "meta": "产品研发联席评审",
            "footer": "2026",
        }
    if kind == "introduction":
        return {
            "schema_version": SCHEMA_VERSION,
            "kind": "introduction",
            "theme_id": "business_blue",
            "title": "公司介绍",
            "subtitle": "用三点快速建立基本认知",
            "items": [
                {"title": "服务对象", "subtitle": "管理者与业务团队"},
                {"title": "核心能力", "subtitle": "材料到可汇报 PPT"},
                {"title": "交付特点", "subtitle": "可编辑、可追溯"},
            ],
        }
    return {
        "schema_version": SCHEMA_VERSION,
        "kind": "agenda",
        "theme_id": "business_blue",
        "title": "目录",
        "subtitle": "本次汇报围绕目标、路径、验证和计划展开",
        "items": [
            {"title": "目标与边界", "children": ["范围", "成功标准"]},
            {"title": "关键问题", "children": ["现状", "瓶颈"]},
            {"title": "方案路径", "children": ["架构", "流程"]},
            {"title": "验证结果", "children": ["PPTX", "PNG预览"]},
            {"title": "风险与动作", "children": ["缺口", "下一步"]},
        ],
        "footer": "内部汇报",
    }


def _load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("spec JSON must be an object")
    return data


def main() -> None:
    parser = argparse.ArgumentParser(description="Build fixed cover/agenda/introduction SVG from JSON.")
    parser.add_argument("--spec", type=Path, help="Fixed page spec JSON.")
    parser.add_argument("--output", type=Path, help="Output SVG path.")
    parser.add_argument("--write-template", type=Path, help="Write a fixed page spec template JSON.")
    parser.add_argument(
        "--kind",
        choices=["cover", "agenda", "introduction", "section_divider", "closing"],
        default="agenda",
    )
    args = parser.parse_args()

    if args.write_template:
        args.write_template.parent.mkdir(parents=True, exist_ok=True)
        args.write_template.write_text(
            json.dumps(build_template(args.kind), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        if args.spec is None:
            print(json.dumps({"ok": True, "template": str(args.write_template)}, ensure_ascii=False))
            return
    if args.spec is None:
        parser.error("--spec is required unless --write-template is used alone")
    spec = _load_json(args.spec)
    svg = build_fixed_svg_page(spec)
    if args.output is None:
        print(json.dumps({"ok": True, "svg": svg}, ensure_ascii=False))
        return
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(svg, encoding="utf-8")
    print(json.dumps({"ok": True, "output": str(args.output)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
