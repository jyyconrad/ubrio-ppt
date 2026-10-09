<!--
id: scenario-educational-pop-science
category: scenario-template
read_when: 课堂宣讲、课程讲授、科普讲座、科学传播、校园宣讲、公开课或主题教育类 PPT，需要把搜索并使用背景图片作为视觉第一优先级
page_roles: cover, content, section_divider, summary, closing
stage_tags: materials, outline, slide_generation
supports: svg_drawingml, background_materialization, web_search, merge_slide_background_binding
outputs: education_outline, background_image_requests, page_style_contract
depends_on: scenario-background-image-premium.md, theme-background-policy.md, image-sourcing-commercial-or-generated.md, theme-training-clean.md
relation_specs: requires:scenario-background-image-premium, requires:theme-background-policy, requires:image-sourcing-commercial-or-generated
triggers: 课堂宣讲, 课堂讲授, 课程宣讲, 科普, 科普PPT, 科普讲座, 科学传播, 校园宣讲, 公开课, 主题教育, popular science, science communication, educational outreach, public lecture, lecture deck, 背景图优先, image background first
max_use: 只读取本文件决定教育/科普类 deck 的叙事和背景优先规则；图片来源和落版细节继续读依赖 reference
-->

# Scenario: Educational / Popular Science

## 核心判断

课堂宣讲、科普、公开课、校园宣讲和主题教育类 PPT 不是默认的经营汇报心智。它们的目标通常是让听众先进入情境、理解概念、记住机制，再迁移到行动或判断。先按 `scenario-background-image-premium.md` 判断背景图是否能建立场景感；命中后再执行本文件的教育/科普叙事规则。

这类 deck 的视觉第一优先级是：**先搜索并准备合适的背景图片候选**。背景图不是装饰补丁；应在 materials / outline 阶段尽早入池，slide_generation 再由每页根据叙事、密度、可读性和候选画面独立决定是否复用、替换或绑定，不强制全册铺图。

## 叙事结构

常用结构：

- `现象引入 → 核心概念 → 机制拆解 → 案例/实验 → 应用/讨论`
- `问题场景 → 误区澄清 → 科学解释 → 生活连接 → 结论回收`
- `课程目标 → 知识点 → 示例演示 → 课堂练习 → 课后迁移`

页面标题仍要是判断句，但语气可以比业务汇报更解释型，例如“潮汐不是海水自己涨落，而是引力和地形共同放大的周期现象”。

## 背景图片优先规则

1. materials / outline 阶段只要识别到 `课堂宣讲`、`科普`、`公开课`、`校园宣讲`、`主题教育`、`popular science`、`science communication` 等场景，就先准备背景图候选，不等到单页生成临时找图。
2. 调用 `web_search(mode='image' 或 'mixed', use_case='background', materialize=true, save_top_k=1-3)`；查询词必须包含主题、概念/场景、页型、16:9 横向、深浅极性、标题安全区和授权要求。
3. 把 `read_ref / material_id / selected_image_binding / source_url / license / commercial_ok` 写入 foundation assets、outline support 或对应页面 `image_request`。
4. slide_generation 阶段每页重新评估背景；任何页面都可用 `merge_slide_background_binding` 写单页 override。只有多页确认使用完全相同的背景规则时，才用 `merge_deck_background_default` 上移为整册或页型兜底。
5. 不允许把外部图片 URL、预签名 URL 或 `<image>` 直接写进 SVG 内容层；背景统一走 `deck_framework.background`。

## 页面背景选型

| 页型 | 背景策略 | 内容层建议 |
|---|---|---|
| 封面 / closing | `photo_dark` 优先，使用主题相关真实或可商用意象图，overlay 保证标题反白可读 | 固定槽位标题、短副标题、来源/讲者信息 |
| 章节 / 概念引入 | `photo_dark` 或深色 `svg` 背景，画面主体偏侧，给标题留安全区 | 一句核心判断 + 1 个关键词或小引语 |
| 正文解释页 | 仍优先复用背景候选；信息较密时提高 overlay 或改 `paper_light` 纹理化背景，不要退成默认白底 | 2-4 个概念块、流程、对比或例子卡 |
| 案例 / 实验页 | 若图片承担证据职责，用普通 picture 或 evidence slot；若只承担氛围，才做背景 | 保留来源，避免证据图被遮罩压暗到不可读 |
| 练习 / 讨论页 | 背景要低干扰，优先浅纹理或弱化影像 | 问题、选项、讨论提示，留出书写/思考空间 |

## 版式与文字

- 不要套经营汇报的 KPI、owner、行动台账和风险闭环，除非用户明确要教学管理或培训落地。
- 正文页要可讲授：概念定义、关键机制、生活例子、常见误区至少覆盖其中 2-3 类。
- 背景图有真实身份或证据含义时，不能用生成图冒充；可公开检索则保留来源，不可确认授权时询问用户补图。
- 背景图不得含可读文字、复杂水印、脸部主体压住标题区或高频纹理；不合格候选必须替换或降级为 `svg` / `paper_light` 安全背景。

## 失败降级

- 找不到安全背景图：先明确缺口或请求用户补图；用户允许系统补位且不涉及真实证据时，可以委派 `slide_image_generator` 生成抽象意象背景。
- 仍无可用图时，改用 `svg` 低干扰矢量背景或 `paper_light` 纸纹背景，并在内部素材清单记录这是背景素材降级。
- 不得因为缺图直接渲染默认白底，也不得把图片背景塞进 SVG 规避背景工具。
