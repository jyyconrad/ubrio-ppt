"""Portable SVG DrawingML: write → validate → render (native.cjs is fallback only)."""

from __future__ import annotations

import ast
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
SVG_DIR = ROOT / "scripts" / "svg"
WRITE = SVG_DIR / "write_svg.py"
INSPECT = SVG_DIR / "inspect_svg_layers.py"
PATCH = SVG_DIR / "patch_svg_layer.py"
VALIDATE = SVG_DIR / "validate_svg_drawingml.py"
RENDER = SVG_DIR / "render_svg_drawingml.py"
EXAMPLES = SVG_DIR / "render_svg_ppt_examples.py"
OVERLAY = SVG_DIR / "overlay_native_slots.py"
SKILL = ROOT / "SKILL.md"
PAGE = ROOT / "references" / "page-generation.md"
CAPABILITY = ROOT / "references" / "generate" / "capability-map.md"
ROUTE = ROOT / "references" / "generate" / "route-evaluation.md"
AUTHORING = ROOT / "references" / "generate" / "methods" / "authoring-and-checks.md"
PARENT_AUTHORING = ROOT / "references" / "generate" / "authoring-and-checks.md"
CORE = (
    ROOT
    / "references"
    / "generate"
    / "original"
    / "slide-authoring"
    / "references"
    / "drawingml-svg-authoring-core.md"
)
PYTHON = ROOT / ".venv" / "bin" / "python"
FORBIDDEN = (
    "websocket",
    "consume_and_validate",
    "agno",
    "ubrio_agent_runtime",
)
MISSING_CONVERTER = (
    "没有自包含的 PPTX 转换器",
    "缺少自包含转换器",
    "当前不承诺转换可执行",
    "没有已验证的 SVG→PPTX 转换器",
)

CONTENT_SVG = """\
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1280 720" data-native-data-ref="native-data.json">
  <text id="title" x="64" y="80" fill="#0F172A" font-family="Microsoft YaHei" font-size="28">渠道转化已转向私域</text>
  <rect id="kpi-card" x="64" y="120" width="360" height="88" rx="8" fill="#EFF6FF" stroke="#2563EB"/>
  <text id="kpi-label" x="80" y="172" fill="#1E3A8A" font-family="Microsoft YaHei" font-size="16">私域成交转化 31%</text>
  <g id="growth-icon" data-icon-id="chart-bar" data-icon-box="448 136 48 48" data-icon-color="#2563EB"/>
  <text x="64" y="248" fill="#0F172A" font-family="Microsoft YaHei" font-size="16">渠道转化对比</text>
  <g id="bar-slot-1" data-role="native-chart-slot" data-native-chart="true"
     data-x="64" data-y="268" data-w="520" data-h="280">
    <rect x="64" y="268" width="520" height="280" fill="none" stroke="#94A3B8"/>
    <text x="80" y="300" fill="#64748B" font-size="12">占位：图表将 overlay</text>
  </g>
  <text x="64" y="584" fill="#64748B" font-family="Microsoft YaHei" font-size="12">来源：CRM 2026 Q2</text>
</svg>
"""

NATIVE_DATA = {
    "version": 1,
    "charts": [
        {
            "slot_id": "bar-slot-1",
            "kind": "bar",
            "labels": ["公域", "私域", "转介"],
            "series": [{"name": "转化", "values": [18, 31, 42], "color": "#2563EB"}],
        }
    ],
}

FULL_PAGE_BG = """\
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1280 720">
  <rect x="0" y="0" width="1280" height="720" fill="#F4F7FA"/>
  <text x="64" y="80" fill="#0F172A" font-family="Microsoft YaHei" font-size="28">标题</text>
</svg>
"""

FULL_PAGE_IMAGE = """\
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1280 720">
  <image x="0" y="0" width="1280" height="720" href="cover.png"/>
  <text x="64" y="80" fill="#0F172A" font-family="Microsoft YaHei" font-size="28">标题</text>
</svg>
"""


def _python() -> str:
    return str(PYTHON) if PYTHON.is_file() else sys.executable


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise FileNotFoundError(path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _slide_xml(path: Path) -> str:
    with zipfile.ZipFile(path) as zf:
        return zf.read("ppt/slides/slide1.xml").decode("utf-8", errors="ignore")


class DrawingMlPresenceTests(unittest.TestCase):
    def test_portable_clis_exist(self) -> None:
        for path in (WRITE, INSPECT, PATCH, VALIDATE, RENDER):
            self.assertTrue(path.is_file(), f"missing {path.relative_to(ROOT)}")

    def test_scripts_are_local_not_ubrio_runtime(self) -> None:
        for path in (WRITE, INSPECT, PATCH, VALIDATE, RENDER, EXAMPLES):
            self.assertTrue(path.is_file(), path)
            source = path.read_text(encoding="utf-8")
            lowered = source.lower()
            self.assertNotIn("from app.", source, path.name)
            self.assertNotIn("import app.", source, path.name)
            self.assertNotIn("app.contexts", source, path.name)
            self.assertNotIn("BACKEND_ROOT", source, path.name)
            for token in FORBIDDEN:
                self.assertNotIn(token, lowered, f"{path.name} mentions {token}")
            tree = ast.parse(source)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        self.assertNotIn(alias.name.split(".")[0].lower(), FORBIDDEN)
                elif isinstance(node, ast.ImportFrom) and node.module:
                    self.assertNotIn(node.module.split(".")[0].lower(), FORBIDDEN)

    def test_live_docs_teach_write_validate_render_not_missing_converter(self) -> None:
        self.assertTrue(CORE.is_file())
        skill = SKILL.read_text(encoding="utf-8")
        page = PAGE.read_text(encoding="utf-8")
        capability = CAPABILITY.read_text(encoding="utf-8")
        route = ROUTE.read_text(encoding="utf-8")
        authoring = AUTHORING.read_text(encoding="utf-8")
        parent = PARENT_AUTHORING.read_text(encoding="utf-8")
        for text in (skill, page, capability, authoring):
            self.assertIn("validate_svg_drawingml.py", text)
            self.assertIn("render_svg_drawingml.py", text)
        self.assertIn("write_svg.py", authoring)
        self.assertIn("inspect_svg_layers.py", authoring)
        self.assertIn("patch_svg_layer.py", authoring)
        self.assertIn("drawingml-svg-authoring-core", authoring)
        self.assertRegex(authoring, r"write\s*→\s*validate\s*→\s*render|write_svg.*validate_svg_drawingml.*render_svg_drawingml")
        for text in (skill, page, capability, route, authoring, parent):
            for phrase in MISSING_CONVERTER:
                self.assertNotIn(phrase, text, phrase)
        self.assertNotIn("已选活动默认路线", route)
        self.assertIn("fallback", authoring.lower())
        self.assertIn("native.cjs", authoring)
        self.assertIn("SVG_FULL_PAGE_BACKGROUND_FORBIDDEN", authoring)
        self.assertIn("SVG_FULL_PAGE_IMAGE_FORBIDDEN", authoring)
        self.assertIn("merge_paragraphs=False", authoring.replace(" ", ""))
        self.assertIn("render_svg_drawingml.py", route)
        self.assertIn("fallback", route.lower())


class DrawingMlValidateTests(unittest.TestCase):
    def test_full_page_background_and_image_are_blocking(self) -> None:
        module = _load(VALIDATE, "validate_svg_drawingml")
        bg = module.validate_svg_drawingml(
            svg_text=FULL_PAGE_BG,
            mode="fast",
            allow_framework_chrome=False,
        )
        self.assertFalse(bg["ok"])
        self.assertIn(
            "SVG_FULL_PAGE_BACKGROUND_FORBIDDEN",
            {issue["code"] for issue in bg["issues"]},
        )
        image = module.validate_svg_drawingml(
            svg_text=FULL_PAGE_IMAGE,
            mode="fast",
            allow_framework_chrome=False,
        )
        self.assertFalse(image["ok"])
        self.assertIn(
            "SVG_FULL_PAGE_IMAGE_FORBIDDEN",
            {issue["code"] for issue in image["issues"]},
        )

    def test_content_svg_expands_icons_diagnoses_slots_and_keeps_color_warnings_non_blocking(self) -> None:
        module = _load(VALIDATE, "validate_svg_drawingml")
        with tempfile.TemporaryDirectory() as tmp:
            page = Path(tmp)
            svg_path = page / "source.svg"
            svg_path.write_text(CONTENT_SVG, encoding="utf-8")
            (page / "native-data.json").write_text(
                json.dumps(NATIVE_DATA, ensure_ascii=False), encoding="utf-8"
            )
            report = module.validate_svg_drawingml(
                svg_path=svg_path,
                mode="full",
                allow_framework_chrome=False,
                style_manifest_snapshot={
                    "palette": {
                        "accent": "#EF4444",
                        "accent2": "#F97316",
                        "warning": "#F59E0B",
                        "success": "#22C55E",
                    }
                },
            )
        self.assertTrue(report["ok"], report.get("issues"))
        self.assertTrue(report.get("ready_to_render"))
        self.assertGreaterEqual(report.get("icon_expanded_count") or 0, 1)
        warning_codes = {item["code"] for item in report.get("warnings") or []}
        self.assertTrue(
            {"SLIDE_COLOR_SCHEME_DRIFT", "SLIDE_COLOR_PALETTE_OVERFLOW"} & warning_codes
            or not report.get("color_scheme_checked"),
            warning_codes,
        )
        self.assertIn("NATIVE_SLOT_PLACEHOLDER_TEXTS_WILL_BE_REMOVED", warning_codes)
        for issue in report.get("issues") or []:
            self.assertNotIn(
                issue["code"],
                {"SLIDE_COLOR_SCHEME_DRIFT", "SLIDE_COLOR_PALETTE_OVERFLOW"},
            )

    def test_inspect_and_patch_operate_on_layer_ids(self) -> None:
        inspect = _load(INSPECT, "inspect_svg_layers")
        patch = _load(PATCH, "patch_svg_layer")
        layers, warnings = inspect.inspect_svg_layers_from_text(CONTENT_SVG)
        ids = {item["id"] for item in layers}
        self.assertIn("title", ids)
        self.assertIn("bar-slot-1", ids)
        self.assertLessEqual(len(layers), 80)
        self.assertEqual(warnings, [])
        patched, summary = patch.patch_svg_layer_text(
            CONTENT_SVG,
            layer_id="kpi-label",
            operation="replace",
            svg_fragment='<text id="kpi-label" x="80" y="172" fill="#1E3A8A" font-family="Microsoft YaHei" font-size="16">私域成交转化 42%</text>',
        )
        self.assertIn("私域成交转化 42%", patched)
        self.assertEqual(summary["operation"], "replace")


class DrawingMlRenderTests(unittest.TestCase):
    def test_write_validate_render_cli_makes_native_drawingml_pptx(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            page = Path(tmp)
            svg_path = page / "source.svg"
            native_path = page / "native-data.json"
            pptx_path = page / "page.pptx"
            write = subprocess.run(
                [_python(), str(WRITE), "--output", str(svg_path)],
                input=CONTENT_SVG,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(write.returncode, 0, write.stderr + write.stdout)
            native_path.write_text(json.dumps(NATIVE_DATA, ensure_ascii=False), encoding="utf-8")
            validate = subprocess.run(
                [_python(), str(VALIDATE), "--svg", str(svg_path), "--mode", "full"],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(validate.returncode, 0, validate.stderr + validate.stdout)
            payload = json.loads(validate.stdout)
            self.assertTrue(payload.get("ready_to_render") or payload.get("ok"))
            render = subprocess.run(
                [
                    _python(),
                    str(RENDER),
                    "--svg",
                    str(svg_path),
                    "--native-data",
                    str(native_path),
                    "--output",
                    str(pptx_path),
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(render.returncode, 0, render.stderr + render.stdout)
            result = json.loads(render.stdout)
            self.assertTrue(result.get("ok"), result)
            self.assertTrue(pptx_path.is_file())
            xml = _slide_xml(pptx_path)
            self.assertIn("<p:sp", xml)
            self.assertIn("渠道转化已转向私域", xml)
            self.assertNotIn("asvg:svgBlip", xml)
            with zipfile.ZipFile(pptx_path) as zf:
                chart_xml = "\n".join(
                    zf.read(name).decode("utf-8", errors="ignore")
                    for name in zf.namelist()
                    if name.startswith("ppt/charts/") and name.endswith(".xml")
                )
            self.assertIn("barChart", chart_xml)
            adapter_source = (SVG_DIR / "drawingml" / "adapter.py").read_text(encoding="utf-8")
            self.assertIn("merge_paragraphs=False", adapter_source.replace(" ", ""))
            self.assertIn("use_compat_mode=False", adapter_source.replace(" ", ""))
            self.assertIn("use_native_shapes=True", adapter_source.replace(" ", ""))

    def test_render_blocks_full_page_background_without_pptx(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            page = Path(tmp)
            svg_path = page / "source.svg"
            svg_path.write_text(FULL_PAGE_BG, encoding="utf-8")
            pptx_path = page / "page.pptx"
            render = subprocess.run(
                [
                    _python(),
                    str(RENDER),
                    "--svg",
                    str(svg_path),
                    "--output",
                    str(pptx_path),
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertNotEqual(render.returncode, 0)
            self.assertFalse(pptx_path.exists())
            payload = json.loads(render.stdout)
            self.assertIn(
                "SVG_FULL_PAGE_BACKGROUND_FORBIDDEN",
                {issue["code"] for issue in payload.get("issues") or []},
            )


if __name__ == "__main__":
    unittest.main()
