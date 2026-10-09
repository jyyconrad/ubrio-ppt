"""Local skill-graph search → load → example (no Agno / PgVector / index_cli)."""

from __future__ import annotations

import ast
import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts" / "skill_graph"
TREE = (
    ROOT
    / "references"
    / "generate"
    / "original"
    / "slide-authoring"
    / "references"
    / "_index"
    / "capability-tree.json"
)
EXAMPLES = (
    ROOT
    / "references"
    / "generate"
    / "original"
    / "slide-authoring"
    / "assets"
    / "examples"
)
FORBIDDEN = ("agno", "pgvector", "index_cli", "search_knowledge_base")


def _load(name: str):
    path = SCRIPTS / f"{name}.py"
    spec = importlib.util.spec_from_file_location(f"skill_graph_{name}", path)
    if spec is None or spec.loader is None:
        raise FileNotFoundError(path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class SkillGraphRoutingTests(unittest.TestCase):
    def test_search_and_load_scripts_exist(self) -> None:
        self.assertTrue((SCRIPTS / "search_modules.py").is_file())
        self.assertTrue((SCRIPTS / "load_modules.py").is_file())
        self.assertTrue(
            (ROOT / "references" / "generate" / "methods" / "skill-graph.md").is_file()
        )

    def test_scripts_do_not_import_host_index_stack(self) -> None:
        for path in SCRIPTS.glob("*.py"):
            source = path.read_text(encoding="utf-8")
            lowered = source.lower()
            for token in FORBIDDEN:
                self.assertNotIn(token, lowered, f"{path.name} mentions {token}")
            tree = ast.parse(source)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        self.assertNotIn(alias.name.split(".")[0].lower(), FORBIDDEN)
                elif isinstance(node, ast.ImportFrom) and node.module:
                    self.assertNotIn(node.module.split(".")[0].lower(), FORBIDDEN)

    def test_search_returns_candidates_only_for_one_dimension(self) -> None:
        search = _load("search_modules")
        payload = search.search_modules(
            query="渠道转化排名柱状图",
            page_role="content",
            dimension="layout",
            top_k=3,
        )
        ids = list(payload["candidate_module_ids"])
        self.assertIn("chart-bar-comparison", ids)
        self.assertEqual(payload.get("loaded_module_ids"), [])
        self.assertLessEqual(len(ids), 3)
        self.assertEqual(payload.get("dimension"), "layout")
        tree_ids = {node["id"] for node in json.loads(TREE.read_text(encoding="utf-8"))["nodes"]}
        for module_id in ids:
            self.assertIn(module_id, tree_ids)
        for hit in payload["candidates"]:
            self.assertEqual(set(hit) >= {"module_id", "title", "excerpt", "why_matched"}, True)
            self.assertNotIn("content", hit)
            self.assertNotIn("body", hit)
            self.assertLessEqual(len(hit["excerpt"]), 280)
            self.assertNotIn("# Chart:", hit["excerpt"])

    def test_theme_query_does_not_return_layout_bodies(self) -> None:
        search = _load("search_modules")
        payload = search.search_modules(
            query="浅底蓝白商务经营汇报配色",
            page_role="content",
            dimension="theme",
            top_k=3,
        )
        ids = payload["candidate_module_ids"]
        self.assertTrue(ids)
        self.assertNotIn("chart-bar-comparison", ids)
        self.assertTrue(any("theme" in item or "visual" in item for item in ids) or any(
            "theme" in hit["why_matched"] for hit in payload["candidates"]
        ))
        blob = json.dumps(payload, ensure_ascii=False)
        self.assertNotIn("Deck 级色彩配额", blob)

    def test_load_injects_cores_gold_path_and_requires_not_candidates(self) -> None:
        load = _load("load_modules")
        payload = load.load_modules(
            module_ids=[
                "chart-bar-comparison",
                "layout-native-chart-slot",
                "layout-sectioned-evidence-dashboard",
                "theme-light-business-blue",
                "chart-line-trend",
                "chart-pie-composition",
            ],
            page_role="content",
        )
        loaded = payload["loaded_module_ids"]
        self.assertIn("drawingml-svg-authoring-core", loaded)
        self.assertIn("contract-visual-token-core", loaded)
        self.assertIn("contract-gold-svg-builder", loaded)
        self.assertIn("contract-structure-hierarchy", loaded)
        primaries = payload["primary_module_ids"]
        self.assertLessEqual(len(primaries), 4)
        self.assertNotIn("chart-pie-composition", primaries)
        self.assertIn("chart-pie-composition", payload.get("deferred_module_ids") or payload.get("candidate_module_ids") or [])
        if "layout-sectioned-evidence-dashboard" in primaries:
            for required in (
                "contract-content-density",
                "layout-chart-insight-card",
                "layout-full-width-rect-step-flow",
            ):
                self.assertIn(required, loaded)
        roles = {item["module_id"]: item["role"] for item in payload["modules"]}
        self.assertEqual(roles["drawingml-svg-authoring-core"], "baseline")
        self.assertEqual(roles["contract-gold-svg-builder"], "gold_path")
        for item in payload["modules"]:
            self.assertTrue(item.get("content"))
            self.assertIn(item["role"], {"baseline", "gold_path", "primary", "requires"})

    def test_example_loads_by_skill_path_and_caps_12kb(self) -> None:
        load = _load("load_modules")
        small = load.load_example(
            "assets/examples/svg-ppt/decks/scenario-chart-type-gold-pages/01-bar-comparison.svg"
        )
        self.assertTrue(small["ok"])
        self.assertLessEqual(small["returned_bytes"], 12288)
        self.assertFalse(small["truncated"])
        self.assertIn("native-chart-slot", small["content"])
        large_rel = (
            "assets/examples/svg-ppt/decks/template-series-composite-library/"
            "13-sectioned-evidence-dashboard.svg"
        )
        self.assertGreater((EXAMPLES.parent.parent / large_rel).stat().st_size, 12288)
        large = load.load_example(large_rel)
        self.assertTrue(large["ok"])
        self.assertTrue(large["truncated"])
        self.assertEqual(large["returned_bytes"], 12288)
        blocked = load.load_example("references/generate/methods/skill-graph.md")
        self.assertFalse(blocked["ok"])

    def test_entry_docs_route_through_local_skill_graph(self) -> None:
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        page = (ROOT / "references" / "page-generation.md").read_text(encoding="utf-8")
        cap = (ROOT / "references" / "generate" / "capability-map.md").read_text(encoding="utf-8")
        recipe = (
            ROOT / "references" / "generate" / "methods" / "skill-graph.md"
        ).read_text(encoding="utf-8")
        self.assertRegex(skill, r"^---\nname: ppt-workbench\ndescription: Use when")
        self.assertTrue(skill.split("description:", 1)[1].lstrip().startswith("Use when"))
        for text in (skill, page, cap):
            self.assertIn("skill-graph.md", text)
            self.assertIn("search_modules.py", text)
        self.assertNotIn(
            "中国式汇报方法](references/generate/original/slide-authoring/references/chinese-business-ppt-authoring.md)",
            skill,
        )
        self.assertNotIn(
            "中国式业务汇报方法](generate/original/slide-authoring/references/chinese-business-ppt-authoring.md)",
            page,
        )
        self.assertIn("candidate", recipe.lower())
        self.assertIn("always_read", recipe)
        self.assertIn("default_gold_path", recipe)
        self.assertIn("兜底", recipe)
        self.assertIn("chinese-business-ppt-authoring.md", recipe)
        self.assertIn("routing-examples.md", recipe)
        self.assertNotIn("PgVector", recipe)
        self.assertNotIn("非原生主线", cap)
        self.assertNotIn("历史 SVG", cap)


if __name__ == "__main__":
    unittest.main()
