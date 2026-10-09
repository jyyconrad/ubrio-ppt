<!--
id: scenario-book-deep-analysis
category: scenario-template
stage: materials, outline, slide_generation
read_when: 书籍深度解析、读书分享、文学作品串讲、人物命运主题演讲、《命运》深度解析、文学纪录片、作品深读、人物命题
page_roles: cover, content, section_divider, closing
style_family: literary_documentary_cn
ppt_types: book_analysis, literary_documentary, keynote
visual_tags: literary_documentary_cn, editorial, photo_dark, paper_light
content_categories: scenario, content_structure
supports: svg_drawingml
outputs: story_spine, page_intents, narrative_arc, image_requests
depends_on: content-literary-documentary-narrative.md, style-literary-documentary-cn.md
max_use: 只读取本文件确定整套书籍解析的叙事组织；单页排版仍按 layout reference 执行
-->

# Scenario: Book Deep Analysis

## 场景目标

面向一本书、一个作者或一个人物命运主题，生成能讲清楚“为什么这本书值得读、它如何展开主题、它与读者经验有什么关系”的 deck。

这类 PPT 不以业务行动闭环为主，而以叙事推进为主。结构可以有观点和证据，但不要把每页都改写成 owner / action / risk / metric。

当请求出现“《命运》”“人物命运”“文学纪录片”“作品深读”“人物命题”“文学叙事”等信号时，优先走本场景，并联动 `style-literary-documentary-cn.md`、`content-literary-documentary-narrative.md`、`layout-editorial-image-panel.md` 和 `layout-native-image-slot.md`。

## 输入契约

进入单页生成前，尽量准备：

- `book_title`：书名或主题对象。
- `central_question`：整套 deck 要回答的问题。
- `reader_takeaway`：希望听众听完带走的共鸣或判断。
- `argument_arc`：3-5 个推进节点。
- `key_images`：书封、作者、地点、物件、自然意象、时代背景。
- `quote_candidates`：可作为金句或页内收束的短句。
- `source_policy`：书封/作者照/背景图是否需要可商用公开素材或生图。

## 叙事骨架

推荐从下面的骨架中选择，不要一次全用：

- 命题引入：提出核心问题，让封面或章节页建立情绪。
- 文本进入：交代作品、作者、时代或人物背景。
- 意象展开：用人物、地点、物件、自然图像解释主题。
- 论点深化：把文本内容转成 2-4 个可讲述观点。
- 现实回声：连接听众生活、组织经验或时代处境。
- 金句收束：用一句判断或引语收住主题。

## 页型分配

- cover：主题命题 + 深色影像背景。
- section_divider：章节转场 + 一句推进判断。
- content：解释论点，可用 `editorial_image_panel` 或 `story_cards_2up/3up`。
- compare：书籍/人物/观点对比，用 `book_compare_quote_panel`。
- summary/closing：回到 central question，给出读者 takeaway。

## SVG benchmark 示例

7 页专题基准样例位于：

- `assets/examples/svg-ppt/benchmarks/scenario-book-deep-analysis-benchmark/`
- `assets/examples/svg-ppt/examples-manifest.json` 的 `benchmark_examples[].id = scenario-book-deep-analysis-benchmark`

这组样例用于 routing 可视化、图片素材路线压测、样式钩子验证和专题级 smoke，不纳入主 7 套业务 SVG-PPT deck 的 `coverage.deck_count / total_pages` 口径。

样例同时附带 `pptx_smoke`：每页独立生成一个单页 PPTX，先应用 `deck_framework` 背景，再渲染为 PNG 缩略图并合成 contact sheet。该 smoke 用于验证 SVG route、框架背景、`native-data.json images[].asset_key` 和原生图片 overlay 能真实落入 PPTX；同目录的 `visual-envelope.json` 记录 native image 内框、纸张正文区和 2/3-up 卡片中缝的区域级视觉护栏，用于发现图片位置、亮暗极性和分栏结构漂移；它仍保留在 `benchmark_examples`，不计入主 `decks` 的 PPTX hash 基线。

读取方式：

- 先用本文件确定 `story_spine / page_intents`。
- 再参考 benchmark 中的 `photo_dark_serif` 固定页、`section_divider`、`editorial_image_panel`、`story_cards_2up/3up`、`book_compare_quote_panel`。
- 局部图片只声明 `data-role="native-image-slot"` 和相邻 `native-data.json images[]`；图片来源优先写 `asset_key` / `asset_id`，不要在 SVG 中直接写 `<image>`。
- 深色影像封面、章节页、结尾页的整页背景仍交给 `deck_framework.background.default_by_page_role / slide_overrides`。

## 输出建议

先产出 `story_spine`，再产出页级 `page_intents`：

```json
{
  "scenario_id": "book_deep_analysis",
  "story_spine": {
    "central_question": "人如何面对命运？",
    "argument_arc": ["提出命题", "进入文本", "展开人物与意象", "对照现实", "回到自我"]
  },
  "page_intents": [
    {"page_role": "cover", "intent": "建立主题气氛", "visual_polarity": "photo_dark"},
    {"page_role": "content", "intent": "解释核心论点", "layout_family": "editorial_image_panel"}
  ]
}
```

## 禁止

- 不要把文学叙事页过度业务化。
- 不要把每页标题写成空泛名词，如“苦难”“命运”“选择”；应改为可讲述判断。
- 不要用未经授权的书封、作者照或影视截图作为可商用素材。
- 不要只做大图大字低密度海报；正文页仍需能支撑讲述。
