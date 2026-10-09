"""Three image owners: deck-framework plate, native.cjs body picture, SVG native-image-slot."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
OVERLAY = ROOT / "scripts" / "svg" / "overlay_native_slots.py"
BUILDER = ROOT / "scripts" / "svg" / "build_gold_svg_page.py"
RECIPE = ROOT / "references" / "generate" / "methods" / "image-owners.md"
CAPABILITY_MAP = ROOT / "references" / "generate" / "capability-map.md"
PAGE_GENERATION = ROOT / "references" / "page-generation.md"
GOLD_PAGES = ROOT / "references" / "generate" / "methods" / "gold-pages.md"
NATIVE_COMPONENTS = ROOT / "references" / "generate" / "methods" / "native-components.md"
SKILL = ROOT / "SKILL.md"
EVIDENCE_PNG = ROOT / "assets" / "examples" / "evidence-synthetic.png"
PYTHON = ROOT / ".venv" / "bin" / "python"
FORBIDDEN_OWNERS = (
    "merge_native_data_image",
    "merge_slide_picture_binding",
    "merge_slide_background_binding",
    "ask_user",
    "/v1/files",
)


def _python() -> str:
    return str(PYTHON) if PYTHON.is_file() else sys.executable


def _load_overlay():
    spec = importlib.util.spec_from_file_location("overlay_native_slots", OVERLAY)
    if spec is None or spec.loader is None:
        raise FileNotFoundError(OVERLAY)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_builder():
    spec = importlib.util.spec_from_file_location("build_gold_svg_page", BUILDER)
    if spec is None or spec.loader is None:
        raise FileNotFoundError(BUILDER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _pptx_has_picture(path: Path) -> bool:
    with zipfile.ZipFile(path) as zf:
        names = zf.namelist()
        if not any(name.startswith("ppt/media/") for name in names):
            return False
        for name in names:
            if not name.startswith("ppt/slides/slide") or not name.endswith(".xml"):
                continue
            text = zf.read(name).decode("utf-8", errors="ignore")
            if "<p:pic" in text or "p:pic>" in text:
                return True
    return False


def _pptx_has_table(path: Path) -> bool:
    with zipfile.ZipFile(path) as zf:
        for name in zf.namelist():
            if not name.startswith("ppt/slides/slide") or not name.endswith(".xml"):
                continue
            text = zf.read(name).decode("utf-8", errors="ignore")
            if "<a:tbl" in text or "a:tbl>" in text:
                return True
    return False


IMAGE_SVG = """\
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1280 720" data-native-data-ref="native-data.json">
  <text x="64" y="72" fill="#0F172A" font-size="22" font-weight="700">台账第三项仍为待验收</text>
  <text x="720" y="108" fill="#0F172A" font-size="16">可确认：状态为待验收</text>
  <g id="screenshot-proof-1" data-role="native-image-slot" data-native-image="true"
     data-x="64" data-y="120" data-w="620" data-h="360">
    <rect x="64" y="120" width="620" height="360" fill="none" stroke="#94A3B8" rx="12"/>
  </g>
  <text x="64" y="516" fill="#64748B" font-size="13">来源：包内合成台账渲染图</text>
  <text x="64" y="540" fill="#334155" font-size="14">不能推出：已延期或客户拒绝验收</text>
  <g id="status-table-1" data-role="native-table-slot" data-native-table="true"
     data-x="720" data-y="140" data-w="496" data-h="200">
    <rect x="720" y="140" width="496" height="200" fill="none" stroke="#94A3B8"/>
  </g>
</svg>
"""


class ImageOwnersPresenceTests(unittest.TestCase):
    def test_live_recipe_teaches_three_owners(self) -> None:
        self.assertTrue(RECIPE.is_file(), RECIPE)
        recipe = RECIPE.read_text(encoding="utf-8")
        for marker in (
            "deck-framework.json",
            "native.cjs",
            "native-image-slot",
            "native-data.json",
            "asset_key",
            "image()",
        ):
            self.assertIn(marker, recipe, marker)
        lowered = recipe.lower()
        self.assertIn("<image", recipe)
        self.assertIn("href", lowered)
        self.assertIn("previewurl", lowered)
        self.assertIn("merge_native_data_image", lowered)
        self.assertRegex(recipe, r"native-table-slot")
        for owner in FORBIDDEN_OWNERS:
            self.assertIn(owner, recipe, f"recipe must name-and-ban {owner}")

    def test_capability_map_and_page_generation_point_at_three_owner_recipe(self) -> None:
        capability = CAPABILITY_MAP.read_text(encoding="utf-8")
        page = PAGE_GENERATION.read_text(encoding="utf-8")
        skill = SKILL.read_text(encoding="utf-8")
        gold = GOLD_PAGES.read_text(encoding="utf-8")
        native = NATIVE_COMPONENTS.read_text(encoding="utf-8")
        for text in (capability, page):
            self.assertIn("image-owners.md", text)
            self.assertIn("native-image-slot", text)
            self.assertIn("deck-framework.json", text)
        self.assertIn("image-owners.md", skill)
        self.assertIn("native-image-slot", gold)
        self.assertIn("image-owners.md", gold)
        self.assertIn("image-owners.md", native)
        self.assertNotRegex(capability, r"merge_native_data_image")
        self.assertNotRegex(page, r"merge_slide_picture_binding")

    def test_recipe_keeps_tables_native_and_captions_beside_slots(self) -> None:
        recipe = RECIPE.read_text(encoding="utf-8")
        page = PAGE_GENERATION.read_text(encoding="utf-8")
        for text in (recipe, page):
            self.assertRegex(text, r"native-table-slot")
            self.assertRegex(text, r"caption|说明|能确认|不能推出")
        self.assertRegex(recipe, r"手绘|drawn grid|rect 单元格")


class ImageOverlayTests(unittest.TestCase):
    def test_validate_blocks_svg_image_href_remote_url_and_previewurl(self) -> None:
        module = _load_overlay()
        href_svg = """\
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 1280 720">
  <image href="https://cdn.example/cover.jpg" x="0" y="0" width="1280" height="720"/>
</svg>
"""
        report = module.diagnose_native_slots(href_svg, {"images": []})
        codes = {issue["code"] for issue in report["issues"]}
        self.assertIn("SVG_IMAGE_HREF_FORBIDDEN", codes)
        self.assertFalse(report.get("ok"))

        remote = {
            "images": [
                {
                    "slot_id": "screenshot-proof-1",
                    "url": "https://cdn.example/shot.png",
                    "previewUrl": "https://cdn.example/preview.png",
                }
            ]
        }
        report = module.diagnose_native_slots(IMAGE_SVG, remote)
        codes = {issue["code"] for issue in report["issues"]}
        self.assertTrue(
            {"NATIVE_IMAGE_SLOT_UNCONTROLLED_EXTERNAL_URL", "NATIVE_IMAGE_SLOT_PREVIEW_URL_FORBIDDEN"}
            & codes,
            codes,
        )
        self.assertFalse(report.get("ok"))

    def test_validate_blocks_full_page_image_slot_and_missing_local_asset(self) -> None:
        module = _load_overlay()
        full_page = """\
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1280 720" data-native-data-ref="native-data.json">
  <g id="cover-plate" data-role="native-image-slot" data-native-image="true"
     data-x="0" data-y="0" data-w="1280" data-h="720">
    <rect x="0" y="0" width="1280" height="720" fill="none"/>
  </g>
</svg>
"""
        native = {"images": [{"slot_id": "cover-plate", "asset_key": "cover.png"}]}
        report = module.diagnose_native_slots(full_page, native)
        codes = {issue["code"] for issue in report["issues"]}
        self.assertIn("SVG_FULL_PAGE_IMAGE_FORBIDDEN", codes)
        self.assertFalse(report.get("ok"))

        missing = module.diagnose_native_slots(IMAGE_SVG, {"images": []})
        missing_codes = {issue["code"] for issue in missing["issues"]}
        self.assertIn("NATIVE_IMAGE_SLOT_MISSING_DATA", missing_codes)

    def test_overlay_embeds_local_png_and_keeps_native_table(self) -> None:
        module = _load_overlay()
        self.assertTrue(EVIDENCE_PNG.is_file(), EVIDENCE_PNG)
        with tempfile.TemporaryDirectory() as tmp:
            page = Path(tmp)
            png = page / "evidence-synthetic.png"
            png.write_bytes(EVIDENCE_PNG.read_bytes())
            native = {
                "version": 1,
                "images": [
                    {
                        "slot_id": "screenshot-proof-1",
                        "asset_key": "evidence-synthetic.png",
                        "fit": "contain",
                    }
                ],
                "tables": [
                    {
                        "slot_id": "status-table-1",
                        "columns": ["Owner", "状态", "口径"],
                        "rows": [["华南项目", "待验收", "台账第三项"]],
                    }
                ],
            }
            out_path = page / "page.pptx"
            result = module.overlay_native_slots(
                svg_text=IMAGE_SVG,
                native_data=native,
                output=out_path,
                assets_dir=page,
            )
            self.assertTrue(out_path.is_file(), result)
            self.assertGreaterEqual(int(result.get("image_count") or 0), 1, result)
            self.assertGreaterEqual(int(result.get("table_count") or 0), 1, result)
            self.assertTrue(_pptx_has_picture(out_path))
            self.assertTrue(_pptx_has_table(out_path))

    def test_cli_validate_then_overlay_local_image_slot(self) -> None:
        self.assertTrue(OVERLAY.is_file())
        self.assertTrue(EVIDENCE_PNG.is_file())
        with tempfile.TemporaryDirectory() as tmp:
            page = Path(tmp)
            png = page / "evidence-synthetic.png"
            png.write_bytes(EVIDENCE_PNG.read_bytes())
            svg_path = page / "source.svg"
            native_path = page / "native-data.json"
            out_path = page / "page.pptx"
            svg_path.write_text(IMAGE_SVG, encoding="utf-8")
            native_path.write_text(
                json.dumps(
                    {
                        "version": 1,
                        "images": [
                            {
                                "slot_id": "screenshot-proof-1",
                                "asset_key": "evidence-synthetic.png",
                                "fit": "contain",
                            }
                        ],
                        "tables": [
                            {
                                "slot_id": "status-table-1",
                                "columns": ["Owner", "状态"],
                                "rows": [["华南项目", "待验收"]],
                            }
                        ],
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            validate = subprocess.run(
                [
                    _python(),
                    str(OVERLAY),
                    "--svg",
                    str(svg_path),
                    "--native-data",
                    str(native_path),
                    "--validate-only",
                ],
                cwd=page,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(validate.returncode, 0, validate.stdout + validate.stderr)
            overlay = subprocess.run(
                [
                    _python(),
                    str(OVERLAY),
                    "--svg",
                    str(svg_path),
                    "--native-data",
                    str(native_path),
                    "--output",
                    str(out_path),
                ],
                cwd=page,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(overlay.returncode, 0, overlay.stdout + overlay.stderr)
            payload = json.loads(overlay.stdout)
            self.assertGreaterEqual(int(payload.get("image_count") or 0), 1, payload)
            self.assertTrue(_pptx_has_picture(out_path))
            self.assertTrue(_pptx_has_table(out_path))


class GoldEvidenceImageSlotTests(unittest.TestCase):
    def test_gold_builder_emits_native_image_slot_not_evidence_asset_slot(self) -> None:
        builder = _load_builder()
        spec = {
            "schema_version": "gold_page_spec/v1",
            "theme_id": "business_blue",
            "layout": "gold_cards",
            "page_role": "content",
            "title": "台账第三项仍为待验收，不能推出客户已拒收",
            "key_message": "截图只证明当前状态，不证明延期原因。",
            "structure_hierarchy": {
                "semantic_layer": ["验收判断", "截图证据", "行动", "口径"],
                "narrative_layer": ["结论先行", "证据链", "解释影响", "行动闭环"],
                "visual_layer": ["main-title", "key-message", "metric-strip", "main-content"],
                "geometry_layer": ["title-band", "metric-strip", "main-body", "source-note"],
                "svg_group_layer": ["main-title-block", "metrics-panel", "main-content", "source-note"],
            },
            "metrics": [
                {"label": "待验收", "value": "1", "note": "台账第三项"},
                {"label": "已验收", "value": "2", "note": "同批"},
                {"label": "风险", "value": "口径待核", "note": "不推断延期"},
            ],
            "groups": [
                {
                    "title": "经营判断",
                    "claim": "第三项仍待验收",
                    "evidence": ["台账状态=待验收"],
                    "explanation": "截图不能推出拒收",
                    "action": "核对手续",
                },
                {
                    "title": "证据链",
                    "claim": "状态来自导出截图",
                    "evidence": ["合成台账渲染图"],
                    "explanation": "来源已标注",
                    "action": "保留口径",
                },
                {
                    "title": "行动",
                    "claim": "先核对手续再升级",
                    "evidence": ["Owner 待定项需点名"],
                    "explanation": "无原因资料不编造",
                    "action": "补齐 Owner",
                },
            ],
            "sources": [{"text": "包内合成台账渲染图", "date": "2026-06"}],
            "evidence_asset_slots": [
                {
                    "id": "screenshot-proof-1",
                    "title": "线索池截图",
                    "caption": "可确认：状态为待验收",
                    "source": "包内合成台账",
                    "asset_key": "evidence-synthetic.png",
                    "box": {"x": 544.0, "y": 320.0, "w": 360.0, "h": 200.0},
                }
            ],
        }
        native = builder.build_native_data(builder.normalize_page_spec(spec))
        images = native.get("images") or []
        self.assertTrue(images, native)
        self.assertEqual(images[0].get("slot_id"), "screenshot-proof-1")
        self.assertEqual(images[0].get("asset_key"), "evidence-synthetic.png")
        self.assertNotIn("url", images[0])
        self.assertNotIn("previewUrl", images[0])
        svg = builder.build_svg_page(spec, native_data_ref="native-data.json")
        self.assertIn('data-role="native-image-slot"', svg)
        self.assertIn('data-native-image="true"', svg)
        self.assertNotIn("evidence-asset-slot", svg)
        self.assertNotIn("<image", svg)
        root = ET.fromstring(svg)
        slot = next(elem for elem in root.iter() if elem.get("id") == "screenshot-proof-1")
        inner = " ".join(
            (child.text or "").strip()
            for child in slot.iter()
            if child.tag.rsplit("}", 1)[-1] == "text"
        )
        self.assertNotIn("线索池截图", inner)
        self.assertIn("线索池截图", svg)
        self.assertIn("可确认：状态为待验收", svg)

    def test_gold_builder_skips_image_slot_without_local_asset(self) -> None:
        builder = _load_builder()
        spec = {
            "schema_version": "gold_page_spec/v1",
            "theme_id": "business_blue",
            "layout": "gold_cards",
            "page_role": "content",
            "title": "没有本地截图时先跳过图位",
            "key_message": "缺图不画 SVG image href，也不留无法 overlay 的槽。",
            "structure_hierarchy": {
                "semantic_layer": ["判断", "证据", "行动", "口径"],
                "narrative_layer": ["结论先行", "证据链", "解释", "行动"],
                "visual_layer": ["main-title", "key-message", "main-content"],
                "geometry_layer": ["title-band", "main-body"],
                "svg_group_layer": ["main-title-block", "main-content"],
            },
            "metrics": [
                {"label": "A", "value": "1", "note": "n"},
                {"label": "B", "value": "2", "note": "n"},
                {"label": "C", "value": "3", "note": "n"},
            ],
            "groups": [
                {
                    "title": "判断",
                    "claim": "缺图",
                    "evidence": ["无本地文件"],
                    "explanation": "跳过槽",
                    "action": "待补文件",
                },
                {
                    "title": "证据",
                    "claim": "不画 href",
                    "evidence": ["无 URL"],
                    "explanation": "本地 only",
                    "action": "等文件",
                },
                {
                    "title": "行动",
                    "claim": "有文件再写 slot",
                    "evidence": ["asset_key 规则"],
                    "explanation": "overlay 才能落图",
                    "action": "补 PNG",
                },
            ],
            "sources": [{"text": "无图", "date": "2026-06"}],
            "evidence_asset_slots": [
                {
                    "id": "screenshot-proof-1",
                    "title": "未到的截图",
                    "url": "https://cdn.example/shot.png",
                    "box": {"x": 544.0, "y": 320.0, "w": 360.0, "h": 200.0},
                }
            ],
        }
        normalized = builder.normalize_page_spec(spec)
        native = builder.build_native_data(normalized)
        self.assertEqual(native.get("images") or [], [])
        svg = builder.build_svg_page(normalized, native_data_ref="native-data.json")
        self.assertNotIn("native-image-slot", svg)
        self.assertNotIn("evidence-asset-slot", svg)
        self.assertNotIn("<image", svg)
        self.assertNotIn("https://cdn.example/shot.png", svg)


if __name__ == "__main__":
    unittest.main()
