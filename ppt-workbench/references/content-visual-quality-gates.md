# 内容与视觉质量门

这份参考用于大纲确认、逐页生成和整册合并前的质量检查。它补充 `build_gold_svg_page.py` 的结构检查；`quality_status=ready` 不代表内容和视觉已经可交付。

## 整册内容合同

先建立一份 deck manifest，再开始逐页制作。至少包含：

```json
{
  "thesis": "整册只回答一个判断",
  "audience_decision": "会议结束前要拍板的事项",
  "evidence_ladder": ["external_fact", "internal_observation", "proposal", "pilot_target"],
  "canonical_metrics": [],
  "canonical_products": [],
  "canonical_artifacts": [],
  "canonical_stages": [],
  "canonical_owners": [],
  "reference_assets": []
}
```

`evidence_ladder` 不是页序装饰，而是证据状态：外部事实说明背景，内部观察说明问题，方案说明取舍，试点目标说明如何验证。每页必须写 `proves`，并能在 `claim→evidence→action→validation→decision` 链中找到上游证据和下游动作。没有上游证据的建议降级为待验证假设；没有下游动作的背景页应合并、补证据或删除。

## 同一份规格，两个校验面

金标 builder 和整册 validator 共用作者规格，但检查不同字段。`quality_status=ready` 不代表整册字段已齐；下面这些字段要在开始画页前补入同一份 `page_spec.json`，不是结束时另造一份“通过版”。完整可运行示例见 `assets/examples/blue-dense/result-dashboard.page_spec.json` 与 `deck-manifest.json`。

| 字段 | 写什么，以及怎样核对 |
| --- | --- |
| `proves` | 引用 thesis 的一个完整分句，逐字一致；页面可用更自然的标题，但不能把无关结论挂上 thesis。 |
| `baseline_status` | 明确 `internal_baseline`、`observed`、`not_applicable` 或没有内部基线的实际状态；有时序图时必须有可追溯基线。 |
| `supporting_points` | 2–3 个支撑关系，区别于物理卡片数；至少有一个 `role: evidence/fact/observation` 和对应 `source_ref`、`limitation`，或给完整 `evidence_refs`。 |
| `plain_language_test` | 分别写 `what_happened/why_it_matters/what_next`，不是重复抽象标题。 |
| `density_budget` | 写本页目标 `min_unique_factual_atoms/min_relation_edges/min_evidence_bearing_objects/min_body_font_px`，正文下限至少15px；它是作者预算，不能替代预览计量或目检。 |
| `skeleton_id/same_skeleton_run` | 按最终页序标记真实骨架与连续次数；不是随意填不同编号。 |
| `evidence_state/claim_type/evidence_type` | 记录本页主证据；每项指标仍保留自己的元数据，异质证据不混成一个事实标签。 |
| `visual_brief/example_refs/reference_dna` | 记录实际读取的参考、信息关系与具体落地；不是通过状态。 |
| `metrics/products/artifacts/stages/owners` | 与 manifest 中 canonical 清单同名。延期分项、目标指标等也要登记；普通 `groups` 标题不是产品清单。无相关对象时明确不适用，不能为了清单造产品或Owner。 |

整册 `--pages-dir` 当前读取目录直属的 `*.json`，不会递归扫描 `pages/page-01/page_spec.json`。保留逐页源文件，同时把同一规格放入专用 `deck-contract-pages/page-01.json`、`page-02.json` 等目录（或将规格作为 manifest 的 `pages[]`）；不要传包含其他 JSON/报告的目录。

```bash
python3 scripts/validate_deck_contract.py \
  --manifest deck_manifest.json --pages-dir deck-contract-pages
python3 scripts/svg/check_deck.py \
  pages/page-01/page_spec.json pages/page-02/page_spec.json
```

出现 blockers 或 `missing` 时继续修复最早的字段、口径或结构问题，再运行对应校验。若只是补充已有证据的作者元数据，核对与最终页面一致；若数字、结论、对象或字体改变，则重新生成和检查最终 PPTX。文件可以作为草稿保留，但阻断项未解时不能把任务收口为验收完成。

## 全局视觉系统与逐页视觉简报

上述 manifest 内容字段还须补上 [全局视觉系统](visual-system.md) 中的 `visual_system`，再写正文页的 `visual_brief`（构图、视觉焦点、背景、元素位置）。实际检查时，构图要与 `dominant` 一致，焦点按页型对应判断、主证据、关键关系或待拍板项，背景和材质不能降低表头、数据及来源的对比度。整页视觉样机按需要使用，不能代替可编辑成品。

## 一页一个主观点

整册前后呼应和每一页的主导信息关系按 [叙事与形状](outline/narrative-shape.md) 写，不在这里重写。首页和末页同一句 `thesis`，中间页 `proves` 引用这句；页面只有一个 `dominant` 关系，但可以有多个相连的证据区。蓝色高密度页的分区与可观察验收见 [复合页型](blue-dense-report.md)。

每页正文先写一条 `primary_claim`，它必须是完整的判断句，能回答“这页要听众记住什么”。`key_message` 与它保持同一含义，不能再承担第二个结论。`primary_claim` 与 `thesis` 或本页 `proves` 说的是同一件事。

- 支撑内容最多保留 2–3 个主点，分别标明是事实、解释、限制、风险或行动。
- 标题 → 主观点 → 主证据 → 影响/限制 → 行动或决策，形成一条主要阅读路径。
- KPI、机制、风险、原则和行动同时出现时，只有一个负责证明主观点，其余降级为辅助信息；无法降级的内容拆到下一页。
- 在预览检查中用一句话复述本页。如果复述需要把多个卡片拼接起来，说明层级仍未成立。

`page_spec.json` 至少保留以下作者元数据；渲染器未读取的字段也必须先通过人工质量门：

```json
{
  "primary_claim": "一句完整判断句",
  "key_message": "与 primary_claim 同义的结论句",
  "supporting_points": [
    {"role": "evidence", "text": "直接支撑主观点的事实"},
    {"role": "limitation", "text": "证据不能推出什么"},
    {"role": "action", "text": "下一步动作或待拍板项"}
  ]
}
```

## 先把话说成人话

标题、`key_message`、卡片标题和动作文案都要能让不熟悉项目的听众快速理解。

- 优先使用自然主语、动作、对象和结果：谁在什么场景遇到什么问题，要做什么，预期改变什么。
- 避免连续堆叠抽象名词、把多个判断压进一句话，或用听众没有上下文的模型术语替代事实。
- 第一次出现的内部术语、等级或缩写必须就地解释；不能用口号、名词短语或“端到端”“全流程”等范围词代替结论。
- 卡片按“事实 → 影响 → 动作”组织；没有事实时明确写“待验证”，不要用确定语气填补空缺。
- 做一次非专业听众复述测试：只看标题和主证据，能否用自己的话说出发生了什么、为什么重要、下一步是什么。不能复述就继续改写或拆页。

## 证据边界与跨页一致性

每个数字或强判断都要靠近标注证据边界，至少记录：

`claim_type`（事实/相关/机制假设/建议）、`evidence_type`（实验/调查/内部基线/公开资料/政策）、`evidence_state`、`population`、`period`、`denominator`、`source_ref` 和 `limitation`。

`evidence_state` 只使用以下可见标签：`FACT`（直接来源事实）、`OBSERVED`（内部已观察）、`PROPOSAL`（设计建议）、`TARGET`（试点目标）、`TO_VALIDATE`（待验证或待采集）。标签应出现在数字、图形或主证据旁，不能只藏在低对比度脚注中。

- 实验、调查、自报、相关关系和内部基线不能在同一 KPI 带中并列成可比结果；除非分母、样本和口径确实一致，并在数字旁显式标注。
- 只有直接证据才能使用“导致、必达、必须、已升级”等强因果或强处方词。相关调查、品类存在性和概念模型应写成“提示、可能、假设、待内部验证”。
- 没有数据、单位、坐标和来源时，不画带端点或趋势语法的实证图；改用明确标注“示意/机制假设”的关系图。
- 没有 `internal_baseline` 时，不能使用“现状”“已提升”“当前水平”“实绩”等已证实语气，也不能画有时间轴和端点的目标折线；目标值优先用目标卡、原生表格或阶段退出条件。若必须画机制图，必须使用示意样式并同时写清假设和待采集字段。
- 整册的指标定义、产品清单、工件字典、阶段名称、Owner 和术语必须来自同一份清单。跨页出现新增或改名时，先补映射再生成。
- 阶段门禁必须闭合为 `artifact → check → threshold → approver → evidence_ref → exception_policy`；只有方向词或原则句不能作为放行条件。
- 决策页至少写清选项、判断标准、Owner、截止时间、成本/风险、可逆性、拒绝条件和下一步证据。没有内部基线时，使用“待采集基线/试点指标”，不要伪装成现状 KPI。
- 只有页面同时提供 Responsible、Accountable、Consulted、Informed 的角色映射时才使用“RACI”；“AI 可做 / 人必须做 / 共担”这类三列应命名为责任边界，不得借用 RACI 标签。

产品、工件、门禁和决策需要落到可执行字段：

- 产品对照至少有 `product`、`task_surface`、`context_access`、`action_boundary`、`verification`、`permission_or_audit`、`deployment_or_data`、`cost_or_unknown`、`fit_for_pilot`、`source_ref`。
- 工件字典至少有 `artifact`、`purpose`、`required_fields`、`producer`、`consumer`、`version`、`evidence_location`；页面不得临时改名或新增同义工件。
- 门禁至少有 `stage`、`artifact`、`check`、`threshold`、`evidence_ref`、`approver`、`exception_policy`、`next_stage`。
- 决策项至少有 `decision`、`options`、`criteria`、`recommendation`、`owner`、`deadline`、`cost_risk`、`reversible`、`reject_if`、`next_evidence`、`consequence_if_deferred`。

没有页内专属证据、限制和动作时，不能用通用的 `metrics`、`evidence_boundary` 或 `action` 默认值补齐；跨页重复数字或动作必须说明本页新增用途，否则直接删除。

## 表格语义路由

左右对照保持两块面板。有列标题、至少三行同类数据，或听众需要编辑、复制、排序和复用时，才按表格处理：

1. 优先使用 `native-table-slot` + `native-data.json` 的 `tables[]`；有现成 HTML 编辑链路时可使用可编辑 HTML table。
2. SVG 只承载表格的标题、注释、状态标记和外框，不绘制单元格网格、行列数据或靠多个 `rect`/`text` 拼成“看起来像表格”的内容。
3. 生成后检查 PPTX 中确实存在可编辑表格对象，列标题、行语义、单位和来源完整；不能只检查截图或 SVG 预览。
4. 只有原生/HTML 表格链路确实不可用时才允许 fallback，并在任务目录记录原因、影响和后续可编辑性限制；不能把 fallback 当默认路径。

## 视觉与整册节奏

- SVG 正文默认不低于 15px；最终 PPTX 的正文、表格和关键动作不得低于约 11pt。最小字号低于该值只能用于来源或注释，并记录例外。蓝色高密度页应先换短句、标签列、微图和关系线，再考虑把普通大字缩到此下限。
- 表格/多栏卡片要检查每格最大行数、字符数和最小列宽。超出容量时先拆页或减少次要信息，不靠缩小字号解决。
- 同一 deck 的“标题 + KPI 带 + 深色分区条 + 白卡 + 底部 takeaway”骨架最多连续复用两页；顶部 KPI、底部结论带和分区条都要有复用上限。
- 有数据语法的图形必须有数据、单位、来源和图例；概念关系图使用单独的“示意/机制”视觉语法，不能让线条和端点冒充实证结果。
- 证据类型、样本/口径和限制要出现在数字附近，完整引用再放来源行；不能把关键边界压成低对比度脚注。
- 导出后核对最终 PPTX 的实际字体、回退字体、标题断行和表格断行，必须与设计契约一致。
- 密度检查同时记录 `unique_factual_atoms`、`relation_edges`、`evidence_bearing_objects`、`table_cells` 和 `tiny_text_ratio`；shape 数量高不能证明信息密度高。空白卡片应减高、补证据或改成更合适的页型。
- 同一 deck 的页型骨架最多连续两页；用户参考图和样例只能迁移构图关系、组件语法和密度，必须记录 `example_id`、`reuse_reason`、`adaptations`，若未复用则写 `not_reused_reason`。
- 当 manifest 有 `reference_assets` 时，每个正文页还要写 `reference_dna`（面板层级、关系、节奏或组件语法）；只复制颜色不算复用。固定页可以用 `not_reused_reason` 说明职责。
- 对蓝色高密度参考，`reference_dna` 还要指出实际选择的包内图片、正文区域组合、蓝色导航、数字/条件焦点和底部收口。最终预览与图片并排核对；只写字段或摆出同色大卡不算视觉复用。
- `page_spec` 还要记录 `skeleton_id` 和 `same_skeleton_run`；后者按页序计算，超过 2 页就换主体形状、阅读方向或证据类型，不能只换颜色和标题。

## 视觉复核最低动作

完成前至少检查 contact sheet、100% 单页 PNG 和一次远距阅读：

- 3 秒内能说出每页主观点；
- 远距能读出关键数字、动作和表头；
- 没有中文缺字、截断、重叠、伪图表或伪表格；
- 来源、限制和证据类型不会因低对比度而消失。

如果当前环境没有渲染或目检能力，必须在交付说明中写明“已检查原生对象，未完成视觉验收”，不能把结构通过写成视觉通过。

最终报告至少分开输出：

```text
content_logic_passed: true|false
density_passed: true|false
example_reuse_passed: true|false
visual_system_passed: true|false
visual_brief_passed: true|false
structure_passed: true|false
visual_review: performed|not_performed
powerpoint_roundtrip: performed|not_performed
blockers: []
```

上述静态 `*_passed` 字段从 `validate_deck_contract.py` 的实际 JSON 逐项引用，同时保留 `evidence_boundary_passed`、`cross_page_consistency_passed`、`baseline_target_rule_passed`、`table_semantics_passed` 及 blockers/warnings；`structure_passed` 来自最终 PPTX inspector。视觉、字体与 PowerPoint 往返状态另外写，不能将脚本失败省略为“已完成三页”。

`structure_passed=true` 只表示文件和对象结构符合检查器，不代表内容逻辑、密度、参考复用或视觉验收通过。

多页任务把上述字段交给 `scripts/validate_deck_contract.py` 做静态预检；它阻断缺失的整册/页级合同、重复默认字段、没有内部基线的折线、需要表格却没有原生表格、缺少视觉系统/视觉简报和未记录样例复用。报告 `validation_scope=declared_contract_only`；它不读取 PNG，不能判断审美或证明作者元数据已进入渲染器，也不替代 `inspect_pptx.py`、contact sheet 或人工目检。
