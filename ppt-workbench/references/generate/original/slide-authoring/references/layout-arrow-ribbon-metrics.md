<!--
id: layout-arrow-ribbon-metrics
category: layout
module_type: layout_family
read_when: 把多段板块/条线成果串成一条方向性陈列带，每段自带一枚成果巨数指标卡（非时间递进、非纯并列 KPI）
page_roles: content, summary
stage_tags: slide_generation
supports: svg_drawingml
outputs: svg_layout, arrow_ribbon_metrics_structure
depends_on: contract-layout-density.md, contract-visual-token-core.md
relation_specs: requires:contract-visual-token-core, conflicts_with:layout-timeline-ascending-steps, conflicts_with:layout-process-flow, pairs_with:layout-kpi-strip
triggers: 成果陈列, 逐项成果, 工作成效展示, 分段成果, 成果箭头带, 箭头串联成果, 板块成果陈列, 分段指标带, 陈列带, 箭头串成, achievement ribbon, arrow ribbon metrics, 成果带, 一条带子, 箭头陈列
max_use: 只讲“多段成果被箭头串成一条方向陈列带、每段自带成果巨数”；逐期时间递进读 layout-timeline-ascending-steps.md，机制闭环读 layout-process-flow.md，纯一排并列巨数读 layout-kpi-strip.md
source_notice: 参考公开职场汇报模板的结构组织方式与配色体系，已抽象为本项目可复制方法；原作固定话术、示例文案、品牌水印一律作为分析输入后丢弃，不入语料。
-->

# Layout: Arrow Ribbon Metrics（方向性成果陈列带）

## 适用判断

- use_when：把多段**板块 / 条线的工作成果**串成一条从左到右的方向性陈列带，每段自带一枚**成果巨数指标卡**（客户增长 1240 家、交付提效 22 天、成本优化 -1870 万…）。段与段是并列成果，但被箭头串出“逐项展开、方向推进”的陈列感。
- avoid_when：
  - 逐月 / 逐季**时间递进**、越走动能越强 → `layout-timeline-ascending-steps.md`；
  - 机制落地 / 责任闭环 / 端到端流转的**因果链路** → `layout-process-flow.md`；
  - 一排纯并列巨数、无分段箭头方向 → `layout-kpi-strip.md`。
- **一句判据**：“每段是不是一块独立成果、彼此并列又被箭头串成一条方向带”——是则本颗粒；有时间 / 因果先后则走 timeline / process-flow，无方向串联则走 kpi-strip。

## 骨架（画法与比例逻辑）

- 三段式竖分：顶部 15–20% 观点标题 + 成果总纲；主体 55–62% 横向箭头带；底部 12–16% 可选结论条。
- 箭头带 N=3–6 段（推荐 4–5），横向等宽等距，`seg_w = (band_w − gap×(N−1)) / N`，`gap ≈ 16–24`。
- 每段 = **chevron 箭头头**（accent 深底、反白段名）+ 下接**成果指标卡**（surface 白底、切角矩形）。chevron 右端凸尖伸入段间隙、次段左端内凹，相邻段视觉相扣＝方向串联。
- 指标卡槽位（自上而下）：条线名 → 成果巨数 ≤6 字符（title_text / accent_strong）＋增幅徽标（巨数下方小上升 / 下降三角＋幅度）→ 一句说明 ≤20 字 → 口径胶囊。
- 图标走 `search_svg_icons`，取不到降级编号 / 几何徽标；chevron 与增幅三角都用单 `<polygon>`，禁 blur / 内发光。

## 容量

- N = 3–6（推荐 4–5）；>6 先合并相近成果再画，不铺满薄段。
- 每段：段名 ≤8 字、巨数 ≤6 字符、增幅 / 口径 ≤10 字、说明句 ≤20 字（≤1 行）。
- 底部结论条：标签 ≤8 字 + 一句 ≤30 字 + 右侧收束语 ≤10 字。

## 配色（accent 单色深浅梯度，禁逐段换色）

- 段体 chevron 用**同一 theme accent 单色深浅梯度**（顺陈列方向由浅到深），表“同一条成果主线逐项展开”；**禁逐段随机换色**——多色会读成无关分类。
- 巨数用 title_text / accent_strong 深色；增幅徽标用**功能色**，按业务正负着色而非纯数值方向（周期 / 成本“越低越好”用绿色下降三角，规模 / 满意“越高越好”用绿色上升三角），颜色一律替换为当前 token。
- 白底指标卡深字、accent 深底 chevron 反白；引 `contract-visual-token-core.md` 保证深底不落黑字、浅底不落浅字。

## 内嵌 motif

- **增长徽标**（巨数 + 上升 / 下降三角 + 幅度）与**切角卡片 tab**：画法见 `svg-shape-patterns.md` 的增长徽标片段与折角 / 切角卡片片段，颜色替换为当前 token。

## 金标示例

- `load_skill_example(path="assets/examples/svg-ppt/decks/scenario-composite-structure-gold-pages/01-arrow-ribbon-metrics.svg")`
- 只参考四段 chevron 相扣、每段成果切角卡、巨数 + 增幅徽标的组织；不照抄坐标或把占位数据当业务事实，也勿照抄首行整页背景 `<rect>`（离线底色，运行时整页背景走 `deck_framework.background`，内容层画满页背景触发 `SVG_FULL_PAGE_BACKGROUND_FORBIDDEN`）。

## 反模式

- 逐段随机换色丢失“同一成果主线”；把时间递进 / 因果闭环硬塞成箭头带（该走 timeline / process-flow）；巨数不加口径或编造增幅；说明句写成长段落挤出卡片。
