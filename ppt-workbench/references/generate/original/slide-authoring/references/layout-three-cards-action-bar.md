<!--
id: layout-three-cards-action-bar
category: layout
read_when: 三个信息组且需要底部结论、行动或风险收口
page_roles: content, summary
supports: svg_drawingml
outputs: svg_layout
depends_on: contract-layout-density.md
relation_specs: conflicts_with:layout-phased-action-columns, requires:contract-gold-svg-builder, requires:structure-hierarchy
max_use: 只读取本文件，不要连带读取同类全部文件
-->

# Layout: Three Cards Plus Action Bar

## 内容说明

适合三类问题、三项举措、三条证据。每卡写短标题、判断句、2-3 条支撑和一个标签。若三栏按期次（月/季/阶段）推进、每栏一个期次表头下挂一列落地举措清单，改 `layout-phased-action-columns.md`；本颗粒是无期次语义的通用三信息组。

## 视觉说明

三张卡不要过高空洞。底部行动条承接页面结论，避免主体下方大空白。

## SVG说明

坐标骨架：

- `main-title`: `x=90 y=95`
- `key-message`: `x=90 y=175 w=1420 h=80`
- 三卡：`x=90/555/1020 y=295 w=410 h=360`
- `actions`: `x=90 y=700 w=1420 h=92`
- `source-note`: `x=90 y=860`

卡片内部从上到下：编号/图标、短标题、判断句、证据、标签。
