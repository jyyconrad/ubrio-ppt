<!--
id: template-series-violet-calendar
category: template-series
read_when: 需要复用 ppt4 的紫色季度三栏或半年事件日历窄系列，强调时间事实和右侧管理总结时
page_roles: content, summary
supports: svg_drawingml
outputs: series_visual_contract, page_archetype_menu, shape_composition_grammar, composite_resource_plan
depends_on: template-series-composite-builder.md, layout-phased-action-columns.md
relation_specs: requires:template-series-composite-builder, pairs_with:composition-stage-mechanism-scorecard, pairs_with:layout-timeline-zigzag-groups, pairs_with:layout-kpi-strip
max_use: 只复用 ppt4 可见的季度/月度页族，不自动继承 ppt3 的全部紫色页型
source_notice: 来源为 ppt4.jpg visual-only 营销拼页，包含两个主展示页面。
-->

# ppt4 系列：紫色季度与半年时间复盘

## 系列视觉逻辑

- 月份/季度是第一分组，深紫期次头高于事件卡和正文。
- 白底、浅灰事件卡、细紫连接线；时间跨度必须由卡片宽度或位置真实表达。
- 每页同时存在“事实区 + 总结层”：季度页用 KPI/总结头，半年页用右侧管理 rail。
- 系列范围刻意收窄，不继承 North-star、VS 或四圆簇等未在主图出现的页型。

## 页面展示系统

- KPI 摘要 + 三个月主题行动列。
- 六个月、两个季度的事件跨度网格 + 右侧 2-3 项总结。
- 三阶段未来计划可复用三栏，但字段必须改为目标、行动、验收。
- 事件超过 8 个或需要日级精度时切到专用 Gantt/表格。

## 形状组合语法

- `grouped month headers + equal-width month columns` 建立时间刻度。
- `event span card` 的 x/width 由 `start/end` 计算，重叠事件分 lane。
- `summary rail` 只提炼管理判断，不重复左侧事件原文。
- 轻量框线和紫色短条维持高密可读，不用厚阴影或 3D。

## 快速组合示例

“7-12 月有三个跨月项目，右边总结三条成果”时使用 `calendar_summary_rail`：
填写 `months[3..6]`、`events[]{title,start,end}`、`summaries[1..3]`，由
由 `build-series-composite-svg` 物化资源计算跨度；复用时只替换 data，具体执行入口由当前 consumer 决定。

## 容量与失败

- 3-6 月份、1-8 事件、1-3 总结；单事件标题一行。
- 失败：`start > end`、跨度超出月份、事件过多仍压缩、summary 引入左侧没有的新事实。
