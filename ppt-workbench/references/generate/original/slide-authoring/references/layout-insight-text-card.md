<!--
id: layout-insight-text-card
category: shape-component-library
module_type: data_driven_svg_component
read_when: 主图表旁边需要一张只解释结论、原因、风险或行动的文字洞察卡时
page_roles: content, summary
stage_tags: slide_generation
supports: data_chart, svg_drawingml
outputs: insight_text_card_spec, grouped_editable_svg, evidence_backed_text_card
depends_on: contract-visual-token-core.md, contract-content-density.md
relation_specs: requires:template-series-composite-builder, pairs_with:composition-chart-insight-rail, pairs_with:layout-native-chart-panel, conflicts_with:anti-pattern-empty-cards
triggers: 图表右侧文字卡, 右侧洞察卡, 图表说明卡, 趋势解读卡, 原因卡, 风险卡, 行动卡, insight text card, chart annotation card
max_use: 每次 builder 调用只生成一张文字卡；每卡 1 个标题、1-3 条短说明和最多 1 个回指指标
-->

# Layout: Insight Text Card

## 组件边界

本组件只生成一个 region-local 文字洞察卡，用来翻译同页主图表。它不是第二张图表，也不是装饰卡。
卡片中的每个判断都必须能回指主图表、来源材料或明确标注的推导。

## 输入合同

```yaml
pattern: insight_text_card
region: {x, y, w, h} # 最小 240x120
data:
  card:
    title: required, 4..14 Chinese chars
    icon_label: optional, 1..2 chars
    tone: insight | risk | action | neutral
    metric: {value, label} # optional, must repeat a visible chart fact
    bullets: 1..3 short evidence-backed statements
    footer: optional source, period, owner or decision tag
```

## 右栏组织

- 两张卡时优先“结论 / 行动”或“原因 / 风险”；三张卡时优先“结论 / 原因 / 行动”。
- 单卡只回答一个问题：发生了什么、为什么、意味着什么、接下来做什么，四选一。
- `metric.value` 只能回显主图表已存在的峰值、差值、增幅或目标差距，不新增第二套指标。
- `tone` 只改变语义强调色，不用于把同级卡片随机染成多色。

## 失败条件

- 卡片只是复述图表标题或逐点念数字，没有解释拐点、差异、风险或行动。
- 一张卡里同时放原因、风险、方案、Owner 和长段落，形成小字堆叠。
- 使用无法从主图表或来源材料推出的因果结论。
- 为凑三卡虚构第三个观点；只有两个有效洞察时就使用两卡。
