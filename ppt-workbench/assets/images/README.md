# 内置图片库（assets/images）

本目录是 ppt-workbench 的内置商务图片库，由 `image-index.json` 统一登记。检索与 stage：`scripts/assets/search_images.py`；嵌入配方：`references/generate/methods/image-library.md` 与 `references/generate/methods/image-owners.md`。

## 分类

| 目录 | 内容 | 典型用途 |
| --- | --- | --- |
| `cover-city/` | 上海/香港/北京/重庆城市天际线夜景 | 封面、章节页底板 |
| `cover-abstract/` | 夜色光轨、抽象光影 | 封面、章节页底板 |
| `business-meeting/` | 会议、洽谈、团队协作 | 正文配图 |
| `business-cooperation/` | 握手、合同签署 | 正文配图 |
| `office-work/` | 办公工位、培训教室 | 正文配图 |
| `industry-factory/` | 生产线、装配、焊接、厂区夜景 | 正文配图 |
| `logistics-port/` | 集装箱港口、码头航拍 | 正文配图 |
| `tech-data/` | 数据中心机柜、机房运维 | 正文配图 |
| `nature-milestone/` | 山峰、日出 | 章节页/收尾页底板 |

## 来源与许可

所有图片来自开放许可来源，逐张记录在 `image-index.json` 的 `source` 字段（`site` / `title` / `creator` / `license` / `page`）：

- **Wikimedia Commons**：CC0、CC BY、CC BY-SA 或 Public domain；来源页见 `source.page`。
- **Openverse**（stocksnap.io / rawpixel 等）：CC0。

使用规则：

1. CC BY / CC BY-SA 图片在对外交付时应保留署名信息（页面备注、交付说明或 credits 汇总均可引用 `source` 字段）。
2. 本图库随 ppt-workbench 仓库分发。每张图的许可以 image-index.json 的 source.license 为准。CC BY / CC BY-SA 在对外交付的 PPT 中仍需署名。不要把整库说成单一公有领域授权，也不要用这些图冒充用户的真实证据。
3. 内置图是通用场景图，不得冒充用户真实证据、客户现场或数据截图。

## 维护者规则（新增/替换图片）

- 只收 JPEG、横构图、宽度 ≥1920（封面类）或 ≥900（正文类，stocksnap 960w 可接受）。
- 逐张人工目检后再入库；淘汰空场景、水印、剪贴画、历史黑白照、全景鱼眼图。
- 每张必须补齐 `image-index.json` 条目：中文标题、分类、标签、尺寸、用途、来源五字段缺一不可。
- 同名或同画面（md5 相同）不得重复入库；替换图片时同步更新 `source`。
- 下载与索引构建脚本不入库到技能目录，只在维护工作区执行；入库即视为已核验许可。
