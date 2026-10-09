"""Page-level visual readability gates (session-884 V-01/02/03/04/05/07/09).

Deck-level consecutive-fingerprint caps live in deck_consistency, not here.
Do not import build_gold_svg_page.
"""

from __future__ import annotations

import math
import re
import xml.etree.ElementTree as ET
from typing import Any

from . import CONTENT_ROLES, COVER_ROLES, GateResult

BODY_PX_MIN = 15
TITLE_PX_RANGE = (28, 34)
SOURCE_PX_RANGE = (9, 11)
MAX_CARDS = 6
FOUR_ACROSS_TITLE_CHARS = 12
FOUR_ACROSS_BODY_LINES = 2
FOUR_ACROSS_BODY_CHARS = 20
MAX_TABLE_COLS = 6
MAX_TABLE_ROWS = 10
MAX_CELL_CHARS = 18
MAX_CELL_LINES = 2
MIN_COL_WIDTH_PX = 120
CANVAS_WIDTH_PX = 1280
MAX_TINY_TEXT_RATIO = 0.25
MIN_CONTRAST_BODY = 4.5
MIN_CONTRAST_SOURCE = 3.0

EXCEPTION_TOKENS = frozenset(
    {"source-note", "source_note", "evidence-gap", "evidence_gap", "flow-label", "flow_label", "kicker"}
)
_MECHANISM_KINDS = frozenset({"mechanism", "概念机制图", "schematic", "concept"})
SEMANTIC_HEX = frozenset(
    {
        "#16A34A",
        "#22C55E",
        "#15803D",
        "#166534",
        "#10B981",
        "#059669",
        "#4ADE80",
        "#0F766E",
        "#DC2626",
        "#EF4444",
        "#B91C1C",
        "#991B1B",
        "#F87171",
        "#E11D48",
        "#BE123C",
        "#F97316",
        "#EA580C",
        "#FB923C",
        "#F59E0B",
        "#D97706",
        "#FBBF24",
        "#B45309",
        "#C2410C",
    }
)
_COLOR_VALUE_KEYS = frozenset(
    {
        "fill",
        "color",
        "status_color",
        "statuscolour",
        "good",
        "risk",
        "warn",
        "warning",
        "pass_color",
        "fail_color",
        "positive",
        "negative",
    }
)
_SKIP_WALK_KEYS = frozenset({"color_legend", "theme", "visual_tokens", "typography", "export_fonts"})
_FONT_SIZE_ATTR = re.compile(r"^([0-9]*\.?[0-9]+)\s*(px|pt|em)?$", re.I)
_FONT_SIZE_STYLE = re.compile(r"font-size\s*:\s*([0-9]*\.?[0-9]+)\s*(px|pt|em)?", re.I)
_FILL_STYLE = re.compile(r"(?:^|;)\s*fill\s*:\s*([^;]+)", re.I)
_RGB = re.compile(r"rgb\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)", re.I)
_NUMBERISH = re.compile(r"^[-+]?\d[\d,.\s]*\s*%?$")

__all__ = [
    "BODY_PX_MIN",
    "MAX_TINY_TEXT_RATIO",
    "compute_layout_fingerprint",
    "check",
    "check_svg",
]


def compute_layout_fingerprint(spec: dict) -> str | None:
    """Canonical page-skeleton id for deck_consistency consecutive-reuse caps.

    Algorithm (stable, do not hash):
    1. `layout` = strip+lower `spec.layout` or `spec.layout_id`. Empty → omit.
    2. `visual_layer` = `spec.structure_hierarchy.visual_layer`, else `spec.visual_layer`.
       Each slot strip+lower; drop empties; preserve order; join with `+`.
    3. Parts: `layout:{layout}` if layout, `visual:{slots}` if any slot.
    4. Join parts with `|`. Return None if both inputs are empty.

    Example: `layout:gold_cards|visual:main-title+key-message+metric-strip+main-content+action-bar`
    """

    layout = str(spec.get("layout") or spec.get("layout_id") or "").strip().lower()
    hierarchy = spec.get("structure_hierarchy")
    visual = None
    if isinstance(hierarchy, dict):
        visual = hierarchy.get("visual_layer")
    if visual is None:
        visual = spec.get("visual_layer")
    slots: list[str] = []
    if isinstance(visual, str):
        visual = [part.strip() for part in re.split(r"[,|]", visual)]
    if isinstance(visual, (list, tuple)):
        for item in visual:
            token = str(item).strip().lower()
            if token:
                slots.append(token)
    parts: list[str] = []
    if layout:
        parts.append(f"layout:{layout}")
    if slots:
        parts.append("visual:" + "+".join(slots))
    return "|".join(parts) if parts else None


def check(spec: dict) -> GateResult:
    result = GateResult()
    spec = spec or {}
    role = _role(spec)
    cover = role in COVER_ROLES
    content = role in CONTENT_ROLES or not cover

    body_px = _read_px(spec, "body_px")
    if body_px is not None:
        result.details["body_px"] = body_px
    has_body_copy = _has_body_copy(spec)
    if (content or has_body_copy) and not cover:
        if body_px is None or body_px < BODY_PX_MIN:
            _miss(result, "body_px")
    elif cover and has_body_copy:
        if body_px is not None and body_px < BODY_PX_MIN:
            _miss(result, "body_px")

    title_px = _read_px(spec, "title_px")
    if title_px is not None and content:
        lo, hi = TITLE_PX_RANGE
        if title_px < lo or title_px > hi:
            result.warnings.append("title_px")

    _check_fingerprint(spec, result, content=content)
    _check_cards(spec, result)
    _check_table(spec, result, body_px=body_px)
    _check_fonts(spec, result)
    _check_color_legend(spec, None, result)
    _check_spec_contrast(spec, result)
    return result


def check_svg(svg_text: str, spec: dict | None = None) -> GateResult:
    result = GateResult()
    if spec:
        result = _combine(result, check(spec))
    root = _parse_svg(svg_text)
    if root is None:
        _miss(result, "svg_parse")
        return result

    texts: list[dict[str, Any]] = []
    semantic: set[str] = set()
    charts: list[ET.Element] = []
    _walk_svg(
        root,
        texts,
        semantic,
        charts,
        inherited_size=None,
        inherited_fill=None,
        exception=None,
        chart_kind=None,
    )

    density_texts = [node for node in texts if node["exception"] != "source-note"]
    tiny = [node for node in density_texts if node["px"] is not None and node["px"] < BODY_PX_MIN]
    total = len(density_texts)
    ratio = (len(tiny) / total) if total else 0.0
    result.details["text_node_count"] = len(texts)
    result.details["source_text_node_count"] = len(texts) - total
    result.details["tiny_text_count"] = len(tiny)
    result.details["tiny_text_ratio"] = ratio
    if total and ratio > MAX_TINY_TEXT_RATIO:
        _miss(result, "tiny_text_ratio")

    exceptions = []
    for node in texts:
        px = node["px"]
        if px is None:
            continue
        if node["exception"]:
            if SOURCE_PX_RANGE[0] <= px < BODY_PX_MIN:
                exceptions.append(
                    {"id": node["id"], "px": px, "reason": node["exception"]}
                )
            elif px < SOURCE_PX_RANGE[0]:
                _miss(result, "svg_body_font_px")
                exceptions.append(
                    {"id": node["id"], "px": px, "reason": f"{node['exception']}_too_small"}
                )
            continue
        if px < BODY_PX_MIN:
            _miss(result, "svg_body_font_px")
        if node["fill"] and node["bg"]:
            contrast = _contrast_ratio(node["fill"], node["bg"])
            if contrast is not None and contrast < MIN_CONTRAST_BODY:
                _miss(result, "contrast")
    if exceptions:
        result.details["font_exceptions"] = exceptions

    _check_color_legend(spec or {}, semantic, result)
    _check_charts(root, charts, spec or {}, result)
    return result


def _check_fingerprint(spec: dict, result: GateResult, *, content: bool) -> None:
    computed = compute_layout_fingerprint(spec)
    provided = str(spec.get("layout_fingerprint") or "").strip()
    if computed:
        result.details["layout_fingerprint"] = computed
        if provided:
            result.details["layout_fingerprint_source"] = "spec"
            if provided.lower() != computed.lower():
                result.warnings.append("layout_fingerprint_mismatch")
        else:
            result.details["layout_fingerprint_source"] = "computed"
            result.warnings.append("layout_fingerprint_computed")
        return
    if content:
        _miss(result, "layout_fingerprint")


def _check_cards(spec: dict, result: GateResult) -> None:
    cards = _cards(spec)
    if not cards:
        return
    reasons: list[str] = []
    if len(cards) > MAX_CARDS:
        reasons.append(f"max_cards:{len(cards)}>{MAX_CARDS}")
    across = _columns_across(spec, len(cards))
    if across >= 4:
        for index, card in enumerate(cards):
            title = str(card.get("title") or card.get("name") or "")
            if _cjk_len(title) > FOUR_ACROSS_TITLE_CHARS:
                reasons.append(f"card_{index + 1}_title_chars")
            body_lines = _card_body_lines(card)
            if len(body_lines) > FOUR_ACROSS_BODY_LINES:
                reasons.append(f"card_{index + 1}_body_lines")
            for line in body_lines:
                if _cjk_len(line) > FOUR_ACROSS_BODY_CHARS:
                    reasons.append(f"card_{index + 1}_body_chars")
                    break
    if reasons:
        result.details["card_capacity"] = reasons
        _miss(result, "card_capacity")


def _check_table(spec: dict, result: GateResult, *, body_px: float | None) -> None:
    density = spec.get("density_budget") if isinstance(spec.get("density_budget"), dict) else {}
    declared_min = _parse_px(density.get("min_body_font_px"))
    minimum_px = max(float(BODY_PX_MIN), declared_min if declared_min and math.isfinite(declared_min) else 0)
    slots = spec.get("native_table_slots") or spec.get("table_slots") or []
    if isinstance(slots, dict):
        slots = [slots]
    font_details = []
    for index, slot in enumerate(slots if isinstance(slots, list) else []):
        if not isinstance(slot, dict):
            continue
        style = slot.get("style") if isinstance(slot.get("style"), dict) else {}
        raw_size = style.get("font_size")
        try:
            actual_px = float(raw_size) * 4 / 3 if raw_size is not None else body_px
        except (TypeError, ValueError):
            actual_px = None
        valid_size = actual_px is not None and math.isfinite(actual_px)
        font_details.append({"slot": slot.get("id") or index, "font_px": actual_px if valid_size else None,
                             "minimum_px": minimum_px})
        if not valid_size or actual_px < minimum_px:
            _miss(result, "native_table_font_px")
    if font_details:
        result.details["native_table_fonts"] = font_details
    columns, rows, width = _table_payload(spec)
    if not columns and not rows:
        return
    reasons: list[str] = []
    n_cols = len(columns) if columns else (max((len(r) for r in rows), default=0))
    n_rows = len(rows)
    if n_cols > MAX_TABLE_COLS:
        reasons.append(f"columns:{n_cols}>{MAX_TABLE_COLS}")
    if n_rows > MAX_TABLE_ROWS:
        reasons.append(f"rows:{n_rows}>{MAX_TABLE_ROWS}")
    col_w = (width / n_cols) if n_cols else width
    if n_cols and col_w < MIN_COL_WIDTH_PX:
        reasons.append(f"col_width:{col_w:.1f}<{MIN_COL_WIDTH_PX}")
    em = body_px if body_px and body_px > 0 else float(BODY_PX_MIN)
    chars_fit = max(1, int(col_w / em)) if n_cols else MAX_CELL_CHARS
    for r_i, row in enumerate(rows):
        for c_i, cell in enumerate(row):
            text = str(cell or "").strip()
            if not text:
                continue
            explicit_lines = [ln for ln in re.split(r"\r?\n", text) if ln.strip()]
            if len(explicit_lines) > MAX_CELL_LINES:
                reasons.append(f"cell_{r_i}_{c_i}_lines")
            units = _cjk_len(text)
            if units > MAX_CELL_CHARS:
                reasons.append(f"cell_{r_i}_{c_i}_chars")
            estimated = max(len(explicit_lines), math.ceil(units / chars_fit) if chars_fit else 1)
            if estimated > MAX_CELL_LINES:
                reasons.append(f"cell_{r_i}_{c_i}_scan")
    if reasons:
        result.details["table_capacity"] = reasons
        _miss(result, "table_capacity")


def _check_fonts(spec: dict, result: GateResult) -> None:
    export = _font_list(spec.get("export_fonts"))
    if not export:
        return
    theme = spec.get("theme") if isinstance(spec.get("theme"), dict) else {}
    typography = spec.get("typography") if isinstance(spec.get("typography"), dict) else {}
    design = _font_list(
        theme.get("fonts")
        or theme.get("font_family")
        or theme.get("fontFamily")
        or typography.get("fonts")
        or typography.get("font_family")
        or spec.get("fonts")
    )
    if not design:
        return
    design_n = {_norm_font(name) for name in design}
    export_n = {_norm_font(name) for name in export}
    if design_n <= export_n:
        return
    reason = spec.get("font_fallback_accepted")
    if isinstance(reason, str) and reason.strip():
        result.details["font_fallback_accepted"] = reason.strip()
        return
    result.details["design_fonts"] = design
    result.details["export_fonts"] = export
    _miss(result, "font_fallback_accepted")


def _check_color_legend(spec: dict, svg_semantic: set[str] | None, result: GateResult) -> None:
    used = set(svg_semantic or ())
    used.update(_spec_semantic_colors(spec))
    if not used:
        return
    result.details["semantic_colors"] = sorted(used)
    legend_colors = _legend_colors(spec.get("color_legend"))
    if legend_colors and used <= legend_colors:
        return
    if legend_colors and used - legend_colors:
        _miss(result, "color_legend")
        return
    if not legend_colors:
        _miss(result, "color_legend")
    for metric in spec.get("metrics") or []:
        if not isinstance(metric, dict):
            continue
        fill = _normalize_hex(str(metric.get("fill") or metric.get("color") or ""))
        value = str(metric.get("value") or metric.get("number") or "")
        if fill in SEMANTIC_HEX and _NUMBERISH.match(value.strip()) and not metric.get("evidence_type"):
            warn = "color_used_as_evidence"
            if warn not in result.warnings:
                result.warnings.append(warn)


def _check_spec_contrast(spec: dict, result: GateResult) -> None:
    tokens = spec.get("visual_tokens") if isinstance(spec.get("visual_tokens"), dict) else {}
    theme = spec.get("theme") if isinstance(spec.get("theme"), dict) else {}
    body = _normalize_hex(str(tokens.get("body_text") or theme.get("body_text") or ""))
    surface = _normalize_hex(
        str(tokens.get("surface") or theme.get("surface") or tokens.get("background") or theme.get("background") or "")
    )
    if body and surface:
        ratio = _contrast_ratio(body, surface)
        if ratio is not None and ratio < MIN_CONTRAST_BODY:
            _miss(result, "contrast")


def _check_charts(
    root: ET.Element,
    charts: list[ET.Element],
    spec: dict,
    result: GateResult,
) -> None:
    if _spec_declares_chart_data(spec):
        return
    for elem in charts:
        if _chart_exempt(elem):
            continue
        _miss(result, "chart_unlabeled")
        result.details.setdefault("unlabeled_charts", []).append(_local(elem.tag))
        break


def _walk_svg(
    elem: ET.Element,
    texts: list[dict[str, Any]],
    semantic: set[str],
    charts: list[ET.Element],
    *,
    inherited_size: float | None,
    inherited_fill: str | None,
    exception: str | None,
    chart_kind: str | None,
) -> None:
    exception = _exception_token(elem) or exception
    own_size = _elem_font_size(elem)
    size = own_size if own_size is not None else inherited_size
    paint = _elem_fill(elem)
    fill_hex = paint or inherited_fill
    if paint in SEMANTIC_HEX:
        semantic.add(paint)
    own_kind = (elem.get("data-chart-kind") or elem.get("data-kind") or "").strip().lower()
    kind = own_kind or chart_kind
    tag = _local(elem.tag)
    if tag == "text":
        texts.append(
            {
                "id": elem.get("id") or (exception or ""),
                "px": size,
                "fill": fill_hex,
                "bg": "#FFFFFF",
                "exception": exception,
            }
        )
    if _looks_like_data_chart(elem) and kind not in _MECHANISM_KINDS:
        charts.append(elem)
    for child in list(elem):
        _walk_svg(
            child,
            texts,
            semantic,
            charts,
            inherited_size=size,
            inherited_fill=fill_hex,
            exception=exception,
            chart_kind=kind,
        )


def _looks_like_data_chart(elem: ET.Element) -> bool:
    tag = _local(elem.tag)
    if tag == "polyline":
        return len(_parse_points(elem.get("points") or "")) >= 3
    if tag == "polygon":
        return False
    if tag == "path":
        d = elem.get("d") or ""
        linetos = len(re.findall(r"[Ll]", d))
        return linetos >= 2
    if tag == "g":
        lines = [child for child in list(elem) if _local(child.tag) == "line"]
        if len(lines) >= 6:
            return True
        rects = [child for child in list(elem) if _local(child.tag) == "rect"]
        if _looks_like_bars(rects):
            return True
    return False


def _looks_like_bars(rects: list[ET.Element]) -> bool:
    slim = []
    for rect in rects:
        try:
            width = float(rect.get("width") or 0)
            height = float(rect.get("height") or 0)
            y = float(rect.get("y") or 0)
        except ValueError:
            continue
        if 4 <= width <= 48 and height >= 24:
            slim.append((width, y))
    if len(slim) < 4:
        return False
    ys = [item[1] for item in slim]
    return max(ys) - min(ys) <= 4


def _chart_exempt(elem: ET.Element) -> bool:
    kind = (elem.get("data-chart-kind") or elem.get("data-kind") or "").strip().lower()
    if kind in _MECHANISM_KINDS:
        return True
    if elem.get("data-chart-data") or elem.get("data-series"):
        return True
    return False


def _spec_declares_chart_data(spec: dict) -> bool:
    for key in ("chart", "charts", "series", "native_chart_slots"):
        value = spec.get(key)
        if isinstance(value, dict) and (value.get("data") or value.get("series") or value.get("values")):
            return True
        if isinstance(value, list) and value:
            first = value[0]
            if isinstance(first, dict) and (first.get("data") or first.get("values") or first.get("points")):
                return True
    return False


def _parse_svg(svg_text: str) -> ET.Element | None:
    raw = (svg_text or "").strip()
    if not raw:
        return None
    try:
        return ET.fromstring(raw)
    except ET.ParseError:
        try:
            return ET.fromstring(f"<root>{raw}</root>")
        except ET.ParseError:
            return None


def _elem_font_size(elem: ET.Element) -> float | None:
    parsed = _parse_px(elem.get("font-size"))
    if parsed is not None:
        return parsed
    style = elem.get("style") or ""
    match = _FONT_SIZE_STYLE.search(style)
    if match:
        return _parse_px(match.group(1) + (match.group(2) or ""))
    return None


def _elem_fill(elem: ET.Element) -> str | None:
    style = elem.get("style") or ""
    match = _FILL_STYLE.search(style)
    if match:
        hex_color = _normalize_hex(match.group(1))
        if hex_color:
            return hex_color
    return _normalize_hex(elem.get("fill") or "")


def _exception_token(elem: ET.Element) -> str | None:
    blob_parts = [
        elem.get("id") or "",
        elem.get("class") or "",
        elem.get("data-role") or "",
        elem.get("data-kind") or "",
    ]
    blob = " ".join(blob_parts).lower().replace("_", "-")
    for token in EXCEPTION_TOKENS:
        needle = token.replace("_", "-")
        if needle in blob:
            return needle
    return None


def _parse_points(raw: str) -> list[tuple[float, float]]:
    nums = [float(part) for part in re.findall(r"[-+]?(?:\d+\.?\d*|\.\d+)", raw or "")]
    pairs = list(zip(nums[::2], nums[1::2]))
    return pairs


def _parse_px(raw: Any) -> float | None:
    if raw is None or raw == "":
        return None
    if isinstance(raw, (int, float)):
        return float(raw)
    text = str(raw).strip().lower()
    match = _FONT_SIZE_ATTR.match(text)
    if not match:
        return None
    value = float(match.group(1))
    unit = (match.group(2) or "px").lower()
    if unit == "pt":
        return value * 96.0 / 72.0
    if unit == "em":
        return value * 16.0
    return value


def _read_px(spec: dict, field: str) -> float | None:
    typography = spec.get("typography") if isinstance(spec.get("typography"), dict) else {}
    tokens = spec.get("visual_tokens") if isinstance(spec.get("visual_tokens"), dict) else {}
    for source in (typography, tokens, spec):
        if field in source and source.get(field) not in (None, ""):
            return _parse_px(source.get(field))
        alias = field.replace("_px", "")
        if alias != field and source.get(alias) not in (None, ""):
            parsed = _parse_px(source.get(alias))
            if parsed is not None:
                return parsed
    return None


def _role(spec: dict) -> str:
    return str(spec.get("page_role") or spec.get("page_archetype") or spec.get("role") or "content").strip().lower()


def _has_body_copy(spec: dict) -> bool:
    return bool(_cards(spec) or spec.get("rows") or spec.get("table") or spec.get("steps"))


def _cards(spec: dict) -> list[dict]:
    raw = spec.get("groups") or spec.get("cards") or spec.get("items") or []
    if not isinstance(raw, list):
        return []
    cards = []
    for item in raw:
        if isinstance(item, dict):
            cards.append(item)
        else:
            cards.append({"title": str(item)})
    return cards


def _columns_across(spec: dict, n_cards: int) -> int:
    for key in ("columns_across", "card_columns", "across"):
        value = spec.get(key)
        if isinstance(value, (int, float)) and value > 0:
            return int(value)
    layout = str(spec.get("layout") or "").lower()
    if any(token in layout for token in ("four", "4up", "quad", "4-across", "four_across")):
        return 4
    return 0


def _card_body_lines(card: dict) -> list[str]:
    lines: list[str] = []
    for key in ("claim", "body", "text", "description"):
        value = card.get(key)
        if value:
            lines.extend([ln.strip() for ln in str(value).splitlines() if ln.strip()])
    for key in ("evidence", "bullets", "points"):
        for item in card.get(key) or []:
            text = str(item).strip()
            if text:
                lines.append(text)
    return lines


def _table_payload(spec: dict) -> tuple[list[Any], list[list[Any]], float]:
    table = spec.get("table") if isinstance(spec.get("table"), dict) else {}
    columns = table.get("columns") if table.get("columns") is not None else spec.get("columns")
    if not isinstance(columns, list):
        columns = []
    raw_rows = table.get("rows") if table.get("rows") is not None else spec.get("rows")
    if not isinstance(raw_rows, list):
        raw_rows = []
    rows: list[list[Any]] = []
    col_names = [str(col.get("name") if isinstance(col, dict) else col) for col in columns]
    for raw in raw_rows:
        if isinstance(raw, dict):
            cells = raw.get("cells")
            if isinstance(cells, list):
                rows.append(list(cells))
            elif isinstance(cells, dict):
                rows.append([cells.get(name, "") for name in col_names] or list(cells.values()))
            else:
                rows.append([raw.get(name, "") for name in col_names] if col_names else [str(raw)])
        elif isinstance(raw, list):
            rows.append(list(raw))
        else:
            rows.append([raw])
    width_raw = table.get("width") or table.get("w") or spec.get("table_width") or CANVAS_WIDTH_PX
    width = float(width_raw) if isinstance(width_raw, (int, float, str)) and str(width_raw).strip() else float(CANVAS_WIDTH_PX)
    try:
        width = float(width)
    except (TypeError, ValueError):
        width = float(CANVAS_WIDTH_PX)
    layout = str(spec.get("layout") or "").lower()
    if not columns and not rows and "table" not in layout:
        return [], [], width
    return columns, rows, width


def _cjk_len(text: str) -> float:
    total = 0.0
    for ch in text:
        if ch.isspace():
            continue
        code = ord(ch)
        if (
            0x2E80 <= code <= 0x9FFF
            or 0xF900 <= code <= 0xFAFF
            or 0xFF00 <= code <= 0xFFEF
            or 0x3000 <= code <= 0x303F
        ):
            total += 1.0
        else:
            total += 0.5
    return total


def _font_list(value: Any) -> list[str]:
    if value is None or value is False:
        return []
    if isinstance(value, str):
        parts = [part.strip().strip("'\"") for part in re.split(r"[,;]", value)]
        return [part for part in parts if part]
    if isinstance(value, (list, tuple)):
        out: list[str] = []
        for item in value:
            out.extend(_font_list(item))
        return out
    return []


def _norm_font(name: str) -> str:
    return re.sub(r"\s+", " ", name).strip().lower()


def _spec_semantic_colors(spec: dict) -> set[str]:
    found: set[str] = set()

    def walk(obj: Any, key: str | None) -> None:
        if isinstance(obj, dict):
            for child_key, child in obj.items():
                if str(child_key) in _SKIP_WALK_KEYS:
                    continue
                walk(child, str(child_key))
            return
        if isinstance(obj, list):
            for item in obj:
                walk(item, key)
            return
        if not isinstance(obj, str) or not key:
            return
        lowered = key.lower()
        if lowered in _COLOR_VALUE_KEYS or lowered.endswith("_fill") or lowered.endswith("_color"):
            hex_color = _normalize_hex(obj)
            if hex_color in SEMANTIC_HEX:
                found.add(hex_color)

    walk(spec, None)
    return found


def _legend_colors(legend: Any) -> set[str]:
    colors: set[str] = set()
    if not legend:
        return colors
    if isinstance(legend, dict):
        for key, value in legend.items():
            for raw in (key, value if not isinstance(value, dict) else value.get("color")):
                hex_color = _normalize_hex(str(raw or ""))
                if hex_color:
                    colors.add(hex_color)
        return colors
    if isinstance(legend, list):
        for item in legend:
            if isinstance(item, dict):
                hex_color = _normalize_hex(str(item.get("color") or item.get("fill") or ""))
                if hex_color:
                    colors.add(hex_color)
            else:
                hex_color = _normalize_hex(str(item))
                if hex_color:
                    colors.add(hex_color)
    return colors


def _normalize_hex(value: str) -> str | None:
    if not value:
        return None
    text = value.strip().lower()
    if text in {"none", "transparent", "currentcolor", "inherit"}:
        return None
    rgb = _RGB.match(text)
    if rgb:
        return "#{:02X}{:02X}{:02X}".format(int(rgb.group(1)), int(rgb.group(2)), int(rgb.group(3)))
    if not text.startswith("#"):
        return None
    digits = text[1:]
    if len(digits) == 3 and all(ch in "0123456789abcdef" for ch in digits):
        digits = "".join(ch * 2 for ch in digits)
    if len(digits) == 8 and all(ch in "0123456789abcdef" for ch in digits):
        digits = digits[:6]
    if len(digits) != 6 or any(ch not in "0123456789abcdef" for ch in digits):
        return None
    return "#" + digits.upper()


def _rel_luminance(hex_color: str) -> float:
    raw = hex_color.lstrip("#")
    channels = [int(raw[i : i + 2], 16) / 255.0 for i in (0, 2, 4)]

    def to_lin(channel: float) -> float:
        return channel / 12.92 if channel <= 0.04045 else ((channel + 0.055) / 1.055) ** 2.4

    lin = [to_lin(channel) for channel in channels]
    return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]


def _contrast_ratio(a: str, b: str) -> float | None:
    try:
        l1, l2 = _rel_luminance(a), _rel_luminance(b)
    except Exception:
        return None
    lighter, darker = (l1, l2) if l1 >= l2 else (l2, l1)
    return (lighter + 0.05) / (darker + 0.05)


def _local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1] if "}" in tag else tag


def _miss(result: GateResult, code: str) -> None:
    if code not in result.missing:
        result.missing.append(code)


def _combine(*results: GateResult) -> GateResult:
    out = GateResult()
    for item in results:
        for code in item.missing:
            _miss(out, code)
        for warn in item.warnings:
            if warn not in out.warnings:
                out.warnings.append(warn)
        out.details.update(item.details)
    return out
