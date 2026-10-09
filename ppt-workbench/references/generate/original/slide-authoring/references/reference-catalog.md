<!--
id: reference-catalog
category: metadata-catalog
runtime_scope: legacy
skill_kind: compatibility_index
read_when: 仅历史兼容; 选 reference 请改用 route_skill_references 工具或 _index/routing-examples.md
page_roles: content, section_divider, summary
supports: svg_drawingml
outputs: reference_selection
depends_on: _index/capability-tree.json
max_use: 不再作为主索引; 路由统一走能力树 + route_skill_references 工具
-->

# Reference Catalog（已降级）

本文件已从"模型扫描的主索引"降级为历史兼容指针。**reference 元数据的单一事实源是
`_index/capability-tree.json`**，选 reference 的入口是语义筛选工具
`route_skill_references`。

不要再逐行扫描本文件挑 reference。改用以下任一方式：

1. **语义筛选工具（首选）**：调用 `route_skill_references`，传入 `skill_id="slide-authoring"`
   和当前页 `requirement` / `page_role` / `issues`，按返回的 `recommended` 读取 2-3 个文件。
2. **人工兜底映射**：工具不可用时读 `_index/routing-examples.md`（常见问题 → reference 固定
   映射，与能力树同源）。

每次仍先读 `drawingml-svg-authoring.md`（SVG 可转换硬合同）。能力树覆盖全部内容 reference；
新增 reference 时只在 `_index/capability-tree.json` 追加节点，无需回填本文件。
