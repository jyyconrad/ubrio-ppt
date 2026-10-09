<!--
id: layout-native-image-slot
category: layout
stage: slide_generation
read_when: SVG DrawingML 页面已经确定需要在正文局部嵌入图片，并需要用 slot 精确约束图片几何
page_roles: content, summary
style_family: literary_documentary_cn
ppt_types: book_analysis, literary_documentary, keynote, briefing
visual_tags: native_image_slot, user_image_asset, uploaded_image, embedded_image, inline_image
content_categories: layout, execution_contract, asset_reference
supports: svg_drawingml
outputs: svg_layout, native_image_slots, native_data_images, image_asset_binding
depends_on: image-sourcing-commercial-or-generated.md
max_use: 只负责正文局部图片 slot 的 SVG 与 native-data 合同；整页背景仍走 deck_framework
-->
# Layout: Native Image Slot
## 核心契约

SVG 只声明图片槽位的位置、尺寸和语义；真实图片由当前页 `native-data.json` 的 `images[]` 提供，renderer 会按 `slot_id` 把图片写成 PowerPoint 原生 picture。
这条路线只用于“当前页已经选择 SVG route，且正文局部图片必须和文字/卡片精确对齐”的场景。公开图片、生图或用户上传图首先都是素材层资产；是否进入本 slot，由页面布局决定，而不是由图片来源决定。
- SVG 中不要写 `<image href="...">`，也不要把远程 URL 直接塞进图层。
- 图片 slot 必须有稳定 `id`，并写 `data-role="native-image-slot"` 与 `data-native-image="true"`。
- SVG 根节点写 `data-native-data-ref="slide-generation/<page_id>/native-data.json"`。
- `native-data.json` 中的 `images[].slot_id` 必须与 SVG slot `id` 一致。
- 有 `native-image-slot` 但缺少同页 `native-data.images[].slot_id`，或 `data-native-data-ref` 指向缺失/错页文件时，必须让 renderer 阻断并要求修正；不要静默退化为空占位。
- 图片来源优先使用素材解析产生的 `image_assets[].asset_id` / `material_id`；如已明确选中单图，也可直接写 `asset_key/key`。
- `url` 只允许本地文件服务相对路径，例如 `/v1/files/...`，且不能作为唯一落版入口；不要写外部 URL、确认卡 `previewUrl` 或临时预签名 URL。
- 同一 material 有多张图时，优先写精确 `asset_id`；如果只能基于页码、文件名、来源类型或素材顺序选择，可写 `image_asset_selector`。
- 新生成页面默认使用 `viewBox="0 0 1280 720"` 作者坐标；历史/benchmark 中的 `1600x900` 可被 renderer 归一化，但不要作为新页默认坐标。

## 多模态选图边界

用户上传图片和上传文件剥离图片会进入素材解析结果的 `image_assets`。具备多模态理解能力的模型可以基于图片内容给出 `ranked_asset_ids`，再调用 `get_materials(action='prepare_image_candidates')` 生成 `ask_user_args`；若本次必须按画面语义判断，传 `requires_content_understanding=true`，文本模型会被工具层阻断，多模态模型若没有提供看图后的 `ranked_asset_ids` 也会被阻断。不要重造确认卡参数，直接把返回的 `ask_user_args` 交给 `ask_user`；如果返回 `NO_IMAGE_ASSET_CANDIDATES`，先补图片来源。`previewUrl / provider / license / commercialOk / attribution` 只服务用户复核，不是落版源。续跑后调用 `resolve_image_candidate_selection`；只有本页确实存在 SVG 图片 slot 时，才使用 `native_data_image` 并调用 `merge_native_data_image` 写入 `native-data.json images[]`。普通文本模型只能基于文件名、页码、metadata、用户明确指定或确认卡结果选图，不能声称自己看过图片。

当书封、作者肖像、真实人物或影视截图涉及身份/授权时，先读 `image-sourcing-commercial-or-generated.md` 决定是否复用用户素材、公开可商用检索或生图替代。

## 缺图补位顺序

当前页已经决定采用 `native-image-slot`，但现有素材里没有合适图片时，按下面顺序处理：

1. 先用 `ask_user` 发**图片占位卡**，明确写出：
   - `slot_id` 对应的页面语义（例如书封、人物、现场证据、地点意象）。
   - 期望主体、构图、横竖比例、裁切重点、是否需要保留人物头部/书名/票据关键字段。
   - 该 slot 是否要求真实素材、是否接受风格化替代图。
   - 当前为什么不能直接落版（无候选、候选不匹配、授权不清等）。
2. 用户补图后，继续走 `prepare_image_candidates` / `resolve_image_candidate_selection`，再用 `merge_native_data_image` 写回。
3. 若用户允许系统补位，且这个 slot 只承担象征性/氛围性/说明性插图，而**不承担真实证据或真实身份**职责，可委派 `slide_image_generator` 生成替代图。
   - 委派时要求输出扁平、矢量感、无文字、边缘清晰、便于 cover/contain 和后续重绘的 SVG-friendly 插图。
   - 当前运行时拿回的是受控图片资产与结构化规格，**不是可编辑 SVG 文件**；主 Agent 要么把它当图片嵌入 `native-data.json images[]`，要么基于返回的 `visual_design_spec` / `native_object_plan` 在本页 SVG 中自行重绘。
4. 书封、作者照、真实人物、影视截图、合同/票据/监控截图等真实性强的 slot，不要用生成图冒充；这类 slot 继续保留占位卡，请用户补图，或改版为无图结构。

## native-data JSON

推荐先写 `native-data.json`，再写 SVG slot：

```json
{
  "version": 1,
  "images": [
    {
      "slot_id": "book-cover-image",
      "asset_id": "material-123:embedded:1:0",
      "asset_key": "materials/material-123/extracted-images/1-0.png",
      "url": "/v1/files/{bucket}/materials/material-123/extracted-images/1-0.png",
      "fit": "cover",
      "crop": {"mode": "center", "focal_x": 0.5, "focal_y": 0.5},
      "corner_radius": 0.16,
      "caption": "用户上传书封",
      "source": {
        "material_id": "material-123",
        "source_kind": "embedded",
        "page_index": 1
      }
    },
    {
      "slot_id": "chapter-photo",
      "material_id": "material-456",
      "image_asset_selector": {"page": 2, "index": 0, "source_kind": "embedded"},
      "fit": "cover",
      "caption": "上传文件第 2 页剥离图"
    }
  ]
}
```

字段规则：

- `slot_id`：必填，绑定 SVG 图片槽位。
- `asset_id/material_id`：优先使用精确 `asset_id`，renderer 会从 workspace `image_assets` 自动解析到受控图片素材；裸 `material_id` 只允许该 material 只有一张图片时使用，一个 material 有多张图时必须写 `asset_id` 或 `image_asset_selector`。
- `image_asset_selector`：可选，仅在只知道 `material_id` 但需要从多张图里选一张时使用。支持 `page / index / source_kind / source_filename / asset_index`；selector 未命中时 renderer 不会回退首图，避免误嵌图片。
- `asset_key`：可选，必须来自受控素材池，例如 `materials/...`、`generated-slides/...`。
- `url`：可选，只能是本地文件服务相对路径；不要写任意外部 URL。若同时带 `asset_id/material_id/selector`，renderer 会从 workspace 回填稳定 `asset_key`，`url` 不作为唯一落版源。
- `previewUrl`：不要写入 `images[]`。它只属于确认卡 UI 选项，用于显示缩略图和触发受控预览 endpoint。
- `fit`：默认 `cover`，会写入 PowerPoint picture crop；需要完整书封/截图时可写 `contain`，renderer 会在 slot 内等比居中。
- `crop`：可写 `{"mode":"center"}` 或 `{"focal_x":0.5,"focal_y":0.5}`。`mode` 支持 `top/bottom/left/right` 这类方向词；`focal_x/y` 为 0..1，表示 cover 时尽量保留的图片焦点。
- `corner_radius`：可选，单位为英寸，写正数时 renderer 会把 PowerPoint 原生 picture 几何改为 `roundRect`；也兼容 `radius / cornerRadius / border_radius / borderRadius`。
- `caption/source`：保留来源，尤其是用户素材、公开可商用图片和证据图。

当前 renderer 已支持 `cover/contain`、焦点裁切和原生 picture 圆角。需要圆角观感时，仍建议在 SVG 内容层保留同尺寸圆角占位框/底板，方便预览理解；最终图片由 renderer 叠加为原生 picture。

## SVG Slot 写法

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1280 720"
     data-native-data-ref="slide-generation/page-4/native-data.json">
  <rect x="74" y="77" width="1133" height="566" rx="22"
        fill="#F5EFE4" stroke="#D8C7A3"/>

  <g id="book-cover-image" data-role="native-image-slot" data-native-image="true"
     data-x="816" data-y="152" data-w="264" data-h="376">
    <rect x="816" y="152" width="264" height="376" rx="14"
          fill="#E8DCC8" stroke="#B89A5B"/>
    <text x="835" y="555" fill="#7A5C2D" font-size="14">书封图片</text>
  </g>
</svg>
```

Slot 外框和标签可以保留为轻量占位，方便预览理解；最终图片会以原生 picture
叠加在同一区域。占位图形不要遮住主体文本，也不要承担真实图片内容。

## 适用场景

- 书籍深度解析：书封、作者照、人物关系页里的局部人物图。
- 业务汇报：案例截图、合同/票据局部图、现场照片、用户上传证据图。
- 公共图片图文页：景点、城市地标、场馆、园区、产品、讲师/人物、活动现场等图片，只有在需要与 SVG 内部标题、说明块或卡片精确对齐时才进入 native-image-slot；普通图文页优先走 `merge_slide_picture_binding`。
- 文学纪录片风格：左文右图 editorial panel、两栏人物对照、浅色纸张上的书封锚点图。
- 数据页：图表旁边的小型证据图；真实图表/表格仍走 `layout-native-chart-slot.md`。

## 禁止

- 不要用 SVG `<image>` 链接外部图片。
- 不要把整页背景图做成 native image slot；背景统一交给 `deck_framework.background`。
- 不要为了使用本能力而把公开图片或生成图强行写入 `images[]`；没有 SVG 局部图片位时，普通图应调用 `merge_slide_picture_binding` 写入 `artifacts.picture_bindings[]`，背景图走 `deck_framework.background`。
- 不要把没有授权确认的公开图片写入 `images[]`。
- 不要在没有多模态能力时基于“看起来像...”选择用户上传图片。
- 不要只写空图片槽位不写 `images[]`；如果本页已经采用 SVG 图片槽位并完成选图确认，必须调用 `merge_native_data_image` 写回，否则 renderer 会在渲染前阻断。
- 不要因为当前缺图就静默删掉语义关键 slot；除非你已经明确改版并向用户说明“本页不再使用该图位”。
