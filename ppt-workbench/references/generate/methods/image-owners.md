# 图片三个 owner

Ubrio `merge_slide_background_binding` / `merge_slide_picture_binding` / `merge_native_data_image`、`ask_user` 确认卡和 `/v1/files` 在本技能不是入口。按用途只选一个 owner。本地 PNG/JPEG only。

没有本地图片时，先从内置图片库取：`scripts/assets/search_images.py` 检索并 `--stage` 到页面目录（配方见[内置图片库检索](image-library.md)）；用户证据截图永远用用户自己的文件，不用内置图。

## 1. 整页底板 → 页旁 `deck-framework.json`

封面/章节影像底板写在页面目录的 `deck-framework.json`，不要做成 1280×720 `native-image-slot`，也不要在内容 SVG 里画满页 `<rect>` / `<image>`。

```json
{
  "background": {
    "type": "photo_dark",
    "base_color": "#0B0F14",
    "image": "cover-plate.png",
    "overlay_color": "#0B0F14",
    "overlay_opacity": 0.4,
    "fit": "cover"
  }
}
```

`image` 必须是本地文件。正文数据页没有底板照片时用 `"type": "solid"`。原始 `theme-background-policy.md` 仍写 Ubrio 工具名；本页才是可执行配方。

## 2. 不对齐 SVG 的正文图 → `native.cjs` `image()`

图片不锁在 SVG 卡片/文字几何上时，不要开 `native-image-slot`。用本地路径：

```js
d.image(slide, localPng, box, {source, description, width, height})
```

`scripts/native.cjs` 拒绝 `https?://`。样例：`assets/examples/make_examples.cjs` 的 `09-evidence`。

## 3. SVG 对齐的证据截图 → `native-image-slot`

截图必须和标题/标注对齐时：先把 PNG 放到页面目录，再写 `native-data.json` `images[]`，SVG 只留空槽。说明文字在槽外，写清「能确认什么 / 不能推出什么」。

```xml
<g id="screenshot-proof-1" data-role="native-image-slot" data-native-image="true"
   data-x="64" data-y="120" data-w="620" data-h="360">
  <rect x="64" y="120" width="620" height="360" fill="none" stroke="#94A3B8" rx="12"/>
</g>
```

```json
{
  "version": 1,
  "images": [
    {
      "slot_id": "screenshot-proof-1",
      "asset_key": "evidence-synthetic.png",
      "fit": "contain"
    }
  ]
}
```

标题在 box 上方，caption/来源在旁边或下方 ≥36px，都在 `<g>` 外。

```bash
python3 scripts/svg/overlay_native_slots.py \
  --svg source.svg --native-data native-data.json --validate-only

python3 scripts/svg/overlay_native_slots.py \
  --svg source.svg --native-data native-data.json --output page.pptx
```

金标 `evidence_asset_slots` 只有本地 `asset_key` 时才写成 `native-image-slot`；没有本地文件就跳过该槽，不要留 `evidence-asset-slot`，也不要写 SVG `<image>`。

## 表格

明细/台账走 `native-table-slot` + `tables[]`，由 overlay 写成 PowerPoint 原生表。不要手绘表格、drawn grid 或 `rect` 单元格。

## 禁止

- SVG `<image href>` / `xlink:href`（含 data URI）
- `previewUrl`
- 远程 `http(s)://`、CDN、`/v1/files`
- `merge_native_data_image` / `merge_slide_picture_binding` / `merge_slide_background_binding`
- 1280×720 `native-image-slot` 冒充整页底板
- 用生成图或远程图冒充可核验证据
