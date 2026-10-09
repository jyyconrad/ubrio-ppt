<!--
id: capacity-and-fallback
category: execution-contract
stage: slide_generation
read_when: shortlist 里的版式装不下当前内容(维度/条目/字数/层级/媒体超容量)；或需要在压缩/换更高容量结构/拆页/询问用户之间决策；或命中 capacity blocking 信号
page_roles: content, summary
supports: svg_drawingml
outputs: capacity_check, fallback_or_split_decision
relation_specs: pairs_with:layout-routing-method, pairs_with:layout-density
max_use: 只讲容量判断与降级/拆分决策；具体密度铺满口径读 layout-density
-->

# 容量核对与 Fallback

选中的版式必须**装得下且装得舒服**。容量是硬约束：装不下时不是压字号硬塞，而是按固定顺序降级。系统会做确定性容量硬过滤并给 blocking 信号，你的职责是尊重这个信号、做压缩/换结构/拆页/询问的决策。

## 先估载荷，再比容量

选版前估四个量，和 composition 的容量区间比对：

- `item_count`：并列维度/卡片/步骤数。
- `char_budget`：每个 slot 的正文字数（标题、正文、指标、来源分别估）。
- `hierarchy_depth`：层级深度（金字塔/树/架构常见 2~3 层）。
- `media_count`：图片/图表/截图槽数量。

## Blocking 时的降级顺序（固定四步）

命中容量 blocking 时，**按顺序**决策，能在前一步解决就不进下一步：

1. **压缩**：合并语义相近的卡片、把描述摘要化、把次要维度并入"其他"、把来源合并成一句。信息不足的卡片合并成更少的实卡，不画空卡占位。
2. **换结构**：优先换 shortlist 中更高容量的备选 composition；若候选都不适配，可声明一个不冒用 catalog id 的 `custom_composition`，但仍要给出容量理由并通过通用 validator/renderer/QA。
3. **拆页**：按维度分组或按阶段切分成多页，每页承载一个可读子集。拆页由后续导出合并，不在当前页硬拼。
4. **询问用户**：内容确实超载且无法取舍时，向用户澄清优先保留什么，不擅自砍关键信息。

## 常见容量红线

- **PESTEL 4 维**不能塞进 3 卡版式；4~6 具名维度用维度卡网格。
- **8 个流程步骤**不能压进 max 5 的流程版式 → 分组或拆页。
- **指标海报反模式**：`kpi_grid` 指标数超容量或缺来源时，不要放大成"大字海报"，超限就换结构或拆页。
- **多对多流向**超过约 3~12 条路径时聚合长尾为"其他"或拆页，避免连线过密难辨读。
- **表格**列数/行数/字符超限必须换 layout 或拆页，不逐单元格塞微型字。

## 最小可读性与硬边界

- 放不下就重排、摘要化、拆页或询问用户，**不许微型字硬塞**（主体正文、图表标签、来源各有最小字号，具体口径以渲染前门禁为准）。
- 不用渲染试错来"发现"装不下：容量在选版阶段就要判断；blocking 是设计信号，不是等渲染失败再补救。
- 密度是双向的：底部/右侧大面积连续空白同样要改（铺满纪律见 `layout-density`），不是只防溢出。
