"""Gold page authoring: local CLI, structure refs, native-data sidecar, no preview rects."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "scripts" / "svg" / "build_gold_svg_page.py"
RECIPE = ROOT / "references" / "generate" / "methods" / "gold-pages.md"
OVERLAY = ROOT / "references" / "generate" / "gold-examples-catalog.json"
ORIGINAL_MANIFEST = (
    ROOT
    / "references"
    / "generate"
    / "original"
    / "slide-authoring"
    / "assets"
    / "examples"
    / "svg-ppt"
    / "examples-manifest.json"
)
GOV_DECK = (
    ROOT
    / "references"
    / "generate"
    / "original"
    / "slide-authoring"
    / "assets"
    / "examples"
    / "svg-ppt"
    / "decks"
    / "scenario-government-briefing-gold-pages"
)
CATALOG = ROOT / "scripts" / "skill_graph" / "catalog.py"
UNSUPPORTED_KINDS = {"sankey", "bubble", "radar", "combo"}


READY_SPEC = {
    "schema_version": "gold_page_spec/v1",
    "theme_id": "business_blue",
    "layout": "gold_cards",
    "page_role": "content",
    "title": "渠道转化已由公域拉动转为私域与老客转介主导",
    "key_message": "下阶段预算应向高转化来源倾斜，同时保留公域获客底盘。",
    "structure_hierarchy": {
        "semantic_layer": ["渠道转化判断", "三类渠道证据", "预算行动", "CRM口径"],
        "narrative_layer": ["结论先行", "证据链", "解释影响", "行动闭环"],
        "visual_layer": ["main-title", "key-message", "metric-strip", "main-content", "chart-slot"],
        "geometry_layer": ["title-band", "metric-strip", "main-body", "source-note"],
        "svg_group_layer": [
            "main-title-block",
            "metrics-panel",
            "main-content",
            "chart-slot-1",
            "source-note",
        ],
    },
    "metrics": [
        {
            "label": "老客转介",
            "value": "42%",
            "note": "CRM Q2 成交转化",
            "evidence_type": "internal_baseline",
            "claim_type": "fact",
            "population": "成交客户",
            "period": "2026 Q2",
            "denominator": "线索数",
            "source_ref": "CRM 线索转化统计",
            "limitation": "不含未归因成交",
            "on_metric_label": "内部基线 · 成交客户 · 不含未归因",
        },
        {
            "label": "私域触达",
            "value": "31%",
            "note": "CRM Q2 成交转化",
            "evidence_type": "internal_baseline",
            "claim_type": "fact",
            "population": "成交客户",
            "period": "2026 Q2",
            "denominator": "线索数",
            "source_ref": "CRM 线索转化统计",
            "limitation": "不含未归因成交",
            "on_metric_label": "内部基线 · 成交客户 · 不含未归因",
        },
        {
            "label": "公域投放",
            "value": "18%",
            "note": "CRM Q2 成交转化",
            "evidence_type": "internal_baseline",
            "claim_type": "fact",
            "population": "成交客户",
            "period": "2026 Q2",
            "denominator": "线索数",
            "source_ref": "CRM 线索转化统计",
            "limitation": "不含未归因成交",
            "on_metric_label": "内部基线 · 成交客户 · 不含未归因",
        },
    ],
    "groups": [
        {
            "title": "经营判断",
            "claim": "高转化来自私域和转介，而不是公域线索量",
            "evidence": ["转介成交转化 42%", "私域成交转化 31%"],
            "explanation": "筛选质量更高，成交路径更短",
            "action": "预算向高质量渠道倾斜",
        },
        {
            "title": "证据链",
            "claim": "公域线索质量不足，继续加投只会放大浪费",
            "evidence": ["公域成交转化 18%", "获客成本连续两季上升"],
            "explanation": "投放筛选偏松，无效线索占比偏高",
            "action": "收紧投放条件和渠道准入",
        },
        {
            "title": "行动闭环",
            "claim": "先复盘预算结构再扩量",
            "evidence": ["财务月报渠道成本", "CRM 归因表"],
            "explanation": "只看线索量会误导投放决策",
            "action": "增长负责人本周提交预算重配方案",
        },
    ],
    "primary_claim": "渠道转化已由公域拉动转为私域与老客转介主导",
    "audience_takeaway": "增长负责人本周把预算从公域转向私域和老客转介。",
    "plain_language_who_scene_problem_action": {
        "who": "增长负责人",
        "scene": "看本季 CRM 渠道成交",
        "problem": "公域成交转化只有一成八，私域和转介更高",
        "action": "把下周预算转向私域和老客转介",
    },
    "typography": {"body_px": 16, "title_px": 32, "source_px": 11},
    "native_chart_slots": [
        {
            "id": "bar-slot-1",
            "chart_type": "bar",
            "title": "渠道转化对比",
            "insight": "私域与老客转介显著领先",
            "source": "CRM 线索转化统计，2026 Q2",
            "unit": "成交转化率",
            "box": {"x": 780, "y": 330, "w": 400, "h": 240},
            "data": [
                {"label": "公域投放", "value": 18},
                {"label": "私域触达", "value": 31},
                {"label": "老客转介", "value": 42},
            ],
        }
    ],
    "sources": ["CRM 线索转化统计，2026 Q2"],
}


def _load_builder():
    spec = importlib.util.spec_from_file_location("build_gold_svg_page", BUILDER)
    if spec is None or spec.loader is None:
        raise FileNotFoundError(BUILDER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_catalog():
    spec = importlib.util.spec_from_file_location("skill_graph_catalog", CATALOG)
    if spec is None or spec.loader is None:
        raise FileNotFoundError(CATALOG)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _local(tag: str) -> str:
    return tag.split("}", 1)[-1]


def _slot_groups(root: ET.Element) -> list[ET.Element]:
    found: list[ET.Element] = []
    for elem in root.iter():
        role = (elem.get("data-role") or "").strip()
        if role in {"native-chart-slot", "native-table-slot", "native-sankey-slot", "native-image-slot", "evidence-asset-slot"}:
            found.append(elem)
            continue
        if (elem.get("data-native-chart") or "").lower() == "true":
            found.append(elem)
    return found


def _full_page_rects(root: ET.Element) -> list[ET.Element]:
    hits: list[ET.Element] = []
    for elem in root.iter():
        if _local(elem.tag) != "rect":
            continue
        try:
            x = float(elem.get("x") or 0)
            y = float(elem.get("y") or 0)
            w = float(elem.get("width") or 0)
            h = float(elem.get("height") or 0)
        except ValueError:
            continue
        if x <= 1280 * 0.02 and y <= 720 * 0.02 and w >= 1280 * 0.96 and h >= 720 * 0.96:
            hits.append(elem)
    return hits


class GoldPageAuthoringTests(unittest.TestCase):
    def test_gold_pages_recipe_maps_ubrio_ids_to_local_cli(self) -> None:
        self.assertTrue(RECIPE.is_file(), "missing references/generate/methods/gold-pages.md")
        text = RECIPE.read_text(encoding="utf-8")
        self.assertIn("validate-gold-page-spec", text)
        self.assertIn("build-gold-svg-page", text)
        self.assertIn("python3 scripts/svg/build_gold_svg_page.py", text)
        self.assertIn("--validate-only", text)
        self.assertIn("--output source.svg", text)
        self.assertIn("native-data.json", text)
        self.assertNotIn("run_skill_resource", text)
        for marker in (
            "gold-page-patterns.md",
            "contract-structure-hierarchy.md",
            "scenario-government-briefing-gold-pages",
        ):
            self.assertIn(marker, text)
        self.assertIn("没有 `source.svg` 的中文业务正文页不能标为金标完成", text)

    def test_entry_docs_treat_gold_patterns_as_active_structure_refs(self) -> None:
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        page = (ROOT / "references" / "page-generation.md").read_text(encoding="utf-8")
        cap = (ROOT / "references" / "generate" / "capability-map.md").read_text(encoding="utf-8")
        for text in (skill, page, cap):
            self.assertIn("gold-pages.md", text)
            self.assertNotIn("非原生主线", text)
        for text in (page, cap):
            self.assertIn("gold-page-patterns.md", text)
            self.assertIn("contract-structure-hierarchy.md", text)
            self.assertIn("scenario-", text)
            self.assertIn("gold-pages", text)
        self.assertIn("没有 `source.svg` 的中文业务正文页不能标记为金标完成", skill)
        self.assertNotIn("历史 SVG", cap)
        self.assertNotRegex(cap, r"金标.*历史")

    def test_government_briefing_is_registered_in_workbench_catalog_only(self) -> None:
        original = json.loads(ORIGINAL_MANIFEST.read_text(encoding="utf-8"))
        original_ids = [item.get("id") for item in original.get("gold_examples") or []]
        self.assertNotIn("scenario-government-briefing-gold-pages", original_ids)
        self.assertTrue(OVERLAY.is_file(), "missing workbench gold-examples-catalog.json")
        overlay = json.loads(OVERLAY.read_text(encoding="utf-8"))
        overlay_ids = [item.get("id") for item in overlay.get("gold_examples") or []]
        self.assertIn("scenario-government-briefing-gold-pages", overlay_ids)
        catalog = _load_catalog()
        merged_ids = [item["id"] for item in catalog.gold_examples(ROOT)]
        self.assertIn("scenario-government-briefing-gold-pages", merged_ids)
        for name in (
            "01-pyramid-hierarchy.svg",
            "02-dark-cockpit-combo.svg",
            "03-evidence-table-dark-panel.svg",
            "04-tiered-cards-composite.svg",
            "05-timeline-arrow.svg",
        ):
            self.assertTrue((GOV_DECK / name).is_file(), name)
        deck = next(
            item
            for item in catalog.gold_examples(ROOT)
            if item["id"] == "scenario-government-briefing-gold-pages"
        )
        self.assertGreaterEqual(len(deck.get("pages") or []), 5)

    def test_validate_only_then_source_svg_emits_sibling_native_data(self) -> None:
        builder = _load_builder()
        report = builder.quality_report(builder.normalize_page_spec(READY_SPEC))
        self.assertEqual(report["quality_status"], "ready", report.get("missing"))
        with tempfile.TemporaryDirectory() as tmp:
            page_dir = Path(tmp)
            spec_path = page_dir / "page_spec.json"
            spec_path.write_text(json.dumps(READY_SPEC, ensure_ascii=False), encoding="utf-8")
            validate = subprocess.run(
                [
                    sys.executable,
                    str(BUILDER),
                    "--spec",
                    str(spec_path),
                    "--validate-only",
                    "--write-normalized",
                    str(page_dir / "page_spec.normalized.json"),
                ],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(validate.returncode, 0, validate.stderr)
            payload = json.loads(validate.stdout)
            self.assertTrue(payload.get("ok"))
            self.assertEqual(payload.get("quality", {}).get("quality_status"), "ready")
            self.assertFalse((page_dir / "source.svg").exists())
            self.assertFalse((page_dir / "native-data.json").exists())

            build = subprocess.run(
                [
                    sys.executable,
                    str(BUILDER),
                    "--spec",
                    str(spec_path),
                    "--output",
                    str(page_dir / "source.svg"),
                ],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(build.returncode, 0, build.stderr)
            svg_path = page_dir / "source.svg"
            native_path = page_dir / "native-data.json"
            self.assertTrue(svg_path.is_file())
            self.assertTrue(native_path.is_file(), "builder must emit sibling native-data.json")
            svg_text = svg_path.read_text(encoding="utf-8")
            self.assertIn('data-native-data-ref="native-data.json"', svg_text)
            self.assertNotIn("data-chart-data", svg_text)
            native = json.loads(native_path.read_text(encoding="utf-8"))
            charts = native.get("charts") or []
            self.assertTrue(charts)
            self.assertEqual(charts[0]["slot_id"], "bar-slot-1")
            self.assertEqual(charts[0]["kind"], "bar")
            self.assertNotIn(charts[0]["kind"], UNSUPPORTED_KINDS)
            self.assertEqual(charts[0]["labels"], ["公域投放", "私域触达", "老客转介"])
            self.assertEqual(charts[0]["series"][0]["values"], [18, 31, 42])

            root = ET.fromstring(svg_text)
            self.assertEqual(_full_page_rects(root), [])
            slots = _slot_groups(root)
            self.assertTrue(slots)
            for slot in slots:
                inner_text = [
                    (child.text or "").strip()
                    for child in slot.iter()
                    if _local(child.tag) == "text" and (child.text or "").strip()
                ]
                joined = " ".join(inner_text)
                self.assertNotIn("渠道转化对比", joined)
                self.assertNotIn("CRM 线索转化统计", joined)
                self.assertNotIn("私域与老客转介显著领先", joined)
            self.assertIn("渠道转化对比", svg_text)
            self.assertIn("CRM 线索转化统计，2026 Q2", svg_text)

    def test_builder_keeps_evidence_titles_outside_slot_groups(self) -> None:
        builder = _load_builder()
        spec = json.loads(json.dumps(READY_SPEC))
        spec["evidence_asset_slots"] = [
            {
                "id": "screenshot-proof-1",
                "title": "线索池截图",
                "caption": "截图证明公域无效线索占比偏高",
                "source": "CRM 线索池导出 2026-06",
                "asset_key": "evidence-synthetic.png",
                "box": {"x": 70, "y": 520, "w": 360, "h": 120},
            }
        ]
        svg = builder.build_svg_page(spec, native_data_ref="native-data.json")
        root = ET.fromstring(svg)
        slots = [
            elem
            for elem in _slot_groups(root)
            if (elem.get("id") or "") == "screenshot-proof-1"
            or (elem.get("data-role") or "") in {"native-image-slot", "evidence-asset-slot"}
        ]
        self.assertTrue(slots)
        for slot in slots:
            inner = " ".join(
                (child.text or "").strip()
                for child in slot.iter()
                if _local(child.tag) == "text"
            )
            self.assertNotIn("线索池截图", inner)
            self.assertNotIn("CRM 线索池导出", inner)
        self.assertIn("线索池截图", svg)


if __name__ == "__main__":
    unittest.main()
