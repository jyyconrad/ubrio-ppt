"""Build literary/editorial SVG DrawingML pages from structured JSON.

This helper covers the narrative layouts used by ``literary_documentary_cn``:
editorial image panels, 2/3-up story cards, and book/quote comparison pages.
It deliberately keeps full-page background ownership in ``deck_framework`` and
only declares local image slots for renderer-side native picture overlay.
"""

from __future__ import annotations

import argparse
import html
import json
import re
from pathlib import Path
from typing import Any

W, H = 1280, 720
SCHEMA_VERSION = "editorial_svg_page/v1"
SERIF = "Noto Serif SC, Source Han Serif SC, Songti SC, Microsoft YaHei, serif"
SANS = "Noto Sans SC, Microsoft YaHei, Arial, sans-serif"

THEMES: dict[str, dict[str, str]] = {
    "literary_documentary_cn": {
        "surface": "#FFFCF6",
        "surface_alt": "#F7F0E5",
        "title_text": "#374151",
        "body_text": "#374151",
        "muted_text": "#6B7280",
        "source_text": "#7C6F64",
        "accent": "#A16207",
        "accent_soft": "#E7D2A4",
        "border": "#D6C8B8",
    },
    "paper_light": {
        "surface": "#FFFCF6",
        "surface_alt": "#F4EFE7",
        "title_text": "#374151",
        "body_text": "#374151",
        "muted_text": "#6B7280",
        "source_text": "#7C6F64",
        "accent": "#A16207",
        "accent_soft": "#E7D2A4",
        "border": "#D6C8B8",
    },
}

TOKEN_ALIASES = {
    "surface-color": "surface",
    "surface_color": "surface",
    "surface_alt-color": "surface_alt",
    "surface_alt_color": "surface_alt",
    "title_text-color": "title_text",
    "title_text_color": "title_text",
    "body_text-color": "body_text",
    "body_text_color": "body_text",
    "muted_text-color": "muted_text",
    "muted_text_color": "muted_text",
    "source_text-color": "source_text",
    "source_text_color": "source_text",
    "accent-color": "accent",
    "accent_color": "accent",
    "border-color": "border",
    "border_color": "border",
}
HEX_COLOR_RE = re.compile(r"^#[0-9A-Fa-f]{6}$")


def build_editorial_svg_page(spec: dict[str, Any]) -> str:
    """Build an SVG content layer for one editorial/literary page."""

    normalized = _normalize_spec(spec)
    theme = _tokens(normalized)
    layout = str(normalized["layout_family"])
    native_data = build_native_data(normalized)
    root_attrs = [
        'xmlns="http://www.w3.org/2000/svg"',
        f'viewBox="0 0 {W} {H}"',
        f'width="{W}"',
        f'height="{H}"',
        f'data-layout-family="{_h(layout)}"',
    ]
    if native_data.get("images"):
        root_attrs.append(f'data-native-data-ref="{_h(_native_data_ref(normalized))}"')
    parts = [f"<svg {' '.join(root_attrs)}>"]
    if layout == "story_cards_2up":
        _story_cards(parts, normalized, theme, count=2)
    elif layout == "story_cards_3up":
        _story_cards(parts, normalized, theme, count=3)
    elif layout == "book_compare_quote_panel":
        _book_compare_quote(parts, normalized, theme)
    else:
        _editorial_image_panel(parts, normalized, theme)
    _source_note(parts, normalized, theme)
    parts.append("</svg>")
    return "\n  ".join(parts) + "\n"


def build_native_data(spec: dict[str, Any]) -> dict[str, Any]:
    """Build renderer native-data JSON for image slots."""

    normalized = _normalize_spec(spec)
    image_slot = _image_slot(normalized)
    if not image_slot:
        return {"version": 1, "images": []}
    payload: dict[str, Any] = {"slot_id": _slot_id(image_slot)}
    for source_keys, target_key in (
        (("asset_id", "image_asset_id", "assetId", "imageAssetId"), "asset_id"),
        (("material_id", "image_material_id", "materialId", "imageMaterialId"), "material_id"),
        (("asset_key", "key", "oss_key", "storage_key", "assetKey", "ossKey", "storageKey"), "asset_key"),
        (("url", "image_url", "src", "imageUrl"), "url"),
        (("fit",), "fit"),
        (("radius", "corner_radius", "cornerRadius", "border_radius", "borderRadius"), "corner_radius"),
        (("caption",), "caption"),
        (("alt_text", "altText"), "alt_text"),
    ):
        value = _pick(image_slot, *source_keys)
        if value not in (None, "", [], {}):
            payload[target_key] = value
    source = _pick(image_slot, "source", "sourceInfo")
    if isinstance(source, dict) and source:
        payload["source"] = source
    crop = _pick(image_slot, "crop", "cropSpec")
    if isinstance(crop, dict) and crop:
        payload["crop"] = crop
    return {"version": 1, "images": [payload]}


def _normalize_spec(spec: dict[str, Any]) -> dict[str, Any]:
    result = dict(spec or {})
    layout = str(
        result.get("layout_family")
        or result.get("layout")
        or result.get("template")
        or "editorial_image_panel"
    ).strip()
    aliases = {
        "editorial": "editorial_image_panel",
        "image_panel": "editorial_image_panel",
        "two_up": "story_cards_2up",
        "2up": "story_cards_2up",
        "three_up": "story_cards_3up",
        "3up": "story_cards_3up",
        "book_compare_quote": "book_compare_quote_panel",
        "compare_quote": "book_compare_quote_panel",
    }
    result["layout_family"] = aliases.get(layout, layout)
    result.setdefault("theme_id", "literary_documentary_cn")
    result.setdefault("title", "主题判断")
    result.setdefault("lead", "")
    return result


def _tokens(spec: dict[str, Any]) -> dict[str, str]:
    theme = dict(THEMES.get(str(spec.get("theme_id")), THEMES["literary_documentary_cn"]))
    style_manifest = _dict(spec.get("style_manifest") or spec.get("style_manifest_snapshot"))
    for source in (
        _dict(style_manifest.get("palette")),
        _dict(style_manifest.get("theme_tokens")),
        _dict(style_manifest.get("tokens")),
        style_manifest,
        _dict(spec.get("visual_tokens")),
        spec,
    ):
        _apply_token_source(theme, source)
    return theme


def _apply_token_source(tokens: dict[str, str], source: dict[str, Any]) -> None:
    for raw_key, raw_value in source.items():
        key = TOKEN_ALIASES.get(str(raw_key), str(raw_key))
        if key in tokens and isinstance(raw_value, str) and HEX_COLOR_RE.match(raw_value.strip()):
            tokens[key] = raw_value.strip().upper()


def _editorial_image_panel(
    parts: list[str],
    spec: dict[str, Any],
    theme: dict[str, str],
) -> None:
    image_on_left = str(spec.get("image_position") or "").lower() == "left"
    image_box = {"x": 82, "y": 168, "w": 346, "h": 410} if image_on_left else {
        "x": 850,
        "y": 166,
        "w": 350,
        "h": 412,
    }
    text_box = {"x": 480, "y": 164, "w": 690, "h": 430} if image_on_left else {
        "x": 78,
        "y": 164,
        "w": 706,
        "h": 430,
    }
    _title_block(parts, spec, theme)
    parts.append(
        _rect(
            text_box["x"],
            text_box["y"],
            text_box["w"],
            text_box["h"],
            theme["surface"],
            stroke=theme["border"],
            rx=22,
            opacity=0.72,
        )
    )
    y = text_box["y"] + 50
    blocks = _blocks(spec, "narrative_blocks", fallback_key="cards")[:3]
    for index, block in enumerate(blocks, start=1):
        heading = _text(block.get("heading") or block.get("title"), f"论述 {index}")
        body = _text(block.get("body") or block.get("claim") or block.get("description"))
        parts.append(_text_svg(text_box["x"] + 34, y, f"0{index}", 13, theme["accent"], font=SANS, weight=700))
        parts.append(_text_svg(text_box["x"] + 76, y, heading, 20, theme["title_text"], weight=800))
        parts.extend(
            _multiline(
                text_box["x"] + 76,
                y + 34,
                body,
                15,
                theme["body_text"],
                width_chars=36,
                max_lines=3,
                line_gap=23,
            )
        )
        y += 118
    _quote(parts, spec, theme, x=text_box["x"] + 34, y=560, w=text_box["w"] - 68)
    _native_image_slot(parts, spec, theme, box=image_box)


def _story_cards(
    parts: list[str],
    spec: dict[str, Any],
    theme: dict[str, str],
    *,
    count: int,
) -> None:
    layout = "story_cards_2up" if count == 2 else "story_cards_3up"
    parts.append(f'<g id="{layout}" data-layout-family="{layout}">')
    _title_block(parts, spec, theme)
    cards = _blocks(spec, "cards", fallback_key="narrative_blocks")[:count]
    while len(cards) < count:
        cards.append({"heading": f"叙事块 {len(cards) + 1}", "body": ""})
    gap = 28 if count == 2 else 22
    card_w = (1120 - gap * (count - 1)) / count
    card_h = 330 if count == 3 else 342
    x0 = 80
    y0 = 190
    for index, card in enumerate(cards, start=1):
        x = x0 + (index - 1) * (card_w + gap)
        parts.append(f'<g id="story-card-{index}" data-role="narrative-card">')
        parts.append(_rect(x, y0, card_w, card_h, theme["surface"], stroke=theme["border"], rx=20, opacity=0.78))
        label = _text(card.get("micro_label"), f"{index:02d}")
        parts.append(_text_svg(x + 28, y0 + 42, label, 16, theme["accent"], font=SANS, weight=800))
        parts.append(_rect(x + 28, y0 + 60, 54, 4, theme["accent"], rx=0))
        heading = _text(card.get("heading") or card.get("title"), f"叙事块 {index}")
        body = _text(card.get("body") or card.get("claim") or card.get("description"))
        parts.extend(_multiline(x + 28, y0 + 108, heading, 21, theme["title_text"], width_chars=12 if count == 3 else 18, max_lines=2, line_gap=28, weight=800))
        parts.extend(_multiline(x + 28, y0 + 184, body, 15, theme["body_text"], width_chars=18 if count == 3 else 28, max_lines=5, line_gap=22))
        anchor = _text(card.get("anchor"))
        if anchor:
            parts.append(_text_svg(x + 28, y0 + card_h - 28, anchor, 12, theme["muted_text"], font=SANS))
        parts.append("</g>")
    close = _text(spec.get("bottom_close") or spec.get("quote_or_close"))
    if close:
        parts.append(_rect(80, 562, 1120, 74, theme["surface_alt"], stroke=theme["border"], rx=18, opacity=0.68))
        parts.extend(_multiline(112, 604, close, 18, theme["title_text"], width_chars=58, max_lines=2, line_gap=24, weight=700))
    parts.append("</g>")


def _book_compare_quote(
    parts: list[str],
    spec: dict[str, Any],
    theme: dict[str, str],
) -> None:
    _title_block(parts, spec, theme)
    image_box = {"x": 86, "y": 182, "w": 286, "h": 386}
    _native_image_slot(parts, spec, theme, box=image_box)
    x, y, w = 430, 174, 760
    blocks = _blocks(spec, "compare_blocks", fallback_key="narrative_blocks")[:3]
    if not blocks:
        blocks = [{"heading": "文本", "body": ""}, {"heading": "现实", "body": ""}]
    for index, block in enumerate(blocks, start=1):
        block_y = y + (index - 1) * 104
        parts.append(_rect(x, block_y, w, 82, theme["surface"], stroke=theme["border"], rx=16, opacity=0.74))
        parts.append(_text_svg(x + 24, block_y + 34, _text(block.get("heading") or block.get("title"), f"对照 {index}"), 19, theme["title_text"], weight=800))
        parts.extend(
            _multiline(
                x + 168,
                block_y + 31,
                _text(block.get("body") or block.get("claim") or block.get("description")),
                14,
                theme["body_text"],
                width_chars=38,
                max_lines=2,
                line_gap=21,
            )
        )
    _quote(parts, spec, theme, x=x, y=522, w=w)


def _title_block(parts: list[str], spec: dict[str, Any], theme: dict[str, str]) -> None:
    parts.append('<g id="editorial-title-block">')
    parts.append(_rect(80, 82, 72, 5, theme["accent"], rx=0))
    title = _text(spec.get("title"), "主题判断")
    parts.extend(_multiline(80, 126, title, 34, theme["title_text"], width_chars=28, max_lines=2, line_gap=42, weight=900))
    lead = _text(spec.get("lead") or spec.get("subtitle"))
    if lead:
        parts.extend(_multiline(82, 158, lead, 16, theme["muted_text"], width_chars=48, max_lines=2, line_gap=24, font=SANS))
    parts.append("</g>")


def _native_image_slot(
    parts: list[str],
    spec: dict[str, Any],
    theme: dict[str, str],
    *,
    box: dict[str, float],
) -> None:
    slot = _image_slot(spec)
    if not slot:
        return
    slot_id = _slot_id(slot)
    caption = _text(_pick(slot, "caption", "alt_text", "altText"), "图片槽位")
    x, y, w, h = box["x"], box["y"], box["w"], box["h"]
    parts.append(
        f'<g id="{_h(slot_id)}" data-role="native-image-slot" data-native-image="true" '
        f'data-x="{x:.1f}" data-y="{y:.1f}" data-w="{w:.1f}" data-h="{h:.1f}">'
    )
    parts.append(_rect(x, y, w, h, theme["surface_alt"], stroke=theme["border"], rx=20, opacity=0.78))
    parts.append(_rect(x + 18, y + 18, w - 36, h - 64, "none", stroke=theme["accent_soft"], rx=16, opacity=0.85))
    parts.append(_text_svg(x + 26, y + h - 28, caption, 13, theme["muted_text"], font=SANS))
    parts.append("</g>")


def _quote(parts: list[str], spec: dict[str, Any], theme: dict[str, str], *, x: float, y: float, w: float) -> None:
    quote = _text(spec.get("quote") or spec.get("quote_or_close"))
    if not quote:
        return
    parts.append(_rect(x, y, w, 76, theme["surface_alt"], stroke=theme["border"], rx=18, opacity=0.72))
    parts.append(_text_svg(x + 24, y + 32, "“", 32, theme["accent"], weight=900))
    parts.extend(_multiline(x + 58, y + 32, quote, 17, theme["title_text"], width_chars=max(18, int(w / 15)), max_lines=2, line_gap=24, weight=700))


def _source_note(parts: list[str], spec: dict[str, Any], theme: dict[str, str]) -> None:
    sources = spec.get("sources")
    if isinstance(sources, list):
        note = " / ".join(str(item).strip() for item in sources[:2] if str(item).strip())
    else:
        note = _text(spec.get("source_note") or sources)
    if note:
        parts.append(_text_svg(80, 674, f"来源：{note}", 11, theme["source_text"], font=SANS))


def _blocks(spec: dict[str, Any], key: str, *, fallback_key: str) -> list[dict[str, Any]]:
    raw = spec.get(key)
    if not isinstance(raw, list):
        raw = spec.get(fallback_key)
    if not isinstance(raw, list):
        return []
    return [item for item in raw if isinstance(item, dict)]


def _image_slot(spec: dict[str, Any]) -> dict[str, Any]:
    raw = spec.get("image_slot") or spec.get("imageSlot") or spec.get("image")
    return dict(raw) if isinstance(raw, dict) else {}


def _slot_id(slot: dict[str, Any]) -> str:
    return _text(slot.get("slot_id") or slot.get("slotId") or slot.get("id"), "image-slot-1")


def _native_data_ref(spec: dict[str, Any]) -> str:
    explicit = _text(spec.get("native_data_ref") or spec.get("nativeDataRef"))
    if explicit:
        return explicit
    page_id = _text(spec.get("page_id") or spec.get("slide_id"), "page-1")
    return f"slide-generation/{page_id}/native-data.json"


def _rect(
    x: float,
    y: float,
    w: float,
    h: float,
    fill: str,
    *,
    stroke: str | None = None,
    rx: float = 0,
    opacity: float | None = None,
) -> str:
    attrs = [
        f'x="{x:.0f}"',
        f'y="{y:.0f}"',
        f'width="{w:.0f}"',
        f'height="{h:.0f}"',
        f'rx="{rx:.0f}"',
        f'fill="{_h(fill)}"',
    ]
    if stroke:
        attrs.append(f'stroke="{_h(stroke)}"')
    if opacity is not None and opacity < 1:
        attrs.append(f'opacity="{opacity:.2f}"')
    return f"<rect {' '.join(attrs)}/>"


def _text_svg(
    x: float,
    y: float,
    text: Any,
    size: int,
    color: str,
    *,
    font: str = SERIF,
    weight: int = 500,
    anchor: str | None = None,
) -> str:
    attrs = [
        f'x="{x:.0f}"',
        f'y="{y:.0f}"',
        f'fill="{_h(color)}"',
        f'font-family="{_h(font)}"',
        f'font-size="{size}"',
        f'font-weight="{weight}"',
    ]
    if anchor:
        attrs.append(f'text-anchor="{_h(anchor)}"')
    return f"<text {' '.join(attrs)}>{_esc(text)}</text>"


def _multiline(
    x: float,
    y: float,
    text: Any,
    size: int,
    color: str,
    *,
    width_chars: int,
    max_lines: int,
    line_gap: int,
    weight: int = 500,
    font: str = SERIF,
) -> list[str]:
    lines = _wrap(_text(text), width_chars=width_chars, max_lines=max_lines)
    return [
        _text_svg(x, y + index * line_gap, line, size, color, font=font, weight=weight)
        for index, line in enumerate(lines)
    ]


def _wrap(text: str, *, width_chars: int, max_lines: int) -> list[str]:
    if not text:
        return []
    units = 0.0
    current = ""
    lines: list[str] = []
    for char in text:
        char_units = 0.55 if ord(char) < 128 else 1.0
        if current and units + char_units > width_chars:
            lines.append(current.rstrip())
            current = ""
            units = 0.0
            if len(lines) >= max_lines:
                break
        current += char
        units += char_units
    if current and len(lines) < max_lines:
        lines.append(current.rstrip())
    if len(lines) == max_lines and len("".join(lines)) < len(text):
        lines[-1] = lines[-1].rstrip("，。；、 ") + "..."
    return lines


def _dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _text(value: Any, default: str = "") -> str:
    if isinstance(value, str):
        cleaned = value.strip()
        return cleaned or default
    return default


def _pick(mapping: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        value = mapping.get(key)
        if value not in (None, "", [], {}):
            return value
    return None


def _esc(value: Any) -> str:
    return html.escape(str(value or ""), quote=False)


def _h(value: Any) -> str:
    return html.escape(str(value or ""), quote=True)


def _load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return data


def main() -> None:
    parser = argparse.ArgumentParser(description="Build one literary/editorial SVG slide from JSON.")
    parser.add_argument("--spec", type=Path, required=True, help="Input editorial page spec JSON.")
    parser.add_argument("--output", type=Path, help="Output SVG path.")
    parser.add_argument("--native-output", type=Path, help="Optional native-data JSON output path.")
    parser.add_argument("--print-native-data", action="store_true", help="Print native-data JSON in stdout payload.")
    args = parser.parse_args()

    spec = _load_json(args.spec)
    svg = build_editorial_svg_page(spec)
    native_data = build_native_data(spec)
    if args.output is None:
        payload: dict[str, Any] = {"ok": True, "svg": svg}
        if args.print_native_data:
            payload["native_data"] = native_data
        print(json.dumps(payload, ensure_ascii=False))
        return
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(svg, encoding="utf-8")
    result: dict[str, Any] = {"ok": True, "output": str(args.output)}
    if args.native_output is not None:
        args.native_output.parent.mkdir(parents=True, exist_ok=True)
        args.native_output.write_text(json.dumps(native_data, ensure_ascii=False, indent=2), encoding="utf-8")
        result["native_output"] = str(args.native_output)
    if args.print_native_data:
        result["native_data"] = native_data
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
