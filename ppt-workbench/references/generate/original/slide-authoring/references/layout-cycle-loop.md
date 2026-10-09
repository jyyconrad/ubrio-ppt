<!--
id: layout-cycle-loop
category: layout
read_when: 循环、闭环机制、PDCA、增长飞轮
page_roles: content, summary
supports: svg_drawingml
outputs: svg_layout
depends_on: contract-layout-density.md
max_use: 只读取本文件，不要连带读取同类全部文件
-->

# Layout: Cycle Loop

## 内容说明

循环页必须说明起点、每环节动作、反馈数据和闭环结果。适合 PDCA、运营飞轮、风险闭环。

## 视觉说明

中心写循环目标或核心判断，周围 4-6 个节点顺时针排列。箭头必须闭合，并标注反馈口径。

## SVG说明

坐标骨架：

- `cycle-loop`: 主分组，中心 `cx=800 cy=500 r=120`。
- 4 节点中心：`(800,285) (1110,500) (800,715) (490,500)`。
- 5 节点中心：`(800,270) (1100,420) (990,690) (610,690) (500,420)`。
- 底部 `loop-contract`: `x=90 y=760 w=1420 h=72`。

分组命名：`cycle-loop`、`loop-core`、`loop-step-1..N`、`loop-arrow-1..N`、`loop-contract`。

禁止：不要把循环画成无方向的圆环；不要只有方法名而没有输入、输出、指标或责任。
