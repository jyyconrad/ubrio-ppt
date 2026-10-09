"""Picture contract: declared dominant must show up in the SVG."""
from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "svg" / "check_shape_picture.py"


def load_checker():
    spec = importlib.util.spec_from_file_location("check_shape_picture", SCRIPT)
    if spec is None or spec.loader is None:
        raise FileNotFoundError(SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


COMPARE_TABLE = """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1280 720">
  <text x="58" y="54">先堆工具和先定用法，不是同一条路</text>
  <g id="path-table" data-role="native-table-slot" data-native-table="true" data-x="48" data-y="140" data-w="1180" data-h="360">
    <rect x="48" y="140" width="1180" height="360" fill="none"/>
  </g>
</svg>
"""

COMPARE_PANELS = """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1280 720">
  <g data-role="comparison-panel" data-x="48" data-y="140" data-w="560" data-h="360">
    <rect x="48" y="140" width="560" height="360" fill="#F4F7FB"/>
    <text x="72" y="190">先堆工具</text>
    <text x="72" y="240">成绩看成了采纳了多少建议。</text>
  </g>
  <g data-role="comparison-panel" data-x="672" data-y="140" data-w="560" data-h="360">
    <rect x="672" y="140" width="560" height="360" fill="#E7EEF6"/>
    <text x="696" y="190">先定用法</text>
    <text x="696" y="240">成绩看成验收记录齐不齐。</text>
  </g>
</svg>
"""

STAGE_NAMES = """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1280 720">
  <g data-role="process-step"><text x="80" y="160">需求澄清</text></g>
  <g data-role="process-step"><text x="280" y="160">方案设计</text></g>
  <g data-role="process-step"><text x="480" y="160">编码实现</text></g>
</svg>
"""

STAGE_SENTENCES = """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1280 720">
  <g data-role="process-step"><text x="80" y="160">需求澄清还没有同一份任务单。</text></g>
  <g data-role="process-step"><text x="280" y="160">方案设计没写不做的范围。</text></g>
  <g data-role="process-step"><text x="480" y="160">编码实现指不回上一张单。</text></g>
</svg>
"""

TOP_HEAVY = """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1280 720">
  <g data-role="evidence-panel">
    <rect x="40" y="120" width="280" height="420" fill="#F4F7FB"/>
    <text x="60" y="160">快 55.8%</text>
  </g>
</svg>
"""

FILLED_PANEL = """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1280 720">
  <g data-role="evidence-panel">
    <rect x="40" y="120" width="280" height="420" fill="#F4F7FB"/>
    <text x="60" y="170">快 55.8%</text>
    <text x="60" y="250">同一 JS 任务，处理 71 分钟。</text>
    <text x="60" y="400">不能外推到整段交付。</text>
  </g>
</svg>
"""


class ShapePictureTests(unittest.TestCase):
    def test_comparison_table_alone_is_not_a_left_right_shape(self):
        missing = load_checker().check_shape_picture("左右对照", COMPARE_TABLE)
        self.assertIn("comparison_collapsed_to_table", missing)

    def test_two_comparison_panels_pass(self):
        self.assertEqual(load_checker().check_shape_picture("左右对照", COMPARE_PANELS), [])

    def test_process_steps_need_a_sentence(self):
        missing = load_checker().check_shape_picture("流程断点", STAGE_NAMES)
        self.assertIn("process_step_sentence", missing)
        self.assertEqual(load_checker().check_shape_picture("流程断点", STAGE_SENTENCES), [])

    def test_evidence_panel_cannot_leave_the_lower_half_empty(self):
        missing = load_checker().check_shape_picture("不可比证据", TOP_HEAVY)
        self.assertIn("panel_text_top_heavy", missing)
        self.assertEqual(load_checker().check_shape_picture("不可比证据", FILLED_PANEL), [])


if __name__ == "__main__":
    unittest.main()
