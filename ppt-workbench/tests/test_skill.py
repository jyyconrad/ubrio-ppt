from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]

WORKFLOW_SUMMARY_MARKERS = (
    "整理 PPT 素材",
    "编排汇报大纲",
    "逐页制作",
    "合并导出",
)

LIVE_PATH_FORBIDDEN = (
    "历史制作方法",
    "非原生主线",
    "已选活动默认路线",
    "只有已验证的 native 组件是当前执行入口",
)


def _yaml_description(text: str) -> str:
    match = re.search(r"^---\n(.*?)\n---", text, re.S)
    if not match:
        return ""
    desc = re.search(r"^description:\s*(.*)$", match.group(1), re.M)
    return desc.group(1).strip() if desc else ""


class WorkbenchSkillTests(unittest.TestCase):
    def test_single_standard_entry_and_integrated_layout(self) -> None:
        text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("name: ppt-workbench", text)
        self.assertIn("references/materials/", text)
        self.assertIn("references/generate/capability-map.md", text)
        self.assertIn("scripts/native.cjs", text)
        self.assertNotIn("modules/", text)

    def test_quality_gate_and_embedded_assets_are_present(self) -> None:
        required = [
            ROOT / "scripts/extract_materials.py",
            ROOT / "scripts/native.cjs",
            ROOT / "scripts/inspect_pptx.py",
            ROOT / "scripts/merge_export.py",
            ROOT / "tests/verify_examples.py",
            ROOT / "tests/test_generation_isolation.py",
            ROOT / "assets/examples/cases.json",
            ROOT / "references/generate/capability-map.md",
            ROOT / "references/generate/methods/skill-graph.md",
            ROOT / "references/generate/methods/gold-pages.md",
            ROOT / "references/generate/gold-examples-catalog.json",
            ROOT / "scripts/skill_graph/search_modules.py",
            ROOT / "scripts/skill_graph/load_modules.py",
            ROOT / "references/generate/original/slide-authoring/assets/icons/icon-index.json",
            ROOT / "references/generate/original/slide-authoring/GUIDE.md",
            ROOT / "references/generate/original/slide-authoring/references/contract-gold-svg-builder.md",
            ROOT / "scripts/svg/build_gold_svg_page.py",
            ROOT / "scripts/svg/overlay_native_slots.py",
            ROOT / "scripts/svg/write_svg.py",
            ROOT / "scripts/svg/validate_svg_drawingml.py",
            ROOT / "scripts/svg/render_svg_drawingml.py",
            ROOT / "scripts/validate_deck_contract.py",
            ROOT / "references/generate/methods/authoring-and-checks.md",
            ROOT / "references/generate/methods/native-components.md",
            ROOT / "scripts/svg/search_icons.py",
            ROOT / "references/generate/methods/icon-embed.md",
            ROOT / "references/generate/methods/image-owners.md",
        ]
        for path in required:
            self.assertTrue(path.exists(), path)

    def test_runtime_quality_gate_instructions_are_explicit(self) -> None:
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        generation = (ROOT / "references/generate/guide.md").read_text(encoding="utf-8")
        runtime = (ROOT / "references/runtime.md").read_text(encoding="utf-8")
        for text in (skill, generation, runtime):
            self.assertIn("inspect_pptx.py", text)
        self.assertIn("每页", skill)
        self.assertIn("verify_examples.py", runtime)
        self.assertIn("test_generation_isolation.py", runtime)
        self.assertIn("check_skill.py", runtime)

    def test_plain_language_is_owned_by_outline_stage(self) -> None:
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        outline = (ROOT / "references/outline/guide.md").read_text(encoding="utf-8")
        method = (ROOT / "references/outline/outline-method.md").read_text(encoding="utf-8")
        page = (ROOT / "references/page-generation.md").read_text(encoding="utf-8")
        outline_section = skill.split("### 2. 大纲", 1)[1].split("### 3.", 1)[0]
        page_section = skill.split("### 3. 逐页制作", 1)[1].split("### 4.", 1)[0]
        self.assertIn("人话", outline_section)
        self.assertIn("谁", outline_section)
        self.assertIn("人话", outline)
        self.assertIn("谁", method)
        self.assertIn("场景", method)
        self.assertIn("check_outline", method)
        self.assertIn("回大纲", page)
        self.assertIn("抄", page_section)

    def test_narrative_shape_is_on_the_outline_path(self) -> None:
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        outline = (ROOT / "references/outline/guide.md").read_text(encoding="utf-8")
        recipe = (ROOT / "references/outline/narrative-shape.md").read_text(encoding="utf-8")
        page = (ROOT / "references/page-generation.md").read_text(encoding="utf-8")
        gates = (ROOT / "references/content-visual-quality-gates.md").read_text(encoding="utf-8")
        outline_section = skill.split("### 2. 大纲", 1)[1].split("### 3.", 1)[0]
        for token in ("thesis", "proves", "dominant", "label", "narrative-shape.md"):
            self.assertIn(token, outline_section)
        self.assertIn("narrative-shape.md", outline)
        self.assertIn("narrative-shape.md", gates)
        for name in ("不可比证据", "流程断点", "左右对照", "门禁", "决定章"):
            self.assertIn(name, recipe)
        self.assertIn("thesis 原样开头", recipe)
        self.assertNotIn("至少两种有语义", page)
        self.assertNotIn("两个辅助信息区", page)

    def test_chinese_business_defaults_to_gold_authoring_path(self) -> None:
        text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        for marker in (
            "默认走金标 authoring 路径",
            "skill-graph.md",
            "search_modules.py",
            "build_gold_svg_page.py",
            "source.svg",
            "没有 `source.svg` 的中文业务正文页不能标记为金标完成",
            "信息密度高",
        ):
            self.assertIn(marker, text)

    def test_skill_description_is_use_when_triggers_not_workflow(self) -> None:
        text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        desc = _yaml_description(text)
        self.assertTrue(desc.startswith("Use when"), desc[:80])
        hits = [marker for marker in WORKFLOW_SUMMARY_MARKERS if marker in desc]
        self.assertLessEqual(
            len(hits),
            1,
            f"description summarizes the four-stage workflow: {hits}",
        )
        for token in (
            "build_gold_svg_page.py",
            "native.cjs",
            "validate-only",
            "page_spec.json",
            "PptxGenJS",
        ):
            self.assertNotIn(token, desc)
        self.assertLessEqual(len(desc), 500)

    def test_live_docs_default_gold_svg_slots_native_cjs_fallback(self) -> None:
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        page = (ROOT / "references/page-generation.md").read_text(encoding="utf-8")
        cap = (ROOT / "references/generate/capability-map.md").read_text(encoding="utf-8")
        guide = (ROOT / "references/generate/guide.md").read_text(encoding="utf-8")
        runtime = (ROOT / "references/runtime.md").read_text(encoding="utf-8")
        authoring = (ROOT / "references/generate/methods/authoring-and-checks.md").read_text(
            encoding="utf-8"
        )
        tests_readme = (ROOT / "tests/README.md").read_text(encoding="utf-8")
        for text in (skill, page, cap, guide, runtime, authoring, tests_readme):
            for phrase in LIVE_PATH_FORBIDDEN:
                self.assertNotIn(phrase, text)
        for text in (page, cap):
            self.assertRegex(text, r"金标 SVG|金标 authoring")
            self.assertIn("native", text.lower())
            self.assertNotIn("历史 SVG", text)
            self.assertNotRegex(text, r"金标.*历史")
            self.assertRegex(
                text,
                r"native\.cjs.{0,40}fallback|fallback.{0,40}native\.cjs|仅当.{0,80}native\.cjs|native\.cjs.{0,80}不可用",
            )
        self.assertIn("render_svg_drawingml.py", runtime)
        self.assertRegex(runtime, r"仅当 SVG→PPTX 不可用时才从 `scripts/native\.cjs`")
        heading = authoring.splitlines()[0]
        self.assertRegex(heading, r"^# 活动")
        self.assertNotIn("历史", heading)
        self.assertIn("fallback", authoring.lower())
        self.assertNotIn("原生 PPTX 路线", tests_readme)
        self.assertIn("render_svg_drawingml.py", tests_readme)
        self.assertIn("fallback", tests_readme.lower())


if __name__ == "__main__":
    unittest.main()
