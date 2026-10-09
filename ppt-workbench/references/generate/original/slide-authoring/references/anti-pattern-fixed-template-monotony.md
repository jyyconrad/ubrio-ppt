<!--
id: anti-pattern-fixed-template-monotony
category: anti-pattern-qa
read_when: 多页看起来都是同一种三卡/四卡/指标条模板
page_roles: content, summary
supports: svg_drawingml
outputs: fix_rules, composition_variation_checklist
depends_on: contract-structure-hierarchy.md, gold-structure-composition.md
max_use: 只用于修正模板感，不要替代具体 layout 或 content reference
-->

# Anti Pattern: Fixed Template Monotony

## 问题表现

- 每页都是标题、key message、指标条、三卡或四卡。
- `gold_cards` 被当成默认答案，而不是当前页信息层级的落地形式。
- 卡片大小一致、内容层次一致，没有证据表、台账、时间线、对比、矩阵或行动条。
- 多页之间只换文字，不换结构承载方式。

## 修复规则

1. 先补 `structure_hierarchy`，写清语义层、讲述层、视觉层、几何层、SVG group 层。
2. 选择一个 `gold-structure-composition` 模式替换固定卡片。
3. 至少引入一个非卡片化主体：证据表、问题漏斗、时间线、对比带、行动台账或风险阶梯。
4. 相邻正文页不得连续使用完全相同的 `layout + svg_group_layer`。
5. 如果保留卡片，卡片内部必须有不同信息角色：判断卡、证据卡、行动卡、风险卡。

## 替换建议

- 经营结果页：用 `north-star + metric-strip + evidence-cluster + action-bar`。
- 痛点页：用 `left-diagnosis + right-proof-chain + bottom-contract`。
- 计划页：用 `stage-timeline + milestone-cards + acceptance-rules`。
- 能力页：用 `central-judgment + radial-capabilities + risk-strip`。
- 对比页：用 `comparison-before-after + evidence-table + decision-strip`。

## QA

- 多页 deck 中，正文页结构组合至少有 3 种。
- 当前页主体区超过 60% 面积承载信息，而不是重复装饰。
- 看到 `layout=gold_cards` 时，必须解释为什么卡片是最佳承载方式。
