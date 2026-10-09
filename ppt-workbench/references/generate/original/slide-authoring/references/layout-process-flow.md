<!--
id: layout-process-flow
category: layout
read_when: 实施路径、责任链路、闭环机制、审批流转、端到端交付、训练/生产/运营链路
page_roles: content, summary
supports: svg_drawingml
outputs: svg_layout
depends_on: contract-layout-density.md, drawingml-svg-authoring.md
relation_specs: conflicts_with:layout-arrow-ribbon-metrics, requires:contract-gold-svg-builder, requires:structure-hierarchy
max_use: 只读取本文件，不要连带读取同类全部文件
-->

# Layout: Process Flow

## 适用与不适用

- 适用：实施路径、专项攻坚打法、审批流转、生产训练链路、运营交付闭环、治理机制、端到端责任链。
- 不适用：并列能力/策略用 `layout-four-cards-grid.md`；时间演进用 `layout-timeline-horizontal.md`；PDCA/飞轮式循环闭环用 `layout-cycle-loop.md`；组织层级用 `layout-pyramid-hierarchy.md`；只把多段板块成果按方向串成陈列带、每段配一枚成果巨数（非机制闭环、无责任链）用 `layout-arrow-ribbon-metrics.md`。
- 若流程只是证据，应缩成 mini-flow，把主区域让给结论、图表、矩阵或截图证据。

## 表达目标

流程页必须证明一件事“能落地、可管控、有人负责、有结果”，而不只是把步骤排成一行。标题写机制判断；主体说明从什么输入出发、经过哪些关键动作和控制点、由谁负责、交付什么结果；底部或右侧用闭环结果收口。

## 内容槽位

每个节点至少包含：

- `label`: 2-6 字动作名，如“预训练”“审批复核”“灰度发布”。
- `action`: 一句动词短语，说明抓手。
- `output`: 关键交付物、状态变化或决策结果。
- `owner_or_gate`: 责任方、验收标准、审批条件三选一；重要节点必须有。

整页还要有：

- `flow_claim`: 观点标题，说明链路价值。
- `start_end`: 起点和终点，避免流程没有边界。
- `control_points`: 关键质量门、审批点、风险回退或资源保障。
- `closure_result`: 最终闭环结果，放底部或右侧。

## 容量与压缩

- 3-4 步：每步可保留动作、产出和责任/质量门。
- 5-6 步：节点只保留短动作名与一个关键输出，责任或控制点下沉到保障条；正文建议不小于 14pt，任何正文不得小于 12pt。
- 7 步以上：压缩成 5-6 个主阶段，把异常/控制点移到第二层，或拆页；禁止靠继续缩小字号硬塞。
- 每个节点的 `label` 2-6 字，`action` 与 `output` 各一条；同一节点超过三条信息时先合并业务层级。

## 比例布局

- 使用 `drawingml-svg-authoring.md` 给出的内容安全区作为 `process_region`，不要另写一套整页坐标。
- 标题与链路价值占可用高度 15%-22%，主流程占 50%-62%，闭环结果或保障条占 12%-18%，其余作为区间留白。
- 单行流程按 `N` 个等宽节点和 `N-1` 个等宽连接槽分配宽度；节点宽度优先于装饰，连接槽只承担阅读方向。
- 审批/跨部门协同采用泳道；训练/生产/交付链采用上下双层；主流程只占左侧 60%-70% 时，右侧必须承载成效、风险或责任合同。
- 异常回路使用虚线并弱于主流程；真实图表只预留 native chart slot，不在 SVG 内手绘数据图。

## SVG 构建合同

- 主分组：`process-flow`；节点：`flow-step-1..N`；连接：`flow-arrow-1..N`；控制点：`control-point-1..N`；异常路径：`exception-path`；收口：`process-contract`。
- 默认阅读方向为从左到右。连接线起点在前一节点出口，终点在后一节点入口；箭头尖端必须落在终点，不能用朝向不明确的独立 polygon 充当连接箭头。
- 优先使用可转换的 `marker-end` 线箭头。下面是局部、参数化片段，放入连接槽时替换变量，不是整页坐标：

```xml
<defs>
  <marker id="flow-arrow-head" viewBox="0 0 10 10" refX="9" refY="5"
          markerWidth="8" markerHeight="8" orient="auto">
    <path d="M 0 0 L 10 5 L 0 10 z" fill="{{accent}}"/>
  </marker>
</defs>
<g id="flow-arrow-1" transform="translate({{connector_x}},{{connector_y}})">
  <line x1="0" y1="0" x2="{{connector_width}}" y2="0"
        stroke="{{accent}}" stroke-width="3"
        marker-end="url(#flow-arrow-head)"/>
</g>
```

## 失败检查

- 不把 5-6 步流程做成同权散卡；必须有箭头、编号或蛇形路径。
- 不只写阶段名；每步要有动作和输入/输出。
- 从左到右逐个检查 `flow-arrow-k`：线段终点、marker-end 尖端和下一节点入口必须同向；任何反向箭头都算失败。
- 节点编号、视觉顺序和业务顺序必须一致；两行蛇形流程要在换行处明确转向。
- 正文小于 12pt、节点溢出、连接线穿过文字、起点/终点缺失或没有闭环结果都算失败。
- 不让异常路径比主流程更抢眼。
- 不靠底部横条掩盖主体空洞；空白必须服务辅助图形或视觉焦点。
- 不手绘真实图表；图表只放 native chart slot。
