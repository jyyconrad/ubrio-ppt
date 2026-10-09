<!--
id: composition-diagnostic-insight-grid
category: composition-branch
read_when: 需要并列诊断 2-4 个问题，并对每个问题给出现象、根因、方案和管理洞察
page_roles: content, summary
supports: svg_drawingml
outputs: diagnostic_grid_spec, semantic_row_schema, svg_group_plan
depends_on: composition-business-report-argument-cascade.md
relation_specs: requires:composition-business-report-argument-cascade, requires:template-series-composite-builder, pairs_with:layout-problem-improve-bilateral, pairs_with:layout-problem-improve-value-rail, pairs_with:svg-shape-patterns
max_use: 只用于共享诊断 schema 的问题组；问题结构不同或条数不等时切非对称双面板
-->

# Composition Branch: Diagnostic Insight Grid

## 输入与选择

`issues[2..4]{title, symptoms[1..3], causes[1..3], responses[1..3], insight, evidence?}`

- 问题共享相同字段，选 1×2、1+2 或 2×2 diagnostic grid。
- 问题和措施一一对应，配 `layout-problem-improve-bilateral`。
- 两域条数不等、内部结构不同，配 `layout-problem-improve-value-rail`。

## 装配

每个问题固定：`issue-header → symptom-row → cause-row → response-row → insight-rail`。

语义行用 `svg-shape-patterns.md` 的 `semantic-row-stack`；Insight 只翻译本卡证据，不新增事实。

## 组合示例

输入：“四个协同卡点，每个卡点分别写表层现象、深层根因、应对方案和一句管理判断。”

输出：`diagnostic-grid-2x2`；四卡共享三行 schema，方案 tone 统一，右侧使用窄 insight rail。

## 容量与失败

- 一页 2-4 个问题；单槽 1-3 条；Insight ≤2 行。
- 症状与根因混写、方案不对应根因、为了凑四卡虚构问题、标签列宽漂移，均需重构。
