import copy
import importlib.util
import json
import re
import sys
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ComparisonCapacityTests(unittest.TestCase):
    def setUp(self):
        module_spec = importlib.util.spec_from_file_location('comparison_capacity_builder', ROOT / 'scripts/svg/build_gold_svg_page.py')
        self.builder = importlib.util.module_from_spec(module_spec)
        module_spec.loader.exec_module(self.builder)
        text = (ROOT / 'references/generate/methods/gold-pages.md').read_text()
        self.spec = json.loads(re.search(r'```json\n(.*?)\n```', text, re.S).group(1))

    def test_four_evidence_items_are_rejected_instead_of_dropped(self):
        self.spec['groups'][0]['evidence'] = ['第一条依据。', '第二条依据。', '第三条依据。', '不能消失的第四条依据。']
        report = self.builder.quality_report(self.builder.normalize_page_spec(self.spec))
        self.assertNotEqual(report['quality_status'], 'ready')

    def test_five_line_evidence_is_rejected_instead_of_truncated(self):
        self.spec['groups'][0]['evidence'] = ['证据内容' * 27, '另一条短依据。']
        report = self.builder.quality_report(self.builder.normalize_page_spec(self.spec))
        self.assertNotEqual(report['quality_status'], 'ready')

    def test_worked_example_uses_the_existing_reference_contract(self):
        self.assertTrue(all(isinstance(item, dict) and all(item.get(key) for key in ['example_id', 'source', 'reuse_reason', 'adaptations']) for item in self.spec['example_refs']))

    def test_evidence_metadata_does_not_turn_panels_into_a_table(self):
        for group in self.spec['groups']:
            group.update(claim_type='proposal', evidence_type='provided_material', evidence_state='PROPOSAL', source_ref='input.md', population='研发团队', period='未定', denominator='不适用', limitation='无内部基线', component='comparison-panel', state_label='方案建议')
        report = self.builder.quality_report(self.builder.normalize_page_spec(self.spec))
        self.assertNotIn('native_table_required', report['missing'])

    def test_shared_boundary_must_not_disappear_silently(self):
        self.spec.pop('boundary')
        self.spec['attached'] = ['限制：缺少内部样本，不能推出收益。']
        report = self.builder.quality_report(self.builder.normalize_page_spec(self.spec))
        self.assertIn('comparison_boundary', report['missing'])

    def test_short_panels_do_not_keep_the_long_panel_height(self):
        longer = copy.deepcopy(self.spec)
        longer['groups'][0]['claim'] = '需要核对的方案安排' * 4
        longer['groups'][0]['evidence'] = ['待核验记录内容' * 6] * 3
        longer['groups'][0]['action'] = '继续核对任务记录' * 4
        heights = []
        for spec in [self.spec, longer]:
            root = ET.fromstring(self.builder.build_svg_page(spec))
            panel = next(node for node in root.iter() if node.get('data-role') == 'comparison-panel')
            rect = next(node for node in panel if node.tag.endswith('rect'))
            heights.append(float(rect.get('height')))
        self.assertLess(heights[0], heights[1])

    def test_meaningful_implication_is_retained_before_capacity_validation(self):
        self.spec['groups'][0]['evidence'] = ['第一条依据。', '第二条依据。', '第三条依据。']
        self.spec['groups'][0]['implication'] = '权限与成本仍需核对，不能先决定采购。'
        normalized = self.builder.normalize_page_spec(self.spec)
        self.assertIn(self.spec['groups'][0]['implication'], normalized['groups'][0]['evidence'])
        self.assertIn('groups[0].evidence.comparison_capacity', self.builder.quality_report(normalized)['missing'])

    def test_requested_noto_cjk_font_is_used_for_east_asian_text(self):
        vendor = ROOT / 'scripts/svg/vendor/ppt_master/scripts'
        sys.path.insert(0, str(vendor))
        try:
            from svg_to_pptx import drawingml_utils
            with patch.object(drawingml_utils, '_host_font_families', return_value=frozenset({'noto sans cjk sc', 'pingfang sc'})):
                resolved = drawingml_utils.parse_font_family('Noto Sans CJK SC')
            self.assertEqual(resolved, {'latin': 'Noto Sans CJK SC', 'ea': 'Noto Sans CJK SC'})
        finally:
            sys.path.remove(str(vendor))


if __name__ == '__main__':
    unittest.main()
