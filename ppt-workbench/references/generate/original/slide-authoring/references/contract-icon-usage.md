<!--
id: contract-icon-usage
category: execution-contract
read_when: 当前页需要业务图标或图标槽位
page_roles: content, summary
supports: svg_drawingml
outputs: icon_rules
depends_on: icon-library.md
max_use: 只读取本文件，不要连带读取同类全部文件
-->

# Icon Usage Contract

## 内容说明

图标只做扫读辅助，不能替代标题、证据和行动。每个图标必须对应一个明确业务语义。

## 视觉说明

同一页只用一种图标风格。图标颜色来自 `style_manifest.palette` 的 `accent-color`、
`title_text-color` 或 `body_text-color`，深色背景用浅色图标，浅底卡片用深色或主色图标。
后端会把这些模型友好的字段规范化成内部 `accent` / `title_text` / `body_text` token。
如果 `style_manifest.object_defaults.icon.default-color-ref` 已存在，优先按它引用的
`*-color` 槽位作为图标默认色；缺失时再从 `accent-color`、`title_text-color`、
`body_text-color` 和 `deck_framework.theme` 兜底。

## SVG说明

只要当前页需要图标，就必须先调用 `search_svg_icons` 查询固定图标库，再写槽位。
模型不得自己造图标、手写复杂图标 path、用文本符号或 emoji 伪装图标，也不得猜测图标文件路径。

```xml
<g id="icon-risk"
   data-icon-id="biz/target-eye"
   data-icon-box="110 320 56 56"
   data-icon-color="#2563EB"
   data-icon-container="rounded_rect"
   data-icon-inset="0.18"/>
```

`data-icon-color` 可以来自 `accent-color`、`title_text-color` 或 `body_text-color`；
常规情况下可以省略，让 renderer 结合 `style_manifest.object_defaults.icon.default-color-ref`、
`style_manifest.palette` 与 `deck_framework` 自动补默认图标色。只有同页少量图标需要语义区分时，
才显式填写具体 HEX。
若省略，renderer 会结合 `deck_framework` / `style_manifest` 自动补默认图标色。
`data-icon-container` 不为 `none` 时，renderer 默认会把内部 glyph 相对容器内缩；如果预览中图标仍显得过大，
在 KPI 卡、指标条、圆形头像式图标等场景显式写 `data-icon-inset="0.16..0.24"`，不要通过缩小整个
`data-icon-box` 牺牲容器尺寸。
同一个视觉位置不要叠放两个 `data-icon-id` 槽位；重叠图标会在 PPTX 中显得拥挤且难以编辑。
禁止 `<use data-icon="...">`、远程图标、emoji、
文本符号伪图标和临场手绘复杂业务图标。
