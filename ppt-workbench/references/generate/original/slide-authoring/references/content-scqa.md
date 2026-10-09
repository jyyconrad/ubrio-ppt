<!--
id: content-scqa
category: content-structure
read_when: 需要背景、冲突、问题、答案的故事链
page_roles: content, section_divider
supports: svg_drawingml
outputs: content_slots
depends_on: contract-content-density.md
max_use: 只读取本文件，不要连带读取同类全部文件
-->

# Content: SCQA

## 内容说明

结构：Situation 情境 -> Complication 冲突 -> Question 问题 -> Answer 答案。

模板：

```text
情境：当前 [趋势/背景] 正在发生。
冲突：但 [约束/风险/矛盾] 造成阻塞。
问题：关键不在于 [表层问题]，而在于 [核心问题]。
答案：因此本页提出 [方案/抓手/路径]。
```

## 视觉说明

冲突和答案形成强对比。答案模块必须是页面主视觉之一。

## SVG说明

分组：`situation`、`conflict`、`question`、`answer`。
