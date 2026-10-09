"""Portable SVG DrawingML authoring: write → validate → native PPTX render."""

from .adapter import create_native_pptx_from_svg_files, svg_contains_data_icon_placeholders
from .authoring import inspect_svg_layers, patch_svg_layer_text, validate_svg_string_for_authoring
from .color_scheme_gate import build_color_scheme_report
from .input_gate import validate_svg_input
from .native_placeholders import strip_native_slot_placeholder_texts
from .pipeline import render_svg_drawingml, validate_svg_drawingml

__all__ = [
    "create_native_pptx_from_svg_files",
    "svg_contains_data_icon_placeholders",
    "inspect_svg_layers",
    "patch_svg_layer_text",
    "validate_svg_string_for_authoring",
    "build_color_scheme_report",
    "validate_svg_input",
    "strip_native_slot_placeholder_texts",
    "render_svg_drawingml",
    "validate_svg_drawingml",
]
