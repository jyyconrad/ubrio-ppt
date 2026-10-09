<!--
id: template-series-blue-summary-pyramid
category: template-series
read_when: 需要复用 ppt1 的蓝白递进经营总结系列，用回顾、成果、展望、阶梯和金字塔组织半年或年度复盘时
page_roles: content, summary
supports: svg_drawingml
outputs: series_visual_contract, page_archetype_menu, shape_composition_grammar, composite_resource_plan
depends_on: template-series-composite-builder.md, layout-retrospect-outlook-pyramid.md
relation_specs: requires:template-series-composite-builder, pairs_with:composition-case-impact-chain, pairs_with:composition-operating-model-blueprint, pairs_with:layout-timeline-ascending-steps, pairs_with:layout-hero-metric-left-rail
max_use: 一页只保留一个上升或层级主视觉；真实经营图表走 native chart
source_notice: 来源为 ppt1.jpg visual-only 营销拼页；品牌、数字、Logo 和精确色值不进入通用规则。
-->

# ppt1 系列：蓝白递进经营总结

## 系列视觉逻辑

- 蓝白浅底，深蓝压住标题、方向箭头和 hero 数，浅蓝承载次级证据。
- 全册反复使用“向上、向前、递进”：阶梯、金字塔、成长轨迹、流程箭头和闭环。
- 一个页面只有一个主视觉关系；hero 数、金字塔和阶梯不能同时抢第一层。
- deck 节奏以 `回顾 → 成果 → 计划` 为主，也可在中段插入数据证明和 SWOT 诊断。

## 页面展示系统

- 回顾—成果—展望三栏，中栏用三层金字塔和一个 hero 指标建立视觉中心。
- 4-6 期突破阶梯，每期一个指标、一句动作、一句意义。
- 左侧 hero 成绩 rail + 右侧三主题计划矩阵。
- 双环运营模式、价值链、成长轨迹和 native chart dashboard 作为受控变体。
- 页面顶部保持轻标题区，底部使用方向条或结论带收口。

## 形状组合语法

- `three-period frame + central pyramid + bottom conclusion band`。
- `ascending steps + circular period badges + long direction arrow`。
- `hero rail + plan matrix + metric support cards`。
- `dual loop + outer satellites` 只用于真的反馈闭环，不把并列能力强画成环。
- 阶梯高度只有在数据单调且可比较时表达增长；否则改普通时间线。

## 快速组合示例

“左边回顾上半年，中间突出三层成果和总业绩，右边写下半年计划”时，选择
`retrospect_outlook_pyramid`，填写恰三项 `periods`、三层 `pyramid_layers` 和一句 `conclusion`。
选择 `build-series-composite-svg` 物化资源，独立预检可选
`validate-series-composite-svg-spec`；后续只替换 data，具体执行入口由当前 consumer 决定。

## 容量与失败

- 三时段必须恰为 3；金字塔恰 3 层；每侧 2-3 条事实；hero 指标只保留 1 个。
- 阶段或月份 4-6 个；超过 6 个改常规时间线或图表。
- 失败：数据不单调却用阶梯制造增长、金字塔层文字超过短标签、同页叠加两个主关系。
