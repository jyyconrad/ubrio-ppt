"""SVG DrawingML input gate.

The gate rejects malformed or unsafe SVG before any PPT-master finalizer or
converter sees the file. It returns a compact summary only; full SVG strings
must remain in renderer workdirs, not RuntimeEvent projections.
"""

from __future__ import annotations

import json
import re
import xml.etree.ElementTree as ET
from collections import Counter
from dataclasses import dataclass, field, replace
from typing import Any

from .repair_ops import (
    MAX_OFFENDERS,
    build_bounds_overflow_ops,
    build_text_box_overflow_ops,
    build_text_overlap_ops,
)

SVG_NS = "http://www.w3.org/2000/svg"
XLINK_NS = "http://www.w3.org/1999/xlink"
DEFAULT_MAX_SVG_BYTES = 64 * 1024
DEFAULT_MAX_DATA_URI_BYTES = 128 * 1024
_REMOTE_URL_RE = re.compile(r"^https?://", re.IGNORECASE)
_RGB_RE = re.compile(r"rgba?\(\s*(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*(\d{1,3})", re.IGNORECASE)
_STYLE_DECL_RE = re.compile(r"([a-zA-Z-]+)\s*:\s*([^;]+)")
_TRANSLATE_RE = re.compile(
    r"translate\(\s*(-?\d+(?:\.\d+)?)\s*(?:[, ]\s*(-?\d+(?:\.\d+)?))?\s*\)",
    re.IGNORECASE,
)
_DANGEROUS_TAG_CODES = {
    "script": "SVG_SCRIPT_FORBIDDEN",
    "foreignobject": "SVG_FOREIGN_OBJECT_FORBIDDEN",
    "use": "SVG_USE_FORBIDDEN",
    "symbol": "SVG_SYMBOL_FORBIDDEN",
}
_DANGEROUS_TAG_MESSAGES = {
    "script": "SVG 禁止包含 <script>。",
    "foreignobject": "SVG 禁止包含 <foreignObject>。",
    "use": "SVG 禁止包含 <use>。",
    "symbol": "SVG 禁止包含 <symbol>。",
}
# 受控真 3D 声明(data-effect-3d)白名单:只允许命名预设 + 受限自由度,
# 与 vendored build_sp3d_xml 的 _SP3D_PRESETS 一一对应(转换器宽容、gate 执法)。
_EFFECT_3D_ALLOWED_TAGS = {"rect", "circle", "ellipse", "path", "polygon"}
_EFFECT_3D_ALLOWED_KEYS = {"preset", "depth", "contour_color"}
_EFFECT_3D_PRESETS = {"card-raised", "button-soft", "block-extruded"}
_EFFECT_3D_MAX_PER_PAGE = 3
_EFFECT_3D_HEX_RE = re.compile(r"^#[0-9A-Fa-f]{6}$")
_FORBIDDEN_CHROME_ID_TOKENS = {
    "breadcrumb",
    "chapter-marker",
    "chrome",
    "deck-background",
    "deck_background",
    "footer",
    "header",
    "page-footer",
    "page-number",
    "page-header",
    "page_footer",
    "page_header",
    "page_number",
    "section-header",
    "section_header",
    "tab-header",
    "tab_header",
    "topbar",
}
_FORBIDDEN_CHROME_CLASS_TOKENS = {
    "breadcrumb",
    "chapter-marker",
    "chrome",
    "deck-background",
    "deck_background",
    "footer",
    "header",
    "page-footer",
    "page-number",
    "page-header",
    "page_footer",
    "page_header",
    "page_number",
    "section-header",
    "section_header",
    "tab-header",
    "tab_header",
    "topbar",
}
_DENSITY_SENSITIVE_LAYOUT_TOKENS = {
    "comparison",
    "compare",
    "matrix",
    "quadrant",
    "riskmatrix",
    "table",
    "swot",
}
# 内容页垂直填充阈值：0.78（即页面下沉到至少 78%）
# 比 _detect_layout_density_issues 的 0.84 宽松，用 warning 而非 blocking，
# 避免误伤合理留白；目标只是提示模型把主体下沉到页面下半屏。
_CONTENT_PAGE_VERTICAL_FILL_RATIO = 0.78

# 豁免内容页填充校验的页型。
# 与 app.tools.ppt_workflow.slide_context_internals.constants._FIXED_PAGE_ARCHETYPES
# 保持同义；这里不直接 import 是为了保持本模块零跨包依赖
# (input_gate 只接受字符串)。
_CONTENT_FILL_EXEMPT_ARCHETYPES = frozenset(
    {
        "cover",
        "agenda",
        "introduction",
        "section_divider",
        "closing",
        "disclaimer",
    }
)
_CENTERED_PAGE_TITLE_ARCHETYPES = frozenset(
    {"cover", "section_divider", "closing"}
)
_PAGE_TITLE_MIN_FONT_SIZE = 24.0
_PAGE_TITLE_BAND_RATIO = 0.24
# contract-layout-density.md 的机器底线使用 SVG px；PPT pt 会随 viewBox 到
# slide 尺寸的缩放比变化，不能在这里用固定换算值混为同一口径。
_FONT_SIZE_ROLE_THRESHOLDS_SVG_PX = {
    "body": 15.0,
    "dense_label": 12.0,
    "source": 11.0,
}
_MIN_TEXT_FONT_SIZE_SVG_PX = min(_FONT_SIZE_ROLE_THRESHOLDS_SVG_PX.values())
_DENSE_TEXT_ROLE_TOKENS = {
    *_DENSITY_SENSITIVE_LAYOUT_TOKENS,
    "axis",
    "chart",
    "diagram",
    "flow",
    "legend",
    "plot",
    "process",
    "step",
    "timeline",
}
# 内容主体越界阈值：right_ratio / bottom_ratio 已 round 到 3 位，
# 用 > 1.0 起算（1.001 起判越界），给刚好贴边 1.0 留容差，避免误报。
_CONTENT_BOUNDS_OVERFLOW_RATIO = 1.0
# 文本盒容量估算：中文按 1.0×font-size、ASCII 按 0.55×font-size 估算字符宽，
# 比 _text_width_px(0.56) 略松，避免对边界长句过度敏感；右边界容差 2%。
_TEXT_CAPACITY_CJK_WIDTH_RATIO = 1.0
_TEXT_CAPACITY_ASCII_WIDTH_RATIO = 0.55
_TEXT_CAPACITY_SPACE_WIDTH_RATIO = 0.33
_TEXT_CAPACITY_TOLERANCE_RATIO = 0.02
# 连线穿透文字检测：仅对长直线段（≥画布宽 25%）生效，避免误杀短装饰线。
_LINE_COLLISION_MIN_LENGTH_RATIO = 0.25
# 卡片边缘色条判定只看“与卡片 surface 同边、且覆盖大部分边长”的实心细矩形。
# 短强调线、内部分隔线不会命中；图表/表格自身的轴与图例也不在本规则职责内。
_CARD_EDGE_BAR_MAX_THICKNESS = 8.0
_CARD_EDGE_BAR_MIN_SPAN_RATIO = 0.7
_CARD_SURFACE_MIN_WIDTH_RATIO = 0.12
_CARD_SURFACE_MIN_HEIGHT_RATIO = 0.09
_CARD_EDGE_BAR_EXEMPT_TOKENS = {
    "axis",
    "chart",
    "gauge",
    "legend",
    "plot",
    "table",
}
_SOURCE_NOTE_TOKENS = {
    "citation",
    "evidence-source",
    "evidence_source",
    "footnote",
    "source-note",
    "source note",
    "source_note",
    "sourcenote",
    "evidence source",
}
# source-note 与页码的正常位置是画布底部安全区。语义 id/class 是首选，但模型可能
# 只输出裸 <text>；因此再用“底部位置 + 文本形态”兜底。位置门槛避免把正文里的
# “5/12”进度或比值误判成页码。
_FOOTER_METADATA_TOP_RATIO = 0.86
_FOOTER_SOURCE_PREFIX_RE = re.compile(
    r"^\s*(?:(?:数据|资料|信息|图表|素材|图片)\s*)?来源\s*[：:]|^\s*sources?\s*[：:]",
    re.IGNORECASE,
)
_FOOTER_PAGE_NUMBER_RE = re.compile(
    r"^\s*(?:第\s*\d+\s*页|\d+\s*页|\d+\s*(?:[/／]|of)\s*\d+)\s*$",
    re.IGNORECASE,
)
_EMPTY_CONTENT_CONTAINER_TOKENS = {
    "card",
    "cell",
    "panel",
    "tile",
}
_EMPTY_CONTENT_DECOR_TOKENS = {
    "accent",
    "background",
    "bg",
    "border",
    "decoration",
    "decor",
    "divider",
    "frame",
    "line",
    "shadow",
    "surface",
}
_EMPTY_CONTENT_EXEMPT_TOKENS = {
    "asset",
    "chart",
    "evidence",
    "icon",
    "image",
    "native",
    "placeholder",
    "screenshot",
    "source",
    "table",
}
_EMPTY_CONTAINER_MIN_AREA_RATIO = 0.035
_EMPTY_CONTAINER_MIN_WIDTH_RATIO = 0.18
_EMPTY_CONTAINER_MIN_HEIGHT_RATIO = 0.12


@dataclass(frozen=True)
class SvgInputGateResult:
    """Structured SVG input validation result."""

    ok: bool
    blocking_issues: list[dict[str, Any]] = field(default_factory=list)
    warnings: list[dict[str, Any]] = field(default_factory=list)
    summary: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class _SvgTextBox:
    element_id: str
    x: float
    y: float
    width: float
    height: float
    # 最近的祖先-或自身 id：可以直接喂给 patch_svg_layer(layer_id=...)。
    # 没有任何带 id 的祖先时为 None（模型只能整页 write_svg 或先补 id）。
    layer_id: str | None = None
    text_excerpt: str = ""


@dataclass(frozen=True)
class _SvgVisualBox:
    x: float
    y: float
    width: float
    height: float
    # 身份字段：越界检测要能指名道姓说"是哪个元素、在哪个 layer 里"，
    # 否则模型只能 read_file 重读整页 SVG 猜（真实回归 72f408ce）。
    element_id: str | None = None
    tag: str = ""
    layer_id: str | None = None

    @property
    def right(self) -> float:
        return self.x + self.width

    @property
    def bottom(self) -> float:
        return self.y + self.height


def _issue(code: str, message: str, **extra: Any) -> dict[str, Any]:
    payload = {"code": code, "message": message}
    payload.update(extra)
    return payload


def _check_effect_3d(
    elem: ET.Element,
    local_name: str,
) -> tuple[list[dict[str, Any]], bool]:
    """校验受控 data-effect-3d 声明,返回 (issues, 是否为合法声明).

    转换器(vendored build_sp3d_xml)对非法输入宽容返回空串,本函数是执法层:
    非法声明必须在 gate 报结构化错误,避免"申请了效果但静默没落地"的失真。
    """
    raw = elem.get("data-effect-3d")
    if raw is None:
        return [], False
    element_id = elem.get("id", "")
    if local_name not in _EFFECT_3D_ALLOWED_TAGS:
        return [
            _issue(
                "SVG_EFFECT_3D_TARGET_UNSUPPORTED",
                "data-effect-3d 只能挂在 rect/circle/ellipse/path/polygon 上;"
                "文字 3D 属 WordArt 语义、组不支持继承,请移到具体形状元素。",
                tag=local_name,
                element_id=element_id,
            )
        ], False
    try:
        spec = json.loads(raw)
    except ValueError as exc:
        return [
            _issue(
                "SVG_EFFECT_3D_INVALID_JSON",
                "data-effect-3d 必须是合法 JSON object,"
                '例如 {"preset":"card-raised"}。',
                detail=str(exc)[:120],
                element_id=element_id,
            )
        ], False
    if not isinstance(spec, dict):
        return [
            _issue(
                "SVG_EFFECT_3D_INVALID_JSON",
                "data-effect-3d 必须是 JSON object,不能是数组/字符串/数字。",
                element_id=element_id,
            )
        ], False

    issues: list[dict[str, Any]] = []
    preset = spec.get("preset")
    if preset not in _EFFECT_3D_PRESETS:
        issues.append(
            _issue(
                "SVG_EFFECT_3D_UNKNOWN_PRESET",
                "preset 必须是受控命名预设之一;不支持自由拼 camera/lightRig/bevel。",
                preset=preset,
                allowed=sorted(_EFFECT_3D_PRESETS),
                element_id=element_id,
            )
        )
    for key in sorted(set(spec) - _EFFECT_3D_ALLOWED_KEYS):
        issues.append(
            _issue(
                "SVG_EFFECT_3D_PARAM_INVALID",
                "data-effect-3d 只接受 preset/depth/contour_color 三个键。",
                field=key,
                value=str(spec[key])[:80],
                element_id=element_id,
            )
        )
    if preset != "block-extruded":
        # depth/contour_color 是 block-extruded 专属自由度,其它预设携带即报错,
        # 防止模型误以为所有预设都可调厚度。
        for field_name in ("depth", "contour_color"):
            if field_name in spec:
                issues.append(
                    _issue(
                        "SVG_EFFECT_3D_PARAM_INVALID",
                        f"{field_name} 仅 block-extruded 预设可用,请删除该键或改用 block-extruded。",
                        field=field_name,
                        value=str(spec[field_name])[:80],
                        element_id=element_id,
                    )
                )
    else:
        depth = spec.get("depth")
        if "depth" in spec and (
            not isinstance(depth, int)
            or isinstance(depth, bool)
            or not 1 <= depth <= 3
        ):
            issues.append(
                _issue(
                    "SVG_EFFECT_3D_PARAM_INVALID",
                    "depth 必须是 1/2/3 档位整数(1=6pt, 2=15pt, 3=30pt 挤出)。",
                    field="depth",
                    value=str(depth)[:80],
                    element_id=element_id,
                )
            )
        contour = spec.get("contour_color")
        if "contour_color" in spec and (
            not isinstance(contour, str) or not _EFFECT_3D_HEX_RE.match(contour)
        ):
            issues.append(
                _issue(
                    "SVG_EFFECT_3D_PARAM_INVALID",
                    "contour_color 必须是 #RRGGBB 六位十六进制颜色。",
                    field="contour_color",
                    value=str(contour)[:80],
                    element_id=element_id,
                )
            )
    return issues, not issues


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1] if "}" in tag else tag


def _iter_href_values(root: ET.Element) -> list[str]:
    values: list[str] = []
    for elem in root.iter():
        for key, value in elem.attrib.items():
            if key in {"href", "xlink:href", f"{{{XLINK_NS}}}href"} and value:
                values.append(value)
    return values


def _parse_style(style: str | None) -> dict[str, str]:
    if not style:
        return {}
    return {key.lower(): value.strip() for key, value in _STYLE_DECL_RE.findall(style)}


def _attr_local_name(name: str) -> str:
    return _local_name(name).lower()


def _is_near_black_color(value: str | None) -> bool:
    if not value:
        return False
    normalized = value.strip().lower()
    if normalized in {"black", "#000", "#000000", "#111", "#111111", "#1f2937"}:
        return True
    if normalized.startswith("#") and len(normalized) in {4, 7}:
        if len(normalized) == 4:
            channels = [int(ch * 2, 16) for ch in normalized[1:]]
        else:
            channels = [
                int(normalized[index : index + 2], 16) for index in (1, 3, 5)
            ]
        return max(channels) <= 48
    match = _RGB_RE.match(normalized)
    if not match:
        return False
    channels = [min(int(channel), 255) for channel in match.groups()]
    return max(channels) <= 48


def _element_paint(elem: ET.Element, name: str) -> str | None:
    style = _parse_style(elem.attrib.get("style"))
    return elem.attrib.get(name) or style.get(name)


def _has_dark_background(root: ET.Element) -> bool:
    root_style = _parse_style(root.attrib.get("style"))
    if _is_near_black_color(root_style.get("background")) or _is_near_black_color(
        root_style.get("background-color")
    ):
        return True
    if _is_near_black_color(_element_paint(root, "fill")):
        return True
    checked_shapes = 0
    for elem in root.iter():
        if elem is root:
            continue
        if _local_name(elem.tag).lower() != "rect":
            continue
        checked_shapes += 1
        if _is_near_black_color(_element_paint(elem, "fill")):
            return True
        if checked_shapes >= 6:
            break
    return False


def _build_summary(
    root: ET.Element,
    byte_len: int,
    *,
    font_size_report: dict[str, Any] | None = None,
) -> dict[str, Any]:
    text_node_count = 0
    shape_count = 0
    top_level_group_count = 0
    for elem in root.iter():
        name = _local_name(elem.tag)
        if name == "text":
            text_node_count += 1
        if name in {"rect", "circle", "ellipse", "line", "path", "polygon", "polyline"}:
            shape_count += 1
    for child in list(root):
        if _local_name(child.tag) == "g":
            top_level_group_count += 1
    page_width, page_height = _read_viewbox_size(root)
    content_bbox = _content_bbox_summary(root, page_width=page_width, page_height=page_height)
    summary = {
        "bytes": byte_len,
        "text_node_count": text_node_count,
        "top_level_group_count": top_level_group_count,
        "shape_count": shape_count,
        "viewbox_width": round(page_width, 1),
        "viewbox_height": round(page_height, 1),
        "content_bbox": content_bbox,
    }
    if font_size_report is not None:
        summary["font_size_report"] = font_size_report
    return summary


def _parse_float(value: str | None) -> float | None:
    if value is None:
        return None
    text = value.strip()
    if not text:
        return None
    if text.endswith("%"):
        return None
    match = re.match(r"^-?\d+(?:\.\d+)?", text)
    if not match:
        return None
    return float(match.group(0))


def _read_viewbox_size(root: ET.Element) -> tuple[float, float]:
    raw_viewbox = root.attrib.get("viewBox") or root.attrib.get("viewbox")
    if raw_viewbox:
        values = [_parse_float(part) for part in re.split(r"[\s,]+", raw_viewbox.strip()) if part]
        if len(values) == 4 and values[2] and values[3]:
            return values[2], values[3]
    width = _parse_float(root.attrib.get("width"))
    height = _parse_float(root.attrib.get("height"))
    return width or 1280.0, height or 720.0


def _tokenize_attr(value: str | None) -> set[str]:
    if not value:
        return set()
    return {token.lower() for token in re.split(r"[\s_:-]+", value) if token}


def _semantic_tokens(elem: ET.Element) -> set[str]:
    tokens: set[str] = set()
    for attr_name in ("id", "class", "data-role"):
        value = elem.attrib.get(attr_name)
        if value:
            normalized = value.strip().lower()
            tokens.add(normalized)
            tokens.update(_tokenize_attr(normalized))
            tokens.add(normalized.replace("-", "").replace("_", ""))
    return tokens


def _has_forbidden_chrome_identity(elem: ET.Element) -> bool:
    identity = (elem.attrib.get("id") or "").strip().lower()
    class_name = (elem.attrib.get("class") or "").strip().lower()
    if identity in _FORBIDDEN_CHROME_ID_TOKENS:
        return True
    if class_name in _FORBIDDEN_CHROME_CLASS_TOKENS:
        return True
    tokens = _tokenize_attr(identity) | _tokenize_attr(class_name)
    if tokens & {"topbar", "breadcrumb", "chrome", "footer"}:
        return True
    if "page" in tokens and bool(tokens & {"footer", "number", "no", "num"}):
        return True
    return "header" in tokens and bool(
        tokens & {"chapter", "page", "section", "slide", "tab", "top"}
    )


def _is_page_level_side_border(
    elem: ET.Element,
    *,
    page_width: float,
    page_height: float,
) -> bool:
    if _local_name(elem.tag).lower() != "rect":
        return False
    x = _parse_float(elem.attrib.get("x")) or 0.0
    width = _parse_float(elem.attrib.get("width"))
    height = _parse_float(elem.attrib.get("height"))
    if width is None or height is None:
        return False

    near_left_or_right = x <= page_width * 0.04 or (x + width) >= page_width * 0.96
    slender_vertical = width <= page_width * 0.025 and height >= page_height * 0.65
    return near_left_or_right and slender_vertical


def _is_page_level_outer_border(
    elem: ET.Element,
    *,
    page_width: float,
    page_height: float,
) -> bool:
    if _local_name(elem.tag).lower() != "rect":
        return False
    x = _parse_float(elem.attrib.get("x")) or 0.0
    y = _parse_float(elem.attrib.get("y")) or 0.0
    width = _parse_float(elem.attrib.get("width"))
    height = _parse_float(elem.attrib.get("height"))
    if width is None or height is None:
        return False
    fill = (_element_paint(elem, "fill") or "").strip().lower()
    stroke = (_element_paint(elem, "stroke") or "").strip().lower()
    no_fill = fill in {"", "none", "transparent"}
    has_stroke = stroke not in {"", "none", "transparent"}
    near_full_page = (
        x <= page_width * 0.04
        and y <= page_height * 0.04
        and width >= page_width * 0.92
        and height >= page_height * 0.88
    )
    return near_full_page and no_fill and has_stroke


def _rect_geometry(elem: ET.Element) -> tuple[float, float, float, float] | None:
    if _local_name(elem.tag).lower() != "rect":
        return None
    x = _parse_float(elem.attrib.get("x")) or 0.0
    y = _parse_float(elem.attrib.get("y")) or 0.0
    width = _parse_float(elem.attrib.get("width"))
    height = _parse_float(elem.attrib.get("height"))
    if width is None or height is None or width <= 0 or height <= 0:
        return None
    return x, y, width, height


def _has_visible_fill(elem: ET.Element) -> bool:
    fill = (_element_paint(elem, "fill") or "").strip().lower()
    return fill not in {"", "none", "transparent"}


def _card_edge_bar(
    *,
    container: tuple[float, float, float, float],
    candidate: tuple[float, float, float, float],
) -> str | None:
    container_x, container_y, container_width, container_height = container
    bar_x, bar_y, bar_width, bar_height = candidate
    x_tolerance = max(2.5, bar_width)
    y_tolerance = max(2.5, bar_height)

    if (
        bar_width <= _CARD_EDGE_BAR_MAX_THICKNESS
        and bar_height >= container_height * _CARD_EDGE_BAR_MIN_SPAN_RATIO
        and bar_y >= container_y - x_tolerance
        and (bar_y + bar_height) <= container_y + container_height + x_tolerance
    ):
        if abs(bar_x - container_x) <= x_tolerance:
            return "left"
        if abs((bar_x + bar_width) - (container_x + container_width)) <= x_tolerance:
            return "right"

    if (
        bar_height <= _CARD_EDGE_BAR_MAX_THICKNESS
        and bar_width >= container_width * _CARD_EDGE_BAR_MIN_SPAN_RATIO
        and bar_x >= container_x - y_tolerance
        and (bar_x + bar_width) <= container_x + container_width + y_tolerance
    ):
        if abs(bar_y - container_y) <= y_tolerance:
            return "top"
        if abs((bar_y + bar_height) - (container_y + container_height)) <= y_tolerance:
            return "bottom"
    return None


def _detect_card_edge_bar_issues(
    root: ET.Element,
    *,
    page_width: float,
    page_height: float,
) -> list[dict[str, Any]]:
    """阻断卡片边缘的全高/全宽装饰色条。

    这类装饰不编码业务语义，却会被模型复制成默认卡片语法。检测限定在同一 ``<g>``
    内的“大 surface rect + 贴边细 rect”，避免把独立短强调线、分隔线或流程连接线误判。
    """

    issues: list[dict[str, Any]] = []
    seen_candidates: set[int] = set()
    min_width = page_width * _CARD_SURFACE_MIN_WIDTH_RATIO
    min_height = page_height * _CARD_SURFACE_MIN_HEIGHT_RATIO
    for group in root.iter():
        if _local_name(group.tag).lower() != "g":
            continue
        if _semantic_tokens(group) & _CARD_EDGE_BAR_EXEMPT_TOKENS:
            continue
        rects = [
            (child, geometry)
            for child in list(group)
            if (geometry := _rect_geometry(child)) is not None
        ]
        containers = [
            (elem, geometry)
            for elem, geometry in rects
            if geometry[2] >= min_width
            and geometry[3] >= min_height
            and _has_visible_fill(elem)
        ]
        for container_elem, container in containers:
            for candidate_elem, candidate in rects:
                if candidate_elem is container_elem or id(candidate_elem) in seen_candidates:
                    continue
                if not _has_visible_fill(candidate_elem):
                    continue
                edge = _card_edge_bar(container=container, candidate=candidate)
                if edge is None:
                    continue
                seen_candidates.add(id(candidate_elem))
                policy_metadata: dict[str, Any] = {}
                issues.append(
                    _issue(
                        "SVG_CARD_EDGE_BAR_FORBIDDEN",
                        (
                            "禁止在卡片左/右/顶/底边添加全高或全宽装饰色条；"
                            "请删除色条，改用填充深浅、留白、字重字号或小面积语义标签表达层级。"
                        ),
                        element_id=candidate_elem.attrib.get("id"),
                        container_id=container_elem.attrib.get("id"),
                        layer_id=group.attrib.get("id"),
                        edge=edge,
                        **policy_metadata,
                    )
                )
    return issues


def _is_full_page_background_rect(
    elem: ET.Element,
    *,
    page_width: float,
    page_height: float,
) -> bool:
    if _local_name(elem.tag).lower() != "rect":
        return False
    x = _parse_float(elem.attrib.get("x")) or 0.0
    y = _parse_float(elem.attrib.get("y")) or 0.0
    width = _parse_float(elem.attrib.get("width"))
    height = _parse_float(elem.attrib.get("height"))
    if width is None or height is None:
        width_text = str(elem.attrib.get("width") or "").strip()
        height_text = str(elem.attrib.get("height") or "").strip()
        return width_text == "100%" and height_text == "100%"
    fill = (_element_paint(elem, "fill") or "").strip().lower()
    if fill in {"", "none", "transparent"}:
        return False
    return (
        x <= page_width * 0.02
        and y <= page_height * 0.02
        and width >= page_width * 0.96
        and height >= page_height * 0.96
    )


def _is_full_page_image(
    elem: ET.Element,
    *,
    page_width: float,
    page_height: float,
) -> bool:
    """近满页 `<image>` 几何拦截，与 `_is_full_page_background_rect` 同阈值口径。

    背景（含图片背景）统一归 deck_framework 处理；SVG 内容层本地 href 的整页图片
    此前只能被 SVG_REMOTE_URL_FORBIDDEN 间接挡住远程 URL，本地 href 可绕过，
    因此这里补一个对称的几何检查，不看 href 是否远程。
    """
    if _local_name(elem.tag).lower() != "image":
        return False
    x = _parse_float(elem.attrib.get("x")) or 0.0
    y = _parse_float(elem.attrib.get("y")) or 0.0
    width = _parse_float(elem.attrib.get("width"))
    height = _parse_float(elem.attrib.get("height"))
    if width is None or height is None:
        width_text = str(elem.attrib.get("width") or "").strip()
        height_text = str(elem.attrib.get("height") or "").strip()
        return width_text == "100%" and height_text == "100%"
    return (
        x <= page_width * 0.02
        and y <= page_height * 0.02
        and width >= page_width * 0.96
        and height >= page_height * 0.96
    )


def _read_translate(value: str | None) -> tuple[float, float]:
    if not value:
        return 0.0, 0.0
    match = _TRANSLATE_RE.search(value)
    if not match:
        return 0.0, 0.0
    return float(match.group(1)), float(match.group(2) or 0.0)


def _first_position(elem: ET.Element, axis: str) -> float | None:
    value = _parse_float(elem.attrib.get(axis))
    if value is not None:
        return value
    for child in elem:
        if _local_name(child.tag).lower() == "tspan":
            value = _parse_float(child.attrib.get(axis))
            if value is not None:
                return value
    return None


def _read_font_size(elem: ET.Element) -> float:
    style = _parse_style(elem.attrib.get("style"))
    return (
        _parse_float(elem.attrib.get("font-size"))
        or _parse_float(style.get("font-size"))
        or 16.0
    )


def _build_font_size_report(
    root: ET.Element,
    *,
    page_archetype: str | None,
) -> dict[str, Any]:
    """按语义角色统计可见 text/tspan 字号，不反向猜 PPT pt。"""

    normalized_archetype = str(page_archetype or "content").strip().lower() or "content"
    if normalized_archetype in _CONTENT_FILL_EXEMPT_ARCHETYPES:
        return {
            "checked": False,
            "reason": "fixed_page_archetype_exempt",
            "page_archetype": normalized_archetype,
            "measurement_unit": "svg_px",
            "minimum_font_size_svg_px": _MIN_TEXT_FONT_SIZE_SVG_PX,
            "role_thresholds_svg_px": dict(_FONT_SIZE_ROLE_THRESHOLDS_SVG_PX),
        }

    observed: list[dict[str, Any]] = []
    _, page_height = _read_viewbox_size(root)

    def own_text_content(elem: ET.Element) -> str:
        fragments = [elem.text or ""]
        fragments.extend(child.tail or "" for child in elem)
        return " ".join("".join(fragments).split())

    def walk(
        elem: ET.Element,
        *,
        inherited_font_size: float = 16.0,
        hidden: bool = False,
        layer_id: str | None = None,
        inherited_role: str = "body",
        translate_y: float = 0.0,
    ) -> None:
        name = _local_name(elem.tag).lower()
        current_layer_id = _own_id(elem) or layer_id
        _, local_translate_y = _read_translate(elem.attrib.get("transform"))
        current_translate_y = translate_y + local_translate_y
        style = _parse_style(elem.attrib.get("style"))
        declared_font_size = _parse_float(elem.attrib.get("font-size"))
        if declared_font_size is None:
            declared_font_size = _parse_float(style.get("font-size"))
        font_size = (
            declared_font_size
            if declared_font_size is not None
            else inherited_font_size
        )
        current_hidden = hidden or _is_hidden_text(elem)
        own_text = own_text_content(elem)
        tokens = _semantic_tokens(elem)
        text_role = inherited_role
        if tokens & (_SOURCE_NOTE_TOKENS | {"source", "sources"}):
            text_role = "source"
        elif tokens & _DENSE_TEXT_ROLE_TOKENS:
            text_role = "dense_label"
        if name == "text" and own_text and _FOOTER_SOURCE_PREFIX_RE.search(own_text):
            y = _first_position(elem, "y")
            if y is not None and current_translate_y + y >= page_height * _FOOTER_METADATA_TOP_RATIO:
                text_role = "source"
        if (
            name in {"text", "tspan"}
            and not current_hidden
            and own_text
        ):
            minimum_font_size = _FONT_SIZE_ROLE_THRESHOLDS_SVG_PX[text_role]
            observed.append(
                {
                    "element_id": _own_id(elem) or current_layer_id or name,
                    "font_size_svg_px": round(font_size, 2),
                    "text_role": text_role,
                    "minimum_font_size_svg_px": minimum_font_size,
                    "text_excerpt": own_text[:40],
                }
            )
        for child in elem:
            walk(
                child,
                inherited_font_size=font_size,
                hidden=current_hidden,
                layer_id=current_layer_id,
                inherited_role=text_role,
                translate_y=current_translate_y,
            )

    walk(root)
    offenders = sorted(
        (
            item
            for item in observed
            if item["font_size_svg_px"] < item["minimum_font_size_svg_px"]
        ),
        key=lambda item: (item["font_size_svg_px"], item["element_id"]),
    )
    minimum_observed = min(
        (item["font_size_svg_px"] for item in observed),
        default=None,
    )
    return {
        "checked": True,
        "page_archetype": normalized_archetype,
        "measurement_unit": "svg_px",
        "ppt_point_conversion": "renderer_dependent",
        "minimum_font_size_svg_px": _MIN_TEXT_FONT_SIZE_SVG_PX,
        "role_thresholds_svg_px": dict(_FONT_SIZE_ROLE_THRESHOLDS_SVG_PX),
        "minimum_observed_font_size_svg_px": minimum_observed,
        "text_runs": len(observed),
        "below_12": sum(item["font_size_svg_px"] < 12.0 for item in observed),
        "below_15": sum(item["font_size_svg_px"] < 15.0 for item in observed),
        "below_18": sum(item["font_size_svg_px"] < 18.0 for item in observed),
        "role_counts": dict(Counter(item["text_role"] for item in observed)),
        "role_violation_counts": dict(
            Counter(item["text_role"] for item in offenders)
        ),
        "affected_text_runs": len(offenders),
        "offending_elements": offenders[:MAX_OFFENDERS],
    }


def _text_width_px(text: str, font_size: float, elem: ET.Element) -> float:
    explicit = _parse_float(elem.attrib.get("textLength"))
    if explicit is not None and explicit > 0:
        return explicit
    width = 0.0
    for ch in text:
        if ch.isspace():
            width += font_size * 0.33
        elif ord(ch) < 128:
            width += font_size * 0.56
        else:
            width += font_size
    return width


def _text_anchor_offset(elem: ET.Element, width: float) -> float:
    style = _parse_style(elem.attrib.get("style"))
    anchor = (
        elem.attrib.get("text-anchor") or style.get("text-anchor") or "start"
    ).strip().lower()
    if anchor == "middle":
        return width / 2
    if anchor == "end":
        return width
    return 0.0


def _visible_text_content(elem: ET.Element) -> str:
    return " ".join("".join(elem.itertext()).split())


def _is_hidden_text(elem: ET.Element) -> bool:
    style = _parse_style(elem.attrib.get("style"))
    display = (elem.attrib.get("display") or style.get("display") or "").strip().lower()
    visibility = (elem.attrib.get("visibility") or style.get("visibility") or "").strip().lower()
    opacity = _parse_float(elem.attrib.get("opacity") or style.get("opacity"))
    return display == "none" or visibility == "hidden" or opacity == 0


def _has_visible_text(elem: ET.Element) -> bool:
    for child in elem.iter():
        if _local_name(child.tag).lower() != "text" or _is_hidden_text(child):
            continue
        if _visible_text_content(child):
            return True
    return False


def find_svg_page_title_issue(
    svg_content: str,
    *,
    expected_title: str | None,
    page_archetype: str | None,
) -> dict[str, Any] | None:
    """检查整页 SVG 是否包含显著主标题；仅供 full validation 调用。"""

    try:
        root = ET.fromstring(svg_content)
    except ET.ParseError:
        return None
    _, page_height = _read_viewbox_size(root)
    normalized_archetype = str(page_archetype or "content").strip().lower()
    allow_centered_title = normalized_archetype in _CENTERED_PAGE_TITLE_ARCHETYPES
    title_band_max_y = page_height * _PAGE_TITLE_BAND_RATIO

    def has_title(
        elem: ET.Element,
        *,
        translate_y: float = 0.0,
    ) -> bool:
        _, local_y = _read_translate(elem.attrib.get("transform"))
        current_y = translate_y + local_y
        if _local_name(elem.tag).lower() == "text" and not _is_hidden_text(elem):
            raw_y = _first_position(elem, "y")
            if (
                _visible_text_content(elem)
                and raw_y is not None
                and _read_font_size(elem) >= _PAGE_TITLE_MIN_FONT_SIZE
                and (allow_centered_title or current_y + raw_y <= title_band_max_y)
            ):
                return True
        return any(has_title(child, translate_y=current_y) for child in elem)

    if has_title(root):
        return None
    title = str(expected_title or "").strip()
    return _issue(
        "SVG_PAGE_TITLE_MISSING",
        "页面缺少位于主体内容上方的显著主标题。",
        expected_title=title or None,
        page_archetype=normalized_archetype,
        minimum_font_size=_PAGE_TITLE_MIN_FONT_SIZE,
        title_band_max_y=round(title_band_max_y, 1),
        fix_hint=(
            f"在主体内容上方加入当前页主标题“{title}”，字号至少 24px；"
            "允许有限度改写，但不能用卡片小标题或指标大数字替代。"
            if title
            else "在主体内容上方加入当前页主标题，字号至少 24px；不能用卡片小标题或指标大数字替代。"
        ),
    )


def _collect_text_boxes(
    elem: ET.Element,
    *,
    translate_x: float = 0.0,
    translate_y: float = 0.0,
    layer_id: str | None = None,
) -> list[_SvgTextBox]:
    local_tx, local_ty = _read_translate(elem.attrib.get("transform"))
    current_x = translate_x + local_tx
    current_y = translate_y + local_ty
    current_layer_id = _own_id(elem) or layer_id
    boxes: list[_SvgTextBox] = []
    if _local_name(elem.tag).lower() == "text" and not _is_hidden_text(elem):
        text = _visible_text_content(elem)
        raw_x = _first_position(elem, "x")
        raw_y = _first_position(elem, "y")
        if text and raw_x is not None and raw_y is not None:
            font_size = _read_font_size(elem)
            width = _text_width_px(text, font_size, elem)
            height = font_size * 1.2
            x = current_x + raw_x - _text_anchor_offset(elem, width)
            # SVG y 是文字 baseline；这里取近似可见盒，主要用于发现明显互压。
            y = current_y + raw_y - font_size * 0.88
            boxes.append(
                _SvgTextBox(
                    element_id=elem.attrib.get("id") or f"text@{round(x)}:{round(y)}",
                    x=x,
                    y=y,
                    width=width,
                    height=height,
                    layer_id=current_layer_id,
                    text_excerpt=text[:40],
                )
            )
    for child in elem:
        boxes.extend(
            _collect_text_boxes(
                child,
                translate_x=current_x,
                translate_y=current_y,
                layer_id=current_layer_id,
            )
        )
    return boxes


def _own_id(elem: ET.Element) -> str | None:
    """元素自身的 id（非空字符串才算）。"""

    value = elem.attrib.get("id")
    if isinstance(value, str) and value.strip():
        return value.strip()
    return None


def _build_layer_index(root: ET.Element) -> dict[int, str]:
    """id(elem) -> 最近的祖先-或自身 layer_id。

    `root.iter()` 拿不到父链，而 patch_svg_layer 只认 layer_id，所以在需要按元素
    定位的 detector 里用这张索引把元素映射回可 patch 的 layer。
    """

    index: dict[int, str] = {}

    def walk(elem: ET.Element, inherited: str | None) -> None:
        current = _own_id(elem) or inherited
        if current:
            index[id(elem)] = current
        for child in elem:
            walk(child, current)

    walk(root, None)
    return index


def _parse_points(value: str | None) -> list[tuple[float, float]]:
    if not value:
        return []
    numbers = [
        float(match.group(0))
        for match in re.finditer(r"-?\d+(?:\.\d+)?", value)
    ]
    return list(zip(numbers[0::2], numbers[1::2], strict=False))


def _shape_visual_box(
    elem: ET.Element,
    *,
    translate_x: float,
    translate_y: float,
) -> _SvgVisualBox | None:
    name = _local_name(elem.tag).lower()
    if name == "text":
        text = _visible_text_content(elem)
        raw_x = _first_position(elem, "x")
        raw_y = _first_position(elem, "y")
        if not text or raw_x is None or raw_y is None:
            return None
        font_size = _read_font_size(elem)
        width = _text_width_px(text, font_size, elem)
        x = translate_x + raw_x - _text_anchor_offset(elem, width)
        y = translate_y + raw_y - font_size * 0.88
        return _SvgVisualBox(x=x, y=y, width=width, height=font_size * 1.2)

    if name == "rect":
        x = _parse_float(elem.attrib.get("x")) or 0.0
        y = _parse_float(elem.attrib.get("y")) or 0.0
        width = _parse_float(elem.attrib.get("width"))
        height = _parse_float(elem.attrib.get("height"))
        if width is None or height is None:
            return None
        return _SvgVisualBox(
            x=translate_x + x,
            y=translate_y + y,
            width=width,
            height=height,
        )

    if name == "circle":
        cx = _parse_float(elem.attrib.get("cx"))
        cy = _parse_float(elem.attrib.get("cy"))
        r = _parse_float(elem.attrib.get("r"))
        if cx is None or cy is None or r is None:
            return None
        return _SvgVisualBox(
            x=translate_x + cx - r,
            y=translate_y + cy - r,
            width=r * 2,
            height=r * 2,
        )

    if name == "ellipse":
        cx = _parse_float(elem.attrib.get("cx"))
        cy = _parse_float(elem.attrib.get("cy"))
        rx = _parse_float(elem.attrib.get("rx"))
        ry = _parse_float(elem.attrib.get("ry"))
        if cx is None or cy is None or rx is None or ry is None:
            return None
        return _SvgVisualBox(
            x=translate_x + cx - rx,
            y=translate_y + cy - ry,
            width=rx * 2,
            height=ry * 2,
        )

    if name == "line":
        x1 = _parse_float(elem.attrib.get("x1"))
        y1 = _parse_float(elem.attrib.get("y1"))
        x2 = _parse_float(elem.attrib.get("x2"))
        y2 = _parse_float(elem.attrib.get("y2"))
        if None in {x1, y1, x2, y2}:
            return None
        assert x1 is not None and y1 is not None and x2 is not None and y2 is not None
        x = min(x1, x2)
        y = min(y1, y2)
        return _SvgVisualBox(
            x=translate_x + x,
            y=translate_y + y,
            width=max(abs(x2 - x1), 1.0),
            height=max(abs(y2 - y1), 1.0),
        )

    if name in {"polygon", "polyline"}:
        points = _parse_points(elem.attrib.get("points"))
        if not points:
            return None
        xs = [point[0] for point in points]
        ys = [point[1] for point in points]
        return _SvgVisualBox(
            x=translate_x + min(xs),
            y=translate_y + min(ys),
            width=max(max(xs) - min(xs), 1.0),
            height=max(max(ys) - min(ys), 1.0),
        )

    return None


def _collect_visual_boxes_for_density(
    elem: ET.Element,
    *,
    translate_x: float = 0.0,
    translate_y: float = 0.0,
    in_source_note: bool = False,
    layer_id: str | None = None,
    page_height: float | None = None,
) -> tuple[list[_SvgVisualBox], bool]:
    local_tx, local_ty = _read_translate(elem.attrib.get("transform"))
    current_x = translate_x + local_tx
    current_y = translate_y + local_ty
    current_layer_id = _own_id(elem) or layer_id
    tokens = _semantic_tokens(elem)
    source_scope = in_source_note or bool(tokens & _SOURCE_NOTE_TOKENS)
    has_density_sensitive_layout = bool(tokens & _DENSITY_SENSITIVE_LAYOUT_TOKENS)
    boxes: list[_SvgVisualBox] = []
    if not source_scope and not _is_hidden_text(elem):
        box = _shape_visual_box(elem, translate_x=current_x, translate_y=current_y)
        if box is not None and not _is_unmarked_footer_metadata_text(
            elem,
            box=box,
            page_height=page_height,
        ):
            # 身份只在收集处补：_shape_visual_box 只管几何，避免每个形状分支重复。
            tag = _local_name(elem.tag).lower()
            boxes.append(
                replace(
                    box,
                    element_id=(
                        _own_id(elem) or f"{tag}@{round(box.x)}:{round(box.y)}"
                    ),
                    tag=tag,
                    layer_id=current_layer_id,
                )
            )
    for child in elem:
        child_boxes, child_has_density = _collect_visual_boxes_for_density(
            child,
            translate_x=current_x,
            translate_y=current_y,
            in_source_note=source_scope,
            layer_id=current_layer_id,
            page_height=page_height,
        )
        boxes.extend(child_boxes)
        has_density_sensitive_layout = has_density_sensitive_layout or child_has_density
    return boxes, has_density_sensitive_layout


def _is_unmarked_footer_metadata_text(
    elem: ET.Element,
    *,
    box: _SvgVisualBox,
    page_height: float | None,
) -> bool:
    """识别没有 id/class 的底部来源说明和页码，不让它们撑大主体 bbox。"""

    if (
        _local_name(elem.tag).lower() != "text"
        or page_height is None
        or page_height <= 0
        or box.bottom < page_height * _FOOTER_METADATA_TOP_RATIO
    ):
        return False
    text = re.sub(r"\s+", " ", "".join(elem.itertext())).strip()
    if not text:
        return False
    return bool(
        _FOOTER_SOURCE_PREFIX_RE.search(text)
        or _FOOTER_PAGE_NUMBER_RE.fullmatch(text)
    )


def _content_bbox_summary(
    root: ET.Element,
    *,
    page_width: float,
    page_height: float,
) -> dict[str, Any] | None:
    boxes, _has_density_sensitive_layout = _collect_visual_boxes_for_density(
        root,
        page_height=page_height,
    )
    if not boxes or page_width <= 0 or page_height <= 0:
        return None
    left = min(box.x for box in boxes)
    top = min(box.y for box in boxes)
    right = max(box.right for box in boxes)
    bottom = max(box.bottom for box in boxes)
    width = max(right - left, 0.0)
    height = max(bottom - top, 0.0)
    return {
        "x": round(left, 1),
        "y": round(top, 1),
        "w": round(width, 1),
        "h": round(height, 1),
        "right": round(right, 1),
        "bottom": round(bottom, 1),
        "width_ratio": round(width / page_width, 3),
        "height_ratio": round(height / page_height, 3),
        "bottom_ratio": round(bottom / page_height, 3),
        "right_ratio": round(right / page_width, 3),
    }


def _subtree_visual_bbox(elem: ET.Element) -> _SvgVisualBox | None:
    boxes, _has_density_sensitive_layout = _collect_visual_boxes_for_density(elem)
    if not boxes:
        return None
    left = min(box.x for box in boxes)
    top = min(box.y for box in boxes)
    right = max(box.right for box in boxes)
    bottom = max(box.bottom for box in boxes)
    return _SvgVisualBox(x=left, y=top, width=max(right - left, 0.0), height=max(bottom - top, 0.0))


def _detect_empty_content_container_issues(
    root: ET.Element,
    *,
    page_width: float,
    page_height: float,
    page_archetype: str | None,
) -> list[dict[str, Any]]:
    """Reject large semantic card/panel containers that carry no visible text."""

    normalized_archetype = (
        page_archetype.strip().lower()
        if isinstance(page_archetype, str) and page_archetype.strip()
        else "content"
    )
    if (
        normalized_archetype in _CONTENT_FILL_EXEMPT_ARCHETYPES
        or page_width <= 0
        or page_height <= 0
    ):
        return []
    issues: list[dict[str, Any]] = []
    for elem in root.iter():
        name = _local_name(elem.tag).lower()
        if name not in {"g", "rect"}:
            continue
        tokens = _semantic_tokens(elem)
        if not tokens & _EMPTY_CONTENT_CONTAINER_TOKENS:
            continue
        if tokens & (
            _EMPTY_CONTENT_DECOR_TOKENS
            | _EMPTY_CONTENT_EXEMPT_TOKENS
            | _SOURCE_NOTE_TOKENS
        ):
            continue
        if _has_visible_text(elem):
            continue
        box = _subtree_visual_bbox(elem)
        if box is None:
            continue
        width_ratio = box.width / page_width
        height_ratio = box.height / page_height
        area_ratio = (box.width * box.height) / (page_width * page_height)
        if (
            area_ratio < _EMPTY_CONTAINER_MIN_AREA_RATIO
            or width_ratio < _EMPTY_CONTAINER_MIN_WIDTH_RATIO
            or height_ratio < _EMPTY_CONTAINER_MIN_HEIGHT_RATIO
        ):
            continue
        issues.append(
            _issue(
                "SVG_EMPTY_CONTENT_CONTAINER",
                (
                    "大型卡片/面板容器没有任何可见正文，最终会形成明显空白；"
                    "请填入对应内容、合并为更少卡片，或删除该空容器后重排。"
                ),
                element_id=elem.attrib.get("id"),
                element_class=elem.attrib.get("class"),
                x=round(box.x, 1),
                y=round(box.y, 1),
                width=round(box.width, 1),
                height=round(box.height, 1),
                width_ratio=round(width_ratio, 3),
                height_ratio=round(height_ratio, 3),
                area_ratio=round(area_ratio, 3),
            )
        )
        if len(issues) >= 6:
            break
    return issues


def _detect_layout_density_issues(
    root: ET.Element,
    *,
    page_height: float,
    boxes: list[_SvgVisualBox] | None = None,
    has_density_sensitive_layout: bool | None = None,
) -> list[dict[str, Any]]:
    # boxes / has_density_sensitive_layout 可由 validate_svg_input 主体一次性算好
    # 后注入；缺省时本函数自带兜底，保持向后兼容（对外语义不变）。
    if boxes is None or has_density_sensitive_layout is None:
        boxes, has_density_sensitive_layout = _collect_visual_boxes_for_density(
            root,
            page_height=page_height,
        )
    if not has_density_sensitive_layout or not boxes or page_height <= 0:
        return []

    content_bottom = max(box.bottom for box in boxes)
    required_bottom = page_height * 0.84
    if content_bottom >= required_bottom:
        return []

    return [
        _issue(
            "SVG_LAYOUT_VERTICAL_UNDERUSED",
            (
                "矩阵、象限或对比表类 SVG 主体没有充分使用页面高度；"
                "请增大主体卡片/矩阵/表格区域高度，或把结论/行动条下沉到内容区底部后重试。"
            ),
            content_bottom=round(content_bottom, 1),
            required_min_bottom=round(required_bottom, 1),
            bottom_blank=round(page_height - content_bottom, 1),
        )
    ]


def _detect_content_page_vertical_fill_warnings(
    root: ET.Element,
    *,
    page_height: float,
    page_archetype: str | None,
    boxes: list[_SvgVisualBox] | None = None,
    has_density_sensitive: bool | None = None,
) -> list[dict[str, Any]]:
    """非密度敏感布局的内容页垂直填充软提示。

    职责边界：
    - 只对内容页（非固定页型）生效；page_archetype 在豁免集合中时不报。
    - 与 _detect_layout_density_issues 互补：那个是 blocking、对矩阵/对比表生效；
      这个是 warning、对其它内容页生效，避免内容只占上半屏。
    - 阈值 0.78 比 matrix 的 0.84 宽松，且作为 warning 不阻塞，仅提示模型下沉主体。

    boxes / has_density_sensitive 可由 validate_svg_input 主体一次性算好后注入；
    缺省时本函数自带兜底，保持向后兼容。
    """
    # 归一一次后，豁免判定与 warning 字段都用同一份归一值，避免 warning 携带
    # 外部传入的非归一字符串（例如 " content "）。
    normalized_archetype = (
        page_archetype.strip().lower()
        if isinstance(page_archetype, str) and page_archetype.strip()
        else "content"
    )
    if normalized_archetype in _CONTENT_FILL_EXEMPT_ARCHETYPES or normalized_archetype == "component":
        return []
    if boxes is None or has_density_sensitive is None:
        boxes, has_density_sensitive = _collect_visual_boxes_for_density(
            root,
            page_height=page_height,
        )
    # 矩阵/对比表已被 _detect_layout_density_issues 覆盖（blocking），
    # 这里跳过避免重复信号。
    if has_density_sensitive or not boxes or page_height <= 0:
        return []
    content_bottom = max(box.bottom for box in boxes)
    suggested_min_bottom = page_height * _CONTENT_PAGE_VERTICAL_FILL_RATIO
    if content_bottom >= suggested_min_bottom:
        return []
    bottom_ratio = round(content_bottom / page_height, 3)
    return [
        _issue(
            "SVG_CONTENT_VERTICAL_UNDERUSED",
            (
                f"内容主体仅延伸到 y≈{round(content_bottom, 1)}"
                f"（{round(bottom_ratio * 100, 1)}%），"
                f"建议下沉到 y≥{round(suggested_min_bottom, 1)}"
                f"（≥{int(_CONTENT_PAGE_VERTICAL_FILL_RATIO * 100)}%）以铺满下半屏。"
                "这是软提示，不阻断渲染；如本页确为封面/章节/总结/目录/免责页型，"
                "请在 page_archetype 中显式声明。"
            ),
            content_bottom=round(content_bottom, 1),
            suggested_min_bottom=round(suggested_min_bottom, 1),
            bottom_ratio=bottom_ratio,
            page_archetype=normalized_archetype,
        )
    ]


def _overlap_ratio(a: _SvgTextBox, b: _SvgTextBox) -> tuple[float, float, float]:
    x_overlap = min(a.x + a.width, b.x + b.width) - max(a.x, b.x)
    y_overlap = min(a.y + a.height, b.y + b.height) - max(a.y, b.y)
    if x_overlap <= 0 or y_overlap <= 0:
        return 0.0, x_overlap, y_overlap
    min_area = max(min(a.width * a.height, b.width * b.height), 1.0)
    return (x_overlap * y_overlap) / min_area, x_overlap, y_overlap


def _text_box_payload(box: _SvgTextBox) -> dict[str, Any]:
    return {
        "element_id": box.element_id,
        "layer_id": box.layer_id,
        "tag": "text",
        "x": round(box.x, 1),
        "y": round(box.y, 1),
        "width": round(box.width, 1),
        "height": round(box.height, 1),
        "text_excerpt": box.text_excerpt,
    }


def _detect_text_overlap_issues(root: ET.Element) -> list[dict[str, Any]]:
    boxes = _collect_text_boxes(root)
    issues: list[dict[str, Any]] = []
    for index, first in enumerate(boxes):
        for second in boxes[index + 1 :]:
            ratio, x_overlap, y_overlap = _overlap_ratio(first, second)
            if (
                ratio < 0.18
                or x_overlap < 8
                or y_overlap < min(first.height, second.height) * 0.45
            ):
                continue
            element_boxes = [_text_box_payload(first), _text_box_payload(second)]
            issues.append(
                _issue(
                    "SVG_TEXT_OVERLAP",
                    "SVG 文本节点存在明显重叠；请调整文本区域、换行或缩短内容，避免文字互相覆盖。",
                    # `elements` 保持旧的 id 列表（既有契约），新增的定位/修复字段
                    # 只做增量：模型光有 `text@x:y` 合成 id 无法调 patch_svg_layer。
                    elements=[first.element_id, second.element_id],
                    overlap_ratio=round(ratio, 3),
                    element_boxes=element_boxes,
                    layer_ids=[
                        layer
                        for layer in (first.layer_id, second.layer_id)
                        if layer
                    ],
                    overlap_px={
                        "x": round(x_overlap, 1),
                        "y": round(y_overlap, 1),
                    },
                    repair_ops=build_text_overlap_ops(
                        element_boxes=element_boxes,
                        overlap_x_px=x_overlap,
                        overlap_y_px=y_overlap,
                    ),
                )
            )
    return issues


def _bounds_offenders(
    boxes: list[_SvgVisualBox],
    *,
    page_width: float,
    page_height: float,
) -> list[dict[str, Any]]:
    """越出画布的元素清单，按越界量降序。

    没有这张清单，模型面对 "右边界到 1422px" 只能 read_file 重读整页 SVG 逐个元素
    比对坐标（真实回归 72f408ce：单页 read_file 重读 + 盲 patch 循环）。
    """

    offenders: list[dict[str, Any]] = []
    for box in boxes:
        overflow_x = box.right - page_width
        overflow_y = box.bottom - page_height
        if overflow_x <= 0 and overflow_y <= 0:
            continue
        offenders.append(
            {
                "element_id": box.element_id,
                "layer_id": box.layer_id,
                "tag": box.tag,
                "x": round(box.x, 1),
                "y": round(box.y, 1),
                "right": round(box.right, 1),
                "bottom": round(box.bottom, 1),
                "overflow_x": round(max(overflow_x, 0.0), 1),
                "overflow_y": round(max(overflow_y, 0.0), 1),
            }
        )
    offenders.sort(
        key=lambda item: max(item["overflow_x"], item["overflow_y"]),
        reverse=True,
    )
    return offenders[:MAX_OFFENDERS]


def _detect_content_bounds_issues(
    root: ET.Element,
    *,
    page_width: float,
    page_height: float,
    content_bbox: dict[str, Any] | None = None,
    boxes: list[_SvgVisualBox] | None = None,
) -> list[dict[str, Any]]:
    """内容主体横向/纵向越界检测（blocking）。

    真实回归：内容主体右边界超出画布（right_ratio>1.0）仍被判 ok 进 renderer，
    导致最终 PPTX 右侧长正文被裁断。这里复用 _content_bbox_summary 已算好的主体
    bbox，对 right_ratio / bottom_ratio > 1.0 升级为 blocking。
    阈值用 > 1.0（ratio 已 round 3 位），给刚好贴边 1.0 留容差。

    content_bbox 可由 validate_svg_input 主体一次性算好后注入，避免重复遍历。
    对缺 viewBox（page_width/height<=0）或无主体 bbox 的畸形输入安全返回空 list。
    """
    if page_width <= 0 or page_height <= 0:
        return []
    if content_bbox is None:
        content_bbox = _content_bbox_summary(
            root, page_width=page_width, page_height=page_height
        )
    if not content_bbox:
        return []
    right_ratio = content_bbox.get("right_ratio", 0.0)
    bottom_ratio = content_bbox.get("bottom_ratio", 0.0)
    horizontal_overflow = right_ratio > _CONTENT_BOUNDS_OVERFLOW_RATIO
    vertical_overflow = bottom_ratio > _CONTENT_BOUNDS_OVERFLOW_RATIO
    if not horizontal_overflow and not vertical_overflow:
        return []
    directions = []
    if horizontal_overflow:
        directions.append(
            f"右边界到 {content_bbox.get('right')}px（画布宽 {round(page_width, 1)}px）"
        )
    if vertical_overflow:
        directions.append(
            f"下边界到 {content_bbox.get('bottom')}px（画布高 {round(page_height, 1)}px）"
        )
    if boxes is None:
        boxes, _sensitive = _collect_visual_boxes_for_density(
            root,
            page_height=page_height,
        )
    offenders = _bounds_offenders(
        boxes,
        page_width=page_width,
        page_height=page_height,
    )
    overflow_x_px = round(max(float(content_bbox.get("right") or 0.0) - page_width, 0.0), 1)
    overflow_y_px = round(max(float(content_bbox.get("bottom") or 0.0) - page_height, 0.0), 1)
    offender_hint = ""
    if offenders:
        offender_hint = "越界元素：" + "、".join(
            f"{item['element_id']}(layer={item['layer_id'] or '无'}，超出 "
            f"{max(item['overflow_x'], item['overflow_y'])}px)"
            for item in offenders
        )
    return [
        _issue(
            "SVG_CONTENT_BOUNDS_OVERFLOW",
            (
                "SVG 内容主体超出画布可视范围（" + "；".join(directions) + "），"
                "最终 PPTX 会被裁断；请按 repair_ops 逐条 patch_svg_layer 收回越界元素，"
                "不要整页重写、也不要重读整份 SVG。" + offender_hint
            ),
            content_bbox=content_bbox,
            right_ratio=right_ratio,
            bottom_ratio=bottom_ratio,
            page_width=round(page_width, 1),
            page_height=round(page_height, 1),
            overflow_x_px=overflow_x_px,
            overflow_y_px=overflow_y_px,
            offending_elements=offenders,
            repair_ops=build_bounds_overflow_ops(
                offending_elements=offenders,
                overflow_x_px=overflow_x_px,
                overflow_y_px=overflow_y_px,
            ),
        )
    ]


def _estimate_text_run_width(text: str, font_size: float) -> float:
    # 中文按 ~1.0×font-size、ASCII 按 ~0.55×font-size、空白按 ~0.33 估算字符宽。
    width = 0.0
    for ch in text:
        if ch.isspace():
            width += font_size * _TEXT_CAPACITY_SPACE_WIDTH_RATIO
        elif ord(ch) < 128:
            width += font_size * _TEXT_CAPACITY_ASCII_WIDTH_RATIO
        else:
            width += font_size * _TEXT_CAPACITY_CJK_WIDTH_RATIO
    return width


def _detect_text_capacity_issues(
    root: ET.Element,
    *,
    page_width: float,
    layer_index: dict[int, str] | None = None,
) -> list[dict[str, Any]]:
    """文本盒容量越界检测（blocking）。

    覆盖"长句未折行但与其它文本不重叠"的裁断场景：单个 <text> 直接承载长正文、
    从靠右 x 起、无 <tspan> 分行，估算右边界远超画布。_detect_text_overlap_issues
    只能发现互压，发现不了这种"自己一行排到画布外"的裁断，所以单独估算。

    估算右边界 = 起始 x - text-anchor 偏移 + 估算文本宽；超过 page_width（留 2% 容差）
    且该 <text> 未用 <tspan> 多行拆分时判 blocking。用 <tspan> 主动控宽的视为已折行豁免。
    对缺 viewBox（page_width<=0）的畸形输入安全返回空 list。
    """
    if page_width <= 0:
        return []
    threshold = page_width * (1 + _TEXT_CAPACITY_TOLERANCE_RATIO)
    if layer_index is None:
        layer_index = _build_layer_index(root)
    issues: list[dict[str, Any]] = []
    for elem in root.iter():
        if _local_name(elem.tag).lower() != "text" or _is_hidden_text(elem):
            continue
        # 用 <tspan> 多行拆分的文本视为模型已主动控宽，豁免（单行 tspan 不豁免）。
        tspans = [child for child in elem if _local_name(child.tag).lower() == "tspan"]
        if len(tspans) >= 2:
            continue
        # 直接文本（不含 tspan 内容）：只看本节点直接承载的可见文字。
        text = (elem.text or "").strip() if not tspans else _visible_text_content(elem)
        raw_x = _first_position(elem, "x")
        if not text or raw_x is None:
            continue
        font_size = _read_font_size(elem)
        run_width = _estimate_text_run_width(text, font_size)
        left = raw_x - _text_anchor_offset(elem, run_width)
        estimated_right = left + run_width
        if estimated_right <= threshold:
            continue
        # element_id 过去直接取 attrib（几乎总是 None），模型拿不到任何定位。
        # 这里回落成坐标定位串并补 layer_id，让 patch_svg_layer 能直接落点。
        element_id = _own_id(elem) or f"text@{round(left)}:{round(_first_position(elem, 'y') or 0)}"
        layer_id = layer_index.get(id(elem))
        overflow_px = round(estimated_right - page_width, 1)
        # 每行安全字数：按剩余可用宽度反推（中文按 1.0×font-size 估宽）。
        usable_width = max(page_width - left, font_size)
        max_chars_per_line = max(int(usable_width / max(font_size, 1.0)), 4)
        issues.append(
            _issue(
                "SVG_TEXT_BOX_OVERFLOW",
                (
                    "单个 <text> 长句未折行，估算右边界超出画布会被裁断；"
                    "请拆成 2-3 行 <tspan>（各自带 x 与 dy）或压缩为更短的短语。"
                    f"（元素 {element_id}，layer={layer_id or '无'}，超出 {overflow_px}px）"
                ),
                element_id=element_id,
                layer_id=layer_id,
                text_excerpt=text[:40],
                start_x=raw_x,
                font_size=font_size,
                char_count=len(text),
                estimated_width=round(run_width, 1),
                estimated_right=round(estimated_right, 1),
                page_width=round(page_width, 1),
                overflow_px=overflow_px,
                max_chars_per_line=max_chars_per_line,
                repair_ops=build_text_box_overflow_ops(
                    layer_id=layer_id,
                    element_id=element_id,
                    overflow_px=overflow_px,
                    char_count=len(text),
                    font_size=font_size,
                    max_chars_per_line=max_chars_per_line,
                ),
            )
        )
    return issues


def _collect_long_line_segments(
    elem: ET.Element,
    *,
    min_length: float,
    translate_x: float = 0.0,
    translate_y: float = 0.0,
) -> list[tuple[float, float, float, float]]:
    """收集长直线段端点（line / path 内的直线段）用于穿透检测。

    保守起见只取明确的直线：<line> 端点，以及 <path> 中 M/L 直线指令；
    曲线（C/Q/A 等）忽略。长度 < min_length 的短段过滤掉，避免误判短装饰线。
    """
    local_tx, local_ty = _read_translate(elem.attrib.get("transform"))
    cur_x = translate_x + local_tx
    cur_y = translate_y + local_ty
    segments: list[tuple[float, float, float, float]] = []
    name = _local_name(elem.tag).lower()
    if name == "line":
        x1 = _parse_float(elem.attrib.get("x1"))
        y1 = _parse_float(elem.attrib.get("y1"))
        x2 = _parse_float(elem.attrib.get("x2"))
        y2 = _parse_float(elem.attrib.get("y2"))
        if None not in {x1, y1, x2, y2}:
            assert x1 is not None and y1 is not None and x2 is not None and y2 is not None
            seg = (cur_x + x1, cur_y + y1, cur_x + x2, cur_y + y2)
            if _segment_length(seg) >= min_length:
                segments.append(seg)
    elif name == "path":
        segments.extend(
            seg
            for seg in _path_line_segments(elem.attrib.get("d"), cur_x, cur_y)
            if _segment_length(seg) >= min_length
        )
    for child in elem:
        segments.extend(
            _collect_long_line_segments(
                child,
                min_length=min_length,
                translate_x=cur_x,
                translate_y=cur_y,
            )
        )
    return segments


def _segment_length(seg: tuple[float, float, float, float]) -> float:
    x1, y1, x2, y2 = seg
    return ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5


def _path_line_segments(
    d: str | None, base_x: float, base_y: float
) -> list[tuple[float, float, float, float]]:
    # 只解析绝对 M/L 直线指令，构造直线段；曲线/相对指令忽略，宁可漏报。
    if not d:
        return []
    commands = re.findall(r"([MLml])\s*(-?\d+(?:\.\d+)?)[\s,]+(-?\d+(?:\.\d+)?)", d)
    points: list[tuple[float, float]] = []
    for cmd, sx, sy in commands:
        if cmd in {"M", "L"}:
            points.append((base_x + float(sx), base_y + float(sy)))
        else:
            # 相对指令无法在不跟踪全程游标的情况下可靠定位，跳过保持保守。
            return [
                (points[i][0], points[i][1], points[i + 1][0], points[i + 1][1])
                for i in range(len(points) - 1)
            ]
    return [
        (points[i][0], points[i][1], points[i + 1][0], points[i + 1][1])
        for i in range(len(points) - 1)
    ]


def _segment_intersects_box(
    seg: tuple[float, float, float, float], box: _SvgTextBox
) -> bool:
    """线段是否穿过文字 bbox 的中部（不是仅擦边）。

    保守判定：把 bbox 上下各内缩 25%（只看中间 50% 高度带），用线段端点采样，
    若任一采样点落在内缩矩形内即判穿透。避免把擦着文字顶/底边的线判为穿透。
    """
    inset_y = box.height * 0.25
    top = box.y + inset_y
    bottom = box.y + box.height - inset_y
    left = box.x
    right = box.x + box.width
    if bottom <= top or right <= left:
        return False
    x1, y1, x2, y2 = seg
    samples = 24
    for i in range(samples + 1):
        t = i / samples
        px = x1 + (x2 - x1) * t
        py = y1 + (y2 - y1) * t
        if left <= px <= right and top <= py <= bottom:
            return True
    return False


def _detect_line_text_collision(root: ET.Element) -> list[dict[str, Any]]:
    """连线穿透中心文字检测（warning，不阻断）。

    真实回归：网络图对角直线穿过中心大字。装饰线常见且无害，所以这里只发 warning，
    宁可漏报也不把正常装饰线误判 blocking。
    """
    page_width, _page_height = _read_viewbox_size(root)
    if page_width <= 0:
        return []
    min_length = page_width * _LINE_COLLISION_MIN_LENGTH_RATIO
    segments = _collect_long_line_segments(root, min_length=min_length)
    if not segments:
        return []
    text_boxes = _collect_text_boxes(root)
    if not text_boxes:
        return []
    warnings: list[dict[str, Any]] = []
    seen: set[str] = set()
    for box in text_boxes:
        for seg in segments:
            if not _segment_intersects_box(seg, box):
                continue
            if box.element_id in seen:
                break
            seen.add(box.element_id)
            warnings.append(
                _issue(
                    "SVG_LINE_TEXT_COLLISION",
                    (
                        "长连线疑似穿过文字中部，可能压住可读性；"
                        "请让连线在文字处断开，或给文字加遮罩底板后重试。"
                    ),
                    element_id=box.element_id,
                )
            )
            break
    return warnings


def validate_svg_input(
    svg: str,
    *,
    max_bytes: int = DEFAULT_MAX_SVG_BYTES,
    max_data_uri_bytes: int = DEFAULT_MAX_DATA_URI_BYTES,
    allow_framework_chrome: bool = False,
    page_archetype: str | None = None,
) -> SvgInputGateResult:
    """Validate model-authored SVG before saving or conversion.

    ``allow_framework_chrome`` 区分两种校验语境:
    - 默认 False: 校验模型实时生成的内容层 SVG。整页背景、页眉/页脚/页码 chrome、
      页级边框由 deck_framework 在 PPT 框架层统一处理, 内容层禁止重复生成。
    - True: 校验完整独立成品 deck (例如离线参考示例套件)。这类 deck 没有单独的
      框架层, 自带整页背景与页面外框是合理的, 因此跳过这四条框架层 chrome 规则;
      其余安全/转换/可读性规则 (脚本、DOCTYPE、远程资源、超大、text fill、对比度、
      文本重叠) 仍然照常执行。

    ``page_archetype`` 用于内容页垂直填充软提示：豁免集合 (cover/agenda/
    section_divider/closing/disclaimer) 内的固定页型不报；缺省 / 空 / 未识别
    时按内容页处理。
    """

    if not isinstance(svg, str) or not svg.strip():
        return SvgInputGateResult(
            ok=False,
            blocking_issues=[_issue("SVG_INVALID_XML", "SVG 内容为空或不是字符串。")],
        )
    # page_archetype 是公开接口参数，调用方可能传非法类型；为避免下游
    # `.strip().lower()` 抛 AttributeError 打断 WebSocket 主循环，
    # 这里把非 str / 非 None 的输入归一为 None（按内容页兜底）。
    if page_archetype is not None and not isinstance(page_archetype, str):
        page_archetype = None
    raw_bytes = svg.encode("utf-8")
    if len(raw_bytes) > max_bytes:
        return SvgInputGateResult(
            ok=False,
            blocking_issues=[
                _issue("SVG_TOO_LARGE", f"SVG 超过 {max_bytes} bytes。", bytes=len(raw_bytes))
            ],
        )
    upper = svg[:512].upper()
    if "<!DOCTYPE" in upper or "<!ENTITY" in upper:
        return SvgInputGateResult(
            ok=False,
            blocking_issues=[
                _issue("SVG_EXTERNAL_ENTITY", "SVG 不能包含 DOCTYPE 或 ENTITY。")
            ],
        )
    try:
        root = ET.fromstring(svg)
    except ET.ParseError as exc:
        return SvgInputGateResult(
            ok=False,
            blocking_issues=[
                _issue("SVG_INVALID_XML", "SVG XML 不良构。", detail=str(exc))
            ],
        )
    if _local_name(root.tag) != "svg":
        return SvgInputGateResult(
            ok=False,
            blocking_issues=[_issue("SVG_INVALID_XML", "根节点必须是 <svg>。")],
        )

    issues: list[dict[str, Any]] = []
    has_dark_background = _has_dark_background(root)
    page_width, page_height = _read_viewbox_size(root)
    # 合法 data-effect-3d 声明计数;超过每页上限单独报 OVERUSE(防全页乱挂 3D)。
    effect_3d_count = 0
    for elem in root.iter():
        name = _local_name(elem.tag).lower()
        if name in _DANGEROUS_TAG_CODES:
            issues.append(
                _issue(_DANGEROUS_TAG_CODES[name], _DANGEROUS_TAG_MESSAGES[name])
            )
        if not allow_framework_chrome and _has_forbidden_chrome_identity(elem):
            issues.append(
                _issue(
                    "SVG_PAGE_HEADER_FORBIDDEN",
                    (
                        "SVG 禁止生成页眉、页脚、页码、章节胶囊、breadcrumb 或其它页面 "
                        "chrome；这些由 PPT 框架层生成。"
                    ),
                    element_id=elem.attrib.get("id"),
                    element_class=elem.attrib.get("class"),
                )
            )
        if not allow_framework_chrome and _is_full_page_background_rect(
            elem, page_width=page_width, page_height=page_height
        ):
            issues.append(
                _issue(
                    "SVG_FULL_PAGE_BACKGROUND_FORBIDDEN",
                    "SVG 禁止生成整页背景矩形；背景只允许由 deck_framework 在 PPT 框架层处理。",
                )
            )
        if not allow_framework_chrome and _is_full_page_image(
            elem, page_width=page_width, page_height=page_height
        ):
            issues.append(
                _issue(
                    "SVG_FULL_PAGE_IMAGE_FORBIDDEN",
                    (
                        "SVG 禁止生成整页背景图片；整页背景图请交给 "
                        "deck_framework.background 处理。"
                    ),
                    element_id=elem.attrib.get("id"),
                    element_class=elem.attrib.get("class"),
                )
            )
        if not allow_framework_chrome and _is_page_level_side_border(
            elem, page_width=page_width, page_height=page_height
        ):
            issues.append(
                _issue(
                    "SVG_PAGE_SIDE_BORDER_FORBIDDEN",
                    "SVG 禁止生成贴边的页级侧边框或侧边竖条；页面外框由 PPT 框架层生成。",
                )
            )
        elif not allow_framework_chrome and _is_page_level_outer_border(
            elem,
            page_width=page_width,
            page_height=page_height,
        ):
            issues.append(
                _issue(
                    "SVG_PAGE_OUTER_BORDER_FORBIDDEN",
                    "SVG 禁止生成覆盖整页的外边框；页面外框由 PPT 框架层生成。",
                )
            )
        for attr_name in elem.attrib:
            if _attr_local_name(attr_name).startswith("on"):
                issues.append(
                    _issue(
                        "SVG_EVENT_HANDLER_FORBIDDEN",
                        "SVG 禁止包含 on* 事件处理属性。",
                    )
                )
        # data-effect-3d 是转换正确性/滥用校验,不是 chrome 归属校验,
        # 因此 allow_framework_chrome 语境同样执行(与 on*/script 拦截同类)。
        effect_3d_issues, effect_3d_valid = _check_effect_3d(elem, name)
        issues.extend(effect_3d_issues)
        if effect_3d_valid:
            effect_3d_count += 1
        if name == "text":
            fill = _element_paint(elem, "fill")
            if not fill:
                issues.append(
                    _issue(
                        "SVG_TEXT_FILL_MISSING",
                        "所有 <text> 必须显式声明 fill。",
                    )
                )
            elif has_dark_background and _is_near_black_color(fill):
                issues.append(
                    _issue(
                        "SVG_TEXT_CONTRAST_LOW",
                        "深色背景下 <text> fill 对比度过低。",
                    )
            )
    if effect_3d_count > _EFFECT_3D_MAX_PER_PAGE:
        issues.append(
            _issue(
                "SVG_EFFECT_3D_OVERUSE",
                f"单页 data-effect-3d 声明不得超过 {_EFFECT_3D_MAX_PER_PAGE} 个;"
                "真 3D 是语义强调装置,请只保留最重要的形状。",
                count=effect_3d_count,
                max=_EFFECT_3D_MAX_PER_PAGE,
            )
        )
    for href in _iter_href_values(root):
        if _REMOTE_URL_RE.match(href.strip()):
            issues.append(
                _issue("SVG_REMOTE_URL_FORBIDDEN", "SVG 禁止引用 http(s) 远程资源。")
            )
        if href.startswith("data:") and len(href.encode("utf-8")) > max_data_uri_bytes:
            issues.append(
                _issue(
                    "SVG_DATA_URI_OVERSIZED",
                    f"单个 data URI 超过 {max_data_uri_bytes} bytes。",
                )
            )
    issues.extend(
        _detect_card_edge_bar_issues(
            root,
            page_width=page_width,
            page_height=page_height,
        )
    )
    issues.extend(_detect_text_overlap_issues(root))
    # 共享 visual boxes 与 density 标记，避免两个 detector 重复遍历整棵 SVG 树。
    density_boxes, density_sensitive = _collect_visual_boxes_for_density(
        root,
        page_height=page_height,
    )
    if page_archetype != "component":
        issues.extend(
            _detect_layout_density_issues(
                root,
                page_height=page_height,
                boxes=density_boxes,
                has_density_sensitive_layout=density_sensitive,
            )
        )
    issues.extend(
        _detect_empty_content_container_issues(
            root,
            page_width=page_width,
            page_height=page_height,
            page_archetype=page_archetype,
        )
    )
    # 内容页垂直填充软提示：不进 blocking_issues，单独走 warnings 字段。
    warnings = _detect_content_page_vertical_fill_warnings(
        root,
        page_height=page_height,
        page_archetype=page_archetype,
        boxes=density_boxes,
        has_density_sensitive=density_sensitive,
    )
    font_size_report = _build_font_size_report(
        root,
        page_archetype=page_archetype,
    )
    if font_size_report.get("affected_text_runs"):
        warnings.append(
            _issue(
                "SVG_TEXT_FONT_SIZE_BELOW_MINIMUM",
                (
                    "内容页存在未满足角色字号合同的可见文字（正文 15px、"
                    "密集表格/流程/图表标签 12px、来源/注释 11px）；"
                    "请压缩内容或重排版式，不要继续缩小字号。该值是 SVG px，"
                    "不是可直接等同的 PPT pt。"
                ),
                minimum_font_size_svg_px=font_size_report["minimum_font_size_svg_px"],
                role_thresholds_svg_px=font_size_report["role_thresholds_svg_px"],
                minimum_observed_font_size_svg_px=font_size_report[
                    "minimum_observed_font_size_svg_px"
                ],
                below_12=font_size_report["below_12"],
                below_15=font_size_report["below_15"],
                below_18=font_size_report["below_18"],
                role_violation_counts=font_size_report["role_violation_counts"],
                affected_text_runs=font_size_report["affected_text_runs"],
                offending_elements=font_size_report["offending_elements"],
                page_archetype=font_size_report["page_archetype"],
            )
        )
    # 横向/纵向越界（blocking）：复用主体 bbox，避免裁断进入 renderer。
    content_bbox = _content_bbox_summary(
        root, page_width=page_width, page_height=page_height
    )
    issues.extend(
        _detect_content_bounds_issues(
            root,
            page_width=page_width,
            page_height=page_height,
            content_bbox=content_bbox,
            boxes=density_boxes,
        )
    )
    # 文本盒容量越界（blocking）：长句未折行但不重叠的裁断。
    issues.extend(_detect_text_capacity_issues(root, page_width=page_width))
    # 连线穿透文字（warning）：保守判定，宁可漏报不误杀装饰线。
    warnings.extend(_detect_line_text_collision(root))
    summary = _build_summary(
        root,
        len(raw_bytes),
        font_size_report=font_size_report,
    )
    if issues:
        return SvgInputGateResult(
            ok=False,
            blocking_issues=issues,
            warnings=warnings,
            summary=summary,
        )

    return SvgInputGateResult(
        ok=True,
        warnings=warnings,
        summary=summary,
    )
