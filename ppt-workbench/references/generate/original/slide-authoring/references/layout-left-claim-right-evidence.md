<!--
id: layout-left-claim-right-evidence
category: layout
read_when: 一个主判断需要配 2-4 条证据、案例或指标
page_roles: content
supports: svg_drawingml
outputs: svg_layout
depends_on: contract-layout-density.md
relation_specs: conflicts_with:layout-hero-metric-left-rail, requires:contract-gold-svg-builder, requires:structure-hierarchy
max_use: 只读取本文件，不要连带读取同类全部文件
-->

# Layout: Left Claim Right Evidence

## 内容说明

左侧写主判断、背景和关键指标；右侧写 2-4 条证据，每条包含事实、解释、来源或行动。若左栏改为深色实底、以单个统领巨数英雄化呈现（视觉最重的大数+一句总结），改 `layout-hero-metric-left-rail.md`；本颗粒左栏以文字主判断与论证为主，不做深色巨数 hero。

## 视觉说明

左侧更强，右侧证据卡清晰分层。两栏间距不少于 48px，主标题不被左侧大数字抢走。

## SVG说明

坐标骨架：

- `main-title`: `x=90 y=90`
- `key-message`: `x=90 y=165 w=1420`
- `left-claim`: `x=90 y=250 w=600 h=520`
- `right-evidence`: `x=760 y=250 w=750 h=520`

右侧证据卡建议高 `120-145`，间距 `22-28`。
