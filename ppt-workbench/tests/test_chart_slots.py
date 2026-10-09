"""Native chart/table slots: sidecar JSON + SVG geometry + python-pptx overlay."""

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
NATIVE_COMPONENTS = ROOT / "references" / "generate" / "methods" / "native-components.md"
CAPABILITY_MAP = ROOT / "references" / "generate" / "capability-map.md"
GOLD_PAGES = ROOT / "references" / "generate" / "methods" / "gold-pages.md"
CHART_GOLD = (
    ROOT
    / "references"
    / "generate"
    / "original"
    / "slide-authoring"
    / "assets"
    / "examples"
    / "svg-ppt"
    / "decks"
    / "scenario-chart-type-gold-pages"
)
UNSUPPORTED_KINDS = {"sankey", "combo", "bubble"}
PYTHON = ROOT / ".venv" / "bin" / "python"


def _python() -> str:
    return str(PYTHON) if PYTHON.is_file() else sys.executable


def _load_overlay():
    spec = importlib.util.spec_from_file_location("overlay_native_slots", OVERLAY)
    if spec is None or spec.loader is None:
        raise FileNotFoundError(OVERLAY)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _pptx_chart_tags(path: Path) -> set[str]:
    tags: set[str] = set()
    with zipfile.ZipFile(path) as zf:
        for name in zf.namelist():
            if not name.startswith("ppt/charts/") or not name.endswith(".xml"):
                continue
            root = ET.fromstring(zf.read(name))
            for elem in root.iter():
                local = elem.tag.rsplit("}", 1)[-1]
                if local in {"barChart", "lineChart", "pieChart", "areaChart"}:
                    tags.add(local)
    return tags


def _pptx_has_table(path: Path) -> bool:
    with zipfile.ZipFile(path) as zf:
        for name in zf.namelist():
            if not name.startswith("ppt/slides/slide") or not name.endswith(".xml"):
                continue
            text = zf.read(name).decode("utf-8", errors="ignore")
            if "<a:tbl" in text or "a:tbl>" in text:
                return True
    return False


def _pptx_has_freeform(path: Path) -> bool:
    with zipfile.ZipFile(path) as zf:
        for name in zf.namelist():
            if not name.startswith("ppt/slides/slide") or not name.endswith(".xml"):
                continue
            text = zf.read(name).decode("utf-8", errors="ignore")
            if "custGeom" in text:
                return True
    return False


FIXTURE_SVG = """\
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1280 720" data-native-data-ref="native-data.json">
  <text x="64" y="92" fill="#0F172A" font-size="18" font-weight="700">渠道转化对比</text>
  <g id="bar-slot-1" data-role="native-chart-slot" data-native-chart="true"
     data-x="64" data-y="120" data-w="520" data-h="280">
    <rect x="64" y="120" width="520" height="280" fill="none" stroke="#94A3B8"/>
  </g>
  <text x="64" y="436" fill="#64748B" font-size="13">来源：CRM 2026 Q2</text>
  <text x="640" y="92" fill="#0F172A" font-size="18" font-weight="700">成本结构</text>
  <g id="pie-slot-1" data-role="native-chart-slot" data-native-chart="true"
     data-x="640" data-y="120" data-w="280" data-h="280">
    <rect x="640" y="120" width="280" height="280" fill="none" stroke="#94A3B8"/>
  </g>
  <text x="64" y="500" fill="#0F172A" font-size="18" font-weight="700">营收桥</text>
  <g id="waterfall-slot-1" data-role="native-chart-slot" data-native-chart="true"
     data-x="64" data-y="520" data-w="520" data-h="160">
    <rect x="64" y="520" width="520" height="160" fill="none" stroke="#94A3B8"/>
  </g>
  <text x="640" y="500" fill="#0F172A" font-size="18" font-weight="700">方案对比</text>
  <g id="table-slot-1" data-role="native-table-slot" data-native-table="true"
     data-x="640" data-y="520" data-w="520" data-h="160">
    <rect x="640" y="520" width="520" height="160" fill="none" stroke="#94A3B8"/>
  </g>
</svg>
"""

FIXTURE_NATIVE = {
    "version": 1,
    "charts": [
        {
            "slot_id": "bar-slot-1",
            "kind": "bar",
            "labels": ["公域", "私域", "转介"],
            "series": [{"name": "转化率", "values": [18, 31, 42], "color": "#2563EB"}],
        },
        {
            "slot_id": "pie-slot-1",
            "kind": "pie",
            "labels": ["云", "人力", "投放"],
            "series": [{"name": "占比", "values": [38, 31, 31], "color": "#2563EB"}],
            "colors": ["#2563EB", "#16A34A", "#F59E0B"],
        },
        {
            "slot_id": "waterfall-slot-1",
            "kind": "waterfall",
            "labels": ["期初", "新增", "流失", "期末"],
            "segments": [
                {"type": "total", "value": 320},
                {"type": "increase", "delta": 95},
                {"type": "decrease", "delta": -58},
                {"type": "total"},
            ],
        },
    ],
    "tables": [
        {
            "slot_id": "table-slot-1",
            "columns": ["维度", "方案A", "方案B"],
            "rows": [["成本", "中", "高"], ["周期", "短", "长"]],
        }
    ],
}

SANKEY_SVG = """\
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1280 720" data-native-data-ref="native-data.json">
  <text x="120" y="160" fill="#0F172A" font-size="18">预算流向</text>
  <g id="sankey-slot-1" data-role="native-sankey-slot" data-native-sankey="true"
     data-x="120" data-y="200" data-w="1000" data-h="400">
    <rect x="120" y="200" width="1000" height="400" fill="none" stroke="#CBD5E1"/>
  </g>
</svg>
"""

SANKEY_NATIVE = {
    "version": 1,
    "sankeys": [
        {
            "slot_id": "sankey-slot-1",
            "flows": [
                {"source": "总预算", "target": "研发", "value": 480},
                {"source": "总预算", "target": "市场", "value": 300},
                {"source": "研发", "target": "平台", "value": 300},
            ],
        }
    ],
}


class ChartSlotRecipeTests(unittest.TestCase):
    def test_overlay_script_is_local_python_pptx_not_ubrio_runtime(self) -> None:
        self.assertTrue(OVERLAY.is_file(), "missing scripts/svg/overlay_native_slots.py")
        source = OVERLAY.read_text(encoding="utf-8")
        lowered = source.lower()
        self.assertNotIn("app.contexts", source)
        self.assertNotIn("from agno", lowered)
        self.assertNotIn("import agno", lowered)
        self.assertIn("python-pptx", lowered)
        self.assertIn("charts", source)
        self.assertIn("tables", source)

    def test_native_components_is_live_svg_slot_recipe(self) -> None:
        self.assertTrue(NATIVE_COMPONENTS.is_file())
        text = NATIVE_COMPONENTS.read_text(encoding="utf-8")
        for marker in (
            "native-data.json",
            "charts[]",
            "tables[]",
            "native-chart-slot",
            "native-table-slot",
            "overlay_native_slots.py",
            "320",
            "200",
            "140",
            "80",
            "scenario-chart-type-gold-pages",
            "--validate-only",
        ):
            self.assertIn(marker, text, marker)
        self.assertIn("sankey", text.lower())
        self.assertRegex(text, r"28\s*[–-]\s*40")
        self.assertIn("36", text)
        lowered = text.lower()
        self.assertIn("validate_svg_drawingml", lowered)
        self.assertIn("render_svg_drawingml_slide", lowered)
        self.assertIn("save_file", lowered)
        self.assertIn("never charts[].kind=sankey", lowered.replace("`", "").replace('"', "").replace("'", ""))
        self.assertIn("native.cjs", text)
        self.assertIn("fallback", lowered)

    def test_capability_map_chart_rows_point_at_overlay_recipe(self) -> None:
        text = CAPABILITY_MAP.read_text(encoding="utf-8")
        self.assertIn("overlay_native_slots.py", text)
        self.assertIn("native-data.json", text)
        self.assertIn("native-chart-slot", text)
        self.assertIn("native-components.md", text)
        self.assertIn("pie", text.lower())
        self.assertIn("waterfall", text.lower())
        self.assertIn("sankey", text.lower())
        self.assertNotRegex(text, r"PptxGenJS `bar`/`line` 仍可用")

    def test_gold_pages_maps_render_tools_to_overlay_cli(self) -> None:
        text = GOLD_PAGES.read_text(encoding="utf-8")
        self.assertIn("overlay_native_slots.py", text)
        self.assertIn("--validate-only", text)
        self.assertIn("native-data.json", text)

    def test_chart_gold_samples_are_sidecar_not_kind_combo(self) -> None:
        for name in (
            "01-bar-comparison.native-data.json",
            "02-line-trend.native-data.json",
            "03-pie-composition.native-data.json",
            "04-combo-dashboard.native-data.json",
        ):
            payload = json.loads((CHART_GOLD / name).read_text(encoding="utf-8"))
            for chart in payload.get("charts") or []:
                self.assertNotIn(chart.get("kind"), UNSUPPORTED_KINDS, name)


class ChartSlotOverlayTests(unittest.TestCase):
    def test_validate_rejects_unsupported_chart_kinds_and_tiny_boxes(self) -> None:
        module = _load_overlay()
        svg = """\
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1280 720" data-native-data-ref="native-data.json">
  <g id="bad-slot" data-role="native-chart-slot" data-native-chart="true"
     data-x="80" data-y="80" data-w="100" data-h="40">
    <rect x="80" y="80" width="100" height="40" fill="none"/>
    <text x="90" y="100">渠道转化对比</text>
  </g>
</svg>
"""
        native = {
            "charts": [
                {
                    "slot_id": "bad-slot",
                    "kind": "sankey",
                    "labels": ["A"],
                    "series": [{"name": "x", "values": [1]}],
                }
            ]
        }
        report = module.diagnose_native_slots(svg, native)
        codes = {issue["code"] for issue in report["issues"] + report.get("warnings", [])}
        self.assertIn("NATIVE_CHART_SLOT_UNSUPPORTED_TYPE", codes)
        self.assertIn("NATIVE_CHART_SLOT_TOO_SMALL", codes)
        self.assertTrue(report.get("ok") is False)

    def test_validate_gold_bar_sample_and_title_outside_slot(self) -> None:
        module = _load_overlay()
        svg_path = CHART_GOLD / "01-bar-comparison.svg"
        native_path = CHART_GOLD / "01-bar-comparison.native-data.json"
        svg = svg_path.read_text(encoding="utf-8")
        native = json.loads(native_path.read_text(encoding="utf-8"))
        report = module.diagnose_native_slots(svg, native)
        blocking = [issue["code"] for issue in report["issues"] if issue.get("severity") != "warning"]
        self.assertNotIn("NATIVE_CHART_SLOT_MISSING_DATA", blocking)
        self.assertNotIn("NATIVE_CHART_SLOT_UNSUPPORTED_TYPE", blocking)
        root = ET.fromstring(svg)
        slot = next(elem for elem in root.iter() if elem.get("id") == "bar-slot-1")
        inner = " ".join(
            (child.text or "") for child in slot.iter() if child.tag.rsplit("}", 1)[-1] == "text"
        )
        self.assertNotIn("渠道转化率对比：私域与老客转介显著领先", inner)
        self.assertIn("渠道转化对比", svg)

    def test_overlay_writes_bar_line_pie_waterfall_and_table(self) -> None:
        module = _load_overlay()
        with tempfile.TemporaryDirectory() as tmp:
            page = Path(tmp)
            svg_path = page / "source.svg"
            native_path = page / "native-data.json"
            out_path = page / "page.pptx"
            svg_path.write_text(FIXTURE_SVG, encoding="utf-8")
            native_path.write_text(json.dumps(FIXTURE_NATIVE, ensure_ascii=False), encoding="utf-8")
            result = module.overlay_native_slots(
                svg_text=FIXTURE_SVG,
                native_data=FIXTURE_NATIVE,
                output=out_path,
            )
            self.assertTrue(out_path.is_file(), result)
            tags = _pptx_chart_tags(out_path)
            self.assertIn("barChart", tags)
            self.assertIn("pieChart", tags)
            self.assertTrue(_pptx_has_table(out_path))
            self.assertGreaterEqual(result.get("chart_count", 0), 3)
            self.assertGreaterEqual(result.get("table_count", 0), 1)

    def test_cli_validate_then_overlay_sankey_geometry_or_explicit_fallback(self) -> None:
        self.assertTrue(OVERLAY.is_file())
        with tempfile.TemporaryDirectory() as tmp:
            page = Path(tmp)
            svg_path = page / "source.svg"
            native_path = page / "native-data.json"
            out_path = page / "page.pptx"
            svg_path.write_text(SANKEY_SVG, encoding="utf-8")
            native_path.write_text(json.dumps(SANKEY_NATIVE, ensure_ascii=False), encoding="utf-8")
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
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(validate.returncode, 0, validate.stderr)
            payload = json.loads(validate.stdout)
            self.assertTrue(payload.get("ok"), payload)
            kinds = [
                chart.get("kind")
                for chart in json.loads(native_path.read_text(encoding="utf-8")).get("charts") or []
            ]
            self.assertNotIn("sankey", kinds)
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
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(overlay.returncode, 0, overlay.stderr)
            report = json.loads(overlay.stdout)
            self.assertTrue(out_path.is_file())
            sankey_ok = bool(report.get("sankey_count")) and _pptx_has_freeform(out_path)
            fallback = report.get("sankey_fallback")
            self.assertTrue(
                sankey_ok or fallback,
                f"sankey must overlay geometrically or set explicit fallback: {report}",
            )

    def test_cli_overlays_gold_pie_sample(self) -> None:
        self.assertTrue(OVERLAY.is_file())
        with tempfile.TemporaryDirectory() as tmp:
            out_path = Path(tmp) / "pie.pptx"
            proc = subprocess.run(
                [
                    _python(),
                    str(OVERLAY),
                    "--svg",
                    str(CHART_GOLD / "03-pie-composition.svg"),
                    "--native-data",
                    str(CHART_GOLD / "03-pie-composition.native-data.json"),
                    "--output",
                    str(out_path),
                ],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertIn("pieChart", _pptx_chart_tags(out_path))


if __name__ == "__main__":
    unittest.main()
