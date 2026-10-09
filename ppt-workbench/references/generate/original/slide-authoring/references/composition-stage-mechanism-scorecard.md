<!--
id: composition-stage-mechanism-scorecard
category: composition-branch
read_when: 页面需要同时说明阶段流程、为什么该机制有效，以及结果指标如何变化
page_roles: content, summary
supports: svg_drawingml
outputs: stage_mechanism_scorecard_spec, flow_capacity_decision, svg_group_plan
depends_on: composition-business-report-argument-cascade.md
relation_specs: requires:composition-business-report-argument-cascade, requires:template-series-composite-builder, pairs_with:layout-process-flow, pairs_with:layout-phased-action-columns, pairs_with:layout-timeline-horizontal, pairs_with:layout-native-chart-slot
max_use: 常规 3-6 步；7 步是需真实渲染复核的高密受控变体；超过 7 步拆页
-->

# Composition Branch: Stage Mechanism Scorecard

## 输入与选择

- `stages[3..7]{label, action_or_output, gate?}`
- `mechanism_proofs[1..2]{claim, evidence_or_chart}`
- `outcomes[2..4]{baseline, result, unit, meaning}`

有明确输入/输出或 gate 时用流程；只有时间演进用 timeline；按月/季并列举措用 phased columns。

## 装配

`action title → stage flow → mechanism proof 1..2 → result scorecard → insight/action`

流程是主视觉，机制解释回答“为什么有效”，scorecard 回答“效果如何”。三者不能互相重复。

## 组合示例

输入：“展示六个门径阶段，并用并行工程和前置评审解释效率提升，底部放周期、延期率、变更次数三个 before/after。”

输出：`process-flow-6 + mechanism-proof-2up + metric-delta-3up + insight-rail`。

## 容量与失败

- 常规 3-6 步；7 步要求每步标题≤7字、说明≤2行并做真实预览；机制最多 2 个；结果 2-4 项。
- 只写阶段名、7 步强塞长文、用 timeline 表达无时间关系的并列成果、微图表伪装真实 chart，均不得完成。
