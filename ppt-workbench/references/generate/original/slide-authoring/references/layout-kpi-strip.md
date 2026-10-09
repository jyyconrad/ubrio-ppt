<!--
id: layout-kpi-strip
category: layout
module_type: layout_family
read_when: 一行横向陈列 3-6 个核心 KPI 指标（开篇摘要 / 结尾收束 / 成果陈列）
page_roles: content, summary
stage_tags: slide_generation
supports: svg_drawingml, validate_svg_drawingml, render_svg_drawingml_slide
outputs: svg_layout, kpi_strip_structures
depends_on: contract-visual-token-core.md, layout-swiss-metric-structures.md
relation_specs: requires:contract-visual-token-core, pairs_with:theme-violet-business, pairs_with:layout-swiss-metric-structures, conflicts_with:chart-bar-comparison, requires:contract-gold-svg-builder, requires:structure-hierarchy
triggers: 水平指标带, 横向KPI, 一排大数字, KPI摘要, 成果陈列, 折角卡, 切角卡, kpi strip, dog-ear card
max_use: 只讲水平多联指标带；纵向账单改 metric-structures，真实高度对比改 bar-comparison
source_notice: 参考公开职场汇报模板的结构组织方式与配色体系，已抽象为本项目可复制方法；原作固定话术、示例文案、品牌水印一律作为分析输入后丢弃，不入语料。
-->

# Layout: KPI Strip（水平多联指标带）

## 适用判断

- use_when：一行并排陈列 3-6 个核心 KPI，用于开篇 KPI 摘要、结尾指标收束或独立成果陈列页。
- avoid_when：指标间需真实高度/比例对比（改 chart-bar-comparison）；指标少于 3 个（用普通指标卡或左判断右证据）；每项都要长说明（改 layout-swiss-metric-structures 纵向承载）。

## 骨架

一行 3-6 个并列块，每块 = 巨数（或百分比）+ 标签；块可为折角卡（dog-ear）或切角平行四边形。三种用法：

- 页顶 KPI 摘要：指标带放标题下方，可附一段总结段承上启下。
- 页尾指标收束：指标带放主体下方，可附一条收束横幅收口。
- 独立陈列页：房形题头（标题+副标，画法见 svg-shape-patterns 房形 chevron 题头片段）+ 分段 ribbon + 底部结论条，指标带占主体。

## 折角 / 切角画法（写逻辑不写死坐标）

- 折角卡：卡体用 polygon，右上角按折边 f 切掉——顶边到 (right−f, top)，斜切到 (right, top+f)，再经右下、左下、左上闭合；折出的小三角另叠一枚作折角阴影。切角卡则四顶点按水平偏移错位、上下边平行。
- 折边 f 取卡宽 12%-16%；卡宽 =（内容宽 − 联间距×(联数−1)）÷ 联数，联间距取卡宽 10%-12%。

## 容量约束

- 3-6 联；超 6 联改纵向 KPI 账单（kpi_ledger）或拆页。
- 每联巨数 ≤6 字符（含单位；纯百分比 ≤4 字符）+ 标签 ≤10 字（1 行）。
- 页顶总结段 ≤55 字；页尾收束横幅 ≤24 字；独立页题头标题 ≤10 字 + 副标 ≤16 字；结论条 ≤30 字。

## 维度纯纪律

- 不内联 hex：渐变块写“accent 浅→深渐变卡”，浅底块写“surface_alt 浅底卡”，收口写“accent_strong 深色条”，由 pairs_with 的 theme（theme-violet-business / theme-blue-green-duotone）给色值。
- 折角/切角只写顶点逻辑与比例，像素由安全区与联数计算。

## 与相邻结构分工

- vs kpi_ledger（纵向账单）：逐行、每行可带说明（4-6 项带注解）；本颗粒横向一行、极简巨数+短标签，一屏速览。
- vs argument_metric_columns（三列带论点）：每列有论点标题+描述+巨数的论证结构；本颗粒不承载论点、只陈列指标。

## 金标示例

- 示例路径与调用：`load_skill_example(path="assets/examples/svg-ppt/decks/scenario-report-structure-gold-pages/01-kpi-strip.svg")`
- 只参考房形题头、分段 ribbon、5 联折角渐变卡与深紫结论条的信息层级与折角画法；不要照抄坐标与占位数据。
- 勿照抄示例首行 `<rect width="1280" height="720">`：它只是离线预览底色。运行时整页背景由 `deck_framework.background` 承载，提交 `render_svg_drawingml_slide` 的 SVG 不画满页背景矩形，否则触发 `SVG_FULL_PAGE_BACKGROUND_FORBIDDEN`（同 `drawingml-svg-authoring-core.md`）。
