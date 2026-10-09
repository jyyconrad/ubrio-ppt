<!--
id: chart-bar-comparison
category: layout
read_when: 当前页需要柱状/条形/排名/类别对比或分组对比图表
page_roles: content, summary
chart_types: bar
visual_tags: chart
supports: svg_drawingml, native_chart_slot
outputs: chart_type_decision, native_chart_slots, bar_chart_layout_rules
depends_on: layout-native-chart-slot.md, contract-visual-token.md
triggers: 柱状, 柱状图, 条形, bar, column, 排名, 类别对比, 分组对比, 渠道对比, 阶段对比, 趋势对比, 渠道转化排名, 转化排名
max_use: 只讲 bar/column 对比图分型；slot JSON 合同仍以 layout-native-chart-slot.md 为准
-->

# Chart: Bar Comparison

## 适用判断

- 类别之间比较、排名、分组对比、阶段对比、区域/渠道/产品线指标对比，优先用 `kind="bar"` 原生 chart slot。
- “渠道转化排名”“各渠道转化率对比”“阶段指标排名”这类虽然含有“转化”，但语义是**类别/渠道之间的排名对比**，优先 bar/column；只有描述同一用户流或线索池从上到下逐层流失，才改读 `layout-funnel-stage-stack.md`。
- 时间趋势如果强调连续走势，用 `chart-line-trend.md`；只有强调不同年份/阶段的离散对比时才用柱状。
- 指标少于 3 个且更适合 KPI 卡片时，不强行上图表；用 metric cards 承载。
- 分型判断与标注纪律（分类超过 8 个改横向条形、超过 12 个压缩为 Top N + 其他、颜色只突出重点系列）同样适用于离线效果稿的手绘摘要图；“禁止手绘坐标轴、柱子、图例和数据标签”仅约束运行时可编辑 SVG DrawingML 路线，不约束离线效果稿。

## 页面结构

- 标题区给出结论，不写“数据对比”这类空标题。
- 主图表区占主体宽度 45% 到 70%；右侧或下方保留 2 到 4 条洞察、异常、行动。
- 分类超过 8 个时优先横向条形图语义，减少横轴标签拥挤；分类超过 12 个时压缩为 Top N + 其他。
- 分组柱只用于同一分类下 2 到 3 个系列；系列更多时改为小倍数图、表格或拆页。

## Native Slot 写法

- SVG 只声明 slot、标题、洞察和来源；真实数据写入 `native-data.json`。
- JSON 使用 `kind: "bar"`。本文件只讲 bar/column 类别对比，不要写 `stacked_bar` 或其他未支持类型冒充 bar。
- **瀑布/桑基现已有原生实现，不要再用 bar 冒充**：单指标期初→期末的归因拆解改用 `kind: "waterfall"`（见 `chart-waterfall.md`，落原生浮动柱）；多节点加权流向改用 `data-role="native-sankey-slot"` 的桑基槽（见 `chart-sankey.md`，落确定性几何缎带）。只有真·类别排名对比才留在本文件的 bar。
- 每个 series 明确 `name`、`values`、`color`；颜色来自当前视觉 token，正文、轴、图例使用高对比中性色。
- 需要百分比时在 `options.value_axis.format` 写 `0%`；需要单位时同时写 `data_unit` 或标题/来源说明。

## 金标示例

- 示例路径：`assets/examples/svg-ppt/decks/scenario-chart-type-gold-pages/01-bar-comparison.svg`
- 需要查看结构时调用：`load_skill_example(path="assets/examples/svg-ppt/decks/scenario-chart-type-gold-pages/01-bar-comparison.svg")`
- 只参考信息层级、native slot 占位、标题/洞察/来源组织；不要照抄坐标，也不要把示例里的数据当成业务事实。
- 勿照抄示例首行 `<rect width="1280" height="720">`：它只是离线预览底色。运行时整页背景由 `deck_framework.background` 承载，提交 `render_svg_drawingml_slide` 的 SVG 不画满页背景矩形，否则触发 `SVG_FULL_PAGE_BACKGROUND_FORBIDDEN`（同 `drawingml-svg-authoring-core.md`）。

## 反模式

- 不用 SVG 手绘坐标轴、柱子、图例和数据标签。
- 不把所有柱子染成同一个深色；主强调只突出 1 到 2 个重点系列或重点分类。
- 不让长分类名横轴硬挤；先改条形、缩短标签或放到表格。
- 不用 3D 柱、阴影柱或渐变柱制造视觉噪音。
