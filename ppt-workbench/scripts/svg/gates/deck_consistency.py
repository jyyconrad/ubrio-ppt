"""Deck-level homology: skeleton rhythm, products, artifacts, metrics, colors."""

from __future__ import annotations

import re
from typing import Any

from . import CONTENT_ROLES, COVER_ROLES, GateResult

_NUM = re.compile(r"[-+]?\d+(?:\.\d+)?")

KPI_TOKENS = frozenset({"metric-strip", "kpi-strip", "kpi_strip", "metrics-panel", "kpi-band"})
CONCLUSION_TOKENS = frozenset(
    {"action-bar", "conclusion-band", "footer-band", "bottom-band", "takeaway-band"}
)
SECTION_BAR_TOKENS = frozenset({"section-bar", "section_bar", "partition-bar", "chapter-bar"})

_PRODUCT_FIELDS = ("products", "product_list", "product_names", "product_coverage")
_DICT_FIELDS = ("artifacts", "hard_artifacts", "artifact_dictionary", "artifact_set")
_PRODUCT_COLUMN_HINTS = frozenset({"产品", "product", "products", "方案", "工具", "vendor"})
_PRODUCT_MATRIX_DIMENSION_FIELDS = ("product_dimensions", "comparison_dimensions")


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


def _norm_name(value: Any) -> str:
    return re.sub(r"\s+", "", str(value or "").strip())


def _page_role(spec: dict[str, Any]) -> str:
    raw = spec.get("page_role") or spec.get("page_archetype") or spec.get("role") or "content"
    return str(raw).strip().lower()


def _is_content(spec: dict[str, Any]) -> bool:
    role = _page_role(spec)
    if role in COVER_ROLES:
        return False
    return role in CONTENT_ROLES or role not in COVER_ROLES


def _visual_layer(spec: dict[str, Any]) -> list[str]:
    layer = spec.get("visual_layer")
    if layer is None:
        hierarchy = spec.get("structure_hierarchy")
        if isinstance(hierarchy, dict):
            layer = hierarchy.get("visual_layer")
    if layer is None:
        return []
    if isinstance(layer, str):
        return [layer] if layer else []
    return [str(item) for item in _as_list(layer)]


def skeleton_key(spec: dict) -> str:
    """Prefer layout_fingerprint; else layout + '|' + comma-joined visual_layer."""
    if not isinstance(spec, dict):
        return "|"
    fingerprint = spec.get("layout_fingerprint")
    if _filled(fingerprint):
        return str(fingerprint)
    layout = str(spec.get("layout") or "")
    return layout + "|" + ",".join(_visual_layer(spec))


def _alias_map(specs: list[dict[str, Any]]) -> dict[str, str]:
    mapping: dict[str, str] = {}
    for spec in specs:
        raw = spec.get("product_alias")
        if raw is None:
            raw = spec.get("product_aliases")
        if isinstance(raw, dict):
            for src, dst in raw.items():
                if _filled(src) and _filled(dst):
                    mapping[_norm_name(src)] = _norm_name(dst)
        else:
            for item in _as_list(raw):
                if not isinstance(item, dict):
                    continue
                src = item.get("from") or item.get("alias") or item.get("src")
                dst = item.get("to") or item.get("canonical") or item.get("name")
                if _filled(src) and _filled(dst):
                    mapping[_norm_name(src)] = _norm_name(dst)
    return mapping


def _canonicalize(name: str, aliases: dict[str, str]) -> str:
    current = name
    seen: set[str] = set()
    for _ in range(8):
        if current in seen:
            break
        seen.add(current)
        nxt = aliases.get(current)
        if not nxt or nxt == current:
            break
        current = nxt
    return current


def _iter_named(value: Any) -> list[str]:
    names: list[str] = []
    for item in _as_list(value):
        if isinstance(item, str) and item.strip():
            names.append(_norm_name(item))
        elif isinstance(item, dict):
            label = (
                item.get("name")
                or item.get("title")
                or item.get("product")
                or item.get("artifact")
                or item.get("label")
            )
            if _filled(label):
                names.append(_norm_name(label))
    return [name for name in names if name]


def _group_dimension_keys(group: dict[str, Any]) -> set[str]:
    skip = {
        "title",
        "name",
        "claim",
        "evidence",
        "explanation",
        "action",
        "body",
        "tag",
        "id",
        "owner",
        "status",
        "note",
        "source",
        "role",
    }
    keys: set[str] = set()
    for key, value in group.items():
        low = str(key).strip().lower()
        if low in skip:
            continue
        if low in {"items", "fields", "dimensions", "attrs", "comparison"}:
            if isinstance(value, dict):
                keys.update(str(k).strip().lower() for k in value)
            else:
                for item in _as_list(value):
                    if isinstance(item, dict):
                        label = item.get("label") or item.get("key") or item.get("name")
                        if _filled(label):
                            keys.add(str(label).strip().lower())
        elif _filled(value):
            keys.add(low)
    return keys


def _declares_product_matrix(spec: dict[str, Any], groups: list[dict[str, Any]]) -> bool:
    if any(_filled(spec.get(field)) for field in _PRODUCT_MATRIX_DIMENSION_FIELDS):
        return True
    matrix = spec.get("product_matrix")
    if isinstance(matrix, dict) and _filled(matrix.get("dimensions")):
        return True
    comparison = spec.get("comparison")
    if isinstance(comparison, dict) and _filled(comparison.get("dimensions")):
        return True
    if groups and all(_filled(group.get("product")) for group in groups):
        return True
    context = " ".join(
        str(spec.get(field) or "").strip().lower()
        for field in ("page_role", "page_archetype", "layout")
    )
    return "product" in context and any(token in context for token in ("matrix", "comparison", "table"))


def _looks_like_product_matrix(spec: dict[str, Any]) -> bool:
    groups = [item for item in _as_list(spec.get("groups") or spec.get("cards")) if isinstance(item, dict)]
    if len(groups) < 2 or not _declares_product_matrix(spec, groups):
        return False
    dim_sets = [_group_dimension_keys(group) for group in groups]
    dim_sets = [keys for keys in dim_sets if len(keys) >= 2]
    if len(dim_sets) < 2:
        return False
    shared = set(dim_sets[0])
    for keys in dim_sets[1:]:
        shared &= keys
    return len(shared) >= 2


def _products_from_slots(spec: dict[str, Any]) -> set[str]:
    names: set[str] = set()
    for slot in _as_list(spec.get("native_table_slots") or spec.get("table_slots")):
        if not isinstance(slot, dict):
            continue
        columns = [str(col).strip() for col in _as_list(slot.get("columns"))]
        if not columns:
            continue
        idx = 0
        header = columns[0].lower()
        if header not in _PRODUCT_COLUMN_HINTS and columns[0] not in _PRODUCT_COLUMN_HINTS:
            continue
        for row in _as_list(slot.get("rows")):
            cell = None
            if isinstance(row, dict):
                cells = _as_list(row.get("cells"))
                cell = cells[idx] if cells else row.get(columns[0])
            elif isinstance(row, (list, tuple)) and row:
                cell = row[idx]
            if _filled(cell):
                names.add(_norm_name(cell))
    return names


def _product_names(spec: dict[str, Any]) -> set[str]:
    names: set[str] = set()
    for field in _PRODUCT_FIELDS:
        names.update(_iter_named(spec.get(field)))
    comparison = spec.get("comparison")
    if isinstance(comparison, dict):
        names.update(_iter_named(comparison.get("products") or comparison.get("items")))
    if _looks_like_product_matrix(spec):
        for group in _as_list(spec.get("groups") or spec.get("cards")):
            if isinstance(group, dict):
                label = group.get("title") or group.get("name") or group.get("product")
                if _filled(label):
                    names.add(_norm_name(label))
    names.update(_products_from_slots(spec))
    return {name for name in names if name}


def _artifact_names(value: Any) -> set[str]:
    return {name for name in _iter_named(value) if name}


def _dictionary_artifacts(spec: dict[str, Any]) -> set[str]:
    names: set[str] = set()
    for field in _DICT_FIELDS:
        names.update(_artifact_names(spec.get(field)))
    return names


def _stage_entries(spec: dict[str, Any]) -> list[dict[str, Any]]:
    stages = spec.get("stages")
    if isinstance(stages, list):
        return [item for item in stages if isinstance(item, dict)]
    if isinstance(spec.get("stage_artifacts"), dict):
        entries = []
        for name, arts in spec["stage_artifacts"].items():
            entries.append({"name": name, "artifacts": arts})
        return entries
    return []


def _stage_artifact_names(spec: dict[str, Any]) -> set[str]:
    names: set[str] = set()
    names.update(_artifact_names(spec.get("stage_artifacts")))
    for stage in _stage_entries(spec):
        names.update(_artifact_names(stage.get("artifacts") or stage.get("outputs") or stage.get("deliverables")))
        mapped = stage.get("artifact")
        if _filled(mapped):
            names.add(_norm_name(mapped))
    for item in _as_list(spec.get("artifact_dictionary") or spec.get("artifacts")):
        if isinstance(item, dict) and _filled(item.get("stage") or item.get("mapped_stage")):
            label = item.get("name") or item.get("artifact") or item.get("title")
            if _filled(label):
                names.add(_norm_name(label))
    return names


def _metric_value(raw: Any) -> str:
    if raw is None:
        return ""
    text = str(raw).strip().replace(",", "")
    match = _NUM.search(text)
    if not match:
        return text.lower()
    number = match.group(0)
    try:
        value = float(number)
    except ValueError:
        return number
    if value.is_integer():
        return str(int(value))
    return format(value, "g")


def _metrics(spec: dict[str, Any]) -> list[tuple[str, str, str]]:
    found: list[tuple[str, str, str]] = []
    for item in _as_list(spec.get("metrics") or spec.get("kpis")):
        if not isinstance(item, dict):
            continue
        value = _metric_value(item.get("value"))
        if not value:
            continue
        role = str(item.get("number_role") or item.get("role") or "").strip().lower() or "unspecified"
        purpose = str(item.get("number_purpose") or item.get("purpose") or "").strip()
        found.append((value, role, purpose))
    return found


def _legend_map(raw: Any) -> dict[str, str]:
    mapping: dict[str, str] = {}
    if isinstance(raw, dict):
        for color, meaning in raw.items():
            if _filled(color) and _filled(meaning):
                mapping[str(color).strip().lower()] = _norm_name(meaning)
        return mapping
    for item in _as_list(raw):
        if not isinstance(item, dict):
            continue
        color = item.get("color") or item.get("token") or item.get("key")
        meaning = item.get("meaning") or item.get("label") or item.get("role")
        if _filled(color) and _filled(meaning):
            mapping[str(color).strip().lower()] = _norm_name(meaning)
    return mapping


def _semantic_colors(spec: dict[str, Any]) -> dict[str, str]:
    raw = spec.get("semantic_colors") or spec.get("color_semantics")
    return _legend_map(raw)


def _token_present(spec: dict[str, Any], tokens: frozenset[str]) -> bool:
    layer = {item.strip().lower() for item in _visual_layer(spec)}
    return bool(layer & tokens)


def _section_value(spec: dict[str, Any]) -> str:
    value = spec.get("section")
    if value is None:
        value = spec.get("chapter")
    return str(value).strip() if _filled(value) else ""


def _append_unique(bucket: list[str], code: str) -> None:
    if code not in bucket:
        bucket.append(code)


def _consecutive_content_runs(specs: list[dict[str, Any]]) -> list[list[tuple[int, dict[str, Any]]]]:
    runs: list[list[tuple[int, dict[str, Any]]]] = []
    current: list[tuple[int, dict[str, Any]]] = []
    for index, spec in enumerate(specs):
        if _is_content(spec):
            current.append((index, spec))
            continue
        if current:
            runs.append(current)
            current = []
    if current:
        runs.append(current)
    return runs


def check_deck(specs: list[dict]) -> GateResult:
    pages = [spec if isinstance(spec, dict) else {} for spec in _as_list(specs)]
    result = GateResult(details={"page_count": len(pages)})
    if not pages:
        return result

    aliases = _alias_map(pages)
    product_sets: list[tuple[int, set[str]]] = []
    dictionary: set[str] = set()
    stage_arts: set[str] = set()
    metric_pages: dict[tuple[str, str], list[int]] = {}
    metric_purpose_missing: dict[str, bool] = {}
    legends: dict[str, str] = {}
    used_semantic = False
    legend_conflict = False
    has_any_legend = False

    for index, spec in enumerate(pages):
        products = {_canonicalize(name, aliases) for name in _product_names(spec)}
        products.discard("")
        if products:
            product_sets.append((index, products))
        dictionary.update(_dictionary_artifacts(spec))
        stage_arts.update(_stage_artifact_names(spec))
        for value, role, purpose in _metrics(spec):
            metric_pages.setdefault((value, role), []).append(index)
            if value not in metric_purpose_missing:
                metric_purpose_missing[value] = False
            if not purpose:
                metric_purpose_missing[value] = True
        page_legend = _legend_map(spec.get("color_legend"))
        if page_legend:
            has_any_legend = True
        semantics = _semantic_colors(spec)
        if semantics:
            used_semantic = True
            if not page_legend:
                page_legend = semantics
        for color, meaning in page_legend.items():
            prior = legends.get(color)
            if prior and prior != meaning:
                legend_conflict = True
            legends[color] = meaning

    for run in _consecutive_content_runs(pages):
        streak_key = None
        streak_len = 0
        streak_pages: list[int] = []
        kpi_streak = 0
        conclusion_streak = 0
        bar_streak = 0
        for index, spec in run:
            key = skeleton_key(spec)
            if key == streak_key:
                streak_len += 1
                streak_pages.append(index)
            else:
                streak_key = key
                streak_len = 1
                streak_pages = [index]
            if streak_len >= 3:
                _append_unique(result.missing, "skeleton_repeat")
                result.details.setdefault("skeleton_repeat_pages", []).append(
                    [page + 1 for page in streak_pages[-3:]]
                )
            kpi_streak = kpi_streak + 1 if _token_present(spec, KPI_TOKENS) else 0
            conclusion_streak = conclusion_streak + 1 if _token_present(spec, CONCLUSION_TOKENS) else 0
            bar_streak = bar_streak + 1 if _token_present(spec, SECTION_BAR_TOKENS) else 0
            if kpi_streak >= 3:
                _append_unique(result.warnings, "kpi_strip_reuse")
            if conclusion_streak >= 3:
                _append_unique(result.warnings, "conclusion_band_reuse")
            if bar_streak >= 3:
                _append_unique(result.warnings, "section_bar_reuse")

        if len(run) >= 4:
            sections = {_section_value(spec) for _, spec in run}
            if len(sections) <= 1:
                _append_unique(result.missing, "chapter_rhythm")
                result.details["chapter_rhythm_pages"] = [index + 1 for index, _ in run]
            else:
                _append_unique(result.warnings, "chapter_rhythm")
                result.details["chapter_rhythm_warning_pages"] = [index + 1 for index, _ in run]

    if len(product_sets) >= 2:
        canonical_sets = [names for _, names in product_sets]
        first = canonical_sets[0]
        if any(names != first for names in canonical_sets[1:]):
            _append_unique(result.missing, "product_list_drift")
            result.details["product_sets"] = {
                str(index + 1): sorted(names) for index, names in product_sets
            }

    if dictionary and stage_arts and dictionary != stage_arts:
        _append_unique(result.missing, "artifact_dictionary")
        result.details["dictionary_only"] = sorted(dictionary - stage_arts)
        result.details["stage_only"] = sorted(stage_arts - dictionary)

    for (value, role), indexes in metric_pages.items():
        unique_pages = sorted(set(indexes))
        if len(unique_pages) >= 3:
            _append_unique(result.missing, "repeated_metric_role")
            result.details.setdefault("repeated_metrics", []).append(
                {"value": value, "number_role": role, "pages": [i + 1 for i in unique_pages]}
            )

    roles_by_value: dict[str, set[str]] = {}
    for value, role in metric_pages:
        roles_by_value.setdefault(value, set()).add(role)
    for value, roles in roles_by_value.items():
        if len(roles) >= 2 and metric_purpose_missing.get(value):
            _append_unique(result.warnings, "number_purpose")

    if legend_conflict or (used_semantic and not has_any_legend and not legends):
        _append_unique(result.missing, "color_legend")

    return result
