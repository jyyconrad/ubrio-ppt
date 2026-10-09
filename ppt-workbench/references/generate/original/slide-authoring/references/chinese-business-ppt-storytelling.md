<!--
id: chinese-business-ppt-storytelling
category: compatibility-index
runtime_scope: legacy
skill_kind: compatibility_index
read_when: 旧提示要求完整叙事线、开场钩子、桥接句或收尾
page_roles: section_divider, summary, content
supports: svg_drawingml
outputs: storytelling_reference_route
depends_on: _index/capability-tree.json
max_use: 只读取本索引和 1-2 个具体 reference
-->

# Chinese Business PPT Storytelling

本文件是旧叙事入口。具体执行优先使用 `content-scqa.md`、`layout-section-divider.md` 和
`layout-summary-action-matrix.md`。

## 内容说明

- 开场钩子：用数据、痛点或冲突引出，不只写口号。
- 桥接句：说明为什么进入下一章。
- 收尾：写结论、行动、风险或资源诉求。

## 视觉说明

桥接句用 `subtitle` 或 `key-message`，不要放成页脚小字。总结页行动要突出。

## SVG说明

开场页可用 `hook-data`、`pain-point`、`main-title`。过渡页用 `section-title`、
`main-title`、`bridge-sentence` 表达章节主题；章节编号、页码和进度导航交给框架层。
总结页用 `summary-points`、`action-matrix`。
