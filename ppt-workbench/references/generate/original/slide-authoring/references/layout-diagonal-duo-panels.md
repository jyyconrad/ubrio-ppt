<!--
id: layout-diagonal-duo-panels
category: layout
read_when: 同页并置两个各自成体系、结构对仗的独立主题（复盘/规划、现状/目标）
page_roles: content, summary
supports: svg_drawingml
outputs: svg_layout, diagonal_duo_panels_structure
depends_on: contract-layout-density.md, contract-visual-token-core.md
relation_specs: pairs_with:theme-blue-green-duotone, pairs_with:layout-kpi-strip, conflicts_with:layout-mirror-compare
triggers: 对角分隔, 双栏并置, 两大板块并置, 复盘规划, 左右两大板块, 现状与目标, diagonal split, duo panels, side-by-side panels
max_use: 只讲两个独立主题的对角双栏并置；同一主体正反镜像读 layout-mirror-compare.md，两对象对决读 layout-versus-duel.md
source_notice: 参考公开职场汇报模板的结构组织方式，已抽象为本项目可复制方法；原作固定话术、示例文案、品牌水印一律作为分析输入后丢弃，不入语料。
-->

# Layout: Diagonal Duo Panels（对角分隔双栏并置）

## 适用判断

- use_when：同页并置两个**独立主题**且结构对仗——复盘 vs 规划、现状 vs 目标；每栏自成一体、指标各自表达，两栏间无逐条对应。
- avoid_when：
  - 同一主体正反两面逐条镜像用 `layout-mirror-compare.md`；
  - 两对象/时点指标对决 PK 给结论用 `layout-versus-duel.md`；
  - 问题→对策一一转化（逐条对应）用 `layout-problem-improve-bilateral.md`；
  - 单主题不需分栏，用四卡/多卡网格。

## 页面结构（画法与比例逻辑）

- 左右两大面板等宽对仗并置，留中央窄通道；两栏起止 y 对齐、同层等高。
- 中央**斜向多边形折带**纵向贯通分隔：2-3 折点之字形 polygon，上下两段拼**撞色**（上主色/下辅色），中点叠白底圆徽标承接两栏。
- 每栏内部对仗，自上而下：标签胶囊 + **4 联 KPI**（数值+标签，2×2）+ **要素相加公式链** + 2-3 条 bullet + 1 个**环形单值进度**（甜甜圈弧）；一栏底部可加横幅收口。

## 要素相加公式链（micro-motif，可复用）

等宽圆角标签 rect 串联表达"多要素相加得一个结论"：`[A] + [B] + [C] = [结论]`。term rect 浅底主色字、`+` 间隔，末尾 `=` 接实底深色结论 rect（反白字）；标签 ≤6 字、term 3 项。其它布局需叠加得结论时可引用。

## 容量

- 两栏内容量必须对仗（不允许一边 4 KPI 一边 2 KPI）；超载先砍最弱项，不为凑对仗编造指标。
- 每栏：KPI 恰 4 项（数值 ≤6 字符、标签 ≤8 字）；公式链 term 3 项（≤6 字）+ 1 结论；bullet 2-3 条（≤34 字，超长改写）；环形单值 1 个（≤4 字符）；底部横幅 ≤12 字。

## 配色语义（双主题分工，不内联 hex）

- 两栏用主题主/辅两主色分区（左蓝右绿分工）构成"主蓝辅绿双区"，引用 `theme-blue-green-duotone`、不写死 hex；折带上下段取两栏主色拼接、中点徽标白底，栏内元素不跨栏串色。

## 渲染降级纪律

- 斜向分隔＝2-3 顶点 polygon 折带（**纯色**，不叠加发光/glow，保持撞色分区的克制感）；禁斜面高光（伪 3D，转换器不支持）与多滤镜堆叠。中点白底圆徽标如需强调可选单个外发光/投影 `filter`（仅 `feGaussianBlur`）。
- 环形单值＝甜甜圈弧（两段 path 或 stroke-dasharray 描边圆，画法见 svg-shape-patterns 环形进度片段）；大圆角卡＝rect 的 rx（rx==ry 保原生调节柄）。

## 金标示例

- 示例路径与调用：`load_skill_example(path="assets/examples/svg-ppt/decks/scenario-report-structure-gold-pages/07-diagonal-duo-panels.svg")`
- 只参考对角折带、两栏对仗结构、相加公式链与环形进度的组织，不照抄坐标或把占位数据当业务事实。
- 勿照抄首行整页背景 `<rect>`：那只是离线预览底色，运行时背景由 `deck_framework.background` 承载，内容层画满页背景会触发 `SVG_FULL_PAGE_BACKGROUND_FORBIDDEN`。

## 反模式

- 两栏不对仗；独立主题硬做成 VS 对决/正反镜像；折带本身发光或做 3D 斜面（折带需保持纯色克制，中点徽标的克制发光不在此列）；徽标塞长文字。
