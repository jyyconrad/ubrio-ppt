<!--
id: scenario-background-image-premium
category: scenario-template
read_when: 需要判断哪些 PPT 或哪些页型加背景图片后更有高级视觉感，或需要把搜索并使用背景图片设为高优先级
page_roles: cover, content, section_divider, summary, closing
stage_tags: materials, outline, slide_generation
supports: background_materialization, web_search, merge_deck_background_default, merge_slide_background_binding, svg_drawingml
outputs: background_priority_decision, background_image_requests, avoid_background_rules
depends_on: scenario-public-image-visual-assets.md, theme-background-policy.md, image-sourcing-commercial-or-generated.md
relation_specs: optional:scenario-public-image-visual-assets, requires:theme-background-policy, requires:image-sourcing-commercial-or-generated
triggers: 高级感, 背景图高级, 背景图片高级, 图片背景优先, 搜索背景图优先, 视觉质感, 场景感, 沉浸感, 叙事感, 氛围感, 主题宣讲, 课堂宣讲, 科普, 品牌发布, 产品发布, 文旅, 城市推介, 展览, 招商, 人物故事, 读书分享, 企业文化, 年会, 生态环保, 医疗科普, 校园宣讲, premium background, image background first, immersive deck
max_use: 只负责判断背景图增益场景和反例；图片来源、授权和落版参数继续读依赖 reference
-->

# Background Image Premium Scenarios

## 核心原则

背景图最能提升高级感的 PPT，不是所有 PPT，而是**需要先建立场景、对象、情绪、主题气质或叙事语境**的 PPT。deck 级策略提供一致性和兜底，但每一页都要根据自己的叙事任务、信息密度、可读性和可用素材独立判断是否使用背景图，并可写单页 override；不要把整页图塞进 SVG 内容层。

判断句：如果一页的第一任务是“让观众进入一个场景 / 记住一个对象 / 感到一种气质 / 相信一个故事”，背景图通常增益很大；如果第一任务是“比较数字 / 阅读表格 / 核对流程 / 做决策”，背景图通常只能做封面、章节或弱纹理，不应压住正文。

公共图片不是都要做背景。景点亮点、场馆、产品、人物、案例和活动现场如果是页面要展示的主体，应优先读 `scenario-public-image-visual-assets.md`，用普通 PPT picture 或图文面板承载；只有封面、章节、氛围页才优先做整页背景。

## 背景图优先的 PPT 类型

| PPT 类型 | 为什么背景图增益大 | 背景图策略 |
|---|---|---|
| 课堂宣讲 / 公开课 / 科普讲座 | 先建立认知场景，降低概念理解门槛 | 封面、章节、概念引入页优先 `photo_dark`；正文解释页可用弱化影像或 `paper_light` |
| 品牌发布 / 产品发布 / keynote | 需要对象感、情绪和品牌记忆点 | 产品、场景、用户使用情境作背景；标题区保留安全留白 |
| 文旅 / 城市推介 / 展览 / 文化主题 | 地点、文化符号和氛围是内容本身 | 高质量地点/文物/空间影像作背景，统一色调和遮罩 |
| 企业文化 / 年会 / 价值观宣贯 | 需要组织记忆、情绪动员和仪式感 | 团队、办公场景、历史照片或抽象意象背景；避免花哨图库感 |
| 人物故事 / 读书分享 / 纪录片叙事 | 背景承载人物、时代和叙事质感 | 暗色影像、纸张纹理、书页/场景意象；正文保持留白和衬线气质 |
| 招商 / 园区 / 产业 / 项目路演 | 场地、设备、产业链或真实案例能增强可信度 | 封面、章节、案例页使用真实场景图；数据页只用弱化底图 |
| 生态环保 / 医疗健康 / 公益传播 | 受众需要直观看到问题场景或目标对象 | 现场/自然/人群影像作背景；证据图不做背景，保留来源和可读性 |
| 校园宣讲 / 招生 / 培训招生 | 场景体验和人群代入感比纯文字更重要 | 校园、课堂、活动、人群影像；正文页减少大面积遮挡 |

## 只适合局部使用背景图的 PPT

- 年度总结、经营复盘、财务分析：封面、章节页、closing 可以用背景图；KPI、表格、图表页优先纯色 / `svg` 装饰底 / 浅纹理。
- 政策解读、合规培训、制度宣贯：封面和章节可用庄重背景；条文、流程、责任清单页不要铺复杂图片。
- SOP、操作手册、检查清单：背景图只用于章节分隔或轻质纸纹；步骤页要保证可读和可打印。
- 技术架构、数据平台、算法汇报：可用抽象科技背景或产品截图；架构图正文页要克制，不能影响线条和标签识别。

## 不应强铺背景图的页面

- 大表格、密集指标、财务明细、预算测算。
- 复杂流程图、系统架构图、泳道图、责任矩阵。
- 法务、合规、审计、风险清单等需要逐字阅读的页面。
- 截图证据页：截图本身是证据，不能再被背景图干扰。

这些页面如需质感，优先使用 `solid` 深/浅主题底、`svg` 低干扰矢量装饰底或 `paper_light` 纸纹，不要为了高级感强行铺照片。

## 运行规则

1. materials 阶段一旦识别到上表“背景图优先”的 PPT 类型，就准备 deck-level 背景候选，不等到单页生成。
2. outline 阶段为需要背景图的页写清 `image_request.use_case="background"`、语义意图、极性、标题安全区和候选引用。
3. slide_generation 阶段逐页做背景决策：优先复用 `selected_image_binding / material_ref`；不匹配时重新搜索、请求用户补图，或改用纯色、纸纹、低干扰抽象 SVG。
4. 全册或页型统一背景用 `merge_deck_background_default` 形成兜底；任何页面都可因本页叙事、主体构图、密度或可读性使用 `merge_slide_background_binding` 覆盖默认，不限于封面和最后一页。
5. 每张背景图必须有来源或 generation metadata；可公开检索的优先 `web_search(mode='image' 或 'mixed', use_case='background', materialize=true, save_top_k=1-3)`。
6. 背景图必须服务内容：主体不压标题、纹理不干扰正文、遮罩后文字可读、授权字段可追溯。
7. 不要求所有页面强铺图片。高密度数据、复杂流程和证据页可主动选择纯色、纸纹或低干扰 SVG；有高度匹配的背景图时也不要因 deck 默认是纯色而放弃使用。

## 搜索提示

查询词至少包含：

- deck 主题和具体对象，如“湿地生态 科普”“城市更新 园区”“产品发布 智能硬件”。
- 画面主体和场景，如“课堂实验”“博物馆展厅”“新能源工厂”“医生患者沟通”。
- 画面要求：`16:9 横向`、`标题安全区`、`低干扰背景`、`可商用`、`无文字`。
- 极性：深色影像 / 浅色纸纹 / 温暖自然光 / 冷静科技感。

搜索后只写受控素材引用，不写裸外链。
