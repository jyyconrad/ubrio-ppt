"""Page-spec evidence/claim gate (session-884 C-01/C-02/C-03/C-06/C-13/C-14/V-04/V-06)."""

from __future__ import annotations

import re
from typing import Any

from . import COVER_ROLES, GateResult

METRIC_REQUIRED_FIELDS = (
    "evidence_type",
    "claim_type",
    "population",
    "period",
    "denominator",
    "source_ref",
    "limitation",
    "on_metric_label",
)

EVIDENCE_ALIASES = {
    "实验": "experiment",
    "调查": "survey",
    "相关": "correlation",
    "相关关系": "correlation",
    "内部基线": "internal_baseline",
    "政策": "policy",
    "结构计数": "structure_count",
    "品类": "category",
    "品类存在": "category",
    "常识": "common_sense",
}

OUTCOME_EVIDENCE_TYPES = frozenset(
    {
        "experiment",
        "survey",
        "correlation",
        "internal_baseline",
        "policy",
        "category",
    }
)
WEAK_CAUSAL_EVIDENCE_TYPES = frozenset({"survey", "correlation", "category", "common_sense", "structure_count"})
STRONG_EVIDENCE_TYPES = frozenset({"experiment", "internal_baseline"})
CAUSAL_VERBS = ("导致", "反噬", "必达", "必须", "已升级")
STRONG_CLAIM_MARKERS = ("已升级", "必达", "必须进入", "必须达到", "必须到达")
GRAPH_CHART_TYPES = frozenset({"line", "bar", "network", "linechart", "barchart", "scatter", "area"})
COMMON_SENSE_RE = re.compile(r"^.{0,12}常识$")
CURRENT_KPI_RE = re.compile(r"(现状|当前).{0,8}(KPI|指标|基线)|current\s*KPI", re.I)
MATH_MARKERS = ("n(n-1)/2", "n(n-1)", "全连接")
ORG_MARKERS = ("团队", "组织", "端到端")
HEDGE_MARKERS = ("示意", "假设", "待验证", "待内部验证", "假设链")
MECHANISM_LABELS = ("假设链", "待内部验证", "示意")
PLACEHOLDER_PREFIXES = ("待补",)


def check(spec: dict) -> GateResult:
    spec = spec if isinstance(spec, dict) else {}
    role = str(spec.get("page_role") or spec.get("page_archetype") or "").strip().lower()
    cover = role in COVER_ROLES
    issues: list[str] = []

    metrics = _dicts(spec.get("metrics"))
    cards = _dicts(spec.get("evidence_cards"))
    claims = _dicts(spec.get("claims"))
    charts = _collect_charts(spec)
    text = _page_text(spec)

    _check_metric_fields(metrics, issues)
    _check_card_fields(cards, issues)
    _check_claim_fields(claims, issues)
    _check_kpi_strip(metrics, issues)
    _check_causal_verbs(text, metrics, cards, issues)
    _check_common_sense(spec, metrics, cards, issues)
    _check_current_kpi(metrics, issues)
    _check_strong_claim(spec, text, metrics, cards, claims, issues)
    _check_math_illustration(text, issues)
    _check_charts(charts, issues)

    details = {
        "page_role": role,
        "cover_role": cover,
        "evidence_types": [_evidence_type(item) for item in metrics if _evidence_type(item)],
        "causal_verbs": [verb for verb in CAUSAL_VERBS if verb in text],
        "chart_kinds": [str(chart.get("chart_kind") or "") for _, _, chart in charts],
    }
    if cover:
        return GateResult(missing=[], warnings=issues, details=details)
    return GateResult(missing=issues, warnings=[], details=details)


def _check_metric_fields(metrics: list[dict[str, Any]], issues: list[str]) -> None:
    for index, metric in enumerate(metrics):
        for field in METRIC_REQUIRED_FIELDS:
            if field == "period" and _filled(metric.get("period") or metric.get("year")):
                continue
            if field == "source_ref" and _source_ref(metric):
                continue
            if _filled(metric.get(field)):
                continue
            _add(issues, f"metrics[{index}].{field}")


def _check_card_fields(cards: list[dict[str, Any]], issues: list[str]) -> None:
    for index, card in enumerate(cards):
        for field in METRIC_REQUIRED_FIELDS:
            if field == "on_metric_label":
                continue
            if field == "period" and _filled(card.get("period") or card.get("year")):
                continue
            if field == "source_ref" and _source_ref(card):
                continue
            if _filled(card.get(field)):
                continue
            _add(issues, f"evidence_cards[{index}].{field}")


def _check_claim_fields(claims: list[dict[str, Any]], issues: list[str]) -> None:
    for index, claim in enumerate(claims):
        if not _filled(claim.get("claim_type")):
            _add(issues, f"claims[{index}].claim_type")


def _check_kpi_strip(metrics: list[dict[str, Any]], issues: list[str]) -> None:
    if len(metrics) < 2:
        return
    types = [_evidence_type(metric) for metric in metrics]
    present = {item for item in types if item}
    if len(present) > 1 and any(not _filled(metric.get("on_metric_label")) for metric in metrics):
        _add(issues, "heterogeneous_kpi_strip")
    if "structure_count" in present and (present & OUTCOME_EVIDENCE_TYPES):
        _add(issues, "structure_count_in_kpi_strip")


def _check_causal_verbs(
    text: str,
    metrics: list[dict[str, Any]],
    cards: list[dict[str, Any]],
    issues: list[str],
) -> None:
    if not any(verb in text for verb in CAUSAL_VERBS):
        return
    types = [_evidence_type(item) for item in (*metrics, *cards)]
    types = [item for item in types if item]
    if not types:
        _add(issues, "causal_verb_without_evidence_grade")
        return
    if any(item in STRONG_EVIDENCE_TYPES for item in types):
        return
    if all(item in WEAK_CAUSAL_EVIDENCE_TYPES for item in types):
        _add(issues, "causal_verb_without_evidence_grade")


def _check_common_sense(
    spec: dict[str, Any],
    metrics: list[dict[str, Any]],
    cards: list[dict[str, Any]],
    issues: list[str],
) -> None:
    used_as_strong = False
    for item in (*metrics, *cards):
        if _is_common_sense(_source_ref(item) or item.get("source")):
            used_as_strong = True
            break
    if not used_as_strong:
        sources = spec.get("sources")
        source_values = sources if isinstance(sources, list) else [sources]
        filled_sources = [item for item in source_values if _filled(item)]
        if filled_sources and all(_is_common_sense(item) for item in filled_sources) and (metrics or cards):
            used_as_strong = True
    if used_as_strong:
        _add(issues, "common_sense_as_strong_evidence")


def _check_current_kpi(metrics: list[dict[str, Any]], issues: list[str]) -> None:
    for metric in metrics:
        if _evidence_type(metric) == "internal_baseline":
            continue
        blob = " ".join(
            str(metric.get(key) or "")
            for key in ("label", "value", "note", "visual_role")
        )
        if "待采集" in blob or "试点验证" in blob:
            continue
        role = str(metric.get("visual_role") or "").strip().lower()
        if role in {"current", "current_kpi", "baseline"} or CURRENT_KPI_RE.search(blob):
            _add(issues, "current_kpi_without_internal_baseline")
            return


def _check_strong_claim(
    spec: dict[str, Any],
    text: str,
    metrics: list[dict[str, Any]],
    cards: list[dict[str, Any]],
    claims: list[dict[str, Any]],
    issues: list[str],
) -> None:
    if not any(marker in text for marker in STRONG_CLAIM_MARKERS):
        return
    direct = 0
    for item in (*metrics, *cards):
        if _evidence_type(item) in STRONG_EVIDENCE_TYPES and _source_ref(item):
            direct += 1
    for claim in claims:
        refs = claim.get("evidence_refs")
        if isinstance(refs, list):
            direct += sum(1 for ref in refs if _filled(ref))
    has_boundary = any(
        _filled(spec.get(key)) for key in ("counterexample", "boundary", "反例", "边界")
    ) or any(marker in text for marker in ("反例", "边界", "不适用"))
    if direct < 2 or not has_boundary:
        _add(issues, "strong_claim_insufficient_evidence")


def _check_math_illustration(text: str, issues: list[str]) -> None:
    if not any(marker in text for marker in MATH_MARKERS):
        return
    if not any(marker in text for marker in ORG_MARKERS):
        return
    if any(marker in text for marker in HEDGE_MARKERS):
        return
    _add(issues, "math_illustration_as_prescription")


def _check_charts(charts: list[tuple[str, int, dict[str, Any]]], issues: list[str]) -> None:
    for prefix, index, chart in charts:
        kind = str(chart.get("chart_kind") or "").strip().lower()
        has_data = _has_chart_data(chart)
        graph = _has_graph_syntax(chart)
        if kind and kind not in {"empirical", "mechanism"}:
            _add(issues, f"{prefix}[{index}].chart_kind")
        if graph and not has_data and kind != "mechanism":
            _add(issues, "pseudo_empirical_chart")
            if not kind:
                _add(issues, f"{prefix}[{index}].chart_kind")
        if kind == "empirical" or (not kind and has_data):
            if not has_data:
                _add(issues, f"{prefix}[{index}].data")
            if not _filled(chart.get("unit") or chart.get("units") or chart.get("y_unit")):
                _add(issues, f"{prefix}[{index}].unit")
            if not _filled(chart.get("source") or chart.get("source_ref") or chart.get("source_url")):
                _add(issues, f"{prefix}[{index}].source")
        if kind == "mechanism":
            blob = " ".join(
                str(chart.get(key) or "")
                for key in ("title", "insight", "caption", "label", "note")
            )
            if not any(marker in blob for marker in MECHANISM_LABELS):
                _add(issues, "mechanism_diagram_unlabeled")


def _collect_charts(spec: dict[str, Any]) -> list[tuple[str, int, dict[str, Any]]]:
    charts: list[tuple[str, int, dict[str, Any]]] = []
    for key in ("native_chart_slots", "charts", "conceptual_charts"):
        for index, item in enumerate(_dicts(spec.get(key))):
            charts.append((key, index, item))
    return charts


def _has_chart_data(chart: dict[str, Any]) -> bool:
    return _filled(chart.get("data") or chart.get("series") or chart.get("values"))


def _has_graph_syntax(chart: dict[str, Any]) -> bool:
    if chart.get("has_endpoints") or chart.get("has_coords"):
        return True
    if _filled(chart.get("endpoints") or chart.get("coords")):
        return True
    chart_type = str(chart.get("chart_type") or chart.get("type") or "").strip().lower()
    return chart_type in GRAPH_CHART_TYPES


def _evidence_type(item: dict[str, Any]) -> str:
    raw = str(item.get("evidence_type") or "").strip()
    if not raw:
        return ""
    return EVIDENCE_ALIASES.get(raw, raw).lower()


def _source_ref(item: dict[str, Any]) -> str:
    for key in ("source_ref", "source_url", "source_section"):
        value = item.get(key)
        if _filled(value):
            return str(value).strip()
    return ""


def _is_common_sense(value: Any) -> bool:
    text = str(value or "").strip()
    if not text:
        return False
    return bool(COMMON_SENSE_RE.match(text))


def _page_text(spec: dict[str, Any]) -> str:
    chunks: list[str] = []
    _collect_text(spec, chunks, depth=0)
    return "\n".join(chunks)


def _collect_text(value: Any, chunks: list[str], depth: int) -> None:
    if depth > 6:
        return
    if isinstance(value, str):
        text = value.strip()
        if text:
            chunks.append(text)
        return
    if isinstance(value, dict):
        skip = {"visual_tokens", "framework_layer", "structure_hierarchy", "quality_targets", "box"}
        for key, item in value.items():
            if key in skip:
                continue
            _collect_text(item, chunks, depth + 1)
        return
    if isinstance(value, list):
        for item in value:
            _collect_text(item, chunks, depth + 1)


def _dicts(raw: Any) -> list[dict[str, Any]]:
    if not isinstance(raw, list):
        return []
    return [item for item in raw if isinstance(item, dict)]


def _filled(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return False
        return not any(text.startswith(prefix) for prefix in PLACEHOLDER_PREFIXES)
    if isinstance(value, (list, tuple, dict)):
        return bool(value)
    return True


def _add(bucket: list[str], code: str) -> None:
    if code not in bucket:
        bucket.append(code)
