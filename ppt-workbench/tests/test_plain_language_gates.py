"""TDD for page-spec plain-language and primary-claim gates (session-884 U-01/U-02)."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from copy import deepcopy
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GATES_DIR = ROOT / "scripts" / "svg" / "gates"


def _load_gate():
    pkg_name = "ppt_workbench_svg_gates"
    if pkg_name not in sys.modules:
        init_spec = importlib.util.spec_from_file_location(
            pkg_name,
            GATES_DIR / "__init__.py",
            submodule_search_locations=[str(GATES_DIR)],
        )
        pkg = importlib.util.module_from_spec(init_spec)
        sys.modules[pkg_name] = pkg
        init_spec.loader.exec_module(pkg)
    else:
        pkg = sys.modules[pkg_name]

    mod_name = f"{pkg_name}.plain_language"
    if mod_name not in sys.modules:
        mod_spec = importlib.util.spec_from_file_location(
            mod_name,
            GATES_DIR / "plain_language.py",
        )
        mod = importlib.util.module_from_spec(mod_spec)
        sys.modules[mod_name] = mod
        mod_spec.loader.exec_module(mod)
    else:
        mod = sys.modules[mod_name]
    return mod, pkg


gate, gates_api = _load_gate()
check = gate.check
BANNED_JARGON = gate.BANNED_JARGON
GateResult = gates_api.GateResult


def _who_scene():
    return {
        "who": "研发团队",
        "scene": "发布前联调",
        "problem": "没有统一验收标准，缺陷打回开发",
        "action": "先补验收清单，再扩大生成范围",
    }


def _good_groups():
    return [
        {
            "title": "验收缺口",
            "role": "support",
            "claim": "当前发布没有统一验收清单",
            "evidence": ["近两周 12 个缺陷从发布打回开发"],
            "impact": "返工占用联调窗口",
            "action": "补一份可勾选的验收清单",
        },
        {
            "title": "生成范围",
            "role": "support",
            "claim": "生成范围扩大后，评审来不及看完",
            "evidence": ["上周生成变更 40 份，评审只看完 18 份"],
            "impact": "漏看的变更带着缺陷上线",
            "action": "生成范围先限在单服务内",
        },
        {
            "title": "口径限制",
            "role": "limitation",
            "claim": "这是本团队两周记录，不是全公司基线",
            "evidence": ["记录来自团队缺陷表，样本 12 条"],
        },
        {
            "title": "下一步",
            "role": "action",
            "claim": "本周先出验收清单",
            "evidence": ["清单草案已有 8 项"],
            "impact": "没有签字人就无法挡住不合格发布",
            "action": "周五前由发布负责人签字",
        },
    ]


def good_content_page(**overrides):
    spec = {
        "page_role": "content",
        "title": "发布前没有统一验收，缺陷会打回开发",
        "key_message": "先把验收标准立住，再扩大代码生成范围",
        "primary_claim": "发布前没有统一验收，缺陷会打回开发，所以要先立验收标准再扩大生成范围",
        "audience_takeaway": "没有验收标准就扩大生成，缺陷会打回开发。",
        "plain_language_who_scene_problem_action": _who_scene(),
        "groups": _good_groups(),
    }
    spec.update(overrides)
    return spec


class PlainLanguageGateTests(unittest.TestCase):
    def test_banned_jargon_list_is_the_python_source_of_truth(self) -> None:
        for term in (
            "收编",
            "免疫机制",
            "吞吐线",
            "责任回流",
            "作业系统",
            "端到端收益",
            "抓手",
            "飞轮",
            "底座",
            "赋能",
            "闭环",
        ):
            self.assertIn(term, BANNED_JARGON)

    def test_missing_primary_claim_on_content_page(self) -> None:
        spec = good_content_page()
        spec.pop("primary_claim")
        result = check(spec)
        self.assertIsInstance(result, GateResult)
        self.assertIn("primary_claim", result.missing)

    def test_title_key_message_contradict_primary_claim(self) -> None:
        spec = good_content_page(
            title="市场已从补全升级为智能体平台",
            key_message="选型应转向平台层能力建设",
            primary_claim="发布前没有统一验收，缺陷会打回开发",
        )
        result = check(spec)
        self.assertIn("claim_alignment", result.missing)

    def test_more_than_three_equal_groups_breaks_support_limit(self) -> None:
        groups = [
            {
                "title": f"模块{index}",
                "claim": "这项也很重要",
                "evidence": [f"事实{index}"],
            }
            for index in range(4)
        ]
        spec = good_content_page(groups=groups)
        result = check(spec)
        self.assertIn("support_limit", result.missing)

    def test_four_equal_weight_supports_break_support_limit(self) -> None:
        groups = [
            {
                "title": f"支撑{index}",
                "role": "support",
                "weight": 1,
                "claim": "同一层级的支撑点",
                "evidence": [f"证据{index}"],
            }
            for index in range(4)
        ]
        spec = good_content_page(groups=groups)
        result = check(spec)
        self.assertIn("support_limit", result.missing)

    def test_two_banned_jargon_in_one_sentence_breaks_plain_language(self) -> None:
        spec = good_content_page(
            key_message="请把收编和免疫机制写进检查单",
        )
        result = check(spec)
        self.assertIn("plain_language", result.missing)

    def test_stacked_abstract_nouns_break_abstract_noun_stack(self) -> None:
        stacked = "组织协同机制能力升级路径已经明确"
        spec = good_content_page(
            title=stacked,
            key_message="先补验收清单，再扩大生成范围",
            primary_claim=stacked + "，但还缺验收清单",
        )
        result = check(spec)
        self.assertIn("abstract_noun_stack", result.missing)

    def test_action_without_fact_breaks_fact_then_impact_then_action(self) -> None:
        groups = deepcopy(_good_groups())
        groups[-1] = {
            "title": "立刻铺开",
            "role": "action",
            "claim": "全员立刻铺开",
            "action": "下周全员推广新做法",
        }
        spec = good_content_page(groups=groups)
        result = check(spec)
        self.assertIn("fact_then_impact_then_action", result.missing)

    def test_missing_audience_takeaway(self) -> None:
        spec = good_content_page()
        spec.pop("audience_takeaway")
        result = check(spec)
        self.assertIn("audience_takeaway", result.missing)

    def test_good_content_page_has_empty_missing(self) -> None:
        result = check(good_content_page())
        self.assertEqual(result.missing, [])
        self.assertEqual(result.warnings, [])

    def test_cover_with_judgment_title_and_primary_claim_passes(self) -> None:
        spec = {
            "page_role": "cover",
            "title": "先立验收，再扩大生成",
            "primary_claim": "发布前没有统一验收，缺陷会打回开发",
        }
        result = check(spec)
        self.assertEqual(result.missing, [])
        self.assertEqual(result.warnings, [])

    def test_content_page_requires_who_scene_problem_action(self) -> None:
        spec = good_content_page()
        spec.pop("plain_language_who_scene_problem_action")
        result = check(spec)
        self.assertIn("plain_language_who_scene_problem_action", result.missing)

    def test_closed_loop_with_concrete_object_is_not_plain_language_block(self) -> None:
        spec = good_content_page(
            key_message="先把缺陷闭环写进检查单，再扩大生成范围",
        )
        result = check(spec)
        self.assertNotIn("plain_language", result.missing)

    def test_repeated_title_number_in_every_group_warns_without_number_role(self) -> None:
        groups = [
            {
                "title": "实验室数字",
                "role": "support",
                "claim": "55.8% 被再次写进卡片",
                "evidence": ["同一 55.8% 没有新口径"],
            },
            {
                "title": "仍是该数字",
                "role": "support",
                "claim": "55.8% 没有改成约束",
                "evidence": ["55.8% 仍当主结论"],
            },
            {
                "title": "口径限制",
                "role": "limitation",
                "claim": "55.8% 只是单任务实验",
                "evidence": ["样本不是本组织"],
            },
            {
                "title": "下一步",
                "role": "action",
                "claim": "不要把 55.8% 当内部基线",
                "evidence": ["先采集本团队基线"],
                "action": "补内部基线后再决策",
            },
        ]
        spec = good_content_page(
            title="55.8% 不能当成内部基线",
            key_message="先采集本团队基线，再决定是否扩大生成",
            primary_claim="55.8% 是实验室单任务结果，不能当成内部基线",
            audience_takeaway="55.8% 只是实验室结果，先采内部基线。",
            groups=groups,
        )
        result = check(spec)
        self.assertEqual(result.missing, [])
        self.assertTrue(
            any("number_role" in warning for warning in result.warnings),
            result.warnings,
        )

    def test_closing_page_needs_one_takeaway_claim(self) -> None:
        result = check({"page_role": "closing", "title": "谢谢"})
        self.assertTrue(
            "primary_claim" in result.missing or "audience_takeaway" in result.missing,
            result.missing,
        )

    def test_outline_seed_without_groups_can_pass_check_outline(self) -> None:
        self.assertTrue(hasattr(gate, "check_outline"))
        seed = {
            "page_role": "content",
            "title": "发布前没有统一验收，缺陷会打回开发",
            "key_message": "先立验收标准，再扩大生成范围",
            "primary_claim": "发布前没有统一验收，缺陷会打回开发，所以要先立验收标准再扩大生成范围",
            "audience_takeaway": "先把验收标准立住，再扩大生成。",
            "plain_language_who_scene_problem_action": {
                "who": "研发团队",
                "scene": "用生成代码赶发布",
                "problem": "没有统一验收，缺陷打回开发",
                "action": "先立验收标准再扩大生成",
            },
        }
        result = gate.check_outline(seed)
        self.assertEqual(result.missing, [], result.missing)

    def test_outline_seed_missing_who_scene_is_blocked(self) -> None:
        seed = {
            "title": "发布前没有统一验收，缺陷会打回开发",
            "primary_claim": "发布前没有统一验收，缺陷会打回开发，所以要先立验收标准",
            "audience_takeaway": "先立验收标准。",
        }
        result = gate.check_outline(seed)
        self.assertIn("plain_language_who_scene_problem_action", result.missing)

    def test_outline_seed_jargon_is_blocked_before_page_authoring(self) -> None:
        seed = {
            "title": "用作业系统收编吞吐线",
            "primary_claim": "用作业系统收编吞吐线",
            "audience_takeaway": "先收编再赋能。",
            "plain_language_who_scene_problem_action": {
                "who": "管理层",
                "scene": "汇报",
                "problem": "说不清",
                "action": "改口吻",
            },
        }
        result = gate.check_outline(seed)
        self.assertTrue(
            "plain_language" in result.missing or "abstract_noun_stack" in result.missing,
            result.missing,
        )

    def test_check_outline_ignores_missing_groups(self) -> None:
        seed = {
            "title": "发布前没有统一验收，缺陷会打回开发",
            "key_message": "先立验收标准，再扩大生成范围",
            "primary_claim": "发布前没有统一验收，缺陷会打回开发，所以要先立验收标准再扩大生成范围",
            "audience_takeaway": "先把验收标准立住，再扩大生成。",
            "plain_language_who_scene_problem_action": {
                "who": "研发团队",
                "scene": "用生成代码赶发布",
                "problem": "没有统一验收，缺陷打回开发",
                "action": "先立验收标准再扩大生成",
            },
            "groups": [
                {"title": "只写动作", "action": "下周上线", "role": "action"},
            ],
        }
        outline = gate.check_outline(seed)
        page = check(seed)
        self.assertNotIn("fact_then_impact_then_action", outline.missing)
        self.assertIn("fact_then_impact_then_action", page.missing)


if __name__ == "__main__":
    unittest.main()
