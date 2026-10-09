"""TDD coverage for the deck-level reporting contract validator."""
from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "validate_deck_contract.py"


def load_validator():
    spec = importlib.util.spec_from_file_location("validate_deck_contract", SCRIPT)
    if spec is None or spec.loader is None:
        raise FileNotFoundError(SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


MANIFEST = {
    "thesis": "统一证据后再扩大试点",
    "audience_decision": "批准一个团队的试点和负责人",
    "evidence_ladder": ["external_fact", "internal_observation", "proposal", "pilot_target"],
    "canonical_metrics": ["周期"],
    "canonical_products": ["工具甲"],
    "canonical_artifacts": ["需求卡"],
    "canonical_stages": ["试点"],
    "canonical_owners": ["研发负责人"],
    "visual_system": {
        "style_profile": "中文业务汇报",
        "typography": {"font": "Arial", "title_px": 36, "body_px": 24},
        "palette": {"background": "#FFFFFF", "text": "#172B4D", "accent": "#1967D2"},
        "spacing": {"margin_px": 48, "panel_gap_px": 24},
        "icon_style": "lucide 线性图标，同一线宽",
        "chart_style": "浅灰辅助线，蓝色强调主序列，标签显示单位",
        "surface": "白底浅灰面板，无投影",
    },
}


def page(**overrides):
    base = {
        "page_no": 2,
        "page_role": "content",
        "title": "一个团队先验证交付证据，再决定是否推广",
        "primary_claim": "先验证交付证据，再决定是否推广",
        "key_message": "先在一个团队把证据跑通，再决定是否推广。",
        "proves": "统一证据后再扩大试点",
        "dominant": "流程断点",
        "attached": ["试点范围", "证据位置"],
        "claim_type": "proposal",
        "evidence_type": "internal_baseline",
        "evidence_state": "PROPOSAL",
        "baseline_status": "internal_baseline",
        "skeleton_id": "process_v1",
        "same_skeleton_run": 1,
        "visual_brief": {
            "composition": "三段流程横向展开，缺证据的交接节点以缺口标记",
            "visual_focus": "流程中段的交接断点和待补的需求卡",
            "background": "白底，需求卡和测试记录用浅灰面板",
            "element_positions": "标题在上；记录附在对应节点下；来源和负责人在底部",
        },
        "plain_language_test": {
            "what_happened": "当前交接缺少统一证据。",
            "why_it_matters": "后续评审无法判断是否可以放行。",
            "what_next": "先在一个团队采集同一套字段。",
        },
        "supporting_points": [
            {
                "role": "evidence",
                "text": "试点团队已有一份需求卡和一份测试记录。",
                "source_ref": "pilot-log#1",
                "limitation": "样本只覆盖一个团队。",
            },
            {"role": "action", "text": "研发负责人在本周确认字段。"},
        ],
        "example_refs": [
            {
                "example_id": "06-process",
                "source": "assets/examples/output/06-process.pptx",
                "reuse_reason": "复用三段流程和验收收口",
                "adaptations": ["加入工件字段"],
            }
        ],
        "density_budget": {
            "min_unique_factual_atoms": 6,
            "min_relation_edges": 2,
            "min_evidence_bearing_objects": 2,
            "min_body_font_px": 15,
        },
    }
    base.update(overrides)
    return base


class DeckContractTests(unittest.TestCase):
    def test_valid_deck_passes(self):
        validator = load_validator()
        report = validator.validate_deck(MANIFEST, [page()])
        self.assertTrue(report["ok"], report)
        self.assertEqual(report["content_logic_passed"], True)

    def test_high_density_semantic_dominants_are_accepted_as_declarations(self):
        validator = load_validator()
        for dominant in ("成效看板", "诊断链", "阶段路线", "机制架构", "决策矩阵"):
            with self.subTest(dominant=dominant):
                report = validator.validate_deck(MANIFEST, [page(dominant=dominant)])
                self.assertTrue(report["ok"], report)
                self.assertEqual(report["validation_scope"], "declared_contract_only")

    def test_unknown_dominant_remains_blocking(self):
        validator = load_validator()
        report = validator.validate_deck(MANIFEST, [page(dominant="未知关系")])
        self.assertFalse(report["ok"])
        self.assertIn("page[2].dominant", report["blockers"])

    def test_missing_page_contract_is_blocking(self):
        validator = load_validator()
        broken = page(primary_claim="", proves="", example_refs=[], density_budget={})
        report = validator.validate_deck(MANIFEST, [broken])
        self.assertFalse(report["ok"])
        self.assertIn("page[2].primary_claim", report["blockers"])
        self.assertTrue(any("example" in item for item in report["blockers"]))

    def test_target_only_line_chart_without_baseline_is_blocking(self):
        validator = load_validator()
        broken = page(
            baseline_status="to_validate",
            native_chart_slots=[{"chart_type": "line", "data": []}],
        )
        report = validator.validate_deck(MANIFEST, [broken])
        self.assertFalse(report["ok"])
        self.assertTrue(any("baseline" in item for item in report["blockers"]))

    def test_comparison_page_without_native_table_is_blocking(self):
        validator = load_validator()
        broken = page(page_role="comparison_table", layout="comparison_table")
        report = validator.validate_deck(MANIFEST, [broken])
        self.assertFalse(report["ok"])
        self.assertTrue(any("table" in item for item in report["blockers"]))

    def test_repeated_default_action_is_blocking(self):
        validator = load_validator()
        repeated = page(action="进入试点设计与统一工件规范评审。")
        pages = [repeated, dict(repeated, page_no=3), dict(repeated, page_no=4)]
        report = validator.validate_deck(MANIFEST, pages)
        self.assertFalse(report["ok"])
        self.assertTrue(any("repeated" in item for item in report["blockers"]))

    def test_fixed_page_can_explain_no_example(self):
        validator = load_validator()
        fixed = page(
            page_no=1,
            page_role="cover",
            primary_claim="",
            key_message="AI开发全流程提效方案",
            proves="",
            dominant="",
            attached=[],
            claim_type="",
            evidence_type="",
            evidence_state="",
            baseline_status="not_applicable",
            supporting_points=[],
            plain_language_test={},
            density_budget={},
            visual_brief={},
            example_refs=[],
            not_reused_reason="固定封面页，职责是交代主题和受众。",
        )
        report = validator.validate_deck(MANIFEST, [fixed])
        self.assertTrue(report["ok"], report)

    def test_visual_system_is_required_at_deck_level(self):
        validator = load_validator()
        for value in (None, {}, "高级感"):
            with self.subTest(value=value):
                report = validator.validate_deck(dict(MANIFEST, visual_system=value), [page()])
                self.assertFalse(report["ok"])
                self.assertTrue(any("visual_system" in item for item in report["blockers"]))

    def test_visual_system_requires_values_for_each_dimension(self):
        validator = load_validator()
        for field in MANIFEST["visual_system"]:
            for value in (None, "", [], {}, True, False):
                with self.subTest(field=field, value=value):
                    system = dict(MANIFEST["visual_system"], **{field: value})
                    report = validator.validate_deck(dict(MANIFEST, visual_system=system), [page()])
                    self.assertFalse(report["ok"])
                    self.assertIn(f"manifest.visual_system.{field}", report["blockers"])

    def test_content_visual_brief_requires_composition_focus_background_and_positions(self):
        validator = load_validator()
        for field in page()["visual_brief"]:
            with self.subTest(field=field):
                brief = dict(page()["visual_brief"], **{field: ""})
                report = validator.validate_deck(MANIFEST, [page(visual_brief=brief)])
                self.assertFalse(report["ok"])
                self.assertIn(f"page[2].visual_brief.{field}", report["blockers"])

    def test_visual_declaration_checks_remain_distinct_from_render_review(self):
        validator = load_validator()
        report = validator.validate_deck(MANIFEST, [page()])
        self.assertTrue(report["visual_system_passed"])
        self.assertTrue(report["visual_brief_passed"])
        self.assertEqual(report["validation_scope"], "declared_contract_only")
        self.assertNotIn("visual_review", report)

    def test_repeated_skeleton_run_is_blocking(self):
        validator = load_validator()
        pages = [page(page_no=2), page(page_no=3, same_skeleton_run=2), page(page_no=4, same_skeleton_run=3)]
        report = validator.validate_deck(MANIFEST, pages)
        self.assertFalse(report["ok"])
        self.assertTrue(any("skeleton" in item for item in report["blockers"]))

    def test_reference_asset_requires_structural_dna(self):
        validator = load_validator()
        manifest = dict(MANIFEST, reference_assets=[{"asset_id": "user-reference-1"}])
        report = validator.validate_deck(manifest, [page()])
        self.assertFalse(report["ok"])
        self.assertIn("page[2].reference_dna", report["blockers"])
        adapted = page(reference_dna=["面板标题带", "证据关系", "底部推论"])
        report = validator.validate_deck(manifest, [adapted])
        self.assertTrue(report["ok"], report)


if __name__ == "__main__":
    unittest.main()
