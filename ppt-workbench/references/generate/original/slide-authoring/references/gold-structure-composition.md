<!--
id: gold-structure-composition
category: composition-system
read_when: 需要从金标示例抽象可组合结构，避免每页固定三卡/四卡
page_roles: content, summary
supports: svg_drawingml
outputs: composition_patterns, page_spec_layout_choice, svg_groups
depends_on: contract-structure-hierarchy.md, gold-page-patterns.md
max_use: 只选择 1-2 个组合模式用于当前页，不要把全部模式塞进一页
-->

# Gold Structure Composition

## 内容说明

先选信息组合，再落到 builder layout。组合模式可以混用，但每页只保留一条主叙事线。

## 组合模式

### 1. north-star + metric-strip + evidence-cluster + action-bar

- read_when：经营复盘、年度总结、结果达成页。
- 必填槽位：北极星判断、3-5 指标、2-3 证据组、底部行动合同。
- SVG groups：`key-message`、`metrics-panel`、`evidence-cluster`、`action-bar`。
- 落地布局：`gold_cards` 或 `gold_evidence_table`。

### 2. left-diagnosis + right-proof-chain + bottom-contract

- read_when：痛点页、问题闭环、风险收敛。
- 必填槽位：左侧诊断结论、右侧证据链、底部 Owner/节点/风险。
- SVG groups：`diagnosis-panel`、`proof-chain`、`bottom-contract`。
- 落地布局：`gold_evidence_table`，必要时手写 SVG 分区。

### 3. stage-timeline + milestone-cards + acceptance-rules

- read_when：项目阶段、实施路线、年度节奏。
- 必填槽位：阶段线、每阶段目标、验收标准、阻塞项。
- SVG groups：`timeline-roadmap`、`milestone-cards`、`acceptance-rules`。
- 落地布局：`gold_timeline`。

### 4. central-judgment + radial-capabilities + risk-strip

- read_when：能力模型、战略抓手、组织机制。
- 必填槽位：中心判断、4-6 个能力环绕、底部风险或推进条件。
- SVG groups：`central-judgment`、`capability-ring`、`risk-strip`。
- 落地布局：手写 SVG 或 `gold_cards` 变体，不能排成普通四卡。

### 5. comparison-before-after + evidence-table + decision-strip

- read_when：改造前后、竞品对比、方案取舍。
- 必填槽位：前后对照、证据表、决策建议。
- SVG groups：`before-after-band`、`evidence-action-table`、`decision-strip`。
- 落地布局：`gold_evidence_table`。

### 6. issue-funnel + root-cause + escalation-ladder

- read_when：问题很多但需要聚焦根因。
- 必填槽位：问题漏斗、根因拆解、升级路径。
- SVG groups：`issue-funnel`、`root-cause-grid`、`escalation-ladder`。
- 落地布局：手写 SVG 或 `gold_cards` 变体。

### 7. process-flow + control-points + owner-contract

- read_when：流程图、审批链、作业流。
- 必填槽位：流程节点、输入输出、控制点、Owner/验收标准。
- SVG groups：`process-flow`、`flow-step-1..N`、`process-contract`。
- 落地布局：`layout-process-flow.md`。

### 8. pyramid-stack + base-proof + risk-sidecar

- read_when：金字塔、战略分层、能力层级。
- 必填槽位：顶层目标、中层抓手、底层证据、侧边风险或来源。
- SVG groups：`pyramid-stack`、`pyramid-top`、`pyramid-middle`、`pyramid-base`。
- 落地布局：`layout-pyramid-hierarchy.md`。

### 9. cycle-loop + feedback-metric + loop-contract

- read_when：闭环机制、PDCA、增长飞轮。
- 必填槽位：循环目标、4-6 个环节、反馈指标、闭环责任。
- SVG groups：`cycle-loop`、`loop-core`、`loop-step-1..N`、`loop-contract`。
- 落地布局：`layout-cycle-loop.md`。

### 10. screenshot-proof + claim-callouts + source-strip

- read_when：截图证明、系统记录、案例证据。
- 必填槽位：主判断、截图占位、2-3 个标注、来源/时间/口径。
- SVG groups：`proof-claim`、`screenshot-proof-1`、`proof-callout-1..N`、`proof-source`。
- 落地布局：`layout-screenshot-proof.md`。

### 11. chart-claim + native-chart-slot + insight-note

- read_when：需要柱线饼等 PowerPoint 原生图表。
- 必填槽位：图表结论、chart slot、数据、洞察、来源。
- SVG groups：`chart-claim`、`native-chart-slots`、`chart-slot-1`、`chart-source`。
- 落地布局：`layout-native-chart-slot.md`；SVG 不手绘真实图表。

## 使用规则

- 每页先写组合名，再写 `structure_hierarchy`，最后写 `page_spec.layout`。
- 同一套 deck 中相邻正文页避免重复相同组合模式。
- builder layout 只是落地手段；金标效果来自信息层级、承载方式和证据密度。
- 如果只能用 `gold_cards`，也要让卡片内部形成不同层级：判断、证据、解释、动作。

## 金标示例

- 示例路径：`assets/examples/svg-ppt/decks/scenario-government-briefing-gold-pages/04-tiered-cards-composite.svg`
- 需要查看结构时调用：`load_skill_example(path="assets/examples/svg-ppt/decks/scenario-government-briefing-gold-pages/04-tiered-cards-composite.svg")`
- 卡片 + 汇流 + 表格三元素融合示例：三档价格卡（含深色推荐主卡）→ 汇流箭头 → 共享额度池横条 → 配比 `native-table-slot`，示范多类结构在一页里的纵向组合与明暗节奏；表格部分走 native-table-slot，不手绘表格。
- 勿照抄示例首行 `<rect x="0" y="0" width="1280" height="720">`：它只是离线预览底色。运行时整页背景由 `deck_framework.background` 承载，提交 `render_svg_drawingml_slide` 的 SVG 不画满页背景矩形，否则触发 `SVG_FULL_PAGE_BACKGROUND_FORBIDDEN`（同 `drawingml-svg-authoring-core.md`）。
