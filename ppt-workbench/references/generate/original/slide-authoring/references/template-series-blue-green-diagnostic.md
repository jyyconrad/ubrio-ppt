<!--
id: template-series-blue-green-diagnostic
category: template-series
read_when: 需要复用 ppt2 的蓝绿问题改进系列，用双语义域表达问题、改进、亮点短板或复盘规划时
page_roles: content, summary
supports: svg_drawingml
outputs: series_visual_contract, page_archetype_menu, shape_composition_grammar, composite_resource_plan
depends_on: template-series-composite-builder.md, layout-problem-improve-value-rail.md
relation_specs: requires:template-series-composite-builder, pairs_with:composition-diagnostic-insight-grid, pairs_with:layout-problem-improve-bilateral, pairs_with:layout-diagonal-duo-panels
max_use: 蓝绿分别代表两个稳定语义域；不得逐页反转或逐卡随机换色
source_notice: 来源为 ppt2.jpg visual-only 营销拼页；不能推断原始对象、母版或可编辑性。
-->

# ppt2 系列：蓝绿问题改进与复盘

## 系列视觉逻辑

- 蓝与绿是固定语义域，分别承载问题/改进、亮点/短板或复盘/规划；具体含义一旦确定需跨页稳定。
- 白色证据卡和价值 rail 负责缓冲，不加入蓝绿对抗。
- 页面关系强调“转化、对照、方向”：相交圆、U 形箭头、斜向折带、双向箭头和中心环。
- 内容结构相同用镜像；结构不同时允许非对称，不能为视觉对仗编造条目。

## 页面展示系统

- 问题面板 + 改进面板 + 三条价值 rail。
- 亮点 vs 短板镜像对照。
- 复盘 vs 规划对角双栏。
- 2-4 组问题与改进的双侧转化。
- 中心优化闭环 + 周边问题/行动，只在存在反馈关系时使用。

## 形状组合语法

- `semantic panel A + semantic panel B + value rail` 用于结构不对称的两域。
- `paired rows + overlapping circles + numbered anchors` 用于可一一对应的问题改进。
- `diagonal divider + two independent evidence stacks` 用于两个独立主题并置。
- 深色面板反白文字；相交圆只放短标签，不承载长段落。

## 快速组合示例

“左侧列三项工作不足，右侧列三项改进，中间强调从问题走向优化”时，使用
`duotone_problem_improve`，分别填 `problems[2..4]`、`responses[2..4]` 和 `center_label`。
选择 `build-series-composite-svg` 物化资源后可继续替换 data，具体执行入口由当前 consumer 决定；
条数不一一对应时改用非对称 value-rail 布局。

## 容量与失败

- 两侧各 2-4 项；每项标题一行、解释不超过两行；中心圆只放 4-8 字。
- 失败：两域颜色语义翻转、问题和改进没有映射却画成转化、正文塞进圆、黑字落在深色面。
