# 内置图片库检索

本技能在 `assets/images/` 内置 40+ 张可直接使用的商务图片（封面底板、会议、合作、办公、工厂、物流、数据中心、山峰日出），统一由 `image-index.json` 记录标题、标签、尺寸、用途和来源许可。检索与 stage 入口是 `scripts/assets/search_images.py`；嵌入规则仍按[图片三个 owner](image-owners.md)执行，本页只解决"图片从哪来"。

## 活动步骤

1. 先检索，只拿元数据（不返回图片内容）：

```bash
python3 scripts/assets/search_images.py --query "封面 城市夜景" --limit 5
python3 scripts/assets/search_images.py --list   # 查看分类
```

返回 `image_id`、`title`、`category`、`tags`、`width/height`、`recommended_usage`、`source`（站点与许可）。

2. 把选中的图 stage 到页面目录（复制为本地文件，满足"图片必须本地文件"合同）：

```bash
python3 scripts/assets/search_images.py \
  --stage cover-city-01 --dest <页面目录> [--rename cover-plate.jpg]
```

输出包含 `staged_path`、许可和来源页。禁止在生成的 PPTX/SVG 中引用技能内置路径或远程 URL——必须先 stage。

3. 按用途选择 owner：

- 封面/章节底板：stage 后写页面目录的 `deck-framework.json` `background`（`type: photo_dark` + overlay），不要做 1280×720 `native-image-slot`。
- 正文配图：与卡片/文字几何对齐时用 `native-image-slot` + `native-data.json` `images[]`；不对齐时用 `scripts/native.cjs` 的 `image()`。
- 截图证据：不用内置图库。内置图是通用场景图，不能冒充用户真实证据或截图。

4. 署名：`source.license` 为 CC BY / CC BY-SA 的图片，对外交付时保留署名（页面备注、交付说明或 credits 汇总均可）；CC0 / Public domain 无强制要求但建议在索引中保留记录。

## 选择原则

- 底板选深色、低对比区域大的图（`cover-*`、`nature-milestone`），保证浅色标题可读。
- 正文配图与页面判断相关时才用；没有图片也能讲清楚时，优先不放图。
- 同一整册的底板风格保持一致（同为夜景或同为光轨），不逐页混用。

## 禁止

- 引用 `assets/images/` 原路径进 PPTX（必须 stage 成本地副本）
- 用内置图冒充用户证据、客户现场或数据截图
- SVG `<image href>`、远程 URL、`previewUrl`
- 二次分发图库或删除 `source` 字段；许可边界见 `assets/images/README.md`

维护者规则（新增/替换图片）见 `assets/images/README.md`。
