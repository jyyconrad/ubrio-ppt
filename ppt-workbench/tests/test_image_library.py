"""Built-in image library: index integrity, licensing, search and staging."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
IMG_ROOT = ROOT / "assets" / "images"
INDEX = IMG_ROOT / "image-index.json"
SEARCH = ROOT / "scripts" / "assets" / "search_images.py"
RECIPE = ROOT / "references" / "generate" / "methods" / "image-library.md"
SKILL = ROOT / "SKILL.md"
CAPABILITY_MAP = ROOT / "references" / "generate" / "capability-map.md"
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
SEARCH_ICONS = ROOT / "scripts" / "svg" / "search_icons.py"

ALLOWED_LICENSES = ("cc0", "cc by", "cc by-sa", "public domain", "pd", "no restrictions")
MIN_LIBRARY_SIZE = 30


def _load_search_images():
    spec = importlib.util.spec_from_file_location("search_images", SEARCH)
    if spec is None or spec.loader is None:
        raise FileNotFoundError(SEARCH)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _image_size(path: Path) -> tuple[int, int]:
    out = subprocess.run(
        ["sips", "-g", "pixelWidth", "-g", "pixelHeight", str(path)],
        capture_output=True, text=True,
    )
    if out.returncode != 0:
        return (0, 0)
    width = height = 0
    for line in out.stdout.splitlines():
        if "pixelWidth" in line:
            width = int(line.split(":")[1].strip())
        if "pixelHeight" in line:
            height = int(line.split(":")[1].strip())
    return (width, height)


class ImageLibraryIndexTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.entries = json.loads(INDEX.read_text(encoding="utf-8"))["images"]

    def test_index_exists_with_enough_images(self) -> None:
        self.assertGreaterEqual(len(self.entries), MIN_LIBRARY_SIZE)

    def test_every_entry_has_required_fields(self) -> None:
        for entry in self.entries:
            for field in ("image_id", "file", "title", "category", "width", "height", "recommended_usage", "source"):
                self.assertTrue(entry.get(field), f"{entry.get('image_id')} missing {field}")
            source = entry["source"]
            for field in ("site", "title", "license"):
                self.assertTrue(source.get(field), f"{entry.get('image_id')} source missing {field}")

    def test_files_exist_and_dims_match(self) -> None:
        for entry in self.entries:
            path = IMG_ROOT / entry["file"]
            self.assertTrue(path.is_file(), entry["file"])
            width, height = _image_size(path)
            self.assertGreaterEqual(width, 900, entry["file"])
            self.assertGreater(width, height, f"{entry['file']} must be landscape")
            self.assertEqual(width, entry["width"], entry["file"])
            self.assertEqual(height, entry["height"], entry["file"])

    def test_unique_files_and_ids(self) -> None:
        ids = [entry["image_id"] for entry in self.entries]
        files = [entry["file"] for entry in self.entries]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(len(files), len(set(files)))

    def test_licenses_are_open(self) -> None:
        for entry in self.entries:
            license_text = str(entry["source"]["license"]).lower()
            self.assertTrue(
                any(token in license_text for token in ALLOWED_LICENSES),
                f"{entry['image_id']} license not in allowlist: {license_text}",
            )
            self.assertNotRegex(license_text, r"\b(nc|nd)\b", entry["image_id"])

    def test_commons_entries_carry_page_url(self) -> None:
        for entry in self.entries:
            if entry["source"]["site"] == "Wikimedia Commons":
                self.assertTrue(
                    str(entry["source"]["page"]).startswith("https://commons.wikimedia.org/"),
                    f"{entry['image_id']} missing commons page url",
                )
                self.assertTrue(entry["source"]["creator"], entry["image_id"])

    def test_categories_covered(self) -> None:
        categories = {entry["category"] for entry in self.entries}
        expected = {
            "cover-city", "cover-abstract", "business-meeting", "business-cooperation",
            "office-work", "industry-factory", "logistics-port", "tech-data", "nature-milestone",
        }
        self.assertTrue(expected.issubset(categories), expected - categories)


class ImageSearchCliTests(unittest.TestCase):
    def test_list_and_query(self) -> None:
        listed = subprocess.run(
            [sys.executable, str(SEARCH), "--list"],
            capture_output=True, text=True, check=True,
        )
        payload = json.loads(listed.stdout)
        self.assertTrue(payload["ok"])
        self.assertGreaterEqual(len(payload["categories"]), 6)

        queried = subprocess.run(
            [sys.executable, str(SEARCH), "--query", "封面 城市夜景", "--limit", "3"],
            capture_output=True, text=True, check=True,
        )
        payload = json.loads(queried.stdout)
        self.assertTrue(payload["ok"])
        self.assertTrue(payload["images"])
        for image in payload["images"]:
            self.assertIn("image_id", image)
            self.assertIn("recommended_usage", image)

    def test_stage_copies_local_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = subprocess.run(
                [sys.executable, str(SEARCH), "--stage", "cover-city-01", "--dest", tmp],
                capture_output=True, text=True, check=True,
            )
            payload = json.loads(out.stdout)
            self.assertTrue(payload["ok"])
            staged = Path(payload["staged_path"])
            self.assertTrue(staged.is_file())
            self.assertGreater(staged.stat().st_size, 50_000)
            self.assertIn("license", payload)

    def test_stage_unknown_id_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = subprocess.run(
                [sys.executable, str(SEARCH), "--stage", "does-not-exist", "--dest", tmp],
                capture_output=True, text=True,
            )
            self.assertNotEqual(out.returncode, 0)
            self.assertIn("未找到图片", out.stdout)


class ImageLibraryDocsTests(unittest.TestCase):
    def test_recipe_and_entry_points_exist(self) -> None:
        self.assertTrue(RECIPE.is_file())
        self.assertTrue(SEARCH.is_file())
        recipe = RECIPE.read_text(encoding="utf-8")
        self.assertIn("scripts/assets/search_images.py", recipe)
        self.assertIn("--stage", recipe)
        skill = SKILL.read_text(encoding="utf-8")
        self.assertIn("image-library.md", skill)
        self.assertIn("assets/images/", skill)
        capability = CAPABILITY_MAP.read_text(encoding="utf-8")
        self.assertIn("search_images.py", capability)

    def test_recipes_forbid_remote_and_library_paths(self) -> None:
        recipe = RECIPE.read_text(encoding="utf-8")
        self.assertIn("禁止", recipe)
        self.assertIn("stage", recipe)
        owners = (ROOT / "references" / "generate" / "methods" / "image-owners.md").read_text(encoding="utf-8")
        self.assertIn("search_images.py", owners)


class FilledIconFamilyTests(unittest.TestCase):
    def test_mdi_entries_present_in_index(self) -> None:
        index = json.loads((ICONS_ROOT / "icon-index.json").read_text(encoding="utf-8"))
        mdi = [icon for icon in index["icons"] if str(icon.get("icon_id", "")).startswith("mdi-")]
        self.assertGreaterEqual(len(mdi), 2000)
        self.assertTrue(all(icon.get("style") == "filled" for icon in mdi))
        for icon in mdi[:50]:
            path = ICONS_ROOT / icon["path"]
            self.assertTrue(path.is_file(), icon["path"])

    def test_filled_search_and_expand_end_to_end(self) -> None:
        found = subprocess.run(
            [sys.executable, str(SEARCH_ICONS), "--query", "工厂", "--style", "filled", "--limit", "3"],
            capture_output=True, text=True, check=True,
        )
        payload = json.loads(found.stdout)
        self.assertTrue(payload["ok"])
        self.assertTrue(payload["icons"])
        self.assertTrue(all(icon["icon_id"].startswith("mdi-") for icon in payload["icons"]))

        icon_id = payload["icons"][0]["icon_id"]
        svg = (
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1280 720">'
            '<rect x="0" y="0" width="1280" height="720" fill="#FFFFFF"/>'
            f'<g id="slot" data-icon-id="{icon_id}" data-icon-box="80 160 56 56"/>'
            "</svg>"
        )
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "page.svg"
            src.write_text(svg, encoding="utf-8")
            out = Path(tmp) / "expanded.svg"
            result = subprocess.run(
                [sys.executable, str(SEARCH_ICONS), "--expand", str(src), "--output", str(out)],
                capture_output=True, text=True, check=True,
            )
            self.assertTrue(json.loads(result.stdout)["ok"])
            expanded = out.read_text(encoding="utf-8")
            self.assertNotIn("data-icon-id", expanded)

    def test_icon_readme_documents_two_families(self) -> None:
        readme = ICON_README.read_text(encoding="utf-8")
        self.assertIn("mdi", readme)
        self.assertIn("Apache-2.0", readme)
        self.assertIn("lucide", readme)


if __name__ == "__main__":
    unittest.main()
