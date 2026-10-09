<!--
id: drawingml-svg-authoring-core
category: execution-contract
read_when: 每次走 svg_drawingml route 前必须读取的最小硬合同
page_roles: cover, agenda, content, section_divider, summary, closing
supports: svg_drawingml
outputs: svg_compatibility_contract_core
depends_on: none
max_use: 只作为 SVG 可转换最小硬合同；复杂边界、详细元素规则和调试说明再读取 drawingml-svg-authoring.md
-->

# DrawingML SVG Authoring Core

`svg_drawingml` 路线的 always-read 最小合同。复杂元素、图片裁切、调试和代码辅助几何再读 `drawingml-svg-authoring.md`。

## 硬规则

- 只写一个完整 `<svg viewBox="0 0 1280 720">`；全部坐标、`data-icon-box`、native slot `data-x/y/w/h` 都用 1280x720。
- 内容安全区建议 `x=64..1216`、`y=58..648`；标题、结论、主体和来源必须在安全区内。
- SVG 只承载内容，不画整页背景、母版、安全区、页眉、breadcrumb、页码、贴边竖条、外框或框架 chrome；整页背景选型与参数统一见 theme-background-policy 颗粒（photo_dark/paper_light/pattern/纯色四形态）。
- 业务字段、指标、周期、来源写入 `<text>` / `<tspan>`；不得改写、删除或发明已确认内容。
- `<text>` 必须显式 `fill`、`font-family`、`font-size`；正文通常 ≥15px，图表/流程标签 ≥12px，来源 ≥11px。
- 过载时先压缩文案、重排、拆页或询问用户，不靠缩小字号或 renderer 兜底。
- 单一色系只作强调色；正文、图表标题、坐标轴、图例、表格文字必须是高对比中性色。
- 最终态不得含 `待补充`、`需补充`、`示意`、`合理推断`、`预计` 等草稿表达。

## 允许元素

`svg`、`defs`、`linearGradient`、`radialGradient`、`rect`、`circle`、`ellipse`、`line`、`path`、`polygon`、`polyline`、`text`、`tspan`、普通 `g`；克制场景可加一个 `filter`（含 `feGaussianBlur`，配色用 `feFlood`，可选 `feOffset`/`feDropShadow`）做外发光或柔和投影。颜色用 HEX，透明度用 `fill-opacity` / `stroke-opacity`；XML 字符转义。

## 槽位

- 图标先 `search_svg_icons`，写 `data-icon-id` + `data-icon-box`；禁止手绘业务图标、emoji、猜 path 或复制原始 SVG path。
- 图片、图表、表格只声明 native slot；真实绑定写入 picture plan 或 `native-data.json`，slot `id` 必须与 JSON `slot_id` 一致。
- 不用 SVG 手绘真实坐标轴、图例、柱线饼、数据标签或逐单元格表格。

## 禁止

`script`、事件属性、DOCTYPE/ENTITY、`style`、`class`、external CSS、`@font-face`、`foreignObject`、`mask`、`symbol/use`、`textPath`、动画、iframe、http(s) 资源、超大 data URI、`rgba()`、`<g opacity>`、`<image opacity>`、`backdrop-filter`、`filter` 内除 `feGaussianBlur`/`feFlood`/`feOffset`/`feDropShadow` 外的其它滤镜原语（如 `feColorMatrix`/`feBlend`/`feComposite`/`feTurbulence`）与多滤镜堆叠。

## 提交前

内容在画布内；主体不只停在上半屏；卡片无空容器；没有黑字、低对比、小字、emoji、多行来源或草稿态；已通过 SVG DrawingML 校验，失败时只局部修当前 SVG。
