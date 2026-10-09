<!--
id: composition-architecture-value-proof
category: composition-branch
read_when: 页面需要展示平台、层级、模块或能力架构，并证明它如何产生业务价值
page_roles: content, summary
supports: svg_drawingml
outputs: architecture_value_spec, capability_value_mapping, svg_group_plan
depends_on: composition-business-report-argument-cascade.md
relation_specs: requires:composition-business-report-argument-cascade, requires:template-series-composite-builder, pairs_with:layout-pyramid-hierarchy, pairs_with:layout-center-radial, pairs_with:layout-process-flow, pairs_with:svg-shape-patterns
max_use: 架构节点 3-5 个，结果 3-5 项；复杂系统先拆层再单独解释
-->

# Composition Branch: Architecture Value Proof

## 输入与选择

- `architecture_type`: `hierarchy | shared_source_platforms | radial | operating_layers`
- `nodes[3..5]{label, responsibility, input_or_output}`
- `common_capabilities[2..4]`
- `value_outcomes[3..5]{metric_or_fact, implication, source}`

架构不是结果。每个层、平台或能力必须能够映射到至少一个共性能力或价值 outcome。

## 装配

`action title → architecture → common-capability rail → value-proof strip → source-note`

- 自下而上依赖配 `layout-pyramid-hierarchy`。
- 中心目标与卫星能力配 `layout-center-radial`。
- 共享数据源到多平台互通配 `layout-process-flow` 的双向拓扑变体，但不得伪装单向流程。

## 组合示例

输入：“一套共享资源库支撑三个业务平台，说明标准统一、数据互通、流程贯通，并给出协同、透明和复用三项价值。”

输出：`shared-source + platform-cards + common-capability-rail + value-proof-3up`。

## 容量与失败

- 一源最多 3 平台；层级 3-5；价值 3-5 项。
- 只有系统盒子没有业务价值、箭头方向与关系不符、平台能力重复、价值与架构无映射，均需重构。
