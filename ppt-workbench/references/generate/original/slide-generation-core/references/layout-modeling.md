<!--
id: skill-section/layout-modeling
module_type: skill_section
category: composition-system
stage: slide_generation
page_roles: content,summary
visual_tags: cards,chart,table
content_categories: layout_modeling,composition_system
skill_types: slide_generation_core,skill_section
summary_categories: skill_section_summary,layout_summary
triggers: 原生对象建模,卡片,图表,表格,标题层级,视觉锚点
priority: P1
read_when: 当前页需要确定对象建模、结构承载和版面层级时
max_use: 只约束页面内容层建模，不替代具体 renderer 路径
-->

# Layout Modeling

当前页建模时，应先按“用户需求 -> 页面意图 -> 语义原子 -> 组合结构 -> 当前工具结构”拆解。

- 文本、数字、标签用文本框。
- 卡片、底板、分组关系用形状和线条。
- 真实数据图表和逐单元格表格优先走 native slot，不手绘完整 series。
- 主标题必须是第一视觉锚点，卡片内也要有短标题、判断句和证据，而不是空白容器。
