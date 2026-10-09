from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SVG_DIR = ROOT / "scripts" / "svg"
if str(SVG_DIR) not in sys.path:
    sys.path.insert(0, str(SVG_DIR))

from gates.native_table import check, is_tabular_content  # noqa: E402


def _columns_rows_spec(**extra):
    spec = {
        "page_role": "content",
        "layout": "gold_cards",
        "columns": ["产品", "部署", "数据驻留"],
        "rows": [
            ["A", "本地", "内网"],
            ["B", "云", "公有云"],
            ["C", "混合", "专有云"],
        ],
    }
    spec.update(extra)
    return spec


def _product_matrix_spec(**extra):
    spec = {
        "page_role": "content",
        "layout": "gold_cards",
        "groups": [
            {"title": "CodeGeeX", "部署": "本地", "数据驻留": "内网", "上下文接入": "IDE"},
            {"title": "Comate", "部署": "本地", "数据驻留": "内网", "上下文接入": "IDE"},
            {"title": "CodeBuddy", "部署": "云", "数据驻留": "公有云", "上下文接入": "插件"},
        ],
    }
    spec.update(extra)
    return spec


def _native_slot():
    return {
        "id": "table-slot-1",
        "box": {"x": 70, "y": 288, "w": 1140, "h": 360},
        "columns": ["产品", "部署", "数据驻留"],
        "rows": [["A", "本地", "内网"]],
        "source": "公开能力综述",
    }


class NativeTableGateTests(unittest.TestCase):
    def test_columns_and_three_rows_without_slot_or_fallback_are_missing(self):
        spec = _columns_rows_spec()
        self.assertTrue(is_tabular_content(spec))
        result = check(spec)
        self.assertIn("native_table_required", result.missing)
        self.assertTrue(result.blocked())

    def test_product_comparison_matrix_is_tabular_and_requires_slot(self):
        spec = _product_matrix_spec()
        self.assertTrue(is_tabular_content(spec))
        result = check(spec)
        self.assertIn("native_table_required", result.missing)

    def test_native_table_slots_with_columns_and_rows_pass(self):
        spec = _columns_rows_spec(native_table_slots=[_native_slot()])
        result = check(spec)
        self.assertEqual(result.missing, [])
        self.assertFalse(result.blocked())

    def test_table_fallback_reason_passes_with_warning(self):
        spec = _columns_rows_spec(table_fallback_reason="列宽不足，保留 SVG 示意表并记录原因")
        result = check(spec)
        self.assertEqual(result.missing, [])
        self.assertTrue(result.warnings)
        self.assertIn("table_fallback_reason", result.warnings)

    def test_cover_page_is_skipped(self):
        spec = _columns_rows_spec(page_role="cover")
        result = check(spec)
        self.assertEqual(result.missing, [])
        self.assertEqual(result.warnings, [])
        self.assertTrue(result.details.get("skipped"))

    def test_gold_evidence_table_without_slot_or_fallback_is_missing(self):
        spec = {
            "page_role": "content",
            "layout": "gold_evidence_table",
            "columns": ["事项", "证据/口径", "影响", "Owner", "状态"],
            "rows": [
                {"cells": ["判断", "来源", "影响", "Owner", "待补"]},
                {"cells": ["动作", "标准", "节奏", "Owner", "跟进"]},
                {"cells": ["风险", "来源", "预案", "Owner", "升级"]},
            ],
        }
        self.assertTrue(is_tabular_content(spec))
        result = check(spec)
        self.assertIn("native_table_required", result.missing)

    def test_two_data_rows_are_not_tabular_on_card_layout(self):
        spec = {
            "page_role": "content",
            "layout": "gold_cards",
            "columns": ["产品", "部署"],
            "rows": [["A", "本地"], ["B", "云"]],
        }
        self.assertFalse(is_tabular_content(spec))
        self.assertEqual(check(spec).missing, [])

    def test_empty_fallback_reason_does_not_pass(self):
        spec = _columns_rows_spec(table_fallback_reason="   ")
        result = check(spec)
        self.assertIn("native_table_required", result.missing)

    def test_section_divider_is_skipped(self):
        spec = _columns_rows_spec(page_role="section_divider")
        result = check(spec)
        self.assertEqual(result.missing, [])
        self.assertTrue(result.details.get("skipped"))


if __name__ == "__main__":
    unittest.main()
