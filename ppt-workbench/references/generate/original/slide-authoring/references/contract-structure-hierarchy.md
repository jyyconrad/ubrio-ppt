<!--
id: contract-structure-hierarchy
category: execution-contract
read_when: 页面效果固定、需要先拆信息层级再生成 SVG-PPT
page_roles: content, section_divider, summary
supports: svg_drawingml
outputs: structure_hierarchy, svg_group_plan, page_spec_json
depends_on: contract-gold-svg-builder.md, gold-structure-composition.md
max_use: 只读取本文件和一个 composition/layout/scenario reference，不要直接套全部模板
-->

# Structure Hierarchy Contract

## 内容说明

金标页不是先选三卡、四卡或表格，而是先写 `structure_hierarchy`。弱模型必须先把
当前页内容先拆出框架层，再拆成 5 个内容层级，最后决定 `page_spec.layout` 和 SVG 分组。
不要不分析层级就直接套 `gold_cards`，也不要把 builder 默认 layout 当作页面设计结论。

层级拆解：

0. 框架层：背景、母版、安全区和全页装饰，归 PPT 框架层，不进 SVG 内容层。
1. 语义层：`page_role`、核心 `claim`、支撑证据、风险/动作、来源。
2. 讲述层：主结论、证据链、解释、影响、行动闭环。
3. 视觉层：主标题、key message、指标带、主体结构、辅助说明、底部来源。
4. 几何层：标题区、主体区、证据区、收口区、来源说明区的面积和主次权重。
5. SVG group 层：把内容层级映射成可转换 DrawingML 的 `<g id="...">`。

## page_spec 必填

在 `page_spec.json` 中先写：

```json
{
  "structure_hierarchy": {
    "framework_layer": ["ppt_framework_background", "safe_area"],
    "semantic_layer": ["核心判断", "关键证据", "风险/动作", "来源"],
    "narrative_layer": ["结论先行", "证据链", "解释影响", "行动闭环"],
    "visual_layer": ["main-title", "key-message", "metric-strip", "evidence-cluster", "chart-slot", "screenshot-proof", "action-bar"],
    "geometry_layer": ["top-stage", "title-band", "main-body", "chart-slot-area", "proof-area", "bottom-contract"],
    "svg_group_layer": ["stage-label", "main-title", "key-message", "metrics-panel", "main-content", "chart-slot-1", "screenshot-proof-1", "actions", "source-note"]
  }
}
```

没有这段，不允许直接生成 `gold_cards`。如果工具模板没有该字段，也要手动补上。

## SVG说明

推荐 group 名：

- `stage-label`：贴近顶部，只做弱导航，不抢标题。
- `main-title`：页面第一视觉锚点。
- `key-message`：一句话结论，位于标题下方。
- `metric-strip`：2-5 个关键指标或事实口径。
- `story-spine`：贯穿主区域的因果/阶段/对比主线。
- `chart-slot-1`：原生 chart 占位，SVG 不手绘图表。
- `screenshot-proof-1`：截图或系统记录证据占位。
- `evidence-cluster`：证据、数据、案例和来源。
- `action-bar`：Owner、节点、风险、检查标准。
- `source-note`：来源、口径、缺口说明。

结构层级必须驱动布局：证据多用表格/证据链，动作多用台账，阶段多用时间线，关系多用矩阵
或中心辐射。不要把所有内容都塞进同样尺寸的卡片。

## 提交前 QA

- `structure_hierarchy` 至少覆盖语义层、讲述层、视觉层、几何层、SVG group 层。
- `page_spec.layout` 必须由内容层级推导，不能因为模板默认就是 `gold_cards`。
- 主体至少有一个非卡片化承载：证据表、时间线、对比带、行动条、矩阵或故事主线。
- 每个 SVG group 都要服务信息层级，不放纯装饰块。
