<!--
id: business-pattern-selection
category: content-structure
stage: outline, slide_generation
read_when: 确认 page role 后要选具体业务分析/论证模型(SWOT/PESTEL/五力/3C/BCG/价值链/甘特/桑基/漏斗/瀑布 等)；或需要区分 SWOT 还是 PESTEL、桑基还是漏斗还是树状图
page_roles: content, summary
supports: svg_drawingml
outputs: business_pattern_selection, framework_discriminator
relation_specs: pairs_with:layout-routing-method, pairs_with:content-swot-3c-pest
max_use: 只定 business_pattern 候选与判别；容量拆分读 capacity-and-fallback，证据核对读 evidence-layout-contract
-->

# Business Pattern 选择

`business_pattern` 回答"用什么业务分析或论证模型"。选它靠两条线索：**维度集合/语义**（战略框架）和 **data_shape**（数据形态）。识别不出时留多候选或留空，让系统返回通用组合 fallback，**不要硬套一个错的框架**。

判别时引用真实 pattern id，但每个 pattern 的完整 `input_contract`（required/optional dimensions）由系统在任务包里给出，不要凭记忆背全套维度。

## 战略框架判别（按维度集合区分）

同样是"分析一页"，选哪个框架取决于维度是什么：

- `swot`：内部×外部 与 优劣势 交叉的四象限（strengths / weaknesses / opportunities / threats）。谈的是"我方 vs 环境、好 vs 坏"。
- `pestel`：宏观**外部**环境的具名维度（policy / economy / society / technology，可选 environment / legal），4~6 个。谈的是"外部大势"，不含内部优劣。
- `porter_five_forces`：五种竞争力（现有竞争 / 新进入者 / 替代品 / 买方议价 / 供方议价），固定 5 维，谈"行业竞争结构"。
- `three_c`：Customer / Company / Competitor 三列，谈"顾客需求 × 我方能力 × 竞品差异"。
- `value_chain`：企业活动链（进料—生产—物流—营销—服务…），谈"环节增值"，是链式不是象限。
- 二维矩阵族按**坐标轴**区分：`bcg_matrix`（增长×份额）、`ansoff_matrix`（产品×市场）、`priority_matrix`（影响×难度/重要×紧急）、`scenario_matrix`（两不确定性）、`risk_matrix`（概率×影响）、`decision_matrix`（方案×加权准则）。都是 2×2/网格，选错常是把坐标轴认错。
- `issue_tree` / `business_model_canvas` / `double_diamond`：分别是 MECE 逻辑树、九宫格画布、双钻阶段流，结构强、别名多，按其固有骨架识别。

判别方法与内容槽（每维度写事实/推理/动作，不只写名词）见 `content-swot-3c-pest`。

## 数据框架判别（按 data_shape 区分）

数据页选 pattern 先问"证据是什么结构"：

- `time_series`（随时间变化）→ `trend_analysis`；若是单序列的逐段增减桥接 → `waterfall`。
- 单路径单调收窄的转化 → `funnel`；严格父子层级的占比 → `treemap`。
- **多对多流向**、数据能拆成 source-target-value 三元组、连宽表达规模 → `sankey`；只是类别占比、无明确来源-去向语义时**退化为 treemap/占比图**，不要画伪桑基。
- 位次/梯队对比 → `ranking_analysis`；相关矩阵/热度分布 → `heatmap`；多维能力对比 → `radar`。
- 若干指标+来源+判断，不做大字海报 → `kpi_grid`；多列多行核对+结论 → `table_insight`。

## 规划与执行族

`timeline`（发展历程）/ `roadmap`（阶段规划）/ `gantt`（带依赖排期）/ `process_flow`（步骤流）/ `swimlane`（跨职能责任）/ `milestone`（关键节点）：都可能带时间轴，区别是"讲历程"、"讲规划"、"讲排期依赖"还是"讲责任分工"。

## 选择原则

- 允许多候选：`business_pattern_candidates` 可给 1~2 个，交给系统在 shortlist 里定夺。
- 识别不出就留空，让系统回落通用 composition，绝不用一个不匹配的框架硬套内容。
- 选定 pattern 后核对它的证据合同（见 `evidence-layout-contract.md`）与容量（见 `capacity-and-fallback.md`）再消费 shortlist。
