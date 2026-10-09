# Evidence & claim gate

Machine check: `scripts/svg/gates/evidence.py` → `check(spec) -> GateResult`.
`GateResult.missing` blocks `quality_status=ready`. Cover roles (`cover`, `section_divider`, `closing`, `end`) collect the same codes as `warnings` only.

Do not import `build_gold_svg_page`. This file is the field contract; the Python module is the machine check.

## Spec fields

### `metrics[]`

| field | required | notes |
| --- | --- | --- |
| label, value, note | yes (existing gold spec) | |
| evidence_type | yes | `experiment` / `survey` / `correlation` / `internal_baseline` / `policy` / `structure_count` / `category` (aliases: 实验/调查/相关/内部基线/政策/结构计数/品类) |
| claim_type | yes | `fact` / `inference` / `mechanism_hypothesis` / `action` (aliases: 事实/相关\|推断/机制假设/政策建议\|行动建议) |
| population | yes | sample / 口径主体 |
| period | yes | `year` is an accepted alias |
| denominator | yes | |
| source_ref | yes | satisfied by `source_url` or `source_section` |
| limitation | yes | caliber boundary, not a footnote-only disclaimer |
| on_metric_label | yes | on-metric visible: type · sample/caliber · limitation; not only a source-note |

### `claims[]` (optional)

`{text, claim_type, evidence_refs}`. Strong conclusions need `evidence_refs` length ≥ 2 plus a page-level `counterexample` or `boundary`.

### `native_chart_slots[]` / `charts[]` / `conceptual_charts[]`

`chart_kind` ∈ `{empirical, mechanism}`. Empirical requires `data` + `unit` + `source`. Line/bar/network with endpoints/coords and no data must be `chart_kind=mechanism` and labeled 假设链 / 待内部验证 / 示意.

## Blocking codes

| code | rule |
| --- | --- |
| `metrics[i].<field>` | KPI missing a required evidence field (C-01, C-14, V-06, EvidenceCard) |
| `heterogeneous_kpi_strip` | mixed `evidence_type` in one strip without each `on_metric_label` (C-01) |
| `structure_count_in_kpi_strip` | `structure_count` sharing a strip with outcome metrics (C-13) |
| `causal_verb_without_evidence_grade` | 导致/反噬/必达/必须/已升级 with only survey/correlation/category evidence (C-02, C-03) |
| `pseudo_empirical_chart` | endpoints/coords/line/bar/network, no data, `chart_kind` ≠ `mechanism` (V-04) |
| `native_chart_slots[i].data\|unit\|source\|chart_kind` | empirical chart missing payload (V-04) |
| `common_sense_as_strong_evidence` | source is only 常识 / 工程治理常识 used as KPI/strong evidence (C-14) |
| `current_kpi_without_internal_baseline` | 现状/当前 KPI visual without `internal_baseline`; use 待采集基线/试点验证指标 |
| `strong_claim_insufficient_evidence` | 已升级/必达/必须进入|达到 needs ≥2 direct items and 反例/边界 (C-03) |
| `math_illustration_as_prescription` | `n(n-1)/2` / 全连接 used as org advice without 示意/假设 (C-06) |
| `mechanism_diagram_unlabeled` | mechanism chart missing 假设链/待内部验证/示意 (C-02, V-04) |

## Wiring

Later, `quality_report` should call `check(spec)` and extend `missing` (content) or record warnings (cover roles). Do not change the gold builder in this gate.
