"""quality_report must merge session-884 page gates."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _load_builder():
    path = ROOT / "scripts/svg/build_gold_svg_page.py"
    spec = importlib.util.spec_from_file_location("build_gold_svg_page", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class QualityReportGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.builder = _load_builder()

    def test_cover_does_not_invent_three_metrics(self) -> None:
        spec = {
            "page_role": "cover",
            "layout": "gold_cards",
            "title": "全流程提效先定使用规范，再按阶段放量",
            "key_message": "这是一次产品调研，不是当场拍板。",
            "sources": ["本册大纲"],
        }
        normalized = self.builder.normalize_page_spec(spec)
        report = self.builder.quality_report(normalized)
        self.assertFalse(any(str(code).startswith("metrics>=") for code in report["missing"]), report["missing"])
        labels = [item.get("label") for item in normalized.get("metrics") or [] if isinstance(item, dict)]
        self.assertEqual(labels, [])

    def test_placeholder_spec_is_not_ready_and_lists_semantic_codes(self) -> None:
        spec = self.builder.build_page_spec_template(layout="gold_cards")
        normalized = self.builder.normalize_page_spec(spec)
        report = self.builder.quality_report(normalized)
        self.assertEqual(report["quality_status"], "needs_repair")
        missing = report["missing"]
        self.assertTrue(any("primary_claim" == code or code.startswith("metrics[") for code in missing), missing)
        self.assertIn("gates", report)
        for name in ("evidence", "decision", "visual", "plain_language", "native_table"):
            self.assertIn(name, report["gates"])

    def test_generated_svg_body_text_meets_15px_except_notes(self) -> None:
        spec = self.builder.normalize_page_spec(
            {
                "layout": "gold_cards",
                "title": "重点客户收入回升，但交付缺口仍未关闭",
                "key_message": "收入回升来自续约，缺口在实施交付",
                "typography": {"body_px": 16, "title_px": 32, "source_px": 11},
                "metrics": [
                    {
                        "label": "续约收入",
                        "value": "102%",
                        "note": "财务月报",
                        "evidence_type": "internal_baseline",
                        "claim_type": "fact",
                        "population": "签约客户",
                        "period": "2025",
                        "denominator": "年度目标",
                        "source_ref": "财务月报 p.12",
                        "limitation": "不含渠道库存",
                        "on_metric_label": "内部基线 · 签约客户 · 不含库存",
                    }
                ]
                * 3,
                "groups": [
                    {
                        "title": "续约拉动",
                        "claim": "续约合同贡献了新增收入的六成",
                        "evidence": ["续约 62%", "新客 18%"],
                        "action": "把续约动作写进季度包",
                        "role": "support",
                    },
                    {
                        "title": "交付缺口",
                        "claim": "实施周期仍比承诺长两周",
                        "evidence": ["平均 16 天", "承诺 10 天"],
                        "action": "补齐交付清单 Owner",
                        "role": "evidence",
                    },
                    {
                        "title": "下一步",
                        "claim": "先堵住交付缺口再扩新客",
                        "evidence": ["客户投诉 4 单"],
                        "action": "两周内给出清单",
                        "role": "action",
                    },
                ],
                "sources": ["财务月报"],
            }
        )
        svg = self.builder.build_svg_page(spec)
        from gates.visual import check_svg

        result = check_svg(svg, spec)
        self.assertNotIn("svg_body_font_px", result.missing, result.missing)
        self.assertNotIn("tiny_text_ratio", result.missing, result.missing)


if __name__ == "__main__":
    unittest.main()
