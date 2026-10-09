<!--
id: layout-timeline-horizontal
category: layout
read_when: 项目计划、阶段复盘、发展历程、里程碑
page_roles: content, summary
supports: svg_drawingml
outputs: svg_layout
depends_on: contract-layout-density.md
relation_specs: conflicts_with:layout-timeline-ascending-steps, conflicts_with:layout-timeline-anchored-columns, conflicts_with:layout-timeline-zigzag-groups, requires:contract-gold-svg-builder, requires:structure-hierarchy
max_use: 只读取本文件，不要连带读取同类全部文件；强调逐期走高读 layout-timeline-ascending-steps.md，逐期"目标/行动/评估"三槽详情读 layout-timeline-anchored-columns.md，6+ 事件分组高密度回顾读 layout-timeline-zigzag-groups.md
-->

# Layout: Horizontal Timeline

## 内容说明

每个节点写时间、动作、交付物、风险或结果。当前阶段和风险节点要有明确标记。

## 视觉说明

时间轴横向均分，节点上下错落以减少拥挤。重点节点用 accent，不要所有节点同权。

## SVG说明

坐标骨架：

- `timeline-axis`: `x1=130 x2=1470 y=475`
- 4 节点：`x=180/530/880/1230`
- 5 节点：`x=150/470/790/1110/1430`
- 节点卡：`w=260 h=150`，上下交错 `y=300/535`

分组命名：`milestone-1..N`。

## 金标示例

- 示例路径：`assets/examples/svg-ppt/decks/scenario-government-briefing-gold-pages/05-timeline-arrow.svg`
- 需要查看结构时调用：`load_skill_example(path="assets/examples/svg-ppt/decks/scenario-government-briefing-gold-pages/05-timeline-arrow.svg")`
- 横向时间线大箭头示例：4 个里程碑节点卡（01-04 + chevron 时序）+ 单条大箭头 ribbon 串 4 个白点节点，是"默认/朴素"横向时间线；无递进/分组/详情卡需求时用本布局，不用 ascending-steps / anchored-columns / zigzag-groups 三个变体。
- 勿照抄示例首行 `<rect x="0" y="0" width="1280" height="720">`：它只是离线预览底色。运行时整页背景由 `deck_framework.background` 承载，提交 `render_svg_drawingml_slide` 的 SVG 不画满页背景矩形，否则触发 `SVG_FULL_PAGE_BACKGROUND_FORBIDDEN`（同 `drawingml-svg-authoring-core.md`）。
