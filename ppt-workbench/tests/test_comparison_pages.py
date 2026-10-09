import copy
import importlib.util
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_module(name, relative):
    module_spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    module = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(module)
    return module


class ComparisonRegressionTests(unittest.TestCase):
    def setUp(self):
        self.builder = load_module("comparison_builder", "scripts/svg/build_gold_svg_page.py")
        self.checker = load_module("comparison_checker", "scripts/svg/check_shape_picture.py")
        fixture = load_module("gold_fixture", "tests/test_gold_pages.py")
        self.spec = copy.deepcopy(fixture.READY_SPEC)
        self.spec.update(dominant="左右对照", metrics=[], native_chart_slots=[])
        self.spec["boundary"] = "合成测试数据，不代表企业实际表现。"
        self.spec["groups"] = self.spec["groups"][:2]

    def test_comparison_does_not_invent_metrics_or_third_group(self):
        normalized = self.builder.normalize_page_spec(self.spec)
        self.assertEqual(normalized["metrics"], [])
        self.assertEqual(len(normalized["groups"]), 2)

    def test_gold_builder_draws_the_declared_comparison(self):
        svg = self.builder.build_svg_page(self.spec)
        self.assertEqual(self.checker.check_shape_picture("左右对照", svg), [])
        root = ET.fromstring(svg)
        panels = [node for node in root.iter() if node.get("data-role") == "comparison-panel"]
        self.assertEqual(len(panels), 2)
        self.assertFalse(any(node.get("id") == "metrics-panel" for node in root.iter()))

    def test_one_empty_panel_does_not_borrow_the_other_sentence(self):
        fixture = load_module("shape_fixture", "tests/test_shape_picture.py")
        root = ET.fromstring(fixture.COMPARE_PANELS)
        panels = [node for node in root.iter() if node.get("data-role") == "comparison-panel"]
        first_texts = [node for node in panels[0] if node.tag.endswith("text")]
        first_texts[0].text = "左侧也有一句完整判断。"
        for node in list(panels[1]):
            if node.tag.endswith("text"):
                panels[1].remove(node)
        self.assertTrue(self.checker.check_shape_picture("左右对照", ET.tostring(root, encoding="unicode")))

    def test_stacked_panels_are_not_left_right_comparison(self):
        fixture = load_module("shape_fixture", "tests/test_shape_picture.py")
        root = ET.fromstring(fixture.COMPARE_PANELS)
        panels = [node for node in root.iter() if node.get("data-role") == "comparison-panel"]
        panels[1].set("data-x", "48")
        panels[1].set("data-y", "520")
        for node in panels[1]:
            if node.tag.endswith("rect"):
                node.set("x", "48")
                node.set("y", "520")
        self.assertTrue(self.checker.check_shape_picture("左右对照", ET.tostring(root, encoding="unicode")))

    def test_template_matches_the_comparison_layout(self):
        template = self.builder.build_page_spec_template(layout="gold_comparison")
        normalized = self.builder.normalize_page_spec(template)
        self.assertEqual(normalized["metrics"], [])
        self.assertEqual(len(normalized["groups"]), 2)
        self.assertEqual(normalized["dominant"], "左右对照")

    def test_declared_font_reaches_svg_text(self):
        self.spec["typography"]["font_family"] = "PingFang SC"
        root = ET.fromstring(self.builder.build_svg_page(self.spec))
        texts = [node for node in root.iter() if node.tag.endswith("text")]
        self.assertTrue(texts)
        self.assertTrue(all(node.get("font-family") == "PingFang SC" for node in texts))

    def test_explicit_zero_metrics_does_not_disable_evidence_checks(self):
        fixture = load_module("gold_fixture", "tests/test_gold_pages.py")
        spec = copy.deepcopy(fixture.READY_SPEC)
        spec["quality_targets"] = {"metrics_min": 0}
        spec["metrics"][0]["source_ref"] = ""
        normalized = self.builder.normalize_page_spec(spec)
        self.assertIn("metrics[0].source_ref", self.builder.quality_report(normalized)["missing"])

    def test_extra_group_and_long_text_are_not_silently_dropped(self):
        self.spec["groups"].append(copy.deepcopy(self.spec["groups"][0]))
        self.spec["groups"][0]["claim"] = "长句" * 40
        missing = self.builder.quality_report(self.builder.normalize_page_spec(self.spec))["missing"]
        self.assertIn("comparison_requires_two_groups", missing)
        self.assertIn("groups[0].claim.comparison_capacity", missing)
        with self.assertRaises(ValueError):
            self.builder.build_svg_page(self.spec)

    def test_wrapped_tspan_sentences_are_supported(self):
        fixture = load_module("shape_fixture", "tests/test_shape_picture.py")
        root = ET.fromstring(fixture.COMPARE_PANELS)
        for node in root.iter():
            if node.tag.endswith("text"):
                value = node.text
                node.text = None
                ET.SubElement(node, "{http://www.w3.org/2000/svg}tspan").text = value
        self.assertEqual(self.checker.check_shape_picture("左右对照", ET.tostring(root, encoding="unicode")), [])

    def test_overlapping_panels_are_rejected(self):
        fixture = load_module("shape_fixture", "tests/test_shape_picture.py")
        root = ET.fromstring(fixture.COMPARE_PANELS)
        panels = [node for node in root.iter() if node.get("data-role") == "comparison-panel"]
        next(node for node in panels[1] if node.tag.endswith("rect")).set("x", "200")
        self.assertIn("comparison_not_side_by_side", self.checker.check_shape_picture("左右对照", ET.tostring(root, encoding="unicode")))


if __name__ == "__main__":
    unittest.main()
