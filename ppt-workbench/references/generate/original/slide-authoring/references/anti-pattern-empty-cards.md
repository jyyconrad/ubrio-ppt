<!--
id: anti-pattern-empty-cards
category: anti-pattern-qa
read_when: 卡片大片空白、只有编号标题和一行说明
page_roles: content
supports: svg_drawingml
outputs: fix_rules
depends_on: contract-content-density.md, contract-layout-density.md
max_use: 只读取本文件，不要连带读取同类全部文件
-->

# Anti Pattern: Empty Cards

## 内容说明

错误卡片通常只有“01 + 标题 + 口号”。修正为：短标题、判断句、2-3 条证据、指标/风险/动作标签。

可补信息：

- 对象、周期、责任、场景。
- 指标、同比/环比、完成率。
- 风险等级、待决策事项。
- 来源、口径、需补充项。

## 视觉说明

卡片高度明显大于内容时，缩小卡片、增加底部行动条，或改成左主结论 + 右证据。

## SVG说明

每张卡建议至少 4 个文本节点：标题、判断、两条证据/行动、标签或来源。
