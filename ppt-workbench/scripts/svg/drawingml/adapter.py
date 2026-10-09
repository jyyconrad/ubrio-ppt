"""Thin wrapper around the vendored SVG → native DrawingML PPTX converter."""

from __future__ import annotations

import importlib
import re
import sys
from collections.abc import Iterator, Sequence
from contextlib import contextmanager
from pathlib import Path
from types import ModuleType
from typing import Any

PACKAGE_DIR = Path(__file__).resolve().parent
VENDOR_SCRIPTS_DIR = PACKAGE_DIR.parent / "vendor" / "ppt_master" / "scripts"
DATA_ICON_RE = re.compile(r"\bdata-icon\s*=")
STANDARD_PPT_CANVAS_FORMAT = "ppt169"


def vendored_scripts_path() -> Path:
    return VENDOR_SCRIPTS_DIR


@contextmanager
def _vendored_sys_path() -> Iterator[None]:
    script_path = str(vendored_scripts_path())
    if script_path not in sys.path:
        sys.path.insert(0, script_path)
    yield


def import_svg_to_pptx_module() -> ModuleType:
    with _vendored_sys_path():
        module = importlib.import_module("svg_to_pptx")
    module_file = Path(getattr(module, "__file__", "")).resolve()
    if not module_file.is_relative_to(vendored_scripts_path()):
        raise ImportError(f"svg_to_pptx resolved outside vendored tree: {module_file}")
    return module


def svg_contains_data_icon_placeholders(svg_path: Path) -> bool:
    return bool(DATA_ICON_RE.search(Path(svg_path).read_text(encoding="utf-8")))


def create_native_pptx_from_svg_files(
    svg_files: Sequence[Path],
    output_path: Path,
    *,
    canvas_format: str | None = None,
    verbose: bool = False,
    merge_paragraphs: bool = False,
    conversion_trace_path: Path | None = None,
) -> bool:
    """Convert local SVGs to an editable native-shape PPTX.

    Always native DrawingML: use_native_shapes=True, use_compat_mode=False,
    merge_paragraphs=False unless the caller opts in.
    """

    if merge_paragraphs:
        raise ValueError("layout fidelity requires merge_paragraphs=False")
    module = import_svg_to_pptx_module()
    with _vendored_sys_path():
        return bool(
            module.create_pptx_with_native_svg(
                [Path(path) for path in svg_files],
                Path(output_path),
                canvas_format=None if canvas_format == "auto" else (canvas_format or STANDARD_PPT_CANVAS_FORMAT),
                verbose=verbose,
                transition=None,
                use_compat_mode=False,
                use_native_shapes=True,
                merge_paragraphs=False,
                conversion_trace_path=conversion_trace_path,
            )
        )


def conversion_kwargs() -> dict[str, Any]:
    return {
        "use_compat_mode": False,
        "use_native_shapes": True,
        "merge_paragraphs": False,
    }
