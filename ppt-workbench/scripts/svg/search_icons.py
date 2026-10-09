#!/usr/bin/env python3
"""Search the bundled lucide icon-index and expand data-icon-id slots.

Local stand-in for the host icon search tool. Returns icon_id / labels /
slot_example only — never raw path payloads. Expand inlines lucide/svgs
before validate/render.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

SVG_NS = "http://www.w3.org/2000/svg"
XLINK_NS = "http://www.w3.org/1999/xlink"
ET.register_namespace("", SVG_NS)

_BLOCKED_TAGS = {
    "script",
    "foreignObject",
    "style",
    "symbol",
    "use",
    "animate",
    "animateTransform",
    "animateMotion",
    "set",
}
_REMOTE_URL_RE = re.compile(r"^https?://", re.IGNORECASE)
_NUM_RE = re.compile(r"-?\d+(?:\.\d+)?")
_SPLIT_RE = re.compile(r"[\s,，;；/|]+")
_CJK_RE = re.compile(r"[\u4e00-\u9fff]{2,}")
_PRESENTATION_ATTRS = {
    "fill",
    "fill-opacity",
    "fill-rule",
    "clip-rule",
    "opacity",
    "stroke",
    "stroke-width",
    "stroke-linecap",
    "stroke-linejoin",
    "stroke-miterlimit",
    "stroke-dasharray",
    "stroke-dashoffset",
    "stroke-opacity",
}
_DEFAULT_ICON_GLYPH_INSET_RATIO = 0.18
_DEFAULT_ICON_GLYPH_INSET_BY_CONTAINER = {
    "circle": 0.20,
    "pill": 0.20,
    "rounded_rect": 0.18,
    "square": 0.18,
}
_QUERY_ALIASES = (
    ("柱状", "chart-bar chart-column 图表 bar"),
    ("柱图", "chart-bar 图表 bar"),
    ("折线", "chart-line 趋势 line"),
    ("饼图", "chart-pie pie"),
    ("预警", "shield-alert warning alert"),
    ("风险", "shield-alert mdi-alert mdi-shield-alert"),
    ("目标", "target mdi-target mdi-bullseye-arrow"),
    ("团队", "users mdi-account-group mdi-account-multiple"),
    ("协同", "users mdi-account-group"),
    ("客户", "mdi-account-group mdi-card-account-details mdi-handshake"),
    ("增长", "trending-up chart-bar mdi-trending-up"),
    ("下降", "trending-down mdi-trending-down"),
    ("经营", "chart-bar mdi-view-dashboard"),
    ("工厂", "mdi-factory mdi-industry"),
    ("制造", "mdi-factory mdi-conveyor-belt"),
    ("生产", "mdi-factory mdi-cog"),
    ("供应链", "mdi-truck mdi-truck-fast mdi-warehouse mdi-package-variant-closed"),
    ("物流", "mdi-truck mdi-truck-fast mdi-warehouse"),
    ("运输", "mdi-truck mdi-train-car-container mdi-ship"),
    ("库存", "mdi-warehouse mdi-package-variant-closed mdi-barcode"),
    ("仓储", "mdi-warehouse mdi-forklift"),
    ("交付", "mdi-truck-delivery mdi-package-variant-closed-check"),
    ("门店", "mdi-store mdi-storefront"),
    ("城市", "mdi-city mdi-map-marker-radius"),
    ("区域", "mdi-map mdi-map-marker-multiple"),
    ("金融", "mdi-bank mdi-cash mdi-currency-cny"),
    ("财务", "mdi-cash-multiple mdi-calculator mdi-receipt-text"),
    ("支付", "mdi-credit-card mdi-cash"),
    ("成本", "mdi-cash-minus mdi-calculator mdi-percent"),
    ("收入", "mdi-cash-plus mdi-trending-up"),
    ("利润", "mdi-trending-up mdi-chart-box"),
    ("预算", "mdi-cash-multiple mdi-calculator"),
    ("合同", "mdi-file-sign mdi-signature-freehand mdi-handshake"),
    ("审批", "mdi-stamp mdi-clipboard-check"),
    ("评审", "mdi-clipboard-check mdi-clipboard-text"),
    ("会议", "mdi-presentation mdi-forum mdi-account-group"),
    ("汇报", "mdi-presentation mdi-chart-box"),
    ("通知", "mdi-bell mdi-email"),
    ("电力", "mdi-transmission-tower mdi-lightning-bolt"),
    ("能源", "mdi-solar-power mdi-transmission-tower mdi-lightning-bolt"),
    ("双碳", "mdi-molecule-co2 mdi-recycle mdi-leaf"),
    ("环保", "mdi-leaf mdi-recycle"),
    ("安全", "mdi-shield-check mdi-lock"),
    ("权限", "mdi-lock mdi-shield-lock"),
    ("合规", "mdi-certificate mdi-clipboard-check"),
    ("医院", "mdi-hospital mdi-medical-bag"),
    ("医疗", "mdi-hospital mdi-stethoscope"),
    ("教育", "mdi-school mdi-graduation-cap"),
    ("排期", "mdi-calendar-clock mdi-calendar-month"),
    ("进度", "mdi-progress-check mdi-timer"),
    ("风险预警", "mdi-alert mdi-shield-alert"),
    ("整改", "mdi-progress-wrench mdi-clipboard-alert"),
    ("报告", "mdi-file-chart mdi-file-document"),
    ("材料", "mdi-file-document mdi-folder-open"),
    ("证据", "mdi-file-check mdi-drawing-box"),
    ("归档", "mdi-archive mdi-file-cabinet"),
    ("接口", "mdi-api mdi-code-json"),
    ("部署", "mdi-cloud-upload mdi-server"),
    ("数据", "mdi-database mdi-chart-box"),
    ("云端", "mdi-cloud mdi-cloud-check"),
    ("农业", "mdi-sprout mdi-tractor mdi-greenhouse"),
)


@dataclass(frozen=True)
class IconSearchResult:
    ok: bool
    icons: list[dict[str, Any]] = field(default_factory=list)
    message: str = ""


@dataclass(frozen=True)
class IconExpandResult:
    ok: bool
    svg: str
    expanded_count: int = 0
    issues: list[dict[str, str]] = field(default_factory=list)


def default_icons_root() -> Path:
    return (
        Path(__file__).resolve().parents[2]
        / "references"
        / "generate"
        / "original"
        / "slide-authoring"
        / "assets"
        / "icons"
    )


def search_svg_icon_library(
    *,
    icons_root: Path,
    query: str,
    category: str | None = None,
    style: str | None = None,
    output_mode: str | None = None,
    limit: int = 5,
) -> IconSearchResult:
    """Search icon metadata without returning raw SVG/path payloads."""

    index, message = _load_icon_index(icons_root)
    if index is None:
        return IconSearchResult(ok=False, message=message)

    query_terms = _query_terms(query)
    requested_category = str(category or "").strip().lower()
    requested_style = str(style or "").strip().lower()
    requested_output_mode = str(output_mode or "").strip()
    has_search_criteria = bool(
        query_terms or requested_category or requested_style or requested_output_mode
    )
    scored: list[tuple[int, dict[str, Any]]] = []
    for icon in index:
        if requested_category and str(icon.get("category") or "").strip().lower() != requested_category:
            continue
        if requested_style and str(icon.get("style") or "").strip().lower() != requested_style:
            continue
        score = _score_icon(icon, query_terms)
        score += _output_mode_score(icon, requested_output_mode)
        if has_search_criteria and score <= 0:
            continue
        scored.append((score, icon))

    scored.sort(key=lambda item: (-item[0], str(item[1].get("icon_id") or "")))
    cap = max(1, min(int(limit or 5), 12))
    return IconSearchResult(
        ok=True,
        icons=[_model_icon_candidate(icon) for _, icon in scored[:cap]],
        message="ok",
    )


def expand_svg_icon_slots(
    svg: str,
    *,
    icons_root: Path,
    default_color: str | None = None,
) -> IconExpandResult:
    """Expand ``<g data-icon-id=...>`` placeholders into inline SVG shapes."""

    try:
        root = ET.fromstring(svg)
    except ET.ParseError as exc:
        return IconExpandResult(
            ok=False,
            svg=svg,
            issues=[_issue("SVG_INVALID_XML", f"SVG XML 不良构: {exc}")],
        )

    parent_map = {child: parent for parent in root.iter() for child in list(parent)}
    placeholders = [
        elem for elem in root.iter() if str(elem.attrib.get("data-icon-id") or "").strip()
    ]
    if not placeholders:
        return IconExpandResult(ok=True, svg=svg, expanded_count=0)

    index, message = _load_icon_index(icons_root)
    if index is None:
        return IconExpandResult(
            ok=False,
            svg=svg,
            issues=[_issue("SVG_ICON_INDEX_MISSING", message)],
        )
    icon_map = {
        str(icon.get("icon_id")): icon
        for icon in index
        if isinstance(icon, dict) and str(icon.get("icon_id") or "").strip()
    }
    expanded = 0
    issues: list[dict[str, str]] = []
    for elem in placeholders:
        icon_id = str(elem.attrib.get("data-icon-id") or "").strip()
        icon = icon_map.get(icon_id)
        if icon is None:
            issues.append(_issue("SVG_ICON_NOT_FOUND", f"未找到图标: {icon_id}"))
            continue
        icon_path, path_error = _resolve_icon_path(icons_root, icon)
        if path_error:
            issues.append(_issue("SVG_ICON_PATH_INVALID", path_error))
            continue
        replacement, build_issues = _build_icon_replacement(
            elem,
            icon_path,
            default_color=default_color,
        )
        if build_issues:
            issues.extend(build_issues)
            continue
        parent = parent_map.get(elem)
        if parent is None:
            issues.append(_issue("SVG_ICON_SLOT_INVALID", "图标槽位不能是根节点。"))
            continue
        children = list(parent)
        index_in_parent = children.index(elem)
        parent.remove(elem)
        parent.insert(index_in_parent, replacement)
        expanded += 1

    if issues:
        return IconExpandResult(ok=False, svg=svg, issues=issues)
    return IconExpandResult(
        ok=True,
        svg=ET.tostring(root, encoding="unicode"),
        expanded_count=expanded,
    )


def _load_icon_index(icons_root: Path) -> tuple[list[dict[str, Any]] | None, str]:
    index_path = icons_root / "icon-index.json"
    if not index_path.exists():
        return None, f"缺少图标索引: {index_path}"
    try:
        payload = json.loads(index_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return None, f"图标索引不可读取: {exc}"
    icons = payload.get("icons") if isinstance(payload, dict) else None
    if not isinstance(icons, list):
        return None, "icon-index.json 必须包含 icons 数组。"
    return [icon for icon in icons if isinstance(icon, dict)], "ok"


def _tokenize(value: str) -> list[str]:
    raw = _SPLIT_RE.split(str(value or "").strip().lower())
    terms = [item for item in raw if item]
    blob = str(value or "")
    for match in _CJK_RE.findall(blob):
        if match.lower() not in terms:
            terms.append(match.lower())
        if len(match) >= 3:
            for index in range(len(match) - 1):
                gram = match[index : index + 2]
                if gram not in terms:
                    terms.append(gram)
    return terms


def _query_terms(query: str) -> list[str]:
    terms = _tokenize(query)
    blob = str(query or "").lower()
    for needle, extra in _QUERY_ALIASES:
        if needle in blob:
            terms.extend(_tokenize(extra))
    seen: set[str] = set()
    ordered: list[str] = []
    for term in terms:
        if term in seen:
            continue
        seen.add(term)
        ordered.append(term)
    return ordered


def _score_icon(icon: dict[str, Any], query_terms: list[str]) -> int:
    haystack_parts = [
        icon.get("icon_id"),
        icon.get("label"),
        icon.get("category"),
        icon.get("style"),
        icon.get("recommended_usage"),
        *(icon.get("keywords") if isinstance(icon.get("keywords"), list) else []),
    ]
    haystack = " ".join(str(item).lower() for item in haystack_parts if item)
    icon_id = str(icon.get("icon_id") or "").lower()
    label = str(icon.get("label") or "").lower()
    score = 0
    for term in query_terms:
        if term == icon_id or term in icon_id.replace("-", " ").split():
            score += 6
        elif term in label:
            score += 3
        elif term in haystack:
            score += 1
    return score


def _output_mode_score(icon: dict[str, Any], requested_output_mode: str) -> int:
    if not requested_output_mode:
        return 0
    output_modes = _string_list(icon.get("output_modes")) or ["editable_svg"]
    return 1 if requested_output_mode in output_modes else 0


def _model_icon_candidate(icon: dict[str, Any]) -> dict[str, Any]:
    icon_id = str(icon.get("icon_id") or "")
    return {
        "icon_id": icon_id,
        "label": str(icon.get("label") or icon_id),
        "category": str(icon.get("category") or ""),
        "style": str(icon.get("style") or ""),
        "keywords": [str(item) for item in icon.get("keywords", []) if str(item).strip()]
        if isinstance(icon.get("keywords"), list)
        else [],
        "recommended_usage": str(icon.get("recommended_usage") or ""),
        "colorizable": bool(icon.get("colorizable", True)),
        "output_modes": _string_list(icon.get("output_modes")) or ["editable_svg"],
        "containers": _string_list(icon.get("containers"))
        or ["none", "circle", "rounded_rect", "square", "pill"],
        "slot_example": {
            "element": "g",
            "data-icon-id": icon_id,
            "data-icon-box": "x y w h",
            "data-icon-color": "#45D1FF",
            "data-icon-container": "rounded_rect",
        },
    }


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value if str(item).strip()]


def _resolve_icon_path(icons_root: Path, icon: dict[str, Any]) -> tuple[Path | None, str | None]:
    rel = str(icon.get("path") or "").strip()
    rel_path = Path(rel)
    if not rel or rel_path.is_absolute() or ".." in rel_path.parts:
        return None, f"图标 path 非法: {rel}"
    icons_root_resolved = icons_root.resolve()
    candidates = [icons_root / rel_path]
    if len(rel_path.parts) == 2 and rel_path.parts[0] == "lucide":
        candidates.append(icons_root / "lucide" / "svgs" / rel_path.name)
    for candidate in candidates:
        path = candidate.resolve()
        try:
            path.relative_to(icons_root_resolved)
        except ValueError:
            return None, f"图标 path 越界: {rel}"
        if path.suffix.lower() == ".svg" and path.is_file():
            return path, None
    return None, f"图标 SVG 不存在: {rel}"


def _build_icon_replacement(
    slot: ET.Element,
    icon_path: Path,
    *,
    default_color: str | None = None,
) -> tuple[ET.Element | None, list[dict[str, str]]]:
    try:
        icon_root = ET.fromstring(icon_path.read_text(encoding="utf-8"))
    except (OSError, ET.ParseError) as exc:
        return None, [_issue("SVG_ICON_INVALID", f"图标 SVG 不可解析: {exc}")]
    issues = _validate_icon_svg(icon_root)
    if issues:
        return None, issues

    box = _parse_box(str(slot.attrib.get("data-icon-box") or ""))
    if box is None:
        return None, [_issue("SVG_ICON_BOX_INVALID", "data-icon-box 必须是 'x y w h' 四个数字。")]
    view_box = _parse_viewbox(icon_root.attrib.get("viewBox"))
    if view_box is None:
        return None, [_issue("SVG_ICON_VIEWBOX_MISSING", "图标 SVG 必须包含 viewBox。")]

    x, y, width, height = box
    _, _, vb_w, vb_h = view_box
    inset = _icon_glyph_inset(slot, width, height)
    glyph_x = x + inset
    glyph_y = y + inset
    glyph_w = max(width - inset * 2, 1)
    glyph_h = max(height - inset * 2, 1)
    scale = min(glyph_w / vb_w, glyph_h / vb_h)
    tx = glyph_x + (glyph_w - vb_w * scale) / 2
    ty = glyph_y + (glyph_h - vb_h * scale) / 2
    color = str(slot.attrib.get("data-icon-color") or default_color or "#1A6CFF").strip() or "#1A6CFF"
    container = str(slot.attrib.get("data-icon-container") or "none").strip()
    slot_id = str(slot.attrib.get("id") or "icon-slot").strip() or "icon-slot"

    group = ET.Element(_svg_tag("g"), {"id": slot_id})
    _append_icon_container(group, slot_id, box, container, color)
    glyph = ET.SubElement(
        group,
        _svg_tag("g"),
        {
            "id": f"{slot_id}-glyph",
            "transform": f"translate({_fmt(tx)} {_fmt(ty)}) scale({_fmt(scale)})",
        },
    )
    root_presentation = _icon_presentation_attrs(icon_root, color, inherited=None)
    for child in list(icon_root):
        glyph.append(_clone_icon_elem(child, color, inherited=root_presentation))
    return group, []


def _icon_glyph_inset(slot: ET.Element, width: float, height: float) -> float:
    raw = slot.attrib.get("data-icon-inset")
    if raw is not None:
        try:
            value = float(str(raw).strip())
        except ValueError:
            value = _default_icon_glyph_inset_ratio(slot)
        if 0 <= value < 0.5:
            return min(width, height) * value
        return max(0.0, min(value, min(width, height) * 0.45))
    container = str(slot.attrib.get("data-icon-container") or "none").strip()
    if container in {"", "none"}:
        return 0.0
    return min(width, height) * _default_icon_glyph_inset_ratio(slot)


def _default_icon_glyph_inset_ratio(slot: ET.Element) -> float:
    container = str(slot.attrib.get("data-icon-container") or "none").strip()
    return _DEFAULT_ICON_GLYPH_INSET_BY_CONTAINER.get(container, _DEFAULT_ICON_GLYPH_INSET_RATIO)


def _validate_icon_svg(root: ET.Element) -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []
    if _local_name(root.tag) != "svg":
        issues.append(_issue("SVG_ICON_INVALID", "图标根节点必须是 <svg>。"))
    for elem in root.iter():
        name = _local_name(elem.tag)
        if name in _BLOCKED_TAGS:
            issues.append(_issue("SVG_ICON_UNSUPPORTED_ELEMENT", f"图标禁止使用 <{name}>。"))
        for key, value in elem.attrib.items():
            if key.lower().startswith("on"):
                issues.append(_issue("SVG_ICON_EVENT_ATTR", "图标禁止事件属性。"))
            if key in {"href", "xlink:href", f"{{{XLINK_NS}}}href"} and _REMOTE_URL_RE.match(value.strip()):
                issues.append(_issue("SVG_ICON_REMOTE_URL", "图标禁止远程资源。"))
            if key in {"style", "class"}:
                issues.append(_issue("SVG_ICON_STYLE_ATTR", "图标禁止 style/class 属性。"))
    return issues


def _append_icon_container(
    group: ET.Element,
    slot_id: str,
    box: tuple[float, float, float, float],
    container: str,
    color: str,
) -> None:
    x, y, width, height = box
    if container in {"", "none"}:
        return
    attrs = {
        "id": f"{slot_id}-container",
        "fill": color,
        "fill-opacity": "0.14",
        "stroke": color,
        "stroke-width": _fmt(max(width, height) * 0.025),
    }
    if container in {"circle"}:
        r = min(width, height) / 2
        attrs.update({"cx": _fmt(x + width / 2), "cy": _fmt(y + height / 2), "r": _fmt(r)})
        ET.SubElement(group, _svg_tag("circle"), attrs)
        return
    rx = {
        "rounded_rect": min(width, height) * 0.22,
        "pill": min(width, height) / 2,
        "square": 0,
    }.get(container, min(width, height) * 0.22)
    attrs.update(
        {
            "x": _fmt(x),
            "y": _fmt(y),
            "width": _fmt(width),
            "height": _fmt(height),
            "rx": _fmt(rx),
        }
    )
    ET.SubElement(group, _svg_tag("rect"), attrs)


def _clone_icon_elem(
    elem: ET.Element,
    color: str,
    *,
    inherited: dict[str, str] | None = None,
) -> ET.Element:
    current_presentation = _icon_presentation_attrs(elem, color, inherited=inherited)
    attrs = {
        key: _replace_current_color(value, color)
        for key, value in elem.attrib.items()
        if key not in {"style", "class"}
    }
    for key, value in current_presentation.items():
        attrs.setdefault(key, value)
    clone = ET.Element(_svg_tag(_local_name(elem.tag)), attrs)
    clone.text = elem.text
    clone.tail = elem.tail
    for child in list(elem):
        clone.append(_clone_icon_elem(child, color, inherited=current_presentation))
    return clone


def _icon_presentation_attrs(
    elem: ET.Element,
    color: str,
    *,
    inherited: dict[str, str] | None,
) -> dict[str, str]:
    attrs = dict(inherited or {})
    for key, value in elem.attrib.items():
        if key in _PRESENTATION_ATTRS:
            attrs[key] = _replace_current_color(value, color)
    return attrs


def _replace_current_color(value: Any, color: str) -> str:
    text = str(value)
    if text.strip().lower() == "currentcolor":
        return color
    return text


def _parse_box(value: str) -> tuple[float, float, float, float] | None:
    parts = [float(match.group(0)) for match in _NUM_RE.finditer(value)]
    if len(parts) != 4 or parts[2] <= 0 or parts[3] <= 0:
        return None
    return parts[0], parts[1], parts[2], parts[3]


def _parse_viewbox(value: str | None) -> tuple[float, float, float, float] | None:
    if not value:
        return None
    parts = [float(match.group(0)) for match in _NUM_RE.finditer(value)]
    if len(parts) != 4 or parts[2] <= 0 or parts[3] <= 0:
        return None
    return parts[0], parts[1], parts[2], parts[3]


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1] if "}" in tag else tag


def _svg_tag(name: str) -> str:
    return f"{{{SVG_NS}}}{name}"


def _fmt(value: float) -> str:
    return f"{value:.3f}".rstrip("0").rstrip(".")


def _issue(code: str, message: str) -> dict[str, str]:
    return {"code": code, "message": message, "severity": "error"}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Search bundled lucide icon-index; expand data-icon-id slots"
    )
    parser.add_argument("--query", help="search text (one intent)")
    parser.add_argument("--category", help="icon-index category filter")
    parser.add_argument("--style", help="line or filled")
    parser.add_argument("--output-mode", default="editable_svg")
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument("--icons-root", help="override icons directory")
    parser.add_argument("--expand", help="source.svg with data-icon-id slots")
    parser.add_argument("--output", help="write expanded SVG here")
    parser.add_argument("--default-color", help="fallback icon color")
    args = parser.parse_args(argv)
    icons_root = Path(args.icons_root) if args.icons_root else default_icons_root()
    if args.expand:
        svg_path = Path(args.expand)
        result = expand_svg_icon_slots(
            svg_path.read_text(encoding="utf-8"),
            icons_root=icons_root,
            default_color=args.default_color,
        )
        payload = {
            "ok": result.ok,
            "expanded_count": result.expanded_count,
            "issues": result.issues,
        }
        if args.output:
            if result.ok:
                Path(args.output).write_text(result.svg, encoding="utf-8")
                payload["output"] = str(Path(args.output))
        else:
            payload["svg"] = result.svg if result.ok else None
        json.dump(payload, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")
        return 0 if result.ok else 2
    if not args.query:
        parser.error("--query is required unless --expand")
    result = search_svg_icon_library(
        icons_root=icons_root,
        query=args.query,
        category=args.category,
        style=args.style,
        output_mode=args.output_mode,
        limit=args.limit,
    )
    json.dump(
        {"ok": result.ok, "icons": result.icons, "message": result.message},
        sys.stdout,
        ensure_ascii=False,
        indent=2,
    )
    sys.stdout.write("\n")
    return 0 if result.ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
