<!--
id: page-role-disambiguation
category: content-structure
stage: outline, slide_generation
read_when: 判断当前页属于 20 类稳定 page role 的哪一类；区分相邻角色(context/statement、metrics/trend、comparison/distribution/relationship、process/trend、analysis_framework/context)；或把视觉形态(image/ambient)错当业务角色
page_roles: content, summary
supports: svg_drawingml
outputs: page_role_selection, visual_mode_separation
relation_specs: pairs_with:layout-routing-method, pairs_with:content-swot-3c-pest
max_use: 只定 page role 与视觉形态分轴；具体 business pattern 选择读 business-pattern-selection
-->

# Page Role 判别

`page_role` 是**这一页在汇报里的业务职责**，全 deck 稳定用同一套 20 类枚举。它不含颜色、背景、坐标，也不等于视觉形态。

## 核心分轴：职责 ≠ 视觉形态

`image_dominant` / `ambient` / `diagram_dominant` / `table_dominant` / `data_dominant` 是 **visual_mode（呈现方式）**，不是 page role。一页"满屏配图"仍可能是 `case_evidence`（证据）或 `cover`（封面）；用图多少由表达主轴决定，不占用职责判断。先定职责，再单独定 visual_mode。

## 20 类角色（按叙事职责分组）

- **开场与结构**：`cover`、`agenda`、`section_divider`
- **背景与主张**：`context`、`statement`
- **数据与经营**：`metrics`、`trend`、`comparison`、`distribution`、`relationship`
- **方法与分析**：`process`、`analysis_framework`、`case_evidence`
- **风险与行动**：`risk_issue`、`action_plan`、`result_summary`
- **背书与收尾**：`team_credibility`、`appendix_source`、`closing`、`disclaimer`

角色带别名（同一职责的旧叫法），选到别名等于选到主角色：`data_insight`/`metric_grid`→`metrics`，`timeline`→`trend`，`before_after`→`comparison`，`funnel`/`treemap`→`distribution`，`sankey`/`network`/`value_chain`→`relationship`，`roadmap`/`gantt`→`process`，`risk_matrix`→`risk_issue`，`executive_summary`→`result_summary`。

## 相邻角色判别（最容易混的几对）

- **context vs statement**：交代背景/现状/问题来源 → `context`；放大一句核心判断或结论 → `statement`。
- **metrics vs trend**：静态汇报 KPI 快照 → `metrics`；解释随时间/阶段的变化 → `trend`。
- **comparison vs distribution vs relationship**：对象/方案/前后对比 → `comparison`；占比、结构、集中度 → `distribution`；关联、流向、生态、网络、层级 → `relationship`。
- **process vs trend**：讲步骤、路径、计划、实施进程 → `process`；讲量随时间的走势 → `trend`。二者都可能带时间轴，区别是"做什么的次序"还是"数值的变化"。
- **analysis_framework vs context**：用标准业务模型（SWOT/PESTEL/五力/3C）做系统分析 → `analysis_framework`；只是叙述外部背景、不套模型 → `context`。
- **risk_issue vs action_plan**：陈列风险/问题/阻碍 → `risk_issue`；给责任、优先级、下一步 → `action_plan`。同页两者都重时，多为 `risk_issue` 主体 + 底部行动收口。
- **result_summary vs statement**：复盘/汇总多项成果与收口 → `result_summary`；单点强判断 → `statement`。

## 选择原则

- 一页只承担**一个主职责**；确实横跨两类时按"主体信息"归主角色，另一类作收口或侧栏。
- 角色要稳定：`page_role` 是 20 类里最贴业务职责的那个，识别不确定时选最接近的，不要为迁就某个版式改角色。
- `business_pattern` 可以多候选、可留空（见 `business-pattern-selection.md`）；但 `page_role` 应尽量给准，它是路由的第一层收窄。
