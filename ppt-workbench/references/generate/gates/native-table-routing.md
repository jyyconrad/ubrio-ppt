# Native table routing

Page-level gate: `scripts/svg/gates/native_table.py` → `check(spec)` / `is_tabular_content(spec)`.

Call `native_table.check(spec)` on each content page after `page_spec` is filled and before `quality_status=ready`. Cover / section / closing pages are skipped. Do not import `build_gold_svg_page`.

## When a page must use a native table

`is_tabular_content` is true when any of these hold:

- layout is `gold_evidence_table` / `gold_action_ledger` / `gold_issue_log` / `table`
- `columns` plus ≥3 data `rows`
- product-comparison groups that repeat the same dimension keys (a matrix, not cards)

Then the spec must have `native_table_slots` with `columns` and `rows`. Empty slots set missing `native_table_required`.

SVG may fake a table only when `table_fallback_reason` is a non-empty string (warning `table_fallback_reason`, not blocking).

`native.cjs` already has `table()`. This gate only routes; it does not draw.

## Slot contract

Same idea as `native_chart_slots`. SVG draws a slot rect + caption only.

```json
{
  "id": "table-slot-1",
  "box": {"x": 70, "y": 288, "w": 1140, "h": 360},
  "columns": ["产品", "部署", "数据驻留"],
  "rows": [["A", "本地", "内网"]],
  "source": "公开能力综述"
}
```

Missing code: `native_table_required`.
