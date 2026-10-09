<!--
id: layout-funnel-stage-stack
category: layout
module_type: layout_family
read_when: 筛选/转化/收窄的动态流转（曝光→点击→转化→成交、线索→商机→成交、初筛→复筛→录用），层间有流量递减/流失
page_roles: content, summary
stage_tags: slide_generation
supports: svg_drawingml
outputs: svg_layout, funnel_stage_structure
depends_on: contract-layout-density.md, contract-visual-token-core.md
relation_specs: conflicts_with:layout-pyramid-hierarchy, pairs_with:layout-kpi-strip, pairs_with:svg-shape-3d-isometric
triggers: 漏斗, 转化漏斗, 逐层转化, 层层筛选, 流失, 收窄, 线索到成交, 转化率, funnel, conversion funnel
max_use: 只讲向下收窄的转化/筛选漏斗；静态层级支撑读 layout-pyramid-hierarchy.md
source_notice: 参考公开职场汇报模板的结构组织方式与配色体系，已抽象为本项目可复制方法；原作固定话术、示例文案、品牌水印一律作为分析输入后丢弃，不入语料。
-->

# Layout: Funnel Stage Stack（转化漏斗分层）

## 适用判断

- use_when：筛选 / 转化 / 收窄的**动态流转**——曝光→点击→转化→成交、线索→商机→成交、初筛→复筛→录用；层间有流量递减 / 流失，常配逐层递减巨数与转化率。
- avoid_when：
  - 静态层级 / 支撑 / 优先级堆叠（底层支撑顶层，无流量流失）→ `layout-pyramid-hierarchy.md`；
  - 逐期（月/季/年）时间推进 → timeline 家族；
  - 问题→方案→收益的因果推进 → `layout-problem-solution-benefit.md`。
- **一句判据**："每层数量是否越往下越少、层间是否有流失/转化"——是则 funnel，否则 pyramid。

## 骨架（画法与比例逻辑）

- 纵向单调收窄：N 层闭合 `<polygon>` 梯形自上而下堆叠，每层上边宽 = 上一层下边宽。
- **收窄系数 r**：第 k+1 层上边宽 = 第 k 层 × r，`r` 取 0.72–0.82（越小越尖）。
- **层高**：`(funnel_region.h − gap×(N−1)) / N`；层间 `gap ≈ funnel_region.h × 0.02–0.03`。
- 每层三个槽位（都居中）：`tier_label` 阶段名 ≤8 字；`tier_metric`（可选）逐层递减巨数 ≤6 字符；`tier_note`（可选）一句限定 ≤24 字、超长移侧栏。
- 转化率标在相邻两层之间（层边右侧小标），承载"层→层转化"语义。
- 侧栏可选：`funnel_side_panels` ≤2，或单侧结论栏（放整体转化率 + 诊断），**默认关闭**；开侧栏时漏斗主体相应缩窄，不占满整页。

## 容量

- N = 3–5（推荐 3–4）；>5 先合并相邻阶段再画，不要切太多薄层。
- 每层：`tier_label` ≤8 字、`tier_metric` ≤6 字符、`tier_note` ≤24 字（≤2 行，随层收窄同步压缩）。
- 侧栏结论栏：标题 ≤12 字、诊断 3–4 条每条 ≤18 字、整体转化率巨数一枚。

## 配色（单色深浅梯度）

- **同主题 accent 单色系深浅梯度**：由上到下加深（或减淡）方向一致，表"逐层聚焦收窄"。
- 末层可用**告警色**点缀"流失"（如层间小箭头、待优化标记），不整层换色。
- **禁逐层随机换色**：多色会读成"并列分类"而非"同一漏斗逐层转化"。

## 立体感与降级

- pairs_with `svg-shape-3d-isometric`：每层可加一条纵向 `linearGradient` 或侧面梯形做轻立体，点到为止，不做真透视/斜切。
- 阶段徽标走 `search_svg_icons`，取不到降级为编号/几何徽标；每个 `<text>` 显式 fill/font-family/font-size，禁毛玻璃/内发光/blur。

## 金标示例

- 路径：`assets/examples/svg-ppt/decks/scenario-effects-structure-gold-pages/04-funnel-stage-stack.svg`
- 调用：`load_skill_example(path="assets/examples/svg-ppt/decks/scenario-effects-structure-gold-pages/04-funnel-stage-stack.svg")`
- 只参考四层收窄梯形、逐层递减巨数、层间转化率与单侧诊断栏的组织；不要照抄坐标或把占位数据当业务事实。
- 勿照抄首行整页背景 `<rect>`：那只是离线预览底色，运行时背景由 `deck_framework.background` 承载，内容层画满页背景会触发 `SVG_FULL_PAGE_BACKGROUND_FORBIDDEN`。

## 反模式

- 用漏斗画静态层级支撑（无流失）——该读 pyramid；逐层随机换色丢失"同一漏斗"语义。
- 层数 >5 切太多薄层；巨数不逐层递减或编造转化率；`tier_note` 写成长段落挤出梯形。
