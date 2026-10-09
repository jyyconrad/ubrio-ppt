<!--
id: layout-chart-insight-card
category: shape-component-library
module_type: data_driven_svg_component
read_when: 内容区需要单独生成一张图表或表格与高亮结论、短解释和洞察组合的证据卡时
page_roles: content, summary
stage_tags: slide_generation
supports: svg_drawingml, native_chart_slot, native_table_slot
outputs: chart_insight_card_spec, grouped_editable_svg, one_native_slot, native_data_sidecar
depends_on: contract-visual-token-core.md, contract-content-density.md, layout-native-chart-slot.md
relation_specs: requires:template-series-composite-builder, requires:layout-native-chart-slot, pairs_with:layout-sectioned-evidence-dashboard, conflicts_with:anti-pattern-empty-cards
triggers: 图表文字组合卡, 图表加文字的指标卡, 单独一张图表卡, 图表加结论卡, 单指标证据卡, 数字趋势洞察卡, 柱图文字卡, 微图表洞察卡, chart insight card, KPI图表卡
max_use: 每次 builder 调用只生成一张卡；一张卡只允许一个证据介质和一个视觉重音
source_notice: 来源为用户提供的 visual-only 截图；只提炼可见的信息层级和组合关系，不推断原始 PPTX 对象类型。
-->

# Layout: 图表文字组合卡（Chart Insight Card）

## 组件边界

当用户说“做一张图表加文字的指标卡”“单独做一张趋势洞察卡”时选择本组件。一次只生成一张内容区
证据卡，不生成分区、大卡容器、页面标题、背景、页眉页脚或其它卡片。1280×720
只是验证画布，实际复用边界是 `region{x,y,w,h}`，输出根组带
`data-component-scope="content-region"`。

## 视觉逻辑

`编号/图标 + 子观点标题 → 唯一高亮值 → 一句意义 → 单一证据介质 → 洞察页脚`

- 高亮值负责第一眼扫描，图表负责证明，洞察负责回答“所以什么”。
- 卡内只保留一个视觉重音：当前值、目标值、风险值或结论词四选一。
- `native_chart` 只容单序列 2–5 点微型柱图/线图；真实图表由 native slot 覆盖。
- `native_table` 只容 2–3 列、2–4 行；更复杂数据改用独立表格组件。
- 没有连续数据时用 `metric` 或 `icon_fact`，不能伪造趋势。

## 输入合同

```yaml
pattern: chart_insight_card
region: {x, y, w, h} # 最小 240×250
data:
  card:
    title: required, 8..14 Chinese chars
    highlight: {prefix, value, suffix}
    meaning: required, one short sentence
    visual:
      kind: native_chart | native_table | metric | icon_fact
      slot_id: stable when native
      chart_kind: bar | line
      labels: 2..5
      series: exactly 1
    insight: required, one evidence interpretation
```

## 失败条件

- 一张卡出现两个主数字、两个图表、图表加长表格或两段同权结论。
- 洞察只是重复数字，或引入卡内没有来源的新事实。
- 目标、预测、标杆被写成已经实现的结果。
- 图表需要图例、多序列、长类目或精确比例，却仍压缩成微图。
- 为塞入正文把字号缩到不可读；此时删除重复说明或放大 `region`。

## 组合方式

外围视觉由一个 `template-series-*` 提供；同页需要多卡时，上层 layout 负责网格、分区、间距和阅读
顺序，重复调用本组件并传入不同 `region`。需要底部根因或行动链时，另行组合
`full_width_rect_step_flow`，不要把流程塞回卡片。
