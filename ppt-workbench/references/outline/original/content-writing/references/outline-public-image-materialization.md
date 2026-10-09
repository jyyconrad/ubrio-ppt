<!--
id: skill-section/public-image-materialization
module_type: skill_section
category: asset-reference
stage: outline
page_roles: cover, content, section_divider, summary, closing
content_categories: asset_reference
skill_types: content_writing,skill_section
summary_categories: skill_section_summary,asset_reference
triggers: 公共图片,公开图片,景点宣传,文旅宣传,城市推介,场馆展示,园区展示,产品展示,人物介绍,讲师介绍,活动现场,案例图片,证据图片,image_request inline,image_request evidence,use_case inline,use_case evidence,selected_image_binding,read_ref
priority: P0
read_when: outline 阶段大纲确定某页需要景点、场馆、产品、人物、案例、活动现场等公共图片时，需要把图片用途和受控引用写入 support 或大纲
max_use: 只服务 outline 阶段的公共图片素材引用登记，不做单页落版
outputs: public_image_requests, outline_support_material_refs, selected_image_bindings
-->

# Outline Public Image Materialization

大纲草稿一旦决定某页需要公共图片，就在 outline 阶段把图片用途和候选引用写清楚：

1. 在页面 `content` 中标注图片用途和图片意图：
   - `background`：封面、章节、氛围页背景。
   - `inline`：景点亮点、场馆/园区、产品、人物、活动现场、案例主体图。
   - `evidence`：报告截图、新闻页面、来源截图、可核验案例证据。
2. materials 阶段已入池的图片优先复用；语义、授权或比例不匹配时，再选择当前可用的图片检索能力补充受控候选。
3. 把 `read_ref / selected_image_binding / source_url / license / commercial_ok` 写入 support 文件或交给工具结果维护，让单页生成直接消费受控素材。
4. 如果图片真实性、版权或肖像授权不明确，大纲里标注缺口并请求用户提供官方素材，不要用无授权公共图片占位。
5. 对密集表格、财务、合规条文和复杂流程页，不因为“更好看”而强插公共图片；需要质感时改用弱背景或纯色。

本模块只负责“选页、登记图片需求和引用”；具体绑定和单页落版由 slide_generation 阶段决定。
