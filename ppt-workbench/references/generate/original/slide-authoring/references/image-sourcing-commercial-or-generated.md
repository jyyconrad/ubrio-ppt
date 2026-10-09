<!--
id: image-sourcing-commercial-or-generated
category: asset-reference
stage: materials, outline, slide_generation
read_when: 页面需要背景图、正文锚点图、书封/人物图、证据图，或 deck 属于课堂宣讲/科普/品牌发布/文旅/企业文化等背景图增益场景，需要在可商用公开检索、用户素材和生图之间做选择
page_roles: cover, content, section_divider, summary, closing
style_family: literary_documentary_cn
ppt_types: book_analysis, literary_documentary, keynote, educational_outreach, popular_science, brand_launch, cultural_tourism, corporate_culture, project_showcase
visual_tags: commercial_image, generative_image, native_image_slot, user_image_asset, uploaded_image, embedded_image, photo_dark, paper_light, background_materialization
content_categories: asset_reference, execution_contract
supports: ask_user, web_search, generate_image, svg_drawingml, merge_slide_picture_binding, merge_slide_background_binding
outputs: image_requests, material_metadata, license_checklist, placeholder_request
depends_on: style-literary-documentary-cn.md
triggers: 商业图片, 可商用图片, 生成图, 生图, 图片授权, 素材图片, 书封, 作者图, 人物图, 背景图, 背景素材, 背景图优先, 高级感背景, 场景感, 沉浸感, 图片入池, 图片占位, 缺图, 公开图库, 课堂宣讲, 科普, 科普讲座, 品牌发布, 产品发布, 文旅, 城市推介, 企业文化, 年会, 招商园区, 项目路演, source_url, license, commercial_ok, native image slot, svg image slot
max_use: 只负责图片来源与素材计划；背景归 deck_framework，普通正文图归 merge_slide_picture_binding，只有 SVG 局部图位才进入 native image slot
-->

# Image Sourcing: Commercial Or Generated

## 决策顺序

先执行图片保护规则：已经选中且适合本页的照片、肖像、书封、真实场景、证据截图或复杂纹理，不因 `asset_key`、入池或 overlay 解析失败而删除。保留相同 `picture_id` 修正受控来源，或在找到更合适图片后用同一 ID 替换。禁止用 `patch_svg_layer` 或手绘 SVG 模仿这些真实图像；SVG 只承担结构、文字、关系、形状和低干扰抽象装饰。

图片来源按下面顺序判断：

0. `early_background_materialization`
   materials / outline 阶段一旦确定整套 deck、某类页型或具体页面需要背景图，不要把找图推迟到单页生成。课堂宣讲、科普、品牌/产品发布、文旅/城市推介、展览/文化主题、企业文化/年会、人物故事、招商/园区/产业项目、生态环保、医疗健康、校园宣讲等背景图增益场景，默认先用公开检索或受限素材专家准备可复用背景素材包：
   - 调用 `web_search(mode='image' 或 'mixed', use_case='background', materialize=true, save_top_k=1-3)`，查询词必须包含 deck 主题、页型、画面主体、氛围、16:9 横向、深浅极性、标题安全区和授权要求。
   - 入池后把 `saved_images[].read_ref`、`material_id`、`selected_image_binding`、`source_url`、`license`、`commercial_ok`、用途建议写进全局素材清单或 outline support 文件；后续页面只引用受控素材，不写裸外部 URL。
   - 单页生成阶段先复用这些候选；如果当前页叙事或可读性需要不同画面，允许再搜索或生成新的背景候选，并用 `merge_slide_background_binding` 覆盖当前页。

1. `user_material_first`
   用户已上传书封、作者照、旧 PPT 图片、场景图时优先复用，并保留原素材引用。
   - 直接上传的图片会以 `image_assets[source_kind='uploaded_image']` 进入素材解析结果。
   - PPTX/PDF/DOCX/XLSX 中的嵌入图片会在上传解析阶段剥离为 `image_assets[source_kind='embedded']`。
   - 可先调用 `get_materials(action='list')` 发现 `image_asset_count` 和安全候选字段；list 预览不含 `key / asset_key / url / provenance`，不能当作落版路径来源。
   - 需要完整素材详情时再调用 `get_materials(action='get')` 读取 `image_assets / image_asset_count`，再决定是否填入背景、`merge_slide_picture_binding` 普通图片计划或 SVG 局部图片 slot。
   - `get_materials(action='get')` 会在图片 URL 过期或历史素材缺少 `url_expires_at` 时基于受控 `key` 服务端重签；`url / url_expires_at` 只用于访问展示，落版仍优先使用 `asset_id / selector`。
   - 多张图同属一个 material 时，优先写精确 `asset_id`；多模态模型看图排序后先调用 `get_materials(action='prepare_image_candidates')` 生成 `ask_user_args` 给用户确认；若必须按图片内容语义判断，传 `requires_content_understanding=true`，文本模型会返回 `CONTENT_BASED_IMAGE_SELECTION_REQUIRES_MULTIMODAL` 阻断，多模态模型未提供看图后的 `ranked_asset_ids` 会返回 `CONTENT_BASED_IMAGE_SELECTION_MISSING_RANKING` 阻断。若返回 `NO_IMAGE_ASSET_CANDIDATES`，不要发空确认卡。普通正文/证据图调用 `merge_slide_picture_binding(image_binding=selected_image_binding, box=...)`；只有当前页确实声明 SVG 局部 `native-image-slot` 时，才把 resolve 返回的 `native_data_image` 交给 `merge_native_data_image`。
   - `ask_user_args.questions[].options[].previewUrl` 只用于前端确认卡缩略图展示；它是受控相对预览路由，不是 renderer 输入。不要把 `previewUrl`、外部图片 URL、对象存储 key 或预签名 URL 写入 `native-data.json`。

2. `ask_user_placeholder_when_current_materials_miss`
   当前素材池里没有合适图片、候选图授权不清，或页面明确需要真实书封/人物/截图/证据图时，先发 `ask_user` 占位卡请求用户补图，而不是先静默降级成无图或直接生成替代图。
   - 占位卡必须明确：`use_case`、主体/场景、构图方向、深浅极性、是否需要标题安全区、真实性/授权要求、为什么当前候选不满足。
   - 推荐把“用户上传/补充图片”放在第一选项；只有可接受风格化替代图时，才把“允许系统生成占位图”作为次选。
   - 不要发空泛的“请补一张图”；要让用户一眼知道该补什么。

3. `web_commercial_first`
   真实地点、景点、城市地标、场馆、产品公开图、人物/讲师、书籍、活动现场、案例图和证据图优先走公开图片候选检索。必须保存 `source_url / provider / license / license_url / commercial_ok / attribution`。
   - `web_search(mode='image' 或 'mixed', materialize=true)` 成功后会把图片写入当前会话素材池，并登记为 `image_assets[source_kind='web_image']`；背景图要传 `use_case='background'`，正文/证据图传 `inline` 或 `evidence`。后续优先复制 `saved_images[].selected_image_binding` 进入背景或 `merge_slide_picture_binding` 普通图片计划。需要再读完整素材时复制 `saved_images[].read_ref` 调用 `get_materials(action='get')`。公开图片不是 SVG slot 的默认输入，只有当前页已有明确 SVG 局部图片位时才引用 `asset_id / material_id / selector` 写入 native-data；不要复制外部图片 URL。
   - 景点宣传、文旅/城市推介、场馆展示、园区展示、产品展示、人物介绍、活动回顾、校园宣讲、展览介绍等页面，公共图片通常优先作为普通 PPT picture 或图文面板；只有封面/章节/氛围页才优先做背景图。先读 `scenario-public-image-visual-assets.md` 决定 owner。

4. `generate_if_no_safe_match`
   用户允许系统补位、公开来源没有安全命中，且页面只需要抽象氛围、象征意象或非证据型插图时，走生图模型。必须保存 prompt、model、生成时间和用途。
   - 若主 Agent 希望后续更容易在 SVG 内容层复用，委派 `slide_image_generator` 时明确要求“扁平、矢量感、无文字、边缘清晰、易裁切”的 SVG-friendly 视觉方向，并要求返回 `visual_design_spec` / `native_object_plan` 供后续嵌入或重绘。
   - 当前运行时生成的是**受控图片资产**，不是可编辑 SVG 文件；不要在 Skill 里把它描述成已经得到 SVG 成品。

5. `ask_when_identity_matters`
   书封、作者肖像、影视截图等身份强相关素材无法确认授权时，询问用户是否提供素材或改用象征图。

## image_requests 合同

先写图片需求，再调用工具：

```json
{
  "slot_id": "cover-bg",
  "use_case": "background",
  "semantic_intent": "海边、潮汐、命运感、压暗后可承载白色标题",
  "preferred_strategy": "web_commercial_first",
  "fallback_strategy": "generate_if_no_safe_match",
  "commercial_required": true,
  "query_zh": "海边 岩石 黄昏 人文 纪录片 背景",
  "query_en": "documentary seashore rocks dusk background",
  "style_prompt": "dark documentary photography, muted gold, calm, cinematic, no text"
}
```

`use_case` 只使用：

- `background`：整页背景图，最终由 `deck_framework` 承接。
- `inline`：正文锚点图、书封、人物、局部意象图。
- `evidence`：来源页、截图、证据型图片。

## 工具使用边界

用途先由页面表达主轴定，再查下表分发 owner（不替你决定要不要图、要几张）：

| 用途 | owner |
|---|---|
| 整页背景 / 章节暗色影像 / 纸张纹理 | `merge_slide_background_binding` → `deck_framework.background`（deck 级默认走 foundation `background_policy`） |
| 正文图 / 证据图 / 书封卡配图 | `merge_slide_picture_binding` → `picture_bindings[]` |
| 与 SVG 精确混排的局部图 | native-image-slot + `merge_native_data_image` |
| 当前素材缺图 | 背景/非证据配图先公开检索入池；真实身份/证据图再 `ask_user` 发图片占位卡 |
| 入池 | 用户素材优先 / `web_search(mode='image' 或 'mixed', materialize=true)` / `generate_image` |
| 选图确认 | `prepare_image_candidates` → `ask_user` → `resolve_image_candidate_selection` |

- `merge_slide_picture_binding` 是普通图片的修复入口：传相同 `picture_id` 可原位替换来源。renderer 返回图片不可用时先按 `issues[]` 修正 asset 引用、完成入池或换图；不要把 `remove_slide_picture_binding` 当成错误逃生口。
- `remove_slide_picture_binding` 只用于用户明确要求移除、图片确认不适合，或替代图片已准备好的返修。

- 用户上传素材：优先读取 `get_materials(action='get')` 顶层 `image_assets`。多模态模型可基于图片内容给出 `ranked_asset_ids`，再调用 `prepare_image_candidates`；若必须按画面语义判断，传 `requires_content_understanding=true`，文本模型会被阻断。将返回的 `ask_user_args` 原样交给 `ask_user`，用户提交后用 `resolve_image_candidate_selection` 得到 `selected_image_binding`。普通正文/证据图调用 `merge_slide_picture_binding`，只有 SVG 正文局部图才调用 `merge_native_data_image`。文本模型只能基于 metadata、用户明确指定或确认卡选择，不能假装看过图片；`previewUrl` 只服务确认卡展示。
- 早期背景素材：materials / outline 已经确定背景图时，必须在确认前完成 `use_case='background'` 的公开图片检索入池或记录明确缺口。入池结果写入全局素材清单后，slide_generation 可复用，也可基于当前页效果搜索更合适的替换背景；替换只影响当前页 override，不反向改写已确认大纲。
- 当前素材池缺图：先发 `ask_user` 占位卡。占位卡里至少写清图片用途、主体/场景、构图与比例、是否需要暗背景/留白、安全/授权要求，以及“这张图会落到背景 / 普通图片 / native slot 哪个 owner”。如果用户选择补图，等素材入池后再继续选图和落版。
- 公开图片：`web_search(mode='image' 或 'mixed', materialize=true)` 找候选并入素材池；背景图必须传 `use_case='background'`，正文公共图片传 `inline`，证据/来源图传 `evidence`，并在 `purpose` 里写明封面/章节/内容页/景点亮点/场馆展示/产品展示/人物介绍/案例证据等用途。返回的 `image_asset.asset_id` / `selected_image_binding` 默认写入背景或 `merge_slide_picture_binding` 普通图片计划，不为了“接入 SVG”而二次包装成 native slot。写素材索引文件时必须保留完整 `material_id/read_ref`，不要只写短 ID。
- 生图：`generate_image(target='slide_image')` 或委派 `slide_image_generator`，不能伪装成公开来源。背景氛围图优先进 `deck_framework.background`；正文图调用 `merge_slide_picture_binding` 落为 PPT picture，只有 SVG 局部图位才写 native-data。若要做系统补位，先确认它不承担真实证据职责；需要“SVG 感”时，要求输出扁平、无文字、易重绘的 SVG-friendly 插图规格，而不是声称已经得到可编辑 SVG 文件。
- 正文局部图片：若只是普通证据图/书封卡/配图，调用 `merge_slide_picture_binding(image_binding=selected_image_binding, box=...)` 写入 `artifacts.picture_bindings[]`；若当前页走 SVG route 且需要精确局部几何占位，才使用 `layout-native-image-slot.md` 的 `native_image_slot` + `native-data.json images[]` 合同。
- 远端图片必须先进入受控素材池再以 `asset_key` 引用；renderer 可预物化受控背景/纹理 `asset_key`，但模型不能把任意外部 URL 当成可直接下载的落版源。

## image_asset_selector

当同一 `material_id` 下有多张 `image_assets`，但当前步骤还拿不到精确
`asset_id` 时，可写 selector 让 renderer 按 metadata 稳定选图：

```json
{
  "material_id": "mat-story",
  "image_asset_selector": {
    "page": 2,
    "index": 0,
    "source_kind": "embedded",
    "source_filename": "chapter-two.pptx"
  }
}
```

可用字段：`page`、`index`、`source_kind`、`source_filename`、`asset_index`。
`asset_index` 是该 material 下 image_assets 的 0 基顺序。selector 未命中时不应回退首图；
模型需要改写 selector、请求用户确认，或改用明确 `asset_id / asset_key / url`。

## license 检查

- `commercial_only=true` 时，不把 unknown / uncertain license 图片写入素材池。
- 搜到图片但来源页不可访问时，不进入可商用素材池。
- 需要署名时，caption 或素材 metadata 必须保留 attribution。
- 生图不能声称来自真实地点、作者或书封，除非用户明确提供参考素材和授权边界。

## 失败降级

- 背景图找不到安全来源：先发占位卡请求用户补图；用户允许系统补位时，再改走生图抽象意象；若仍不适合生图，退回 `solid` / `svg` / `paper_light` 安全背景。
- 书封/作者图授权不清：询问用户提供素材，或改用书籍/纸张/海浪/道路等象征图。
- 图片策略禁用：改用纯色/纸张纹理背景和文字排版，不偷偷调用外部图片，也不偷偷用生成图冒充真实素材。
- 普通图片 binding 解析失败：保留相同 `picture_id` 修复 `asset_id / asset_key / selector / 受控 URL`，或替换为已入池图片；不得删除后用 SVG 画一个“看起来像图片”的替代物。
