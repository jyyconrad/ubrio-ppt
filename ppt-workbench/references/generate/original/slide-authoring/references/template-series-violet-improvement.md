<!--
id: template-series-violet-improvement
category: template-series
read_when: 需要复用 ppt6 的紫色存在不足与改进系列，用双圆转化、双侧问题措施或中心优化闭环表达整改时
page_roles: content, summary
supports: svg_drawingml
outputs: series_visual_contract, page_archetype_menu, shape_composition_grammar, composite_resource_plan
depends_on: template-series-composite-builder.md, layout-problem-improve-bilateral.md
relation_specs: requires:template-series-composite-builder, pairs_with:composition-diagnostic-insight-grid, pairs_with:layout-cycle-loop, pairs_with:layout-problem-improve-value-rail
max_use: 只在问题与改进存在清晰映射时使用双侧转化；中心圆不承载长文
source_notice: 来源为 ppt6.jpg visual-only 营销拼页；具体紫色、文案、Logo 和箭头装饰不晋级。
-->

# ppt6 系列：紫色不足与改进

## 系列视觉逻辑

- 白底、深紫主结构、浅紫辅助关系；左侧问题和右侧改进用同一家族的不同明度，而非多色分类。
- 第一类页面以相交双圆表达从“不足”到“改进”的转化，两侧编号条目形成对称扫描。
- 第二类页面以中心优化圆为锚，左右各放问题证据与改进行动，强调持续反馈。
- 页面必须从问题进入行动，不允许只列不足后停住。

## 页面展示系统

- 2-4 组不足 ↔ 2-4 组改进的双侧转化。
- 左侧问题证据卡 + 中心优化闭环 + 右侧改进卡。
- 问题和措施条数不等时，改非对称 value-rail，而不是强行凑对称。
- 需要多时点改善数据时补 native chart/KPI，不把趋势画进中心圆。

## 形状组合语法

- `numbered side rows + overlapping semantic circles + center arrow`。
- `evidence cards + circular hub + action cards`，连接线只表达可解释映射。
- 中心圆只放 4-8 字核心标签；详细原因、动作和验收放两侧卡。
- 深紫底必须反白字；浅色正文用深紫/近黑，不用低对比灰。

## 快速组合示例

“三项不足对应三项改进，中间强调从被动响应转向主动治理”时选择
`duotone_problem_improve`，将本系列 `series_id` 设为 `violet_improvement`。
选择 `build-series-composite-svg` 物化资源后可继续替换 data；具体执行入口由当前 consumer 决定。
不同数量或无逐项映射时切换非对称布局。

## 容量与失败

- 两侧 2-4 项，每项标题一行、说明两行；中心标签不超过 8 字。
- 失败：问题和行动无映射、中心圆塞长文、环没有反馈关系、为了对称虚构措施。
