<!--
id: composition-pressure-bottleneck-positioning
category: composition-branch
read_when: 章节开篇或转型 Why 页需要从外部压力、内部瓶颈推进到体系定位
page_roles: content, summary
supports: svg_drawingml
outputs: scqa_positioning_spec, evidence_alignment_checks, svg_group_plan
depends_on: composition-business-report-argument-cascade.md
relation_specs: requires:composition-business-report-argument-cascade, requires:template-series-composite-builder, pairs_with:content-scqa, pairs_with:layout-left-claim-right-evidence, pairs_with:layout-native-chart-slot, pairs_with:svg-shape-patterns
max_use: 压力事实 2-3 项、瓶颈 3-4 项、定位 1 句；不要把完整方案提前塞进 Why 页
-->

# Composition Branch: Pressure Bottleneck Positioning

## 输入与选择

- `pressure_facts[2..3]`
- `pressure_chart?`
- `bottlenecks[3..4]{label, evidence_metric_or_fact}`
- `positioning_answer`

本分支用于 Why，不承担完整方案。它应出现在方案/架构/案例之前，为后续页面建立问题方向。

## 装配

`action title → situation facts + conflict chart + insight → bottleneck grid → positioning answer`

内容逻辑配 `content-scqa`；真实趋势/对比配 native chart；底部 answer 用 conclusion band。

## 组合示例

输入：“说明市场周期从 18 个月压缩到 8-12 个月，归纳流程、复用、度量、用户传导四个瓶颈，最后给出体系升级定位。”

输出：`pressure-3facts + native-comparison-chart + bottleneck-4up + conclusion-band`。

## 容量与失败

- 压力 2-3 项；瓶颈 3-4 个，每个一个证据；定位一句。
- 瓶颈没有事实、结论带提前展开完整方案、Why 页放在大量 Proof 之后却不解释回溯目的，均需调整。
