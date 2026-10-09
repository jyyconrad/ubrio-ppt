"""Visual readability gates from session-884 (V-01/02/03/04/05/07/09)."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "svg"))

from gates.visual import (  # noqa: E402
    BODY_PX_MIN,
    MAX_TINY_TEXT_RATIO,
    compute_layout_fingerprint,
    check,
    check_svg,
)


def _three_cards() -> list[dict]:
    return [
        {"title": "判断一", "claim": "短判断句", "evidence": ["证据甲", "证据乙"]},
        {"title": "判断二", "claim": "短判断句", "evidence": ["证据甲", "证据乙"]},
        {"title": "判断三", "claim": "短判断句", "evidence": ["证据甲", "证据乙"]},
    ]


def _content_spec(**overrides) -> dict:
    spec: dict = {
        "page_role": "content",
        "layout": "gold_cards",
        "layout_fingerprint": (
            "layout:gold_cards|visual:main-title+key-message+main-content"
        ),
        "structure_hierarchy": {
            "visual_layer": ["main-title", "key-message", "main-content"],
        },
        "typography": {"body_px": 16, "title_px": 32, "source_px": 11},
        "groups": _three_cards(),
    }
    spec.update(overrides)
    return spec


def _svg(inner: str) -> str:
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1280 720">'
        f"{inner}</svg>"
    )


def _body_texts(n: int = 4, size: int = 16) -> str:
    parts = []
    for i in range(n):
        parts.append(
            f'<text x="80" y="{180 + i * 28}" font-size="{size}" '
            f'fill="#334155">正文节点{i}</text>'
        )
    return "".join(parts)


class LayoutFingerprintTests(unittest.TestCase):
    def test_algorithm_layout_and_visual_layer(self) -> None:
        spec = {
            "layout": "Gold_Cards",
            "structure_hierarchy": {
                "visual_layer": [
                    "main-title",
                    "Key-Message",
                    "metric-strip",
                    "main-content",
                    "action-bar",
                ],
            },
        }
        self.assertEqual(
            compute_layout_fingerprint(spec),
            "layout:gold_cards|visual:main-title+key-message+metric-strip+main-content+action-bar",
        )

    def test_algorithm_layout_only(self) -> None:
        self.assertEqual(
            compute_layout_fingerprint({"layout": "gold_timeline"}),
            "layout:gold_timeline",
        )

    def test_algorithm_visual_only(self) -> None:
        self.assertEqual(
            compute_layout_fingerprint(
                {"structure_hierarchy": {"visual_layer": ["main-title", "main-content"]}}
            ),
            "visual:main-title+main-content",
        )

    def test_algorithm_empty_when_layout_and_visual_missing(self) -> None:
        self.assertIsNone(compute_layout_fingerprint({"page_role": "content"}))
        self.assertIsNone(
            compute_layout_fingerprint({"layout": "", "structure_hierarchy": {"visual_layer": []}})
        )


class SpecVisualGateTests(unittest.TestCase):
    def test_body_px_below_min_is_missing(self) -> None:
        result = check(_content_spec(typography={"body_px": 13, "title_px": 32}))
        self.assertIn("body_px", result.missing)
        self.assertTrue(result.blocked())

    def test_body_px_missing_on_content_page(self) -> None:
        spec = _content_spec()
        spec["typography"] = {"title_px": 32}
        result = check(spec)
        self.assertIn("body_px", result.missing)

    def test_table_cell_over_max_chars_is_missing(self) -> None:
        spec = _content_spec(
            layout="gold_evidence_table",
            columns=["事项", "证据"],
            rows=[
                {
                    "cells": [
                        "这是一段远远超过十八个汉字限制的单元格正文必须拆页",
                        "短",
                    ]
                }
            ],
        )
        result = check(spec)
        self.assertIn("table_capacity", result.missing)

    def test_table_too_many_columns_for_width_is_missing(self) -> None:
        spec = _content_spec(
            layout="gold_evidence_table",
            table={"width": 600, "columns": ["A", "B", "C", "D", "E", "F"]},
            columns=["A", "B", "C", "D", "E", "F"],
            rows=[{"cells": ["一", "二", "三", "四", "五", "六"]}],
        )
        result = check(spec)
        self.assertIn("table_capacity", result.missing)

    def test_table_too_many_columns_is_missing(self) -> None:
        cols = [f"列{i}" for i in range(7)]
        spec = _content_spec(
            layout="gold_evidence_table",
            columns=cols,
            rows=[{"cells": ["x"] * 7}],
        )
        result = check(spec)
        self.assertIn("table_capacity", result.missing)

    def test_semantic_fill_without_color_legend_is_missing(self) -> None:
        spec = _content_spec(
            metrics=[{"label": "通过", "value": "90%", "fill": "#16A34A"}],
        )
        result = check(spec)
        self.assertIn("color_legend", result.missing)

    def test_export_fonts_diverge_without_fallback_reason(self) -> None:
        spec = _content_spec(
            theme={"fonts": ["PingFang SC", "Helvetica Neue", "Arial"]},
            export_fonts=["Microsoft YaHei", "Arial"],
        )
        result = check(spec)
        self.assertIn("font_fallback_accepted", result.missing)

    def test_export_fonts_ok_with_fallback_reason(self) -> None:
        spec = _content_spec(
            theme={"fonts": ["PingFang SC", "Helvetica Neue", "Arial"]},
            export_fonts=["Microsoft YaHei", "Arial"],
            font_fallback_accepted="Windows PowerPoint 基线映射 PingFang SC→Microsoft YaHei",
        )
        result = check(spec)
        self.assertNotIn("font_fallback_accepted", result.missing)

    def test_content_page_fingerprint_missing_when_uncomputable(self) -> None:
        spec = {
            "page_role": "content",
            "typography": {"body_px": 16, "title_px": 32},
            "groups": _three_cards(),
        }
        result = check(spec)
        self.assertIn("layout_fingerprint", result.missing)
        self.assertIsNone(result.details.get("layout_fingerprint"))

    def test_fingerprint_computed_when_layout_present(self) -> None:
        spec = _content_spec()
        spec.pop("layout_fingerprint")
        result = check(spec)
        self.assertNotIn("layout_fingerprint", result.missing)
        self.assertEqual(
            result.details.get("layout_fingerprint"),
            "layout:gold_cards|visual:main-title+key-message+main-content",
        )
        self.assertTrue(
            any("layout_fingerprint" in w for w in result.warnings)
            or result.details.get("layout_fingerprint_source") == "computed"
        )

    def test_valid_spec_body_16_three_cards_fingerprint_empty_missing(self) -> None:
        result = check(_content_spec())
        self.assertEqual(result.missing, [])
        self.assertFalse(result.blocked())
        self.assertGreaterEqual(
            result.details.get("body_px") or BODY_PX_MIN, BODY_PX_MIN
        )

    def test_cover_without_body_px_not_blocked(self) -> None:
        result = check({"page_role": "cover", "title": "封面标题"})
        self.assertNotIn("body_px", result.missing)
        self.assertNotIn("layout_fingerprint", result.missing)

    def test_seven_cards_exceeds_max(self) -> None:
        cards = [
            {"title": f"卡{i}", "claim": "短句", "evidence": ["证"]}
            for i in range(7)
        ]
        result = check(_content_spec(groups=cards))
        self.assertIn("card_capacity", result.missing)

    def test_four_across_title_too_long(self) -> None:
        cards = [
            {"title": "这是超过十二字的卡片长标题", "claim": "短句", "evidence": ["证"]}
            for _ in range(4)
        ]
        result = check(_content_spec(groups=cards, columns_across=4))
        self.assertIn("card_capacity", result.missing)


class SvgVisualGateTests(unittest.TestCase):
    def test_main_content_font_12_without_source_note_id_missing(self) -> None:
        svg = _svg(
            '<g id="main-content">'
            '<text font-size="12" fill="#334155" x="80" y="240">正文过小</text>'
            "</g>"
            + _body_texts(4, 16)
        )
        result = check_svg(svg)
        self.assertIn("svg_body_font_px", result.missing)

    def test_font_size_px_suffix_and_style_attr(self) -> None:
        svg = _svg(
            '<g id="main-content">'
            '<text font-size="12px" fill="#334155" x="80" y="240">属性px</text>'
            '<text style="font-size:13px" fill="#334155" x="80" y="270">样式号</text>'
            "</g>"
            + _body_texts(4, 16)
        )
        result = check_svg(svg)
        self.assertIn("svg_body_font_px", result.missing)

    def test_source_note_11px_allowed(self) -> None:
        svg = _svg(
            _body_texts(4, 16)
            + '<g id="source-note">'
            '<text font-size="11" fill="#64748B" x="80" y="700">来源：DORA 2024</text>'
            "</g>"
        )
        result = check_svg(svg)
        self.assertNotIn("svg_body_font_px", result.missing)
        self.assertNotIn("tiny_text_ratio", result.missing)
        exceptions = result.details.get("font_exceptions") or []
        self.assertTrue(exceptions)

    def test_tiny_text_ratio_too_high_is_missing(self) -> None:
        inner = (
            '<text font-size="16" fill="#334155" x="80" y="120">主1</text>'
            '<text font-size="16" fill="#334155" x="80" y="150">主2</text>'
            '<text id="source-note" font-size="11" fill="#64748B" x="80" y="680">来源</text>'
            '<text class="flow-label" font-size="12" fill="#64748B" x="80" y="400">标签一</text>'
            '<text class="kicker" font-size="10" fill="#64748B" x="80" y="430">标签二</text>'
            '<text class="evidence-gap" font-size="11" fill="#64748B" x="80" y="460">缺口</text>'
        )
        result = check_svg(_svg(inner))
        self.assertIn("tiny_text_ratio", result.missing)
        ratio = result.details.get("tiny_text_ratio")
        self.assertGreater(ratio, MAX_TINY_TEXT_RATIO)

    def test_semantic_svg_fill_without_legend_is_missing(self) -> None:
        svg = _svg(
            _body_texts(4, 16)
            + '<rect x="80" y="300" width="40" height="20" fill="#16A34A"/>'
            '<rect x="130" y="300" width="40" height="20" fill="#DC2626"/>'
        )
        result = check_svg(svg, _content_spec())
        self.assertIn("color_legend", result.missing)

    def test_semantic_svg_fill_with_legend_ok(self) -> None:
        spec = _content_spec(
            color_legend=[
                {"color": "#16A34A", "meaning": "pass"},
                {"color": "#DC2626", "meaning": "risk"},
            ]
        )
        svg = _svg(
            _body_texts(4, 16)
            + '<rect x="80" y="300" width="40" height="20" fill="#16A34A"/>'
            '<rect x="130" y="300" width="40" height="20" fill="#DC2626"/>'
        )
        result = check_svg(svg, spec)
        self.assertNotIn("color_legend", result.missing)

    def test_axisless_polyline_without_mechanism_kind_fails(self) -> None:
        svg = _svg(
            _body_texts(4, 16)
            + '<polyline points="80,400 160,320 240,360 320,280" fill="none" stroke="#2563EB"/>'
        )
        result = check_svg(svg)
        self.assertIn("chart_unlabeled", result.missing)

    def test_mechanism_polyline_allowed(self) -> None:
        svg = _svg(
            _body_texts(4, 16)
            + '<polyline data-chart-kind="mechanism" points="80,400 160,320 240,360 320,280" '
            'fill="none" stroke="#2563EB"/>'
        )
        result = check_svg(svg)
        self.assertNotIn("chart_unlabeled", result.missing)

    def test_gold_builder_body_sizes_fail_unless_tagged(self) -> None:
        svg = _svg(
            '<g id="main-content">'
            '<text font-size="14" fill="#334155" x="90" y="330">组判断</text>'
            '<text font-size="13" fill="#334155" x="90" y="360">• 要点</text>'
            '<text font-size="12" fill="#334155" x="90" y="400">单元格</text>'
            "</g>"
            + _body_texts(4, 16)
        )
        result = check_svg(svg)
        self.assertIn("svg_body_font_px", result.missing)


if __name__ == "__main__":
    unittest.main()
