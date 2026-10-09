<!--
id: template-series-composite-builder
category: shape-component-library
read_when: 已由模板系列确定整页外围视觉，需要只替换内容或提供基础数据就快速生成某一类局部复杂组合形状时
page_roles: content, summary
supports: svg_drawingml
outputs: series_composite_spec, grouped_editable_svg, stable_group_ids, capacity_errors
depends_on: drawingml-svg-authoring.md, contract-visual-token-core.md, contract-content-density.md
relation_specs: requires:drawingml-svg-authoring, requires:contract-visual-token-core, requires:contract-content-density, pairs_with:composition-business-report-argument-cascade, conflicts_with:anti-pattern-fixed-template-monotony
max_use: 一次调用只生成一个 region-local pattern；真实图表、逐格表格、照片和证据截图必须走 native slot 或受控图片
source_notice: 组件来自 docs/03-architecture/ppt模板 的 visual-only 截图系列；只保留参数化几何和视觉语法，不保存源坐标、品牌色、Logo、水印、业务数据或可编辑性推断。
-->

# Template Series Composite Builder

## 目标与边界

本 reference 负责模板系列之下的组件层能力：把已经选定的视觉系列和局部关系转换为复杂、分组、
可编辑的 SVG 组合组件；涉及原生图表/表格时同时生成 `native-data.json` sidecar。它不生成整页 PPT，也不复制整页模板截图。

- 论证分支决定页面证明什么。
- `template-series-*` 决定整册视觉节奏、页面外围、页面菜单和形状语言。
- 本 builder 计算组件内部的比例、列数、跨度、连接、对齐与稳定 group ID。
- 框架层仍负责整页背景、action title、页眉、页脚和页码；builder 只画调用方给定的 `region`。
- 1280×720 只是统一验证画布；真正复用边界是 `region{x,y,w,h}`，输出根组固定标记 `data-component-scope="content-region"`。
- 一个 pattern 只表示一类复杂组合形状。多种组件同页出现时分别生成，再由上层 layout/assembly 放入不同 region。
- 真实柱线饼图、Gantt、逐格表格和截图证据不由本 builder 手绘。

## 系列路由

| `series_id` | 对应系列 | 主要视觉逻辑 | 优先 pattern |
|---|---|---|---|
| `rd_efficiency_blue` | 汇报模板 p1-p15 + 分区证据仪表板补充截图 | 浅底蓝白、高密分带、机制与结果同页 | `phased_roadmap_matrix`、`diagnostic_insight_grid`、`shared_source_platform_value`、`stage_mechanism_scorecard`、`operating_model_blueprint`、`native_chart_panel`、`insight_text_card`、`chart_insight_card`、`full_width_rect_step_flow` |
| `blue_summary_pyramid` | ppt1 | 蓝白递进、回顾成果展望、上升与层级 | `retrospect_outlook_pyramid` |
| `blue_green_diagnostic` | ppt2 | 蓝绿双语义域、问题到改进、对照与转化 | `duotone_problem_improve` |
| `violet_quarterly_overview` | ppt3 | 紫色经营总览、KPI 与季度/月度组织 | `calendar_summary_rail`、`north_star_kpi_roof`、`arrow_ribbon_metrics`、`highlight_matrix_core` |
| `violet_calendar` | ppt4 | 月份跨度事实区 + 管理总结侧栏 | `calendar_summary_rail` |
| `violet_planning_5w1h` | ppt5 | 目标、行动、评估沿月份展开 | `target_action_timeline`；复杂 Gantt 改 native table/专用 overlay |
| `violet_improvement` | ppt6 | 紫色双侧问题改进与中心转化锚 | `duotone_problem_improve` |
| `violet_performance` | ppt7 | North-star、管理语义条、KPI 与目标达成 | `north_star_kpi_roof` |
| `violet_achievements` | ppt8 | 连续成果方向带、四主题中心簇 | `arrow_ribbon_metrics`、`highlight_matrix_core` |

一套 deck 只选择一个系列作为主视觉基准。可以复用其它系列的局部结构，但必须重绘为当前系列的
颜色、线条、圆角、密度和强调规则，不能把蓝绿撞色页直接插进紫色 deck。

## Pattern 合同

| `pattern` | 核心数据槽 | 容量 | 页面展示与形状组合 |
|---|---|---|---|
| `phased_roadmap_matrix` | `stages[]{label,window,goal,actions,outputs,risk}` | 2-4 阶段 | 顶部方向轨 + 圆节点 + 共享行 schema 的阶段矩阵 |
| `diagnostic_insight_grid` | `issues[]{title,symptoms,causes,responses,insight}` | 2-4 问题 | 2×2 诊断网格 + 三行语义栈 + 窄洞察 rail |
| `shared_source_platform_value` | `source,platforms,common_capabilities,values` | 2-4 平台、2-4 价值 | 共享源 → 平台群 → 共性能力条 → 结果卡 |
| `stage_mechanism_scorecard` | `stages,mechanisms,metrics` | 3-7、1-2、2-4 | chevron 阶段带 → 机制解释双栏 → 结果 scorecard |
| `operating_model_blueprint` | `north_star,enablers,layers,collaborations,values` | 1、2、3-5、1-2、3-5 | 屋顶目标 + 双轮 + 分层能力 + 横向协同 + 价值带 |
| `retrospect_outlook_pyramid` | `periods[3],pyramid_layers[3],conclusion` | 恰三时段/三层 | 回顾—成果—展望三栏，中央金字塔和底部结论带 |
| `duotone_problem_improve` | `problems,responses,center_label` | 两侧各 2-4 | 双语义色侧栏 + 相交双圆 + 成对编号锚 |
| `calendar_summary_rail` | `months,events{start,end},summaries` | 3-6 月、1-8 事件、1-3 总结 | 月份网格 + 按跨度计算的事件卡 + 右侧总结 rail |
| `target_action_timeline` | `periods[]{label,goal,actions,result,emphasis?}` | 4-6 期 | 顶部月份箭头轴 + 圆节点 + 目标/行动/评估卡 |
| `north_star_kpi_roof` | `north_star,subtitle,principles[3],metrics,conclusion` | 3-5 KPI | 屋顶 North-star + 三段管理条 + 折角 KPI + 结论带 |
| `arrow_ribbon_metrics` | `items[]{title,detail,metric_label,metric_value}` | 3-6 段 | chevron 成果方向带 + 说明锚线 + 底部单指标卡 |
| `highlight_matrix_core` | `items[4],core_labels[4]` | 恰四组 | 四角证据卡 + 中央 2×2 圆簇，连接关系保持正交 |
| `native_chart_panel` | `chart{slot_id,title,kind,labels,series,value_format?,data_unit?,source}` | 1 个 bar/line 主图，2-12 类目，1-3 系列 | 图表小标题 + 大尺寸原生 chart slot + 来源；图表数据自动生成 native sidecar |
| `insight_text_card` | `card{title,tone,metric?,bullets[1..3],footer?}` | 恰 1 张文字卡 | 单一语义强调边 + 标题 + 可选回指指标 + 1-3 条证据说明 |
| `chart_insight_card` | `card{title,highlight,meaning,visual,insight}` | 恰 1 卡、1 证据介质 | 编号/图标 + 高亮结论 + 原生微图/微表或事实 + 洞察页脚 |
| `full_width_rect_step_flow` | `title,steps[],action?` | 3-6 步、可选 1 个行动块 | 横向关系带 + 等宽矩形步骤 + 明确箭头 + 可选末端收口 |
| `sectioned_evidence_dashboard` | `sections[].cards[],closure?` | 兼容 benchmark | 仅保留为历史编排示例；新页面应分别组合 `chart_insight_card` 与 `full_width_rect_step_flow`，不把它当原子组件 |

## 输入合同

```json
{
  "schema_version": "series_composite_svg/v1",
  "series_id": "rd_efficiency_blue",
  "pattern": "stage_mechanism_scorecard",
  "region": {"x": 72, "y": 112, "w": 1136, "h": 520},
  "title": "六阶段门径把等待与返工前置收敛",
  "data": {
    "stages": [
      {"title": "需求澄清", "detail": "冻结关键口径"},
      {"title": "概念评审", "detail": "验证技术路线"},
      {"title": "方案确认", "detail": "同步成本与质量"}
    ],
    "mechanisms": [
      {"title": "并行工程", "detail": "让可并行任务提前启动"}
    ],
    "metrics": [
      {"metric_label": "交付周期", "metric_value": "-28%", "detail": "同口径项目"},
      {"metric_label": "延期率", "metric_value": "-11pp", "detail": "季度均值"}
    ]
  }
}
```

复用时保持 `series_id + pattern + region`，只替换 data 和可选组件标题。这里的 `title` 是组件内部标题，
不是页面 action title。需要改变颜色时优先换 `series_id`；只有当前 deck 已确认视觉 token 时，才在
`theme` 中覆盖同名 token。

## 声明资源

1. `validate-series-composite-svg-spec` 是可选的独立预检资源，接收 spec 并输出 normalized spec。
2. `build-series-composite-svg` 是物化资源，接收同一 spec，内部仍会执行 schema、容量与区域校验，输出 SVG、可选 `native-data.json` 和 normalized spec；因此代码侧执行器只选择 build 资源也不会跳过输入校验。
3. 两个资源 ID 由 Skill Graph snapshot 和当前 consumer 的资源合同绑定；Skill reference 不假定具体工具名、调用顺序或模型可见执行面。模型只提交结构化内容，资源选择、sandbox 路径、执行、校验与写回由当前运行时完成。
4. 输出 SVG 中根组固定为 `series-composite` 并带 `data-component-scope="content-region"`，pattern 根组固定为 `pattern-<pattern>`；子组使用 `stage-*`、`issue-*`、`metric-*`、`period-*` 等稳定 ID，便于后续替换或检查。
5. 模型不能读取或复制脚本源码，也不能传脚本路径、shell、argv、解释器或环境变量。

## 离线示例与 benchmark

示例目录为 `assets/examples/svg-ppt/decks/template-series-composite-library/`，仅供离线 benchmark、
fixture 和人工结构检查。运行时模型不读取示例目录，也不调用示例加载工具；它只按当前
`PageMethodContract` 选择 `component_id`、填写 `builder_spec`，并提交一次 `execute_page`。

| pattern | 可替换 JSON | 生成 SVG |
|---|---|---|
| `phased_roadmap_matrix` | `assets/examples/svg-ppt/decks/template-series-composite-library/01-phased-roadmap-matrix.json` | `assets/examples/svg-ppt/decks/template-series-composite-library/01-phased-roadmap-matrix.svg` |
| `diagnostic_insight_grid` | `assets/examples/svg-ppt/decks/template-series-composite-library/02-diagnostic-insight-grid.json` | `assets/examples/svg-ppt/decks/template-series-composite-library/02-diagnostic-insight-grid.svg` |
| `shared_source_platform_value` | `assets/examples/svg-ppt/decks/template-series-composite-library/03-shared-source-platform-value.json` | `assets/examples/svg-ppt/decks/template-series-composite-library/03-shared-source-platform-value.svg` |
| `stage_mechanism_scorecard` | `assets/examples/svg-ppt/decks/template-series-composite-library/04-stage-mechanism-scorecard.json` | `assets/examples/svg-ppt/decks/template-series-composite-library/04-stage-mechanism-scorecard.svg` |
| `operating_model_blueprint` | `assets/examples/svg-ppt/decks/template-series-composite-library/05-operating-model-blueprint.json` | `assets/examples/svg-ppt/decks/template-series-composite-library/05-operating-model-blueprint.svg` |
| `retrospect_outlook_pyramid` | `assets/examples/svg-ppt/decks/template-series-composite-library/06-retrospect-outlook-pyramid.json` | `assets/examples/svg-ppt/decks/template-series-composite-library/06-retrospect-outlook-pyramid.svg` |
| `duotone_problem_improve` | `assets/examples/svg-ppt/decks/template-series-composite-library/07-duotone-problem-improve.json` | `assets/examples/svg-ppt/decks/template-series-composite-library/07-duotone-problem-improve.svg` |
| `calendar_summary_rail` | `assets/examples/svg-ppt/decks/template-series-composite-library/08-calendar-summary-rail.json` | `assets/examples/svg-ppt/decks/template-series-composite-library/08-calendar-summary-rail.svg` |
| `target_action_timeline` | `assets/examples/svg-ppt/decks/template-series-composite-library/09-target-action-timeline.json` | `assets/examples/svg-ppt/decks/template-series-composite-library/09-target-action-timeline.svg` |
| `north_star_kpi_roof` | `assets/examples/svg-ppt/decks/template-series-composite-library/10-north-star-kpi-roof.json` | `assets/examples/svg-ppt/decks/template-series-composite-library/10-north-star-kpi-roof.svg` |
| `arrow_ribbon_metrics` | `assets/examples/svg-ppt/decks/template-series-composite-library/11-arrow-ribbon-metrics.json` | `assets/examples/svg-ppt/decks/template-series-composite-library/11-arrow-ribbon-metrics.svg` |
| `highlight_matrix_core` | `assets/examples/svg-ppt/decks/template-series-composite-library/12-highlight-matrix-core.json` | `assets/examples/svg-ppt/decks/template-series-composite-library/12-highlight-matrix-core.svg` |
| `sectioned_evidence_dashboard` | `assets/examples/svg-ppt/decks/template-series-composite-library/13-sectioned-evidence-dashboard.json` | `assets/examples/svg-ppt/decks/template-series-composite-library/13-sectioned-evidence-dashboard.svg` |
| `chart_insight_card` | `assets/examples/svg-ppt/decks/template-series-composite-library/14-chart-insight-card.json` | `assets/examples/svg-ppt/decks/template-series-composite-library/14-chart-insight-card.svg` |
| `full_width_rect_step_flow` | `assets/examples/svg-ppt/decks/template-series-composite-library/15-full-width-rect-step-flow.json` | `assets/examples/svg-ppt/decks/template-series-composite-library/15-full-width-rect-step-flow.svg` |
| `native_chart_panel` | `assets/examples/svg-ppt/decks/template-series-composite-library/16-native-chart-panel.json` | `assets/examples/svg-ppt/decks/template-series-composite-library/16-native-chart-panel.svg` |
| `insight_text_card` | `assets/examples/svg-ppt/decks/template-series-composite-library/17-insight-text-card.json` | `assets/examples/svg-ppt/decks/template-series-composite-library/17-insight-text-card.svg` |

第 13 组是历史整块编排 benchmark，用来证明多个组件如何同页协作，不再作为新页面的原子 pattern 首选。
第 14 组另带 `14-chart-insight-card.native-data.json`。这些 SVG 中的
`data-preview-only="true"` 微图/微表只服务人工预览，转换前会被确定性移除；真实 Office chart/table 按稳定
`slot_id` 从 sidecar 覆盖。`contact-sheet.png` 只用于人工视觉验收，不作为可编辑结构真源；JSON 是输入真源，SVG 与 native-data 是生成结果。

## 视觉与编辑性检查

- 同级模块使用同一颜色角色；颜色表达语义，不逐卡随机换色。
- 数字、标题、结构锚和结论有清晰权重，正文不与 hero 数争夺注意力。
- 关系几何必须真实：事件跨度来自 `start/end`，阶段数来自数据，双侧结构来自 problem/response。
- `native_chart_panel` 只承载一张主体 bar/line 图，`insight_text_card` 只翻译同页证据；`chart_insight_card` 必须保持 `子观点 → 单一证据 → 洞察`；`full_width_rect_step_flow` 只表达一条顺序、因果或流转关系。
- 需要“六卡 + 底部流程”时，上层先分配 7 个 region，再分别生成 6 张卡和 1 条流程；不让任一组件生成页面外围。
- 输出不得含 `<script>`、`foreignObject`、`use/symbol`、整页背景或位图。
- 数据超容量时 builder 直接失败；不要通过缩小字号把 7 段塞进 6 段组件。
- SVG 生成后仍需经过 `validate_svg_drawingml` 和真实渲染预览。

## 停止条件

- 页面需要真实趋势、精确比例、日级 Gantt、逐格责任表或证据截图。
- 业务内容不符合 pattern 的关系语义，只是外观相似。
- 当前系列视觉逻辑尚未确定，或跨系列颜色语义发生冲突。
- 组件需要超过合同容量，且无法删除重复内容或拆页。
