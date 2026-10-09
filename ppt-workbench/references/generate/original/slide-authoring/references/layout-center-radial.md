<!--
id: layout-center-radial
category: layout
read_when: 能力模型、战略抓手、组织机制、中心目标与卫星模块
page_roles: content
supports: svg_drawingml
outputs: svg_layout
depends_on: contract-layout-density.md
relation_specs: conflicts_with:layout-quad-cards-core-cluster
max_use: 只读取本文件，不要连带读取同类全部文件；单一中心核+一圈卫星是本颗粒，无核 2×2 等圆簇+四角详情卡读 layout-quad-cards-core-cluster.md
-->

# Layout: Center Radial

## 内容说明

中心写目标或核心能力，周围 4-6 个模块写路径、保障、证据或动作。

## 视觉说明

中心突出但不压过主标题。卫星模块等距、同密度，连接线不穿过正文。

连接线与中心文字保护（检查项）：

- 连接线不得穿过中心主文字 bbox：要么在文字框边缘断开（连线起点退到 `center-core` 半径外或
  文字 bbox 外），要么给中心文字加一层与背景同色/半透明的遮罩底板压在连线之上。
- 卫星连线也不得压住卫星模块自身的标题或正文；如发生穿字，先缩短连线或调模块位置。

## SVG说明

坐标骨架：

- `center-core`: `cx=800 cy=500 r=120`
- 4 模块中心：`(420,380) (1180,380) (420,650) (1180,650)`
- 6 模块中心：`(360,400) (620,650) (980,650) (1240,400) (620,300) (980,300)`

分组命名：`center-core`、`satellite-1..N`、`relation-lines`。
