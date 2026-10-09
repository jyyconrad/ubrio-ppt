#!/usr/bin/env python3
"""Validate the deck-level Chinese reporting contract before page authoring.

This is intentionally a small, deterministic preflight.  It complements the
single-page gold builder: the builder checks whether a page can be rendered,
while this validator checks whether a deck can be explained, compared, and
reviewed without silently filling missing business fields.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

ALLOWED_STATES = {"FACT", "OBSERVED", "PROPOSAL", "TARGET", "TO_VALIDATE"}
# These are accepted semantic declarations. Whether the rendered page visibly
# realizes the declared relationship still requires preview-based review.
ALLOWED_DOMINANTS = {
    "不可比证据",
    "流程断点",
    "左右对照",
    "门禁",
    "决定章",
    "成效看板",
    "诊断链",
    "阶段路线",
    "机制架构",
    "决策矩阵",
}
FIXED_ROLES = {"cover", "agenda", "section_divider", "closing", "chapter"}
TABLE_ROLES = {
    "comparison_table",
    "contract_matrix",
    "stage_gate",
    "decision_matrix",
    "table",
    "evidence_table",
    "product_comparison",
    "gate",
    "decision",
    "contract",
}
REQUIRED_MANIFEST_FIELDS = (
    "thesis",
    "audience_decision",
    "evidence_ladder",
    "canonical_metrics",
    "canonical_products",
    "canonical_artifacts",
    "canonical_stages",
    "canonical_owners",
)
REQUIRED_DENSITY_FIELDS = (
    "min_unique_factual_atoms",
    "min_relation_edges",
    "min_evidence_bearing_objects",
    "min_body_font_px",
)
REQUIRED_RHYTHM_FIELDS = ("skeleton_id", "same_skeleton_run")
REQUIRED_VISUAL_SYSTEM_FIELDS = (
    "style_profile", "typography", "palette", "spacing",
    "icon_style", "chart_style", "surface",
)
REQUIRED_VISUAL_BRIEF_FIELDS = (
    "composition", "visual_focus", "background", "element_positions",
)


def _design_value(value: Any) -> bool:
    """Accept descriptions or concrete tokens, not an approval boolean."""
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, dict):
        return any(_design_value(item) for item in value.values())
    if isinstance(value, list):
        return any(_design_value(item) for item in value)
    return type(value) in (int, float)


def _items(value: Any) -> list[Any]:
    return value if isinstance(value, list) else ([] if value is None else [value])


def _text(value: Any) -> str:
    return str(value or "").strip()


def _filled(value: Any) -> bool:
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, list):
        return any(_filled(item) for item in value)
    if isinstance(value, dict):
        return any(_filled(item) for item in value.values())
    return value is not None


def _page_no(page: dict[str, Any], index: int) -> str:
    return _text(page.get("page_no") or page.get("page") or index)


def _native_table_present(page: dict[str, Any]) -> bool:
    native_data = page.get("native_data")
    return bool(
        page.get("native_table") is True
        or _items(page.get("native_table_slots"))
        or _items(page.get("tables"))
        or (isinstance(native_data, dict) and _items(native_data.get("tables")))
    )


def _chart_kinds(page: dict[str, Any]) -> set[str]:
    kinds: set[str] = set()
    for slot in _items(page.get("native_chart_slots") or page.get("chart_slots")):
        if isinstance(slot, dict):
            kind = _text(slot.get("kind") or slot.get("chart_type") or slot.get("type")).lower()
            if kind:
                kinds.add(kind)
    native_data = page.get("native_data")
    if isinstance(native_data, dict):
        for chart in _items(native_data.get("charts")):
            if isinstance(chart, dict):
                kind = _text(chart.get("kind") or chart.get("chart_type")).lower()
                if kind:
                    kinds.add(kind)
    return kinds


def _canonical_values(page: dict[str, Any], field: str) -> list[str]:
    values = page.get(field)
    if values is None:
        values = page.get(field.removeprefix("canonical_"))
    output: list[str] = []
    for item in _items(values):
        if isinstance(item, dict):
            item = item.get("label") or item.get("name") or item.get("id")
        if _text(item):
            output.append(_text(item))
    return output


def validate_deck(manifest: dict[str, Any], pages: list[dict[str, Any]]) -> dict[str, Any]:
    blockers: list[str] = []
    warnings: list[str] = []
    categories: defaultdict[str, list[str]] = defaultdict(list)

    def block(message: str, category: str) -> None:
        blockers.append(message)
        categories[category].append(message)

    def warn(message: str) -> None:
        warnings.append(message)

    for field in REQUIRED_MANIFEST_FIELDS:
        value = manifest.get(field)
        if field in {"thesis", "audience_decision"}:
            if not _text(value):
                block(f"manifest.{field}", "content")
        elif not isinstance(value, list) or not value:
            block(f"manifest.{field}", "content")
    ladder = {_text(item) for item in _items(manifest.get("evidence_ladder"))}
    if len(ladder) < 3:
        block("manifest.evidence_ladder>=3", "evidence")

    if not pages:
        block("manifest.pages>=1", "content")

    visual_system = manifest.get("visual_system")
    if not isinstance(visual_system, dict):
        block("manifest.visual_system", "visual_system")
    else:
        for field in REQUIRED_VISUAL_SYSTEM_FIELDS:
            value = visual_system.get(field)
            if not isinstance(value, (str, dict)) or not _design_value(value):
                block(f"manifest.visual_system.{field}", "visual_system")

    content_pages: list[dict[str, Any]] = []
    thesis = _text(manifest.get("thesis"))
    has_reference_assets = bool(_items(manifest.get("reference_assets")))
    for index, page in enumerate(pages, start=1):
        if not isinstance(page, dict):
            block(f"page[{index}].object", "content")
            continue
        number = _page_no(page, index)
        role = _text(page.get("page_role") or page.get("page_archetype") or "content").lower()
        prefix = f"page[{number}]"
        if role in FIXED_ROLES:
            if not _filled(page.get("title")):
                block(f"{prefix}.title", "content")
            if not (_items(page.get("example_refs")) or _text(page.get("not_reused_reason"))):
                block(f"{prefix}.example_reuse", "examples")
            continue
        content_pages.append(page)

        visual_brief = page.get("visual_brief")
        if not isinstance(visual_brief, dict):
            block(f"{prefix}.visual_brief", "visual_brief")
        else:
            for field in REQUIRED_VISUAL_BRIEF_FIELDS:
                value = visual_brief.get(field)
                if not isinstance(value, (str, dict)) or not _design_value(value):
                    block(f"{prefix}.visual_brief.{field}", "visual_brief")

        for field in ("title", "primary_claim", "key_message", "proves", "claim_type", "evidence_type", "evidence_state", "baseline_status"):
            if not _filled(page.get(field)):
                block(f"{prefix}.{field}", "content")
        dominant = _text(page.get("dominant"))
        if dominant not in ALLOWED_DOMINANTS:
            block(f"{prefix}.dominant", "content")
        attached = _items(page.get("attached"))
        if not 1 <= len(attached) <= 3:
            block(f"{prefix}.attached=1..3", "content")
        if any(field not in page for field in REQUIRED_RHYTHM_FIELDS):
            block(f"{prefix}.rhythm_fields", "density")
        elif not _text(page.get("skeleton_id")) or not isinstance(page.get("same_skeleton_run"), int) or page.get("same_skeleton_run") < 1:
            block(f"{prefix}.rhythm_values", "density")
        elif page.get("same_skeleton_run") > 2:
            block(f"{prefix}.same_skeleton_run<=2", "density")
        if thesis and _text(page.get("proves")) not in thesis:
            block(f"{prefix}.proves_not_in_thesis", "content")

        points = _items(page.get("supporting_points") or page.get("groups"))
        if not 2 <= len(points) <= 3:
            block(f"{prefix}.supporting_points=2..3", "content")
        evidence_found = False
        for point in points:
            if not isinstance(point, dict):
                continue
            role_name = _text(point.get("role"))
            if role_name in {"evidence", "fact", "observation"}:
                evidence_found = True
                if not (_text(point.get("source_ref")) or _text(page.get("source_ref")) or _items(page.get("evidence_refs"))):
                    block(f"{prefix}.evidence.source_ref", "evidence")
                if not (_text(point.get("limitation")) or _items(page.get("limitations"))):
                    block(f"{prefix}.evidence.limitation", "evidence")
        if not evidence_found and not _items(page.get("evidence_refs")):
            block(f"{prefix}.evidence", "evidence")
        state = _text(page.get("evidence_state")).upper()
        if state not in ALLOWED_STATES:
            block(f"{prefix}.evidence_state", "evidence")

        plain = page.get("plain_language_test")
        if not isinstance(plain, dict) or any(not _text(plain.get(key)) for key in ("what_happened", "why_it_matters", "what_next")):
            block(f"{prefix}.plain_language_test", "content")

        refs = _items(page.get("example_refs"))
        if not refs and not _text(page.get("not_reused_reason")):
            block(f"{prefix}.example_reuse", "examples")
        if has_reference_assets and not _items(page.get("reference_dna")) and not _text(page.get("not_reused_reason")):
            block(f"{prefix}.reference_dna", "examples")
        for ref_index, ref in enumerate(refs, start=1):
            if not isinstance(ref, dict) or not _text(ref.get("example_id")):
                block(f"{prefix}.example_refs[{ref_index}].example_id", "examples")
            elif not (_text(ref.get("source")) and _text(ref.get("reuse_reason")) and _items(ref.get("adaptations"))):
                block(f"{prefix}.example_refs[{ref_index}].reuse_reason_adaptations", "examples")

        density = page.get("density_budget")
        if not isinstance(density, dict) or any(key not in density for key in REQUIRED_DENSITY_FIELDS):
            block(f"{prefix}.density_budget", "density")
        elif any(
            not isinstance(density.get(key), (int, float)) or density.get(key) <= 0
            for key in REQUIRED_DENSITY_FIELDS
        ) or density.get("min_body_font_px", 0) < 15:
            block(f"{prefix}.density_budget_values", "density")
        if _text(page.get("baseline_status")).lower() not in {"internal_baseline", "observed", "actual", "not_applicable"}:
            kinds = _chart_kinds(page)
            if "line" in kinds or "trend" in kinds or "timeseries" in kinds:
                block(f"{prefix}.baseline_required_for_line_chart", "baseline")

        page_layout = _text(page.get("layout") or role).lower()
        if page.get("fake_table") is True or page.get("svg_table") is True or page.get("draw_table_with_svg") is True:
            block(f"{prefix}.fake_table", "table")
        if page_layout in TABLE_ROLES and not _native_table_present(page):
            block(f"{prefix}.native_table_required", "table")

        action = page.get("action") or page.get("action_or_decision")
        if not _filled(action) and not any(isinstance(point, dict) and _text(point.get("role")) in {"action", "decision"} for point in points):
            block(f"{prefix}.action_or_decision", "content")

    for canonical_field in ("canonical_metrics", "canonical_products", "canonical_artifacts", "canonical_stages", "canonical_owners"):
        allowed = {_text(item) for item in _items(manifest.get(canonical_field)) if _text(item)}
        page_field = canonical_field.removeprefix("canonical_")
        for page in content_pages:
            unknown = set(_canonical_values(page, page_field)) - allowed if allowed else set()
            if unknown:
                block(f"page[{_page_no(page, 0)}].{page_field}_not_canonical:{','.join(sorted(unknown))}", "consistency")

    for field in ("action", "action_or_decision", "evidence_boundary"):
        values: Counter[str] = Counter()
        locations: defaultdict[str, list[str]] = defaultdict(list)
        for page in content_pages:
            value = _text(page.get(field))
            if value:
                values[value] += 1
                locations[value].append(_page_no(page, 0))
        for value, count in values.items():
            if count >= 3 and not any(_text(page.get("page_function_change") or page.get("reuse_purpose")) for page in content_pages if _text(page.get(field)) == value):
                block(f"repeated_default.{field}:{','.join(locations[value])}", "consistency")
            elif count >= 2:
                warn(f"repeated.{field}:{','.join(locations[value])}")

    previous_skeleton = ""
    run_length = 0
    for page in content_pages:
        skeleton = _text(page.get("skeleton_id"))
        if skeleton and skeleton == previous_skeleton:
            run_length += 1
        else:
            previous_skeleton = skeleton
            run_length = 1 if skeleton else 0
        if run_length > 2:
            block(f"repeated_skeleton.{skeleton}:run>{2}", "density")

    return {
        "ok": not blockers,
        "validation_scope": "declared_contract_only",
        "content_logic_passed": not categories["content"],
        "evidence_boundary_passed": not categories["evidence"],
        "baseline_target_rule_passed": not categories["baseline"],
        "table_semantics_passed": not categories["table"],
        "example_reuse_passed": not categories["examples"],
        "density_passed": not categories["density"],
        "cross_page_consistency_passed": not categories["consistency"],
        "visual_system_passed": not categories["visual_system"],
        "visual_brief_passed": not categories["visual_brief"],
        "blockers": sorted(set(blockers)),
        "warnings": sorted(set(warnings)),
    }


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_pages(manifest: dict[str, Any], pages_dir: Path | None, page_spec: Path | None) -> list[dict[str, Any]]:
    if page_spec:
        return [_load_json(page_spec)]
    if pages_dir:
        paths = sorted(
            path for path in pages_dir.glob("*.json")
            if not any(token in path.name for token in ("normalized", "fill_plan", "patch"))
        )
        return [_load_json(path) for path in paths]
    pages = manifest.get("pages")
    return pages if isinstance(pages, list) else []


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--pages-dir", type=Path)
    parser.add_argument("--page-spec", type=Path)
    args = parser.parse_args()
    if args.pages_dir and args.page_spec:
        parser.error("use only one of --pages-dir and --page-spec")
    manifest = _load_json(args.manifest)
    if not isinstance(manifest, dict):
        raise SystemExit("manifest must be a JSON object")
    pages = load_pages(manifest, args.pages_dir, args.page_spec)
    report = validate_deck(manifest, pages)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["ok"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
