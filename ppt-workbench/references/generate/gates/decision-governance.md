# Decision governance gates

Page-level checks for session-884 C-04 and C-07–C-12. Home: `scripts/svg/gates/decision.py`.

## Hook

`quality_report(spec)` should call `gates.decision.check(spec)` and extend `missing`. Any `GateResult.missing` item blocks `quality_status=ready`. Cover / section_divider / closing / end skip blocking checks. Do not import `build_gold_svg_page`.

Scan `title`, `key_message`, `layout`, group titles, `columns`, and `table_title`. Do not require a new layout name.

## Fields (optional unless triggered)

| Field | Shape |
| --- | --- |
| `decisions` | DecisionCard list: `decision`, `options`, `criteria`, `owner`, `deadline`, `cost_or_risk`, `reversible`, `reject_condition`, `next_evidence` |
| `raci` | `{columns: ["R","A","C","I"], rows}` or `role_mapping`. Else forbid the word RACI and use `responsibility_boundary` |
| `north_star` | `{name, baseline, window, threshold, owner, alert, stop_rule}`. No internal baseline → `待采集`. Direction words are not KPIs |
| `stages` | `[{name, artifacts, gate: {check, threshold, evidence_ref, approver, exception_policy}}]` |
| `artifacts` | `[{id, name, stage_id, owner, gate_id}]`. Every artifact maps to stage + gate + owner |
| `roadmap` | `[{horizon, items: [{action, predecessor, resource_owner, budget_or_permission, exit_threshold, delay_policy, status}]}]`. `status` is `proposal` or `committed` |
| `product_matrix` | `{dimensions, rows, status: pending_validation\|internally_validated}`. Dimensions: deploy form, data residency, permission model, context access, cost, audit, integration, measured results |

## Missing codes

| Code | Repair |
| --- | --- |
| `raci_schema` | Four R/A/C/I columns or explicit role mapping; otherwise drop RACI |
| `decision.options` / `decision.criteria` / `decision.owner` / `decision.deadline` / `decision.reject_condition` | Fill DecisionCard. Also `decision.cost_or_risk`, `decision.reversible`, `decision.next_evidence` |
| `north_star.baseline` | Plus `window` / `threshold` / `owner` / `alert` / `stop_rule` |
| `gate.threshold` | Plus `check` / `evidence_ref` / `approver` / `exception_policy`. Principle sentences are not release conditions |
| `artifact_stage_unmapped` | Map each artifact to a stage, gate, and owner |
| `product_matrix.pending_validation` | Add decision dimensions or mark `status=pending_validation`. No internal pilot → 待验证矩阵, not a default stack |
| `roadmap.proposal_required` | Add exit/resource fields or mark `status=proposal` |
