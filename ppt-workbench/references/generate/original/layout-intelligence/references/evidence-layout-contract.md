<!--
id: evidence-layout-contract
category: execution-contract
stage: slide_generation
read_when: 选证据型版式(分析框架/指标/案例)前要核对证据形态是否达标(每维度有事实/推理、需要来源时有来源)；或证据缺口时先补齐再锁版
page_roles: content, summary
supports: svg_drawingml
outputs: evidence_layout_contract, evidence_gap_action
relation_specs: pairs_with:layout-routing-method, pairs_with:content-evidence-gap-labeling
max_use: 只讲证据-版式匹配合同与缺口动作；证据缺口标注写法读 content-evidence-gap-labeling
-->

# 证据-版式合同

有些版式对证据有**结构化要求**：选它之前先核对证据形态，否则会把分析退化成图标海报或空槽占位。核对不过关时先补齐证据，再锁版式。

## 证据项最小形态

证据型版式的每条证据应能拆成：

- `dimension_id`：它归属哪个维度（如 PESTEL 的 policy、五力的 rivalry）。
- `statement`：一句事实或推理，不只写名词。
- `source`：需要来源时的出处（数据/政策/案例/专家判断）。
- `kind`：`fact`（事实）还是 `inference`（推理），二者都可，但要可辨。

## 合同核对（锁版前）

选中一个证据型 pattern 后，对照它的 `evidence_contract` 逐条核对：

- **每个必填维度都有事实或推理**：`minimum_evidence_per_dimension` 要求每维度至少一条实证；只有维度名、没有内容的维度算不达标。
- **需要来源时留了来源**：`source_required=true` 的 pattern（如 `pestel`、`kpi_grid`、`sankey`、`porter_five_forces`），每条硬数据/关键判断要能追溯来源。
- **口径可辨**：内部测算、单一厂商案例、能力示意类数字不得写成普适事实，在紧邻文案或该页唯一来源行标注口径。

## 缺口动作（先补齐，不空塞）

证据不达标时的顺序：

1. **先补齐**：走素材读取、素材整理或公开检索补足事实与来源。
2. **补不齐则降级**：把强证据结构降级为更低证据要求的结构（如从"每维度带来源的分析框架"降到"要点列表 + 明确风险边界"），或明确标注为待确认的判断边界。
3. **仍不行则询问用户**：身份/证据型缺口（真实数据、案例、来源）用占位方式向用户要，不用生成内容冒充。
4. **绝不渲染空证据槽**：不留只有维度名、没有事实/来源的空卡赌渲染兜底；证据缺口的标注写法见 `content-evidence-gap-labeling`。

## 哪些角色需要证据

- **需要**：`analysis_framework`、`metrics`、`case_evidence`、`risk_issue`、`result_summary` —— 这些页的说服力来自证据密度。
- **不强制**：`cover`、`section_divider`、`agenda`、`closing`、`statement` —— 以主张/结构/情绪为主，不套每维度证据合同。
