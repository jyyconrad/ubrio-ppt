<!--
id: chinese-business-ppt-page-roles
category: compatibility-index
runtime_scope: legacy
skill_kind: compatibility_index
read_when: 旧提示要求判断页面角色、论证方式和文案压缩
page_roles: content, section_divider, summary
supports: svg_drawingml
outputs: page_role_reference_route
depends_on: _index/capability-tree.json
max_use: 只读取本索引和 1-2 个对应 reference
-->

# Chinese Business PPT Page Roles

本文件是旧页面角色入口。具体内容已拆到 `content-*`、`layout-*` 和 `anti-pattern-*`。

## 内容说明

- 内容页：读 `contract-content-density.md` 和一个 `content-*`。
- 章节页：读 `layout-section-divider.md`。
- 总结页：读 `layout-summary-action-matrix.md`。
- 标题太空：读 `content-title-rewriting.md`。

正文页必须有观点、证据、解释、影响、行动/风险中的至少 3 类。

## 视觉说明

页面角色决定层级：内容页主标题和核心结论优先，章节页允许更强视觉，但桥接句必须可读。

## SVG说明

主标题组命名 `main-title`，核心判断组命名 `key-message`，内容组命名
`content-group-1..N`，内容区来源命名 `source-note`。
