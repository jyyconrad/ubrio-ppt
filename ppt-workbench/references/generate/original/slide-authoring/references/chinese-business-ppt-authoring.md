<!--
id: chinese-business-ppt-authoring
category: compatibility-index
runtime_scope: legacy
skill_kind: compatibility_index
read_when: 旧提示或工具要求读取中国式 PPT authoring 入口
page_roles: content, section_divider, summary
supports: svg_drawingml
outputs: reference_route
depends_on: _index/capability-tree.json
max_use: 只读取本索引后改用 route_skill_references 工具路由，不要一次读取全部场景
-->

# Chinese Business PPT Authoring Index

本文件是旧入口兼容层，仍采用按需读取。现在中国式 PPT 内容和样式方法已拆到平铺 reference
文件，选取入口是 `route_skill_references` 工具（能力树 `_index/capability-tree.json` 为事实源）。

## 使用方式

1. 用 `route_skill_references` 工具按当前页 requirement/page_role/issues 路由出 2-3 个 reference
   （工具不可用时读 `_index/routing-examples.md` 兜底）。
2. 判断当前缺口：执行合同、视觉主题、页面布局、内容结构、场景模板或反例 QA。
3. 只读取路由返回的 2-4 个具体 reference。
4. 不要一次读取全部 `scenario-*`、`layout-*`、`theme-*`、`content-*` 文件。

## 快速路由

| 缺口 | 优先读取 |
| --- | --- |
| 不知道怎么开始写 SVG | `contract-svg-page-workflow.md` |
| 视觉主题、颜色、字号不清 | `contract-visual-token.md` + 一个 `theme-*` |
| 内容过简、只有口号 | `contract-content-density.md` + 一个 `content-*` |
| 主体空白、章节号抢标题 | `contract-layout-density.md` + 一个 `layout-*` |
| 只有场景/主题，缺页面内容 | 一个 `scenario-*` + 一个 `content-*` |
| 已知错误需要修正 | 对应 `anti-pattern-*` |

## 旧分类入口

旧 `chinese-business-ppt-scenarios.md`、`chinese-business-ppt-structures.md`、
`chinese-business-ppt-page-roles.md`、`chinese-business-ppt-layouts.md`、
`chinese-business-ppt-visual-themes.md`、`chinese-business-ppt-storytelling.md`、
`chinese-business-ppt-case-templates.md` 仍保留为兼容索引。具体正文以
`_index/capability-tree.json` 收录的平铺 reference 为准。
