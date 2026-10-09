<!--
id: content-pyramid-claim-evidence-action
category: content-structure
read_when: 需要结论先行、三证据和行动收口
page_roles: content, summary
supports: svg_drawingml
outputs: content_slots
depends_on: contract-content-density.md
max_use: 只读取本文件，不要连带读取同类全部文件
-->

# Content: Pyramid Claim Evidence Action

## 内容说明

结构：`结论 -> 证据 1/2/3 -> 行动或风险`。标题必须是判断句，不是名词。

模板：

```text
本页观点：在 [背景/约束] 下，[核心判断]，关键来自 [三类抓手]。
证据 1：[事实/数据]，说明 [解释]。
证据 2：[案例/对象]，说明 [影响]。
证据 3：[动作/机制]，支撑 [结果]。
行动/风险：[下一步/需决策/需补充]。
```

## 视觉说明

顶部结论条最醒目，主体三证据卡同宽或一强两弱，底部行动条收口。

## SVG说明

分组：`key-message`、`evidence-1..3`、`actions`、`source-note`。
