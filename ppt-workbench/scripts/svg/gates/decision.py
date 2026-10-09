"""Page-level decision governance gates (session-884 C-04, C-07–C-12).

`check(spec)` is unit-testable and must not import `build_gold_svg_page`.
`GateResult.missing` is intended to block `quality_status=ready` in quality_report.
"""

from __future__ import annotations

import re
from typing import Any

from . import COVER_ROLES, GateResult

# Trigger tokens scanned from title, key_message, layout, group titles,
# columns, and table_title. Do not require a dedicated layout name.
_RACI_RE = re.compile(r"raci", re.I)
_DECISION_RE = re.compile(r"拍板|决策卡|决策页|待决策|请决策|需决策")
_DECISION_NOISE = ("决策含义",)
_NORTH_STAR_TOKEN = "北极星"
_GATE_TOKEN = "门禁"
_ROADMAP_TOKEN = "路线图"
_PRODUCT_TOKEN = "产品对照"
_DIRECTIONAL_RE = re.compile(r"[↑↓⬆⬇]|不恶化")
_PENDING_BASELINE = ("待采集", "待验证")
_PENDING_MATRIX = {"pending_validation", "pending", "待验证"}
_VALIDATED_MATRIX = {"internally_validated", "validated", "已验证"}
_PROPOSAL = "proposal"

_RACI_ROLES = frozenset({"R", "A", "C", "I"})
_RACI_ALIAS = {
    "r": "R",
    "responsible": "R",
    "负责": "R",
    "责任人": "R",
    "a": "A",
    "accountable": "A",
    "问责": "A",
    "c": "C",
    "consulted": "C",
    "咨询": "C",
    "i": "I",
    "informed": "I",
    "知情": "I",
    "知会": "I",
}

DECISION_FIELDS = (
    ("decision", ("decision", "topic", "议题")),
    ("options", ("options", "选项")),
    ("criteria", ("criteria", "判断标准", "标准")),
    ("owner", ("owner", "Owner", "负责人")),
    ("deadline", ("deadline", "截止时间", "截止日期", "截止")),
    ("cost_or_risk", ("cost_or_risk", "cost_risk", "cost", "risk", "成本", "风险")),
    ("reversible", ("reversible", "reversibility", "可逆性", "可逆")),
    ("reject_condition", ("reject_condition", "reject", "拒绝条件")),
    ("next_evidence", ("next_evidence", "next evidence", "下一步证据")),
)

NORTH_STAR_FIELDS = ("baseline", "window", "threshold", "owner", "alert", "stop_rule")
GATE_FIELDS = ("check", "threshold", "evidence_ref", "approver", "exception_policy")
ROADMAP_ITEM_FIELDS = (
    "predecessor",
    "resource_owner",
    "budget_or_permission",
    "exit_threshold",
    "delay_policy",
)
REQUIRED_DIMENSIONS = (
    ("deploy_form", ("deploy form", "deploy_form", "deployment", "部署形态", "部署方式")),
    ("data_residency", ("data residency", "data_residency", "数据驻留", "数据边界")),
    ("permission_model", ("permission model", "permission_model", "权限模型")),
    ("context_access", ("context access", "context_access", "上下文接入")),
    ("cost", ("cost", "成本")),
    ("audit", ("audit", "审计")),
    ("integration", ("integration", "集成")),
    ("measured_results", ("measured results", "measured_results", "实测结果", "实测")),
)


def check(spec: dict) -> GateResult:
    if not isinstance(spec, dict):
        spec = {}
    role = str(spec.get("page_role") or spec.get("page_archetype") or "").strip().lower()
    if role in COVER_ROLES:
        return GateResult()

    missing: list[str] = []
    warnings: list[str] = []
    blob = _trigger_blob(spec)
    triggers: list[str] = []

    raci_hit = _raci_mentioned(spec, blob)
    decision_hit = role == "decision" or _decision_mentioned(spec, blob)
    north_hit = _north_star_mentioned(spec, blob)
    gate_hit = _gate_mentioned(spec, blob)
    artifact_hit = _has_entries(spec.get("artifacts"))
    product_hit = _product_mentioned(spec, blob)
    roadmap_hit = _roadmap_mentioned(spec, blob)

    if raci_hit:
        triggers.append("raci")
        _check_raci(spec, missing, warnings)
    if decision_hit:
        triggers.append("decision")
        _check_decisions(spec, missing)
    if north_hit:
        triggers.append("north_star")
        _check_north_star(spec, missing)
    if gate_hit:
        triggers.append("gate")
        _check_gates(spec, missing)
    if artifact_hit:
        triggers.append("artifacts")
        _check_artifacts(spec, missing)
    if product_hit:
        triggers.append("product_matrix")
        _check_product_matrix(spec, missing, warnings)
    if roadmap_hit:
        triggers.append("roadmap")
        _check_roadmap(spec, missing)

    return GateResult(
        missing=missing,
        warnings=warnings,
        details={"triggers": triggers},
    )


def _add(missing: list[str], code: str) -> None:
    if code not in missing:
        missing.append(code)


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    return [value]


def _filled(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, bool):
        return True
    if isinstance(value, (int, float)):
        return True
    if isinstance(value, str):
        text = value.strip()
        return bool(text) and not text.startswith("待补")
    if isinstance(value, dict):
        return any(_filled(item) for item in value.values())
    if isinstance(value, (list, tuple, set)):
        return any(_filled(item) for item in value)
    return True


def _has_entries(value: Any) -> bool:
    return any(isinstance(item, (dict, str)) and _filled(item) for item in _as_list(value))


def _trigger_blob(spec: dict[str, Any]) -> str:
    parts: list[str] = []
    for key in ("title", "key_message", "layout", "table_title", "subtitle"):
        parts.append(str(spec.get(key) or ""))
    for col in _as_list(spec.get("columns")):
        parts.append(_label_of(col))
    for group in _as_list(spec.get("groups")):
        if isinstance(group, dict):
            parts.append(str(group.get("title") or ""))
        else:
            parts.append(str(group or ""))
    return "\n".join(parts)


def _label_of(value: Any) -> str:
    if isinstance(value, dict):
        for key in ("title", "name", "label", "id", "header"):
            if _filled(value.get(key)):
                return str(value.get(key)).strip()
        return ""
    return str(value or "").strip()


def _strip_noise(text: str) -> str:
    cleaned = text
    for noise in _DECISION_NOISE:
        cleaned = cleaned.replace(noise, "")
    return cleaned


def _raci_mentioned(spec: dict[str, Any], blob: str) -> bool:
    if _RACI_RE.search(blob):
        return True
    if isinstance(spec.get("raci"), dict):
        return True
    return False


def _decision_mentioned(spec: dict[str, Any], blob: str) -> bool:
    if _has_entries(spec.get("decisions")):
        return True
    if isinstance(spec.get("decision"), dict):
        return True
    text = _strip_noise(blob)
    if _DECISION_RE.search(text):
        return True
    return "决策" in text


def _north_star_mentioned(spec: dict[str, Any], blob: str) -> bool:
    if spec.get("north_star") not in (None, "", [], {}):
        return True
    if _NORTH_STAR_TOKEN in blob:
        return True
    for text in _metric_texts(spec):
        if _NORTH_STAR_TOKEN in text or _directional_only(text):
            return True
    return False


def _gate_mentioned(spec: dict[str, Any], blob: str) -> bool:
    if _has_entries(spec.get("stages")):
        return True
    return _GATE_TOKEN in blob


def _product_mentioned(spec: dict[str, Any], blob: str) -> bool:
    if isinstance(spec.get("product_matrix"), dict):
        return True
    return _PRODUCT_TOKEN in blob


def _roadmap_mentioned(spec: dict[str, Any], blob: str) -> bool:
    if _has_entries(spec.get("roadmap")):
        return True
    return _ROADMAP_TOKEN in blob


def _metric_texts(spec: dict[str, Any]) -> list[str]:
    texts: list[str] = []
    for metric in _as_list(spec.get("metrics")):
        if isinstance(metric, dict):
            for key in ("label", "value", "note", "name"):
                if metric.get(key) is not None:
                    texts.append(str(metric.get(key)))
        elif metric is not None:
            texts.append(str(metric))
    ns = spec.get("north_star")
    if isinstance(ns, str):
        texts.append(ns)
    elif isinstance(ns, dict):
        for key in ("name", "value", "statement", "goal"):
            if ns.get(key) is not None:
                texts.append(str(ns.get(key)))
    return texts


def _directional_only(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    text = value.strip()
    if not text or not _DIRECTIONAL_RE.search(text):
        return False
    if any(token in text for token in _PENDING_BASELINE):
        return False
    return re.search(r"\d", text) is None


def _substantive(value: Any) -> bool:
    if isinstance(value, bool):
        return True
    if isinstance(value, (int, float)):
        return True
    if isinstance(value, str):
        text = value.strip()
        if not text or text.startswith("待补"):
            return False
        if any(token in text for token in _PENDING_BASELINE):
            return True
        if _directional_only(text):
            return False
        return True
    if isinstance(value, dict):
        return any(_substantive(item) for item in value.values())
    if isinstance(value, (list, tuple, set)):
        return any(_substantive(item) for item in value)
    return _filled(value)


def _field(record: dict[str, Any], names: tuple[str, ...]) -> Any:
    for name in names:
        if name in record and record.get(name) is not None:
            return record.get(name)
    lowered = {str(key).strip().lower(): value for key, value in record.items()}
    for name in names:
        key = name.lower()
        if key in lowered:
            return lowered[key]
    return None


def _check_raci(spec: dict[str, Any], missing: list[str], warnings: list[str]) -> None:
    if _has_raci_schema(spec):
        return
    _add(missing, "raci_schema")
    warnings.append("RACI requires R/A/C/I columns or role_mapping; otherwise use 责任边界")


def _has_raci_schema(spec: dict[str, Any]) -> bool:
    raci = spec.get("raci")
    if isinstance(raci, dict):
        if _roles_from_columns(raci.get("columns")) >= _RACI_ROLES:
            return True
        mapping = raci.get("role_mapping") or raci.get("mapping")
        if isinstance(mapping, dict) and _roles_from_columns(list(mapping.keys())) >= _RACI_ROLES:
            return True
        rows = [row for row in _as_list(raci.get("rows")) if isinstance(row, dict)]
        if rows and all(_roles_from_columns(list(row.keys())) >= _RACI_ROLES for row in rows):
            return True
    if _roles_from_columns(spec.get("columns")) >= _RACI_ROLES:
        return True
    group_titles = [
        group.get("title")
        for group in _as_list(spec.get("groups"))
        if isinstance(group, dict)
    ]
    if _roles_from_columns(group_titles) >= _RACI_ROLES:
        return True
    return False


def _roles_from_columns(columns: Any) -> set[str]:
    found: set[str] = set()
    for column in _as_list(columns):
        label = _label_of(column)
        tokens = _raci_tokens(label)
        if len(tokens) == 1:
            found.update(tokens)
    return found


def _raci_tokens(label: str) -> set[str]:
    found: set[str] = set()
    for part in re.split(r"[/|,;；，\s]+", label.strip()):
        token = part.strip().lower()
        if not token:
            continue
        if token in _RACI_ALIAS:
            found.add(_RACI_ALIAS[token])
        elif token.upper() in _RACI_ROLES:
            found.add(token.upper())
    return found


def _collect_decision_cards(spec: dict[str, Any]) -> list[dict[str, Any]]:
    cards: list[dict[str, Any]] = []
    for item in _as_list(spec.get("decisions")):
        if isinstance(item, dict):
            cards.append(item)
    raw = spec.get("decision")
    if isinstance(raw, dict):
        cards.append(raw)
    return cards


def _check_decisions(spec: dict[str, Any], missing: list[str]) -> None:
    cards = _collect_decision_cards(spec)
    if not cards:
        for code, _names in DECISION_FIELDS:
            _add(missing, f"decision.{code}")
        return
    for card in cards:
        for code, names in DECISION_FIELDS:
            value = _field(card, names)
            if code == "reversible":
                ok = value is not None and _filled(value)
            elif code == "options":
                ok = _filled(value) and (
                    not isinstance(value, list) or any(_filled(item) for item in value)
                )
            else:
                ok = _substantive(value) if isinstance(value, str) else _filled(value)
            if not ok:
                _add(missing, f"decision.{code}")


def _north_star_record(spec: dict[str, Any]) -> dict[str, Any]:
    raw = spec.get("north_star")
    if isinstance(raw, dict):
        return raw
    record: dict[str, Any] = {}
    if isinstance(raw, str) and raw.strip():
        record["name"] = raw.strip()
    return record


def _check_north_star(spec: dict[str, Any], missing: list[str]) -> None:
    record = _north_star_record(spec)
    for field in NORTH_STAR_FIELDS:
        if not _substantive(record.get(field)):
            _add(missing, f"north_star.{field}")


def _measurable_threshold(value: Any) -> bool:
    if not _filled(value):
        return False
    if isinstance(value, (int, float, bool)):
        return True
    text = str(value).strip()
    if any(token in text for token in _PENDING_BASELINE):
        return True
    if re.search(r"\d", text):
        return True
    if any(token in text for token in (">=", "<=", "≥", "≤", ">", "<", "%", "=")):
        return True
    return False


def _gate_records(spec: dict[str, Any]) -> list[Any]:
    records: list[Any] = []
    for stage in _as_list(spec.get("stages")):
        if not isinstance(stage, dict):
            continue
        if "gate" in stage:
            records.append(stage.get("gate"))
        elif any(key in stage for key in GATE_FIELDS):
            records.append(stage)
    return records


def _check_gates(spec: dict[str, Any], missing: list[str]) -> None:
    records = _gate_records(spec)
    if not records:
        for field in GATE_FIELDS:
            _add(missing, f"gate.{field}")
        return
    for gate in records:
        if isinstance(gate, str):
            principle = any(token in gate for token in ("必须通过", "人确认", "齐全"))
            for field in GATE_FIELDS:
                if field == "check" and _filled(gate) and not principle:
                    continue
                _add(missing, f"gate.{field}")
            continue
        if not isinstance(gate, dict):
            for field in GATE_FIELDS:
                _add(missing, f"gate.{field}")
            continue
        for field in GATE_FIELDS:
            value = _field(gate, (field,))
            if field == "threshold":
                ok = _measurable_threshold(value)
            else:
                ok = _filled(value)
            if not ok:
                _add(missing, f"gate.{field}")


def _stage_index(spec: dict[str, Any]) -> dict[str, dict[str, Any]]:
    index: dict[str, dict[str, Any]] = {}
    for stage in _as_list(spec.get("stages")):
        if not isinstance(stage, dict):
            continue
        for key in (stage.get("id"), stage.get("stage_id"), stage.get("name")):
            if _filled(key):
                index[str(key).strip()] = stage
    return index


def _check_artifacts(spec: dict[str, Any], missing: list[str]) -> None:
    artifacts = [item for item in _as_list(spec.get("artifacts")) if isinstance(item, dict)]
    if not artifacts:
        _add(missing, "artifact_stage_unmapped")
        return
    stages = _stage_index(spec)
    if not stages:
        _add(missing, "artifact_stage_unmapped")
        return
    for artifact in artifacts:
        stage_key = artifact.get("stage_id") or artifact.get("stage")
        stage = stages.get(str(stage_key).strip()) if _filled(stage_key) else None
        owner = artifact.get("owner") or (stage.get("owner") if stage else None)
        gate_ref = artifact.get("gate_id") or artifact.get("gate")
        stage_gate = stage.get("gate") if stage else None
        if stage is None or not _filled(owner) or not (_filled(gate_ref) or _filled(stage_gate)):
            _add(missing, "artifact_stage_unmapped")
            return


def _dimension_labels(matrix: dict[str, Any]) -> list[str]:
    labels: list[str] = []
    for item in _as_list(matrix.get("dimensions") or matrix.get("decision_dimensions")):
        labels.append(_label_of(item) or str(item))
    return labels


def _has_required_dimensions(matrix: dict[str, Any]) -> bool:
    blob = "\n".join(_dimension_labels(matrix)).lower()
    for _code, aliases in REQUIRED_DIMENSIONS:
        if not any(alias.lower() in blob for alias in aliases):
            return False
    return True


def _check_product_matrix(spec: dict[str, Any], missing: list[str], warnings: list[str]) -> None:
    matrix = spec.get("product_matrix")
    if not isinstance(matrix, dict):
        matrix = {}
    status = str(matrix.get("status") or "").strip().lower()
    pending = status in _PENDING_MATRIX
    if pending:
        warnings.append("product_matrix is 待验证矩阵; do not present a default stack")
        return
    if _has_required_dimensions(matrix) and status in _VALIDATED_MATRIX:
        return
    _add(missing, "product_matrix.pending_validation")


def _roadmap_items(spec: dict[str, Any]) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for block in _as_list(spec.get("roadmap")):
        if not isinstance(block, dict):
            continue
        nested = _as_list(block.get("items"))
        if nested:
            items.extend(item for item in nested if isinstance(item, dict))
        elif any(key in block for key in ("action", "exit_threshold", "status")):
            items.append(block)
    return items


def _item_complete(item: dict[str, Any]) -> bool:
    if not _filled(item.get("action") or item.get("name") or item.get("title")):
        return False
    for field in ROADMAP_ITEM_FIELDS:
        if not _filled(item.get(field)):
            return False
    return True


def _check_roadmap(spec: dict[str, Any], missing: list[str]) -> None:
    items = _roadmap_items(spec)
    if not items:
        _add(missing, "roadmap.proposal_required")
        return
    for item in items:
        status = str(item.get("status") or "").strip().lower()
        if status == _PROPOSAL:
            continue
        if not _item_complete(item):
            _add(missing, "roadmap.proposal_required")
            return
