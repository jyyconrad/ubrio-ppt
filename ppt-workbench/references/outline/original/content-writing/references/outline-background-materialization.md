<!--
id: skill-section/background-materialization
module_type: skill_section
category: asset-reference
stage: outline
page_roles: cover, section_divider, content, closing
content_categories: asset_reference
skill_types: content_writing,skill_section
summary_categories: skill_section_summary,asset_reference
triggers: 大纲阶段背景图,大纲确定背景图,页面背景图需求,image_request background,搜索背景图,背景图素材入池,全局背景图候选,selected_image_binding,read_ref
priority: P0
read_when: outline 阶段大纲草稿确定某页或整套 deck 使用背景图时，需要先搜索入池并把引用写入 support 或大纲
max_use: 只服务 outline 阶段的背景素材入池与引用登记，不做单页落版
outputs: background_image_requests, outline_support_material_refs, selected_image_bindings
-->

# Outline Background Materialization

大纲草稿一旦决定某页或整套 deck 使用背景图，就在 outline 阶段先补齐背景素材，不把找图推迟到单页生成：

1. 先从大纲草稿里圈出真正需要背景图的页（封面、章节页、氛围页），逐页在 `background_image` 中明确画面主体、深浅极性和标题安全区要求。
2. materials 阶段已入池的全局背景候选优先复用；语义或极性不匹配时，再选择当前可用的图片检索能力补充受控候选。
3. 把 `read_ref / selected_image_binding / source_url / license` 写入 support 文件或交给工具结果维护，让单页生成能消费受控素材，不从裸外链开始。
4. 没有安全候选时明确降级或在大纲里标注背景缺口，不用授权不明的图占位。

本模块只负责“选页、入池、登记引用”；具体绑定和单页落版由 slide_generation 阶段决定。
