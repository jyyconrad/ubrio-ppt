<!--
id: layout-mirror-compare
category: layout
read_when: 同一主体的正反两面对照（亮点/短板、成果/不足、优势/风险），每条各带一个量化
page_roles: content, summary
supports: svg_drawingml
outputs: svg_layout, mirror_compare_structure
depends_on: contract-layout-density.md, contract-visual-token-core.md
relation_specs: pairs_with:theme-blue-green-duotone, pairs_with:content-comparison, conflicts_with:layout-versus-duel, conflicts_with:layout-problem-improve-bilateral, conflicts_with:layout-diagonal-duo-panels
triggers: 镜像对照, 正反两面, 亮点短板, 优劣对照, 成果与不足, 优势与风险, mirror compare, pros and cons, strengths and weaknesses
max_use: 只讲同一主体正反镜像结构；两个不同对象的对碰改读 layout-versus-duel.md
source_notice: 参考公开职场汇报模板的结构组织方式，已抽象为本项目可复制方法；原作固定话术、示例文案、品牌水印一律作为分析输入后丢弃，不入语料。
-->

# Layout: Mirror Compare（镜像优劣对照）

## 适用判断

- use_when：同一主体的正反两面复盘——亮点/短板、成果/不足、优势/风险；两侧条数相等且逐条对仗，每条各带一个量化。
- avoid_when：
  - 两个不同对象或两个时点的对碰改用 `layout-versus-duel.md`（"甲 VS 乙"对决，非同一主体自我复盘）；
  - 两侧条数不等、不对仗，或无褒贬方向只并列同级要点，改用四卡/多卡网格；
  - 一个主判断配多证据用 `layout-left-claim-right-evidence.md`；问题→方案→收益的因果推进用 `layout-problem-solution-benefit.md`。

## 页面结构（画法与比例逻辑）

- 两半镜像等宽：正面区居左、负面区居右，中间留窄通道给中央双箭头。
- 每半纵向堆 N 行（两侧行数必须相等），行块等高等距；行内布置"标题 + 巨数卡 + 说明"，配一枚圆形编号徽标。
- 负面区镜像排布：徽标与巨数卡相对正面区水平对调，巨数旁加一枚升/降三角（▲▼）标方向。
- 中央一对上下贯通大箭头（polygon）：上箭头承载"正面/向好"、下箭头承载"负面/走弱"，**不承载文字**。
- 两枚区块标签走对角（正面置左下、负面置右上），形成正反张力。
- 比例：中央通道宽 ≥ 单侧巨数卡宽一半；行高按"(内容区高 − 行距×(N−1)) / N"均分。

## 容量

- 每侧恰 2–4 行（推荐 3，两侧必须相等）。
- 每行：标题 ≤14 字；巨数 ≤6 字符（含单位）；巨数标签 ≤8 字；说明 ≤34 字且 ≤2 行。
- 超载先砍最弱一条或两侧同步减行，绝不为凑对称编造量化；说明超长先改写，不缩字号硬塞。

## 配色语义（双色分工，不内联 hex）

- 正面区用主题主色、负面区用主题辅色/对比色，构成"主题双色分工"；色值引用 `theme-blue-green-duotone`（如蓝=亮点、绿=短板），本颗粒不写死 hex。
- 中央双箭头上下分取正面色/负面色；方向三角用统一告警色标"变差"，不逐行换色。

## 图标纪律

- 行内圆形图标走 `search_svg_icons` 取，取不到降级为圆+编号或几何徽标；禁手绘复杂象形。

## 金标示例

- 路径：`assets/examples/svg-ppt/decks/scenario-report-structure-gold-pages/02-mirror-compare.svg`
- 调用：`load_skill_example(path="assets/examples/svg-ppt/decks/scenario-report-structure-gold-pages/02-mirror-compare.svg")`
- 只参考镜像分区、行内信息层级、双箭头与对角标签组织；不要照抄坐标或把示例占位数据当业务事实。
- 勿照抄首行整页背景 `<rect>`：那只是离线预览底色，运行时背景由 `deck_framework.background` 承载，内容层画满页背景会触发 `SVG_FULL_PAGE_BACKGROUND_FORBIDDEN`。

## 反模式

- 两侧行数不等还硬对齐；正反色混用丢失分区语义；中央箭头塞文字。
- 方向三角乱指、与数据升降相悖；巨数编造或缺单位；说明写成长段落挤出卡片。
