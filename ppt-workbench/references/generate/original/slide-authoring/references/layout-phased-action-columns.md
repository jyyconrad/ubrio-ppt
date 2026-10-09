<!--
id: layout-phased-action-columns
category: layout
module_type: layout_family
read_when: 按期次（月/季/阶段）分三栏，每栏一个期次表头 + 一列落地举措子项清单；非贯穿时间轴、非通用三信息卡
page_roles: content, summary
stage_tags: slide_generation
supports: svg_drawingml
outputs: svg_layout, phased_action_columns_structure
depends_on: contract-layout-density.md, contract-visual-token-core.md
relation_specs: requires:contract-visual-token-core, conflicts_with:layout-three-cards-action-bar, conflicts_with:layout-timeline-anchored-columns, pairs_with:layout-kpi-strip
triggers: 分期举措, 按月份分阶段, 三个阶段工作安排, 分月推进计划, 三栏分期任务, 阶段举措分栏, 一季度二季度三季度举措, 月度分期清单, 落地举措, 子任务清单, phased actions, phase columns, 分阶段举措, 阶段举措, 分阶段推进
max_use: 只讲“按期次分三栏、每栏期次表头 + 落地举措清单”；无期次的三信息组读 layout-three-cards-action-bar.md，有贯穿时间轴读 layout-timeline-anchored-columns.md，顶部纯指标带读 layout-kpi-strip.md
source_notice: 参考公开职场汇报模板的结构组织方式与配色体系，已抽象为本项目可复制方法；原作固定话术、示例文案、品牌水印一律作为分析输入后丢弃，不入语料。
-->

# Layout: Phased Action Columns（分期举措三栏）

## 适用判断

- use_when：按**期次**（月 / 季 / 阶段）分三栏，每栏一个期次表头 + 一列落地举措子项清单（Q1 试点、Q2 铺开、Q3 收口，每栏下列 3–5 条具体任务）。主轴是“分期推进、逐栏落地”。
- avoid_when：
  - 三个通用信息组、无期次语义、靠底部收口 → `layout-three-cards-action-bar.md`；
  - 有一条**贯穿时间轴线**锚定各栏节点 → `layout-timeline-anchored-columns.md`；
  - 顶部一排纯指标带、无举措清单 → `layout-kpi-strip.md`。
- **一句判据**：“三栏是不是各代表一个期次、栏内是逐条落地举措”——是则本颗粒；有贯穿轴线走 anchored-columns，无期次语义走 three-cards。

## 骨架（画法与比例逻辑）

- 顶部 18% 标题（可选内嵌一条 `layout-kpi-strip.md` 摘要复用，横排 3–4 个阶段总量指标）。
- 主体三**等宽栏**，`col_w = (content_w − gap×2) / 3`，栏间距 `gap ≥ 48`；恰 3 栏。
- 栏内自上而下：**期次表头**（房形上升 chevron 题头 motif，accent 深底反白期次名）→ 期次副标（时间段 + 主题）→ 子项清单 3–5 条 → 可选栏底里程碑标。
- 子项：accent 序号 / 圆点 + 一行文字 ≤22 字（≤1 行，超长压短语不折二行）。
- 三栏共用 surface 浅底卡，仅期次表头着 accent 深色。

## 容量

- **恰 3 栏**；期次名 ≤6 字、期次副标 ≤14 字。
- 每栏子项 3–5 条，每条 ≤22 字且 ≤1 行；>5 条先合并再列。
- 顶部 kpi-strip 摘要：≤4 个指标，每个数值 ≤6 字符 + 标签 ≤6 字。

## 配色（三栏同底，禁三栏三色）

- 三栏**同一 surface 浅底**，期次表头用**同一 accent 深色**（仅期次名不同），表“同一条推进主线分三期”；**禁三栏三色**——三色会读成无关并列分类而非分期。
- 子项序号 / 圆点用 accent，正文深色；引 `contract-visual-token-core.md` 保证对比度、浅底不落浅字。

## 内嵌 motif

- **房形上升 chevron 题头**：画法见 `svg-shape-patterns.md` 的房形 chevron 题头片段（矩形顶边中央上凸 6 点 `<polygon>`、标题反白居中），颜色替换为当前 token。

## 金标示例

- `load_skill_example(path="assets/examples/svg-ppt/decks/scenario-composite-structure-gold-pages/02-phased-action-columns.svg")`
- 只参考三栏等宽、房形期次表头、栏内举措清单与顶部 kpi 摘要的组织；不照抄坐标或把占位数据当业务事实，也勿照抄首行整页背景 `<rect>`（离线底色，运行时触发 `SVG_FULL_PAGE_BACKGROUND_FORBIDDEN`）。

## 反模式

- 三栏三色丢失“同一主线分期”；把无期次的三信息组硬塞成分期栏（走 three-cards）；画一条贯穿轴线却又叫分期栏（走 anchored-columns）；子项写成长段落挤爆栏宽。
