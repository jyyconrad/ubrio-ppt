<!--
id: composition-metric-system-with-case
category: composition-branch
read_when: 页面需要先定义指标体系，再用结果卡或改善案例解释指标如何驱动业务结果
page_roles: content, summary
supports: svg_drawingml
outputs: metric_taxonomy_spec, result_or_case_spec, evidence_alignment_checks
depends_on: composition-business-report-argument-cascade.md
relation_specs: requires:composition-business-report-argument-cascade, requires:template-series-composite-builder, pairs_with:layout-native-chart-slot, pairs_with:layout-sectioned-evidence-dashboard, pairs_with:layout-chart-insight-card, pairs_with:layout-full-width-rect-step-flow, pairs_with:layout-process-flow, pairs_with:svg-shape-patterns
max_use: 指标体系 2-3 类且每类不超过 3 个指标；更多内容拆成指标定义页和案例页
-->

# Composition Branch: Metric System With Case

## 输入与选择

- `metric_groups[2..3]{label, metrics[1..3]{name, definition, benchmark_or_target, implication}}`
- `proof_mode`: `outcome_cards | case_chain | native_chart | component_assembly`
- `proof_items[2..4]`
- `source_and_period`

先定义“测什么、怎么算、健康阈值是什么”，再证明“指标变化意味着什么”。指标名、定义、数值和洞察不能互相替代。

## 装配

`action title → metric taxonomy rows → result cards / case chain / native chart → conclusion or action`

- 结果是单值或 before/after，用 `metric-delta-card`。
- 结果是 4 步现象/根因/动作/成效，配 `layout-process-flow`。
- 结果是趋势、阈值或多个时间点，配 `layout-native-chart-slot`。
- 需要同时扫读 2 类、每类 2-3 个指标，并让每个指标都有微图/微表和洞察时，用 `layout-sectioned-evidence-dashboard` 分配 region，逐张生成 `chart_insight_card`；底部 RCA 另行生成一条 `full_width_rect_step_flow`，且只能解释其中一个代表性偏差。

## 组合示例

输入：“左边三个人效指标、右边三个资源指标，下方用一个四步案例解释为什么人增但产出不增。”

输出：`dual-metric-system + case-chain`，两组共享 row height；下方使用 `phenomenon → cause → action → outcome`。

输入：“效率和质量各三个指标，每卡一个高亮结果、一张趋势微图和一句洞察，底部解释一次延期的五层根因。”

输出：`chart_insight_card × 6 + native micro chart slots + full_width_rect_step_flow × 1`；外围分区由 assembly 负责，卡内严格保持“标题 → hero 结果 → 单一证据 → 洞察”，不再放第二段说明。

## 容量与失败

- 每组最多 3 指标；每个指标一个主数值和一句 implication；普通案例最多 4 步，RCA closure 最多 5 层。
- 目标写成实绩、标题数字没有同口径证据、洞察只复述数字、六张小图塞入过多标签，均不得完成。
