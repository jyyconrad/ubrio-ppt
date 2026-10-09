# Visual readability gates

Machine-checkable deltas on top of [内容密度合同](../original/slide-authoring/references/contract-content-density.md). Copy/capacity rewriting still follows that contract; this file only lists gates in `scripts/svg/gates/visual.py`.

Cover / section / closing may keep extra whitespace. Body size and contrast still apply when those texts exist.

## Size (V-02)

- Body ≥ 15px. Below 15px only `source-note` / `evidence-gap` / `flow-label` / `kicker` (id/class/`data-role`), recorded in `details.font_exceptions`.
- Source 9–11px allowed. Title 28–34px on content pages (warning if outside).
- Gold-builder 14/13/12px claims, bullets, cells, timeline copy fail `svg_body_font_px` unless tagged.

## Capacity (V-03 / V-09)

- `max_cards` 6.
- 4-across: title ≤ 12 CJK, body ≤ 2 lines × 20 CJK.
- Table: ≤ 6 cols, ≤ 10 rows, ≤ 18 CJK/cell, ≤ 2 lines/cell, min col 120px on a 1280 canvas. Overflow → `table_capacity` (split page).
- Tiny-text ratio: at most 25% of `<text>` nodes may be &lt; 15px.

## `layout_fingerprint` (V-01)

Page-level field so deck_consistency can cap consecutive skeleton reuse (cap is not this module).

```
layout:{lower(layout)}|visual:{lower(slot)+...}
```

- `layout` from `spec.layout` or `spec.layout_id`.
- slots from `structure_hierarchy.visual_layer` (else `spec.visual_layer`), order preserved.
- Omit empty parts. `None` only when both layout and visual_layer are empty → missing `layout_fingerprint` on content pages.
- If the field is absent but computable, write it to `details.layout_fingerprint` and warn; do not miss.

Public helper: `compute_layout_fingerprint(spec)`.

## Fonts (V-05)

If `export_fonts` is present and differs from `theme.fonts` / `font_family`, require a non-empty `font_fallback_accepted` reason.

## Color (V-07)

Green/red/orange fills (`#16A34A`, `#DC2626`, and kin) require `color_legend` covering those colors. Colored numbers are not a substitute for `evidence_type`.

## Charts (V-04)

Axis-less polyline / L-path / bar-strip / line-network that looks like a data chart fails `chart_unlabeled` unless `data-chart-kind=mechanism` (概念机制图) or spec already declares chart data. Empirical-vs-mechanism claim checks stay in evidence.py.

## Missing codes

| code | when |
| --- | --- |
| `body_px` | content page body &lt; 15 or typography.body_px missing |
| `svg_body_font_px` | SVG body `<text>` &lt; 15px without exception tag |
| `tiny_text_ratio` | &gt; 25% of text nodes &lt; 15px |
| `table_capacity` | cols/rows/chars/lines/col-width overflow |
| `card_capacity` | &gt; 6 cards or 4-across title/body overflow |
| `layout_fingerprint` | content page and fingerprint not computable |
| `font_fallback_accepted` | design vs export fonts diverge, no reason |
| `color_legend` | semantic green/red/orange without legend |
| `chart_unlabeled` | data-like SVG mark with no mechanism tag / data |
| `contrast` | body text contrast &lt; 4.5 |
| `svg_parse` | SVG is not well-formed |
