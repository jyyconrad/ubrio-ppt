#!/usr/bin/env python3
"""Build a reference-layout deck from already-authored page specs and content."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"
for candidate in (Path(__file__).resolve().parent, SCRIPTS):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from build_gold_svg_page import (  # noqa: E402
    build_native_data,
    build_svg_page,
    normalize_page_spec,
    quality_report,
)
from build_reference_page import CATALOG, _check_content, resources  # noqa: E402
from drawingml.pipeline import render_svg_drawingml, validate_svg_drawingml  # noqa: E402
from reference_layouts.components import _bind, _bounds, _business_data, _no_unknown, data_contract  # noqa: E402
from validate_deck_contract import validate_deck  # noqa: E402

SVG_NS = "http://www.w3.org/2000/svg"
SOURCE_FONT_PX = 11
SOURCE_MAX_LINES = 2
EVIDENCE_STATE_LABELS = {
    "FACT": "事实",
    "OBSERVED": "观察",
    "PROPOSAL": "建议",
    "TARGET": "目标",
    "TO_VALIDATE": "待验证",
}


class ReferenceDeckError(RuntimeError):
    def __init__(self, code: str, message: str, *, report: dict[str, Any] | None = None):
        super().__init__(message)
        self.code = code
        self.report = report or {"ok": False, "error": {"code": code, "message": message}}


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _json_hash(value: Any) -> str:
    return _sha256_text(_canonical_json(value))


def _write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _load_document(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ReferenceDeckError("INPUT_INVALID", f"cannot read input JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise ReferenceDeckError("INPUT_INVALID", "input JSON must be an object")
    return value


def describe_contract() -> dict[str, Any]:
    return {
        "entry": "scripts/svg/build_reference_deck.py",
        "input": {
            "manifest": "Existing complete manifest accepted by validate_deck_contract.validate_deck.",
            "pages": [
                {
                    "existing_complete_page_spec": "Keep all existing page_spec business judgments.",
                    "reference_id": "R01..R32",
                    "reference_content": "Business-only contract returned by --describe-reference.",
                }
            ],
        },
        "preflight_order": [
            "bind every actual reference_content in memory",
            "derive native slots from those same bound objects",
            "run one deck validation and every gold/SVG validation",
            "start the first PPTX render only after all blockers are clear",
        ],
        "outputs": "Stable page-NNN directories plus reference-deck-manifest.json; merge with merge_export.py.",
        "examples": "No business facts are generated. Pass an explicitly authorized fixture as --input.",
    }


def describe_reference(reference_id: str) -> dict[str, Any]:
    renderers, defaults, schemas = resources()
    if reference_id not in renderers:
        raise ReferenceDeckError("REFERENCE_ID_INVALID", f"unknown reference_id: {reference_id}")
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))["items"]
    record = next(item for item in catalog if item["id"] == reference_id)
    business_shape = _business_data(defaults[reference_id])
    canvas = schemas[reference_id].get("canvas")
    if not canvas and isinstance(record.get("canvas"), list):
        canvas = "x".join(str(item) for item in record["canvas"])
    return {
        "reference_id": reference_id,
        "reference_file": record["file"],
        "canvas": canvas,
        "source_band": copy.deepcopy(schemas[reference_id].get("source_band")),
        "business_fields": list(business_shape),
        "business_data_contract": data_contract(business_shape),
        "capacity": schemas[reference_id].get("fields", schemas[reference_id]),
        "agent_requirement": (
            "Agent must supply this business contract and an existing complete page_spec; "
            "the entry preserves the fixed reference geometry and does not invent business facts."
        ),
    }


def _page_spec(page: dict[str, Any]) -> dict[str, Any]:
    spec = copy.deepcopy(page)
    spec.pop("reference_content", None)
    return spec


def _metric_value(spec: dict[str, Any], field: str) -> str:
    direct = spec.get(field)
    if isinstance(direct, list):
        direct = "；".join(str(item).strip() for item in direct if str(item).strip())
    if str(direct or "").strip():
        return str(direct).strip()
    values = []
    for metric in spec.get("metrics") or []:
        if isinstance(metric, dict) and str(metric.get(field) or "").strip():
            value = str(metric[field]).strip()
            if value not in values:
                values.append(value)
    if len(values) == 1:
        return values[0]
    if len(values) > 1:
        return "；".join(values)
    return ""


def _source_metadata(spec: dict[str, Any], page_number: int) -> dict[str, str]:
    limitation = _metric_value(spec, "limitation")
    if not spec.get("limitation"):
        limitation = _metric_value(spec, "limitations") or limitation
    metadata = {
        "evidence_state": str(spec.get("evidence_state") or "").strip(),
        "period": _metric_value(spec, "period"),
        "population": _metric_value(spec, "population"),
        "denominator": _metric_value(spec, "denominator"),
        "source_ref": _metric_value(spec, "source_ref"),
        "limitation": limitation,
    }
    missing = [key for key, value in metadata.items() if not value]
    if missing:
        raise ReferenceDeckError(
            "BUSINESS_METADATA_MISSING",
            f"page {page_number}: fill or explicitly mark unknown business metadata: {', '.join(missing)}",
        )
    return metadata


def _char_width(character: str) -> float:
    if character.isspace():
        return SOURCE_FONT_PX * 0.35
    # DrawingML text boxes add font-dependent advance and fallback spacing.
    return SOURCE_FONT_PX * (1.2 if ord(character) > 255 else 0.68)


def _wrap_source(text: str, max_width: float) -> list[str]:
    lines: list[str] = []
    current: list[str] = []
    width = 0.0
    for character in text:
        character_width = _char_width(character)
        if current and width + character_width > max_width:
            lines.append("".join(current).strip())
            current = [character]
            width = character_width
        else:
            current.append(character)
            width += character_width
    if current:
        lines.append("".join(current).strip())
    return lines


def _compact_period(value: str) -> str:
    for separator in ("与", "和"):
        if separator not in value:
            continue
        left, right = value.split(separator, 1)
        prefix_length = 0
        for first, second in zip(left, right):
            if first != second:
                break
            prefix_length += 1
        prefix = left[:prefix_length]
        if prefix_length >= 2 and any(ord(character) > 255 for character in prefix):
            return f"{left}/{right[prefix_length:]}"
    return value


def _source_band(
    raw: Any,
    *,
    width: float,
    height: float,
    line_count: int,
    page_number: int,
) -> tuple[dict[str, float | int], str]:
    if raw is None:
        band_height = 15 if line_count == 1 else 32
        return {
            "x": 24.0,
            "y": height - band_height,
            "w": width - 48.0,
            "h": float(band_height - 1),
            "max_lines": 1 if line_count == 1 else SOURCE_MAX_LINES,
            "font_size": SOURCE_FONT_PX,
        }, "default_bottom"
    if not isinstance(raw, dict):
        raise ReferenceDeckError("SOURCE_BAND_INVALID", f"page {page_number}: renderer source_band must be an object")
    try:
        band = {
            "x": float(raw["x"]),
            "y": float(raw["y"]),
            "w": float(raw["w"]),
            "h": float(raw["h"]),
            "max_lines": int(raw.get("max_lines", 1)),
            "font_size": int(raw.get("font_size", SOURCE_FONT_PX)),
        }
    except (KeyError, TypeError, ValueError) as exc:
        raise ReferenceDeckError("SOURCE_BAND_INVALID", f"page {page_number}: invalid renderer source_band") from exc
    if (
        band["x"] < 0
        or band["y"] < 0
        or band["w"] <= 0
        or band["h"] <= 0
        or band["x"] + band["w"] > width
        or band["y"] + band["h"] > height
        or band["max_lines"] not in {1, 2}
        or band["font_size"] != SOURCE_FONT_PX
    ):
        raise ReferenceDeckError("SOURCE_BAND_INVALID", f"page {page_number}: renderer source_band is outside its trusted bounds")
    return band, "renderer_schema"


def _boxes_intersect(first: tuple[float, float, float, float], second: tuple[float, float, float, float]) -> bool:
    return not (first[2] <= second[0] or second[2] <= first[0] or first[3] <= second[1] or second[3] <= first[1])


def _is_enclosing_container(node: ET.Element, bounds: tuple[float, float, float, float], band: tuple[float, float, float, float]) -> bool:
    if node.tag.rsplit("}", 1)[-1] != "rect":
        return False
    return bounds[0] <= band[0] and bounds[1] <= band[1] and bounds[2] >= band[2] and bounds[3] >= band[3]


def _canvas_label(svg_text: str, declared: Any) -> str:
    if str(declared or "").strip():
        return str(declared)
    root = ET.fromstring(svg_text)
    view_box = [float(item) for item in root.get("viewBox", "0 0 1280 720").split()]
    return f"{view_box[2]:g}x{view_box[3]:g}"


def _append_source_footnote(
    svg_text: str,
    metadata: dict[str, str],
    page_number: int,
    *,
    source_band: dict[str, Any] | None = None,
) -> tuple[str, dict[str, Any]]:
    try:
        root = ET.fromstring(svg_text)
    except ET.ParseError as exc:
        raise ReferenceDeckError("REFERENCE_SVG_INVALID", f"page {page_number}: invalid reference SVG: {exc}") from exc
    view_box = [float(item) for item in root.get("viewBox", "0 0 1280 720").split()]
    width = view_box[2]
    height = view_box[3]
    display_state = EVIDENCE_STATE_LABELS.get(metadata["evidence_state"].upper(), metadata["evidence_state"])
    source = (
        f"{display_state}｜期:{_compact_period(metadata['period'])}｜样:{metadata['population']}｜"
        f"分:{metadata['denominator']}｜源:{metadata['source_ref'].replace(' / ', '·')}｜限:{metadata['limitation']}"
    )
    initial_lines = _wrap_source(source, width - 64)
    band, band_origin = _source_band(
        source_band,
        width=width,
        height=height,
        line_count=len(initial_lines),
        page_number=page_number,
    )
    lines = _wrap_source(source, float(band["w"]) - 16)
    if len(lines) > int(band["max_lines"]):
        raise ReferenceDeckError(
            "SOURCE_FOOTNOTE_OVERFLOW",
            f"page {page_number}: source footnote needs {len(lines)} lines; maximum is {band['max_lines']}",
        )
    band_box = (float(band["x"]), float(band["y"]), float(band["x"] + band["w"]), float(band["y"] + band["h"]))
    conflicts: list[dict[str, Any]] = []
    unknown: list[dict[str, Any]] = []
    for node in root.iter():
        tag = node.tag.rsplit("}", 1)[-1]
        if tag in {"svg", "g", "tspan", "defs", "style", "title", "desc"}:
            continue
        try:
            bounds = _bounds(node)
        except Exception as exc:  # noqa: BLE001
            unknown.append({"tag": tag, "reason": str(exc)[:120]})
            continue
        if bounds is None:
            if tag in {"path", "image", "use"}:
                unknown.append({"tag": tag, "reason": "visible element bounds unavailable"})
            continue
        if _is_enclosing_container(node, bounds, band_box):
            continue
        if _boxes_intersect(bounds, band_box):
            conflicts.append({"tag": tag, "bounds": [round(value, 2) for value in bounds], "text": "".join(node.itertext())[:60]})
    if conflicts or unknown:
        raise ReferenceDeckError(
            "SOURCE_BAND_CONFLICT",
            f"page {page_number}: source band conflicts with content or contains geometry that cannot be verified",
            report={"ok": False, "page": page_number, "band": band, "conflicts": conflicts[:8], "unknown": unknown[:8]},
        )

    ET.register_namespace("", SVG_NS)
    group = ET.SubElement(root, f"{{{SVG_NS}}}g", {"id": "reference-business-source", "role": "source", "data-role": "source"})
    ET.SubElement(
        group,
        f"{{{SVG_NS}}}rect",
        {
            "x": f"{float(band['x']):.1f}",
            "y": f"{float(band['y']):.1f}",
            "width": f"{float(band['w']) - 1:.1f}",
            "height": f"{float(band['h']) - 1:.1f}",
            "fill": "#FFFFFF",
            "opacity": "0.96",
        },
    )
    line_height = SOURCE_FONT_PX + 1
    last_baseline = float(band["y"] + band["h"]) - 8
    first_baseline = last_baseline - (len(lines) - 1) * line_height
    text_x = float(band["x"]) + 8
    text = ET.SubElement(
        group,
        f"{{{SVG_NS}}}text",
        {
            "x": f"{text_x:.1f}",
            "y": f"{first_baseline:.1f}",
            "font-family": "Noto Sans CJK SC, Microsoft YaHei, Arial",
            "font-size": str(SOURCE_FONT_PX),
            "font-weight": "400",
            "fill": "#52667D",
            "data-role": "source",
        },
    )
    for index, line in enumerate(lines):
        span = ET.SubElement(
            text,
            f"{{{SVG_NS}}}tspan",
            {"x": f"{text_x:.1f}", "dy": "0" if index == 0 else str(line_height)},
        )
        span.text = line
    return ET.tostring(root, encoding="unicode"), {
        "role": "source",
        "font_px": SOURCE_FONT_PX,
        "line_count": len(lines),
        "display_state": display_state,
        "band_origin": band_origin,
        "band": band,
        "safe_top": band["y"],
        "metadata": metadata,
    }


def preflight_reference_deck(document: dict[str, Any]) -> dict[str, Any]:
    manifest = document.get("manifest")
    pages = document.get("pages")
    if not isinstance(manifest, dict):
        raise ReferenceDeckError("MANIFEST_INVALID", "manifest must be an object")
    if not isinstance(pages, list) or not pages:
        raise ReferenceDeckError("PAGES_INVALID", "pages must be a non-empty array")

    dashboard_pages = {
        str(page.get("reference_id") or ""): page
        for page in pages
        if isinstance(page, dict) and str(page.get("reference_id") or "") in {"R10", "R31"}
    }
    if set(dashboard_pages) == {"R10", "R31"}:
        r10, r31 = dashboard_pages["R10"], dashboard_pages["R31"]
        if (
            _canonical_json(r10.get("reference_content")) != _canonical_json(r31.get("reference_content"))
            or _source_metadata(_page_spec(r10), int(r10.get("page_no") or 0))
            != _source_metadata(_page_spec(r31), int(r31.get("page_no") or 0))
        ):
            raise ReferenceDeckError(
                "R31_SOURCE_MISMATCH",
                "R31 must share the same actual reference_content and page_spec evidence metadata as R10",
            )

    renderers, defaults, schemas = resources()
    prepared_pages: list[dict[str, Any]] = []
    deck_pages: list[dict[str, Any]] = []
    shared_dashboard_source: dict[str, tuple[dict[str, Any], dict[str, str]]] = {}
    events: list[dict[str, Any]] = [{"sequence": 1, "event": "input_loaded", "page_count": len(pages)}]

    for index, raw_page in enumerate(pages, start=1):
        if not isinstance(raw_page, dict):
            raise ReferenceDeckError("PAGE_INVALID", f"page {index} must be an object")
        reference_id = str(raw_page.get("reference_id") or "").strip()
        if reference_id not in renderers:
            raise ReferenceDeckError("REFERENCE_ID_INVALID", f"page {index}: unknown reference_id {reference_id!r}")
        actual_content = raw_page.get("reference_content")
        business_shape = _business_data(defaults[reference_id])
        try:
            _check_content(actual_content, business_shape, path=f"pages[{index}].reference_content")
            _no_unknown(actual_content, business_shape, path=f"pages[{index}].reference_content")
        except (KeyError, TypeError, ValueError) as exc:
            raise ReferenceDeckError("REFERENCE_CONTENT_INVALID", str(exc)) from exc

        original_spec = _page_spec(raw_page)
        if str(original_spec.get("title") or "").strip() != str(actual_content.get("title") or "").strip():
            raise ReferenceDeckError(
                "TITLE_MISMATCH",
                f"page {index}: page_spec.title must equal reference_content.title",
            )
        metadata = _source_metadata(original_spec, index)
        if reference_id in {"R10", "R31"}:
            other_id = "R31" if reference_id == "R10" else "R10"
            if other_id in shared_dashboard_source:
                other_content, other_metadata = shared_dashboard_source[other_id]
                if _canonical_json(actual_content) != _canonical_json(other_content) or metadata != other_metadata:
                    raise ReferenceDeckError(
                        "R31_SOURCE_MISMATCH",
                        "R31 must share the same actual reference_content and page_spec evidence metadata as R10",
                    )
            shared_dashboard_source[reference_id] = (copy.deepcopy(actual_content), copy.deepcopy(metadata))
        bound_content = _bind(defaults[reference_id], actual_content)
        try:
            reference_svg, native_data = renderers[reference_id](bound_content)
        except (KeyError, TypeError, ValueError) as exc:
            raise ReferenceDeckError("REFERENCE_CAPACITY_INVALID", f"page {index}: {exc}") from exc
        final_svg, footnote = _append_source_footnote(
            reference_svg,
            metadata,
            index,
            source_band=schemas[reference_id].get("source_band"),
        )
        normalized_spec = normalize_page_spec(original_spec)
        gold_quality = quality_report(normalized_spec)
        gold_native = build_native_data(normalized_spec)
        gold_ref = "gold-start.native-data.json" if any(gold_native.get(key) for key in ("charts", "tables", "images", "sankeys")) else None
        gold_svg = build_svg_page(normalized_spec, native_data_ref=gold_ref)

        deck_spec = copy.deepcopy(original_spec)
        deck_spec["native_data"] = copy.deepcopy(native_data)
        deck_pages.append(deck_spec)
        prepared_pages.append(
            {
                "sequence": index,
                "reference_id": reference_id,
                "canvas": _canvas_label(reference_svg, schemas[reference_id].get("canvas")),
                "page_spec": original_spec,
                "normalized_spec": normalized_spec,
                "reference_content": copy.deepcopy(actual_content),
                "bound_content": bound_content,
                "gold_quality": gold_quality,
                "gold_svg": gold_svg,
                "gold_native": gold_native,
                "reference_svg": final_svg,
                "native_data": native_data,
                "source_footnote": footnote,
            }
        )
        events.append({"sequence": len(events) + 1, "event": "page_prepared", "page": index, "reference_id": reference_id})

    deck_validation = validate_deck(manifest, deck_pages)
    events.append({"sequence": len(events) + 1, "event": "deck_validated", "ok": deck_validation["ok"]})
    blocked = not deck_validation["ok"]
    page_reports: list[dict[str, Any]] = []
    for page in prepared_pages:
        final_validation = validate_svg_drawingml(
            svg_text=page["reference_svg"],
            mode="full",
            native_data=page["native_data"],
        )
        gold_ready = page["gold_quality"]["quality_status"] == "ready"
        blocked = blocked or not gold_ready or not final_validation["ok"]
        report = {
            "page": page["sequence"],
            "reference_id": page["reference_id"],
            "gold_quality": page["gold_quality"],
            "reference_svg_validation": {key: value for key, value in final_validation.items() if key not in {"expanded_svg", "stripped_svg"}},
            "source_footnote": page["source_footnote"],
        }
        page_reports.append(report)
        events.append({"sequence": len(events) + 1, "event": "page_gold_validated", "page": page["sequence"], "ok": gold_ready})
        events.append({"sequence": len(events) + 1, "event": "page_svg_validated", "page": page["sequence"], "ok": final_validation["ok"]})

    report = {
        "ok": not blocked,
        "validation_scope": "existing_deck_gold_and_svg_contracts",
        "deck_validation": deck_validation,
        "pages": page_reports,
        "events": events,
        "visual_review": "not_performed",
    }
    if blocked:
        raise ReferenceDeckError("PREFLIGHT_BLOCKED", "deck is blocked before the first render", report=report)
    events.append({"sequence": len(events) + 1, "event": "preflight_complete", "ok": True})
    return {"manifest": copy.deepcopy(manifest), "pages": prepared_pages, "preflight": report, "events": events}


def _ensure_output_dir(output_dir: Path) -> None:
    if output_dir.exists() and (not output_dir.is_dir() or any(output_dir.iterdir())):
        raise ReferenceDeckError("OUTPUT_NOT_EMPTY", f"output directory must be absent or empty: {output_dir}")
    output_dir.mkdir(parents=True, exist_ok=True)


def _file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_reference_deck(document: dict[str, Any], *, output_dir: Path) -> dict[str, Any]:
    prepared = preflight_reference_deck(document)
    output_dir = Path(output_dir)
    _ensure_output_dir(output_dir)
    events = copy.deepcopy(prepared["events"])
    events.append({"sequence": len(events) + 1, "event": "first_render_started", "page": 1})
    manifest_pages: list[dict[str, Any]] = []

    for page in prepared["pages"]:
        index = page["sequence"]
        page_dir = output_dir / f"page-{index:03d}"
        page_dir.mkdir()
        paths = {
            "page_spec": page_dir / "page_spec.json",
            "normalized_spec": page_dir / "page_spec.normalized.json",
            "reference_content": page_dir / "reference-content.json",
            "preflight": page_dir / "preflight-report.json",
            "gold_svg": page_dir / "gold-start.svg",
            "gold_native": page_dir / "gold-start.native-data.json",
            "reference_svg": page_dir / "reference-final.svg",
            "native_data": page_dir / "native-data.json",
            "adaptation": page_dir / "adaptation-report.json",
            "pptx": page_dir / "page.pptx",
        }
        _write_json(paths["page_spec"], page["page_spec"])
        _write_json(paths["normalized_spec"], page["normalized_spec"])
        _write_json(paths["reference_content"], page["reference_content"])
        _write_json(paths["preflight"], prepared["preflight"]["pages"][index - 1])
        paths["gold_svg"].write_text(page["gold_svg"], encoding="utf-8")
        _write_json(paths["gold_native"], page["gold_native"])
        paths["reference_svg"].write_text(page["reference_svg"], encoding="utf-8")
        _write_json(paths["native_data"], page["native_data"])
        adaptation = {
            "reference_id": page["reference_id"],
            "canvas": page["canvas"],
            "same_actual_spec_and_content_consumed": True,
            "fixed_design_restored_by_existing_bind": True,
            "source_footnote": page["source_footnote"],
            "visual_review": "not_performed",
            "powerpoint_roundtrip": "not_performed",
        }
        _write_json(paths["adaptation"], adaptation)
        result = render_svg_drawingml(
            svg_path=paths["reference_svg"],
            output=paths["pptx"],
            native_data=page["native_data"],
            assets_dir=page_dir,
            canvas_format="auto",
        )
        if not result.get("ok"):
            raise ReferenceDeckError(
                "RENDER_BLOCKED",
                f"page {index} render failed",
                report={key: value for key, value in result.items() if key not in {"expanded_svg", "stripped_svg"}},
            )
        events.append({"sequence": len(events) + 1, "event": "page_rendered", "page": index, "reference_id": page["reference_id"]})
        hashes = {
            "page_spec": _json_hash(page["page_spec"]),
            "normalized_spec": _json_hash(page["normalized_spec"]),
            "reference_content": _json_hash(page["reference_content"]),
            "gold_svg": _file_hash(paths["gold_svg"]),
            "gold_native": _file_hash(paths["gold_native"]),
            "reference_svg": _file_hash(paths["reference_svg"]),
            "native_data": _file_hash(paths["native_data"]),
            "pptx": _file_hash(paths["pptx"]),
        }
        manifest_pages.append(
            {
                "page": index,
                "reference_id": page["reference_id"],
                "directory": page_dir.name,
                "canvas": page["canvas"],
                "artifacts": {key: str(path.relative_to(output_dir)) for key, path in paths.items()},
                "sha256": hashes,
                "source_footnote": page["source_footnote"],
                "visual_review": "not_performed",
            }
        )

    output_manifest = {
        "ok": True,
        "entry": "build_reference_deck.py",
        "page_count": len(manifest_pages),
        "input_manifest": prepared["manifest"],
        "preflight": prepared["preflight"],
        "events": events,
        "pages": manifest_pages,
        "merge_instruction": "Use scripts/merge_export.py for a same-ratio merged deck.",
        "visual_review": "not_performed",
        "powerpoint_roundtrip": "not_performed",
    }
    _write_json(output_dir / "reference-deck-manifest.json", output_manifest)
    return output_manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, help="Business JSON containing manifest and pages.")
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--validate-only", action="store_true")
    parser.add_argument("--describe", action="store_true")
    parser.add_argument("--describe-reference")
    args = parser.parse_args()
    try:
        if args.describe:
            print(json.dumps(describe_contract(), ensure_ascii=False, indent=2))
            return 0
        if args.describe_reference:
            print(json.dumps(describe_reference(args.describe_reference), ensure_ascii=False, indent=2))
            return 0
        if args.input is None:
            parser.error("--input is required for validation or generation")
        document = _load_document(args.input)
        if args.validate_only:
            result = preflight_reference_deck(document)["preflight"]
        else:
            if args.output_dir is None:
                parser.error("--output-dir is required for generation")
            result = build_reference_deck(document, output_dir=args.output_dir)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except ReferenceDeckError as exc:
        payload = {"ok": False, "error": {"code": exc.code, "message": str(exc)}, "report": exc.report}
        print(json.dumps(payload, ensure_ascii=False, indent=2), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
