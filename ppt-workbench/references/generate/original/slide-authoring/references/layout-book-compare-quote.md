<!--
id: layout-book-compare-quote
category: layout
module_type: layout_family
stage: slide_generation
read_when: 书籍、作者、人物或两个主题判断需要对比，并用引语/金句收束
page_roles: content, summary
style_family: literary_documentary_cn
ppt_types: book_analysis, literary_documentary, keynote
visual_tags: editorial, paper_light, native_image_slot
content_categories: layout, content_structure
summary_categories: layout_summary
supports: svg_drawingml
outputs: svg_layout, compare_blocks, quote_panel, image_slot_plan
depends_on: content-literary-documentary-narrative.md, image-sourcing-commercial-or-generated.md, layout-native-image-slot.md
max_use: 只用于书籍/人物/主题对比；复杂表格对比仍走 native table 或其他 layout
-->

# Layout: Book Compare Quote

## 适用

用于书籍/人物/主题之间的对照，或者用左侧图片锚点 + 右侧 2-3 个比较块 + 底部引语收束。

## 输入槽位

- `title`
- `image_slot`：书封、作者、物件或象征图。
- `compare_blocks`：2-3 个对照说明。
- `quote`：一句引语或总结。
- `source_note`

## 图片绑定

图片仍走 `layout-native-image-slot.md` 合同。`image_slot` 优先写精确 `asset_id`；如果只能基于页码、文件名或来源类型选择，可写 `material_id + image_asset_selector`；只有确认该素材只有一张 `image_assets` 时才只写 `material_id`。`asset_key` / `url` 必须来自受控素材池或本地文件服务，不写任意外部 URL。

可用 `build_editorial_svg_page.py` 生成：`layout_family` 取 `book_compare_quote_panel`，helper 会输出 `data-role="native-image-slot"` 和同页 `native-data.json images[]`，不要在 SVG 里写 `<image href>`。

## 布局规则

- 图片区是锚点，不铺满页面。
- compare blocks 使用细线分隔，不做重色块 dashboard。
- quote panel 可以横跨底部或右下角，但不超过 2 行。
- 图片没有授权时，使用象征图或纯文字书名牌，不伪造书封。

## 容量规则

- compare blocks 最多 3 个。
- 每个 block 标题不超过 12 个汉字，正文不超过 60-90 个中文字符。
- quote 超过 2 行时，删减或单独成页。

## 禁止

- 不把对比写成业务评分矩阵。
- 不用无授权书封、影视剧照或作者照片。
- 不在 SVG 里直接嵌远程图片。
