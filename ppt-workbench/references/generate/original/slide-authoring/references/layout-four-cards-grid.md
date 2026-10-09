<!--
id: layout-four-cards-grid
category: layout
read_when: 四项机制、四个策略、四类问题、四个能力模块
page_roles: content
supports: svg_drawingml
outputs: svg_layout
depends_on: contract-layout-density.md, anti-pattern-layout-overflow.md
relation_specs: pairs_with:layout-quad-cards-core-cluster, requires:contract-gold-svg-builder, requires:structure-hierarchy
max_use: 只读取本文件，不要连带读取同类全部文件；需要中心关键词圆簇提炼四卡本质时读 layout-quad-cards-core-cluster.md
-->

# Layout: Four Cards Grid

## 内容说明

适合 4 个并列信息组。每组必须信息密度接近，不要让某张卡只有标题。

先确认这 4 项确实是并列关系，再用横排。如果是议程/问题清单，或每卡正文超过 2 行，
改用「2x2 决策矩阵」或「左侧结论 + 右侧四问题短列表」，不要硬撑四张等宽重卡。

## 视觉说明

四卡并列时避免第 4 张超出画布。主标题和核心结论占上方，主体卡片占中部。
每卡标题 ≤ 12 个中文字符，正文最多 2 行、每行 ≤ 18-20 个中文字符；超出先压短语、减条数，
仍装不下改 2x2 或上下双区，绝不裁断第 3/4 卡或缩到不可读字号。

## SVG说明

坐标骨架：

- `main-title`: `x=86 y=92`
- `key-message`: `x=86 y=170 w=1428`
- 四卡：`x=86/450/814/1178 y=290 w=336 h=380`
- 卡间距：`28`
- `actions` 可放 `x=86 y=715 w=1428 h=76`

如果正文较多，改成 2x2：`x=90/820 y=270/535 w=690 h=220`。
