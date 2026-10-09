<!--
id: layout-pyramid-hierarchy
category: layout
read_when: 金字塔、战略分层、能力层级、优先级递进
page_roles: content, summary
supports: svg_drawingml
outputs: svg_layout, pyramid_layers
depends_on: contract-layout-density.md
relation_specs: pairs_with:svg-shape-3d-isometric, conflicts_with:layout-funnel-stage-stack, conflicts_with:layout-retrospect-outlook-pyramid
max_use: 只读取本文件，不要连带读取同类全部文件；向下收窄的转化/筛选漏斗读 layout-funnel-stage-stack.md
-->

# Layout: Pyramid Hierarchy

## 内容说明

顶部写最终目标或最高判断，中层写 2-3 个抓手，底层写证据、资源、行动或约束。
`pyramid_layers` 固定 3 层时最稳定；超过 3 层要先合并为目标/能力/证据三类，不要把
金字塔切成很多薄片。若金字塔只作中央递进装置、把"回顾—成果—展望"等三时段叙事栏串联起来（非静态层级主体），改 `layout-retrospect-outlook-pyramid.md`。

## 视觉说明

金字塔强调层级，不强调面积装饰。每层必须有文字证据，不只放标签。
层内只放短 `title` 和短 `claim`；证据、风险、行动、来源放到 `hierarchy-proof`
区，避免三角或梯形内部塞满小字。

## SVG说明

金字塔主体必须是闭合 `<polygon>` / `<path>` 图形结构，转换后成为可编辑 DrawingML
freeform。不要用三层矩形卡片冒充金字塔，不要退化成三层矩形卡片；也不要走原生 PPT overlay。

布局输入：

- `pyramid_region`: 当前页给金字塔的内容区域，格式 `{x,y,w,h}`。
- 未给 `pyramid_region` 时，用主体区左中部；如果右侧还要放 chart/screenshot，
  必须主动缩小 `pyramid_region`，不要默认占满整页。
- `pyramid_proof_region` 可选；不写时先尝试放到金字塔右侧，右侧不足再放到底部。

计算规则：

- 令 `cx = x + w/2`，三层高度各约 `h/3`，层间 gap 取 `h*0.02` 到 `h*0.04`。
- 顶层是三角：顶点在 `(cx,y)`，底边宽约 `w*0.35~0.45`。
- 中层是梯形：上边接近顶层底边，下边宽约 `w*0.65~0.75`。
- 底层是梯形：上边接近中层下边，下边占满 `pyramid_region.w`。
- 每层 label 放在该层视觉中心附近，`text-anchor="middle"`。
- 宽度小于 520 时，每层只放标题；claim 改放 `hierarchy-proof`。

文本压缩：

- `title`: 4-8 个字，保留在层内。
- `claim`: 10-18 个字，最多两行；超长时截短或移到 proof。
- `evidence/action`: 不进 polygon，统一放 proof 区，每层 1-2 条。
- proof 在右侧时按竖向三段排列；proof 在底部时按三列或三段短行排列。

分组命名：`pyramid-stack`、`pyramid-layer-1..3`、`hierarchy-proof`。

禁止：不要用巨大三角形占满主体却缺证据；不要让底层文字小到不可读。

需要等距轻立体表达时读 `svg-shape-3d-isometric.md` 的分层金字塔画法，仍保持闭合 polygon 可编辑。

## 金标示例

- 示例路径：`assets/examples/svg-ppt/decks/scenario-government-briefing-gold-pages/01-pyramid-hierarchy.svg`
- 需要查看结构时调用：`load_skill_example(path="assets/examples/svg-ppt/decks/scenario-government-briefing-gold-pages/01-pyramid-hierarchy.svg")`
- 只参考四层金字塔（自下而上渐深，polygon 堆叠、顶层最深=最高抽象/底层最浅=最基础）+ 每层虚线引出说明卡 + 左侧方向轴的层级装配；不要照抄坐标与占位数据。
- 勿照抄示例首行 `<rect x="0" y="0" width="1280" height="720">`：它只是离线预览底色。运行时整页背景由 `deck_framework.background` 承载，提交 `render_svg_drawingml_slide` 的 SVG 不画满页背景矩形，否则触发 `SVG_FULL_PAGE_BACKGROUND_FORBIDDEN`（同 `drawingml-svg-authoring-core.md`）。
