<!--
id: layout-swiss-core-grid
category: layout
module_type: layout_family
read_when: Swiss 页面需要确定安全区、网格、标题区、主体区、来源区和密度
page_roles: cover, agenda, content, section_divider, summary
stage: slide_generation
supports: svg_drawingml, validate_svg_drawingml, render_svg_drawingml_slide
outputs: swiss_grid_contract, svg_layout
depends_on: drawingml-svg-authoring-core.md, contract-layout-density.md
relation_specs: requires:drawingml-svg-authoring-core, requires:contract-layout-density
max_use: 只讲 Swiss 网格和容量，不讲具体页型结构或配色
-->

# Swiss Core Grid

Swiss 信息设计的稳定方法是“强网格 + 短判断 + 高密度证据”。不要复刻固定模板坐标；先把本页压成一个明确判断，再按信息关系切网格。

## 网格

- 画布 `1280x720`；内容安全区建议 `x=64..1216`、`y=58..648`。
- 标题区、主体区、来源区独立；正文不侵入页脚或母版 chrome。
- 主体区按 12 或 16 列网格切分；gutter 一致，窄卡减少文字，不靠缩字号硬塞。
- 标题和核心判断先占位，再分配正文区域；标题超载时先压缩或移到 subtitle/source-note。
- 多卡/多格信息密度接近；空卡、只有编号或泛标签时，先补内容或换结构。

## 语义分组

使用 `main-title`、`key-message`、`main-content`、`content-group-1..N`、`source-note`。时间线/流程线只用简单线段、节点、短标签和说明块，不堆装饰、阴影、渐变或背景图。

## Slot 边界

图表、表格、图片证据只在 SVG 中声明槽位和周边说明；真实对象由 renderer 按 `native-data.json` 或 picture bindings 写入。
