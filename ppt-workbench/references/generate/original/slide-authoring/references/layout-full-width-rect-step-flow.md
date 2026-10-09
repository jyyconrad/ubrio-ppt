<!--
id: layout-full-width-rect-step-flow
category: shape-component-library
module_type: data_driven_svg_component
read_when: 内容区需要单独生成一条横向满宽的矩形节点流程、根因链、阶段链或整改闭环时
page_roles: content, summary
stage_tags: slide_generation
supports: svg_drawingml
outputs: full_width_rect_step_flow_spec, grouped_editable_svg, stable_step_groups
depends_on: contract-visual-token-core.md, contract-content-density.md, layout-process-flow.md
relation_specs: requires:template-series-composite-builder, requires:layout-process-flow, pairs_with:layout-sectioned-evidence-dashboard, conflicts_with:anti-pattern-fixed-template-monotony
triggers: 横向满宽流程图, 矩形块流程, 根因链, 阶段矩形带, 整改闭环流程, full width rect flow, rect step flow
max_use: 每次 builder 调用只生成一条 3-6 步横向流程；可选一个末端行动块
source_notice: 来源为用户提供的 visual-only 截图；只提炼可见的横向关系、节点 anatomy 和收口方式。
-->

# Layout: Full-Width Rect Step Flow

## 组件边界

一次只生成一条内容区横向流程带，不生成页面标题、背景、分区、指标卡或整页 PPT。所谓“满宽”是填满
调用方给定的 `region`，不是强制占满 1280×720 页面；最小区域为 620×125。

## 视觉逻辑

`组件标题/关系说明 → 3–6 个等宽矩形步骤 → 明确方向箭头 → 可选末端行动块`

- 每个步骤固定由 `编号/图标 + 短标题 + 一句事实或动作` 构成。
- 根因链按“现象 → 执行 → 流程 → 机制 → 根因”排序；阶段链按时间或依赖排序。
- 箭头只表达真实顺序、因果或流转；并列对象不能套用流程箭头。
- 行动块与步骤区分造型，用于整改、决策、验收或最终结果，不应伪装成第 N+1 个普通步骤。

## 输入合同

```yaml
pattern: full_width_rect_step_flow
region: {x, y, w, h} # 最小 620×125
data:
  title: required # 组件标题，不是页面 action title
  steps: 3..6
  step:
    title: required, <=7 Chinese chars
    icon_label: optional, 1..2 chars
    detail: required, <=2 lines
  action:
    title: required
    detail: required
```

`action` 可省略；省略后步骤自动使用完整 region 宽度。

## 失败条件

- 节点没有先后、依赖或因果关系，只是并列分类。
- 步骤超过 6 个、单步解释超过 2 行，或需要分支/回路却仍用单线流程。
- 根因层级缺失或顺序颠倒；整改动作与根因无映射。
- 用不同颜色逐块装饰，破坏模板系列的颜色语义。
- 流程依赖真实日期、Owner 和里程碑明细；此时改 native table 或专用 Gantt。

## 组合方式

先由 `template-series-*` 提供颜色、圆角、线条、密度和页面节奏，再把本组件放在内容区的横向 band。
上方可以由上层 layout 编排多张 `chart_insight_card`，但两个 builder 分别执行、分别产出 `<g>`，由页面装配器
决定相对位置。
