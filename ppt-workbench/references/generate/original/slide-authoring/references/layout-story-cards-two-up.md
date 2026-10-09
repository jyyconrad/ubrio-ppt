<!--
id: layout-story-cards-two-up
category: layout
module_type: layout_family
stage: slide_generation
read_when: 文学/人文主题需要并列解释两个核心观点、两类人物处境或两种选择
page_roles: content, summary
style_family: literary_documentary_cn
ppt_types: book_analysis, literary_documentary, keynote
visual_tags: paper_light, editorial, cards
content_categories: layout, content_structure
summary_categories: layout_summary
supports: svg_drawingml
outputs: svg_layout, narrative_cards
depends_on: content-literary-documentary-narrative.md
max_use: 只用于 2 个并列叙事块；超过 2 个块请改用 story-cards-three-up 或拆页
-->

# Layout: Story Cards Two Up

## 适用

用于两个并列主题：两种命运、两类选择、两个阶段、文本与现实、人物与读者。它是 narrative card，不是业务指标卡。

## 输入槽位

- `title`
- `lead`
- `cards[2]`
- `quote_or_close`
- `sources`

每张 card 包含：

- `heading`：短小论点。
- `body`：1-3 句解释。
- `anchor`：可选，人物/场景/章节/意象。

## 布局规则

- 两张卡宽度接近，留出清晰 gutter。
- 卡片可有细边框或淡纸色 surface，不使用强阴影。
- 每张卡可有一条金棕短线或小号序号，但不要做大图标。
- 底部可放一句 quote_or_close，作为主题收束。

## 容量规则

- 每张卡正文不超过 90-120 个中文字符。
- 两张卡内容差异要清楚，避免只是同义重复。
- 如果两张卡难以并列，改用 `editorial_image_panel`。

## 生成方式

可用 `build_editorial_svg_page.py` 生成：`layout_family` 取 `story_cards_2up`，输入 `cards[2]` 和 `quote_or_close`。该 layout 默认不需要图片槽位；如果确实需要图像锚点，应改用 `editorial_image_panel` 或 `book_compare_quote_panel`。

## 禁止

- 不写 KPI、owner、action ledger。
- 不使用空泛小标题，如“方面一/方面二”。
- 不为了对称强行补内容。
