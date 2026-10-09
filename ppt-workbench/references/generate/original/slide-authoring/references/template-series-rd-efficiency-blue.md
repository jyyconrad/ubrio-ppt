<!--
id: template-series-rd-efficiency-blue
category: template-series
read_when: 需要复用汇报模板 p1-p15 的浅底蓝白高密业务汇报系列，强调结论、机制、证据、洞察和结果闭环时
page_roles: content, summary
supports: svg_drawingml
outputs: series_visual_contract, page_archetype_menu, shape_composition_grammar, composite_resource_plan
depends_on: composition-business-report-argument-cascade.md, template-series-composite-builder.md
relation_specs: requires:composition-business-report-argument-cascade, requires:template-series-composite-builder, pairs_with:composition-metric-system-with-case, pairs_with:composition-stage-mechanism-scorecard, pairs_with:composition-diagnostic-insight-grid, pairs_with:theme-light-business-blue, pairs_with:svg-shape-patterns
max_use: 作为整册主系列；不能把具体研发业务数字、Logo、水印和截图坐标写入新页面
source_notice: 来源为汇报模板-p1 至 p15 的 visual-only 截图；可证明可见视觉与组合关系，不能证明母版、对象类型或编辑性。
-->

# 汇报模板系列：浅底蓝白研发效能业务汇报

## 系列视觉逻辑

- 白底或极浅灰底，深蓝负责标题、结构锚、关键数字和最终判断；浅蓝负责证据面与解释层。
- 页面不是一组装饰卡，而是 2-3 条纵向分带：框架/机制在上，证据/案例在中下，洞察或行动收口。
- 全册密度高但层级清楚：一个强标题、一个主关系、一个结果出口；同页机制与结果互相回指。
- 章节节奏建议 `Why → Diagnosis → What → How → Proof → Closure`，问题页和蓝图页之间穿插案例/指标证明。
- 颜色深浅只在单页内保持语义一致，不全局宣称“越深越高级”。

## 页面展示系统

| 页面任务 | 展示骨架 | 主要证据页 |
|---|---|---|
| 价值总纲 | 3 段价值递进 + 趋势卡 + 深色结论带 | p1 |
| 组织机制 | 三角协作核心 + 2×3 支撑矩阵 + 原则条 | p2 |
| 阶段路线 | 顶部轨道 + 共享 row schema 的阶段矩阵 | p3 |
| 案例成效 | 基线 → 举措 → KPI → 经验 | p4、p11 |
| 问题诊断 | 2×2 问题网格，每格现象/根因/方案/洞察 | p5 |
| 指标与案例 | 指标定义矩阵 + 结果卡/案例链 | p6-p8、p10 |
| 架构价值 | 层级/平台结构 + 共性能力 + 价值结果 | p9、p12 |
| 门径治理 | 阶段流程 + 为什么有效 + 结果 scorecard | p13 |
| 转型 Why | 外部压力 + 内部瓶颈 + 定位结论 | p14 |
| 体系蓝图 | 北极星 + 双轮 + 分层能力 + 横向协同 + 价值 | p15 |

同一 deck 不要求每页保持相同卡片数；稳定的是标题层级、蓝白色角色、分带节奏、洞察出口和来源槽。

## 形状组合语法

- `阶段轨道 = line/arrow + circular badge + aligned stage column`。
- `语义矩阵 = section tab + repeated semantic row stack + shared row heights`。
- `案例证明 = intervention chain + metric delta cards + conclusion band`。
- `问题诊断 = issue header + symptom/cause/response rows + insight rail`。
- `架构价值 = hierarchy/source topology + common capability rail + value scorecard`。
- `门径治理 = chevron flow + 1-2 mechanism panels + 2-4 result cards`。
- `体系蓝图 = north-star roof + two enablers + 3-5 layers + collaboration rail + value strip`。
- 真实柱线饼图和逐格表格由 native slot 承载；SVG 只画组合框架、文字、关系和 slot。

## 快速组合示例

| 用户意图 | 系列组件 | 资源输入重点 |
|---|---|---|
| “三阶段推进，每阶段写目标、动作、产出和风险” | `phased_roadmap_matrix` | `stages[2..4]` 共享四行 schema |
| “四个卡点逐一分析并给洞察” | `diagnostic_insight_grid` | `issues[2..4]`，每格四个语义槽 |
| “一库支撑三平台并证明价值” | `shared_source_platform_value` | 共享源、平台、共性能力、价值结果 |
| “七个门径，解释为什么有效并给三项结果” | `stage_mechanism_scorecard` | 3-7 阶段、1-2 机制、2-4 指标 |
| “一核两翼四层加横向协同” | `operating_model_blueprint` | 北极星、双轮、3-5 层、协同、价值 |

优先选择 `build-series-composite-svg` 物化资源；需要独立预检时再使用
`validate-series-composite-svg-spec`。复用时保持系列与 pattern，只替换 `data`；标题数字必须能在同页
证据中按同口径回指。具体资源执行入口由当前 consumer 决定，不在本系列中写死。

## 容量与失败

- 阶段矩阵 2-4 列；门径流程 3-7 步；问题网格 2-4 格；架构平台 2-4 个；能力层级 3-5 层。
- 三列每列 2-3 行，四列每列不超过 2 行；五至七段只保留短标题和一个解释槽。
- 失败：只有流程没有结果、只有架构没有价值、洞察引入新事实、目标冒充实际结果、为对称虚构条目。
- 超量先删重复、转移来源或拆页，不缩小字号维持截图外观。
