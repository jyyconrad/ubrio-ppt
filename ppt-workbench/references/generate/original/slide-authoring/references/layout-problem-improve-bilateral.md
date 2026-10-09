<!--
id: layout-problem-improve-bilateral
category: layout
read_when: 问题与改进措施一一对应的复盘/整改页，强调从问题域到改进域的转化
page_roles: content, summary
supports: svg_drawingml
outputs: svg_layout, problem_improve_bilateral_structure
depends_on: contract-layout-density.md, contract-visual-token-core.md
relation_specs: pairs_with:theme-blue-green-duotone, conflicts_with:layout-problem-solution-benefit, conflicts_with:layout-mirror-compare, conflicts_with:layout-problem-improve-value-rail
triggers: 问题改进对照, 痛点对策, 症结整改, 问题域改进域, 双侧转化, 问题到改进, 左问题右改进, problem improvement, problem to improvement
max_use: 只讲问题↔改进一一对应的双侧转化结构；问题→方案→收益三段因果读 layout-problem-solution-benefit.md，同一主体量化正反镜像读 layout-mirror-compare.md
source_notice: 参考公开职场汇报模板的结构组织方式，已抽象为本项目可复制方法；原作固定话术、示例文案、品牌水印一律作为分析输入后丢弃，不入语料。
-->

# Layout: Problem-Improve Bilateral（问题↔改进双侧对照）

## 适用判断

- use_when：痛点→对策一一对应的复盘/整改页，左问题右改进逐条对仗，主轴是"从问题到改进的转化"。
- avoid_when：
  - 需收益推导的问题→方案→收益三段因果，用 `layout-problem-solution-benefit.md`（单向三列）；
  - 同一主体量化正反镜像用 `layout-mirror-compare.md`；两个对象对决式 PK 用 `layout-versus-duel.md`；
  - 单侧条数 >4：拆页或改 PSB 三列。
  - 两域交集本身承载共性/兼备结论（而非问题→改进转化）的通用维恩页，与非对称"问题面板+改进面板+价值轨"页（读 `layout-problem-improve-value-rail.md`）都不属本颗粒。

## 两变体与画法

- variant A（维恩转化锚，3+3）：深色单句题条；两等径交叠圆（左问题域/右改进域，圆心间距 ≈1.3r、透镜宽 ≈0.7r），圆内白字域标签，透镜内一枚指向改进侧的转化箭头；两翼各 3 个编号点，左翼右对齐贴左圆、右翼左对齐贴右圆，左 i 右 i 同基线 y 一一对应，每点=空心编号圆+小标题+正文。
- variant B（循环锚，2+2）：左右各"区块头条 + 2 张纵叠卡"，中心同心虚线圆 + 中心标签 + 环绕虚线箭头。
- 选型：恰 3 对用 A、恰 2 对用 B、>4 对拆页或改 PSB。中心环是"转化锚"不是流程环——闭环步骤流程读 `layout-cycle-loop.md`。

## 容量

- variant A：每侧恰 3 点，小标题 ≤10 字、正文 ≤44 字且 ≤4 行；中心两域标签各 ≤6 字。
- variant B：每栏恰 2 卡，标题 ≤10 字、正文 ≤44 字；中心标签 ≤8 字。
- 超载先合并弱项或拆页，不缩字号硬塞、不凑对称编造条目。

## 配色语义（主题双色分工，不内联 hex）

- 问题域用主题辅色、改进域用主题主色，色值引用 `theme-blue-green-duotone`（绿=问题、蓝=改进），不写死 hex。
- 交叠加深优先用两个 `<circle fill-opacity>` 做 per-element alpha 叠加，交叠区自然变深、可编辑；圆身需要保持纯色不透时才手算第三色画独立更深色 polygon 透镜。深色圆面域标签反白，编号圆/文字浅底深字。

## 渲染降级纪律

- 交叠加深**优先**用两个 `<circle fill-opacity="0.5~0.6">` 做 per-element alpha 双圆叠加（可编辑，交叠区自然变深）；圆身需保持纯色不透明时才退回画独立更深色 `path`/`polygon` 透镜叠在两圆之上。**禁 `rgba()` 颜色语法与 `<g opacity>` 组级透明模拟混色**（per-element `fill-opacity`/`stroke-opacity` 允许）；variant B 同心虚线圆与环绕虚线箭头用 `stroke-dasharray` + `polygon`/`marker`。
- 原模板放射沙漏底纹去除或改单个浅色实心 `polygon`；底纹本身禁 `filter`/`blur`/`mask` 模拟（复杂纹理转换器不支持），需要强调时可在卡片/徽标上叠加单个外发光或投影 `filter`（仅 `feGaussianBlur`）。

## 金标示例

- 路径：`assets/examples/svg-ppt/decks/scenario-report-structure-gold-pages/06-problem-improve-bilateral.svg`
- 调用：`load_skill_example(path="assets/examples/svg-ppt/decks/scenario-report-structure-gold-pages/06-problem-improve-bilateral.svg")`
- alpha 叠加版对照：`assets/examples/svg-ppt/decks/scenario-effects-structure-gold-pages/03-venn-alpha-overlap.svg`（两圆 fill-opacity 交叠自然加深、可编辑；圆身纯色诉求仍看本页 06 的独立 polygon 透镜法）。
- 只参考维恩双域分区、交叠透镜转化箭头、两翼编号点逐条对应的组织与信息层级；不要照抄坐标或把示例占位数据当业务事实。
- 勿照抄首行整页背景 `<rect>`：那只是离线预览底色，运行时背景由 `deck_framework.background` 承载，内容层画满页背景会触发 `SVG_FULL_PAGE_BACKGROUND_FORBIDDEN`。
