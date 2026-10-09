<!--
id: skill-section/work-method
module_type: skill_section
category: workflow-method
stage: outline
content_categories: workflow_method
skill_types: content_writing,skill_section
summary_categories: skill_section_summary,workflow_method
triggers: 读取本地输入,简化 JSON,outline.md,outline_confirm,一次性改完再确认
priority: P1
read_when: outline 阶段需要确认文件工作流和校验顺序时
max_use: 只服务大纲编排流程，不直接生成页面
-->

# Outline Work Method

outline 的工作方法是一个判断循环，不是固定工具调用顺序：

1. 根据当前任务自行决定需要读取哪些 Foundation 资产、用户提纲、素材索引和 support 文件；不要为了“读全”而读取无关内容。
2. 判断现有证据是否足以支撑页面结构。只有缺公开来源、事实核验或图片候选时，才选择检索或委派受限研究助手；主 Agent 始终是两个大纲文件的唯一写作者。
3. 读取 `outline.example.json`，以示例的浅层字段写 `outline.draft.json`。页面概要、写作、证据和素材要求统一放在 `content` 文本，背景图、背景色和主题使用独立字段。
4. 另写 `outline.md`，只提炼整册结构、论证思路、视觉设计理念和跨页素材原则，不承载逐页任务，不复制 JSON。
5. 两个文件满足合同后调用零参数提交出口 `outline_confirm()`。它会自行读取并检查双文件；若返回 `errors` 或 `missing_info`，按具体问题修正后再次提交。
6. 确认卡出现后停止输出，等待用户定稿。若运行时发来文件检查结果，只处理明确缺口，不重做已经通过的部分。

这个阶段的完成标准是“用户可确认的大纲草稿”，不是“已经开始做页面”，也不是“按顺序调用完所有可用工具”。
