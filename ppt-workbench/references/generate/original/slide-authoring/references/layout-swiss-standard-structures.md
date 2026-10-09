<!--
id: layout-swiss-standard-structures
category: layout
module_type: layout_family
read_when: Swiss 页面是封面、目录、陈述、四卡、六格、三支撑或横向时间线
page_roles: cover, agenda, content, section_divider, summary
stage: slide_generation
supports: svg_drawingml, validate_svg_drawingml, render_svg_drawingml_slide
outputs: swiss_standard_structures, svg_layout
depends_on: layout-swiss-core-grid.md, narrative-swiss-copywriting.md
relation_specs: requires:layout-swiss-core-grid, pairs_with:narrative-swiss-copywriting
max_use: 只讲标准 Swiss 结构，不讲指标账单或复杂图表
-->

# Swiss Standard Structures

按内容形态选结构骨架，选定后再用 `narrative-swiss-copywriting.md` 决定每类字段的口吻和字数。

## 结构

- `cover`：大标题 + 副标题 + 短标签；适合封面、章节首页、主题宣言。
- `agenda/toc`：序号列 + 章节标题 + 页码/状态列；不要画成六张定义卡。
- `section_divider/key_takeaway`：单句陈述放大，保留少量归因或说明。
- `timeline/process`：水平节点线，3-7 个节点，每个节点有 label / year / description。
- `four_cards`：四项机制、策略、风险或能力模块；正文过长时改 2x2。
- `six_cells`：六个并列定义、术语解释或能力盘点；少于或多于 6 项时换结构或拆页。
- `three_support`：一个 lead + 三条支撑；lead 必须是真判断，三卡承载不同证据角度。

## 容量

四卡每卡标题 ≤18 字、正文 ≤50 字；六格每格标题 ≤16 字、正文 ≤36 字；横向时间线 3-7 节点，节点标题 ≤16 字、说明 ≤40 字。超载先改写、合并或拆页。

## 禁止

不要把目录页误画成六格定义页；不要把六项并列内容塞进 agenda；不要让 Swiss 标题变成空泛名词短语。
