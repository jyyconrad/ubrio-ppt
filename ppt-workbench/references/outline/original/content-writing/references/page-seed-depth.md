<!--
id: skill-section/page-seed-depth
module_type: skill_section
category: content-structure
stage: outline
page_roles: content, summary
content_categories: content_structure,page_seed
skill_types: content_writing,skill_section
summary_categories: skill_section_summary,content_structure
triggers: 逐页素材, 素材深度, 页面种子, 页面seed, 成稿过浅, 逐页输入包, 必须出现的数据点, 内容过素, seed深度
priority: P1
read_when: 把大纲/母稿细化为逐页生成输入（seed / page_spec 输入包）时，或成稿反复过浅时
max_use: 只约束逐页输入包的深度字段，不替代页面生成本身
outputs: page_seed_fields, seed_depth_checklist
-->

# Page Seed Depth

## 因果律：成稿深度上限 = 输入包深度

单页成稿的深度，上限被它的输入包（seed / page_spec）深度锁死。编写端的密度合同只能防"**有料不写**"，防不了"**无料硬写**"——输入包本身单薄时，密度合同逼出来的只会是注水和口号。

所以：**页面反复过浅，先修 seed，不修 prompt**。反复调生成提示、加"要写得充实"这类指令，是在错误的环节使劲；正确动作是回到 outline，把这一页的输入包补深。

## 逐页输入包最小语义

把大纲细化为逐页输入时，每页至少覆盖这些语义，成稿才有深度可依。当前简化大纲把它们统一写入页面 `content`，不要自行扩展内部 schema：

- **观点句标题**：一句有判断的观点，不是"业务概况"这类栏目名。
- **核心结论**：本页要立住的一句话判断。
- **必须出现的数据点清单**：逐条写 **值 + 口径 + 来源 + 时间**。这是本页最硬的深度来源，也是内容审核逐条核对的对象。
- **内容组**：按 claim / evidence / explanation / implication / action 的语义拆开写，不是一段素材摘要。
- **来源清单**：本页所有可引用来源，保留 URL / 发布方 / 时间。
- **图片 / 截图候选**：本页需要的背景图、证据截图或配图线索（含入池引用，见 `outline-background-materialization.md`）。
- **按页 content / visual 审核检查点**：把"这一页最该被审什么"前置写进 seed（如"某数据是预测值，不能写成已发生"）——这是把页面特有风险交给 reviewer 的关键机制。
- **主要风险**：本页最容易做错什么（口径错、编号错序、改写失义、密度过素）。

审核检查点写进 seed，是把风险从"生成后才发现"提前到"生成前已声明"，直接喂给 `slide-authoring:contract-review-baseline-discipline` 的内容审核。

## 常态豁免

封面 / 目录等固定页的 `structure_hierarchy` 为空是**正常**的（校验只提 warning），不要为固定页硬造五层结构或硬塞数据点清单。豁免只针对固定页；正文页缺字段仍按缺口处理。

## 机器 / 语义分工

- **交校验器**（机器可判）：字段完整性、死链、来源引用是否存在、页码 / 编号连号。
- **语义判断**（人 / 内容审核判）：数据点齐不齐、口径标没标、结论句强不强、改写有没有失义。机器查不了这些，别指望校验器兜住内容深度。
