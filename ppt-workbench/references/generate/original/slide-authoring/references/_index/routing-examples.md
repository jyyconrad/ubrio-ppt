<!--
id: routing-examples
category: routing-index
read_when: route_skill_references 工具不可用, 或需要快速人工对照常见问题与 reference
page_roles: content, section_divider, summary
supports: svg_drawingml
outputs: reference_selection
depends_on: _index/capability-tree.json
max_use: 作为语义筛选工具的人工兜底; 工具可用时优先用工具而非本表
-->

# Routing Examples（路由兜底映射）

正常态先用 `search_knowledge_base` 聚焦检索，再用 `load_skill_references` 装配必要颗粒；
`route_skill_references` 和本文件都是降级兜底或人工调试入口。映射与
`_index/capability-tree.json` 的 `triggers` 同源，新增 reference 时以能力树为准，本表只做
常见高频问题的固定对照。

每次都先读 `drawingml-svg-authoring.md`（always_read），再叠加下表推荐。

## 按页型

| 页型 | 推荐起点 |
| --- | --- |
| 封面 / cover | `layout-fixed-cover-agenda.md`；文学纪录片深色影像封面加 `layout-dark-photo-interlude.md` |
| 目录 / agenda / toc | `layout-fixed-cover-agenda.md` |
| 2-4 项简单介绍 / introduction | `layout-fixed-cover-agenda.md`；超出容量或需要图表/复杂证据时回到正文页 |
| 默认正文页 | `contract-gold-svg-builder.md` + `contract-structure-hierarchy.md` |
| 章节 / 过渡页 | `layout-section-divider.md` + 一个 `theme-*` |
| 总结 / 行动页 | `layout-summary-action-matrix.md` + `content-pyramid-claim-evidence-action.md` |
| 读书分享 / 文学纪录片叙事 | `scenario-book-deep-analysis.md` + `style-literary-documentary-cn.md` + 一个 editorial layout |
| 课堂宣讲 / 科普 / 公开课 | `scenario-educational-pop-science.md` + `scenario-background-image-premium.md` + `image-sourcing-commercial-or-generated.md` |
| 景点宣传 / 文旅城市推介 / 场馆产品展示 | `scenario-public-image-visual-assets.md` + `image-sourcing-commercial-or-generated.md` + `theme-background-policy.md` |

## 按问题（P0 阻塞优先）

| 当前页问题 | 推荐 reference | 优先级 |
| --- | --- | --- |
| 不知道 SVG 页从哪开始 | `contract-svg-page-workflow.md` + `contract-gold-svg-builder.md` | P0 |
| 深色背景黑字 / 文字看不清 / 低对比 | `anti-pattern-dark-background-black-text.md` + `contract-visual-token.md` + 对应深色 `theme-*` | P0 |
| 紫色系列 / 单一色系导致整页同色、图表文字看不清 | `contract-visual-token.md` + `layout-native-chart-slot.md`（有图表时） | P0 |
| 汇报页并列模块逐卡换色 / 每个模块一种颜色 / 彩虹卡片 | `anti-pattern-rainbow-parallel-modules.md` + `contract-visual-token.md` | P0 |
| 元素越界 / 重叠 / 第四卡超出画布 | `anti-pattern-layout-overflow.md` + `contract-layout-density.md` | P0 |
| 渲染前自检 | `contract-svg-self-qa.md` | P0 |
| 内容过简 / 只有标题或泛标签 | `contract-content-density.md` + `content-pyramid-claim-evidence-action.md` | P1 |
| 标题是名词 / 口号，需改判断句 | `content-title-rewriting.md` | P1 |
| 主体空白 / 章节号抢主标题 | `contract-layout-density.md` + `anti-pattern-chapter-marker-dominates.md` | P1 |
| 多页都像同一种三卡 / 四卡模板 | `gold-structure-composition.md` + `anti-pattern-fixed-template-monotony.md` | P1 |
| 卡片大片空白 / 只有一行说明 | `anti-pattern-empty-cards.md` + `contract-content-density.md` | P1 |
| 缺数据 / 缺案例 / 缺来源 | `content-evidence-gap-labeling.md` | P2 |
| 读书分享页被写成业务指标/行动台账 | `anti-pattern-over-businessified-literary-slides.md` + `content-literary-documentary-narrative.md` | P0 |
| 图片背景/书封/人物图需要可商用或生图策略 | `image-sourcing-commercial-or-generated.md` | P0 |
| 公共图片、景点、场馆、产品、人物或案例图提升视觉效果 | `scenario-public-image-visual-assets.md` + `image-sourcing-commercial-or-generated.md` | P0 |
| 判断哪些 PPT/页型加背景图更高级 | `scenario-background-image-premium.md` + `theme-background-policy.md` | P0 |
| 用户上传图片 / 上传文件剥离图片需要嵌入正文局部 | `image-sourcing-commercial-or-generated.md` + `layout-native-image-slot.md` | P0 |
| 深色影像封面 / 章节 / 收尾页需要固定槽位 | `layout-dark-photo-interlude.md` + `layout-fixed-cover-agenda.md` | P0 |

## 按结构 / 布局

| 内容形态 | 推荐 layout |
| --- | --- |
| 一个主判断 + 2-4 条证据 | `layout-left-claim-right-evidence.md` |
| 三个信息组 + 底部收口 | `layout-three-cards-action-bar.md` |
| 四项机制 / 策略 / 能力 | `layout-four-cards-grid.md` |
| 问题-方案-收益 / 前后因果 | `layout-problem-solution-benefit.md` |
| 实施路径 / 责任链路 / 闭环机制 / 审批流转 / 端到端 | `layout-process-flow.md` |
| 金字塔 / 分层 / 优先级递进 | `layout-pyramid-hierarchy.md` |
| 里程碑 / 阶段 / 发展历程 | `layout-timeline-horizontal.md` |
| 循环 / 闭环 / PDCA / 飞轮 | `layout-cycle-loop.md` |
| SWOT / 四象限 / 象限图 / 二维定位 / 2x2 positioning matrix / 竞品或方案定位 | `layout-matrix-quadrant.md`（SWOT/3C/PEST 再加 `content-swot-3c-pest.md`） |
| 中心目标 + 卫星模块 | `layout-center-radial.md` |
| 截图证明 / 系统记录 | `layout-screenshot-proof.md` |
| 柱线饼等原生图表 / 逐单元格表格 / 对比表 | `layout-native-chart-slot.md` |
| 用户图片 / 书封 / 人物 / 证据图作为正文局部图片 | `layout-native-image-slot.md` |
| 景点 / 场馆 / 产品 / 人物 / 案例公共图片图文页 | `scenario-public-image-visual-assets.md` + `layout-editorial-image-panel.md` 或普通 picture binding |
| 文学正文左文右图 / 左图右文 | `layout-editorial-image-panel.md` |
| 文学主题两个并列观点 | `layout-story-cards-two-up.md` |
| 文学主题三段递进 / 三栏叙事 | `layout-story-cards-three-up.md` |
| 书籍 / 作者 / 人物对比 + 金句 | `layout-book-compare-quote.md` |
| 深色影像封面 / 章节 / 收尾页 | `layout-dark-photo-interlude.md` |
| 多段板块成果串成方向性箭头陈列带(每段自带成果巨数) | `layout-arrow-ribbon-metrics.md` |
| 按月/季分期三栏落地举措清单(房形期次表头) | `layout-phased-action-columns.md` |
| 左侧深色 hero 巨数统领 + 右侧 2-4 指标块(可含环形 gauge) | `layout-hero-metric-left-rail.md` |
| 回顾-成果-展望三时段叙事 + 中央递进金字塔串联 | `layout-retrospect-outlook-pyramid.md` |
| 单独一张指标/证据卡，组合高亮数字、微图/微表、短解释和洞察 | `layout-chart-insight-card.md` + `layout-native-chart-slot.md` |
| 一条横向满宽的 3-6 步矩形流程、根因链或整改闭环 | `layout-full-width-rect-step-flow.md` |
| 1-2 个大分区内嵌 3-6 张指标卡，底部再放流程 | `layout-sectioned-evidence-dashboard.md` 只做编排；分别生成 `chart_insight_card` 与 `full_width_rect_step_flow` |

## 按模板系列与复杂形状组合

需要复用截图模板的完整观感时，先选一个 `template-series-*` 作为整册与整页外围视觉基准，再选一个
composition branch 决定当前页证明什么，最后选择一个或多个 region-local pattern 落位。系列不是配色
标签：它同时约束跨页节奏、页型菜单、信息密度、强调方式、形状关系和收口位置；组件只负责自己的内容区。

### 系列选择

| 用户可能会说 | 系列节点 | 页面展示与形状语言 | 快速组合起点 |
| --- | --- | --- | --- |
| “按这组汇报模板做一套高密蓝白业务汇报，既讲问题、体系和路线，也要用案例和结果证明” | `template-series-rd-efficiency-blue.md` | 2-3 条分带；深蓝结构锚；机制与结果同页；Why→Diagnosis→What→How→Proof→Closure | `phased_roadmap_matrix` / `diagnostic_insight_grid` / `shared_source_platform_value` / `stage_mechanism_scorecard` / `operating_model_blueprint` |
| “按 ppt1 的蓝白上升感做半年复盘，回顾、成果、计划要一眼看懂” | `template-series-blue-summary-pyramid.md` | 回顾-成果-展望三栏、递进金字塔、阶梯、成长轨迹；每页一个主视觉关系 | `retrospect_outlook_pyramid` |
| “按 ppt2 做蓝绿问题改进汇报，左边讲短板，右边讲整改，颜色要有稳定语义” | `template-series-blue-green-diagnostic.md` | 蓝绿双语义域；镜像/非对称双面板；U 形箭头、相交圆和中心转化锚 | `duotone_problem_improve` |
| “按 ppt3 做紫色季度、半年、年度经营总览，要能混合 KPI、月份、成果和年度目标” | `template-series-violet-quarterly-overview.md` | KPI strip + 月份/季度主体 + 右侧或底部总结；屋顶、箭头带、四主题中心簇 | `calendar_summary_rail` / `north_star_kpi_roof` / `arrow_ribbon_metrics` / `highlight_matrix_core` |
| “按 ppt4 只做季度三栏和半年跨月事件，不要扩成整套紫色大系列” | `template-series-violet-calendar.md` | 月份为第一分组；事件卡按起止月份计算跨度；右侧总结 rail | `calendar_summary_rail` |
| “按 ppt5 做目标、行动、评估的月度计划和 5W1H 页面” | `template-series-violet-planning-5w1h.md` | 月份箭头轴 + 目标/行动/验收卡；策略分解后以行动矩阵收口 | `target_action_timeline` |
| “按 ppt6 做不足与改进的一一对应页，中心突出从问题到行动” | `template-series-violet-improvement.md` | 双侧语义列 + 中心转化锚 + 底部原则/行动带 | `duotone_problem_improve` |
| “按 ppt7 做年度绩效和目标达成总览，最上面要有 North-star” | `template-series-violet-performance.md` | North-star 屋顶 + 三段管理语义条 + 3-5 KPI + 结论带 | `north_star_kpi_roof` |
| “按 ppt8 做成果陈列，既能连续推进，也能按四主题汇聚” | `template-series-violet-achievements.md` | 连续 chevron 成果带或四角证据 + 中央 2×2 圆簇 | `arrow_ribbon_metrics` / `highlight_matrix_core` |

### 复杂组合组件

以下 pattern 均由 `template-series-composite-builder.md` 定义。选择
`build-series-composite-svg` 物化时会同时执行 schema、区域和容量校验；只有需要在物化前单独检查或
归一化输入时，才选择 `validate-series-composite-svg-spec`。具体执行入口和资源顺序由当前 consumer
负责，模型只提交结构化 spec。复用时保留 `series_id + pattern + region`，只替换 `data` 和可选组件标题；
页面 action title 与外围视觉不在组件 spec 内。

| 用户可能会说 | pattern | 视觉逻辑与关键形状 | 输入容量 |
| --- | --- | --- | --- |
| “三阶段路线，每阶段都按目标、动作、产出、风险展示” | `phased_roadmap_matrix` | 顶部方向轨 + 圆形阶段节点 + 共享 row schema 矩阵 | 2-4 阶段 |
| “四个问题都拆成现象、根因、方案、洞察” | `diagnostic_insight_grid` | 2×2 诊断网格 + 三行语义栈 + 洞察 rail | 2-4 问题 |
| “一个共享资源库支撑三个平台，再落到共性能力和业务价值” | `shared_source_platform_value` | 共享源 → 平台群 → 共性能力条 → 价值 scorecard | 2-4 平台、2-4 价值 |
| “六个门径阶段，下面解释两个机制，再给三个结果指标” | `stage_mechanism_scorecard` | chevron 阶段带 → 机制解释面板 → 结果卡 | 3-7 阶段、1-2 机制、2-4 指标 |
| “North-star、双轮、四层能力、两条协同和五项价值放成总蓝图” | `operating_model_blueprint` | 屋顶目标 + 双轮 + 层级 stack + 横向协同 + 价值带 | 双轮恰 2、3-5 层、1-2 协同、3-5 价值 |
| “左边回顾，中间三层成果金字塔，右边展望” | `retrospect_outlook_pyramid` | 三时段 frame + 中央金字塔 + 底部结论带 | 三时段、三层均恰 3 |
| “左边三项不足，右边三项改进，中间强调转化” | `duotone_problem_improve` | 双语义面板 + 相交双圆 + 成对编号锚 | 两侧各 2-4 项 |
| “7-12 月的项目按实际跨月宽度摆放，右边提炼三条总结” | `calendar_summary_rail` | 月份刻度 + event span card + 自动 lane + summary rail | 3-6 月、1-8 事件、1-3 总结 |
| “1-6 月每月给目标、动作和验收，重点月要突出” | `target_action_timeline` | 月份箭头轴 + 圆节点 + 目标/行动/验收卡 | 4-6 期 |
| “用屋顶突出年度关键指标，下面三条管理原则和五个 KPI” | `north_star_kpi_roof` | North-star roof + 三段语义条 + 折角 KPI + 结论 | 3 条原则、3-5 KPI |
| “六类成果串成一条向前推进的箭头带，每段带一个主指标” | `arrow_ribbon_metrics` | chevron ribbon + 说明锚线 + 指标卡 | 3-6 段 |
| “四类工作亮点放四角，中间汇聚成四个核心关键词” | `highlight_matrix_core` | 四角证据卡 + 中央 2×2 圆簇 + 正交连接 | 恰 4 组 |
| “单独做一张交付率卡片，突出 83%→90%，配季度柱图和一句洞察” | `chart_insight_card` | 子观点标题 → 唯一高亮值 → 原生微图/微表 → 洞察 footer | 恰 1 卡、1 个证据介质、1 个 native slot |
| “把现象、执行、流程、机制、根因横向排成矩形流程，最后接整改闭环” | `full_width_rect_step_flow` | 横向关系带 → 3-6 个等宽矩形步骤 → 箭头 → 可选行动块 | 3-6 步、可选 1 行动块 |
| “效率和质量分成两个大区，里面放六张指标小卡，底部做根因闭环” | 组件编排，不选单一 pattern | `template-series-*` 提供外围 → `chart_insight_card × 6` → `full_width_rect_step_flow × 1` | 上层分配 7 个 region；组件分别生成 |

选择纪律：真实柱线饼图、精确比例、日级 Gantt、逐格责任表和证据截图不交给该 SVG builder；
保留同一系列视觉语言，数据区改用 native chart/table/image slot。

## 按业务论证组合

模板系列已确定时，composition branch 只决定当前页的 proof goal 和论证主链，再配关系 layout 与必要
shape/chart 颗粒；没有指定系列时先按场景选择 theme/scenario。不要一次加载本表全部分支。

| 用户可能会说 | 主分支 | 推荐组合 | 预期 group plan 示例 |
| --- | --- | --- | --- |
| “把改造前基线、四项动作和结果写成一页案例，最后提炼经验” | `composition-case-impact-chain.md` | `layout-process-flow.md` + `layout-kpi-strip.md` + `svg-shape-patterns.md` | `context-baseline + flow-step-1..4 + metric-delta-1..4 + conclusion-band` |
| “四个卡点都按现象、根因、方案和一句洞察分析” | `composition-diagnostic-insight-grid.md` | `layout-problem-improve-bilateral.md` 或 `layout-problem-improve-value-rail.md` + `svg-shape-patterns.md` | `diagnostic-grid + semantic-row-stack + insight-rail` |
| “上面定义两套指标体系，下面用案例解释为什么指标改善” | `composition-metric-system-with-case.md` | `layout-sectioned-evidence-dashboard.md` 分配 region，组合 `layout-chart-insight-card.md` 与 `layout-full-width-rect-step-flow.md` | `chart-insight-card × N + rect-step-flow × 1` |
| “一库支撑三个平台，还要说明共性能力和业务价值” | `composition-architecture-value-proof.md` | `layout-process-flow.md` / `layout-pyramid-hierarchy.md` + `svg-shape-patterns.md` | `shared-source + platform-cards + capability-rail + value-proof` |
| “展示六个门径阶段，解释为什么有效，再给三项结果” | `composition-stage-mechanism-scorecard.md` | `layout-process-flow.md` + `layout-native-chart-slot.md` | `process-flow-6 + mechanism-proof-2up + result-scorecard-3up` |
| “先讲市场压力，再归纳四个瓶颈，最后给转型定位” | `composition-pressure-bottleneck-positioning.md` | `content-scqa.md` + `layout-left-claim-right-evidence.md` + `layout-native-chart-slot.md` | `pressure-facts + conflict-chart + bottleneck-grid + conclusion-band` |
| “做一张北极星、双轮、四层能力、两条协同和五项价值的总蓝图” | `composition-operating-model-blueprint.md` | `layout-pyramid-hierarchy.md` + `layout-process-flow.md` + `layout-kpi-strip.md` | `north-star + enabler-2up + layer-stack + collaboration-loops + value-strip` |
| “我有很多材料，但不知道这页到底该如何组织论证” | `composition-business-report-argument-cascade.md` | `contract-structure-hierarchy.md` + 一个上表分支 | 先选唯一 `proof_goal` 和主链，再生成具体 group plan |

快速组合纪律：

- template series 决定“整册如何看、页面外围如何稳定”，composition branch 决定“这一页为什么这样组织”，assembly/layout 决定“多个 region 如何排布”，component pattern 决定“某一个局部复杂形状如何生成”。
- 一页只选一个主分支；第二个分支只能作为 sidecar 或 proof，不能形成双主线。
- 标题含数字时，必须同时加载分支中的 `evidence_alignment_checks`，不能只组合视觉组件。

## 按视觉主题

| 场景 | 推荐 theme |
| --- | --- |
| 浅底蓝白商务 / 经营汇报 | `theme-light-business-blue.md` |
| 深蓝强调 / 章节页 | `theme-dark-business-blue.md` |
| 党政 / 国企 / 政策学习 | `theme-red-gold-government.md` |
| 科技 / 互联网 / AI 平台 | `theme-tech-dark-neon.md` |
| 金融 / 财务 / 投资人材料 | `theme-finance-silver-blue.md` |
| 培训 / 课件 / 方法论 | `theme-training-clean.md` |
| 文化 / 品牌 / 文旅 | `theme-cultural-green.md` |
| 中文读书分享 / 文学纪录片叙事 | `style-literary-documentary-cn.md` |
| 整页背景选型(纯色/矢量装饰底 svg/暗色影像/纸纹;禁透明·禁斑点波纹 pattern)与 merge_slide_background_binding 参数 | `theme-background-policy.md` |

## 按场景模板

| 场景 | 推荐 scenario |
| --- | --- |
| 年终总结 / 经营复盘 / 述职 | `scenario-annual-summary.md`（复现金标三页用 `scenario-annual-summary-gold-pages.md`） |
| 项目汇报 / 周报 / 里程碑 | `scenario-project-report.md`（复现金标两页用 `scenario-project-report-gold-pages.md`） |
| BP / 融资 / 路演 | `scenario-financing-roadshow.md` |
| 产品发布 / 新品价值 | `scenario-product-launch.md` |
| 学术答辩 / 论文 / 研究 | `scenario-academic-defense.md` |
| 党政学习 / 政策宣贯 | `scenario-government-study.md` |
| 培训课程 / SOP / 练习 | `scenario-training-course.md` |
| 书籍深度解析 / 读书分享 / 作品深读 | `scenario-book-deep-analysis.md` |
| 课堂宣讲 / 科普 / 科学传播 / 公开课 | `scenario-educational-pop-science.md` |
| 景点宣传 / 文旅 / 城市推介 / 场馆展示 | `scenario-public-image-visual-assets.md` |
| 高级感 / 场景感 / 图片背景优先 | `scenario-background-image-premium.md` |
| 课堂宣讲 / 科普 / 校园公开课 | `scenario-educational-pop-science.md` |
