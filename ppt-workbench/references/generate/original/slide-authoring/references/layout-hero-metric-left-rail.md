<!--
id: layout-hero-metric-left-rail
category: layout
module_type: layout_family
read_when: 左侧深色 hero 巨数英雄栏（一个统领巨数 + 一句总结，视觉最重）+ 右侧 2-4 个指标块（可含环形 gauge）；左深右浅配色分区
page_roles: content, summary
stage_tags: slide_generation
supports: svg_drawingml
outputs: svg_layout, hero_metric_rail_structure
depends_on: contract-layout-density.md, contract-visual-token-core.md
relation_specs: requires:contract-visual-token-core, conflicts_with:layout-left-claim-right-evidence, pairs_with:theme-dark-business-blue, pairs_with:svg-shape-patterns
triggers: 左边深色大数字总结, 左侧英雄栏巨数, 深色总结栏配右侧指标块, 英雄数字栏, 左深色hero右侧看板, 环形进度配大数字, 左栏一个大数右栏几块, 深色栏, 指标块, hero metric rail, hero metric left rail, 左侧大数字, 左大数右卡, 大数字统领
max_use: 只讲左深色 hero 巨数 + 右侧指标块分区；左栏以文字论证为主读 layout-left-claim-right-evidence.md，对称镜像对比读 layout-mirror-compare.md
source_notice: 参考公开职场汇报模板的结构组织方式与配色体系，已抽象为本项目可复制方法；原作固定话术、示例文案、品牌水印一律作为分析输入后丢弃，不入语料。
-->

# Layout: Hero Metric Left Rail（左深色英雄巨数栏 + 右侧指标块）

## 适用判断

- use_when：**一个统领巨数**领衔（核心营收 / 总量 / 达成率），配一句总结定调，视觉最重；右侧再挂 2-4 个支撑指标块，其中可含一枚环形 gauge。左深右浅配色分区强化"总—分"主次。
- avoid_when：
  - 左栏是**文字论证 / 主判断 + 背景 + 逐条证据**（数字不是主角）→ `layout-left-claim-right-evidence.md`；
  - 同一主体正反 / 双时点**对称镜像**逐条对比 → `layout-mirror-compare.md`；
  - 一排等权并列巨数、无统领英雄数 → `layout-kpi-strip.md`。
- **一句判据**："左栏是否有唯一压场巨数 + 深色实底反白"——是则本颗粒，否则回文字论证或 KPI 带。

## 骨架（画法与比例逻辑）

- 左栏 hero：占页宽 **35-40%**，深色**实底面板**（非整页背景）承载，自上而下：小标签（口径/周期）+ 统领巨数 ≤6 字符 + 总结句 ≤24 字 +（可选）一枚小徽标 / 增长徽标。巨数字号最大，是全页视觉锚。
- 右栏：占页宽 **55-60%**，铺一层浅色 `surface` 区，其上 **2-4 块**指标块（2×2 或竖排）。每块：标题 ≤10 字 + 数值 ≤6 字符 + 一句 ≤20 字；序号 / 图标徽标可选。
- 其中**一块可换成环形 gauge**（达成率 / 完成度）：底环 + 前景弧 + 中心巨数，画法见 `svg-shape-patterns` 环形进度片段。
- 左右两栏之间留 ≥40px 通道；块间距 ≥24px。左栏底边与右栏指标区上下留白对齐。

## 容量

- 右侧块 **2-4 个**（推荐 3-4）；>4 先合并次要指标或拆页，不塞第 5 块破坏"左总右分"。
- hero：巨数 ≤6 字符、总结 ≤24 字（≤2 行）；右块：标题 ≤10 字、数值 ≤6 字符、一句 ≤20 字。
- gauge 中心数 ≤4 字符（百分比 / 达成率），环内只放这一个数，说明文字落环下。

## 配色（左深右浅分区，引 token 不内联死 hex）

- 左栏 `background` / 深色 `surface`，**文字全部反白**（`title_text=#FFFFFF`、`body_text` 浅色）；**深底禁黑字、深灰正文和低透明细线**（见 `contract-visual-token-core` 可见性条款与 `theme-dark-business-blue`）。巨数用最亮反白，`accent` 只点小标签 / 徽标。
- 右栏浅 `surface` + 深字，指标块浅底细描边；数值用 `accent` 或深主色，增长 / 达标用功能色（cyan/green 正、amber/red 负）。
- 左深右浅两档明度差要足够，构成"深色总结栏统领、浅色看板支撑"的分区语义；禁左右同明度。

## 环形 gauge 与增长徽标

- 环形单值达成率 = 甜甜圈弧（两段 path 扇形闭合或 stroke-dasharray 描边圆），可编辑可转换，画法见 `svg-shape-patterns` 环形进度片段。
- 巨数配同比涨跌时用增长徽标（巨数 + 上升 / 下降三角 + 增幅%，功能色），见 `svg-shape-patterns` 增长徽标片段。
- 每个 `<text>` 显式 `fill` / `font-family` / `font-size`；徽标走 `search_svg_icons`，取不到降级编号 / 几何徽标；禁 blur / 内发光。

## 金标示例

- 路径：`assets/examples/svg-ppt/decks/scenario-composite-structure-gold-pages/03-hero-metric-left-rail.svg`
- 调用：`load_skill_example(path="assets/examples/svg-ppt/decks/scenario-composite-structure-gold-pages/03-hero-metric-left-rail.svg")`
- 只参考左深色 hero 巨数栏、右侧四块（含环形达成率）与左深右浅分区的组织；不要照抄坐标或把占位数据当业务事实。
- 勿照抄首行整页背景 `<rect>`：那只是离线预览底色，运行时背景由 `deck_framework.background` 承载，内容层画满页背景会触发 `SVG_FULL_PAGE_BACKGROUND_FORBIDDEN`。

## 反模式

- 左栏堆长段文字论证冒充 hero（该读 left-claim-right-evidence）；左栏无唯一压场巨数、几个数平权（该读 kpi-strip）。
- 深底黑字 / 深灰小字（不可读）；左右同明度丢失分区；右侧块 >4 挤成密集网格；gauge 环内塞多个数字或长文本。
