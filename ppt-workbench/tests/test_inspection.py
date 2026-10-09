import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("inspect_pptx", ROOT / "scripts/inspect_pptx.py")
inspector = importlib.util.module_from_spec(spec)
spec.loader.exec_module(inspector)
SAMPLE = ROOT / "assets/examples/output/03-target.pptx"


class InspectionTests(unittest.TestCase):
    def test_sample_chart_objects_and_cached_values(self):
        report = inspector.inspect(SAMPLE)
        self.assertTrue(report["structure_passed"])
        chart = report["pages"][0]["charts"][0]
        self.assertEqual(chart["series"][0]["values"], ["400", "300", "300"])
        self.assertEqual(chart["series"][0]["labels"], ["华东", "华北", "华南"])
        self.assertTrue(chart["embedded_workbook"])
        self.assertEqual(report["powerpoint_roundtrip"], "not_performed")

    def test_missing_resources_are_blocking(self):
        with tempfile.TemporaryDirectory() as tmp:
            file = Path(tmp) / "missing-workbook.pptx"
            with ZipFile(SAMPLE) as source, ZipFile(file, "w") as dest:
                for name in source.namelist():
                    if not name.startswith("ppt/embeddings/"):
                        dest.writestr(name, source.read(name))
            report = inspector.inspect(file)
            self.assertFalse(report["structure_passed"])
            self.assertTrue(any("Missing relationship" in error for error in report["errors"]))

    def test_bad_zip_is_explicit_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            file = Path(tmp) / "bad.pptx"
            file.write_text("not a PPTX")
            result = subprocess.run([sys.executable, str(ROOT / "scripts/inspect_pptx.py"), str(file)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 2)
            self.assertIn("BadZipFile", result.stderr)
            self.assertNotIn("Traceback", result.stderr)

    def test_entities_and_zip_traversal_are_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            file = Path(tmp) / "unsafe.pptx"
            with ZipFile(file, "w") as archive:
                archive.writestr("../outside", "data")
            with self.assertRaisesRegex(ValueError, "Unsafe"):
                inspector.inspect(file)
            with ZipFile(file, "w") as archive:
                archive.writestr("_rels/.rels", '<!DOCTYPE x [<!ENTITY y "payload">]><x/>')
            with self.assertRaisesRegex(ValueError, "DTD"):
                inspector.inspect(file)

    def test_optional_renderer_is_not_loaded_for_inspection(self):
        report = inspector.inspect(SAMPLE)
        self.assertEqual(report["visual_review"], "not_performed")
        self.assertNotIn("render_with_libreoffice", sys.modules)

    def test_sparse_cache_preserves_missing_points_instead_of_shifting_values(self):
        cache = ET.fromstring(f'<c:numCache xmlns:c="{inspector.NS["c"]}"><c:ptCount val="3"/>'
                              '<c:pt idx="0"><c:v>0</c:v></c:pt><c:pt idx="2"><c:v>-2</c:v></c:pt></c:numCache>')
        self.assertEqual(inspector.cache_points(cache), ["0", None, "-2"])
        cache.find("c:ptCount", inspector.NS).set("val", "1000000000")
        with self.assertRaisesRegex(ValueError, "bounds"):
            inspector.cache_points(cache)


if __name__ == "__main__":
    unittest.main()
