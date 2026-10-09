# SVG Icon Library

本目录内置两个图标家族，统一由 `icon-index.json` 索引：

- **lucide line**（约 1700 条）：`lucide/svgs/*.svg`，ISC License，线型，`icon_id` 为 lucide 短名（如 `chart-bar`、`target`）。
- **mdi filled**（约 3600 条）：`mdi/svgs/*.svg`，来自 [@mdi/svg](https://github.com/Templarian/MaterialDesign-SVG) 7.4.47（Apache-2.0）业务子集，填充型，`icon_id` 带 `mdi-` 前缀（如 `mdi-factory`、`mdi-trending-up`）。

不要直接打开原始 SVG。检索与展开：

```bash
python3 scripts/svg/search_icons.py --query "经营增长 柱状图" --style line --limit 5
python3 scripts/svg/search_icons.py --query "工厂 风险预警" --style filled --limit 5
python3 scripts/svg/search_icons.py --expand source.svg --output expanded.svg
```

返回 `icon_id` / `label` / `slot_example`，不含 `path`。页面只写 `data-icon-id` + `data-icon-box`。同一页只用一个家族。活动配方见 `references/generate/methods/icon-embed.md`。

整理规则（维护者）：

- 只放本地 SVG，不放远程 URL。
- 每个图标保留 `viewBox`；lucide 用 `stroke="currentColor"`，mdi 用 `fill="currentColor"`。
- 删除 `<style>`、`class`、`script`、`foreignObject`、`symbol`、`use`、动画。
- 优先 `currentColor` 或单色，便于统一设色。
- `icon_id` 使用索引里的稳定 id（lucide 短名或 `mdi-` 前缀名），不要发明 `biz/data-bars`。
- 来源与许可必须保留：lucide ISC、@mdi/svg Apache-2.0（7.4.47）；更新 mdi 子集时同步记录版本。
