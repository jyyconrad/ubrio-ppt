# Deck consistency

Deck-level gate: `scripts/svg/gates/deck_consistency.py` → `check_deck(specs)`.

Run once after every page spec exists. `GateResult.missing` blocks deck `quality_status=ready`. Page-level table routing is `native_table.check`; this module only checks homology and rhythm.

## skeleton_key

1. If `spec["layout_fingerprint"]` is non-empty, use it.
2. Else `layout + "|" + ",".join(visual_layer)`.
3. `visual_layer` is `spec["visual_layer"]`, else `spec["structure_hierarchy"]["visual_layer"]`.

Same skeleton may appear on at most two consecutive **content** pages.

## Missing codes

| code | rule |
| --- | --- |
| `skeleton_repeat` | 3+ consecutive content pages share `skeleton_key` |
| `product_list_drift` | product name sets differ and no deck `product_alias` map closes them |
| `artifact_dictionary` | hard-artifact list vs stage artifacts is not a closed union (unmapped items such as 评测集) |
| `repeated_metric_role` | same metric value on ≥3 pages with the same `number_role` |
| `chapter_rhythm` | 4+ consecutive content pages with no `section_divider`; **missing** if `section` is unchanged, **warning** if `section` still changes |
| `color_legend` | semantic colors used and legends contradict (or none exist) |

Repeat a number only when `number_role` changes (evidence → constraint → decision) and `number_purpose` is stated.

KPI strip / conclusion band / section bar: at most two consecutive content pages (warnings `kpi_strip_reuse`, `conclusion_band_reuse`, `section_bar_reuse`).
