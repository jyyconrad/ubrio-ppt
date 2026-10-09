<!--
id: template-series-violet-performance
category: template-series
read_when: 需要复用 ppt7 的紫色年度关键指标、North-star KPI 和目标达成对比系列时
page_roles: content, summary
supports: svg_drawingml
outputs: series_visual_contract, page_archetype_menu, shape_composition_grammar, composite_resource_plan
depends_on: template-series-composite-builder.md, layout-kpi-strip.md
relation_specs: requires:template-series-composite-builder, pairs_with:composition-metric-system-with-case, pairs_with:layout-versus-duel, pairs_with:content-pyramid-claim-evidence-action
max_use: 屋顶造型仅为系列受控变体；真实目标与达成数据必须同口径
source_notice: 来源为 ppt7.jpg visual-only 营销拼页；不能把特定屋顶、紫色值或目标数字晋级为全局模板。
-->

# ppt7 系列：紫色 North-star 与业绩达成

## 系列视觉逻辑

- North-star 判断位于页面上部中心，以屋顶/山峰几何建立目标层级；左右证据保持次级。
- 三段管理语义条把目标翻译为战略规划、目标分解和执行监控。
- 下方 KPI 卡使用深紫实底和折角，巨数高于指标名，底部结论带完成管理收口。
- 目标 vs 达成页使用左右镜像和中央 VS，数字必须同单位、同周期、同范围。

## 页面展示系统

- North-star + 3 个管理原则 + 3-5 个关键指标 + 一句结论。
- 目标 vs 达成对决 + 左右亮点/问题分析 + 总结。
- 如果只是同一主体的亮点与不足，使用镜像对比而非竞争型 VS。
- 连续趋势、构成和精确差距使用 native chart。

## 形状组合语法

- `roof/north-star + three-part management rail + dog-ear KPI strip + conclusion band`。
- `mirror arrow panels + central VS badge + two analysis columns`。
- KPI 卡一个卡只放一个主指标；折角只作为方向细节，不承担新语义。
- 屋顶内部只放目标和一句说明，不能作为长段落容器。

## 快速组合示例

“年度关键目标放顶部，下面三条管理机制，再展示五项 KPI”时使用
`north_star_kpi_roof`，填写 `north_star`、`principles[3]`、`metrics[3..5]` 和 `conclusion`。
选择 `build-series-composite-svg` 物化资源，独立预检可选
`validate-series-composite-svg-spec`；后续只替换 data，具体执行入口由当前 consumer 决定。

## 容量与失败

- North-star 1 个、管理原则恰 3、KPI 3-5、结论一句。
- 失败：屋顶长文、KPI 没有单位/口径、目标冒充达成、左右 VS 数据不可比较。
