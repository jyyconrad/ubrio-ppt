<!--
id: chart-combo-dashboard
category: layout
read_when: 当前页需要组合图/双轴/多指标经营看板/图表+指标卡混排
page_roles: content, summary
chart_types: combo
visual_tags: chart, cards
supports: svg_drawingml, native_chart_slot, metric_cards
outputs: chart_type_decision, dashboard_layout_rules, fallback_rendering_strategy
depends_on: layout-native-chart-slot.md, chart-bar-comparison.md, chart-line-trend.md, contract-visual-token.md
max_use: 当前 renderer 没有原生 combo chart；本文件只给拆分策略和 dashboard 组合规则
-->

# Chart: Combo Dashboard

## 适用判断

- 多指标经营看板、柱线组合、双轴诉求、KPI + 趋势 + 构成混排，使用本分型做拆分设计。
- 当前 native chart slot 只稳定支持 `bar`、`line`、`pie`；不要写 `kind="combo"`、`radar`、`area` 或 `scatter` 期待原生转换。
- 如果用户明确要求双轴柱线组合，默认拆成相邻 `bar` slot + `line` slot，或用一个主图表 + KPI 卡解释次指标。
- 分型判断与标注纪律（KPI 卡先给结论、不同图表共享同一口径、双轴必须在洞察区说明单位）同样适用于离线效果稿的手绘摘要图；“不用原生 combo chart”仅约束运行时可编辑 SVG DrawingML 路线，不约束离线效果稿。

## 页面结构

- 顶部 2 到 4 个 KPI 卡先给当前值、变化率和状态，主体放 1 到 2 个原生图表。
- 经营汇报页优先采用“左侧核心结论 + 中部主图 + 右侧洞察/风险”或“上方 KPI + 下方双图”的结构。
- 不同图表必须共享同一时间范围或业务口径；口径不同则拆成模块化卡片说明。
- 图表数量超过 2 个时，用 dashboard 分区和清晰标题，不把所有数据压进一张大图。

## 渲染策略

- 可编辑优先：把组合拆为多个 native slot，分别用 `kind="bar"`、`kind="line"` 或 `kind="pie"`。
- 视觉摘要优先：若只是表达趋势关系且不需要编辑数据，可用 SVG 画简化 sparkline、状态符号和 KPI 卡，但不要伪造完整坐标轴图表。
- 双轴场景必须在洞察区说明两个指标的单位，避免模型或用户误读同一坐标轴。

## 深色驾驶舱面板变体（离线效果稿）

多指标经营看板走深色“驾驶舱”视觉时的技法要点（纯手法描述，不绑定具体色值，实际取色仍用当前视觉 token）：

- 深色大面板承载整体看板，与浅色卡片式看板的基调区分开。
- 曲线用高亮强调色描边，与深色背景形成强对比，视觉焦点落在趋势本身。
- 关键数据点加发光/光晕效果，强调峰值、拐点或当前值。
- 面板内部网格线弱化、低对比，只做刻度参照，不与主曲线抢视觉权重。

## 金标示例

- 示例路径：`assets/examples/svg-ppt/decks/scenario-chart-type-gold-pages/04-combo-dashboard.svg`
- 需要查看结构时调用：`load_skill_example(path="assets/examples/svg-ppt/decks/scenario-chart-type-gold-pages/04-combo-dashboard.svg")`
- 只参考 KPI + 多 native slot 的装配方式；示例刻意拆成 `bar` 与 `line`，不要写 `kind="combo"`。
- 勿照抄示例首行 `<rect width="1280" height="720">`：它只是离线预览底色。运行时整页背景由 `deck_framework.background` 承载，提交 `render_svg_drawingml_slide` 的 SVG 不画满页背景矩形，否则触发 `SVG_FULL_PAGE_BACKGROUND_FORBIDDEN`（同 `drawingml-svg-authoring-core.md`）。
- 高密度深色场景第二示例：`assets/examples/svg-ppt/decks/scenario-government-briefing-gold-pages/02-dark-cockpit-combo.svg`（`load_skill_example(path="assets/examples/svg-ppt/decks/scenario-government-briefing-gold-pages/02-dark-cockpit-combo.svg")`）
- 参考大数字 KPI 带 + 两个相邻 native chart slot（bar 排名 / line 趋势）+ 管理动作洞察卡的高密度深色装配；组合诉求同样拆成 bar/line，不写 `kind="combo"`。slot 是结构占位（`<g data-native-chart>`；真实标题/洞察/来源写在分组外，组内文字仅为占位、渲染时自动移除），真实数据运行时写入 `charts[]`。

## 反模式

- 不写 `kind="combo"` 或未知 chart kind；未知 kind 会导致错误或降级，产出不可信。
- 不把单位不同的指标混在同一轴上。
- 不让 dashboard 变成小字数据墙；每个图表都要有结论和行动解释。
- 不把 KPI 卡、图例、表格、来源互相遮挡；先减少模块数或拆页。
