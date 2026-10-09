from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SVG_DIR = ROOT / "scripts" / "svg"
if str(SVG_DIR) not in sys.path:
    sys.path.insert(0, str(SVG_DIR))

from gates.deck_consistency import check_deck, skeleton_key  # noqa: E402


def _page(role: str = "content", layout: str = "gold_cards", visual=None, **extra):
    spec = {"page_role": role, "layout": layout}
    if visual is not None:
        spec["visual_layer"] = visual
    spec.update(extra)
    return spec


def _metric(value, role="evidence", purpose=None, label="采用率"):
    item = {"label": label, "value": value, "number_role": role}
    if purpose is not None:
        item["number_purpose"] = purpose
    return item


class DeckConsistencyGateTests(unittest.TestCase):
    def test_skeleton_key_prefers_layout_fingerprint(self):
        spec = _page(
            layout="gold_cards",
            visual=["main-title", "metric-strip"],
            layout_fingerprint="cards|kpi|footer",
        )
        self.assertEqual(skeleton_key(spec), "cards|kpi|footer")

    def test_skeleton_key_falls_back_to_layout_and_visual_layer(self):
        spec = _page(layout="gold_cards", visual=["main-title", "key-message", "action-bar"])
        self.assertEqual(skeleton_key(spec), "gold_cards|main-title,key-message,action-bar")

    def test_skeleton_key_reads_nested_visual_layer(self):
        spec = {
            "layout": "gold_cards",
            "structure_hierarchy": {"visual_layer": ["main-title", "metric-strip"]},
        }
        self.assertEqual(skeleton_key(spec), "gold_cards|main-title,metric-strip")

    def test_three_consecutive_content_pages_with_same_skeleton_are_missing(self):
        visual = ["main-title", "key-message", "metric-strip", "main-content", "action-bar"]
        specs = [
            _page(visual=visual),
            _page(visual=visual),
            _page(visual=visual),
        ]
        result = check_deck(specs)
        self.assertIn("skeleton_repeat", result.missing)
        self.assertTrue(result.blocked())

    def test_two_consecutive_same_skeleton_is_allowed(self):
        visual = ["main-title", "metric-strip"]
        specs = [
            _page(visual=visual),
            _page(visual=visual),
            _page(layout="gold_timeline", visual=["main-title", "timeline"]),
        ]
        result = check_deck(specs)
        self.assertNotIn("skeleton_repeat", result.missing)

    def test_product_list_drift_without_alias_is_missing(self):
        specs = [
            _page(visual=["a"], products=["CodeGeeX", "Copilot"]),
            _page(layout="gold_timeline", visual=["b"], products=["Comate", "CodeBuddy", "Snap"]),
        ]
        result = check_deck(specs)
        self.assertIn("product_list_drift", result.missing)

    def test_product_alias_map_closes_product_coverage(self):
        specs = [
            _page(
                visual=["a"],
                products=["CodeGeeX", "CodeBuddy"],
                product_alias={"CodeGeeX": "Comate"},
            ),
            _page(layout="gold_timeline", visual=["b"], products=["Comate", "CodeBuddy"]),
        ]
        result = check_deck(specs)
        self.assertNotIn("product_list_drift", result.missing)

    def test_generic_business_groups_are_not_inferred_as_product_lists(self):
        def groups(prefix):
            return [
                {
                    "title": f"{prefix}一",
                    "claim": "结论",
                    "evidence": "证据",
                    "explanation": "解释",
                    "role": "analysis",
                },
                {
                    "title": f"{prefix}二",
                    "claim": "结论",
                    "evidence": "证据",
                    "explanation": "解释",
                    "role": "analysis",
                },
            ]

        specs = [
            _page(layout="initiative_cards", visual=["initiative"], groups=groups("举措")),
            _page(layout="diagnosis_chain", visual=["diagnosis"], groups=groups("诊断")),
            _page(layout="stage_route", visual=["stages"], groups=groups("阶段")),
        ]
        result = check_deck(specs)
        self.assertNotIn("product_list_drift", result.missing)

    def test_product_tables_still_detect_product_list_drift(self):
        def product_table(*names):
            return [{"columns": ["产品", "定位"], "rows": [[name, "研发助手"] for name in names]}]

        specs = [
            _page(visual=["products-a"], native_table_slots=product_table("Comate", "CodeBuddy")),
            _page(
                layout="product_table",
                visual=["products-b"],
                native_table_slots=product_table("Comate", "Copilot"),
            ),
        ]
        result = check_deck(specs)
        self.assertIn("product_list_drift", result.missing)

    def test_explicit_product_comparison_dimensions_still_detect_drift(self):
        def products(*names):
            return [
                {"title": name, "定位": "研发助手", "权限": "仓库级"}
                for name in names
            ]

        specs = [
            _page(
                visual=["products-a"],
                comparison_dimensions=["定位", "权限"],
                groups=products("Comate", "CodeBuddy"),
            ),
            _page(
                layout="product_comparison",
                visual=["products-b"],
                comparison_dimensions=["定位", "权限"],
                groups=products("Comate", "Copilot"),
            ),
        ]
        result = check_deck(specs)
        self.assertIn("product_list_drift", result.missing)

    def test_artifact_dictionary_not_closed_with_stage_set_is_missing(self):
        specs = [
            _page(
                visual=["dict"],
                artifacts=["需求验收标准", "ADR", "上下文包", "评测集", "发布清单"],
            ),
            _page(
                layout="gold_timeline",
                visual=["stages"],
                stages=[
                    {"name": "需求", "artifacts": ["需求验收标准", "上下文包"]},
                    {"name": "设计", "artifacts": ["ADR"]},
                    {"name": "构建", "artifacts": ["变更集", "AI 产物标识"]},
                    {"name": "测试", "artifacts": ["秘密扫描报告"]},
                    {"name": "发布", "artifacts": ["发布清单", "回滚预案"]},
                    {"name": "运行", "artifacts": ["值班确认"]},
                ],
            ),
        ]
        result = check_deck(specs)
        self.assertIn("artifact_dictionary", result.missing)

    def test_closed_artifact_union_passes(self):
        artifacts = ["需求验收标准", "ADR", "上下文包", "评测集", "发布清单"]
        specs = [
            _page(visual=["dict"], artifacts=artifacts),
            _page(
                layout="gold_timeline",
                visual=["stages"],
                stages=[
                    {"name": "需求", "artifacts": ["需求验收标准", "评测集"]},
                    {"name": "设计", "artifacts": ["ADR", "上下文包"]},
                    {"name": "发布", "artifacts": ["发布清单"]},
                ],
            ),
        ]
        result = check_deck(specs)
        self.assertNotIn("artifact_dictionary", result.missing)

    def test_same_metric_value_on_three_pages_with_same_number_role_is_missing(self):
        specs = [
            _page(visual=["a"], metrics=[_metric("55.8%")]),
            _page(layout="gold_timeline", visual=["b"], metrics=[_metric(55.8)]),
            _page(layout="gold_action_ledger", visual=["c"], metrics=[_metric("55.8")]),
        ]
        result = check_deck(specs)
        self.assertIn("repeated_metric_role", result.missing)

    def test_repeated_metric_allowed_when_number_role_changes(self):
        specs = [
            _page(visual=["a"], metrics=[_metric("90%", "evidence", "实验室对照")]),
            _page(
                layout="gold_timeline",
                visual=["b"],
                metrics=[_metric("90%", "constraint", "门禁下限")],
            ),
            _page(
                layout="gold_action_ledger",
                visual=["c"],
                metrics=[_metric("90%", "decision", "是否立项")],
            ),
        ]
        result = check_deck(specs)
        self.assertNotIn("repeated_metric_role", result.missing)

    def test_four_content_pages_without_divider_and_same_section_are_missing(self):
        specs = [
            _page(layout="gold_cards", visual=["a"], section="市场"),
            _page(layout="gold_timeline", visual=["b"], section="市场"),
            _page(layout="gold_action_ledger", visual=["c"], section="市场"),
            _page(layout="pyramid_hierarchy", visual=["d"], section="市场"),
        ]
        result = check_deck(specs)
        self.assertIn("chapter_rhythm", result.missing)

    def test_four_content_pages_without_divider_but_changing_section_warn(self):
        specs = [
            _page(layout="gold_cards", visual=["a"], section="市场"),
            _page(layout="gold_timeline", visual=["b"], section="对照"),
            _page(layout="gold_action_ledger", visual=["c"], section="规范"),
            _page(layout="pyramid_hierarchy", visual=["d"], section="决策"),
        ]
        result = check_deck(specs)
        self.assertNotIn("chapter_rhythm", result.missing)
        self.assertIn("chapter_rhythm", result.warnings)

    def test_section_divider_resets_chapter_rhythm(self):
        specs = [
            _page(layout="gold_cards", visual=["a"], section="市场"),
            _page(layout="gold_timeline", visual=["b"], section="市场"),
            _page(layout="gold_action_ledger", visual=["c"], section="市场"),
            _page(role="section_divider", layout="gold_section", visual=["div"], section="规范"),
            _page(layout="pyramid_hierarchy", visual=["d"], section="规范"),
        ]
        result = check_deck(specs)
        self.assertNotIn("chapter_rhythm", result.missing)
        self.assertNotIn("chapter_rhythm", result.warnings)

    def test_consistent_deck_has_empty_missing(self):
        artifacts = ["需求验收标准", "ADR", "上下文包", "评测集", "发布清单"]
        specs = [
            _page(role="cover", layout="gold_cover", visual=["hero"]),
            _page(
                visual=["cards"],
                section="市场",
                products=["Comate", "CodeBuddy"],
                metrics=[_metric("55.8%", "evidence", "实验")],
                artifacts=artifacts,
            ),
            _page(
                layout="gold_timeline",
                visual=["timeline"],
                section="市场",
                products=["Comate", "CodeBuddy"],
                metrics=[_metric("90%", "constraint", "门禁")],
            ),
            _page(role="section_divider", layout="gold_section", visual=["div"], section="规范"),
            _page(
                layout="gold_action_ledger",
                visual=["ledger"],
                section="规范",
                native_table_slots=[
                    {
                        "id": "table-slot-1",
                        "box": {"x": 70, "y": 288, "w": 1140, "h": 360},
                        "columns": ["工件", "阶段"],
                        "rows": [["评测集", "需求"]],
                        "source": "规范草案",
                    }
                ],
                stages=[
                    {"name": "需求", "artifacts": ["需求验收标准", "评测集"]},
                    {"name": "设计", "artifacts": ["ADR", "上下文包"]},
                    {"name": "发布", "artifacts": ["发布清单"]},
                ],
            ),
            _page(role="closing", layout="gold_closing", visual=["end"]),
        ]
        result = check_deck(specs)
        self.assertEqual(result.missing, [])
        self.assertFalse(result.blocked())


if __name__ == "__main__":
    unittest.main()
