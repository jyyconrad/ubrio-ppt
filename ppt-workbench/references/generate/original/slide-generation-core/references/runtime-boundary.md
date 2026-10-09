<!--
id: skill-section/runtime-boundary
module_type: skill_section
runtime_scope: legacy
category: execution-contract
stage: slide_generation
content_categories: runtime_boundary,execution_contract
skill_types: slide_generation_core,skill_section
summary_categories: skill_section_summary,quality_gate
triggers: 当前页边界,不切下一页,不切阶段,不暴露工具名,不编造指标
priority: P1
read_when: 当前页生成过程中需要提醒运行时硬边界时
max_use: 只约束本轮运行时边界，不替代页级内容方法
-->

# Runtime Boundary

本历史单页合同不再参与运行期检索。当前阶段、用户确认、证据和审核边界由
`prompts/ppt_workflow/stages/slide_generation_instructions.md` 与代码门禁统一维护，
包括普通逐页与 Turbo 批次的不同范围；以下内容仅用于旧版本来源追溯。

`slide_generation` 只负责当前一页：

- 用户确认前不进入下一页、不切阶段。
- 不在用户可见正文里暴露工具名、Skill 名、renderer、workspace 路径或状态机。
- 没有素材或公开来源时，不编造具体数字、比例、金额、样本量等硬指标。
- 渲染成功后，若预览审核工具可见则按页面实际风险调用或跳过；审核通过、修复重渲染完成或明确跳过后停止正文。预览卡由系统立即发布，不等待后台审核。
