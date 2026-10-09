<!--
id: skill-section/outline-criteria
module_type: skill_section
category: content-structure
stage: outline
ppt_types: business_consulting,project_report
content_categories: outline_criteria,content_structure
skill_types: content_writing,skill_section
summary_categories: skill_section_summary,outline_criteria
triggers: evidence gap,证据缺口,素材不足,引用来源,结论先行标题
priority: P1
read_when: outline 阶段需要定义 evidence gap 写法和证据驱动判断时
max_use: 只约束大纲中的证据字段写法，不替代事实检索本身
-->

# Outline Evidence Gap

写大纲时，正文页不能只写“要讲什么”，还要写“需要什么证据”。判断准则：

- 标题必须是观点句，不是模糊话题。
- 每页先看要证明什么，再在 `content` 的 `证据：...` 中写清需要数据、案例、政策还是权威来源。
- 素材不足时在 `content` 中显式写 `证据缺口：是`，不要硬编数字或把缺口藏起来。
- 公开来源必须保留 URL、发布方和时间，后续才能进 PPT 正文或来源区。
- 背景图属于视觉素材，不是正文证据。需要背景图时在 `background_image` 中写清画面意图；受控候选及其来源、许可和 binding 由工具结果或 support 文件维护。没有安全候选时，写成明确缺口或改为纯色、弱纹理、SVG 背景，不写裸外链或含糊的“待找背景图”。

这条合同的目标是让 outline 成为单页生成的施工图，而不是只给出页标题列表。
