"""Integrity regressions for reference mechanism layouts and component crops."""

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


def _render(ref_id: str, content=None):
    svg, native = RENDERERS[ref_id](content or DEFAULTS[ref_id])
    return ET.fromstring(svg), native


def _role_nodes(root: ET.Element, role: str) -> list[ET.Element]:
    return [node for node in root.iter() if node.get("data-role") == role]


def _layout_role_nodes(root: ET.Element, role: str) -> list[ET.Element]:
    return [node for node in root.iter() if node.get("data-layout-role") == role]


def _text(node: ET.Element) -> str:
    return "".join(node.itertext()).strip()


class ReferenceMechanismIntegrityTests(unittest.TestCase):
    def test_r16_curve_signals_remain_complete_within_panel(self):
        root, _ = _render("R16")
        signal_text = next(node for node in root if _text(node).startswith("分水岭信号｜"))
        lines = [line.text for line in signal_text]
        for signal in DEFAULTS["R16"]["curve_signals"]:
            self.assertTrue(any(signal in line for line in lines), signal)
        bottom = (float(signal_text.get("y"))
                  + sum(float(line.get("dy")) for line in signal_text)
                  + 0.3 * float(signal_text.get("font-size")))
        self.assertLess(bottom, 695)

    def test_r17_component_keeps_all_five_notes_and_native_radar(self):
        component = catalog()["mech-radar-action-loop"]
        root = ET.fromstring(build_scene(component["id"], example(component))[0])
        _, native, report = build_scene(component["id"], example(component))
        self.assertEqual(len(_role_nodes(root, "radar-dimension-note")), 5)
        self.assertEqual(len(native["charts"]), 1)
        excluded_text = [item for item in report["excluded_boundary_elements"] if item["text"].strip()]
        self.assertEqual(excluded_text, [])

        inconsistent = copy.deepcopy(DEFAULTS["R17"])
        inconsistent["radar"]["labels"][4] = "旧维度名"
        with self.assertRaisesRegex(ValueError, "R17 radar labels must match"):
            RENDERERS["R17"](inconsistent)

    def test_r18_component_box_contains_all_seven_icon_discs(self):
        component = catalog()["mech-outcome-backward-seven-steps"]
        _, _, report = build_scene(component["id"], example(component))
        excluded_icons = [item for item in report["excluded_boundary_elements"] if item["tag"] in {"circle", "path"}]
        self.assertEqual(excluded_icons, [])

    def test_r18_gate_rule_has_complete_lines_inside_track(self):
        root, _ = _render("R18")
        rule = next(node for node in root if node.get("x") == "425"
                    and _text(node).replace(" ", "") == "16/20独立完成")
        self.assertTrue(all(len(line.text.strip()) > 1 for line in rule))
        bottom = (float(rule.get("y"))
                  + sum(float(line.get("dy")) for line in rule)
                  + 0.3 * float(rule.get("font-size")))
        self.assertLessEqual(bottom, 698)
        zero_threshold = copy.deepcopy(DEFAULTS["R18"])
        zero_threshold["gates"][0]["rule"] = "0"
        RENDERERS["R18"](zero_threshold)

    def test_r20_component_selects_all_four_native_tables(self):
        component = catalog()["mech-impact-reversibility-matrix"]
        _, native, report = build_scene(component["id"], example(component))
        self.assertEqual(len(native["tables"]), 4)
        self.assertEqual(len(report["native_slots"]), 4)

    def test_r21_good_path_panel_is_painted_before_its_nodes(self):
        root, _ = _render("R21")
        children = list(root)
        title_index = next(i for i, node in enumerate(children) if _text(node) == DEFAULTS["R21"]["good_path"]["title"])
        node_indices = [
            i
            for i, node in enumerate(children)
            if _text(node) in {item["name"] for item in DEFAULTS["R21"]["good_path"]["nodes"]}
        ]
        self.assertTrue(node_indices)
        self.assertLess(title_index, min(node_indices))

    def test_r23_uses_explicit_supported_people_counts_and_complete_graphs(self):
        root, _ = _render("R23")
        self.assertEqual(len(_role_nodes(root, "communication-network-node")), 28)
        edge_groups = _role_nodes(root, "communication-network-edges")
        self.assertEqual([int(node.get("data-edge-count")) for node in edge_groups], [28, 190])
        page_text = [_text(node) for node in root.iter()]
        self.assertIn("8 人｜28 条关系", page_text)
        self.assertIn("20 人｜190 条关系", page_text)

        inconsistent = copy.deepcopy(DEFAULTS["R23"])
        inconsistent["networks"][1]["count"] = 8
        with self.assertRaisesRegex(ValueError, "R23.*8.*20"):
            RENDERERS["R23"](inconsistent)

    def test_r23_formula_explanation_ends_before_metric_cards(self):
        root, _ = _render("R23")
        explanation = next(node for node in root if node.get("x") == "255"
                           and _text(node) == DEFAULTS["R23"]["formula_note"])
        bottom = (float(explanation.get("y"))
                  + sum(float(line.get("dy")) for line in explanation)
                  + 0.3 * float(explanation.get("font-size")))
        metric_card_top = min(float(node.get("y")) for node in root
                              if node.get("width") == "160" and node.get("height") == "142")
        self.assertLess(bottom, metric_card_top)

    def test_r23_explicit_zero_people_cannot_inherit_fixed_network_sizes(self):
        zero_people = copy.deepcopy(DEFAULTS["R23"])
        for network in zero_people["networks"]:
            network["count"] = 0
        with self.assertRaisesRegex(ValueError, "R23.*8.*20"):
            RENDERERS["R23"](zero_people)
        for component in catalog().values():
            if component["reference_id"] == "R23" and "networks" not in component["fields"]:
                build_scene(component["id"], example(component))

    def test_r24_keeps_bilingual_scope_explanations_and_icon_gutter(self):
        root, native = _render("R24")
        self.assertEqual(len(_layout_role_nodes(root, "scope-name")), 6)
        self.assertEqual(len(_layout_role_nodes(root, "scope-explanation")), 6)
        table_slot = _role_nodes(root, "native-table-slot")[0]
        table_x = float(table_slot.get("x"))
        self.assertTrue(all(float(node.get("data-icon-box").split()[0]) >= table_x for node in _role_nodes(root, "mindset-row-icon")))
        self.assertGreaterEqual(native["tables"][0]["column_styles"][0]["margin_left_pt"], 20)

    def test_r26_branch_labels_have_dedicated_clearance(self):
        root, _ = _render("R26")
        branch_labels = _layout_role_nodes(root, "decision-branch-label")
        self.assertEqual(len(branch_labels), 2)
        self.assertTrue(all(node.get("data-clearance") == "dedicated" for node in branch_labels))

    def test_r27_bottom_native_tables_end_before_source_band(self):
        root, native = _render("R27")
        source_y = min(float(node.get("y")) for node in root.iter() if node.get("data-role") == "source")
        bottom_tables = [table for table in native["tables"] if table["slot_id"] in {"r27-anomalies", "r27-thresholds"}]
        self.assertEqual(len(bottom_tables), 2)
        slots = [node for node in _role_nodes(root, "native-table-slot") if node.get("id") in {"r27-anomalies", "r27-thresholds"}]
        self.assertEqual(len(slots), 2)
        self.assertTrue(all(float(node.get("y")) + float(node.get("height")) <= source_y - 8 for node in slots))
        self.assertTrue(all(float(node.get("height")) >= 176 for node in slots))

    def test_r32_memory_rows_clear_notes_and_relation_labels_clear_nodes(self):
        root, _ = _render("R32")
        cards = _layout_role_nodes(root, "memory-card")
        self.assertEqual([node.get("data-color-role") for node in cards], ["blue", "teal", "blue"])
        for key in ("short", "long", "reason"):
            rows = [node for node in _role_nodes(root, "memory-item") if node.get("data-memory-key") == key]
            notes = [node for node in _role_nodes(root, "memory-note-band") if node.get("data-memory-key") == key]
            self.assertEqual(len(notes), 1)
            row_bottom = max(float(node.get("y")) + float(node.get("height")) for node in rows)
            self.assertLessEqual(row_bottom + 8, float(notes[0].get("y")))
        relation_nodes = _role_nodes(root, "relation-node")
        relation_labels = _layout_role_nodes(root, "relation-label")
        self.assertEqual(len(relation_labels), 7)
        for label in relation_labels:
            ly = float(label.get("y"))
            lx = float(label.get("x"))
            same_row = [node for node in relation_nodes if abs(float(node.get("y")) + 13 - ly) < 14]
            self.assertTrue(all(not (float(node.get("x")) <= lx <= float(node.get("x")) + float(node.get("width"))) for node in same_row))

    def test_r32_relation_node_colors_preserve_entity_and_trace_roles(self):
        root, _ = _render("R32")
        nodes = _role_nodes(root, "relation-node")
        self.assertEqual(len(_role_nodes(root, "relation-node-icon")), 10)
        colors = [[node.get("stroke") for node in nodes
                   if node.get("data-relation-row") == str(row)] for row in range(3)]
        self.assertEqual(colors, [
            ["#082B66", "#24846B", "#24846B"],
            ["#082B66", "#65458D", "#65458D", "#082B66"],
            ["#082B66", "#082B66", "#082B66"],
        ])

    def test_r32_memory_note_cannot_wrap_beyond_its_single_line_band(self):
        content = copy.deepcopy(DEFAULTS["R32"])
        content["memories"]["long"]["note"] = "沉淀业务对象、规则与证据来源，持续补齐全局上下文"
        with self.assertRaisesRegex(ValueError, "text exceeds.*capacity"):
            RENDERERS["R32"](content)


if __name__ == "__main__":
    unittest.main()
