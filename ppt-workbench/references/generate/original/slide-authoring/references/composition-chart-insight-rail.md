<!--
id: composition-chart-insight-rail
category: composition-branch
module_type: component_assembly_recipe
read_when: 页面需要左侧主体折线图或柱状图，右侧用 2-3 张卡片解释结论、原因、风险或行动
page_roles: content, summary
stage_tags: slide_generation
supports: data_chart, svg_drawingml, native_chart_slot
outputs: chart_insight_rail_assembly_plan, primary_chart_region, insight_card_regions, chart_story_checks
depends_on: composition-business-report-argument-cascade.md, layout-native-chart-panel.md, layout-insight-text-card.md
relation_specs: requires:composition-business-report-argument-cascade, requires:template-series-composite-builder, requires:layout-native-chart-panel, requires:layout-insight-text-card, pairs_with:chart-line-trend, pairs_with:chart-bar-comparison, conflicts_with:anti-pattern-empty-cards, conflicts_with:anti-pattern-low-density-slogan
triggers: 左侧折线图右侧卡片, 左侧柱状图右侧文字, 左图右文, 左边图表右边说明, 图表加洞察侧栏, 主图加解释卡, chart insight rail, chart with insight cards, chart with annotation rail
max_use: 一页一个主体图表和 2-3 张洞察卡；更多图表或更多解释拆页
-->

# Composition: Chart + Insight Rail

## 证明目标

用于“数据是主要证据，但听众还需要知道结论、原因和行动”的页面。阅读路径固定为：

`action title → 左侧主体图表 → 右侧洞察卡 → 来源/口径`

先写标题判断，再让图表证明，最后让右栏回答“所以什么”。不能先套左右栏，再把任意文字和数字塞进去。

## 输入合同

- `action_claim`：一条可被主图表验证的结论句。
- `chart`：`kind, labels, series, value_format, data_unit, source, period, scope`。
- `insight_cards[2..3]`：每卡 `title, tone, bullets[1..3], metric?, footer?`。
- `evidence_alignment`：每张卡回指哪个系列、类目、峰值、拐点、差值或来源事实。

缺少真实 labels/series 时不要生成图表；可以先补素材或把页面改成“数据缺口 + 待验证假设”。

## Assembly 合同

内容区按 1280x720 坐标表达，具体位置由 assembly 提交，不背固定坐标：

- `primary-chart`：宽度 58%-64%，高度占满主体内容区，使用 `native_chart_panel`。
- `insight-1..N`：宽度 36%-42%，纵向等高或按重要性 45/30/25 分配，使用 `insight_text_card`。
- gutter 20-28px；图表和右栏共享顶线与底线；卡间距 12-16px。
- 两卡优先结论/行动或原因/风险；三卡优先结论/原因/行动。

PageMethod v2 提交示意：

```yaml
assembly:
  regions: [primary-chart, insight-1, insight-2, insight-3]
components:
  - component_id: layout-native-chart-panel
    region_id: primary-chart
    builder_spec: {schema_version: series_composite_svg/v1, pattern: native_chart_panel, data: {...}}
  - component_id: layout-insight-text-card
    region_id: insight-1
    builder_spec: {schema_version: series_composite_svg/v1, pattern: insight_text_card, data: {...}}
```

图表 labels/series 只放在 `native_chart_panel.builder_spec.data.chart`；builder 自动产出 native sidecar。
不要在 proposal 的 `native_data` 中重复同一 slot。

## 图表与洞察规则

- 连续时间走势、拐点和同比环比用 line；类别排名、渠道/区域/产品比较用 bar。
- 图表最多 3 个系列。主系列使用 accent，比较系列使用 contrast，中性基线弱化。
- 右栏不能逐点念数：至少一张卡解释差异或拐点，最后一张优先给行动、风险或决策请求。
- 洞察只能解释可见证据。相关不等于因果；没有材料支持时写“可能因素/待验证”，不能写确定性根因。
- 来源必须包含周期、范围和单位；actual、target、forecast、benchmark 不混写。

## 容量与降级

- 2-8 个类别、1-3 系列最适合；9-12 个类别只保留短标签并降低数据标签密度。
- 右栏每卡 1-3 条短句；只有一个有效洞察时改用底部 insight band，不虚构第二卡。
- 需要两个同等重要图表时拆页，或使用双图 dashboard；不要把两个主图塞进左栏。
- 右栏超过 3 卡或出现长段落时先合并同义项，再拆到后续“原因/行动”页。

## 完成检查

- 标题结论能被主图表直接验证。
- 折线/柱状选择符合数据关系，labels 与每个 series.values 等长。
- 图表为原生 chart slot，不是 SVG 手绘完整坐标轴。
- 右栏卡片分别承担不同解释职责，没有复述、虚构或卡套卡。
- 单位、周期、范围、来源和实际/目标/预测口径可见。
