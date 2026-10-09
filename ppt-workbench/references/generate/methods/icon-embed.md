# 图标嵌入

Ubrio `search_svg_icons` 在本技能就是 `scripts/svg/search_icons.py`，检索捆绑图标索引 `icon-index.json`。不要调用宿主 `search_svg_icons`，不要读 `lucide/svgs`、`mdi/svgs` 原始文件，也不要把 `icon-library.md` 里的 `biz/data-bars` 当真实 id（本库没有这些 id）。

捆绑库有两个家族：**lucide line**（约 1700 个，`--style line`）和 **mdi filled**（约 3600 个，`--style filled`，id 带 `mdi-` 前缀）。线型适合白底描边风格；填充型适合彩色容器底、深色底板上的高对比小图标。同一页只用一个家族。

## 活动步骤

1. 先搜，只拿返回的 `icon_id`：

```bash
python3 scripts/svg/search_icons.py \
  --query "经营增长 柱状图" --style line --limit 5
python3 scripts/svg/search_icons.py \
  --query "工厂 风险预警" --style filled --limit 5
```

stdout 只有 `icon_id`、`label`、`category`、`style`、`keywords`、`slot_example`。没有 `path`，没有 `d`。

2. 把命中的 `icon_id` 写进空槽（标题/数字仍是 `<text>`，图标不进 `native-data.json`）：

```xml
<g id="icon-growth"
   data-icon-id="chart-bar"
   data-icon-box="110 320 56 56"
   data-icon-container="rounded_rect"
   data-icon-inset="0.18"/>
```

`data-icon-box` 固定 `x y w h`（1280×720）。常规省略 `data-icon-color`；同页少量语义对比时才写 HEX。容器：`none` / `circle` / `rounded_rect` / `square` / `pill`。同一视觉位置只放一个槽。

3. 同一页只用一种图标家族：`lucide line` 或 `mdi filled` 二选一。不要混用两家、不要混入手绘填充形、emoji 或另一套 icon set。

4. 预检会 expand `data-icon-id`（未知 id 失败关闭）：

```bash
python3 scripts/svg/overlay_native_slots.py \
  --svg source.svg --native-data native-data.json --validate-only

python3 scripts/svg/search_icons.py \
  --expand source.svg --output expanded.svg
```

5. 搜不到就用编号圆点、短标签或色条，不要现场画复杂图标。

## 禁止

- 手绘业务图标、emoji、文本符号伪装图标
- `<use data-icon>` / `symbol`
- 猜测 `biz/data-bars`、`biz/target-eye` 或任何未返回的 id
- 复制 lucide/mdi `path d` 或整份 SVG 进页面
- 把图标写进 `native-data.json`
- 同页混用 line 与 filled 两个家族

原始 `icon-library.md` / `contract-icon-usage.md` 仍写 Ubrio 工具名；本页才是可执行配方。
