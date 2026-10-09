<!--
id: chinese-business-ppt-visual-themes
category: compatibility-index
runtime_scope: legacy
skill_kind: compatibility_index
read_when: 旧提示要求确定中国式 PPT 视觉主题、字体、可见性
page_roles: content, section_divider, summary
supports: svg_drawingml
outputs: visual_theme_reference_route
depends_on: _index/capability-tree.json, contract-visual-token.md
max_use: 只读取本索引、contract-visual-token.md 和 1 个 theme-* 文件
-->

# Chinese Business PPT Visual Themes

本文件是旧视觉入口。具体主题已拆到 `theme-*` 文件。

## 内容说明

视觉主题必须服务内容判断：政务强调落实，金融强调稳健，科技强调能力与增长，培训强调步骤。

## 视觉说明

选定主题后必须写清 `background`、`surface`、`title_text`、`body_text`、`source_text`、
`accent`、`border`，并标明主标题、主体正文、来源文字字号。所有文字、图形、图标和线条
都必须视觉可见。

主题路由：

- 商务浅底：`theme-light-business-blue.md`
- 深蓝强调：`theme-dark-business-blue.md`
- 党政红金：`theme-red-gold-government.md`
- 科技深色：`theme-tech-dark-neon.md`
- 金融银蓝：`theme-finance-silver-blue.md`
- 培训清爽：`theme-training-clean.md`
- 文化青绿：`theme-cultural-green.md`

## SVG说明

所有 `<text>` 必须显式写 `fill`、`font-family`、`font-size`；深色背景黑字直接修正。
