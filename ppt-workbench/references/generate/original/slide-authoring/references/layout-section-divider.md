<!--
id: layout-section-divider
category: layout
read_when: 章节页、过渡页、问题引入页
page_roles: section_divider
supports: svg_drawingml
outputs: svg_layout
depends_on: contract-visual-token.md
max_use: 只读取本文件，不要连带读取同类全部文件
-->

# Layout: Section Divider

## 内容说明

章节页要说明本章讲什么、为什么进入本章。不要只有巨大编号和空背景。

## 视觉说明

章节编号可以强于内容页，但主标题仍必须清晰。副标题或桥接句说明逻辑承接。

## SVG说明

坐标骨架：

- `section-title`: `x=90 y=220 font-size=24..36`
- `main-title`: `x=90 y=360 font-size=56..72`
- `bridge-sentence`: `x=90 y=440 font-size=22..28`
- 不在 SVG 内画页眉、页码、章节胶囊或进度导航；需要章节编号时交给框架层。

深色背景时标题用浅色，桥接句用次浅色。
