<!--
id: layout-native-chart-panel
category: shape-component-library
module_type: data_driven_svg_component
read_when: 页面需要一张占主体区域的可编辑折线图或柱状图，并在另一侧放独立洞察卡时
page_roles: content, summary
stage_tags: slide_generation
supports: data_chart, svg_drawingml, native_chart_slot
outputs: native_chart_panel_spec, grouped_editable_svg, one_primary_native_chart_slot, native_data_sidecar
depends_on: contract-visual-token-core.md, contract-content-density.md, layout-native-chart-slot.md
relation_specs: requires:template-series-composite-builder, requires:layout-native-chart-slot, pairs_with:composition-chart-insight-rail, pairs_with:layout-insight-text-card, pairs_with:chart-line-trend, pairs_with:chart-bar-comparison, conflicts_with:anti-pattern-empty-cards
triggers: 左侧折线图, 左侧柱状图, 左边主图表, 大折线图右侧说明, 大柱状图右侧洞察, 主图表, 图表主体区, native chart panel, primary chart panel
max_use: 每次 builder 调用只生成一个主体图表区；仅支持 bar 或 line、2-12 个类目、1-3 个系列
-->

# Layout: Native Chart Panel

## 组件边界

本组件只生成调用方 `region` 内的一张主体原生图表面板：图表小标题、一个 native chart slot、来源和单位。
它不生成页面 action title、右侧洞察卡、整页背景、页眉页脚或其它图表。右侧说明使用
`layout-insight-text-card.md`，整页左右编排使用 `composition-chart-insight-rail.md`。

## 输入合同

```yaml
pattern: native_chart_panel
region: {x, y, w, h} # 最小 520x320，推荐占内容区宽度 58%-64%
data:
  chart:
    slot_id: required, stable
    title: required, 8..20 Chinese chars
    kind: bar | line
    labels: 2..12
    series:
      - name: required
        values: same length as labels
        color: optional theme token override
    value_format: "0" | "0%" | other supported Office format
    data_unit: optional but required when unit is not obvious
    source: required, include period and scope
    insight: optional machine-readable interpretation
```

图表数据只写一次：写入 `builder_spec.data.chart`，builder 会确定性生成 `native-data.json`。不要再在
`execute_page.proposal.native_data` 中重复同一 `slot_id`，否则会形成重复 overlay。

## 图表选择

- 连续时间序列、走势、拐点、同比或环比变化用 `line`；至少 3 个时间点，最多 3 条线。
- 类别、渠道、区域、产品或阶段的离散比较与排名用 `bar`；超过 8 个类目优先横向条形语义或 Top N。
- 只有两个时间点时优先柱状或 before/after，不用折线制造趋势。
- 多系列只保留真正需要比较的 2-3 条；其它系列拆页或放表格，不把图例压成小字。

## 页面占比与可见性

- 主图表区占页面内容区宽度 58%-64%，右侧洞察区占 36%-42%，中间 gutter 20-28px。
- 图表 slot 不小于 520x320；标题和来源在 slot 外，避免被原生图表覆盖。
- 轴标签、图例、网格线使用主题中的高对比 token；只强调关键系列或关键类目。
- 单位、周期、范围和来源必须可见；目标、预测、标杆和实际结果必须明确区分。

## 失败条件

- 没有真实数据却生成折线或柱状图，或用装饰性 SVG 假装完整坐标轴图表。
- labels 与任一 series.values 数量不一致，系列超过 3 条，或类目超过 12 个仍不拆分。
- 图表标题只写“数据分析”“趋势图”，没有先给业务判断。
- 来源、周期、单位缺失，或右侧洞察引入图表和素材中不存在的新事实。
- 把大图表压进 `chart_insight_card` 微图卡，导致坐标轴、图例和标签不可读。
