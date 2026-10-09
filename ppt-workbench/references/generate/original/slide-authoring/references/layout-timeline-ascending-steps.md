<!--
id: layout-timeline-ascending-steps
category: layout
read_when: 按期次(月/季/年)推进且强调"逐期走高"的增长动能叙事，需要每期一个量化巨数
page_roles: content, summary
supports: svg_drawingml
outputs: svg_layout, ascending_steps_layout_rules
depends_on: layout-timeline-horizontal.md, contract-layout-density.md
relation_specs: conflicts_with:layout-timeline-horizontal, conflicts_with:layout-timeline-anchored-columns, conflicts_with:layout-timeline-zigzag-groups, pairs_with:narrative-swiss-copywriting, pairs_with:theme-violet-business, pairs_with:svg-shape-3d-isometric, conflicts_with:layout-arrow-ribbon-metrics
source_notice: 参考公开职场汇报模板的结构组织方式，已抽象为本项目可复制方法；原作固定话术、示例文案、品牌水印一律作为分析输入后丢弃，不入语料。
max_use: 只讲递进阶梯变体；节点式基准时间轴读 layout-timeline-horizontal.md，逐期三槽详情读 layout-timeline-anchored-columns.md
-->

# Layout: Timeline Ascending Steps

## 与基准时间轴的分工

`layout-timeline-horizontal.md` 是通用节点时间轴：节点上下错落，承载事件/交付物/风险，不强调数值大小关系。本颗粒是它的**增长动能变体**：把节点换成沿期次递增高度的阶梯柱，让"高度"直接编码"逐期走高"的量级关系。两者互斥，同一页只选一种。若这页并不强调逐期走高、也没有分组或三槽详情需求，退回基准 `layout-timeline-horizontal.md`，不靠阶梯高度硬造递进。

## 适用判断

- use_when：按期次(月/季)推进、每期一个量化指标，且叙事重点是"持续走高、动能增强"（总结页、复盘页高频）。
- avoid_when：期次间无递进/高低关系（阶梯高度会暗示大小，误导受众）；需要真实数值比例（改 `chart-bar-comparison.md`，本颗粒高度是叙事装置，不是数据刻度）；单期需要多要点详情（改 `layout-timeline-anchored-columns.md`）；不是逐期走高、而是把多个板块/条线成果分段串成方向性陈列带（每段一枚成果巨数、段间无高低递进）改 `layout-arrow-ribbon-metrics.md`。

## 骨架

顶部可选 4 项 KPI 小标行（数值+说明），右侧配一条强调短语。主体 4-6 列按期次从左到右排布，列容器高度递增，呈"平面阶梯上升"观感——**只做平面矩形+渐变，不做 3D 透视/斜切**。每列固定四项，从上到下：巨数百分比、短标题、描述（1-2 行）、底部数值。底部贯穿一个 polygon 大箭头，承载"期次推进+增长方向"语义，期次标签落在箭头分段上。

列越高，字号与行距应同比放大，避免顶部堆内容、底部留大片空白；矮列同理只用最小字号，不强行塞满。

## 容量

4-6 列；每列：巨数 ≤5 字符、短标题 ≤10 字、描述 ≤24 字（≤2 行）、底部数值 ≤8 字符、期次标签 ≤4 字；顶部 KPI 4 项：数值 ≤6 字符、说明 ≤14 字。超 6 列先合并期次或拆两页；描述超行先压缩改写，不缩字号硬塞。

## 渲染降级纪律

阶梯柱只用平面矩形（高度递增）+ `linearGradient` 制造纵深感；渲染器不支持透视/斜切的真 3D 柱效果，写这类效果会转换失败或被拒绝，等距轻立体画法读 `svg-shape-3d-isometric.md`。箭头用单个 `polygon`；如需强调推进方向可选叠加**单个**外发光/投影 `filter`（仅 `feGaussianBlur`，可选 `feOffset`），但不得堆叠多个滤镜或用滤镜伪造立体厚度。

## 金标示例

- 示例路径：`assets/examples/svg-ppt/decks/scenario-report-structure-gold-pages/04-timeline-steps.svg`
- 需要查看结构时调用：`load_skill_example(path="assets/examples/svg-ppt/decks/scenario-report-structure-gold-pages/04-timeline-steps.svg")`
- 只参考阶梯递增、KPI 行、箭头分段和文字随高度缩放的组织方式；不要照抄坐标，不要把示例数据当业务事实。
- 勿照抄示例首行整页背景 `<rect width="1280" height="720">`：它只是离线预览底色，运行时整页背景由 `deck_framework.background` 承载，SVG 内容层不画满页背景矩形，否则触发 `SVG_FULL_PAGE_BACKGROUND_FORBIDDEN`（同 `drawingml-svg-authoring-core.md`）。

## 反模式

- 不用 3D、透视或斜切柱制造立体感。
- 不让阶梯高度脱离真实数量级关系乱排序；必须从左到右单调递增。
- 不让最高列堆满文字、最低列留大片空白（或反之）。
- 不用阶梯高度冒充精确数据比例；需要精确比例改用 bar chart。
