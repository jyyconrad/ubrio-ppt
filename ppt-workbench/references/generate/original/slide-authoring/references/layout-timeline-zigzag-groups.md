<!--
id: layout-timeline-zigzag-groups
category: layout
read_when: 6+ 个带日期事件按季度/阶段分组做高密度回顾，且页侧需要一栏提炼总结
page_roles: content, summary
supports: svg_drawingml
outputs: svg_layout, zigzag_groups_layout_rules
depends_on: layout-timeline-horizontal.md, contract-layout-density.md
relation_specs: conflicts_with:layout-timeline-horizontal, conflicts_with:layout-timeline-ascending-steps, conflicts_with:layout-timeline-anchored-columns, pairs_with:theme-violet-business
source_notice: 参考公开职场汇报模板的结构组织方式，已抽象为本项目可复制方法；原作固定话术、示例文案、品牌水印一律作为分析输入后丢弃，不入语料。
max_use: 只讲分组交错 + 侧栏提炼变体；基准读 layout-timeline-horizontal.md，逐期走高读 layout-timeline-ascending-steps.md，三槽详情读 layout-timeline-anchored-columns.md
-->

# Layout: Timeline Zigzag Groups

## 四方分工

`layout-timeline-horizontal.md` 是基准，节点承载事件/风险。`layout-timeline-ascending-steps.md` 是增长动能变体，阶梯高度编码逐期走高。`layout-timeline-anchored-columns.md` 是三槽详情变体，轴退化为导航条，信息量下沉轴下卡片。本颗粒是**高密度分组回顾 + 侧栏提炼变体**：6 期以上按季度分 2 组、沿中轴“之”字形交错压缩纵向空间，右侧再辟一栏做结论提炼。四者同一页只选一种。若事件不足以分组、也没有递进或三槽详情需求，退回基准 `layout-timeline-horizontal.md`，不为用满版式硬凑分组。

## 适用判断

- use_when：6+ 带日期事件按季度/阶段分组做高密度回顾，且页侧需要提炼总结（年度/半年度复盘高频）。
- avoid_when：事件少于 4 个或无需分组（改基准 `layout-timeline-horizontal.md`）；强调逐期走高（改 `layout-timeline-ascending-steps.md`）；每期需目标/行动/评估三槽（改 `layout-timeline-anchored-columns.md`）；无需侧栏总结（改基准）。

## 骨架

左约 2/3 宽是主时间区，右约 1/3 宽是总结栏。主时间区顶部两条组标题横带（如“第三季度/第四季度”），带下均分 3 个期次标签；带下是水平中轴，6 期沿轴等距排开，每期引一条竖直细线接对应事件卡、方向向上或向下——组内交错规律必须一致，跨组可重新起势。事件卡从上到下：弱化日期区间、粗体标题、1-2 行描述。右栏顶部标题块，下方 3 组，每组粗体组标题 + 2 条箭头 bullet，只做提炼不复述左区事件。上下振幅全卡统一；纵向高度先扣横带与标签开销，剩余部分对半分给上下两侧定卡高与字号，不够时精简描述或减卡，不缩字号；右栏总高与左区相当。

## 容量

6 期分 2 组，组标题 ≤6 字、期次标签 ≤8 字；事件卡 6-7 张，日期 ≤14 字符、标题 ≤12 字、描述 ≤34 字（≤2 行）；右栏 3 组，组标题 ≤14 字，每组 2 条 bullet、每条 ≤34 字。超 7 卡先拆页；描述超行先压缩改写，不缩字号硬塞。

## 渲染降级纪律

横带、事件卡与总结卡均用 `rect`+`line`/`polyline`；zigzag 线用直线段，不用曲线。bullet 箭头用单个 `polygon`，不做多层合成。禁止多滤镜堆叠、`mask` 或 `<g opacity>` 组透明模拟阴影；事件卡如需强调可选叠加单个 `feGaussianBlur`（可选 `feOffset`）做克制投影，层级仍优先靠色块、描边与留白区分。

## 金标示例

- 示例路径：`assets/examples/svg-ppt/decks/scenario-report-structure-gold-pages/08-timeline-zigzag-groups.svg`
- 需要查看结构时调用：`load_skill_example(path="assets/examples/svg-ppt/decks/scenario-report-structure-gold-pages/08-timeline-zigzag-groups.svg")`
- 只参考分组横带、之字形交错和右栏提炼的组织方式；不要照抄坐标或示例数据。
- 勿照抄示例首行整页背景 `<rect width="1280" height="720">`：它只是离线预览底色，运行时整页背景由 `deck_framework.background` 承载，SVG 内容层不画满页背景矩形，否则触发 `SVG_FULL_PAGE_BACKGROUND_FORBIDDEN`（同 `drawingml-svg-authoring-core.md`）。

## 反模式

- 不让同组内交错规律忽上忽下，组内必须统一。
- 不让连接线穿过组标题横带或相邻卡片。
- 不为填满而让 bullet 超过 2 行或塞进第 4 组。
- 不用箭头以外的图形（emoji、图片）做 bullet 前缀。
- 无分组必要时不画两条组标题带，退回基准时间轴。
