<!--
id: chart-pie-composition
category: layout
read_when: 当前页需要饼图/环形图/份额/占比/结构构成
page_roles: content, summary
chart_types: pie
visual_tags: chart
supports: svg_drawingml, native_chart_slot
outputs: chart_type_decision, native_chart_slots, pie_chart_layout_rules
depends_on: layout-native-chart-slot.md, contract-visual-token.md
max_use: 只讲 pie/composition 分型；slot JSON 合同仍以 layout-native-chart-slot.md 为准
-->

# Chart: Pie Composition

## 适用判断

- 份额拆分、渠道构成、成本结构、用户结构等“部分之和等于整体”的数据，才使用 `kind="pie"`。
- 类别超过 5 个时优先合并长尾为“其他”，或改为条形图；饼图不适合承载排名细节。
- 需要比较两个时间点的结构变化时，优先用两个小饼/环形并列，或改为堆叠条形的可读替代方案。

## 页面结构

- 饼图只占一个明确图表区；旁边必须放最大项、变化项、风险项或行动解释。
- 图例放在右侧或下方，不压在饼图内部。
- 扇区标签只保留类别 + 百分比；长解释转移到洞察区。
- 来源必须说明统计口径和整体基数。

## Native Slot 写法

- JSON 使用 `kind: "pie"`，通常只写一个 series。
- `labels` 和 `values` 数量一致；values 应表达同一口径的份额或数值，不混百分比和金额。
- 颜色最多 5 个，主强调只给最重要扇区；其他项使用中性或低饱和色。
- 深色主题下，legend 和 data label 使用浅色高对比 token。

## 金标示例

- 示例路径：`assets/examples/svg-ppt/decks/scenario-chart-type-gold-pages/03-pie-composition.svg`
- 需要查看结构时调用：`load_skill_example(path="assets/examples/svg-ppt/decks/scenario-chart-type-gold-pages/03-pie-composition.svg")`
- 只参考构成结论、最大项/行动解释、native slot 占位和来源组织；不要照抄坐标，也不要把示例里的数据当成业务事实。
- 勿照抄示例首行 `<rect width="1280" height="720">`：它只是离线预览底色。运行时整页背景由 `deck_framework.background` 承载，提交 `render_svg_drawingml_slide` 的 SVG 不画满页背景矩形，否则触发 `SVG_FULL_PAGE_BACKGROUND_FORBIDDEN`（同 `drawingml-svg-authoring-core.md`）。

## 反模式

- 不用 3D 饼图、爆炸饼、过多阴影或装饰环。
- 不用饼图比较 8 个以上类别的微小差异。
- 不把非整体构成的数据强行画成饼图。
- 不把标签都塞进扇区导致重叠；可把详细说明移到洞察区。
