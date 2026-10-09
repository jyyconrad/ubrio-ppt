"""Build one gold-standard Chinese business SVG slide from structured JSON.

This helper distills the reusable page-building patterns from
render_svg_ppt_examples.py into a single-page builder. It is intentionally
standalone: weak models can first validate and normalize a page_spec JSON,
write a repair patch, then build one bounded SVG saved as
slide-generation/<page_id>/svg_drawingml/source.svg.
"""

from __future__ import annotations

import argparse
import copy
import html
import json
import re
import sys
from pathlib import Path
from typing import Any

_GATES_HOME = Path(__file__).resolve().parent
if str(_GATES_HOME) not in sys.path:
    sys.path.insert(0, str(_GATES_HOME))

from gates.runner import run_page_gates, run_svg_gates
from gates.visual import compute_layout_fingerprint
from check_shape_picture import check_shape_picture

W, H = 1280, 720
FONT = "Microsoft YaHei, Arial"
SPEC_SCHEMA_VERSION = "gold_page_spec/v1"

THEMES: dict[str, dict[str, str]] = {
    "business_blue": {
        "background": "#F6F8FB",
        "surface": "#FFFFFF",
        "title_text": "#0F172A",
        "body_text": "#334155",
        "muted_text": "#64748B",
        "source_text": "#64748B",
        "accent": "#2563EB",
        "accent2": "#0EA5E9",
        "warning": "#B91C1C",
        "border": "#D9E2EC",
    },
    "project_blue": {
        "background": "#F4F7FA",
        "surface": "#FFFFFF",
        "title_text": "#003D79",
        "body_text": "#243447",
        "muted_text": "#6B7A90",
        "source_text": "#6B7A90",
        "accent": "#2F80ED",
        "accent2": "#F59E0B",
        "warning": "#B91C1C",
        "border": "#D7DEE8",
    },
    "dark_business": {
        "background": "#07111F",
        "surface": "#0F2438",
        "title_text": "#FFFFFF",
        "body_text": "#D8E7FF",
        "muted_text": "#8CA3C7",
        "source_text": "#8CA3C7",
        "accent": "#45D1FF",
        "accent2": "#A7F3D0",
        "warning": "#FCA5A5",
        "border": "#2B4C7E",
    },
}

DEFAULT_COLUMNS = ["事项", "证据/口径", "影响", "Owner", "状态"]
STRUCTURED_FIELDS = (
    "claim",
    "evidence",
    "explanation",
    "implication",
    "action",
    "risk",
)
PLACEHOLDER_MARKERS = (
    "待补：",
    "待补指标",
    "待补来源",
    "待补模块",
    "待补事项",
    "待补证据",
    "待补行动",
    "待补口径",
    "待补Owner",
    "待补 owner",
    "待补 ",
    "待补",
    "需补充：",
    "Owner 待定",
)

DEFAULT_QUALITY_TARGETS = {
    "metrics_min": 3,
    "groups_min": 3,
    "rows_min": 4,
    "steps_min": 4,
    "evidence_per_group_min": 2,
    "structured_fields_min": 3,
    "sources_min": 1,
}


def build_page_spec_template(
    *,
    layout: str = "gold_cards",
    theme_id: str = "business_blue",
    page_role: str = "content",
) -> dict[str, Any]:
    """生成弱模型可逐步填充的复杂 page_spec 模板。"""

    layout = _select_layout({"layout": layout, "page_role": page_role})
    spec: dict[str, Any] = {
        "schema_version": SPEC_SCHEMA_VERSION,
        "page_role": page_role,
        "theme_id": theme_id,
        "layout": layout,
        "stage_label": "仅供框架层页眉使用，SVG 不渲染此字段",
        "title": "待补：观点句标题，不写名词短语",
        "key_message": "待补：一句话写清本页核心判断和决策含义",
        "framework_layer": {
            "background_owner": "ppt_framework",
            "draw_full_page_background_in_svg": False,
            "safe_area": {"x": 58, "y": 38, "w": 1165, "h": 643},
        },
        "structure_hierarchy": {
            "semantic_layer": ["待补：核心判断", "待补：关键证据", "待补：行动/风险", "待补：来源"],
            "narrative_layer": ["结论先行", "证据链", "解释影响", "行动闭环"],
            "visual_layer": ["main-title", "key-message", "metric-strip", "main-content", "action-bar"],
            "geometry_layer": ["title-band", "metric-strip", "main-body", "source-note"],
            "svg_group_layer": [
                "main-title-block",
                "key-message",
                "metrics-panel",
                "main-content",
                "chart-slot-1",
                "screenshot-proof-1",
                "source-note",
            ],
        },
        "quality_targets": dict(DEFAULT_QUALITY_TARGETS),
        "visual_tokens": {
            "background": "待补：框架层背景 token，SVG 不绘制整页背景",
            "surface": "待补：卡片/面板底色",
            "title_text": "待补：标题颜色",
            "body_text": "待补：正文颜色",
            "source_text": "待补：来源文字颜色",
            "accent": "待补：强调色",
            "border": "待补：描边/分割线颜色",
        },
        "native_chart_slots": [],
        "native_table_slots": [],
        "evidence_asset_slots": [],
        "primary_claim": "待补：本页唯一主观点，谁在什么场景遇到什么问题、要做什么",
        "audience_takeaway": "待补：这页要听众记住什么",
        "plain_language_who_scene_problem_action": {
            "who": "待补：谁",
            "scene": "待补：场景",
            "problem": "待补：问题",
            "action": "待补：动作",
        },
        "typography": {"body_px": 16, "title_px": 32, "source_px": 11},
        "pyramid_region": {"x": 136, "y": 264, "w": 768, "h": 336},
        "pyramid_layers": [],
        "metrics": [_normalize_metric({}, index) for index in range(1, 4)],
        "sources": ["待补来源：当前页材料名 / 数据口径 / 公开来源"],
    }
    if layout in {"gold_evidence_table", "gold_action_ledger"}:
        spec["columns"] = DEFAULT_COLUMNS
        spec["rows"] = [_normalize_row({}, DEFAULT_COLUMNS, index) for index in range(1, 5)]
    elif layout == "gold_timeline":
        spec["steps"] = [_placeholder_group(index) for index in range(1, 5)]
    elif layout == "pyramid_hierarchy":
        spec["pyramid_layers"] = [_placeholder_pyramid_layer(index) for index in range(1, 4)]
        spec["groups"] = [_placeholder_group(index) for index in range(1, 4)]
    else:
        spec["groups"] = [_placeholder_group(index) for index in range(1, 4)]
    if layout == "gold_comparison":
        spec["dominant"] = "左右对照"
        spec["quality_targets"].update(metrics_min=0, groups_min=2)
        spec["metrics"] = []
        spec["groups"] = [_placeholder_group(index) for index in range(1, 3)]
        spec["boundary"] = "待补：两种方案共同的证据限制"
        spec["action"] = "待补：下一步核验什么，不补造负责人或时间"
        spec["typography"]["body_px"] = 22
    return spec


def build_fill_plan(spec: dict[str, Any]) -> dict[str, Any]:
    """给弱模型返回逐项补全顺序，避免一次性自由写 SVG。"""

    normalized = normalize_page_spec(spec)
    report = quality_report(normalized)
    layout = str(normalized.get("layout") or "")
    unit_key = "rows" if layout in {"gold_evidence_table", "gold_action_ledger"} else (
        "steps" if layout == "gold_timeline" else (
            "pyramid_layers" if layout == "pyramid_hierarchy" else "groups"
        )
    )
    return {
        "schema_version": SPEC_SCHEMA_VERSION,
        "quality_status": report["quality_status"],
        "next_steps": [
            "1. 先补 structure_hierarchy：语义层、讲述层、视觉层、几何层、SVG group 层。",
            "2. 再补 visual_tokens 或 theme_id，保证框架层背景、标题、正文、来源文字和线条可见。",
            "3. 把 title 改成观点句，把 key_message 写成本页核心判断。",
            "4. 补齐 3 个以上 metrics，每个指标都要有 label/value/note。",
            f"5. 补齐 {unit_key}：每个单元要有短标题、判断、证据、解释/影响、行动或风险。",
            "6. 补 sources，写清材料名、数据口径或证据缺口。",
            "7. 再运行 validate-only；quality_status=ready 后才生成 source.svg。",
        ],
        "missing": report["missing"],
        "target_unit_key": unit_key,
        "quality_targets": normalized.get("quality_targets", DEFAULT_QUALITY_TARGETS),
        "repair_patch": build_repair_patch(normalized),
    }


def _as_list(value: Any) -> list[Any]:
    if isinstance(value, list):
        return value
    if value is None:
        return []
    return [value]


def _deep_merge(base: dict[str, Any], patch: dict[str, Any]) -> dict[str, Any]:
    merged = copy.deepcopy(base)
    for key, value in patch.items():
        if key == "append" and isinstance(value, dict):
            for list_key, items in value.items():
                merged.setdefault(list_key, [])
                if isinstance(merged[list_key], list):
                    merged[list_key].extend(_as_list(items))
            continue
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = copy.deepcopy(value)
    return merged


def _filled(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            return False
        lowered = stripped.lower()
        return not any(marker.lower() in lowered for marker in PLACEHOLDER_MARKERS)
    if isinstance(value, list):
        return any(_filled(item) for item in value)
    if isinstance(value, dict):
        return any(_filled(item) for item in value.values())
    return True


def _select_layout(spec: dict[str, Any]) -> str:
    raw = str(spec.get("layout") or "").strip()
    if spec.get("dominant") == "左右对照" and raw in {"", "gold_cards", "gold_comparison"}:
        return "gold_comparison"
    if raw:
        if raw in {"table", "gold_issue_log"}:
            return "gold_evidence_table"
        if raw == "timeline":
            return "gold_timeline"
        if raw in {"pyramid", "pyramid_stack", "pyramid_hierarchy", "gold_pyramid"}:
            return "pyramid_hierarchy"
        return raw
    page_role = str(spec.get("page_role") or spec.get("page_archetype") or "").lower()
    if page_role in {"pyramid", "hierarchy", "strategy_hierarchy"}:
        return "pyramid_hierarchy"
    if page_role in {"timeline", "roadmap", "milestone"}:
        return "gold_timeline"
    if page_role in {"summary", "action", "closing"}:
        return "gold_action_ledger"
    if spec.get("rows"):
        return "gold_evidence_table"
    if spec.get("steps"):
        return "gold_timeline"
    return "gold_cards"


def _placeholder_group(index: int) -> dict[str, Any]:
    return {
        "title": f"待补模块{index}",
        "claim": "待补：写成可证明的判断句",
        "evidence": ["待补：事实/数据/案例一", "待补：事实/数据/案例二"],
        "explanation": "待补：说明原因或机制",
        "implication": "待补：说明影响",
        "action": "待补：Owner / 节点 / 风险",
    }


def _placeholder_pyramid_layer(index: int) -> dict[str, Any]:
    defaults = (
        ("目标层", "待补：最高判断或最终目标", ["待补：目标口径"]),
        ("能力层", "待补：中层抓手或能力组合", ["待补：抓手一", "待补：抓手二"]),
        ("证据层", "待补：底层证据、资源或行动", ["待补：证据一", "待补：证据二", "待补：行动"]),
    )
    title, claim, evidence = defaults[min(index - 1, len(defaults) - 1)]
    return {"title": title, "claim": claim, "evidence": evidence}


def _normalize_group(raw: Any, index: int, *, preserve_evidence: bool = False) -> dict[str, Any]:
    group = raw if isinstance(raw, dict) else {"title": str(raw or "")}
    normalized = _placeholder_group(index)
    normalized.update({str(key): value for key, value in group.items() if value is not None})
    evidence = list(_as_list(normalized.get("evidence")))
    if not preserve_evidence:
        evidence = evidence[:3]
    for field in ("explanation", "implication", "risk"):
        if len(evidence) >= 3 and not preserve_evidence:
            break
        value = normalized.get(field)
        if _filled(value) and (not preserve_evidence or value not in evidence):
            evidence.append(value)
    while len(evidence) < 2:
        evidence.append(f"待补：支撑事实 {len(evidence) + 1}")
    normalized["evidence"] = evidence if preserve_evidence else evidence[:3]
    if not normalized.get("role"):
        normalized["role"] = "待补：support/evidence/limitation/action/context"
    return normalized


def _normalize_metric(raw: Any, index: int) -> dict[str, Any]:
    metric = raw if isinstance(raw, dict) else {"label": str(raw or "")}
    return {
        "label": metric.get("label") or f"待补指标{index}",
        "value": metric.get("value") or "待补",
        "note": metric.get("note") or "待补：口径/来源",
        "evidence_type": metric.get("evidence_type") or "待补：experiment/survey/correlation/internal_baseline/policy",
        "claim_type": metric.get("claim_type") or "待补：fact/inference/mechanism_hypothesis/action",
        "population": metric.get("population") or "待补：样本/口径主体",
        "period": metric.get("period") or metric.get("year") or "待补：期间",
        "denominator": metric.get("denominator") or "待补：分母",
        "source_ref": metric.get("source_ref") or metric.get("source_url") or metric.get("source_section") or "待补：来源",
        "limitation": metric.get("limitation") or "待补：证据限制",
        "on_metric_label": metric.get("on_metric_label") or "待补：类型·口径·限制",
    }


def _normalize_row(raw: Any, columns: list[Any], index: int) -> dict[str, Any]:
    if isinstance(raw, dict) and isinstance(raw.get("cells"), list):
        cells = raw["cells"]
    elif isinstance(raw, dict):
        cells = [raw.get(str(col), "") for col in columns]
    else:
        cells = _as_list(raw)
    defaults = [f"待补{col}" for col in columns]
    merged = list(cells[: len(columns)])
    while len(merged) < len(columns):
        merged.append(defaults[len(merged)])
    if not _filled(merged):
        merged[0] = f"待补事项{index}"
    return {"cells": merged}


def _normalize_pyramid_layers(raw: Any) -> list[dict[str, Any]]:
    layers = [
        _normalize_group(item, idx + 1)
        for idx, item in enumerate(_as_list(raw))
        if _filled(item)
    ]
    while len(layers) < 3:
        layers.append(
            _normalize_group(
                _placeholder_pyramid_layer(len(layers) + 1),
                len(layers) + 1,
            )
        )
    return layers[:3]


def _quality_targets(spec: dict[str, Any]) -> dict[str, int]:
    targets = dict(DEFAULT_QUALITY_TARGETS)
    if _select_layout(spec) == "gold_comparison":
        targets.update(metrics_min=0, groups_min=2)
    raw = spec.get("quality_targets")
    if isinstance(raw, dict):
        for key, value in raw.items():
            if key in targets and type(value) is int and (value > 0 or (key == "metrics_min" and value == 0)):
                targets[key] = value
    role = str(spec.get("page_role") or spec.get("page_archetype") or "").strip().lower()
    if role in {"cover", "closing", "section_divider", "agenda", "chapter", "end"}:
        for key in (
            "metrics_min",
            "groups_min",
            "rows_min",
            "steps_min",
            "evidence_per_group_min",
            "structured_fields_min",
            "sources_min",
        ):
            targets[key] = 0
    return targets


def normalize_page_spec(spec: dict[str, Any]) -> dict[str, Any]:
    normalized = copy.deepcopy(spec)
    normalized["schema_version"] = normalized.get("schema_version") or SPEC_SCHEMA_VERSION
    normalized["theme_id"] = normalized.get("theme_id") or normalized.get("theme") or "business_blue"
    normalized["layout"] = _select_layout(normalized)
    normalized["quality_targets"] = _quality_targets(normalized)
    normalized["framework_layer"] = _normalize_framework_layer(normalized.get("framework_layer"))
    normalized["stage_label"] = normalized.get("stage_label") or "业务汇报 / 金标单页"
    normalized["title"] = normalized.get("title") or "待补：观点句标题"
    normalized["key_message"] = (
        normalized.get("key_message")
        or normalized.get("subtitle")
        or "待补：本页核心判断，必须说明要证明什么"
    )

    metrics = [_normalize_metric(item, idx + 1) for idx, item in enumerate(_as_list(normalized.get("metrics")))]
    targets = _quality_targets(normalized)
    while len(metrics) < targets["metrics_min"]:
        metrics.append(_normalize_metric({}, len(metrics) + 1))
    normalized["metrics"] = metrics[:5]

    sources = [str(item) for item in _as_list(normalized.get("sources")) if str(item).strip()]
    normalized["sources"] = sources or ["待补来源：当前页素材、公开来源或口径说明"]
    normalized["native_chart_slots"] = _normalize_chart_slots(
        normalized.get("native_chart_slots") or normalized.get("chart_slots"),
    )
    normalized["evidence_asset_slots"] = _as_list(normalized.get("evidence_asset_slots"))

    layout = normalized["layout"]
    if layout in {"gold_evidence_table", "gold_action_ledger"}:
        columns = _as_list(normalized.get("columns")) or DEFAULT_COLUMNS
        normalized["columns"] = columns
        rows = [
            _normalize_row(item, columns, idx + 1)
            for idx, item in enumerate(_as_list(normalized.get("rows")))
        ]
        while len(rows) < targets["rows_min"]:
            rows.append(_normalize_row({}, columns, len(rows) + 1))
        normalized["rows"] = rows[:7]
    elif layout == "gold_timeline":
        steps = [
            _normalize_group(item, idx + 1)
            for idx, item in enumerate(_as_list(normalized.get("steps") or normalized.get("groups")))
        ]
        while len(steps) < targets["steps_min"]:
            steps.append(_placeholder_group(len(steps) + 1))
        normalized["steps"] = steps[:6]
    elif layout == "pyramid_hierarchy":
        layers = _normalize_pyramid_layers(
            normalized.get("pyramid_layers") or normalized.get("layers") or normalized.get("groups")
        )
        normalized["pyramid_layers"] = layers
        normalized["groups"] = layers
        normalized["pyramid_region"] = _normalize_box(
            normalized.get("pyramid_region")
            or normalized.get("region")
            or normalized.get("pyramid_box"),
            default={"x": 136, "y": 264, "w": 768, "h": 336},
        )
    else:
        raw_groups = _as_list(normalized.get("groups") or normalized.get("cards"))
        if layout == "gold_comparison" and not raw_groups:
            raw_groups = [
                dict(panel, claim=panel.get("claim") or panel.get("sentence"))
                for panel in _as_list(normalized.get("panels"))
                if isinstance(panel, dict)
            ]
        groups = [
            _normalize_group(item, idx + 1, preserve_evidence=layout == "gold_comparison")
            for idx, item in enumerate(raw_groups)
        ]
        while len(groups) < targets["groups_min"]:
            groups.append(_placeholder_group(len(groups) + 1))
        normalized["groups"] = groups[:4]
    normalized["native_table_slots"] = _normalize_table_slots(normalized)
    typography = normalized.get("typography") if isinstance(normalized.get("typography"), dict) else {}
    typography.setdefault("body_px", 16)
    typography.setdefault("title_px", 32)
    typography.setdefault("source_px", 11)
    normalized["typography"] = typography
    if not normalized.get("layout_fingerprint"):
        fingerprint = compute_layout_fingerprint(normalized)
        if fingerprint:
            normalized["layout_fingerprint"] = fingerprint
    if not _filled(normalized.get("primary_claim")):
        normalized["primary_claim"] = normalized.get("primary_claim") or "待补：本页唯一主观点，谁在什么场景要做什么"
    if not _filled(normalized.get("audience_takeaway")):
        normalized["audience_takeaway"] = normalized.get("audience_takeaway") or "待补：这页要听众记住什么"
    who = normalized.get("plain_language_who_scene_problem_action")
    if not isinstance(who, dict):
        normalized["plain_language_who_scene_problem_action"] = {
            "who": "待补：谁",
            "scene": "待补：场景",
            "problem": "待补：问题",
            "action": "待补：动作",
        }
    return normalized


def _row_cells(row: Any, columns: list[Any]) -> list[str]:
    if isinstance(row, dict) and isinstance(row.get("cells"), list):
        cells = row["cells"]
    elif isinstance(row, dict):
        cells = [row.get(str(col), "") for col in columns]
    elif isinstance(row, (list, tuple)):
        cells = list(row)
    else:
        cells = [row]
    return [str(cell) for cell in cells[: len(columns) or None]]


def _normalize_table_slots(spec: dict[str, Any]) -> list[dict[str, Any]]:
    columns = _as_list(spec.get("columns")) or DEFAULT_COLUMNS
    raw_slots = spec.get("native_table_slots") or spec.get("table_slots")
    slots: list[dict[str, Any]] = []
    for index, item in enumerate(_as_list(raw_slots), start=1):
        if not isinstance(item, dict):
            continue
        slot_columns = _as_list(item.get("columns")) or columns
        rows = [_row_cells(row, slot_columns) for row in _as_list(item.get("rows") or spec.get("rows"))]
        box = item.get("box") if isinstance(item.get("box"), dict) else {"x": 70, "y": 288, "w": 1139, "h": 336}
        slots.append(
            {
                "id": item.get("id") or f"table-slot-{index}",
                "box": box,
                "columns": slot_columns,
                "rows": rows,
                "source": item.get("source") or (_as_list(spec.get("sources")) or ["待补来源"])[0],
                "title": item.get("title") or spec.get("table_title") or "原生表格",
                "style": copy.deepcopy(item.get("style")) if isinstance(item.get("style"), dict) else {},
            }
        )
    layout = str(spec.get("layout") or "")
    if not slots and layout in {"gold_evidence_table", "gold_action_ledger", "gold_issue_log", "table"}:
        rows = [_row_cells(row, columns) for row in _as_list(spec.get("rows"))]
        slots.append(
            {
                "id": "table-slot-1",
                "box": {"x": 70, "y": 288, "w": 1139, "h": 336},
                "columns": columns,
                "rows": rows,
                "source": (_as_list(spec.get("sources")) or ["待补来源"])[0],
                "title": spec.get("table_title") or "原生表格",
            }
        )
    return slots


def _normalize_box(raw: Any, *, default: dict[str, float]) -> dict[str, float]:
    box = raw if isinstance(raw, dict) else {}
    x = _float_or_default(box.get("x"), default["x"])
    y = _float_or_default(box.get("y"), default["y"])
    w = _float_or_default(box.get("w") or box.get("width"), default["w"])
    h = _float_or_default(box.get("h") or box.get("height"), default["h"])
    return {"x": x, "y": y, "w": max(w, 260.0), "h": max(h, 210.0)}


def _slot_box(slot: Any, *, default: dict[str, float]) -> dict[str, float]:
    if not isinstance(slot, dict):
        return dict(default)
    raw_box = slot.get("box") if isinstance(slot.get("box"), dict) else {}
    return {
        "x": _float_or_default(raw_box.get("x"), default["x"]),
        "y": _float_or_default(raw_box.get("y"), default["y"]),
        "w": _float_or_default(raw_box.get("w") or raw_box.get("width"), default["w"]),
        "h": _float_or_default(raw_box.get("h") or raw_box.get("height"), default["h"]),
    }


def _right_side_slot_min_x(spec: dict[str, Any]) -> float | None:
    min_x: float | None = None
    for key, default in (
        ("evidence_asset_slots", {"x": 544.0, "y": 196.0, "w": 656.0, "h": 384.0}),
        ("native_chart_slots", {"x": 736.0, "y": 312.0, "w": 344.0, "h": 208.0}),
    ):
        for slot in _as_list(spec.get(key)):
            box = _slot_box(slot, default=default)
            if box["x"] <= 70 or box["x"] >= 1210:
                continue
            min_x = box["x"] if min_x is None else min(min_x, box["x"])
    return min_x


def _bounded_visual_box(
    box: dict[str, float],
    *,
    max_right: float = 1209.0,
    max_bottom: float = 640.0,
    min_w: float = 120.0,
    min_h: float = 96.0,
) -> dict[str, float]:
    x = min(max(box["x"], 70.0), max_right - min_w)
    y = min(max(box["y"], 196.0), max_bottom - min_h)
    w = min(max(box["w"], min_w), max_right - x)
    h = min(max(box["h"], min_h), max_bottom - y)
    return {"x": x, "y": y, "w": w, "h": h}


def _boxes_overlap(a: dict[str, float], b: dict[str, float]) -> bool:
    return not (
        a["x"] + a["w"] <= b["x"]
        or b["x"] + b["w"] <= a["x"]
        or a["y"] + a["h"] <= b["y"]
        or b["y"] + b["h"] <= a["y"]
    )


def _float_or_default(value: Any, default: float) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return float(default)
    return parsed


def _normalize_framework_layer(raw: Any) -> dict[str, Any]:
    layer = raw if isinstance(raw, dict) else {}
    return {
        "background_owner": layer.get("background_owner") or "ppt_framework",
        "draw_full_page_background_in_svg": False,
        "safe_area": layer.get("safe_area") or {"x": 58, "y": 38, "w": 1165, "h": 643},
    }


def _normalize_chart_slots(raw: Any) -> list[dict[str, Any]]:
    slots: list[dict[str, Any]] = []
    for index, item in enumerate(_as_list(raw), start=1):
        if not isinstance(item, dict):
            continue
        box = item.get("box") if isinstance(item.get("box"), dict) else {}
        data = item.get("data") or item.get("series") or []
        rows: list[dict[str, Any]] = []
        for row in _as_list(data):
            if isinstance(row, dict):
                label = row.get("label") or row.get("name") or row.get("category")
                value = row.get("value")
            elif isinstance(row, list) and len(row) >= 2:
                label, value = row[0], row[1]
            else:
                continue
            if label is None or value is None:
                continue
            rows.append({"label": str(label), "value": value})
        slots.append(
            {
                "id": item.get("id") or f"chart-slot-{index}",
                "chart_type": item.get("chart_type") or item.get("type") or "bar",
                "box": {
                    "x": box.get("x", 736),
                    "y": box.get("y", 312),
                    "w": box.get("w") or box.get("width") or 344,
                    "h": box.get("h") or box.get("height") or 208,
                },
                "title": item.get("title") or "原生图表",
                "insight": item.get("insight") or item.get("caption") or "图表洞察待补",
                "source": item.get("source") or "来源口径待补",
                "unit": item.get("unit") or item.get("units") or item.get("y_unit") or "",
                "data": rows,
            }
        )
    return slots


def quality_report(spec: dict[str, Any]) -> dict[str, Any]:
    missing: list[str] = []
    layout = str(spec.get("layout") or "")
    targets = _quality_targets(spec)
    if not _filled(spec.get("title")):
        missing.append("title")
    if not _filled(spec.get("key_message")):
        missing.append("key_message")
    if len([item for item in _as_list(spec.get("sources")) if _filled(item)]) < targets["sources_min"]:
        missing.append(f"sources>={targets['sources_min']}")
    filled_metrics = [
        item for item in _as_list(spec.get("metrics"))
        if isinstance(item, dict)
        and _filled(item.get("label"))
        and _filled(item.get("value"))
        and _filled(item.get("note"))
    ]
    if len(filled_metrics) < targets["metrics_min"]:
        missing.append(f"metrics>={targets['metrics_min']}")

    units: list[Any]
    if layout in {"gold_evidence_table", "gold_action_ledger"}:
        units = _as_list(spec.get("rows"))
        filled_rows = [
            row for row in units
            if isinstance(row, dict)
            and sum(1 for cell in _as_list(row.get("cells")) if _filled(cell)) >= 4
        ]
        if len(filled_rows) < targets["rows_min"]:
            missing.append(f"rows>={targets['rows_min']}")
    elif layout == "gold_timeline":
        units = _as_list(spec.get("steps"))
        filled_steps = [item for item in units if _filled(item)]
        if len(filled_steps) < targets["steps_min"]:
            missing.append(f"steps>={targets['steps_min']}")
    elif layout == "pyramid_hierarchy":
        units = _as_list(spec.get("pyramid_layers") or spec.get("groups"))
        filled_layers = [item for item in units if _filled(item)]
        if len(filled_layers) < 3:
            missing.append("pyramid_layers>=3")
    else:
        units = _as_list(spec.get("groups"))
        filled_groups = [item for item in units if _filled(item)]
        if len(filled_groups) < targets["groups_min"]:
            missing.append(f"groups>={targets['groups_min']}")

    structured_hits = 0
    group_like = _as_list(spec.get("groups") or spec.get("steps"))
    for field in STRUCTURED_FIELDS:
        if any(_filled(item.get(field)) for item in group_like if isinstance(item, dict)):
            structured_hits += 1
    evidence_ready = True
    for item in group_like:
        if isinstance(item, dict):
            evidence_count = len([entry for entry in _as_list(item.get("evidence")) if _filled(entry)])
            if evidence_count < targets["evidence_per_group_min"]:
                evidence_ready = False
                break
    if layout in {"gold_evidence_table", "gold_action_ledger"} and _filled(spec.get("rows")):
        structured_hits = max(structured_hits, 3)
    if structured_hits < targets["structured_fields_min"]:
        missing.append(
            "claim/evidence/explanation/implication/action_or_risk"
            f">={targets['structured_fields_min']}"
        )
    if not evidence_ready:
        missing.append(f"evidence_per_group>={targets['evidence_per_group_min']}")

    if layout == "gold_comparison":
        missing.extend(_comparison_missing(spec))
    elif spec.get("dominant") == "左右对照":
        missing.append("comparison_requires_gold_comparison")

    semantic = run_page_gates(spec)
    for code in semantic.missing:
        if code not in missing:
            missing.append(code)

    return {
        "quality_status": "ready" if not missing else "needs_repair",
        "missing": missing,
        "warnings": semantic.warnings,
        "gates": semantic.details,
        "structured_hits": structured_hits,
        "layout": layout,
        "metric_count": len(_as_list(spec.get("metrics"))),
        "content_unit_count": len(units),
        "quality_targets": targets,
    }


def build_repair_patch(spec: dict[str, Any]) -> dict[str, Any]:
    patch: dict[str, Any] = {}
    append: dict[str, list[Any]] = {}
    if not _filled(spec.get("title")):
        patch["title"] = "待补：改写为观点句标题"
    if not _filled(spec.get("key_message")):
        patch["key_message"] = "待补：一句话写清本页核心判断"
    targets = _quality_targets(spec)
    filled_metrics = [
        item for item in _as_list(spec.get("metrics"))
        if isinstance(item, dict)
        and _filled(item.get("label"))
        and _filled(item.get("value"))
        and _filled(item.get("note"))
    ]
    if len(filled_metrics) < targets["metrics_min"]:
        patch["metrics"] = [
            _normalize_metric({}, index)
            for index in range(1, targets["metrics_min"] + 1)
        ]
    if len([item for item in _as_list(spec.get("sources")) if _filled(item)]) < targets["sources_min"]:
        patch["sources"] = ["待补来源：当前页材料名 / 数据口径 / 公开来源"]
    if not _filled(spec.get("primary_claim")):
        patch["primary_claim"] = "待补：本页唯一主观点，谁在什么场景遇到什么问题、要做什么"
    if not _filled(spec.get("audience_takeaway")):
        patch["audience_takeaway"] = "待补：这页要听众记住什么"
    who = spec.get("plain_language_who_scene_problem_action")
    if not isinstance(who, dict) or any(not _filled(who.get(key)) for key in ("who", "scene", "problem", "action")):
        patch["plain_language_who_scene_problem_action"] = {
            "who": "待补：谁",
            "scene": "待补：场景",
            "problem": "待补：问题",
            "action": "待补：动作",
        }

    layout = str(spec.get("layout") or "")
    if layout in {"gold_evidence_table", "gold_action_ledger"}:
        rows = _as_list(spec.get("rows"))
        existing = len(rows)
        filled_rows = [
            row for row in rows
            if isinstance(row, dict)
            and sum(1 for cell in _as_list(row.get("cells")) if _filled(cell)) >= 4
        ]
        if len(filled_rows) < targets["rows_min"]:
            columns = _as_list(spec.get("columns")) or DEFAULT_COLUMNS
            patch["rows"] = [
                _normalize_row({}, columns, index)
                for index in range(1, targets["rows_min"] + 1)
            ]
        elif existing < targets["rows_min"]:
            columns = _as_list(spec.get("columns")) or DEFAULT_COLUMNS
            append["rows"] = [
                _normalize_row({}, columns, index)
                for index in range(existing + 1, targets["rows_min"] + 1)
            ]
    elif layout == "gold_timeline":
        steps = _as_list(spec.get("steps"))
        existing = len(steps)
        if len([item for item in steps if _filled(item)]) < targets["steps_min"]:
            patch["steps"] = [_placeholder_group(index) for index in range(1, targets["steps_min"] + 1)]
        elif existing < targets["steps_min"]:
            append["steps"] = [
                _placeholder_group(index)
                for index in range(existing + 1, targets["steps_min"] + 1)
            ]
    elif layout == "pyramid_hierarchy":
        layers = _as_list(spec.get("pyramid_layers") or spec.get("groups"))
        if len([item for item in layers if _filled(item)]) < 3:
            patch["pyramid_layers"] = [
                _placeholder_pyramid_layer(index)
                for index in range(1, 4)
            ]
    else:
        groups = _as_list(spec.get("groups"))
        existing = len(groups)
        if len([item for item in groups if _filled(item)]) < targets["groups_min"]:
            patch["groups"] = [
                _placeholder_group(index)
                for index in range(1, targets["groups_min"] + 1)
            ]
        elif existing < targets["groups_min"]:
            append["groups"] = [
                _placeholder_group(index)
                for index in range(existing + 1, targets["groups_min"] + 1)
            ]
    if append:
        patch["append"] = append
    return patch


def _theme(spec: dict[str, Any]) -> dict[str, str]:
    theme_id = str(spec.get("theme_id") or spec.get("theme") or "business_blue")
    theme = dict(THEMES.get(theme_id, THEMES["business_blue"]))
    if isinstance(spec.get("visual_tokens"), dict):
        theme.update(
            {
                str(key): str(value)
                for key, value in spec["visual_tokens"].items()
                if value
            }
        )
    return theme


def _h(value: Any) -> str:
    return html.escape(str(value or ""), quote=True)


def _wrap(value: Any, limit: int) -> list[str]:
    text = str(value or "").strip()
    if not text:
        return []
    chunks: list[str] = []
    current = ""
    for char in text:
        current += char
        if len(current) >= limit:
            chunks.append(current)
            current = ""
    if current:
        chunks.append(current)
    return chunks[:4]


def _clip_text(value: Any, limit: int) -> str:
    text = str(value or "").strip()
    if len(text) <= limit:
        return text
    return text[: max(limit - 1, 0)] + "…"


def _compact_metric_value(value: Any) -> str:
    text = str(value or "待补").strip()
    match = re.fullmatch(r"([+-]?\d+(?:\.\d+)?)(%)", text)
    if match:
        return match.group(1) + match.group(2)
    return text


def _metric_value_parts(value: Any) -> tuple[str, str]:
    text = _compact_metric_value(value)
    match = re.fullmatch(r"([+-]?\d+(?:\.\d+)?)(%)", text)
    if match:
        return match.group(1), match.group(2)
    return text, ""


def _text(
    x: float,
    y: float,
    value: Any,
    size: int,
    fill: str,
    *,
    weight: int = 400,
    anchor: str = "start",
) -> str:
    return (
        f'<text x="{x:.1f}" y="{y:.1f}" fill="{fill}" font-family="{FONT}" '
        f'font-size="{size}" font-weight="{weight}" text-anchor="{anchor}">{_h(value)}</text>'
    )


def _multiline(
    x: float,
    y: float,
    value: Any,
    size: int,
    fill: str,
    *,
    width_chars: int = 28,
    line_gap: int | None = None,
    weight: int = 400,
) -> list[str]:
    parts: list[str] = []
    gap = line_gap or int(size * 1.5)
    for index, line in enumerate(_wrap(value, width_chars)):
        parts.append(_text(x, y + index * gap, line, size, fill, weight=weight))
    return parts


def _rect(
    x: float,
    y: float,
    w: float,
    h: float,
    fill: str,
    *,
    stroke: str = "none",
    rx: int = 10,
    opacity: float | None = None,
) -> str:
    opacity_attr = f' opacity="{opacity:.2f}"' if opacity is not None else ""
    return (
        f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" '
        f'rx="{rx}" fill="{fill}" stroke="{stroke}"{opacity_attr}/>'
    )


def _polygon(
    points: list[tuple[float, float]],
    fill: str,
    *,
    stroke: str = "none",
    opacity: float | None = None,
) -> str:
    points_attr = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    opacity_attr = f' opacity="{opacity:.2f}"' if opacity is not None else ""
    return f'<polygon points="{points_attr}" fill="{fill}" stroke="{stroke}"{opacity_attr}/>'


def _pyramid_layer_shapes(region: dict[str, float]) -> list[list[tuple[float, float]]]:
    x, y, w, h = region["x"], region["y"], region["w"], region["h"]
    layer_h = h / 3.0
    gap = min(max(h * 0.022, 6.0), 14.0)
    top_width = max(w * 0.38, min(w * 0.72, 180.0))
    middle_width = w * 0.70
    cx = x + w / 2.0
    top_y0 = y
    top_y1 = y + layer_h - gap
    middle_y0 = y + layer_h + gap
    middle_y1 = y + layer_h * 2.0 - gap
    base_y0 = y + layer_h * 2.0 + gap
    base_y1 = y + h
    return [
        [
            (cx, top_y0),
            (cx + top_width / 2.0, top_y1),
            (cx - top_width / 2.0, top_y1),
        ],
        [
            (cx - top_width / 2.0, middle_y0),
            (cx + top_width / 2.0, middle_y0),
            (cx + middle_width / 2.0, middle_y1),
            (cx - middle_width / 2.0, middle_y1),
        ],
        [
            (cx - middle_width / 2.0, base_y0),
            (cx + middle_width / 2.0, base_y0),
            (x + w, base_y1),
            (x, base_y1),
        ],
    ]


def _pyramid_label_points(region: dict[str, float]) -> list[tuple[float, float]]:
    x, y, w, h = region["x"], region["y"], region["w"], region["h"]
    layer_h = h / 3.0
    cx = x + w / 2.0
    return [
        (cx, y + layer_h * 0.64),
        (cx, y + layer_h * 1.52),
        (cx, y + layer_h * 2.50),
    ]


def _pyramid_text_capacity(region: dict[str, float]) -> dict[str, int]:
    return {
        "claim_chars": max(8, min(28, int(region["w"] / 34))),
        "claim_width": max(8, min(18, int(region["w"] / 58))),
        "proof_evidence_chars": max(18, min(38, int(region["w"] / 20))),
        "proof_action_chars": max(14, min(30, int(region["w"] / 25))),
    }


def _pyramid_proof_region(spec: dict[str, Any], pyramid_region: dict[str, float]) -> dict[str, Any]:
    raw = spec.get("pyramid_proof_region") or spec.get("proof_region")
    if isinstance(raw, dict):
        box = _normalize_box(raw, default={"x": 888, "y": 306, "w": 322, "h": 288})
        return {"placement": raw.get("placement") or "custom", **box}
    safe = _normalize_box(
        (spec.get("framework_layer") or {}).get("safe_area") if isinstance(spec.get("framework_layer"), dict) else None,
        default={"x": 58, "y": 38, "w": 1165, "h": 643},
    )
    gap = 24.0
    right_x = pyramid_region["x"] + pyramid_region["w"] + gap
    # 金字塔支持占用左侧自定义区域；右侧举证卡允许保留少量 bleed，
    # 以匹配 PPTX 宽屏边缘的视觉留白和历史契约测试。
    right_w = W - right_x + 26.0
    if right_w >= 300:
        return {
            "placement": "right",
            "x": right_x,
            "y": pyramid_region["y"],
            "w": min(402.0, right_w),
            "h": pyramid_region["h"],
        }
    bottom_y = pyramid_region["y"] + pyramid_region["h"] + gap
    bottom_h = safe["y"] + safe["h"] - bottom_y
    return {
        "placement": "bottom",
        "x": pyramid_region["x"],
        "y": bottom_y,
        "w": pyramid_region["w"],
        "h": max(min(bottom_h, 144.0), 96.0),
    }


def _header(parts: list[str], spec: dict[str, Any], theme: dict[str, str]) -> None:
    # 页眉、章节胶囊、背景和页面侧边框归 PPT 框架层；SVG builder 只输出正文内容标题块。
    parts.append('<g id="main-title-block">')
    parts.append(_text(70, 94, spec.get("title", "当前页标题"), 40, theme["title_text"], weight=700))
    parts.extend(_multiline(70, 133, spec.get("subtitle") or spec.get("key_message"), 18, theme["body_text"], width_chars=54, weight=500))
    parts.append("</g>")


def _metrics(parts: list[str], metrics: list[Any], theme: dict[str, str], *, y: int = 192) -> None:
    if not metrics:
        return
    card_w = 262 if len(metrics) <= 4 else 200
    gap = 18
    parts.append('<g id="metrics-panel">')
    for index, metric in enumerate(metrics[:5]):
        x = 70 + index * (card_w + gap)
        data = metric if isinstance(metric, dict) else {"label": str(metric)}
        parts.append(_rect(x, y, card_w, 90, theme["surface"], stroke=theme["border"], rx=12))
        parts.append(_text(x + 18, y + 27, data.get("label", "指标"), 15, theme["muted_text"], weight=600))
        value, suffix = _metric_value_parts(data.get("value", "待补"))
        value_size = 29 if len(value) <= 4 else 24
        parts.append(_text(x + 18, y + 62, value, value_size, theme["accent"], weight=800))
        if suffix:
            suffix_x = x + 24 + max(len(value), 1) * value_size * 0.58
            parts.append(_text(suffix_x, y + 62, suffix, 18, theme["accent"], weight=800))
        parts.append('<g id="kicker-metric-note">')
        parts.extend(
            _multiline(
                x + 131,
                y + 43,
                _clip_text(data.get("note", ""), 16),
                11,
                theme["body_text"],
                width_chars=9,
                line_gap=16,
            )
        )
        parts.append("</g>")
    parts.append("</g>")


def _source_note(parts: list[str], spec: dict[str, Any], theme: dict[str, str]) -> None:
    sources = " / ".join(str(item) for item in _as_list(spec.get("sources"))[:4])
    source_note = spec.get("source_note") or spec.get("footer") or sources or "来源：请替换为当前页材料、口径或责任方"
    parts.append('<g id="source-note">')
    parts.append(_rect(70, 658, 1139, 27, theme["surface"], stroke=theme["border"], rx=8, opacity=0.82))
    parts.append(_text(86, 675, source_note, 11, theme["source_text"], weight=500))
    parts.append("</g>")


def _gold_cards(parts: list[str], spec: dict[str, Any], theme: dict[str, str]) -> None:
    groups = _as_list(spec.get("groups") or spec.get("cards"))[:4]
    if not groups:
        groups = [
            {"title": "核心判断", "claim": spec.get("key_message", "补充本页判断"), "evidence": ["补充证据一", "补充证据二"], "action": "补充行动或风险"},
            {"title": "证据链", "claim": "用事实证明判断", "evidence": ["补充数据来源", "补充案例来源"], "action": "标注证据缺口"},
            {"title": "行动闭环", "claim": "把结论落到责任", "evidence": ["责任人", "时间点"], "action": "补齐验收标准"},
        ]
    cols = 2 if len(groups) <= 4 else 3
    card_w = 552 if cols == 2 else 360
    card_h = 152
    parts.append('<g id="main-content">')
    for index, raw in enumerate(groups):
        group = raw if isinstance(raw, dict) else {"title": str(raw)}
        col = index % cols
        row = index // cols
        x = 70 + col * (card_w + 35)
        y = 306 + row * (card_h + 22)
        parts.append(f'<g id="content-group-{index + 1}">')
        # 汇报类卡片禁装饰性左缘色条（contract-svg-self-qa），层级靠标题字重与留白表达。
        parts.append(_rect(x, y, card_w, card_h, theme["surface"], stroke=theme["border"], rx=12))
        parts.append(_text(x + 19, y + 27, group.get("title", f"模块 {index + 1}"), 19, theme["title_text"], weight=700))
        parts.extend(_multiline(x + 19, y + 53, group.get("claim", ""), 16, theme["body_text"], width_chars=30, weight=600))
        for b_index, bullet in enumerate(_as_list(group.get("evidence"))[:3]):
            parts.append(_text(x + 24, y + 92 + b_index * 20, f"• {bullet}", 15, theme["body_text"], weight=500))
        parts.append(_text(x + card_w - 19, y + card_h - 14, group.get("action", group.get("tag", "行动待补")), 15, theme["accent"], weight=700, anchor="end"))
        parts.append("</g>")
    parts.append("</g>")


def _comparison_footer(spec: dict[str, Any]) -> tuple[str, str]:
    boundary = spec.get("boundary") or spec.get("evidence_boundary") or spec.get("limitation") or ""
    frame = spec.get("plain_language_who_scene_problem_action")
    action = spec.get("action") or (frame.get("action") if isinstance(frame, dict) else "") or ""
    return str(boundary), str(action)


def _comparison_missing(spec: dict[str, Any]) -> list[str]:
    missing: list[str] = []
    groups = _as_list(spec.get("groups"))
    if len(groups) != 2:
        missing.append("comparison_requires_two_groups")
    if spec.get("metrics"):
        missing.append("comparison_put_evidence_in_panels")
    if any(spec.get(key) for key in ("native_chart_slots", "native_table_slots", "evidence_asset_slots")):
        missing.append("comparison_text_layout_has_no_native_slots")
    for index, group in enumerate(groups):
        if not isinstance(group, dict):
            continue
        for field, limit in (("title", 20), ("claim", 44), ("action", 44)):
            value = group.get(field)
            if not _filled(value):
                missing.append(f"groups[{index}].{field}")
            elif len(str(value)) > limit:
                missing.append(f"groups[{index}].{field}.comparison_capacity")
        evidence = _as_list(group.get("evidence"))
        evidence_lines = [(len(str(item)) + 20) // 21 for item in evidence]
        if len(evidence) > 3 or any(lines > 4 for lines in evidence_lines) or sum(evidence_lines) > 6:
            missing.append(f"groups[{index}].evidence.comparison_capacity")
    boundary, action = _comparison_footer(spec)
    for field, value in (("boundary", boundary), ("action", action)):
        if not _filled(value):
            missing.append(f"comparison_{field}")
        elif len(value) > 56:
            missing.append(f"comparison_{field}_capacity")
    if len(str(spec.get("title") or "")) > 70 or len(str(spec.get("key_message") or "")) > 108:
        missing.append("comparison_header_capacity")
    if len(groups) == 2 and all(isinstance(group, dict) for group in groups):
        if _comparison_geometry(spec)["footer_top"] + 72 > 646:
            missing.append("comparison_page_capacity")
    return missing


def _comparison_geometry(spec: dict[str, Any]) -> dict[str, int]:
    groups = spec["groups"]
    title_lines = max(1, (len(str(spec.get("title") or "")) + 34) // 35)
    subtitle_lines = max(1, (len(str(spec.get("key_message") or "")) + 53) // 54)
    panel_top = max(190, 94 + title_lines * 38 + (subtitle_lines - 1) * 23 + 36)
    claim_lines = max(max(1, (len(str(group.get("claim") or "")) + 21) // 22) for group in groups)
    evidence_lines = max(sum(max(1, (len(str(item)) + 20) // 21) for item in _as_list(group.get("evidence"))) for group in groups)
    action_lines = max(max(1, (len(str(group.get("action") or "")) + 21) // 22) for group in groups)
    claim_y = panel_top + 76
    evidence_y = claim_y + (claim_lines - 1) * 28 + 32
    action_y = evidence_y + max(evidence_lines - 1, 0) * 26 + 34
    panel_bottom = action_y + (action_lines - 1) * 28 + 26
    extra_spacing = max(0, 270 - (panel_bottom - panel_top))
    evidence_y += extra_spacing // 2
    action_y += extra_spacing
    panel_bottom += extra_spacing
    return {"panel_top": panel_top, "claim_y": claim_y, "evidence_y": evidence_y,
            "action_y": action_y, "panel_bottom": panel_bottom, "footer_top": max(574, panel_bottom + 18)}


def _gold_comparison(parts: list[str], spec: dict[str, Any], theme: dict[str, str]) -> None:
    geometry = _comparison_geometry(spec)
    title = str(spec.get("title") or "")
    parts.append('<g id="main-title-block">')
    parts.extend(_multiline(70, 84, title, 32, theme["title_text"], width_chars=35, line_gap=38, weight=700))
    subtitle_y = 94 + len(_wrap(title, 35)) * 38
    parts.extend(_multiline(70, subtitle_y, spec.get("key_message"), 18, theme["body_text"], width_chars=54, line_gap=23))
    parts.append("</g>")
    for index, group in enumerate(spec["groups"]):
        panel_x = 70 + index * 587
        parts.append(f'<g id="comparison-panel-{index + 1}" data-role="comparison-panel">')
        parts.append(_rect(panel_x, geometry["panel_top"], 552, geometry["panel_bottom"] - geometry["panel_top"], theme["surface"], stroke=theme["border"], rx=12))
        parts.append(_text(panel_x + 24, geometry["panel_top"] + 36, group["title"], 24, theme["title_text"], weight=700))
        parts.extend(_multiline(panel_x + 24, geometry["claim_y"], group["claim"], 22, theme["body_text"], width_chars=22, line_gap=28, weight=600))
        evidence_y = geometry["evidence_y"]
        for evidence in _as_list(group.get("evidence")):
            lines = _wrap(evidence, 21)
            for line_index, line in enumerate(lines):
                parts.append(_text(panel_x + 24, evidence_y, ("• " if line_index == 0 else "  ") + line, 22, theme["body_text"]))
                evidence_y += 26
        parts.extend(_multiline(panel_x + 24, geometry["action_y"], group["action"], 22, theme["accent"], width_chars=22, line_gap=28, weight=600))
        parts.append("</g>")
    boundary, action = _comparison_footer(spec)
    parts.append('<g id="comparison-boundary-action">')
    parts.append(_rect(70, geometry["footer_top"], 1139, 72, theme["surface"], stroke=theme["border"], rx=8))
    if boundary:
        parts.append(_text(86, geometry["footer_top"] + 27, f"限制：{boundary}", 18, theme["body_text"]))
    if action:
        parts.append(_text(86, geometry["footer_top"] + 57, f"下一步：{action}", 18, theme["accent"], weight=600))
    parts.append("</g>")


def _json_number(value: Any) -> int | float:
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value) if value.is_integer() else value
    text = str(value or "").strip().replace("%", "").replace(",", "")
    if not text:
        return 0
    parsed = float(text)
    return int(parsed) if parsed.is_integer() else parsed


def _chart_kind(raw: Any) -> str | None:
    kind = str(raw or "bar").strip().lower()
    aliases = {
        "column": "bar",
        "bar-clustered": "bar",
        "timeseries": "line",
        "trend": "trend",
        "combo": "bar",
    }
    kind = aliases.get(kind, kind)
    if kind in {"sankey", "bubble"}:
        return None
    if kind not in {"bar", "line", "pie", "trend", "waterfall", "radar"}:
        return "bar"
    return kind


def _native_data_ref(svg_path: Path, native_path: Path) -> str:
    try:
        if native_path.parent.resolve() == svg_path.parent.resolve():
            return native_path.name
        return native_path.resolve().relative_to(svg_path.parent.resolve()).as_posix()
    except ValueError:
        return native_path.name


def _is_remote_image_ref(value: Any) -> bool:
    text = str(value or "").strip().lower()
    return text.startswith(("http://", "https://", "/v1/files"))


def _local_image_asset_key(slot: dict[str, Any]) -> str | None:
    for key in ("asset_key", "key", "path"):
        value = slot.get(key)
        if isinstance(value, str) and value.strip() and not _is_remote_image_ref(value):
            return value.strip()
    url = slot.get("url")
    if isinstance(url, str) and url.strip() and not _is_remote_image_ref(url) and not url.strip().startswith("/"):
        return url.strip()
    return None


def _slot_caption(
    parts: list[str],
    x: float,
    y: float,
    w: float,
    h: float,
    slot: dict[str, Any],
    theme: dict[str, str],
) -> None:
    title = str(slot.get("title") or "")
    insight = str(slot.get("insight") or slot.get("caption") or "")
    source = str(slot.get("source") or "")
    if title:
        parts.append(_text(x, max(y - 16.0, 58.0), title, 16, theme["title_text"], weight=700))
    note_y = min(y + h + 22.0, 700.0)
    if insight:
        parts.append(_text(x, note_y, insight, 15, theme["body_text"], weight=500))
        note_y = min(note_y + 18.0, 716.0)
    if source:
        parts.append('<g id="source-note-slot">')
        parts.append(_text(x, note_y, source, 11, theme["source_text"], weight=500))
        parts.append("</g>")


def build_native_data(spec: dict[str, Any]) -> dict[str, Any]:
    """Emit renderer native-data JSON; chart values stay out of SVG attributes."""

    normalized = normalize_page_spec(spec)
    theme = _theme(normalized)
    charts: list[dict[str, Any]] = []
    for slot in _as_list(normalized.get("native_chart_slots")):
        if not isinstance(slot, dict):
            continue
        kind = _chart_kind(slot.get("chart_type") or slot.get("kind") or slot.get("type"))
        if kind is None:
            continue
        rows = [row for row in _as_list(slot.get("data")) if isinstance(row, dict)]
        labels = [str(row.get("label") or "") for row in rows]
        values: list[int | float] = []
        for row in rows:
            try:
                values.append(_json_number(row.get("value")))
            except (TypeError, ValueError):
                values.append(0)
        color = theme["accent"]
        charts.append(
            {
                "slot_id": str(slot.get("id") or f"chart-slot-{len(charts) + 1}"),
                "kind": kind,
                "title": str(slot.get("title") or ""),
                "labels": labels,
                "series": [
                    {
                        "name": str(slot.get("title") or "系列"),
                        "values": values,
                        "color": color,
                    }
                ],
                "colors": [color],
                "source": str(slot.get("source") or ""),
                "insight": str(slot.get("insight") or ""),
                "style": {
                    "title_text_color": theme["title_text"],
                    "axis_text_color": theme["body_text"],
                    "legend_text_color": theme["body_text"],
                    "grid_color": theme["border"],
                },
                "options": {"legend": False, "show_title": False},
            }
        )
    tables: list[dict[str, Any]] = []
    for slot in _as_list(normalized.get("native_table_slots")):
        if not isinstance(slot, dict):
            continue
        columns = [str(column) for column in _as_list(slot.get("columns"))]
        rows: list[list[str]] = []
        for row in _as_list(slot.get("rows")):
            if isinstance(row, dict) and isinstance(row.get("cells"), list):
                rows.append([str(cell) for cell in row["cells"]])
            elif isinstance(row, dict):
                rows.append([str(row.get(column, "")) for column in columns])
            elif isinstance(row, (list, tuple)):
                rows.append([str(cell) for cell in row])
        tables.append(
            {
                "slot_id": str(slot.get("id") or f"table-slot-{len(tables) + 1}"),
                "columns": columns,
                "rows": rows,
                "style": {
                    "font_face": str(normalized["typography"].get("font_family") or FONT).split(",")[0].strip().strip("'\""),
                    "font_size": float(normalized["typography"]["body_px"]) * 0.75,
                    **(slot.get("style") if isinstance(slot.get("style"), dict) else {}),
                },
            }
        )
    images: list[dict[str, Any]] = []
    for index, slot in enumerate(_as_list(normalized.get("evidence_asset_slots")), start=1):
        if not isinstance(slot, dict):
            continue
        asset_key = _local_image_asset_key(slot)
        if asset_key is None:
            continue
        payload: dict[str, Any] = {
            "slot_id": str(slot.get("id") or f"screenshot-proof-{index}"),
            "asset_key": asset_key,
        }
        if slot.get("caption"):
            payload["caption"] = slot.get("caption")
        if slot.get("fit") in {"cover", "contain"}:
            payload["fit"] = slot.get("fit")
        images.append(payload)
    return {"version": 1, "charts": charts, "tables": tables, "images": images}


def _native_table_slots(parts: list[str], spec: dict[str, Any], theme: dict[str, str]) -> None:
    slots = _as_list(spec.get("native_table_slots"))
    if not slots:
        return
    parts.append('<g id="native-table-slots">')
    for index, slot in enumerate(slots, start=1):
        if not isinstance(slot, dict):
            continue
        visual = _bounded_visual_box(
            _slot_box(slot, default={"x": 70.0, "y": 288.0, "w": 1139.0, "h": 336.0}),
            min_w=240.0,
            min_h=160.0,
        )
        x, y, w, h = visual["x"], visual["y"], visual["w"], visual["h"]
        slot_id = _h(slot.get("id") or f"table-slot-{index}")
        n_cols = max(len(_as_list(slot.get("columns"))), 1)
        n_rows = max(len(_as_list(slot.get("rows"))), 1)
        _slot_caption(
            parts,
            x,
            y,
            w,
            h,
            {
                "title": slot.get("title") or spec.get("table_title") or "原生表格",
                "source": slot.get("source") or "来源口径待补",
            },
            theme,
        )
        parts.append(
            f'<g id="{slot_id}" data-role="native-table-slot" data-native-table="true" '
            f'data-x="{x:.1f}" data-y="{y:.1f}" data-w="{w:.1f}" data-h="{h:.1f}" '
            f'data-columns="{n_cols}" data-rows="{n_rows}">'
        )
        parts.append(_rect(x, y, w, h, "none", stroke=theme["border"], rx=14))
        parts.append("</g>")
    parts.append("</g>")


def _gold_table(parts: list[str], spec: dict[str, Any], theme: dict[str, str]) -> None:
    if _as_list(spec.get("native_table_slots")) and not spec.get("table_fallback_reason"):
        _native_table_slots(parts, spec, theme)
        return
    rows = _as_list(spec.get("rows"))[:7]
    columns = _as_list(spec.get("columns")) or ["事项", "证据/口径", "影响", "Owner", "状态"]
    if not rows:
        rows = [
            {"cells": ["关键判断", "补充证据来源", "说明影响", "责任人", "待补齐"]},
            {"cells": ["执行动作", "补充检查标准", "说明节奏", "责任人", "跟进中"]},
            {"cells": ["风险缺口", "补充风险来源", "说明预案", "责任人", "需升级"]},
        ]
    x, y, base_w, row_h = 70, 288, 1139, 38
    w = base_w
    slot_min_x = _right_side_slot_min_x(spec)
    if slot_min_x is not None:
        # 右侧有截图/图表 sidecar 时，主表格主动让出空间，避免
        # builder 生成的文字与素材占位框重叠后被 input gate 阻断。
        w = max(560.0, min(base_w, slot_min_x - 22.0 - x))
    col_w = w / max(len(columns), 1)
    cell_width_chars = max(6, min(13, int((col_w - 24.0) / 11.5)))
    parts.append('<g id="evidence-action-table">')
    parts.append(_rect(x, y - 43, w, 43, theme["accent"], rx=12))
    parts.append(_text(x + 19, y - 16, spec.get("table_title", "证据-行动闭环表"), 21, "#FFFFFF", weight=700))
    for index, col in enumerate(columns):
        parts.append(_text(x + index * col_w + 14, y + 24, _clip_text(col, cell_width_chars + 2), 15, theme["muted_text"], weight=700))
    for row_index, row in enumerate(rows):
        row_y = y + 38 + row_index * row_h
        fill = theme["surface"] if row_index % 2 == 0 else theme["background"]
        parts.append(_rect(x, row_y, w, row_h, fill, stroke=theme["border"], rx=0))
        cells = row.get("cells") if isinstance(row, dict) else row
        if isinstance(cells, dict):
            cells = [cells.get(str(col), "") for col in columns]
        for col_index, cell in enumerate(_as_list(cells)[: len(columns)]):
            parts.extend(
                _multiline(
                    x + col_index * col_w + 14,
                    row_y + 23,
                    cell,
                    15,
                    theme["body_text"],
                    width_chars=cell_width_chars,
                    line_gap=18,
                )
            )
    parts.append("</g>")


def _gold_timeline(parts: list[str], spec: dict[str, Any], theme: dict[str, str]) -> None:
    steps = _as_list(spec.get("steps") or spec.get("rows") or spec.get("groups"))[:6]
    if not steps:
        steps = [{"title": "阶段一", "claim": "补充阶段目标", "action": "补充验收标准"}]
    parts.append('<g id="timeline-roadmap">')
    parts.append(f'<line x1="120" y1="402" x2="1160" y2="402" stroke="{theme["border"]}" stroke-width="4"/>')
    gap = 1040 / max(len(steps) - 1, 1)
    for index, raw in enumerate(steps):
        step = raw if isinstance(raw, dict) else {"title": str(raw)}
        x = 120 + index * gap
        parts.append(f'<circle cx="{x:.1f}" cy="402" r="12" fill="{theme["accent"]}"/>')
        parts.append(_rect(x - 84, 443, 168, 115, theme["surface"], stroke=theme["border"], rx=12))
        parts.append(_text(x - 67, 469, step.get("title", f"阶段 {index + 1}"), 16, theme["title_text"], weight=700))
        parts.extend(_multiline(x - 67, 496, step.get("claim", step.get("body", "")), 15, theme["body_text"], width_chars=12))
        parts.append(_text(x + 67, 541, step.get("action", step.get("tag", "验收")), 15, theme["accent"], weight=700, anchor="end"))
    parts.append("</g>")


def _gold_pyramid(parts: list[str], spec: dict[str, Any], theme: dict[str, str]) -> None:
    layers = _as_list(spec.get("pyramid_layers") or spec.get("groups"))[:3]
    while len(layers) < 3:
        layers.append(_placeholder_pyramid_layer(len(layers) + 1))
    normalized_layers = [
        layer if isinstance(layer, dict) else {"title": str(layer)}
        for layer in layers[:3]
    ]
    fills = [
        theme["accent"],
        theme.get("accent2", theme["accent"]),
        "#DBEAFE" if theme.get("background", "").upper() != "#07111F" else "#123B5D",
    ]
    text_fills = ["#FFFFFF", theme["title_text"], theme["body_text"]]
    region = _normalize_box(
        spec.get("pyramid_region"),
        default={"x": 136, "y": 264, "w": 768, "h": 336},
    )
    shapes = _pyramid_layer_shapes(region)
    label_points = _pyramid_label_points(region)
    capacity = _pyramid_text_capacity(region)
    parts.append(
        f'<g id="pyramid-stack" data-region-x="{region["x"]:.1f}" '
        f'data-region-y="{region["y"]:.1f}" data-region-w="{region["w"]:.1f}" '
        f'data-region-h="{region["h"]:.1f}">'
    )
    for index, layer in enumerate(normalized_layers):
        parts.append(f'<g id="pyramid-layer-{index + 1}">')
        parts.append(_polygon(shapes[index], fills[index], stroke=theme["border"]))
        x, y = label_points[index]
        title = layer.get("title") or f"层级 {index + 1}"
        claim = layer.get("claim") or layer.get("body") or ""
        parts.append(_text(x, y - 18, title, 20, text_fills[index], weight=800, anchor="middle"))
        parts.extend(
            _multiline(
                x - 120,
                y + 18,
                _clip_text(claim, capacity["claim_chars"]),
                16,
                text_fills[index],
                width_chars=capacity["claim_width"],
                line_gap=20,
                weight=600,
            )
        )
        parts.append("</g>")
    parts.append("</g>")

    proof = _pyramid_proof_region(spec, region)
    px, py, pw, ph = proof["x"], proof["y"], proof["w"], proof["h"]
    placement = _h(proof["placement"])
    parts.append(f'<g id="hierarchy-proof" data-placement="{placement}">')
    parts.append(_rect(px, py, pw, ph, theme["surface"], stroke=theme["border"], rx=14))
    parts.append(_text(px + 24, py + 42, spec.get("proof_title", "层级举证"), 19, theme["title_text"], weight=800))
    item_gap = max(min((ph - 74) / 3.0, 96.0), 58.0)
    for index, layer in enumerate(normalized_layers):
        y = py + 86 + index * item_gap
        title = str(layer.get("title") or f"层级 {index + 1}")
        evidence = " / ".join(str(item) for item in _as_list(layer.get("evidence"))[:2])
        action = layer.get("action") or layer.get("implication") or layer.get("risk") or layer.get("claim") or ""
        proof_width_chars = max(14, min(30, int(pw / 16)))
        parts.append(_text(px + 24, y, f"{index + 1}. {title}", 16, theme["accent"], weight=800))
        parts.extend(
            _multiline(
                px + 52,
                y + 26,
                _clip_text(evidence, capacity["proof_evidence_chars"]),
                15,
                theme["body_text"],
                width_chars=proof_width_chars,
                line_gap=18,
                weight=500,
            )
        )
        parts.extend(
            _multiline(
                px + 52,
                y + 56,
                _clip_text(action, capacity["proof_action_chars"]),
                15,
                theme["muted_text"],
                width_chars=max(12, proof_width_chars - 2),
                line_gap=18,
                weight=500,
            )
        )
    parts.append("</g>")


def _native_chart_slots(parts: list[str], spec: dict[str, Any], theme: dict[str, str]) -> None:
    slots = _as_list(spec.get("native_chart_slots"))
    if not slots:
        return
    parts.append('<g id="native-chart-slots">')
    for index, slot in enumerate(slots, start=1):
        if not isinstance(slot, dict):
            continue
        raw = _slot_box(slot, default={"x": 736.0, "y": 312.0, "w": 344.0, "h": 208.0})
        visual = _bounded_visual_box(raw, min_w=150.0, min_h=128.0)
        for evidence_slot in _as_list(spec.get("evidence_asset_slots")):
            evidence = _bounded_visual_box(
                _slot_box(
                    evidence_slot,
                    default={"x": 544.0, "y": 196.0, "w": 656.0, "h": 384.0},
                ),
                min_w=150.0,
                min_h=120.0,
            )
            if _boxes_overlap(visual, evidence):
                visual["y"] = min(evidence["y"] + evidence["h"] + 16.0, 640.0 - 128.0)
                visual["h"] = min(visual["h"], 640.0 - visual["y"])
        x, y, w, h = visual["x"], visual["y"], visual["w"], visual["h"]
        slot_id = _h(slot.get("id") or f"chart-slot-{index}")
        chart_type = _h(slot.get("chart_type") or "bar")
        _slot_caption(parts, x, y, w, h, slot, theme)
        parts.append(
            f'<g id="{slot_id}" data-role="native-chart-slot" data-native-chart="true" '
            f'data-chart-type="{chart_type}" '
            f'data-x="{x:.1f}" data-y="{y:.1f}" data-w="{w:.1f}" data-h="{h:.1f}">'
        )
        parts.append(_rect(x, y, w, h, "none", stroke=theme["border"], rx=14))
        parts.append("</g>")
    parts.append("</g>")


def _evidence_asset_slots(parts: list[str], spec: dict[str, Any], theme: dict[str, str]) -> None:
    slots = [
        slot
        for slot in _as_list(spec.get("evidence_asset_slots"))
        if isinstance(slot, dict) and _local_image_asset_key(slot)
    ]
    if not slots:
        return
    parts.append('<g id="native-image-slots">')
    for index, slot in enumerate(slots, start=1):
        visual = _bounded_visual_box(
            _slot_box(slot, default={"x": 544.0, "y": 196.0, "w": 656.0, "h": 384.0}),
            min_w=150.0,
            min_h=120.0,
        )
        x, y, w, h = visual["x"], visual["y"], visual["w"], visual["h"]
        slot_id = _h(slot.get("id") or f"screenshot-proof-{index}")
        _slot_caption(parts, x, y, w, h, slot, theme)
        parts.append(
            f'<g id="{slot_id}" data-role="native-image-slot" data-native-image="true" '
            f'data-x="{x:.1f}" data-y="{y:.1f}" data-w="{w:.1f}" data-h="{h:.1f}">'
        )
        parts.append(_rect(x, y, w, h, "none", stroke=theme["border"], rx=14))
        parts.append("</g>")
    parts.append("</g>")


def build_svg_page(spec: dict[str, Any], native_data_ref: str | None = None) -> str:
    spec = normalize_page_spec(spec)
    theme = _theme(spec)
    layout = str(spec.get("layout") or "gold_cards")
    root_attrs = [
        'xmlns="http://www.w3.org/2000/svg"',
        f'viewBox="0 0 {W} {H}"',
        f'width="{W}"',
        f'height="{H}"',
    ]
    ref = str(native_data_ref or "").strip()
    if ref:
        root_attrs.append(f'data-native-data-ref="{_h(ref)}"')
    parts = [f"<svg {' '.join(root_attrs)}>"]
    if layout == "gold_comparison":
        missing = _comparison_missing(spec)
        if missing:
            raise ValueError("comparison layout needs repair: " + ", ".join(missing))
        _gold_comparison(parts, spec, theme)
    else:
        _header(parts, spec, theme)
        _metrics(parts, _as_list(spec.get("metrics"))[:5], theme)
        parts.append(_rect(70, 298, 1139, 336, theme["surface"], stroke=theme["border"], rx=16, opacity=0.36))
    if layout == "gold_comparison":
        pass
    elif layout in {"gold_evidence_table", "gold_issue_log", "gold_action_ledger", "table"}:
        _gold_table(parts, spec, theme)
    elif layout in {"gold_timeline", "timeline"}:
        _gold_timeline(parts, spec, theme)
    elif layout == "pyramid_hierarchy":
        _gold_pyramid(parts, spec, theme)
    else:
        _gold_cards(parts, spec, theme)
    _native_chart_slots(parts, spec, theme)
    _evidence_asset_slots(parts, spec, theme)
    _source_note(parts, spec, theme)
    parts.append("</svg>")
    svg = "\n  ".join(parts) + "\n"
    font_family = spec["typography"].get("font_family")
    if font_family:
        svg = svg.replace(f'font-family="{FONT}"', f'font-family="{_h(font_family)}"')
    return svg


def _load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return data


def main() -> None:
    parser = argparse.ArgumentParser(description="Build one gold-style SVG slide from JSON.")
    parser.add_argument("--spec", type=Path, help="Base page spec JSON.")
    parser.add_argument("--patch", type=Path, help="Optional patch JSON for supplement/repair.")
    parser.add_argument("--output", type=Path, help="Output SVG path.")
    parser.add_argument(
        "--native-output",
        type=Path,
        help="Sibling native-data JSON path. Defaults to native-data.json next to --output.",
    )
    parser.add_argument("--validate-only", action="store_true", help="Validate and report without writing SVG.")
    parser.add_argument("--write-normalized", type=Path, help="Write normalized page_spec JSON.")
    parser.add_argument("--write-repair-patch", type=Path, help="Write suggested repair patch JSON.")
    parser.add_argument("--write-template", type=Path, help="Write a fillable gold page_spec template JSON.")
    parser.add_argument("--write-fill-plan", type=Path, help="Write step-by-step fill plan JSON.")
    parser.add_argument("--layout", default="gold_cards", help="Template layout when using --write-template.")
    parser.add_argument("--theme-id", default="business_blue", help="Template theme_id when using --write-template.")
    parser.add_argument("--page-role", default="content", help="Template page_role when using --write-template.")
    args = parser.parse_args()

    if args.write_template:
        template = build_page_spec_template(
            layout=args.layout,
            theme_id=args.theme_id,
            page_role=args.page_role,
        )
        args.write_template.parent.mkdir(parents=True, exist_ok=True)
        args.write_template.write_text(
            json.dumps(template, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        fill_plan = build_fill_plan(template)
        if args.write_fill_plan:
            args.write_fill_plan.parent.mkdir(parents=True, exist_ok=True)
            args.write_fill_plan.write_text(
                json.dumps(fill_plan, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        if args.spec is None:
            print(
                json.dumps(
                    {
                        "ok": False,
                        "template": str(args.write_template),
                        "quality": quality_report(template),
                        "fill_plan": fill_plan,
                    },
                    ensure_ascii=False,
                )
            )
            return

    if args.spec is None:
        parser.error("--spec is required unless --write-template is used alone")
    spec = _load_json(args.spec)
    if args.patch:
        spec = _deep_merge(spec, _load_json(args.patch))
    normalized = normalize_page_spec(spec)
    report = quality_report(normalized)
    repair_patch = build_repair_patch(normalized)

    if args.write_normalized:
        args.write_normalized.parent.mkdir(parents=True, exist_ok=True)
        args.write_normalized.write_text(
            json.dumps(normalized, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    if args.write_repair_patch:
        args.write_repair_patch.parent.mkdir(parents=True, exist_ok=True)
        args.write_repair_patch.write_text(
            json.dumps(repair_patch, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    if args.write_fill_plan:
        args.write_fill_plan.parent.mkdir(parents=True, exist_ok=True)
        args.write_fill_plan.write_text(
            json.dumps(build_fill_plan(normalized), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    output = None
    byte_count = 0
    native_output = None
    if not args.validate_only:
        if args.output is None:
            parser.error("--output is required unless --validate-only is set")
        if report["quality_status"] != "ready":
            parser.error(
                "quality_status=needs_repair; fill page_spec/patch and rerun validate-only before writing SVG"
            )
        native_data = build_native_data(normalized)
        native_path = args.native_output or args.output.with_name("native-data.json")
        has_native = any(native_data.get(key) for key in ("charts", "tables", "images", "sankeys"))
        native_ref = _native_data_ref(args.output, native_path) if has_native else None
        svg = build_svg_page(normalized, native_data_ref=native_ref)
        if normalized["layout"] == "gold_comparison":
            missing_shape = check_shape_picture("左右对照", svg)
            if missing_shape:
                parser.error("comparison shape check failed: " + ", ".join(missing_shape))
        svg_gate = run_svg_gates(svg, normalized)
        if svg_gate.missing:
            report["quality_status"] = "needs_repair"
            for code in svg_gate.missing:
                if code not in report["missing"]:
                    report["missing"].append(code)
            report["svg_gates"] = svg_gate.details
            parser.error(
                "svg visual gate failed: " + ", ".join(svg_gate.missing)
            )
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(svg, encoding="utf-8")
        output = str(args.output)
        byte_count = len(svg.encode("utf-8"))
        if has_native:
            native_path.parent.mkdir(parents=True, exist_ok=True)
            native_path.write_text(
                json.dumps(native_data, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            native_output = str(native_path)

    print(
        json.dumps(
            {
                "ok": report["quality_status"] == "ready",
                "output": output,
                "native_output": native_output,
                "bytes": byte_count,
                "quality": report,
                "repair_patch": repair_patch,
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
