"""Component captions retain exact business context without changing the diagram."""

import sys
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "svg"))
import build_component
from reference_layouts.common import Svg


class ComponentEvidenceContextTests(unittest.TestCase):
    def test_context_is_separate_business_data_and_preserves_complete_year(self):
        original = {"results": ["explicit data"], "evidence_context": {
            "period": "2026年8月至9月", "population": "1000单合成订单",
            "source": "授权合成履约台账", "limitation": "合成演示，不代表真实经营成效"}}
        data, context = build_component.split_context(original)
        self.assertEqual(data, {"results": ["explicit data"]})
        self.assertIn("evidence_context", original)
        scene = Svg()
        scene.rect(30, 260, 1220, 180)
        source, _ = scene.finish()
        changed = build_component.attach_context(source, context, baseline=465)
        before, after = ET.fromstring(source), ET.fromstring(changed)
        self.assertEqual(before[0].attrib, after[0].attrib)
        text = "\n".join("".join(node.itertext()) for node in after if node.tag.endswith("text"))
        for value in context.values():
            self.assertIn(value, text)
        self.assertEqual(after.get("viewBox"), before.get("viewBox"))
        for node in after:
            if node.tag.endswith("text"):
                self.assertEqual(node.get("font-size"), "11")
                self.assertEqual(node.get("data-role"), "source")

    def test_context_rejects_missing_fields_and_layout_controls(self):
        with self.assertRaisesRegex(ValueError, "requires evidence_context"):
            build_component.split_context({"results": ["explicit data"]})
        context = {"period": "2026年9月", "population": "30位合成客户",
                   "source": "授权合成回访", "limitation": "不代表总体"}
        for field in context:
            with self.subTest(field=field):
                with self.assertRaisesRegex(ValueError, "evidence_context"):
                    build_component.split_context({"evidence_context": {
                        key: value for key, value in context.items() if key != field}})
        with self.assertRaisesRegex(ValueError, "evidence_context"):
            build_component.split_context({"evidence_context": {**context, "font_size": 8}})

    def test_caption_over_capacity_fails_without_shrinking_or_truncating(self):
        scene = Svg()
        source, _ = scene.finish()
        with self.assertRaisesRegex(ValueError, "capacity"):
            build_component.attach_context(source, {
                "period": "2026年9月", "population": "合成客户" * 80,
                "source": "授权合成回访", "limitation": "不代表总体"}, baseline=650)


if __name__ == "__main__":
    unittest.main()
