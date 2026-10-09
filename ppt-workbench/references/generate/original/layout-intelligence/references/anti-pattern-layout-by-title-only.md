<!--
id: anti-pattern-layout-by-title-only
category: anti-pattern-qa
stage: slide_generation
read_when: 只凭标题关键词就套版式(标题带"对比"就上四象限、带"流程"就横向步骤、带"趋势"就画大趋势图)，没核对真实内容的 role/pattern/data_shape/条目数
page_roles: content, summary
supports: svg_drawingml
outputs: title_trap_checklist, content_first_routing
relation_specs: pairs_with:page-role-disambiguation, pairs_with:business-pattern-selection
max_use: 只列标题陷阱与内容优先纠偏；正向选版方法读 layout-routing-method
-->

# 反模式：只看标题就套版式

## 失败信号

看到标题里的一个关键词就直接映射到某种结构：标题带"对比"就上四象限，带"流程"就横向步骤条，带"趋势"就画满屏折线图，带"分析"就套 SWOT。没有核对真实内容的 page role、business pattern、data_shape 和条目数。

## 为什么会错

**标题措辞 ≠ 信息结构**。同一个词后面可能是完全不同的数据形态：

- "我们的三大优势" —— 是三个**并列**能力（`parallel_cards`），不是"我方 vs 竞品"的 `comparison`。
- "增长趋势" —— 如果只有一个同比数字，是 `single_metric`（`metrics`/`statement`），不是要画时间序列图的 `trend`。
- "竞争格局对比" —— 若是 4 个宏观维度各给影响，其实是 `analysis_framework`/`pestel` 的维度卡，不是两栏 versus。
- "实施流程" —— 若讲的是几个阶段的**前后因果与里程碑**，更接近 `timeline`/`roadmap`，而非等距步骤条；若是跨部门责任，是 `swimlane`。
- "资金流向" —— 只有类别占比时是 `distribution`/占比图，只有拆成 source-target-value 多对多才是 `sankey`，别凭"流向"二字画伪桑基。

## 正确方法（内容优先）

1. 先读**真实内容**：有几组信息、什么关系（并列/递进/因果/对比/流向/层级）、有没有数据、数据是什么形态、有没有证据和来源。
2. 从内容推出 `page_role` + `business_pattern` + `data_shape`（见 `page-role-disambiguation`、`business-pattern-selection`）。
3. 再消费系统返回的 shortlist 选版式（见 `layout-routing-method`），而不是用标题直接映射。

## 自检清单

- [ ] 我选这个结构，是因为**内容关系**如此，还是因为标题里有那个词？
- [ ] 并列的 N 组信息，真的是"对比/递进/流向"，还是只是并列？
- [ ] 带"趋势/流程/流向"的页，数据形态核对过吗（几个点、单序列还是多对多）？
- [ ] page role 与 business pattern 是从内容推出的，不是从标题猜的？
