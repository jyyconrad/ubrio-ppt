# 模板系列复杂组合组件示例

本目录保存 `series_composite_svg/v1` 的可替换 JSON 输入和由
`build-series-composite-svg` 生成的 SVG。每个 SVG 只承载调用方 `region` 内的一类复杂组合形状，不是整页 PPT；不含页面背景、action title、页眉页脚、照片或手绘的真实图表/逐格表格。需要原生 chart/table 的示例另带 `native-data.json`。

复用时优先保留 `series_id`、`pattern` 和 `region`，只替换 `title` 与 `data`。内容超出组件容量时应拆页或改用 native chart/table/image slot，不得缩小字号硬塞。

| 编号 | pattern | 主要展示逻辑 |
|---|---|---|
| 01 | `phased_roadmap_matrix` | 阶段方向轨 + 共享行矩阵 |
| 02 | `diagnostic_insight_grid` | 问题网格 + 现象/根因/方案/洞察 |
| 03 | `shared_source_platform_value` | 共享源 → 平台群 → 共性能力 → 价值 |
| 04 | `stage_mechanism_scorecard` | 门径流程 → 机制解释 → 结果指标 |
| 05 | `operating_model_blueprint` | North-star + 双轮 + 分层能力 + 协同 + 价值 |
| 06 | `retrospect_outlook_pyramid` | 回顾—成果—展望 + 三层金字塔 |
| 07 | `duotone_problem_improve` | 蓝绿/紫色双侧问题改进 + 中心转化 |
| 08 | `calendar_summary_rail` | 月份刻度 + 跨月事件 + 总结侧栏 |
| 09 | `target_action_timeline` | 目标—行动—验收的月度时间线 |
| 10 | `north_star_kpi_roof` | North-star 屋顶 + 管理语义条 + KPI |
| 11 | `arrow_ribbon_metrics` | 连续成果箭头带 + 指标证据 |
| 12 | `highlight_matrix_core` | 四角证据 + 中央四主题汇聚 |
| 13 | `sectioned_evidence_dashboard` | 历史编排 benchmark；展示多卡与流程如何同页协作，不作为新页面的原子组件首选 |
| 14 | `chart_insight_card` | 单张图表/表格 + 高亮结论 + 洞察卡 |
| 15 | `full_width_rect_step_flow` | 横向满 region 的矩形步骤流程 + 可选行动块 |
| 16 | `native_chart_panel` | 主体折线/柱状原生图表面板 + 来源 |
| 17 | `insight_text_card` | 图表侧栏的结论/原因/风险/行动文字卡 |

新页面需要复现第 13 组观感时，由上层模板系列和 assembly 分配多个 region，分别生成
`chart_insight_card × N` 与 `full_width_rect_step_flow × 1`，不要直接把整页内容塞进单个 pattern。
“左侧主图 + 右侧说明卡”由上层 assembly 组合 `native_chart_panel × 1` 与
`insight_text_card × 2..3`，不要把主图压进微图卡。
