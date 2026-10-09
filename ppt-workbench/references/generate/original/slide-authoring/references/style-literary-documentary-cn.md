<!--
id: style-literary-documentary-cn
category: visual-theme
module_type: style_family
stage: materials, outline, slide_generation
read_when: 中文读书分享、人文主题、人物命运、文学/纪录片叙事 deck，需要深色影像页与浅色纸张正文页
page_roles: cover, content, section_divider, summary
style_family: literary_documentary_cn
ppt_types: book_analysis, literary_documentary, keynote
visual_tags: literary_documentary_cn, photo_dark, paper_light, editorial, serif_cn, documentary
content_categories: style, visual_theme
summary_categories: style_summary
supports: svg_drawingml
outputs: visual_tokens, background_policy, layout_family_hints, image_request_hints
depends_on: contract-visual-token.md, image-sourcing-commercial-or-generated.md, anti-pattern-over-businessified-literary-slides.md
max_use: 只读取本文件作为视觉风格合同；内容逻辑另读 scenario/content reference，具体布局另读 layout reference
-->

# Style: Literary Documentary CN

## 适用判断

适合中文读书分享、人文演讲、人物命运、作品深读、纪录片式主题串讲。它不是 business gold 的换色版本；若页面目标是“主题-意象-论述-共鸣”，优先使用本风格，而不是强行套 `claim/evidence/action`。

不适合纯经营复盘、项目汇报、行动台账、指标 dashboard；这些仍走业务汇报风格和 gold builder。

## 视觉合同

基础气质是“深色影像页 + 浅色纸张正文页”的双极结构：

- `photo_dark`：封面、章节、情绪高潮、收尾页。使用可追溯图片或生图背景，由 `deck_framework` 负责铺图、遮罩和整页背景。
- `paper_light`：正文、对比、金句、阶段卡片页。使用暖纸色或低透明纸张纹理，由 `deck_framework` 负责背景。
- `editorial_image_panel`：正文局部图片只作为叙事锚点，不抢正文主角。
- `story_cards_2up/3up`：多段论述页用 2/3 列 narrative card 承载，不做业务指标卡。

推荐 token：

- `background.paper`: `#F4EFE7`
- `background.photo_overlay`: `#0B0F14`
- `title_text`: `#374151` on light / `#FFFFFF` on dark
- `body_text`: `#374151`
- `muted_text`: `#6B7280`
- `accent`: `#A16207`
- `border`: `#D6C8B8`
- `surface`: `#FFFCF6`

字体：

- 标题、引语、长段正文：优先 `Noto Serif SC`。
- 小标签、页内元信息、caption：优先 `Noto Sans SC`。
- 缺字体时可降级到 `Source Han Serif SC` / `Songti SC` / `Microsoft YaHei`，但不要把全篇改回默认无衬线商务风。

## 背景策略

把背景需求写入 `deck_framework` 或 `image_requests`，不要在 SVG 内容层画整页背景。各形态（solid 纯色 / svg 低干扰抽象矢量装饰底 / photo_dark 暗色影像 / paper_light 纸纹；整页基础底禁透明色、禁斑点/波纹 pattern）的通用选型规则、无图 `texture_preset` 参数、svg 背景输入契约与错误码读 `theme-background-policy.md`；本文件只定本风格族的具体取值。

Page role 映射：

- cover：`photo_dark`
- section_divider：`photo_dark`
- content：`paper_light`
- summary：`paper_light` 或收束型 `photo_dark`
- closing：`photo_dark`

需要单页差异时，使用 `deck_framework.background.slide_overrides`，不要在该页 SVG 中铺满图片或矩形。

推荐背景合同骨架：

```json
{
  "background": {
    "default_by_page_role": {
      "cover": {"type": "photo_dark", "image_material_id": "mat-cover", "fit": "cover", "crop": {"mode": "center"}, "overlay_color": "#0B0F14", "overlay_opacity": 0.42},
      "section_divider": {"type": "photo_dark", "overlay_color": "#0B0F14", "overlay_opacity": 0.36},
      "content": {"type": "paper_light", "base_color": "#F4EFE7", "texture_material_id": "mat-paper-texture", "texture_opacity": 0.08},
      "summary": {"type": "paper_light", "base_color": "#F4EFE7"},
      "closing": {"type": "photo_dark", "overlay_color": "#0B0F14", "overlay_opacity": 0.38}
    },
    "slide_overrides": {
      "page-4": {"type": "photo_dark", "image_material_id": "mat-chapter-1", "fit": "cover", "crop": {"focal_x": 0.5, "focal_y": 0.5}, "overlay_color": "#0B0F14", "overlay_opacity": 0.44}
    }
  }
}
```

当前 renderer 行为：

- `paper_light.base_color` 写入 PPT 原生背景色。
- `paper_light.texture_material_id / texture_asset_key / texture_url` 会物化为 PPT 原生纹理图片层，并用 `texture_opacity` 写入 picture 透明度；未命中真实纹理图片时才退回基础纸张 wash 层。
- `photo_dark` 在提供受控 `url / asset_key / key` 时会写入全页 PPT 原生图片背景；远端受控 `asset_key` 会先预物化到 renderer workdir。
- `photo_dark.fit=cover` 默认裁切，可用 `crop.focal_x/y` 或 `crop.mode=top|bottom|left|right|center` 控制焦点。
- `overlay_opacity` 生成位于背景图和内容层之间的半透明遮罩。
- 只写 `image_material_id` 时，renderer 会尝试从 workspace `image_assets` 自动解析用户上传或上传文件剥离图片；解析不到只能落安全底色，不能退回 SVG 内容层铺图。
- 纸张纹理同理；精确纹理优先写 `texture_asset_id / texture_asset_key / texture_url`。
- 同一 material 多图但只能基于 metadata 选择时，背景图可写 `image_asset_selector`，纸张纹理可写 `texture_asset_selector`；支持 `page / index / source_kind / source_filename / asset_index`。

## 图文关系

- 深色影像页文字少、重情绪，标题安全区优先中部或左中。
- 浅色纸张页文字是主角，图片只作锚点、证据或意象，不做大幅装饰。
- 正文页优先 `editorial_image_panel`、`story_cards_2up/3up`、`book_compare_quote_panel`。
- 局部图片走 `layout-native-image-slot.md`，不直接在 SVG 写 `<image href>`。
- 图片必须有来源、授权或 generation metadata；文本模型不能根据图片内容自行选图。

## 风格检查

- 标题是否像文学观点或主题命题，而不是业务 KPI 标题。
- 图片是否服务主题意象，而不是通用 stock 装饰。
- 浅色页是否保留足够留白和可读正文，不变成海报口号。
- 深色页白字和金棕强调是否有足够对比。
- 局部图片是否有来源、授权或 generation metadata。
