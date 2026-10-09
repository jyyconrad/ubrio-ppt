<!--
id: layout-timeline-anchored-columns
category: layout
read_when: 按期推进的规划/复盘，且每期有明确"目标+行动+结果评估"三要素需要展开
page_roles: content, summary
supports: svg_drawingml
outputs: svg_layout, anchored_columns_layout_rules
depends_on: layout-timeline-horizontal.md, contract-layout-density.md
relation_specs: conflicts_with:layout-timeline-horizontal, conflicts_with:layout-timeline-ascending-steps, conflicts_with:layout-timeline-zigzag-groups, pairs_with:narrative-swiss-copywriting, pairs_with:theme-violet-business, conflicts_with:layout-phased-action-columns
source_notice: 参考公开职场汇报模板的结构组织方式，已抽象为本项目可复制方法；原作固定话术、示例文案、品牌水印一律作为分析输入后丢弃，不入语料。
max_use: 只讲锚定多列详情变体；节点式基准时间轴读 layout-timeline-horizontal.md，增长动能阶梯读 layout-timeline-ascending-steps.md
-->

# Layout: Timeline Anchored Columns

## 三方分工

`layout-timeline-horizontal.md` 是基准：节点承载事件/交付物/风险，只需要"看到发生了什么"。`layout-timeline-ascending-steps.md` 是增长动能变体：阶梯高度编码逐期走高。本颗粒是**逐期三槽详情变体**：时间轴退化为页眉导航条，真正的信息量下沉到轴下的等宽详情卡，每卡固定"目标/行动/评估"三槽。三者语义不同，同一页只选一种。若这页不需要逐期三槽详情、也没有递进或分组诉求，退回基准 `layout-timeline-horizontal.md`，不为填满版式硬造三槽。

## 适用判断

- use_when：按期推进的规划或复盘，每期都有明确的目标、行动计划和结果评估三要素（规划页、执行复盘页高频）。
- avoid_when：纯并列无时间序（改 `layout-three-cards-action-bar.md` 或四卡）；每列要点超过三槽（拆页，不加第四槽硬塞）；只需要事件点、不需要展开详情（改基准 `layout-timeline-horizontal.md`）；无贯穿时间轴线、仅按期次分三栏各挂一列举措清单（每栏一个期次表头）改 `layout-phased-action-columns.md`。

## 骨架

顶部说明段：粗体头 + 2-3 行解释。其下是横向 4-6 节点时间轴页眉：空心圆节点 + 浅→深渐变连接条 + 末端三角箭头，**当前节点用实心+更大半径高亮**，其余节点保持空心。轴下是等宽满高详情卡，节点与卡片按同一套 x 坐标锚定对齐（每个节点正下方一张卡）；卡内固定三槽，从上到下：目标（标题句，不用胶囊）、行动计划（胶囊标签+文）、结果评估（胶囊标签+文），槽间用细分隔线区隔。当前节点对应的卡片呼应轴上高亮：描边可比其余卡片略深同色（≤1.5px）并叠加一枚"当前"胶囊标签；不整圈加粗描边（≥2px）、不叠加顶部色条，卡片本身不应比同组卡片明显更"重"。

节点数越多，每槽文本应越精简：4 节点时三槽合计可以接近容量上限，6 节点时建议只用到上限的六到七成，优先保证 2 行内工整换行，而不是缩字号硬塞。

## 容量

4-6 节点；时间标签 ≤4 字；每列三槽：目标 ≤28 字（≤2 行）、行动 ≤32 字、评估 ≤34 字（6 节点时建议只用六到七成）。超 6 列先合并期次或拆页；正文超行先压缩改写，不缩字号硬塞。

## 金标示例

- 示例路径：`assets/examples/svg-ppt/decks/scenario-report-structure-gold-pages/05-timeline-columns.svg`
- 需要查看结构时调用：`load_skill_example(path="assets/examples/svg-ppt/decks/scenario-report-structure-gold-pages/05-timeline-columns.svg")`
- 只参考轴与卡的锚定对齐、当前节点高亮呼应和三槽分隔的组织方式；不要照抄坐标，也不要把示例里的数据当成业务事实。
- 勿照抄示例首行整页背景 `<rect width="1280" height="720">`：它只是离线预览底色。运行时整页背景由 `deck_framework.background` 承载，提交 `render_svg_drawingml_slide` 的 SVG 不画满页背景矩形，否则触发 `SVG_FULL_PAGE_BACKGROUND_FORBIDDEN`（同 `drawingml-svg-authoring-core.md`）。

## 反模式

- 不让节点和卡片错位；每个节点必须正对一张卡。
- 不在同一卡里塞第四槽；超槽先拆页。
- 不用空心圆节点表示"当前"；当前必须实心+高亮，视觉上唯一。
- 不用整圈粗描边或顶部/左侧色条包住"当前"卡制造强调；同组卡片视觉重量应接近，强调靠描边深浅和胶囊标签。
- 不为了填满卡片高度而重复措辞或注水；宁可保留合理留白也不注水凑字数。
