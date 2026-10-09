<!--
id: template-series-violet-quarterly-overview
category: template-series
read_when: 需要复用 ppt3 的紫色季度半年年度经营总览系列，组合 KPI、月份、事件、North-star、成果和复盘页时
page_roles: content, summary
supports: svg_drawingml
outputs: series_visual_contract, page_archetype_menu, shape_composition_grammar, composite_resource_plan
depends_on: template-series-composite-builder.md, scenario-annual-summary.md
relation_specs: requires:template-series-composite-builder, pairs_with:composition-metric-system-with-case, pairs_with:composition-case-impact-chain, pairs_with:layout-kpi-strip, pairs_with:layout-phased-action-columns, pairs_with:layout-arrow-ribbon-metrics
max_use: 作为紫色经营总结的宽系列；目标、计划和实际结果必须明确区分
source_notice: 来源为 ppt3.jpg visual-only 营销拼页；缩略页只能作为局部视觉证据。
-->

# ppt3 系列：紫色经营总结总览

## 系列视觉逻辑

- 白底、深紫结构头、主紫关键数字、浅紫次级面，单一色系通过面积与明度建立层级。
- 页顶常用 KPI strip，主体按季度、月份、成果方向或四主题组织，右侧 rail/底部带翻译管理意义。
- 全册可以覆盖结果摘要、时间事实、年度目标、问题改进和计划，但每页只选一个主关系。
- 目标、达成、预测和计划的标签不能省略，避免视觉相似导致口径混淆。

## 页面展示系统

- 3-4 个 KPI + 三期行动列。
- 六个月事件跨度网格 + 右侧总结 rail。
- North-star 屋顶 + 三段管理条 + 3-5 个 KPI。
- 3-6 段成果箭头带。
- 四主题中心圆簇 + 四角证据卡。
- 目标 vs 达成对决、问题改进和 Gantt 作为受控页型；真实数据用 native 对象。

## 形状组合语法

- `kpi strip + phased columns` 用于季度行动。
- `month headers + span cards + summary rail` 用于跨月事件。
- `roof + management rail + dog-ear metrics + conclusion` 用于年度 north-star。
- `chevron ribbon + evidence note + metric box` 用于并列成果。
- `four evidence cards + 2x2 central cluster` 用于四主题亮点。

## 快速组合示例

- 7-12 月跨月活动：`calendar_summary_rail`，用 `start/end` 计算事件宽度。
- 年度关键指标：`north_star_kpi_roof`。
- 六项年度成果：`arrow_ribbon_metrics`。
- 四类工作亮点：`highlight_matrix_core`。

选择 `build-series-composite-svg` 物化资源，独立预检可选
`validate-series-composite-svg-spec`；系列确定后只替换 data，具体执行入口由当前 consumer 决定。

## 容量与失败

- 月份 3-6、事件 1-8、总结 1-3；成果段 3-6；KPI 3-5；中心主题恰 4。
- 失败：超过 8 个事件仍用 SVG 网格、手绘真实 Gantt/图表、紫色逐卡随机变化、目标和实际混写。
