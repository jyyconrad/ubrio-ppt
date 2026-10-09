<!--
id: layout-story-cards-three-up
category: layout
module_type: layout_family
stage: slide_generation
read_when: 文学/纪录片叙事需要三段递进、三个人物阶段、三种主题解释
page_roles: content, summary
style_family: literary_documentary_cn
ppt_types: book_analysis, literary_documentary, keynote
visual_tags: paper_light, editorial, cards
content_categories: layout, content_structure
summary_categories: layout_summary
supports: svg_drawingml
outputs: svg_layout, narrative_cards
depends_on: content-literary-documentary-narrative.md
max_use: 只用于 3 个短叙事块；正文过长时拆页或改 2-up
-->

# Layout: Story Cards Three Up

## 适用

用于三段递进或三类解释：童年/漂泊/归来，苦难/选择/承担，文本/人物/读者。三列之间应有叙事顺序，而不是随机并列。

## 输入槽位

- `title`
- `lead`
- `cards[3]`
- `bottom_close`
- `sources`

每张 card 必须有 `heading` 和 `body`，可选 `micro_label`。

## 布局规则

- 三列卡片高度一致，但内部内容允许自然换行。
- 使用浅纸面、细边框和金棕短线形成节奏。
- 底部 `bottom_close` 用一句话连接三列，避免页面像碎片清单。

## 容量规则

- 每列正文建议 50-85 个中文字符。
- 每列最多 1 个小标题 + 2 段短正文。
- 如果每列都需要长段解释，改为两页或 `editorial_image_panel`。

## 生成方式

可用 `build_editorial_svg_page.py` 生成：`layout_family` 取 `story_cards_3up`，输入 `cards[3]` 和 `bottom_close`。该 layout 适合纯叙事卡片，不直接放正文图片；需要书封/人物/地点图时改用图片面板类 layout。

## 失败检查

- 三列只有标签，没有观点。
- 字号低于可读下限。
- 三列没有递进关系。
- 金棕强调过多，变成装饰。
