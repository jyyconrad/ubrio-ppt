<!--
id: layout-swiss-metric-structures
category: layout
module_type: layout_family
read_when: Swiss 页面是指标时间轴、三列指标论点、KPI 账单或收束要点
page_roles: content, summary
stage: slide_generation
supports: svg_drawingml, validate_svg_drawingml, render_svg_drawingml_slide
outputs: swiss_metric_structures, svg_layout
depends_on: layout-swiss-core-grid.md, contract-visual-token-core.md
relation_specs: requires:layout-swiss-core-grid, pairs_with:contract-visual-token-core, conflicts_with:chart-bar-comparison
max_use: 只讲纯 SVG 指标结构；需要真实柱线饼高度/趋势语义时改读图表分型颗粒
-->

# Swiss Metric Structures

这些结构用于业务汇报中的数字证据，但不画真实图表。若需要条形/柱状高度、折线趋势或占比构成，改走 `chart-bar-comparison.md`、`chart-line-trend.md` 或 `chart-pie-composition.md`。

## vertical_metric_timeline

适用随时间、期次或版本推进且每个节点带量化数据的演化。2-5 个节点；每节点 = 年份/期次 + 巨数/倍数 + 短标题 + 描述。左侧窄轴列，右侧信息块等距分布。容量：年份/期次 ≤12 字符、量化值 ≤10 字符、标题 ≤18 字符、描述 ≤44 字符。节点超过 5 个先合并相邻期次或拆两页；描述超长压两行以内，不缩字号硬塞；没有真实数据时降级为横向流程线。

## argument_metric_columns

适用三条并列论点，每条配一个量化支撑数字并呈方向性递进。主体区三等分，列底巨数统一基准线；末列可用唯一强调色。恰好 3 列，数字必须真实。容量：kicker ≤16 字符、论点标题 ≤20 字符（一行）、描述 ≤60 字符（≤2 行）、巨数 ≤10 字符。超载时先砍最弱论据或换四卡；描述超两行先改写压缩，绝不为凑格式编造数字。

## kpi_ledger

适用 4-6 项核心指标账单式纵向排布。每行 = 巨数 + 标签 + 可选说明，行高均分，分隔线统一。容量：数值 ≤10 字符、标签 ≤22 字符、可选说明 ≤30 字符。超过 6 行拆页或改六格；数值必须真实，不为概念解释编造。需要条形高度比较时不要用本结构，改读柱状图分型。

## closing_takeaways

适用整套 deck 收尾：一句收束宣言 + 三条可带走结论。左区放大宣言，右区 3 条 takeaway 等高排列；每套 deck 仅 1 页收束。容量：宣言 ≤60 字符；恰好 3 条 takeaway，每条标题 ≤18 字符、说明 ≤44 字符。takeaway 超 3 条先合并或改摘要矩阵；宣言超长先改写为一句判断。

## 冲突消解

本颗粒与 `chart-bar-comparison` 同时出现时，先判断用户要的是“真实柱状/条形比较”还是“纯数字账单/论点巨数”。真实图表优先 chart 分型；纯数字或论点递进优先本颗粒。
