<!--
id: layout-dark-photo-interlude
category: layout
stage: slide_generation
read_when: 封面、章节过渡、情绪高潮或收尾页需要深色影像背景、衬线标题和少量文字
page_roles: cover, section_divider, closing
style_family: literary_documentary_cn
ppt_types: book_analysis, literary_documentary, keynote
visual_tags: photo_dark, serif_cn, documentary
content_categories: layout, fixed_page
supports: svg_drawingml
outputs: svg_layout, background_variant_hints, title_safe_region
depends_on: style-literary-documentary-cn.md, image-sourcing-commercial-or-generated.md, layout-fixed-cover-agenda.md
max_use: 只描述内容层结构和背景需求；整页图片、遮罩和背景仍归 deck_framework
-->

# Layout: Dark Photo Interlude

## 适用

用于封面、章节页、情绪转折页和结尾页。页面应像纪录片章节卡：一张压暗影像承载气氛，文字少而有力。普通 summary 若仍需承载多条观点，优先用浅色正文页；只有收束型总结才按 `kind=closing` 使用本 layout。

## 输入槽位

- `kicker`：小标签，如章节名、PART、作品名，可选。
- `title`：一句主题命题。
- `subtitle`：一句补充说明，可选。
- `quote_text`：引语或收束句，可选。
- `background_request`：图片语义、来源策略和 fallback。
- `title_safe_region`：标题偏中上、居中或偏左的安全区域。

## 布局规则

- 文字组占画面高度的 20%-35%，不要铺满。
- 标题用衬线大字，副标题和 kicker 用较小无衬线。
- 金棕强调只用短线、小标签或一处细线，不做大面积色块。
- 背景图由 `deck_framework` 写入，SVG 内容层只写标题、引语和少量强调线。

## 生成方式

使用 `build_fixed_svg_page.py` 的 `photo_dark_serif` 变体生成内容层：

```json
{
  "kind": "section_divider",
  "variant": "photo_dark_serif",
  "theme_id": "literary_documentary_cn",
  "chapter_label": "第一部分",
  "title": "苦难不是命运的终点",
  "subtitle": "真正的叙事，是人在命运里如何继续承担",
  "title_align": "left"
}
```

`kind` 可取 `cover`、`section_divider`、`closing`。不要手写 SVG 坐标；除可选 `title_safe_region`
外，几何和字号由 helper 计算。整页图片背景仍写入 `deck_framework.background`，不写进 SVG。

## 背景计划

若需要图片背景，先生成：

```json
{
  "use_case": "background",
  "preferred_strategy": "web_commercial_first",
  "fallback_strategy": "generate_if_no_safe_match",
  "visual_polarity": "photo_dark"
}
```

## 禁止

- 不在 SVG 中画整页黑色矩形、整页图片或整页遮罩。
- 不堆三卡、指标、表格。
- 不把章节编号做得比主题标题更大。
