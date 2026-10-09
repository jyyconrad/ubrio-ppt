<!--
id: layout-summary-action-matrix
category: layout
read_when: 总结页、行动计划、责任闭环、风险收口
page_roles: summary
supports: svg_drawingml
outputs: svg_layout
depends_on: contract-layout-density.md
max_use: 只读取本文件，不要连带读取同类全部文件
-->

# Layout: Summary Action Matrix

## 内容说明

总结页不只是感谢。要写 3 点结论、行动清单、责任人、时间和风险闭环。

## 视觉说明

上方放总结判断，中部放行动矩阵，底部放资源诉求或下一步。

## SVG说明

坐标骨架：

- `key-message`: `x=90 y=180 w=1420 h=90`
- `summary-points`: `x=90 y=300 w=500 h=390`
- `action-matrix`: `x=640 y=300 w=870 h=390`
- `next-step`: `x=90 y=730 w=1420 h=80`

矩阵列建议：`事项 / 责任 / 时间 / 风险`。
