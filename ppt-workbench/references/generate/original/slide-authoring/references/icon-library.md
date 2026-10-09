<!--
id: icon-library
category: asset-reference
read_when: 当前 SVG 页面需要业务图标或图标槽位
page_roles: content, summary
supports: svg_drawingml
outputs: icon_query_rules, icon_slot_contract
depends_on: contract-icon-usage.md
max_use: 只读取图标规则，不读取 assets/icons 原始图标文件
-->

# Icon Library Reference

固定图标库目录：

`backend/app/skills/slide-authoring/assets/icons/`

图标索引文件是 `icon-index.json`。模型不直接读取原始图标文件，必须通过工具查询。

模型不直接读取该目录。需要任何业务图标、箭头图标、能力图标或装饰性图标时，必须调用
`search_svg_icons`，从结果中选择 `icon_id`，再在 SVG 中写 `data-icon-id` 槽位。

## 使用规则

- 不临场手绘业务图标，不用 emoji，不用文本符号伪装图标。
- 不猜图标文件路径，不复制原始 SVG path。
- 不写 `<use data-icon="...">`；renderer 只识别 `data-icon-id` 槽位。
- 同一页只用一种图标风格：线性或面性。
- 图标颜色必须来自当前视觉 token，通常用 `accent-color` 或 `title_text-color`；正文辅助图标可用
  `body_text-color`。
- `data-icon-color` 默认省略；renderer 会优先消费
  `style_manifest.object_defaults.icon.default-color-ref`，再从 `style_manifest.palette` /
  `deck_framework.theme` 兜底到当前主题色。
- 图标只是辅助，不得替代标题、证据和行动文字。

## 查询方式

```json
{
  "query": "经营增长 数据 柱状图",
  "category": "biz",
  "style": "line",
  "output_mode": "editable_svg",
  "limit": 5
}
```

## 槽位写法

```xml
<g id="icon-growth"
   data-icon-id="biz/data-bars"
   data-icon-box="110 320 56 56"
   data-icon-container="rounded_rect"
   data-icon-inset="0.18"/>
```

`data-icon-box` 格式固定为 `x y w h`。`data-icon-color` 只有需要覆盖默认图标色时才填，
且必须来自 `style_manifest.palette` 中某个 `*-color` 槽位。`data-icon-container` 可用 `none`、`circle`、
`rounded_rect`、`square`、`pill`。

带容器的图标槽位会默认把内部 glyph 内缩，避免图标贴满圆形/方形容器。KPI 卡片、指标条和
小型图标容器如果需要“容器明显、glyph 更轻”的效果，可显式写 `data-icon-inset="0.16..0.24"`；
该值按 `data-icon-box` 短边比例计算。无容器的独立图标通常不要写 inset。

同一个视觉位置只能有一个 `data-icon-id` 槽位；不要用两个相同或高度重叠的 `data-icon-box`
叠加图标来表达复合含义。需要复合含义时，选择一个更接近的图标，或用图标加短文字标签表达。

## 常用语义

- 增长/数据：`biz/data-bars`
- 目标/聚焦：`biz/target-eye`
- 传播/发布：`biz/megaphone`
- 资产/流转：`biz/asset-flow`
- 风险/预警：搜索 `风险 预警 shield warning`
- 协同/组织：搜索 `协同 团队 network`
- 时间/进度：搜索 `时间 进度 milestone`

## 缺图标时

如果 `search_svg_icons` 没有合适图标，用编号圆点、短标签或色条承载层级；不要现场画复杂图标。
