"""Local write → validate → render pipeline (no websocket or workspace writeback)."""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path
from typing import Any

_SVG_DIR = Path(__file__).resolve().parent.parent
if str(_SVG_DIR) not in sys.path:
    sys.path.insert(0, str(_SVG_DIR))

import overlay_native_slots as overlay  # noqa: E402

from .adapter import create_native_pptx_from_svg_files
from .authoring import validate_svg_string_for_authoring
from .color_scheme_gate import build_color_scheme_report
from .input_gate import validate_svg_input
from .native_placeholders import strip_native_slot_placeholder_texts

_SLOT_MARKERS = (
    "native-chart-slot",
    "native-table-slot",
    "native-sankey-slot",
    "native-image-slot",
    "data-native-chart",
    "data-native-table",
    "data-native-sankey",
    "data-native-image",
    "data-native-data-ref",
)


def validate_svg_drawingml(
    *,
    svg_text: str | None = None,
    svg_path: Path | str | None = None,
    mode: str = "fast",
    allow_framework_chrome: bool = False,
    native_data: dict[str, Any] | None = None,
    style_manifest_snapshot: dict[str, Any] | None = None,
    icons_root: Path | None = None,
    assets_dir: Path | None = None,
    artifact_kind: str = "page",
) -> dict[str, Any]:
    """Expand icons, gate content SVG, diagnose slots. Color warnings are non-blocking."""

    if artifact_kind not in {"page", "component"}:
        return _fail("SVG_ARTIFACT_KIND_INVALID", "artifact_kind must be page or component")
    path = Path(svg_path) if svg_path is not None else None
    if svg_text is None:
        if path is None:
            return _fail("SVG_INVALID_XML", "需要 svg_text 或 svg_path。")
        svg_text = path.read_text(encoding="utf-8")
    ok, issue = validate_svg_string_for_authoring(svg_text)
    if not ok and issue is not None:
        return _fail(str(issue.get("code") or "SVG_INVALID_XML"), str(issue.get("message") or "invalid svg"))

    icon_report = overlay.expand_page_icons(svg_text, icons_root=icons_root)
    if not icon_report["ok"]:
        return {
            "ok": False,
            "ready_to_render": False,
            "status": "blocked",
            "issues": icon_report["issues"],
            "warnings": [],
            "icon_expanded_count": icon_report.get("expanded_count") or 0,
        }
    expanded = str(icon_report["svg"])
    gate = validate_svg_input(expanded, allow_framework_chrome=allow_framework_chrome,
                              page_archetype="component" if artifact_kind == "component" else None)
    issues = [dict(item) for item in gate.blocking_issues]
    warnings = [dict(item) for item in gate.warnings]
    native, native_issues = _load_native_data(path, svg_text, native_data)
    issues.extend(native_issues)
    slot_report = overlay.diagnose_native_slots(
        expanded,
        native,
        assets_dir=assets_dir or (path.parent if path else None),
    )
    issues.extend(slot_report.get("issues") or [])
    warnings.extend(slot_report.get("warnings") or [])
    stripped_svg, placeholder = strip_native_slot_placeholder_texts(expanded)
    issues.extend(dict(item) for item in placeholder.blocking_issues)
    warnings.extend(dict(item) for item in placeholder.warnings)
    normalized_mode = (mode or "fast").strip().lower()
    if normalized_mode not in {"fast", "full"}:
        return _fail("SVG_VALIDATE_MODE_INVALID", "mode 只能是 fast 或 full。")
    if normalized_mode == "full" and placeholder.stripped_count:
        if not any(item.get("code") == "NATIVE_SLOT_PLACEHOLDER_TEXTS_WILL_BE_REMOVED" for item in warnings):
            warnings.append(
                {
                    "code": "NATIVE_SLOT_PLACEHOLDER_TEXTS_WILL_BE_REMOVED",
                    "message": (
                        f"slot 分组内有 {placeholder.stripped_count} 段占位文字，"
                        "渲染时会被自动移除；真实标题/洞察/来源请放在 slot box 之外。"
                    ),
                    "samples": [dict(item) for item in placeholder.stripped_samples],
                    "severity": "warning",
                }
            )
    color_checked = False
    if normalized_mode == "full":
        try:
            color_report = build_color_scheme_report(
                expanded,
                style_manifest_snapshot=style_manifest_snapshot,
            )
            color_checked = bool(color_report.get("checked"))
            if color_checked:
                for warning in color_report.get("warnings") or []:
                    if isinstance(warning, dict):
                        warning.setdefault("severity", "warning")
                        warnings.append(warning)
        except Exception:  # noqa: BLE001
            color_checked = False
    blocking = [item for item in issues if item.get("severity") != "warning"]
    ok_result = not blocking
    return {
        "ok": ok_result,
        "ready_to_render": ok_result,
        "status": "ready_to_render" if ok_result else "blocked",
        "mode": normalized_mode,
        "issues": blocking,
        "warnings": warnings,
        "icon_expanded_count": icon_report.get("expanded_count") or 0,
        "expanded_svg": expanded,
        "stripped_svg": stripped_svg,
        "color_scheme_checked": color_checked,
        "svg_summary": dict(gate.summary),
        "allow_framework_chrome": allow_framework_chrome,
    }


def render_svg_drawingml(
    *,
    svg_path: Path | str,
    output: Path | str,
    native_data: dict[str, Any] | Path | str | None = None,
    assets_dir: Path | str | None = None,
    icons_root: Path | None = None,
    style_manifest_snapshot: dict[str, Any] | None = None,
    canvas_format: str = "ppt169",
    artifact_kind: str = "page",
) -> dict[str, Any]:
    """expand → validate → strip placeholders → native PPTX → local overlays."""

    path = Path(svg_path)
    output_path = Path(output)
    svg_text = path.read_text(encoding="utf-8")
    native_payload, native_path = _coerce_native_data(native_data, path)
    report = validate_svg_drawingml(
        svg_text=svg_text,
        svg_path=path,
        mode="full",
        allow_framework_chrome=False,
        native_data=native_payload,
        style_manifest_snapshot=style_manifest_snapshot,
        icons_root=icons_root,
        assets_dir=Path(assets_dir) if assets_dir else path.parent,
        artifact_kind=artifact_kind,
    )
    if not report["ok"]:
        report["pptx"] = None
        return report
    expanded = str(report["expanded_svg"])
    stripped = str(report.get("stripped_svg") or expanded)
    with tempfile.TemporaryDirectory(prefix="svg-drawingml-") as tmp:
        work_svg = Path(tmp) / "source.svg"
        work_svg.write_text(stripped, encoding="utf-8")
        trace_path = Path(tmp) / "conversion.trace.json"
        try:
            ok = create_native_pptx_from_svg_files(
                [work_svg],
                output_path,
                canvas_format=canvas_format,
                verbose=False,
                merge_paragraphs=False,
                conversion_trace_path=trace_path,
            )
        except Exception as exc:  # noqa: BLE001
            report["ok"] = False
            report["ready_to_render"] = False
            report["status"] = "blocked"
            report["issues"] = [
                *report["issues"],
                {"code": "SVG_DRAWINGML_CONVERT_FAILED", "message": str(exc), "severity": "error"},
            ]
            return report
        if not ok:
            report["ok"] = False
            report["ready_to_render"] = False
            report["status"] = "blocked"
            report["issues"] = [
                *report["issues"],
                {
                    "code": "SVG_DRAWINGML_CONVERT_FAILED",
                    "message": "create_native_pptx_from_svg_files returned False",
                    "severity": "error",
                },
            ]
            return report
    overlay_result = overlay.overlay_native_slots(
        svg_text=expanded,
        native_data=native_payload,
        output=output_path,
        pptx_path=output_path,
        assets_dir=Path(assets_dir) if assets_dir else path.parent,
    )
    report["ok"] = bool(overlay_result.get("ok"))
    report["status"] = "rendered" if report["ok"] else "blocked"
    report["pptx"] = str(output_path)
    report["overlay"] = overlay_result
    if native_path is not None:
        report["native_data"] = str(native_path)
    return report


def write_svg_file(
    *,
    output: Path | str,
    svg_text: str,
    validate: bool = True,
    layout_decision: dict[str, Any] | None = None,
) -> dict[str, Any]:
    ok, issue = validate_svg_string_for_authoring(svg_text)
    if not ok and issue is not None:
        return {
            "ok": False,
            "status": "blocked",
            "issues": [issue],
            "warnings": [],
        }
    path = Path(output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(svg_text, encoding="utf-8")
    result: dict[str, Any] = {
        "ok": True,
        "status": "written",
        "svg": str(path),
        "next_action": {
            "tool": "validate_svg_drawingml.py",
            "args": {"svg": str(path), "mode": "full"},
        },
    }
    if layout_decision is not None:
        decision_path = path.with_name("layout-decision.v1.json")
        decision_path.write_text(json.dumps(layout_decision, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        result["layout_decision"] = str(decision_path)
    if not validate:
        return result
    icon_report = overlay.expand_page_icons(svg_text)
    if not icon_report["ok"]:
        result["ok"] = False
        result["status"] = "written_invalid"
        result["issues"] = icon_report["issues"]
        return result
    gate = validate_svg_input(str(icon_report["svg"]), allow_framework_chrome=False)
    result["icon_expanded_count"] = icon_report.get("expanded_count") or 0
    result["issues"] = [dict(item) for item in gate.blocking_issues]
    result["warnings"] = [dict(item) for item in gate.warnings]
    if gate.blocking_issues:
        result["ok"] = False
        result["status"] = "written_invalid"
    return result


def _load_native_data(
    svg_path: Path | None,
    svg_text: str,
    native_data: dict[str, Any] | None,
) -> tuple[dict[str, Any] | None, list[dict[str, Any]]]:
    if isinstance(native_data, dict):
        return native_data, []
    if not _needs_native_data(svg_text):
        return None, []
    if svg_path is None:
        return None, [
            {
                "code": "NATIVE_DATA_FILE_NOT_FOUND",
                "message": "missing native-data.json next to source.svg",
                "severity": "error",
            }
        ]
    payload, _path, issues = overlay._resolve_native_data(svg_path, svg_text, None)
    return payload, issues


def _coerce_native_data(
    native_data: dict[str, Any] | Path | str | None,
    svg_path: Path,
) -> tuple[dict[str, Any] | None, Path | None]:
    if isinstance(native_data, dict):
        return native_data, None
    if native_data is not None:
        path = Path(native_data)
        return json.loads(path.read_text(encoding="utf-8")), path
    payload, path, _issues = overlay._resolve_native_data(svg_path, svg_path.read_text(encoding="utf-8"), None)
    return payload, path


def _needs_native_data(svg_text: str) -> bool:
    return any(marker in svg_text for marker in _SLOT_MARKERS)


def _fail(code: str, message: str) -> dict[str, Any]:
    return {
        "ok": False,
        "ready_to_render": False,
        "status": "blocked",
        "issues": [{"code": code, "message": message, "severity": "error"}],
        "warnings": [],
        "icon_expanded_count": 0,
        "color_scheme_checked": False,
    }
