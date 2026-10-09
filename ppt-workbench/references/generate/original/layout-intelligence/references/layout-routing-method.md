<!--
id: layout-routing-method
category: capability
stage: slide_generation
read_when: 当前页要从"业务问题"落到"用哪种信息结构/版式"，需要一套稳定选版方法；或系统在任务包里注入了路由指纹与候选版式(shortlist)需要消费
page_roles: content, summary
supports: svg_drawingml
outputs: routing_method, shortlist_consumption, fallback_decision
relation_specs: pairs_with:structure-hierarchy
max_use: 只提供选版方法骨架；维度判别、容量拆分、主题分离、证据合同读对应 reference，不在此展开
-->

# 版式路由方法（选版骨架）

选版式不是"看标题挑一个好看的结构"，而是从**当前页真实要证明的业务判断**出发，逐层收窄到一个可执行版式。全过程六步，每一步都可复用到相似但不同的页面。

## 六步方法

1. **识别业务问题**：这一页要回答什么、要让用户接受什么判断、有哪些证据。先看内容，不看标题措辞。
2. **确认 page role**：这一页在汇报里承担的**业务职责**（20 类稳定角色之一，见 `page-role-disambiguation.md`）。角色是职责，不是视觉形态。
3. **选 business pattern**：用什么分析/论证模型（SWOT、PESTEL、五力、KPI、甘特、桑基…，见 `business-pattern-selection.md`）。识别不出就留多候选或留空，不硬套。
4. **核对 data / evidence shape**：证据是什么结构（时间序列、并列维度、占比、多对多流向、矩阵…），是否满足该 pattern 的证据合同（见 `evidence-layout-contract.md`）。
5. **评估代码返回的 composition / layout shortlist**：系统按容量、证据、主题、renderer、成熟度过滤后返回**一个主推荐 + 2~4 个备选**。把它作为高置信能力候选逐个核对，不把 top-1 当固定答案。
6. **声明实际决策并填充**：适配时采用可验证的 catalog variant；都不适配时加载相关方法/example，设计并声明 `custom_composition`（见 `layout-decision-and-custom-composition.md`）。目录版式按 slot/capacity 填充；自定义结构仍要过通用容量、可读性、renderer 和 QA。

## 路由指纹（心智清单）

选版前先在脑内（或消费系统注入的指纹）明确这些量，它们决定 shortlist：

- `page_role`：业务职责（步骤 2）。
- `business_pattern_candidates`：候选分析模型，可多个、可留空（步骤 3）。
- `data_shape`：证据结构（`time_series` / `categorical_dimensions` / `part_to_whole` / `network_flow` / `matrix` / `ranking` / `single_metric` …）。
- `item_count` / `hierarchy_depth`：并列条目数、层级深度——直接决定容量是否够。
- `evidence_mode` / `source_required`：是否需要每维度事实/推理、是否必须留来源。
- `visual_mode`：`data_dominant` / `image_dominant` / `ambient` …，是**呈现方式**，不占用 page role。
- `theme_polarity`：深/浅极性，是硬约束（见 `theme-structure-separation.md`）。

## 消费 shortlist 的纪律

- **先评估 shortlist**：主推荐通常最贴表达主轴；备选用于容量、证据或主题不匹配时替换。采用某项时必须使用它真实的 catalog id 和合同。
- **shortlist 为空、blocking 或全部不适配**：不要猜 layout id。可改走 fallback（换 pattern、降级、拆页、补证据），也可以基于已加载的 SOP/example 设计可执行 `custom_composition`；custom 不得携带 catalog layout_id。
- **shortlist 外的目录版式**：只有 Provider 可解析、renderer route 可执行、容量和固定页型约束都通过时才可采用；否则用 custom 表达真实身份。
- **role/pattern 与业务语义不符**：可带更准确的 role/pattern 参数让系统重算 shortlist；版式选择的最终落账在代码侧，你提出更好的判断，不直接改写版式库。

## 失败信号

- 只凭标题关键词套结构（见 `anti-pattern-layout-by-title-only.md`）。
- 背诵或扫描整个版式库、猜测不存在的 layout id，或让自定义结构冒用目录 layout id。
- 用主题名（"深色商务风"）替代信息结构选择。
- 容量已 blocking 仍继续硬塞内容或压字号。
- 该有证据的维度只写名词、无事实/推理/来源。
