"""Local lucide icon search + data-icon-id expand (no Ubrio search_svg_icons)."""

from __future__ import annotations

import ast
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from xml.etree import ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
SEARCH = ROOT / "scripts" / "svg" / "search_icons.py"
OVERLAY = ROOT / "scripts" / "svg" / "overlay_native_slots.py"
RECIPE = ROOT / "references" / "generate" / "methods" / "icon-embed.md"
CAPABILITY_MAP = ROOT / "references" / "generate" / "capability-map.md"
PAGE_GENERATION = ROOT / "references" / "page-generation.md"
SKILL = ROOT / "SKILL.md"
ICON_README = (
    ROOT
    / "references"
    / "generate"
    / "original"
    / "slide-authoring"
    / "assets"
    / "icons"
    / "README.md"
)
ICONS_ROOT = (
    ROOT
    / "references"
    / "generate"
    / "original"
    / "slide-authoring"
    / "assets"
    / "icons"
)
PYTHON = ROOT / ".venv" / "bin" / "python"
FORBIDDEN = ("search_svg_icons", "agno", "websocket")


def _python() -> str:
    return str(PYTHON) if PYTHON.is_file() else sys.executable


def _load_search():
    spec = importlib.util.spec_from_file_location("search_icons", SEARCH)
    if spec is None or spec.loader is None:
        raise FileNotFoundError(SEARCH)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _load_overlay():
    spec = importlib.util.spec_from_file_location("overlay_native_slots", OVERLAY)
    if spec is None or spec.loader is None:
        raise FileNotFoundError(OVERLAY)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class IconEmbedPresenceTests(unittest.TestCase):
    def test_search_cli_and_live_recipe_exist(self) -> None:
        self.assertTrue(SEARCH.is_file(), SEARCH)
        self.assertTrue(RECIPE.is_file(), RECIPE)

    def test_scripts_do_not_call_ubrio_search_tool(self) -> None:
        source = SEARCH.read_text(encoding="utf-8")
        lowered = source.lower()
        self.assertNotIn("search_svg_icons", lowered)
        self.assertNotIn("from app.", source)
        self.assertNotIn("ubrio_agent_runtime", lowered)
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    self.assertNotIn(alias.name.split(".")[0].lower(), FORBIDDEN)
            elif isinstance(node, ast.ImportFrom) and node.module:
                self.assertNotIn(node.module.split(".")[0].lower(), FORBIDDEN)

    def test_live_docs_teach_local_search_not_ubrio_tool(self) -> None:
        recipe = RECIPE.read_text(encoding="utf-8")
        capability = CAPABILITY_MAP.read_text(encoding="utf-8")
        page = PAGE_GENERATION.read_text(encoding="utf-8")
        skill = SKILL.read_text(encoding="utf-8")
        for text in (recipe, capability, page):
            self.assertIn("search_icons.py", text)
            self.assertIn("data-icon-id", text)
            self.assertIn("data-icon-box", text)
        self.assertIn("search_icons.py", skill)
        self.assertIn("icon-embed.md", capability)
        self.assertIn("icon-embed.md", page)
        self.assertRegex(recipe, r"numbered|编号")
        lowered_recipe = recipe.lower()
        self.assertIn("emoji", lowered_recipe)
        self.assertIn("<use", recipe)
        self.assertNotRegex(recipe, r'data-icon-id="biz/')
        self.assertIn("search_svg_icons", recipe)
        readme = ICON_README.read_text(encoding="utf-8")
        self.assertNotIn("空的 `icon-index.json` 骨架", readme)
        self.assertIn("icon-index.json", readme)
        self.assertIn("lucide", readme.lower())


class IconSearchTests(unittest.TestCase):
    def test_search_returns_metadata_and_slot_example_without_payloads(self) -> None:
        module = _load_search()
        payload = module.search_svg_icon_library(
            icons_root=ICONS_ROOT,
            query="经营增长 柱状图 数据",
            style="line",
            limit=5,
        )
        self.assertTrue(payload.ok)
        self.assertTrue(payload.icons)
        self.assertLessEqual(len(payload.icons), 5)
        ids = [item["icon_id"] for item in payload.icons]
        self.assertTrue(
            any(item in ids for item in ("chart-bar", "chart-column", "chart-bar-big")),
            ids,
        )
        blob = json.dumps(payload.icons, ensure_ascii=False)
        self.assertNotIn('"path"', blob)
        self.assertNotIn("lucide/", blob)
        self.assertNotIn('"d":', blob)
        for item in payload.icons:
            self.assertIn("icon_id", item)
            self.assertIn("label", item)
            self.assertIn("slot_example", item)
            self.assertEqual(item["slot_example"]["data-icon-id"], item["icon_id"])
            self.assertEqual(item["slot_example"]["data-icon-box"], "x y w h")
            self.assertNotIn("path", item)
            self.assertNotIn("svg", item)

    def test_search_honors_category_style_limit_and_cli(self) -> None:
        module = _load_search()
        payload = module.search_svg_icon_library(
            icons_root=ICONS_ROOT,
            query="warning alert 风险 预警",
            category="account",
            style="line",
            limit=3,
        )
        self.assertTrue(payload.ok)
        self.assertLessEqual(len(payload.icons), 3)
        self.assertTrue(payload.icons)
        self.assertTrue(all(item.get("style") == "line" for item in payload.icons))
        self.assertTrue(all(item.get("category") == "account" for item in payload.icons))
        result = subprocess.run(
            [
                _python(),
                str(SEARCH),
                "--query",
                "target 目标",
                "--style",
                "line",
                "--limit",
                "4",
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        cli = json.loads(result.stdout)
        self.assertTrue(cli.get("ok"))
        self.assertIn("icons", cli)
        self.assertTrue(any(item["icon_id"] == "target" for item in cli["icons"]))
        self.assertNotIn("path", json.dumps(cli))

    def test_missing_ids_are_not_invented(self) -> None:
        module = _load_search()
        payload = module.search_svg_icon_library(
            icons_root=ICONS_ROOT,
            query="biz/data-bars",
            limit=5,
        )
        ids = [item["icon_id"] for item in payload.icons]
        self.assertNotIn("biz/data-bars", ids)
        self.assertNotIn("biz/target-eye", ids)


class IconExpandTests(unittest.TestCase):
    def test_expand_inlines_lucide_svgs_subdir_and_tints(self) -> None:
        module = _load_search()
        svg = """\
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1280 720">
  <g id="growth-icon" data-icon-id="chart-bar" data-icon-box="80 96 48 48"
     data-icon-color="#2563EB" data-icon-container="rounded_rect"/>
</svg>
"""
        result = module.expand_svg_icon_slots(svg, icons_root=ICONS_ROOT)
        self.assertTrue(result.ok, result.issues)
        self.assertEqual(result.expanded_count, 1)
        self.assertNotIn("data-icon-id", result.svg)
        self.assertIn("growth-icon-glyph", result.svg)
        self.assertIn("growth-icon-container", result.svg)
        self.assertIn("#2563EB", result.svg)
        self.assertIn("translate(", result.svg)
        root = ET.fromstring(result.svg)
        paths = [elem for elem in root.iter() if elem.tag.rsplit("}", 1)[-1] == "path"]
        self.assertTrue(paths)

    def test_expand_fail_closed_on_unknown_icon_id(self) -> None:
        module = _load_search()
        svg = """\
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1280 720">
  <g id="missing" data-icon-id="biz/data-bars" data-icon-box="80 96 48 48"/>
</svg>
"""
        result = module.expand_svg_icon_slots(svg, icons_root=ICONS_ROOT)
        self.assertFalse(result.ok)
        codes = {issue["code"] for issue in result.issues}
        self.assertIn("SVG_ICON_NOT_FOUND", codes)

    def test_overlay_validate_expands_and_blocks_unknown_ids(self) -> None:
        good = """\
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1280 720">
  <g id="ok-icon" data-icon-id="users" data-icon-box="64 64 40 40" data-icon-color="#0F172A"/>
</svg>
"""
        bad = """\
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1280 720">
  <g id="bad-icon" data-icon-id="biz/target-eye" data-icon-box="64 64 40 40"/>
</svg>
"""
        sidecar = json.dumps({"version": 1, "charts": [], "tables": []})
        with tempfile.TemporaryDirectory() as tmp:
            page = Path(tmp)
            native = page / "native-data.json"
            native.write_text(sidecar, encoding="utf-8")
            good_svg = page / "good.svg"
            bad_svg = page / "bad.svg"
            good_svg.write_text(good, encoding="utf-8")
            bad_svg.write_text(bad, encoding="utf-8")
            good_result = subprocess.run(
                [
                    _python(),
                    str(OVERLAY),
                    "--svg",
                    str(good_svg),
                    "--native-data",
                    str(native),
                    "--validate-only",
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(good_result.returncode, 0, good_result.stdout + good_result.stderr)
            good_payload = json.loads(good_result.stdout)
            self.assertGreaterEqual(int(good_payload.get("icon_expanded_count") or 0), 1)
            bad_result = subprocess.run(
                [
                    _python(),
                    str(OVERLAY),
                    "--svg",
                    str(bad_svg),
                    "--native-data",
                    str(native),
                    "--validate-only",
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertNotEqual(bad_result.returncode, 0, bad_result.stdout)
            payload = json.loads(bad_result.stdout)
            codes = {issue["code"] for issue in payload.get("issues") or []}
            self.assertIn("SVG_ICON_NOT_FOUND", codes)


if __name__ == "__main__":
    unittest.main()
