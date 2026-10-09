"""Strict reference-style regression tests for mechanism layouts R16-R30/R32."""

from __future__ import annotations

import copy
import sys
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "svg"))

from reference_layouts.components import build_scene, catalog, example
from reference_layouts.mechanism_layouts import DEFAULTS, RENDERERS


REFS = [*(f"R{number}" for number in range(16, 31)), "R32"]


def _render(ref_id: str):
    svg, native = RENDERERS[ref_id](DEFAULTS[ref_id])
    return ET.fromstring(svg), native


def _local(node: ET.Element) -> str:
    return node.tag.rsplit("}", 1)[-1]


def _text(node: ET.Element) -> str:
    return "".join(node.itertext()).strip()


def _role_nodes(root: ET.Element, role: str) -> list[ET.Element]:
    return [node for node in root.iter() if node.get("data-role") == role]


class ReferenceMechanismStyleTests(unittest.TestCase):
    def test_all_pages_use_explicit_typography_roles_and_real_font_floors(self):
        minimum = {"body": 15.0, "diagram": 12.0, "source": 11.0}
        for ref_id in REFS:
            with self.subTest(ref_id=ref_id):
                root, _ = _render(ref_id)
                texts = [node for node in root.iter() if _local(node) == "text" and _text(node)]
                self.assertTrue(texts)
                for node in texts:
                    role = node.get("data-role")
                    self.assertIn(role, minimum, f"{ref_id} unclassified text: {_text(node)!r}")
                    self.assertGreaterEqual(float(node.get("font-size")), minimum[role])

    def test_r16_to_r20_restore_reference_relationships(self):
        r16, _ = _render("R16")
        self.assertEqual(len(_role_nodes(r16, "vitality-quadrant-divider")), 2)
        self.assertEqual(len(_role_nodes(r16, "vitality-curve-axis")), 2)

        r17, r17_native = _render("R17")
        self.assertEqual(sum(_local(node) == "text" and _text(node) == "VS" for node in r17.iter()), 1)
        columns = _role_nodes(r17, "comparison-column")
        self.assertEqual(len(columns), 2)
        left, right = sorted(columns, key=lambda node: float(node.get("x")))
        self.assertLessEqual(float(right.get("x")) - (float(left.get("x")) + float(left.get("width"))), 25)
        self.assertEqual(len(_role_nodes(r17, "comparison-row-icon")), 10)
        self.assertEqual(len(_role_nodes(r17, "radar-dimension-note")), 5)
        self.assertEqual(len(_role_nodes(r17, "radar-series-legend")), 3)
        self.assertEqual(len(_role_nodes(r17, "action-stage-header")), 3)
        self.assertEqual(len(_role_nodes(r17, "action-body-icon")), 12)
        self.assertEqual(len(_role_nodes(r17, "solid-stage-arrow")), 3)
        self.assertEqual(len(_role_nodes(r17, "voice-return-arrow")), 1)
        self.assertEqual([chart["slot_id"] for chart in r17_native["charts"]], ["r17-radar"])
        radar = r17_native["charts"][0]
        self.assertEqual(
            radar["options"]["value_axis"],
            {"minimum": 0, "maximum": 5, "format": "0.0", "labels": False},
        )
        self.assertEqual(radar["options"]["dashed_series_indices"], [2])
        self.assertFalse(radar["options"]["legend"])
        self.assertFalse(radar["options"]["category_labels"])
        self.assertGreaterEqual(float(_role_nodes(r17, "native-chart-slot")[0].get("width")), 240)
        comparison_bodies = [
            node
            for node in r17.iter()
            if _local(node) == "text"
            and node.get("data-role") == "body"
            and float(node.get("x")) < 624
            and 330 <= float(node.get("y")) <= 680
        ]
        self.assertGreaterEqual(len(comparison_bodies), 10)

        r18, _ = _render("R18")
        self.assertEqual(len(_role_nodes(r18, "dashed-system-frame")), 2)
        self.assertEqual(len(_role_nodes(r18, "system-summary-strip")), 2)
        self.assertEqual(len(_role_nodes(r18, "document-paper")), 1)
        self.assertEqual(len(_role_nodes(r18, "continuous-gate-track")), 1)

        r19, _ = _render("R19")
        self.assertEqual(len(_role_nodes(r19, "continuous-comparison-row")), 3)
        self.assertEqual(len(_role_nodes(r19, "continuous-lever-row")), 4)
        self.assertEqual(len(_role_nodes(r19, "flywheel-arc")), 8)
        self.assertEqual(len(_role_nodes(r19, "formula-result")), 1)
        self.assertIn("=", [_text(node) for node in r19.iter()])

        r20, r20_native = _render("R20")
        self.assertEqual(len(r20_native["tables"]), 4)
        self.assertEqual(len(_role_nodes(r20, "shared-matrix-axis")), 2)
        self.assertEqual(len(_role_nodes(r20, "process-step-icon")), 5)
        self.assertEqual(len(_role_nodes(r20, "matrix-row-icon")), 20)

    def test_r21_to_r26_restore_dense_panels_and_navigation(self):
        r21, _ = _render("R21")
        self.assertEqual(len(_role_nodes(r21, "path-node-panel")), 8)
        self.assertEqual(len(_role_nodes(r21, "rule-line")), 8)
        self.assertEqual(len(_role_nodes(r21, "arrow-closing-band")), 1)

        r22, _ = _render("R22")
        self.assertEqual(len(_role_nodes(r22, "swimlane-background")), 2)
        self.assertGreaterEqual(len(_role_nodes(r22, "swimlane-divider")), 10)
        self.assertEqual(len(_role_nodes(r22, "charter-column")), 5)

        r23, _ = _render("R23")
        self.assertEqual(sum(_local(node) == "text" and _text(node) == "VS" for node in r23.iter()), 1)
        self.assertEqual(len(_role_nodes(r23, "network-header")), 2)
        self.assertEqual(len(_role_nodes(r23, "principle-icon")), 5)
        self.assertIn("28", [_text(node) for node in r23.iter()])
        self.assertIn("190", [_text(node) for node in r23.iter()])

        r24, r24_native = _render("R24")
        self.assertEqual(len(_role_nodes(r24, "journey-step-icon")), 6)
        self.assertEqual(len(_role_nodes(r24, "mindset-row-icon")), 5)
        self.assertEqual(len(_role_nodes(r24, "journey-direction-band")), 1)
        self.assertEqual([table["slot_id"] for table in r24_native["tables"]], ["r24-mindset"])

        r25, r25_native = _render("R25")
        self.assertEqual(len(_role_nodes(r25, "input-arrow-node")), 6)
        self.assertEqual([table["slot_id"] for table in r25_native["tables"]], ["r25-metrics"])

        r26, _ = _render("R26")
        self.assertEqual(len(_role_nodes(r26, "strong-quadrant-icon")), 4)
        self.assertEqual(len(_role_nodes(r26, "guardrail-column")), 4)

    def test_r27_to_r32_preserve_native_data_and_strict_visual_structure(self):
        r27, r27_native = _render("R27")
        trends = [chart for chart in r27_native["charts"] if chart["slot_id"].startswith("r27-trend-")]
        self.assertEqual(len(trends), 5)
        self.assertTrue(all(chart["options"].get("sparkline") is True for chart in trends))
        self.assertTrue(all(len(chart["labels"]) == 6 for chart in trends))
        self.assertEqual(len(_role_nodes(r27, "mechanism-right-icon")), 6)

        r28, r28_native = _render("R28")
        self.assertEqual(len(_role_nodes(r28, "paper-fold")), 2)
        self.assertEqual(len(_role_nodes(r28, "compare-row-icon")), 4)
        self.assertEqual(len(_role_nodes(r28, "meeting-step-panel")), 4)
        self.assertEqual([table["slot_id"] for table in r28_native["tables"]], ["r28-compare"])

        r29, _ = _render("R29")
        self.assertEqual(len(_role_nodes(r29, "matrix-row-header")), 2)
        self.assertEqual(len(_role_nodes(r29, "matrix-column-header")), 2)
        markers = _role_nodes(r29, "score-marker")
        self.assertEqual(len(markers), 5)
        self.assertTrue(all(node.get("x1") == node.get("x2") for node in markers))
        self.assertEqual(len(_role_nodes(r29, "score-trial-marker")), 5)
        custom_r29 = copy.deepcopy(DEFAULTS["R29"])
        custom_r29["option_names"] = ["方案甲", "方案乙"]
        custom_root = ET.fromstring(RENDERERS["R29"](custom_r29)[0])
        custom_text = [_text(node) for node in custom_root.iter() if _local(node) == "text"]
        self.assertIn("橙=方案甲｜蓝=方案乙", custom_text)
        self.assertNotIn("橙=直接扩建｜蓝=可逆试点", custom_text)
        self.assertEqual(len(_role_nodes(r29, "probability-branch")), 4)

        r30, r30_native = _render("R30")
        self.assertGreaterEqual(len(_role_nodes(r30, "principle-ring")), 2)
        self.assertEqual(len(_role_nodes(r30, "principle-ring-node")), 6)
        self.assertEqual(len(_role_nodes(r30, "lifecycle-step-icon")), 6)
        self.assertEqual(len(_role_nodes(r30, "principle-table-icon")), 6)
        self.assertEqual(len(_role_nodes(r30, "lifecycle-direction-band")), 1)
        self.assertEqual([table["slot_id"] for table in r30_native["tables"]], ["r30-mechanisms"])

        r32, _ = _render("R32")
        self.assertEqual((r32.get("width"), r32.get("height")), ("1080", "720"))
        self.assertEqual(len(_role_nodes(r32, "memory-note-band")), 3)
        self.assertEqual(len(_role_nodes(r32, "core-idea-icon")), 1)
        self.assertEqual(len(_role_nodes(r32, "pipeline-mainline")), 1)

    def test_all_34_mechanism_components_compile_from_declared_boxes(self):
        components = {
            component_id: component
            for component_id, component in catalog().items()
            if component_id.startswith("mech-")
        }
        self.assertEqual(len(components), 34)
        for component_id, component in components.items():
            with self.subTest(component_id=component_id):
                self.assertEqual(component["capacity"]["body_font_size_px"], 15)
                self.assertEqual(component["capacity"]["dense_label_font_size_px"], 12)
                self.assertEqual(component["capacity"]["source_font_size_px"], 11)
                svg, native, report = build_scene(component_id, example(component))
                root = ET.fromstring(svg)
                self.assertTrue(list(root), "component export is visually empty")
                self.assertEqual(report["component_id"], component_id)
                self.assertEqual(report["data_fields"], component["fields"])
                slot_ids = [item["slot_id"] for kind in ("charts", "tables") for item in native[kind]]
                self.assertEqual(len(slot_ids), len(set(slot_ids)))

        self.assertEqual(components["mech-five-dimension-inside-outside-comparison"]["capacity"]["global_vs"], 1)
        self.assertEqual(components["mech-radar-action-loop"]["capacity"]["action_body_icons"], 12)
        self.assertEqual(components["mech-impact-reversibility-matrix"]["capacity"]["shared_axes"], 2)
        self.assertEqual(components["mech-wbr-main-table-trends"]["capacity"]["native_sparklines"], 5)
        self.assertEqual(components["mech-six-principle-network"]["capacity"]["ring_nodes"], 6)


if __name__ == "__main__":
    unittest.main()
