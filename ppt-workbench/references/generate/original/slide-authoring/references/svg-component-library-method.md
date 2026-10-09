<!--
id: svg-component-library-method
category: shape-patterns
read_when: 已有 deck 设计契约或参考图语汇，需要把某类高频组件转成可复制 SVG 片段并归档，且不确定是否已有同类片段时
page_roles: content, summary
supports: svg_drawingml
outputs: component_fragment_library, fragment_extraction_method
depends_on: svg-shape-patterns.md
relation_specs: requires:svg-shape-patterns, pairs_with:contract-reference-image-benchmarking
triggers: 组件库, 组件片段, 提取组件, 图形片段怎么写, 复用片段, 卡片怎么画, 徽标怎么画, 六边形怎么画, 别再画一遍, 片段归档, 查重, 跨页一致
max_use: 只讲片段提炼与归档方法；具体基础片段清单读 svg-shape-patterns
-->

# SVG Component Library Method

本颗粒讲**方法**，不是又一份片段清单：如何从参考图 / deck 设计契约提炼出可复制的 `<g>` 组件片段并归档。基础片段库本身是 `svg-shape-patterns.md`，本文件教怎么往里加、怎么复用，不重列它已有的片段。

## 为什么用片段而不是文字描述

**可复制片段比文字描述可靠一个量级**，是多页一致性的核心机制。同一类组件（指标卡 / 论证卡 / 徽章 / 进度环 / 表头）跨页一致，靠的是**每页复制同一段 `<g>` 改参数**，不是靠每页照文字描述重画——重画必然产生圆角 / 投影 / 字重 / 边距的微差。

## 先查重再落笔

提炼任何组件前，**先搜 `svg-shape-patterns.md` 是否已有同类画法**：

- 有同类（流程节点 / 指标卡 / 增长徽标 / 环形 gauge / 折角卡 / 房形题头 / 证据卡 / 风险动作条 / 连接箭头）→ **直接复用改参**，不新造。
- 只是尺寸 / 配色 / 文案不同 → 那是"改参"，不是"新组件"，仍复用既有片段。
- 确实是库里没有的画法 → 才进入下面的提炼归档流程。

违反查重 = 制造第二种画同一组件的方式，直接破坏跨页一致性。

## 提炼与归档四步

1. **定位语汇**：从 deck 设计契约的"组件语汇线索"（见 `contract-reference-image-benchmarking.md`）挑出高频、值得复用的组件；一次性、只出现一页的造型不必归档。
2. **抽几何逻辑**：只抽**顶点逻辑与比例关系**（如"折边 f 取卡宽 12%-16%"），不抽本次的绝对坐标——绝对坐标是某页安全区算出来的，换页即失效。
3. **参数化占位**：把颜色、字体、可变文案换成 `{{token}}` 占位（见下）。
4. **归档进 `svg-shape-patterns.md`**：作为新增一节，标题写组件名，正文一句话说明用途与回指来源，附最小 `<g>` 片段。片段档案至少含：稳定 `id`、`{{token}}` 占位、一句参数说明（哪些值可改）。

## 占位约定

片段里**一律用 `{{token}}` 占位，不内联具体色值 / 字体名**。复制后由使用页替换为当前 deck 的对应 token：

```xml
<!-- 组件档案：{{comp_name}}；可改参数：宽高、{{accent}}、标签文案 -->
<g id="{{comp_name}}-1">
  <rect width="{{w}}" height="{{h}}" rx="16" fill="{{surface}}" stroke="{{border}}"/>
  <text x="20" y="52" fill="{{title_text}}" font-family="{{font_cn}}"
        font-size="40" font-weight="800">{{value}}</text>
  <text x="20" y="88" fill="{{body_text}}" font-family="{{font_cn}}"
        font-size="15">{{label}}</text>
</g>
```

颜色 token 由当前 deck 的 `background` / `surface` / `title_text` / `body_text` / `accent` / `border` 替换；字体 token（`{{font_cn}}`）按 `contract-font-portability.md` 的白名单字体替换。**内联的裸 hex / 裸字体名仅为示意，不得照抄进成稿。**

## 跨页一致性检查

- **同组件跨页参数漂移视为违约**：同一类组件在不同页出现圆角 / 投影 / 字重 / 边距不一致，即判违约。修法是回到唯一片段复制改参，不是逐页手调。
- 新组件归档后，全 deck 该类组件都应从这一个片段派生；发现两处画法不同，合并到一个片段。
