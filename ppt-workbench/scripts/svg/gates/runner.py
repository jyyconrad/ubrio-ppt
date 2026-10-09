"""Run page-level session-884 gates without importing the SVG builder."""

from __future__ import annotations

from typing import Any, Callable

from . import GateResult
from .decision import check as check_decision
from .evidence import check as check_evidence
from .native_table import check as check_native_table
from .plain_language import check as check_plain_language
from .visual import check as check_visual
from .visual import check_svg as check_visual_svg

PAGE_GATES: tuple[tuple[str, Callable[[dict[str, Any]], GateResult]], ...] = (
    ("evidence", check_evidence),
    ("decision", check_decision),
    ("visual", check_visual),
    ("plain_language", check_plain_language),
    ("native_table", check_native_table),
)


def run_page_gates(spec: dict[str, Any]) -> GateResult:
    combined = GateResult()
    details: dict[str, Any] = {}
    for name, fn in PAGE_GATES:
        result = fn(spec if isinstance(spec, dict) else {})
        for code in result.missing:
            if code not in combined.missing:
                combined.missing.append(code)
        for code in result.warnings:
            if code not in combined.warnings:
                combined.warnings.append(code)
        details[name] = result.details
    combined.details = details
    return combined


def run_svg_gates(svg_text: str, spec: dict[str, Any] | None = None) -> GateResult:
    return check_visual_svg(svg_text, spec)
