"""Focused visual-contract checks for the editable R01-R15 layouts."""

from __future__ import annotations

import json
import re
from copy import deepcopy
import sys
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "svg"))

from reference_layouts import rd_layouts  # noqa: E402
from reference_layouts.components import build_scene, catalog, example  # noqa: E402
from build_reference_page import resources  # noqa: E402
from drawingml.input_gate import validate_svg_input  # noqa: E402


NS = {"svg": "http://www.w3.org/2000/svg"}
DENSE_ROLES = {"axis", "chart", "diagram", "flow", "legend", "plot", "process", "step", "timeline"}
SOURCE_ROLES = {"citation", "evidence-source", "footnote", "source-note", "source"}


def _root(reference_id: str) -> tuple[ET.Element, dict]:
    svg, native = rd_layouts.RENDERERS[reference_id]()
    return ET.fromstring(svg), native


def _texts(root: ET.Element) -> list[ET.Element]:
    return root.findall(".//svg:text", NS)


def _plain_text(node: ET.Element) -> str:
    return "".join(node.itertext()).strip()


def _matching_text(root: ET.Element, value: str) -> list[ET.Element]:
    return [node for node in _texts(root) if _plain_text(node) == value]


class ReferenceRdStyleTests(unittest.TestCase):
    def test_six_chart_dashboard_rejects_long_categories_before_render(self):
        content = deepcopy(rd_layouts.DEFAULTS["R10"])
        content["chart_groups"][0]["items"][0]["labels"][0] = "测试保留版本"
        with self.assertRaisesRegex(ValueError, "category.*capacity"):
            rd_layouts.render_r10(content)
        content = deepcopy(rd_layouts.DEFAULTS["R10"])
        content["chart_groups"][0]["items"][0]["target_category"] = "复盘异常闭环"
        with self.assertRaisesRegex(ValueError, "category.*capacity"):
            rd_layouts.render_r10(content)

    def test_plain_component_placeholders_do_not_trigger_before_after_parsing(self):
        content = deepcopy(rd_layouts.DEFAULTS["R04"])
        for item in content["results"]:
            item["value"] = "待填数值"
        root = ET.fromstring(rd_layouts.render_r04(content)[0])
        placeholders = _matching_text(root, "待填数值")
        self.assertEqual(len(placeholders), 5)
        self.assertTrue(all(float(node.attrib["font-size"]) == 28 for node in placeholders))

    def test_r10_declares_shared_two_line_source_band(self):
        self.assertEqual(rd_layouts.SCHEMAS["R10"]["source_band"], {
            "x": 32, "y": 470, "w": 1216, "h": 26,
            "max_lines": 2, "font_size": 11,
        })
        root, _ = _root("R10")
        heading = _matching_text(root, rd_layouts.DEFAULTS["R10"]["diagnosis_heading"])[0]
        self.assertGreaterEqual(float(heading.attrib["y"]), 528)

    def test_r31_crop_has_no_shape_crossing_the_640_canvas(self):
        renderers, defaults, schemas = resources()
        svg = renderers["R31"](defaults["R31"])[0]
        root = ET.fromstring(svg)
        self.assertEqual(schemas["R31"]["source_band"], rd_layouts.SCHEMAS["R10"]["source_band"])
        for polygon in root.findall(".//svg:polygon", NS):
            bottom = max(float(point.split(",")[1]) for point in polygon.attrib["points"].split())
            self.assertLessEqual(bottom, 640)
        gate = validate_svg_input(svg, page_archetype="content")
        blocking_codes = {issue["code"] for issue in gate.blocking_issues}
        self.assertNotIn("SVG_CONTENT_BOUNDS_OVERFLOW", blocking_codes)
        self.assertNotIn("SVG_TEXT_OVERLAP", blocking_codes)

    def test_all_fifteen_pages_use_role_accurate_readable_type(self):
        for reference_id in rd_layouts.RENDERERS:
            with self.subTest(reference_id=reference_id):
                root, _ = _root(reference_id)
                offenders = []
                for node in _texts(root):
                    size = float(node.attrib["font-size"])
                    role = (node.attrib.get("data-role") or "body").lower()
                    if any(token in role for token in SOURCE_ROLES):
                        minimum = 11.0
                    elif any(token in role for token in DENSE_ROLES):
                        minimum = 12.0
                    else:
                        minimum = 15.0
                    if size < minimum:
                        offenders.append((_plain_text(node), size, role, minimum))
                self.assertEqual(offenders, [])

    def test_page_specific_reference_structures_are_restored(self):
        r02, _ = _root("R02")
        lobe_colors = {"#0D59C4", rd_layouts.TEAL, "#0A438E"}
        responsibility_polygons = [node for node in r02.findall(".//svg:polygon", NS)
                                   if node.attrib.get("fill") in lobe_colors
                                   and node.attrib.get("stroke") == rd_layouts.WHITE]
        self.assertEqual(len(responsibility_polygons), 3)
        coordinates = [tuple(float(value) for value in pair.split(","))
                       for node in responsibility_polygons
                       for pair in node.attrib["points"].split()]
        self.assertLessEqual(max(x for x, _ in coordinates) - min(x for x, _ in coordinates), 330)
        self.assertLessEqual(max(y for _, y in coordinates), 560)
        center_holes = [node for node in r02.findall(".//svg:polygon", NS)
                        if node.attrib.get("fill") == rd_layouts.WHITE
                        and len(node.attrib["points"].split()) == 3]
        self.assertEqual(len(center_holes), 1)
        self.assertTrue(any(float(node.attrib.get("width", 0)) >= 700 and float(node.attrib.get("height", 0)) == 225
                            for node in r02.findall(".//svg:rect", NS)))

        r03, _ = _root("R03")
        for stage in rd_layouts.DEFAULTS["R03"]["stages"]:
            focus = _matching_text(r03, stage["focus"])
            self.assertEqual(len(focus), 1)
            self.assertGreaterEqual(float(focus[0].attrib["font-size"]), 28)

        r04, _ = _root("R04")
        for item in rd_layouts.DEFAULTS["R04"]["results"]:
            before, after = [part.strip() for part in item["value"].split("→", 1)]
            self.assertTrue(any(before in _plain_text(node) and node.attrib["fill"] == rd_layouts.GREY
                                for node in _texts(r04)))
            after_number = re.match(r"([+\-≤≥]?\d[\d,.]*)", after).group(1)
            after_nodes = [node for node in _texts(r04) if after_number == _plain_text(node)]
            self.assertTrue(after_nodes)
            self.assertGreaterEqual(max(float(node.attrib["font-size"]) for node in after_nodes), 28)
            self.assertGreaterEqual(min(float(node.attrib["y"]) for node in after_nodes), 572)
        insight_bands = [node for node in r04.findall(".//svg:rect", NS)
                         if node.attrib.get("fill") == rd_layouts.LIGHT
                         and 34 <= float(node.attrib.get("height", 0)) <= 40
                         and float(node.attrib.get("y", 0)) >= 580]
        self.assertEqual(len(insight_bands), 5)
        for item in rd_layouts.DEFAULTS["R04"]["actions"]:
            self.assertGreaterEqual(
                sum(len(item[field]) for field in ("input", "action", "output")), 20
            )

        metric_values = [item["value"] for group in rd_layouts.DEFAULTS["R06"]["metric_groups"]
                         for item in group["items"] if item.get("value")]
        self.assertEqual(len(metric_values), 1)

        r07, _ = _root("R07")
        for expected_number in ("26", "≤12"):
            focus_nodes = _matching_text(r07, expected_number)
            self.assertEqual(len(focus_nodes), 1)
            self.assertGreaterEqual(float(focus_nodes[0].attrib["font-size"]), 28)

        r09, _ = _root("R09")
        vertical_bars = [node for node in r09.findall(".//svg:rect", NS)
                         if float(node.attrib.get("width", 0)) == 6]
        self.assertGreaterEqual(len(vertical_bars), 2)

        r10, _ = _root("R10")
        insight_icons = [node for node in r10.findall(".//svg:g", NS)
                         if node.attrib.get("data-icon-id") == "lightbulb"]
        self.assertEqual(len(insight_icons), 6)
        for value in ("83", "90", "≤15", "1.0", "0.8"):
            focus_nodes = _matching_text(r10, value)
            self.assertTrue(focus_nodes, value)
            self.assertTrue(any(float(node.attrib["font-size"]) >= 20
                                and node.attrib.get("fill") == rd_layouts.BLUE
                                for node in focus_nodes), value)
        diagnosis_polygons = [node for node in r10.findall(".//svg:polygon", NS)
                              if max(float(pair.split(",")[1]) for pair in node.attrib["points"].split()) >= 685]
        self.assertGreaterEqual(len(diagnosis_polygons), 5)
        for node in diagnosis_polygons[:5]:
            points = [(float(pair.split(",")[0]), float(pair.split(",")[1]))
                      for pair in node.attrib["points"].split()]
            top = [x for x, y in points if y == min(point[1] for point in points)]
            bottom = [x for x, y in points if y == max(point[1] for point in points)]
            self.assertGreater((max(top) - min(top)) - (max(bottom) - min(bottom)), 35)
        diagnosis_icons = [node for node in r10.findall(".//svg:g", NS)
                           if node.attrib.get("data-icon-id")
                           in {item["icon"] for item in rd_layouts.DEFAULTS["R10"]["diagnosis"]}]
        self.assertEqual(len(diagnosis_icons), 5)
        for index, icon in enumerate(diagnosis_icons):
            x, y, w, h = [float(value) for value in icon.attrib["data-icon-box"].split()]
            self.assertEqual((w, h), (40, 40))
            self.assertAlmostEqual(x + w / 2, 26 + index * 196 + 90)
            self.assertLessEqual(y + h, 632)
        centered_diagnosis_lines = [
            node for node in _texts(r10)
            if node.attrib.get("text-anchor") == "middle"
            and float(node.attrib.get("y", 0)) >= 650
            and any(abs(float(node.attrib["x"]) - (26 + index * 196 + 90)) < 0.1
                    for index in range(5))
        ]
        self.assertEqual(len(centered_diagnosis_lines), 10)

        r12, native12 = _root("R12")
        self.assertFalse(native12["tables"][0]["show_header"])
        grey_level_blocks = [node for node in r12.findall(".//svg:polygon", NS)
                             if node.attrib.get("fill") == rd_layouts.PALE
                             and max(float(pair.split(",")[1]) for pair in node.attrib["points"].split()) < 264]
        self.assertEqual(len(grey_level_blocks), 3)
        action_number_blocks = [node for node in r12.findall(".//svg:rect", NS)
                                if node.attrib.get("fill") == rd_layouts.BLUE
                                and float(node.attrib.get("width", 0)) == 42
                                and float(node.attrib.get("height", 0)) == 38]
        self.assertEqual(len(action_number_blocks), 3)
        result_icons = [node for node in r12.findall(".//svg:g", NS)
                        if node.attrib.get("data-icon-box", "").split()[1:2] == ["534"]]
        self.assertEqual(len(result_icons), 3)
        self.assertTrue(all(node.attrib["data-icon-box"].split()[2:] == ["52", "52"]
                            for node in result_icons))

        r13, _ = _root("R13")
        for stage in rd_layouts.DEFAULTS["R13"]["flow"]:
            node = _matching_text(r13, stage["label"])[0]
            self.assertGreater(float(node.attrib["y"]), 200)
        flow_polygons = [node for node in r13.findall(".//svg:polygon", NS)
                         if min(float(pair.split(",")[1]) for pair in node.attrib["points"].split()) == 130]
        flow_starts = sorted(min(float(pair.split(",")[0]) for pair in node.attrib["points"].split())
                             for node in flow_polygons[:7])
        self.assertEqual([round(b - a) for a, b in zip(flow_starts, flow_starts[1:])], [170] * 6)
        for result in rd_layouts.DEFAULTS["R13"]["results"]:
            after = result["value"].split("→", 1)[1]
            after_number = re.match(r"([+\-≤≥]?\d[\d,.]*)", after).group(1)
            value_nodes = _matching_text(r13, after_number)
            self.assertTrue(value_nodes)
            self.assertGreaterEqual(max(float(node.attrib["font-size"]) for node in value_nodes), 30)

        r14, _ = _root("R14")
        bottom_bands = [node for node in r14.findall(".//svg:rect", NS)
                        if float(node.attrib.get("y", 0)) == 623 and float(node.attrib.get("height", 0)) == 75]
        self.assertTrue(bottom_bands)

        r15, _ = _root("R15")
        for target in rd_layouts.DEFAULTS["R15"]["targets"]:
            node = _matching_text(r15, target["value"])[0]
            self.assertGreaterEqual(float(node.attrib["font-size"]), 23)

    def test_component_catalog_tracks_complete_revised_panels(self):
        path = ROOT / "assets" / "components" / "blue-dense" / "rd-components.json"
        items = json.loads(path.read_text(encoding="utf-8"))["components"]
        self.assertEqual(len(items), 26)
        by_id = {item["id"]: item for item in items}
        expected_boxes = {
            "rd-value-staircase-3": [38, 100, 1144, 278],
            "rd-responsibility-tri-loop": [34, 110, 455, 507],
            "rd-mechanism-2x3-grid": [515, 112, 730, 473],
            "rd-three-stage-execution-roadmap": [40, 145, 1200, 550],
            "rd-four-action-chain": [60, 230, 1160, 191],
            "rd-five-metric-result-row": [60, 431, 1160, 195],
            "rd-four-issue-diagnosis-matrix": [48, 129, 1184, 550],
            "rd-metric-definition-3x3": [48, 126, 1190, 294],
            "rd-three-tool-evidence-cards": [48, 438, 1190, 240],
            "rd-dual-metric-systems": [50, 108, 1195, 292],
            "rd-four-step-case-funnel": [50, 425, 1195, 255],
            "rd-cost-method-metric-stack": [35, 103, 1211, 365],
            "rd-cost-case-ledger": [35, 473, 1211, 207],
            "rd-one-store-three-platforms": [42, 100, 1152, 397],
            "rd-six-chart-metric-dashboard": [24, 90, 1232, 379],
            "rd-five-layer-diagnosis-chain": [22, 503, 1235, 201],
            "rd-four-function-strip": [40, 105, 757, 193],
            "rd-mode-transition-comparison": [42, 303, 755, 311],
            "rd-three-level-module-pyramid": [38, 89, 1192, 175],
            "rd-root-action-evidence-pair": [35, 289, 1210, 202],
            "rd-seven-stage-process-axis": [35, 90, 1225, 198],
            "rd-parallel-late-change-evidence": [35, 296, 1210, 168],
            "rd-environment-main-chart-evidence": [42, 112, 1194, 270],
            "rd-four-bottleneck-row": [42, 394, 1196, 229],
            "rd-roof-wings-four-layers": [232, 125, 696, 435],
            "rd-dual-collaboration-loops": [944, 136, 318, 424],
        }
        self.assertEqual(set(by_id), set(expected_boxes))
        for component_id, box in expected_boxes.items():
            with self.subTest(component_id=component_id):
                self.assertEqual(by_id[component_id]["box"], box)
                self.assertTrue(by_id[component_id]["fields"])
                self.assertTrue(by_id[component_id]["capacity"])

    def test_all_rd_components_extract_without_boundary_loss(self):
        for component_id, component in catalog().items():
            if not component_id.startswith("rd-"):
                continue
            with self.subTest(component_id=component_id):
                _, _, report = build_scene(component_id, example(component))
                self.assertEqual(report["excluded_boundary_elements"], [])


if __name__ == "__main__":
    unittest.main()
