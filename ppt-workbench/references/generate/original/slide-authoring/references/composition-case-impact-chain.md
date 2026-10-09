<!--
id: composition-case-impact-chain
category: composition-branch
read_when: 已有基线、实施举措和量化结果，需要把案例写成可验证的成效证据链
page_roles: content, summary
supports: svg_drawingml
outputs: case_impact_page_spec, evidence_alignment_checks, svg_group_plan
depends_on: composition-business-report-argument-cascade.md
relation_specs: requires:composition-business-report-argument-cascade, requires:template-series-composite-builder, pairs_with:layout-process-flow, pairs_with:layout-kpi-strip, pairs_with:svg-shape-patterns
max_use: 只用于有真实 baseline、intervention 和 outcome 的案例；缺一项时先补证据或降级
-->

# Composition Branch: Case Impact Chain

## 输入与选择

- `headline_metrics[1..2]`
- `baseline_facts[2..4]`
- `interventions[3..5]`
- `outcomes[3..6]{name, baseline, result, unit, period, meaning, source}`
- `lesson_or_next_action`

只在举措与结果有可解释关系、数据口径可追溯时使用。没有 baseline 时改普通成果页；没有结果时改实施路线页。

## 装配

`action title → context-baseline → intervention-chain → metric-delta-strip → conclusion-band → source-note`

- 举措有严格顺序时配 `layout-process-flow`；只是并列抓手时改 2×2 或横向 action cards，不能伪造流程。
- 结果 3-6 个时配 `layout-kpi-strip`；趋势或多时点比较转 native chart。
- 标题只选最高价值的 1-2 个 outcome，并在 KPI 区同口径回指。

## 组合示例

输入：“说明试点改造前的三条基线、四项升级动作、交付周期和人均产出变化，并总结可复制经验。”

输出 group plan：

`context-baseline + flow-step-1..4 + metric-delta-1..4 + conclusion-band + source-note`

## 容量与失败

- baseline 2-4 条；举措 3-5 项；结果 3-6 个；lesson 1 句。
- 缺单位/周期/来源、目标冒充结果、标题数字与证据不一致、相关性写成已证明因果，均不得完成。
