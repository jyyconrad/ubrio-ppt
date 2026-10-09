<!--
id: scenario-public-image-visual-assets
category: asset-reference
read_when: 需要判断哪些 PPT 页面适合加入公共图片、景点/场馆/产品/人物/案例图片来提升视觉效果，并决定图片应作为背景、普通 PPT 图片还是 SVG 局部 slot
page_roles: cover, content, section_divider, summary, closing
stage_tags: materials, outline, slide_generation
supports: web_search, background_materialization, merge_slide_picture_binding, merge_slide_background_binding, svg_drawingml
outputs: public_image_page_candidates, image_requests, picture_binding_plan, avoid_image_rules
depends_on: image-sourcing-commercial-or-generated.md, theme-background-policy.md, layout-native-image-slot.md
relation_specs: requires:image-sourcing-commercial-or-generated, requires:theme-background-policy, optional:layout-native-image-slot
triggers: 公共图片, 公开图片, 景点宣传, 景区宣传, 文旅宣传, 城市推介, 场馆展示, 园区展示, 产品展示, 案例图片, 人物介绍, 讲师介绍, 校园图片, 活动现场, 展览图片, 证据图片, 配图提升视觉, public image, place image, destination promotion, scenic spot, tourism promotion, venue photo, product photo, case photo
max_use: 只负责公共图片适用页型和 owner 决策；图片搜索授权和具体落版继续读依赖 reference
-->

# Public Image Visual Assets

## 核心原则

公共图片适合放在**对象明确、场景可视、故事需要锚点**的页面。它们不一定都要做背景：景点、场馆、产品、人物、案例和活动现场图片，经常作为正文主体图或证据图更有效。

先判断图片职责，再选 owner：

- **建立气质和场景**：整页背景，走 `merge_slide_background_binding` 或 deck 级 `merge_deck_background_default`。
- **展示真实对象**：普通 PPT picture，走 `merge_slide_picture_binding`。
- **和 SVG 内部文字/卡片精确排版**：native image slot + `merge_native_data_image`，只在确实需要局部精确混排时使用。

不要为了“有图”把所有公共图片都铺成背景；也不要把外部 URL 直接塞进 SVG。

## 最适合加入公共图片的页面

| 页面类型 | 推荐图片 | 推荐 owner | 为什么能提升视觉效果 |
|---|---|---|---|
| 景点/城市/文旅宣传封面 | 地标、景区航拍、街区、自然风景 | 背景图 | 第一眼建立地点记忆和旅行/文化氛围 |
| 景点亮点页 | 单个景点、文物、特色建筑、自然奇观 | 普通 picture 或左右图文 | 让“卖点”变成可感知对象，不只靠形容词 |
| 行程/路线页 | 地图、交通节点、景点串联图 | 普通 picture；必要时局部 slot | 帮观众理解空间关系，避免纯文字路线 |
| 酒店/场馆/展厅/园区展示 | 外立面、空间内景、功能区照片 | 普通 picture 或局部图文面板 | 空间品质需要可视化，文字无法替代 |
| 产品展示 / 新品发布 | 产品主图、使用场景、细节特写 | 普通 picture；封面可背景 | 建立对象感和信任感，突出质感/尺寸/使用方式 |
| 案例页 / 客户故事 | 现场照片、案例截图、前后对比图 | 普通 picture / evidence slot | 增强可信度，避免案例停留在口号 |
| 人物/讲师/团队介绍 | 人物肖像、工作场景、团队照 | 普通 picture | 建立身份和亲近感；不宜压成背景导致脸部不可见 |
| 活动回顾 / 年会 / 校园宣讲 | 现场照片、人群互动、舞台画面 | 背景或普通 picture | 强化真实发生感和情绪记忆 |
| 科普/课堂概念引入 | 科学现象、实验场景、自然对象、器械 | 背景或普通 picture | 帮助抽象概念落到可观察画面 |
| 公益/医疗/环保传播 | 场景、人群、问题对象、目标状态 | 背景或普通 picture | 让议题有具体对象，但不能替代证据来源 |
| 证据/来源页 | 截图、报告封面、新闻页面、数据来源图 | 普通 picture / evidence slot | 图片承担证据职责，必须保留来源且不能被遮罩压暗 |

## 不推荐加公共图片的页面

- 密集表格、预算、财务明细、指标明细。
- 复杂流程、架构、组织责任矩阵、法务条文。
- 需要用户逐字阅读的 SOP、检查清单、考试题。
- 图片和论点无关，只是图库式“好看”的页面。

这些页面如果需要视觉质感，用 `solid`、`svg` 低干扰装饰底或 `paper_light`，不要硬塞公共图片。

## 搜索和素材入池

公共图片必须先入受控素材池：

1. 用 `web_search(mode='image' 或 'mixed', materialize=true)` 搜索，按用途设置 `use_case='background' | 'inline' | 'evidence'`。
2. 查询词包含：对象名称、地点/行业/场景、横向或竖向需求、图片用途、授权要求、无文字/低干扰等限制。
3. 入池后记录 `read_ref / selected_image_binding / source_url / license / attribution / commercial_ok`。
4. 多图候选需要用户确认时，走 `prepare_image_candidates` → `ask_user` → `resolve_image_candidate_selection`。

景点、城市、场馆、产品和人物图片容易出现版权/肖像/商标问题；`commercial_ok` 不明确时，不要当成可商用素材落版。

## 页面落版规则

- 背景图要有标题安全区和 overlay；主体不要压住标题、人物脸部或关键信息。
- 普通 picture 应有明确图注或上下文标签，避免像装饰图。
- 证据图不能过度裁切、模糊或遮罩；必要时放大成局部图文页。
- 多张公共图片时优先做 2-3 张精选图，不做杂乱相册；每张图都要服务一个明确卖点。
- 图片风格要统一：同一 deck 避免混用写实航拍、卡通插画、低清截图和 AI 生成图造成质感割裂。

## 失败降级

- 搜不到安全图片：请求用户提供官方图包，或改用抽象矢量背景 / 纸纹 / 产品示意图。
- 版权不清：只保留为候选，不落版；询问用户是否有授权素材。
- 图片承担证据职责但来源弱：改为文字说明 + 来源链接，或要求用户补官方截图。
- 图片质量低：不要放大铺满；改为小图卡、缩略证据或不使用。
