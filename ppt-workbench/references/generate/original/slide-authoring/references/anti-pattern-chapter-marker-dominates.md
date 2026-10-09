<!--
id: anti-pattern-chapter-marker-dominates
category: anti-pattern-qa
read_when: 章节编号、PART、页码、装饰标签出现在 SVG 或抢主标题
page_roles: content, section_divider
supports: svg_drawingml
outputs: fix_rules
depends_on: contract-layout-density.md
max_use: 只读取本文件，不要连带读取同类全部文件
-->

# Anti Pattern: Chapter Marker Dominates

## 内容说明

章节标识是导航，不是页面观点。内容页的受众首先要看到主标题和核心判断；章节、页码、
进度和顶部标签由框架层统一生成，不进入 SVG 内容层。

## 视觉说明

错误：

- 巨大 `01` 占据最大留白。
- `PART 1` 字号大于主标题。
- 页码或标签压住标题区。

修正：

- 删除 SVG 内章节标识、页码、顶部胶囊和进度标签，只在 `stage_label` 或页面元数据中记录。
- SVG 内容层保留 `main-title-block` / `main-title` 和 `key-message`。
- 如果需要章节导航，等待 PPT 框架层按全 deck 背景、母版和页码统一生成。

## SVG说明

不得在 SVG 中使用 `chapter-marker`、`eyebrow`、`page-header`、`topbar` 或类似组来画页眉导航；
主标题放 `main-title-block` 或 `main-title`。
