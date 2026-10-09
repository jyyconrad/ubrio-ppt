"""Page-level routing: tabular specs must use native_table_slots, not SVG fake tables."""

from __future__ import annotations

from typing import Any

from . import COVER_ROLES, GateResult

TABLE_LAYOUTS = frozenset(
    {
        "gold_evidence_table",
        "gold_action_ledger",
        "gold_issue_log",
        "table",
        "evidence_table",
        "action_ledger",
    }
)

# Card copy fields are not comparison dimensions.
_CARD_KEYS = frozenset(
    {
        "title",
        "name",
        "claim",
        "evidence",
        "action",
        "action_or_risk",
        "explanation",
        "implication",
        "body",
        "tag",
        "icon",
        "note",
        "notes",
        "bullets",
        "id",
        "role",
        "owner",
        "status",
        "index",
        "subtitle",
        "key_message",
        "caption",
        "source",
        "layout",
        "page_role",
        "claim_type",
        "evidence_type",
        "evidence_state",
        "source_ref",
        "source_url",
        "source_section",
        "population",
        "period",
        "year",
        "denominator",
        "limitation",
        "component",
        "state_label",
    }
)

_NESTED_DIM_KEYS = frozenset(
    {
        "items",
        "fields",
        "dimensions",
        "attrs",
        "attributes",
        "compare",
        "comparison",
        "cells",
        "metrics",
        "values",
    }
)


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
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, tuple, dict)):
        return bool(value)
    return True


def _page_role(spec: dict[str, Any]) -> str:
    raw = spec.get("page_role") or spec.get("page_archetype") or spec.get("role") or "content"
    return str(raw).strip().lower()


def _row_count(rows: Any) -> int:
    count = 0
    for row in _as_list(rows):
        if isinstance(row, dict):
            if "cells" in row:
                if any(_filled(cell) for cell in _as_list(row.get("cells"))) or _as_list(row.get("cells")):
                    count += 1
            elif any(_filled(v) for k, v in row.items() if str(k).lower() not in {"id"}):
                count += 1
        elif isinstance(row, (list, tuple)):
            if any(_filled(cell) for cell in row) or row:
                count += 1
        elif _filled(row):
            count += 1
    return count


def _columns_of(value: Any) -> list[str]:
    columns: list[str] = []
    for item in _as_list(value):
        if isinstance(item, dict):
            label = item.get("label") or item.get("name") or item.get("title") or item.get("key")
            if _filled(label):
                columns.append(str(label).strip())
        elif _filled(item):
            columns.append(str(item).strip())
    return columns


def _nested_dimension_keys(value: Any) -> set[str]:
    keys: set[str] = set()
    if isinstance(value, dict):
        for key, nested in value.items():
            low = str(key).strip().lower()
            if low in _CARD_KEYS:
                continue
            if isinstance(nested, (dict, list, tuple)):
                keys.update(_nested_dimension_keys(nested))
            elif _filled(nested):
                keys.add(low)
        return keys
    for item in _as_list(value):
        if isinstance(item, dict):
            label = item.get("label") or item.get("key") or item.get("name") or item.get("title") or item.get("dim")
            if _filled(label):
                keys.add(str(label).strip().lower())
            else:
                keys.update(_nested_dimension_keys(item))
        elif isinstance(item, str) and ":" in item:
            keys.add(item.split(":", 1)[0].strip().lower())
    return keys


def _group_dimension_keys(group: Any) -> set[str]:
    if not isinstance(group, dict):
        return set()
    keys: set[str] = set()
    for key, value in group.items():
        low = str(key).strip().lower()
        if low in _CARD_KEYS:
            continue
        if low in _NESTED_DIM_KEYS:
            keys.update(_nested_dimension_keys(value))
        elif _filled(value):
            keys.add(low)
    return keys


def _comparison_groups(spec: dict[str, Any]) -> list[Any]:
    groups = _as_list(spec.get("groups") or spec.get("cards") or spec.get("products"))
    comparison = spec.get("comparison")
    if isinstance(comparison, dict):
        groups = groups + _as_list(comparison.get("items") or comparison.get("products") or comparison.get("groups"))
    return groups


def _is_comparison_matrix(spec: dict[str, Any]) -> bool:
    groups = [item for item in _comparison_groups(spec) if isinstance(item, dict)]
    if len(groups) < 2:
        return False
    dim_sets = [_group_dimension_keys(group) for group in groups]
    dim_sets = [keys for keys in dim_sets if keys]
    if len(dim_sets) < 2:
        return False
    shared = set(dim_sets[0])
    for keys in dim_sets[1:]:
        shared &= keys
    return len(shared) >= 2


def _group_has_embedded_table(spec: dict[str, Any]) -> bool:
    for group in _as_list(spec.get("groups") or spec.get("cards")):
        if not isinstance(group, dict):
            continue
        columns = _columns_of(group.get("columns"))
        if columns and _row_count(group.get("rows")) >= 3:
            return True
    comparison = spec.get("comparison")
    if isinstance(comparison, dict):
        columns = _columns_of(comparison.get("columns"))
        rows = comparison.get("rows") or comparison.get("items") or comparison.get("products")
        if columns and _row_count(rows) >= 3:
            return True
        if _row_count(rows) >= 3 and len(_columns_of(comparison.get("axes"))) >= 2:
            return True
    return False


def is_tabular_content(spec: dict) -> bool:
    if not isinstance(spec, dict):
        return False
    layout = str(spec.get("layout") or "").strip().lower()
    if layout in TABLE_LAYOUTS:
        return True
    columns = _columns_of(spec.get("columns"))
    if columns and _row_count(spec.get("rows")) >= 3:
        return True
    if _group_has_embedded_table(spec):
        return True
    table = spec.get("table")
    if isinstance(table, dict) and _columns_of(table.get("columns")) and _row_count(table.get("rows")) >= 3:
        return True
    if _is_comparison_matrix(spec):
        return True
    return False


def _slot_box_ok(slot: dict[str, Any]) -> bool:
    box = slot.get("box")
    if not isinstance(box, dict):
        return False
    has_origin = "x" in box and "y" in box
    has_size = ("w" in box or "width" in box) and ("h" in box or "height" in box)
    return has_origin and has_size


def _valid_native_slots(spec: dict[str, Any]) -> list[dict[str, Any]]:
    raw = spec.get("native_table_slots")
    if raw is None:
        raw = spec.get("table_slots")
    slots = raw if isinstance(raw, list) else _as_list(raw)
    valid: list[dict[str, Any]] = []
    for slot in slots:
        if not isinstance(slot, dict):
            continue
        columns = _columns_of(slot.get("columns"))
        if not columns or _row_count(slot.get("rows")) < 1:
            continue
        valid.append(slot)
    return valid


def _fallback_reason(spec: dict[str, Any]) -> str:
    reason = spec.get("table_fallback_reason")
    if isinstance(reason, str) and reason.strip():
        return reason.strip()
    return ""


def check(spec: dict) -> GateResult:
    if not isinstance(spec, dict):
        spec = {}
    role = _page_role(spec)
    result = GateResult(details={"page_role": role, "tabular": False, "slot_count": 0})
    if role in COVER_ROLES:
        result.details["skipped"] = True
        return result

    tabular = is_tabular_content(spec)
    result.details["tabular"] = tabular
    if not tabular:
        return result

    slots = _valid_native_slots(spec)
    result.details["slot_count"] = len(slots)
    if slots:
        incomplete = [slot.get("id") or "?" for slot in slots if not _slot_box_ok(slot) or not _filled(slot.get("source"))]
        if incomplete:
            result.warnings.append("native_table_slot_incomplete")
            result.details["incomplete_slots"] = incomplete
        return result

    reason = _fallback_reason(spec)
    if reason:
        result.warnings.append("table_fallback_reason")
        result.details["table_fallback_reason"] = reason
        return result

    result.missing.append("native_table_required")
    layout = str(spec.get("layout") or "")
    if layout in TABLE_LAYOUTS:
        result.details["reason"] = "table_layout"
    elif _is_comparison_matrix(spec):
        result.details["reason"] = "comparison_matrix"
    else:
        result.details["reason"] = "columns_rows"
    return result
