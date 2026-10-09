<!--
id: contract-svg-page-workflow
category: execution-contract
read_when: 不知道 SVG 页从哪里开始，或需要弱模型分步写作路径
page_roles: content, summary
supports: svg_drawingml
outputs: svg_steps
depends_on: drawingml-svg-authoring.md, _index/capability-tree.json
max_use: 只读取本文件，不要连带读取同类全部文件
-->

# SVG Page Workflow Contract

## 内容说明

先确定页面要回答的问题：本页观点是什么、用什么证明、希望受众做什么。内容页必须有
标题、核心结论、3-5 个内容组和行动/风险收口。

## 视觉说明

先写视觉 token，再画图形。没有 token 就不要开始自由配色。主标题是第一视觉锚点，
正文主体是页面主要面积，内容区弱化保留来源和口径。

## SVG说明

固定流程：

1. 建 `<svg viewBox="0 0 1280 720">`。
2. 读取 `deck_framework_snapshot.content_region_px` 作为内容安全区；没有该字段时才按
   默认 1280x720 页面估算主体区。
3. 记录 `framework/background` token，但不画整页 background、页眉、页码、侧边框或外框；
   背景和页面 chrome 由 PPT 框架层负责，SVG 编译后由 renderer 套到 PPTX。
4. 写 `main-title` 和 `key-message`。
5. 建 `main-content` 主体组。
6. 建 `content-group-1..N`，或按页型建立 `process-flow`、`pyramid-stack`、`cycle-loop`、`screenshot-proof-1`、`chart-slot-1` 等主体组。
7. 补 `actions` 或 `source-note`。
8. 检查文本 fill、字号、边界、禁止元素、无整页背景 rect、无页眉/侧边框/外框。

最小分组：

```xml
<g id="main-title">...</g>
<g id="key-message">...</g>
<g id="main-content">
  <g id="content-group-1">...</g>
  <g id="content-group-2">...</g>
  <g id="content-group-3">...</g>
</g>
<g id="native-chart-slots">
  <g id="chart-slot-1" data-role="native-chart-slot" data-native-chart="true">...</g>
</g>
<g id="actions">...</g>
<g id="source-note">...</g>
```
