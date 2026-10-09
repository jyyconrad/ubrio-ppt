<!--
id: layout-sectioned-evidence-dashboard
category: composition-system
module_type: component_assembly_recipe
read_when: 用户明确要求两个大分区、3-6 个重复子区域和一个底部收口带，需要规划多个 region 的页面内容区编排时
page_roles: content, summary
stage_tags: slide_generation
supports: svg_drawingml, native_chart_slot, native_table_slot
outputs: sectioned_evidence_dashboard_assembly_plan, chart_insight_card_regions, rect_step_flow_region
depends_on: contract-visual-token-core.md, contract-content-density.md, layout-chart-insight-card.md, layout-full-width-rect-step-flow.md
relation_specs: requires:template-series-composite-builder, requires:layout-chart-insight-card, requires:layout-full-width-rect-step-flow, pairs_with:composition-metric-system-with-case, pairs_with:theme-light-business-blue, conflicts_with:anti-pattern-empty-cards
triggers: 大卡套多张小卡, 两个分区六张指标卡, 两个分区放六张图表洞察卡底部加一条根因整改流程, 分区式证据仪表板, 多指标体系总览, 六张小图, 多卡加底部流程, sectioned evidence dashboard, nested evidence cards
max_use: 一页 1-2 个大分区，每区 2-3 张证据卡；总卡数 3-6，超过后拆页或改为单一主图表
source_notice: 来源为用户提供的单张 visual-only 截图；只证明可见层级、构图和组件关系，不能证明 PPTX 原生对象、分组、母版或可编辑性。
-->

# Assembly: Sectioned Evidence Dashboard

## 角色与边界

本 reference 只在用户明确要求“多个分区 + 多个重复子区域 + 底部收口”时使用；只要一张卡或一条流程时
禁止选择。它是页面级编排方法，不是一个不可拆分的 SVG 组件，只决定外围 section frame、子区域、
收口区域和阅读顺序；具体图表文字卡由 `chart_insight_card` 逐张生成，横向根因/行动链由
`full_width_rect_step_flow` 单独生成。页面背景、action title、页眉页脚仍由 `template-series-*` 与框架层负责。

## 核心视觉逻辑

这不是“卡片越多越高级”，而是三级信息压缩：

1. action title 给出全页唯一管理判断；
2. 1-2 个大分区回答判断由哪些维度构成；
3. 每张证据小卡只证明一个子观点，并用一个主要证据介质完成佐证。

大分区应是轻量 section frame 或浅色 surface，不再堆第二层厚阴影。小卡使用白色或浅色面、细描边和统一内边距；强调色只落在编号、关键数字、图表重点系列和洞察图标。

## 组件编排骨架

`template series chrome → action title → section frame[1..2] → chart_insight_card[2..3] → optional full_width_rect_step_flow`

- 大分区标题使用 `icon badge + section label + 延伸细线`，先建立扫描分组。
- 同一分区的小卡共享宽度、标题基线、证据区高度和洞察条位置。
- 两个分区通常左右并置；只有一个分区时可放 3-4 张更宽的小卡。
- 下方收口区只承担一种任务：根因拆解、行动链、风险闭环或决策请求，不能再开第二套指标故事。

## 图表洞察卡 Anatomy

每张小卡按固定顺序组合，但不是把所有元素都塞进去：

| 层 | 必填 | 作用与容量 |
|---|---|---|
| card header | 编号/图标 + 子观点标题 | 标题 8-14 字，只命名一个指标或判断 |
| highlight line | 高亮数字、阈值、before→after 或一句结果 | 一个 hero 值；前后值必须同单位、同周期、同范围 |
| meaning line | 一句解释 | 12-22 字，说明业务意义，不复述标题 |
| evidence well | `native_chart` / `native_table` / `metric` / `icon_fact` 四选一 | 证据介质只能有一个主角；不能同时塞图表、表格和长文 |
| insight footer | 图标 + 洞察短句 | 12-20 字，只翻译本卡证据，不引入新事实 |

视觉占比建议：header 12%-16%，highlight/meaning 20%-24%，evidence well 42%-52%，insight footer 14%-18%。卡内正文通常不超过 45 个中文字符。

## 图表与表格边界

- `native_chart`：仅用于单序列 3-5 点的微型柱/线图；隐藏图例和 Office 标题，标签保持短词。SVG slot 写 `data-native-chart-variant="micro"`，真实数据写入 `native-data.json`。
- 普通多序列、长类目、复杂坐标轴或需要图例的图表，不得缩进小卡；改成一张主图表 + 周边 2-3 张洞察卡。
- `native_table`：最多 3 列、4 行，只做小型对比或状态账单；更大表格独立成页。
- SVG slot 内可有 `data-preview-only="true"` 的预览层供截图和人工检查；DrawingML 转换前必须确定性移除，由原生 chart/table 覆盖。
- `metric` 用于单值、前后差和阈值；`icon_fact` 用于没有连续数据但有事实分类的卡片。

## 观点突出规则

- 页标题比所有小卡标题高一级；分区标题只做导航，不与页标题竞争。
- 小卡只允许一个视觉重音：hero 数字、目标值、风险值或结论词四选一。
- 同分区使用同一 accent；不同分区也优先用图标和标题区分，不逐卡换色。
- 图表最后一个点、目标线或异常点可用强调色，其余系列使用低饱和主题色。
- 洞察条使用浅背景形成稳定出口，文本必须是“所以什么”，不能写成第二段正文。

## 编排输入合同

```yaml
template_series: exactly 1
sections: 1..2
section:
  title: required
  icon_label: optional, 1..2 chars
  card_regions: 2..3
  card_specs: chart_insight_card[2..3]
closure_region: optional
closure_spec: full_width_rect_step_flow when closure_region exists
```

## 容量与失败

- 一页总卡数 3-6；每区 2-3 卡。六卡已经是上限，且只能使用短标题、一个高亮结论和一个证据介质。
- 连续六张小卡都只有文字，说明证据不足；连续六张小图都需要复杂图例，说明应改主图表页面。
- 失败：标题是主题词、卡内有两个主数字、洞察引入新数据、为了填满而虚构指标、目标冒充实绩、颜色逐卡随机变化、外层与内层同时使用厚阴影。
- 文字或图表超过容量时，优先保留 `观点 → 证据 → 洞察`，删除重复解释；仍超量则拆成指标体系页与偏差闭环页。

## 快速组合

输入：“效率和质量各三个指标，每个指标给趋势和一句洞察，底部再解释项目延期的五层根因与整改动作。”

组合：`template-series-rd-efficiency-blue → composition-metric-system-with-case → sectioned evidence assembly → chart_insight_card × 6 → full_width_rect_step_flow × 1`。每个组件独立生成并落入上层分配的 `region`；若图表不满足微图条件，改为一张主图 + 三张洞察卡。
