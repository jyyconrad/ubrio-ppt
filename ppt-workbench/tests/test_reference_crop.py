"""The viewport crop keeps visible geometry and stays within its canvas."""

import sys
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "svg"))
from build_reference_page import _crop_dashboard, resources
from reference_layouts import rd_layouts
from reference_layouts.common import Svg
from drawingml.pipeline import validate_svg_drawingml


class ReferenceCropTests(unittest.TestCase):
    def test_dashboard_crop_has_no_overflow(self):
        renderers, defaults, _ = resources()
        svg, native = renderers["R31"](defaults["R31"])
        result = validate_svg_drawingml(svg_text=svg, native_data=native)
        self.assertTrue(result["ok"], result["issues"])
        root = ET.fromstring(svg)
        self.assertEqual(root.get("viewBox"), "0 0 1280 640")

    def test_partial_circle_is_clipped_instead_of_disappearing(self):
        scene = Svg()
        scene.circle(800, 620, 35)
        with patch.dict(rd_layouts.RENDERERS, {"R10": lambda _: scene.finish()}):
            svg, _ = _crop_dashboard({})
        node = next(node for node in ET.fromstring(svg)
                    if node.get("data-cropped-circle") == "true")
        coordinates = [float(value) for value in node.get("points").replace(",", " ").split()]
        self.assertGreater(len(coordinates), 100)
        self.assertLessEqual(max(coordinates[1::2]), 639)
        self.assertAlmostEqual(min(coordinates[1::2]), 585)


if __name__ == "__main__":
    unittest.main()
