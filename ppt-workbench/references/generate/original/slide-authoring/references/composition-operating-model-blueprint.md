<!--
id: composition-operating-model-blueprint
category: composition-branch
runtime_scope: controlled_extension
read_when: 需要用北极星、双重 enabler、多层能力、横向协同和价值结果组成 operating model 总蓝图
page_roles: content, summary
supports: svg_drawingml
outputs: operating_model_spec, hierarchy_collaboration_mapping, svg_group_plan
depends_on: composition-business-report-argument-cascade.md
relation_specs: requires:composition-business-report-argument-cascade, requires:template-series-composite-builder, pairs_with:layout-pyramid-hierarchy, pairs_with:layout-process-flow, pairs_with:layout-kpi-strip, pairs_with:svg-shape-patterns
max_use: 作为参数化组合候选，不把屋顶、一核两翼四层或任何单一截图造型固化为 established layout
-->

# Composition Branch: Operating Model Blueprint

## 输入与选择

- `north_star`：恰 1 个业务目标。
- `enablers[2]`：两种互补方法、机制或底座；不是随意凑双轮。
- `layers[3..5]{label, responsibility, capability_terms[1..3]}`。
- `collaboration_loops[1..2]{parties, flow, feedback}`。
- `value_outcomes[3..5]`。

本分支只提供组合合同。目标造型可以是顶条、轻量屋顶或 north-star badge；不得记忆源截图坐标和“一核两翼四层”文案。

## 装配

`north-star → enablers → vertical layers` 是纵向主轴；`collaboration loops` 作为横向 sidecar；底部 `value outcomes` 回答体系价值。

- 层级关系复用 `layout-pyramid-hierarchy` 的比例和容量方法。
- 协同关系复用 `layout-process-flow` 的双向连接纪律。
- 结果复用 `layout-kpi-strip` 或 `metric-delta-card`。

## 组合示例

输入：“以客户价值为北极星，流程精益和数字工具为双重 enabler，组织成战略、运营、工程、基础四层，并展示市场/研发、制造/研发两条反馈闭环和五项结果。”

输出：`north-star + enabler-2up + layer-stack-4 + collaboration-loop-2 + value-strip-5`。

## 容量与失败

- 北极星 1、enabler 恰 2、层级 3-5、协同 1-2、结果 3-5。
- enabler 不是互补关系、层级职责重叠、协同只有箭头没有信息流/反馈、总蓝图缺实施承接，均需修正。
