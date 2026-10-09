<!--
id: layout-problem-solution-benefit
category: layout
read_when: 需要表达问题、方案、收益或原因、措施、结果
page_roles: content
supports: svg_drawingml
outputs: svg_layout
depends_on: contract-layout-density.md
relation_specs: conflicts_with:layout-problem-improve-bilateral, conflicts_with:layout-problem-improve-value-rail
max_use: 只读取本文件，不要连带读取同类全部文件；痛点与对策一一对应的双侧转化页读 layout-problem-improve-bilateral.md；非对称双撞色面板+价值轨读 layout-problem-improve-value-rail.md
-->

# Layout: Problem Solution Benefit

## 内容说明

左侧问题/原因，中间方案/抓手，右侧收益/结果。每列写判断、证据、动作或风险。

## 视觉说明

问题可用弱红或警示标签，方案用主色，收益用正向强调。箭头表示因果，不做装饰线。

## SVG说明

坐标骨架：

- 三列：`x=90/580/1070 y=285 w=420 h=390`
- 箭头：`problem -> solution -> benefit`
- 底部 `actions`: `x=90 y=720 w=1420 h=82`

分组命名：`problem-panel`、`solution-panel`、`benefit-panel`、`fix-action`。
