<!--
id: chart-line-trend
category: layout
read_when: 当前页需要折线/趋势/走势/时间序列/同比环比变化
page_roles: content, summary
chart_types: line
visual_tags: chart
supports: svg_drawingml, native_chart_slot
outputs: chart_type_decision, native_chart_slots, line_chart_layout_rules
depends_on: layout-native-chart-slot.md, contract-visual-token.md
max_use: 只讲 line/trend 分型；slot JSON 合同仍以 layout-native-chart-slot.md 为准
-->

# Chart: Line Trend

## 适用判断

- 连续时间序列、月度/季度/年度走势、增长曲线、健康度变化，优先用 `kind="line"` 原生 chart slot。
- 只有 2 个时间点时不要用折线制造趋势感；改为柱状对比或前后对比卡。
- 类别排名或非连续分类对比，用 `chart-bar-comparison.md`。
- 分型判断与标注纪律（2 个时间点不画趋势线、2-3 条线上限、只标峰值/拐点/末值）同样适用于离线效果稿的手绘摘要图；“禁止手绘坐标轴”仅约束运行时可编辑 SVG DrawingML 路线，不约束离线效果稿。

## 页面结构

- 先写趋势结论：上升、下降、拐点、波动、阶段性平台或异常点。
- 图表区保留足够横向宽度，避免时间标签重叠；右侧保留关键拐点解释或行动建议。
- 2 到 3 条线是上限；更多系列先筛选重点或拆成小倍数图。
- 有历史 + 预测时，用标注线或注释区说明 forecast 起点，不用虚构不确定数据口径。

## Native Slot 写法

- JSON 使用 `kind: "line"`；`kind: "trend"` 也会按 line 处理，但推荐直接写 line，避免语义不清。
- `labels` 必须是连续时间粒度；series 的 values 数量与 labels 完全一致。
- 颜色使用主强调 + 对比强调 + 中性弱线；轴、网格和图例文字必须使用高对比 token。
- 折线图必须配 `insight` 或页面洞察文本，说明变化原因或决策含义。

## 金标示例

- 示例路径：`assets/examples/svg-ppt/decks/scenario-chart-type-gold-pages/02-line-trend.svg`
- 需要查看结构时调用：`load_skill_example(path="assets/examples/svg-ppt/decks/scenario-chart-type-gold-pages/02-line-trend.svg")`
- 只参考趋势结论、拐点解释、native slot 占位和来源组织；不要照抄坐标，也不要把示例里的数据当成业务事实。
- 勿照抄示例首行 `<rect width="1280" height="720">`：它只是离线预览底色。运行时整页背景由 `deck_framework.background` 承载，提交 `render_svg_drawingml_slide` 的 SVG 不画满页背景矩形，否则触发 `SVG_FULL_PAGE_BACKGROUND_FORBIDDEN`（同 `drawingml-svg-authoring-core.md`）。

## 反模式

- 不用折线连接无序分类。
- 不用过多数据标签铺满每个点；只标最后值、峰值、谷值或拐点。
- 不用面积填充遮挡多线对比；若需要面积图，先确认 renderer 支持，否则用纯 SVG 摘要图或拆页。
- 不让预测线和历史线口径混在一起不说明。
