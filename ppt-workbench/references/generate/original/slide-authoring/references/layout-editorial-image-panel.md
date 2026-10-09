<!--
id: layout-editorial-image-panel
category: layout
module_type: layout_family
stage: slide_generation
read_when: 正文页需要左文右图或左图右文，图片作为人文叙事锚点，文字仍是主角
page_roles: content
style_family: literary_documentary_cn
ppt_types: book_analysis, literary_documentary, keynote
visual_tags: editorial, paper_light, native_image_slot
content_categories: layout, content_structure
summary_categories: layout_summary
supports: svg_drawingml
outputs: svg_layout, image_slot_plan, narrative_blocks
depends_on: content-literary-documentary-narrative.md, image-sourcing-commercial-or-generated.md, layout-native-image-slot.md
max_use: 只读取本文件确定图文比例和 slot 语义；图片真实嵌入由后续 renderer slot 处理
-->

# Layout: Editorial Image Panel

## 适用

用于一页解释一个主题判断，并配一张书封、人物、地点、物件或抽象意象图。图片承担“进入语境”的作用，文字承担“说清楚观点”的作用。

## 输入槽位

- `title`：主题判断。
- `lead`：一句导语。
- `narrative_blocks`：2-3 个论述块。
- `image_slot`：图片语义、素材 id 或 image_request。
- `quote`：短引语或总结，可选。
- `sources`：来源或素材说明。

## 布局选择

- 文字强：文字 58%-65%，图片 30%-38%。
- 图片强：图片 42%-48%，文字 46%-54%，适合书封/人物照。
- 图片放左用于“进入文本/人物”，图片放右用于“解释观点/收束意象”。
- caption 不超过一行；来源放在页面底部或图片下方弱化。

## 容量规则

- 标题 1-2 行。
- lead 1 行。
- narrative blocks 最多 3 个；每个 block 1 个小标题 + 1-3 句正文。
- quote 最多 2 行；超出时移到下一页。

## 图片规则

SVG 只声明图片区域和语义。使用 `build_editorial_svg_page.py` 时，把图片写入 `image_slot`，helper 会输出 `data-role="native-image-slot"` 并在 `native-data.json` 写 `images[]`。

这条 helper lane 只用于图片必须与 SVG 内部文字/卡片精确对齐的 editorial panel。普通正文图、证据图或书封卡如果不需要 SVG 局部 slot，应按 `image-sourcing-commercial-or-generated.md` 走 `merge_slide_picture_binding` 写入 `artifacts.picture_bindings[]`，不要为了套用本布局强行生成 native-data。

`image_slot` 可引用 `asset_id`、`material_id`、`asset_key` 或受控本地 `/v1/files/...` URL。用户直接上传图片、上传文件剥离图片优先用 workspace `image_assets` 中的精确 `asset_id`；如果只能基于页码、文件名或来源类型选择，可在 `material_id` 旁写 `image_asset_selector`，由 renderer 解析成真实图片对象。公开图片、生图或外部图片 URL 必须先入池转为 `asset_id` / `asset_key`，不要把裸外链写进 slot。

不要直接在 SVG 里写远程 `<image href>`。

## 失败检查

- 图片区域比正文更抢眼，但没有明确叙事作用。
- 正文被压成微型字。
- 图片没有来源或授权信息。
- 页面变成大图海报，缺少可讲述的内容路径。
