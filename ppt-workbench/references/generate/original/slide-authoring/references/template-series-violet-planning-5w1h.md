<!--
id: template-series-violet-planning-5w1h
category: template-series
read_when: 需要复用 ppt5 的紫色个人目标规划、月度目标行动评估和 5W1H/PDCA 计划系列时
page_roles: content, summary
supports: svg_drawingml
outputs: series_visual_contract, page_archetype_menu, shape_composition_grammar, composite_resource_plan
depends_on: template-series-composite-builder.md, layout-timeline-anchored-columns.md
relation_specs: requires:template-series-composite-builder, pairs_with:composition-stage-mechanism-scorecard, pairs_with:layout-phased-action-columns, pairs_with:layout-native-chart-slot
max_use: 月度目标轴只用于 4-6 期；复杂 Gantt、责任矩阵和日级排期必须走 native table 或专用 overlay
source_notice: 来源为 ppt5.jpg visual-only 营销拼页；可见两个主页面，不能证明表格对象类型或可编辑性。
-->

# ppt5 系列：紫色目标计划与 5W1H 执行

## 系列视觉逻辑

- 深紫色时间主轴和月份节点提供唯一推进方向，白色纵向任务卡承载高密说明。
- 每个月份共享 `目标 → 行动计划 → 结果评估` schema，强调可比较、可追踪和可验收。
- 强调月份允许用深紫实底卡，但只能有一个当前焦点，不能每月都高亮。
- 计划页与执行表页形成“管理叙事 → 落地台账”的跨页承接。

## 页面展示系统

- 4-6 月目标行动评估轴：顶部节点、下方等宽纵卡。
- 5W1H/PDCA 计划表：WHAT/WHEN/WHO/WHERE/HOW + 计划/实施线。
- 月度轴适合汇报，精确 Gantt 适合执行；不得用一个页面同时承担两种密度。
- 台账页必须保留 Owner、时间、地点/范围、方法/工具和验收结果。

## 形状组合语法

- `long arrow rail + period circles + aligned semantic cards`。
- `semantic card = goal row + action row + result row`，三行标签位置和高度跨月份稳定。
- 当前月份使用实底反白，其他月份使用白底紫边，视觉焦点不改变列宽。
- 真实 Gantt 由结构化表格和时间线对象承载；SVG 不手绘大量周网格。

## 快速组合示例

“把 1-6 月计划按目标、行动、结果评估展开，4 月是关键里程碑”时使用
`target_action_timeline`，填写 `periods[4..6]` 并仅给 4 月 `emphasis=true`。
选择 `build-series-composite-svg` 物化资源，独立预检可选
`validate-series-composite-svg-spec`；复用时只替换 data，具体执行入口由当前 consumer 决定。

## 容量与失败

- 4-6 期；每期一个目标、1-2 个动作、一个结果；每个语义槽最多 2-3 行。
- 失败：没有真实时间顺序、结果字段写成下一步动作、6 期以上仍用窄卡、执行表缺 Owner 或验收。
