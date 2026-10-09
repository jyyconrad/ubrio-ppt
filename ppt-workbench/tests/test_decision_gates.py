"""Page-level decision governance gates (session-884 C-04, C-07–C-12)."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SVG_DIR = ROOT / "scripts" / "svg"
if str(SVG_DIR) not in sys.path:
    sys.path.insert(0, str(SVG_DIR))

from gates.decision import check  # noqa: E402


class DecisionGateTests(unittest.TestCase):
    def test_raci_title_without_role_columns_missing_raci_schema(self) -> None:
        result = check(
            {
                "page_role": "content",
                "title": "研发协作 RACI",
                "key_message": "先分清谁来做",
                "layout": "gold_cards",
                "columns": ["AI可做", "人必须做", "共担"],
                "groups": [
                    {"title": "AI可做", "claim": "起草变更说明"},
                    {"title": "人必须做", "claim": "发布签字"},
                    {"title": "共担", "claim": "评审"},
                ],
            }
        )
        self.assertIn("raci_schema", result.missing)
        self.assertTrue(result.blocked())

    def test_decision_page_missing_card_fields(self) -> None:
        result = check(
            {
                "page_role": "decision",
                "title": "是否默认上线助手栈",
                "key_message": "请拍板试点范围",
                "layout": "gold_cards",
            }
        )
        for code in (
            "decision.options",
            "decision.criteria",
            "decision.owner",
            "decision.deadline",
            "decision.reject_condition",
        ):
            self.assertIn(code, result.missing, code)

    def test_decision_keyword_in_title_missing_card_fields(self) -> None:
        result = check(
            {
                "page_role": "content",
                "title": "本周拍板：默认工具栈",
                "key_message": "决策缺少拒绝条件",
                "layout": "gold_cards",
            }
        )
        self.assertIn("decision.criteria", result.missing)
        self.assertIn("decision.options", result.missing)

    def test_north_star_directional_metric_missing_baseline(self) -> None:
        result = check(
            {
                "page_role": "content",
                "title": "北极星：吞吐与稳定性",
                "key_message": "吞吐↑且稳定性不恶化",
                "layout": "gold_cards",
                "metrics": [
                    {
                        "label": "北极星",
                        "value": "吞吐↑且稳定性不恶化",
                        "note": "方向词",
                    }
                ],
                "north_star": "吞吐↑且稳定性不恶化",
            }
        )
        self.assertIn("north_star.baseline", result.missing)
        self.assertTrue(
            any(
                code in result.missing
                for code in (
                    "north_star.window",
                    "north_star.threshold",
                    "north_star.owner",
                )
            )
        )

    def test_stage_gate_principle_sentence_missing_threshold(self) -> None:
        result = check(
            {
                "page_role": "content",
                "title": "六阶段门禁",
                "key_message": "扫描必须通过才能放行",
                "layout": "gold_timeline",
                "stages": [
                    {
                        "id": "release",
                        "name": "发布",
                        "gate": "扫描必须通过",
                    }
                ],
            }
        )
        self.assertIn("gate.threshold", result.missing)
        self.assertTrue(
            any(code in result.missing for code in ("gate.approver", "gate.check"))
        )

    def test_artifacts_listed_without_stage_mapping(self) -> None:
        result = check(
            {
                "page_role": "content",
                "title": "硬工件字典",
                "key_message": "评测集必须进阶段",
                "layout": "gold_cards",
                "artifacts": [
                    {"id": "eval-set", "name": "评测集"},
                    {"id": "adr", "name": "ADR"},
                ],
                "stages": [
                    {
                        "id": "release",
                        "name": "发布",
                        "gate": {
                            "check": "秘密扫描",
                            "threshold": "高危=0",
                            "evidence_ref": "scan-log",
                            "approver": "安全负责人",
                            "exception_policy": "无例外",
                        },
                    }
                ],
            }
        )
        self.assertIn("artifact_stage_unmapped", result.missing)

    def test_product_comparison_without_dimensions_or_pending_status(self) -> None:
        result = check(
            {
                "page_role": "content",
                "title": "产品对照",
                "key_message": "公开能力描述不能当默认栈",
                "layout": "gold_evidence_table",
                "table_title": "产品对照",
                "product_matrix": {
                    "rows": [{"name": "Copilot"}, {"name": "Comate"}],
                },
            }
        )
        self.assertIn("product_matrix.pending_validation", result.missing)

    def test_roadmap_committed_without_exit_threshold(self) -> None:
        result = check(
            {
                "page_role": "content",
                "title": "90天路线图",
                "key_message": "按季度推进",
                "layout": "gold_timeline",
                "roadmap": [
                    {
                        "horizon": "90天",
                        "items": [
                            {
                                "action": "试点内部助手",
                                "status": "committed",
                            }
                        ],
                    }
                ],
            }
        )
        self.assertIn("roadmap.proposal_required", result.missing)

    def test_cover_page_has_no_blocking_missing(self) -> None:
        result = check(
            {
                "page_role": "cover",
                "title": "RACI 决策 拍板 北极星 门禁 路线图 产品对照",
                "key_message": "吞吐↑且稳定性不恶化",
                "layout": "cover",
            }
        )
        self.assertEqual(result.missing, [])
        self.assertFalse(result.blocked())

    def test_section_divider_has_no_blocking_missing(self) -> None:
        result = check(
            {
                "page_role": "section_divider",
                "title": "RACI 决策 门禁 路线图 产品对照",
                "key_message": "吞吐↑且稳定性不恶化",
            }
        )
        self.assertEqual(result.missing, [])

    def test_product_matrix_pending_validation_without_dimensions_ok(self) -> None:
        result = check(
            {
                "page_role": "content",
                "title": "产品对照",
                "key_message": "无内部试点，只给待验证矩阵",
                "product_matrix": {
                    "status": "pending_validation",
                    "rows": [{"name": "Copilot"}],
                },
            }
        )
        self.assertNotIn("product_matrix.pending_validation", result.missing)
        self.assertEqual(result.missing, [])

    def test_product_internally_validated_without_dimensions_missing(self) -> None:
        result = check(
            {
                "page_role": "content",
                "title": "产品对照",
                "product_matrix": {
                    "status": "internally_validated",
                    "rows": [{"name": "Copilot"}],
                },
            }
        )
        self.assertIn("product_matrix.pending_validation", result.missing)

    def test_roadmap_proposal_without_exit_threshold_ok(self) -> None:
        result = check(
            {
                "page_role": "content",
                "title": "90天路线图",
                "roadmap": [
                    {
                        "horizon": "90天",
                        "items": [
                            {"action": "试点内部助手", "status": "proposal"},
                        ],
                    }
                ],
            }
        )
        self.assertNotIn("roadmap.proposal_required", result.missing)
        self.assertEqual(result.missing, [])

    def test_north_star_pending_collection_is_substantive(self) -> None:
        result = check(
            {
                "page_role": "content",
                "title": "北极星",
                "north_star": {
                    "name": "吞吐且稳定性",
                    "baseline": "待采集",
                    "window": "待采集",
                    "threshold": "待采集",
                    "owner": "待采集",
                    "alert": "待采集",
                    "stop_rule": "待采集",
                },
            }
        )
        self.assertNotIn("north_star.baseline", result.missing)
        self.assertEqual(result.missing, [])

    def test_valid_decision_card_and_raci_matrix_has_no_missing(self) -> None:
        result = check(
            {
                "page_role": "decision",
                "title": "本周拍板：RACI 与可逆试点",
                "key_message": "四角色列已对齐，按标准选择可逆方案",
                "layout": "gold_evidence_table",
                "columns": ["R", "A", "C", "I"],
                "raci": {
                    "columns": ["R", "A", "C", "I"],
                    "rows": [
                        {
                            "item": "发布审批",
                            "R": "工程负责人",
                            "A": "CTO",
                            "C": "安全",
                            "I": "全员",
                        }
                    ],
                },
                "decisions": [
                    {
                        "decision": "是否试点内部代码助手",
                        "options": ["试点", "暂缓", "否决"],
                        "criteria": ["数据驻留内网", "成本可逆"],
                        "owner": "CTO",
                        "deadline": "2026-10-01",
                        "cost_or_risk": "试点预算 20 万，可回退",
                        "reversible": True,
                        "reject_condition": "无法内网部署则否决",
                        "next_evidence": "两周内网试点日志",
                    }
                ],
            }
        )
        self.assertEqual(result.missing, [])
        self.assertFalse(result.blocked())


if __name__ == "__main__":
    unittest.main()
