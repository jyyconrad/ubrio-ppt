<!--
id: composition-business-report-argument-cascade
category: composition-system
read_when: 中国式业务汇报正文页需要把观点、机制、指标、案例、洞察和行动组合成一条论证链，而普通三卡/四卡不足以表达时
page_roles: content, summary
supports: svg_drawingml
outputs: report_argument_spine, page_composition_plan, svg_group_plan, evidence_alignment_checks
depends_on: contract-structure-hierarchy.md, contract-content-density.md, content-pyramid-claim-evidence-action.md, svg-shape-patterns.md
relation_specs: pairs_with:gold-structure-composition, conflicts_with:anti-pattern-fixed-template-monotony, conflicts_with:anti-pattern-low-density-slogan
max_use: 只选择一条主论证链和一个现有 layout；不要把全部组合塞进一页
source_notice: 方法来自 docs/03-architecture/ppt模板 的 23 张 visual-only 截图逐页分析；只晋级跨页重复的方法，不保存源模板坐标、色值、文案、业务数据、Logo、水印或可编辑性推断。
-->

# Business Report Argument Cascade

## 目标

把高密度业务内容装成一条可以汇报、可以验证的论证链。先回答“这页要证明什么”，再决定
机制、证据、洞察和行动如何组合；不能先画三卡/四卡，再把内容硬塞进去。

本 reference 是 composition method，不是新 layout 家族。时间、层级、对比、流程、矩阵、
原生图表和图片仍路由到已有 `layout-*` reference。

## 输入合同

开始前写清：

- `page_role`：定向、诊断、方案、路线、举证、治理或总结。
- `action_claim`：可被同页证据验证的标题判断。
- `proof_goal`：听众看完后应相信什么，而不是页面要放哪些组件。
- `mechanism`：组织、方法、架构、流程或因果解释；没有则明确本页是纯证据页。
- `evidence[]`：数据、事实、案例、图表、截图、来源和口径。
- `implication`：证据意味着什么；不能只复述数字。
- `action_or_risk`：Owner、时点、验收、风险或决策请求；不适用时说明原因。
- `source`：来源、周期、范围和计算口径。

标题含数字时，必须在 `evidence[]` 中找到同周期、同范围、同单位的回指。目标、预测、行业值
和实际结果必须显式区分，不能把 `target` 写成 `achieved`。

## 先选一条主论证链

| 业务任务 | 主论证链 | 必填槽位 | 优先复用 |
|---|---|---|---|
| 案例复盘 / 成效证明 | `baseline → intervention → outcomes → lesson` | 2-4 背景事实、3-5 举措、3-6 KPI、1 句经验 | `layout-process-flow`、`layout-kpi-strip`、`layout-three-cards-action-bar` |
| 问题治理 / 整改 | `symptom → cause → response → insight` | 2-4 问题，每个问题有现象、根因、方案、洞察 | `layout-problem-improve-bilateral`、`layout-problem-improve-value-rail` |
| 方法论 / ROI | `method → metric → case → value` | 2-4 方法、2-3 度量、1 个案例、2-4 结果 | `layout-left-claim-right-evidence`、`layout-native-chart-slot` |
| 平台 / 能力架构 | `architecture → common capability → value proof` | 3-5 架构节点、2-4 共性能力、3-5 结果 | `layout-pyramid-hierarchy`、`layout-center-radial`、`layout-process-flow` |
| 阶段推进 / 门径治理 | `stage flow → mechanism proof → result scorecard` | 3-6 阶段、1-2 个有效性解释、3 个结果 | `layout-process-flow`、`layout-phased-action-columns`、`layout-timeline-horizontal` |
| Why / 转型定位 | `pressure → bottleneck → positioning` | 2-3 环境事实、3-4 瓶颈、1 句定位 | `content-scqa`、`layout-left-claim-right-evidence` |
| operating model | `north star → enablers → layers → collaboration → value` | 北极星1、enabler 2、层级3-5、协同1-2、结果3-5 | 先组合已有 hierarchy/process/KPI，不把单个截图屋顶造型晋级为固定 layout |

只选一条主链。需要第二条关系时，它只能作为 proof、sidecar 或 bottom contract，不能与主链争夺
第一阅读路径。

## 区域装配

按可用内容区比例分配，不记忆源截图坐标：

- `title_claim`：高度 12%-18%，标题和必要 lead；标题是第一视觉锚点。
- `context_or_baseline`：0%-12%，只在理解证据需要基线时出现。
- `mechanism_or_evidence`：45%-60%，承载主关系和主要证据。
- `implication_or_action`：12%-18%，使用 insight rail、case proof rail 或 conclusion band。
- `source_note`：3%-5%，一句来源/口径；不能用水印代替。

主体必须至少包含一个非普通卡片网格的关系载体：时间轨道、流程、层级、对照、矩阵、原生图表、
证据表或案例链。若主体仍只是同尺寸卡片，重新检查 `proof_goal` 和关系类型。

## 组件组合合同

详细 SVG 片段见 `svg-shape-patterns.md`：

- `section-tab-frame`：只命名一个大分区；不能给每张小卡加页签。
- `semantic-row-stack`：多个对象共享同一字段时使用，标签列和 row schema 跨对象稳定。
- `metric-delta-card`：一个卡只表达一个主指标，按“定义/基线 → 结果 → implication”排序。
- `insight-rail`：翻译主体证据，不新增事实，最多两行。
- `conclusion-band`：把复杂证据收成原则、行动或决策，最多三项且必须回指主体。

推荐 group 命名：

- `main-title` / `key-message`
- `context-baseline`
- `argument-spine`
- `mechanism-panel`
- `evidence-cluster`
- `metric-delta-1..N`
- `insight-rail`
- `conclusion-band`
- `source-note`

## 容量与受控变体

- 三列组件：每列允许标题 + 2-3 行说明；四列只允许标题 + 2 行；五至六列只保留一个指标和一句意义。
- 阶段/门径常规 3-6 步；7 步仅在流程主导、每步标题不超过 7 字且说明不超过 2 行时作为高密候选，必须真实渲染复核；超过 7 步拆主阶段/子阶段。
- 指标体系 2-3 类，每类最多 3 个指标；案例链 3-5 个动作；问题网格 2-4 个问题。
- 架构层级 3-5 层；协同机制 1-2 个；结果 3-5 项。层级更多时合并抽象或拆说明页。
- 内容超量先删重复、压缩次要解释、转移来源/附录或拆页；不能缩小字号维持表面对齐。

## 观点突出算法

1. 标题只保留一个判断，可带 1-2 个最高价值数字。
2. 用关系几何表达时间、因果、层级或对照，不靠随机颜色表达关系。
3. 主色只强调标题、关键数字、结构锚点和收口；同级并列模块保持同色。
4. 数据旁边写 implication，回答“因此怎样”；不要再写一遍“提升 41%”。
5. 最终行动/决策组件的视觉权重高于普通节点，但低于标题。

## 失败检查

- 标题数字在主体没有同口径证据，或目标/预测被写成已完成结果。
- 只有架构/流程，没有业务价值、验收结果或风险闭环。
- Insight / conclusion 引入主体不存在的新事实，或只是复述数字。
- 多对象本应共享字段，却各自采用不同 row schema，无法比较。
- 为了套模板虚构第四卡、第五阶段或第三个指标。
- 页面同时存在两条同权主线，阅读方向冲突。
- 真实图表、照片、书封、证据截图被手绘 SVG 模仿。
- 依靠小字号、长段落、水印或装饰横条掩盖证据缺口和主体空洞。

## Deck 承接

当前页还要说明它在整册中的问题位置。业务汇报优先使用：

`Why / 定向 → Diagnosis / 问题 → What / 目标体系 → How / 推进机制 → Proof / 价值证明 → Closure / 决策收口`

若当前页是 Why 页却出现在大量方案证明之后，检查是否应前置；若最后只有体系蓝图和 KPI，补 Owner、
时点、资源、验收和风险页完成闭环。
