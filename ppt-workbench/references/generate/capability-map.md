# PPT 生成能力图

本页是 L1 目录，不是已加载模块。先按 [本地 skill-graph 路由](methods/skill-graph.md) 运行 `scripts/skill_graph/search_modules.py`（一次一个维度，只得候选 id），再用 `scripts/skill_graph/load_modules.py` 注入 always_read、default_gold_path 和最多 2–4 个主模块。`chinese-business-ppt-authoring.md` 与 `routing-examples.md` 只是兜底索引。路径映射见 [source-map.md](source-map.md) 与 [route-evaluation.md](route-evaluation.md)。

## 按任务进入

中文业务正文页默认走金标 SVG + native slots。先 skill-graph 检索/加载当前页，不要把本表或整棵能力树当已读。

| 当前任务 | 必要入口 | 可选深入 |
| --- | --- | --- |
| 开始写一页 / 不知道读哪些合同 | [本地 skill-graph 路由](methods/skill-graph.md) | capability-tree 的 always_read 与 default_gold_path |
| 写金标正文页 / `page_spec` → `source.svg` | [金标单页路径](methods/gold-pages.md) | [金标页型](original/slide-authoring/references/gold-page-patterns.md)、[结构层级](original/slide-authoring/references/contract-structure-hierarchy.md)、`scenario-*-gold-pages` |
| 把 `source.svg` 编成可编辑 PPTX | [活动 SVG DrawingML](methods/authoring-and-checks.md) | `write_svg.py` → `validate_svg_drawingml.py` → `render_svg_drawingml.py`；`native.cjs` 只是 fallback |
| 指标、图表、表格、流程、矩阵、图片或基础结构页 | skill-graph `--dimension layout` | [原生图表与表格槽](methods/native-components.md) |
| 业务图标 / KPI 徽标 | [图标嵌入](methods/icon-embed.md) | `scripts/svg/search_icons.py`（line/filled 两个家族）→ `data-icon-id`；不要 `search_svg_icons` |
| 截图 / 照片 / 整页底板 | [图片三个 owner](methods/image-owners.md) | 页旁 `deck-framework.json`、`native.cjs` `image()`、`native-image-slot` |
| 没有本地图片，需要封面底板或场景配图 | [内置图片库检索](methods/image-library.md) | `scripts/assets/search_images.py` 检索 + `--stage` 到页面目录 |
| 页面角色或结构拿不准 | skill-graph `--dimension layout` 或 [版式选择](methods/layout-selection.md) | 对应 layout 原文 |
| 内容过多、证据不足或标题不成结论 | skill-graph `--dimension content` 或 [当前页表达与质量](methods/current-slide.md) | 密度与证据原文 |
| 页与页对不上，或一页里几张卡同样重 | [叙事与形状](../outline/narrative-shape.md) | [内容与视觉质量门](../content-visual-quality-gates.md) |
| 配色、主题、模板系列 | skill-graph `--dimension theme` | 下方主题与系列原文 |
| 需要视觉预览 | 优先使用宿主或用户现有 PPTX 预览/编辑能力 | [预览选项](preview-options.md)；LibreOffice 只是可选转换支线 |

总样例说明见 [成对制作样例](../../assets/examples/README.md)。原生 smoke 证明固定合成输入可由工具生成并通过既定对象检查，不等于模型质量评测，也不等于 Microsoft PowerPoint 编辑往返验证。

`contract-layout-density` 与 `contract-content-density` 不是缺失能力：它们分别映射到 [版面密度原文](original/slide-authoring/references/contract-layout-density.md) 和 [内容密度原文](original/slide-authoring/references/contract-content-density.md)。`layout-density`、`content-density` 是能力树节点 ID；带 `contract-` 的名称是原文件/原文 ID。独立导航统一直达上述真实文件，不修改原始声明。

## 内容与论证

- 结论、证据、行动闭环：[金字塔表达](original/slide-authoring/references/content-pyramid-claim-evidence-action.md)、[SCQA](original/slide-authoring/references/content-scqa.md)、[标题改写](original/slide-authoring/references/content-title-rewriting.md)。
- 对比、分析框架和证据缺口：[内容对比](original/slide-authoring/references/content-comparison.md)、[SWOT/3C/PEST](original/slide-authoring/references/content-swot-3c-pest.md)、[证据缺口标注](original/slide-authoring/references/content-evidence-gap-labeling.md)。
- 非业务叙事：[文学纪录片叙事](original/slide-authoring/references/content-literary-documentary-narrative.md)。

以上是原始可读方法；是否能直接制作成原生 PPTX 取决于活动组件，不由原文收录状态保证。

## 指标、趋势与图表

- 指标总览：[KPI 条](original/slide-authoring/references/layout-kpi-strip.md)、[指标系统与案例](original/slide-authoring/references/composition-metric-system-with-case.md)。
- 比较与趋势：[柱状比较](original/slide-authoring/references/chart-bar-comparison.md)、[折线趋势](original/slide-authoring/references/chart-line-trend.md)、[组合仪表盘](original/slide-authoring/references/chart-combo-dashboard.md)。
- 构成与桥接：[饼图构成](original/slide-authoring/references/chart-pie-composition.md)、[瀑布图](original/slide-authoring/references/chart-waterfall.md)、[桑基图](original/slide-authoring/references/chart-sankey.md)。
- 图表组合：[原生图表槽](original/slide-authoring/references/layout-native-chart-slot.md)、[图表洞察侧栏](original/slide-authoring/references/composition-chart-insight-rail.md)。

图表方法经 skill-graph 按 layout 维加载。正文页活动配方见 [原生图表与表格槽](methods/native-components.md)：写 `native-data.json` 的 `charts[]`/`tables[]`，SVG 只放空 `native-chart-slot`/`native-table-slot`，用 `scripts/svg/validate_svg_drawingml.py` 预检、`render_svg_drawingml.py` 转 DrawingML 后再 `overlay_native_slots.py` 叠 bar/line/pie/waterfall 与原生表格。桑基走 `native-sankey-slot` 几何 overlay 或显式 fallback，不写 `charts[].kind=sankey`。不要手绘坐标轴。`scripts/native.cjs` 只在 SVG→PPTX 不可用时 fallback，且仅 bar/line/table。

## 对比、矩阵与关系

- 对比：[镜像对比](original/slide-authoring/references/layout-mirror-compare.md)、[正面对决](original/slide-authoring/references/layout-versus-duel.md)、[问题改善双栏](original/slide-authoring/references/layout-problem-improve-bilateral.md)。
- 矩阵：[四象限](original/slide-authoring/references/layout-matrix-quadrant.md)、[总结行动矩阵](original/slide-authoring/references/layout-summary-action-matrix.md)、[诊断洞察网格](original/slide-authoring/references/composition-diagnostic-insight-grid.md)。
- 层级与关系：[金字塔](original/slide-authoring/references/layout-pyramid-hierarchy.md)、[中心辐射](original/slide-authoring/references/layout-center-radial.md)、[架构价值证明](original/slide-authoring/references/composition-architecture-value-proof.md)。

## 流程、时间与行动

- 流程：[过程流](original/slide-authoring/references/layout-process-flow.md)、[阶段堆叠漏斗](original/slide-authoring/references/layout-funnel-stage-stack.md)、[循环闭环](original/slide-authoring/references/layout-cycle-loop.md)。
- 时间：[水平时间线](original/slide-authoring/references/layout-timeline-horizontal.md)、[上升步骤](original/slide-authoring/references/layout-timeline-ascending-steps.md)、[锚定列](original/slide-authoring/references/layout-timeline-anchored-columns.md)。
- 行动：[分阶段行动列](original/slide-authoring/references/layout-phased-action-columns.md)、[目标行动时间线组合示例](original/slide-authoring/assets/examples/svg-ppt/decks/template-series-composite-library/09-target-action-timeline.json)。

## 证据、图片与叙事

- 截图与证据：活动配方 [图片三个 owner](methods/image-owners.md)。结构参考 [截图证明](original/slide-authoring/references/layout-screenshot-proof.md)、[证据版式合同](original/layout-intelligence/references/evidence-layout-contract.md)。
- 图片：三个 owner 见 [图片三个 owner](methods/image-owners.md)（整页 `deck-framework.json`、不对齐正文 `native.cjs` `image()`、SVG 对齐 `native-image-slot` + 本地 `images[].asset_key`）。不要 SVG `<image href>`。槽契约原文：[原生图片槽](original/slide-authoring/references/layout-native-image-slot.md)、[图片来源](original/slide-authoring/references/image-sourcing-commercial-or-generated.md)、[背景策略](original/slide-authoring/references/theme-background-policy.md)。
- 内置图库：[内置图片库检索](methods/image-library.md)。没有本地图片时先 `scripts/assets/search_images.py` 检索 `assets/images/image-index.json`，再 `--stage` 到页面目录；内置图是通用场景图，不得冒充用户证据。CC BY / CC BY-SA 对外交付时保留 `source` 署名。
- 图标：[图标嵌入](methods/icon-embed.md)。先 `scripts/svg/search_icons.py` 检索捆绑 `icon-index.json`（lucide line 约 1700 个、mdi filled 约 3600 个），再写 `data-icon-id` + `data-icon-box`；validate/render 会 expand。同一页只用一个家族。不要调用 `search_svg_icons`，不要猜 `biz/data-bars`，不要手绘、emoji、`<use data-icon>` 或复制 `path d`；搜不到用编号圆点。图标不进 `native-data.json`。
- 故事页：[双故事卡](original/slide-authoring/references/layout-story-cards-two-up.md)、[三故事卡](original/slide-authoring/references/layout-story-cards-three-up.md)、[书籍对比引文](original/slide-authoring/references/layout-book-compare-quote.md)。

图片许可必须逐项核验：内置图库逐张记录在 `assets/images/image-index.json` 的 `source` 字段；原始目录整体尚无统一公开发行授权。

## 主题、结构与模板系列

- 基础视觉合同：[视觉 token 核心](original/slide-authoring/references/contract-visual-token-core.md)、[字体可移植性](original/slide-authoring/references/contract-font-portability.md)、[结构层级](original/slide-authoring/references/contract-structure-hierarchy.md)。
- 选版方法：[路由方法](original/layout-intelligence/references/layout-routing-method.md)、[业务模式选择](original/layout-intelligence/references/business-pattern-selection.md)、[主题结构分离](original/layout-intelligence/references/theme-structure-separation.md)。
- 模板系列入口：[复合 builder](original/slide-authoring/references/template-series-composite-builder.md)、[研发效能蓝](original/slide-authoring/references/template-series-rd-efficiency-blue.md)、[蓝绿诊断](original/slide-authoring/references/template-series-blue-green-diagnostic.md)、[紫色季度总览](original/slide-authoring/references/template-series-violet-quarterly-overview.md)。

模板系列与金标 SVG builder 经 skill-graph 按需加载，不是整册必读。可执行默认是 [金标单页路径](methods/gold-pages.md) 再 [活动 SVG DrawingML](methods/authoring-and-checks.md)：`page_spec.json` → `--validate-only` → `source.svg` + `native-data.json` → `validate_svg_drawingml.py` → `render_svg_drawingml.py`。结构参考按路径加载 [金标页型](original/slide-authoring/references/gold-page-patterns.md)、[结构层级](original/slide-authoring/references/contract-structure-hierarchy.md) 和 `scenario-*-gold-pages`（government-briefing 在 [workbench 金标目录](gold-examples-catalog.json)，不要改 SHA-frozen `examples-manifest.json`）。`scripts/native.cjs` 只在 SVG→PPTX 不可用时 named fallback。验证和限制以 [活动 SVG DrawingML](methods/authoring-and-checks.md) 为准。

## 质量与失败检查

- 容量：[内容密度](original/slide-authoring/references/contract-content-density.md)、[版面密度](original/slide-authoring/references/contract-layout-density.md)、[容量与回退](original/layout-intelligence/references/capacity-and-fallback.md)、[视觉可读](gates/visual-readability.md)。
- 语义门（`build_gold_svg_page.py --validate-only` 合并执行）：[证据与主张](gates/evidence-claim.md)、[决策与门禁](gates/decision-governance.md)、[人话与主观点](gates/plain-language-and-primary-claim.md)、[原生表格路由](gates/native-table-routing.md)。整册另跑 [一致性](gates/deck-consistency.md)（`scripts/svg/check_deck.py`）。不说人话时先回 [大纲方法](../outline/outline-method.md)。
- 自检：[SVG 自检](original/slide-authoring/references/contract-svg-self-qa.md)、[预渲染门](original/slide-generation-core/references/pre-render-gate.md)。
- 常见失败：[布局溢出](original/slide-authoring/references/anti-pattern-layout-overflow.md)、[空卡片](original/slide-authoring/references/anti-pattern-empty-cards.md)、[固定模板单调](original/slide-authoring/references/anti-pattern-fixed-template-monotony.md)、[仅按标题选版](original/layout-intelligence/references/anti-pattern-layout-by-title-only.md)。

完整平铺节点仍以三份原始能力树为历史事实源：[生成主控](original/slide-generation-core/references/_index/capability-tree.json)、[页面制作](original/slide-authoring/references/_index/capability-tree.json)、[版式智能](original/layout-intelligence/references/_index/capability-tree.json)。
