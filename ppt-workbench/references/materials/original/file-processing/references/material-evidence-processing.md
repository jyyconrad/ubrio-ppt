<!--
id: skill-section/material-evidence-processing
module_type: skill_section
category: workflow-method
stage: materials,outline,slide_generation
content_categories: material_processing,evidence_processing,workflow_method
skill_types: file_processing,skill_section
summary_categories: skill_section_summary,workflow_method
triggers: 材料盘点,素材盘点,文件整理,文件提取,文档摘要,根据材料整理,证据整理,数据证据,材料清单,素材清单,material_id,get_materials,extract_material
priority: P0
read_when: 需要把上传文件、素材清单或文档内容整理成 PPT 可用证据时
max_use: 只处理素材读取、摘要、证据字段和缺口标注；不直接写大纲、确认页面或决定 SVG 落版
-->

# Material Evidence Processing

文件处理的目标不是“读完文件”本身，而是把材料变成后续 PPT 阶段能复用的证据资产。

## 读取顺序

1. 先用材料清单或任务上下文里的 `material_id` 定位真实素材；文件名、URL 和展示名只用于识别，不作为工具输入。
2. 能通过 `get_materials(action='get')` 直接取得 Markdown 内容时，不重复调用复杂提取工具。
3. 只有需要页码、sheet、嵌入图片、表格结构或虚拟分页时，才补充 `extract_material(types=[...])`。

## 证据输出

交给主 Agent 的结果至少包含：

- 素材用途：这份材料能支撑哪个主题、章节或当前页。
- 关键证据：事实、数字、案例、来源页码和引用口径。
- 风险缺口：口径不一致、来源缺失、扫描/OCR 不可靠、只能作为推断的信息。
- 后续建议：适合写入 foundation、outline evidence gap，还是当前页的素材补充。

不要把未读取到的材料内容补全成“合理推测”，也不要替主 Agent 确认 foundation、大纲或页面。
