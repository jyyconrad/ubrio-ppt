<!--
id: content-comparison
category: content-structure
read_when: 前后对比、竞品对比、预期实际对比、差距分析
page_roles: content
supports: svg_drawingml
outputs: content_slots
depends_on: contract-content-density.md
relation_specs: requires:contract-gold-svg-builder, requires:structure-hierarchy
max_use: 只读取本文件，不要连带读取同类全部文件
-->

# Content: Comparison

## 内容说明

对比必须写基准、差异、原因和动作。

模板：

```text
基准：[过去/竞品/目标] 是 [状态]。
当前：[现在/我方/实际] 是 [状态]。
差异：[指标/体验/效率] 提升/下降 [数值或描述]。
原因：[原因 1/2]。
动作：[下一步修正或放大]。
```

## 视觉说明

左右或上下对比，差异标签突出。红绿只少量使用，避免全页变成警告页。
对比矩阵、竞品对比表和“痛点对比矩阵”属于高密度正文结构，主体区域应使用页面下半部：
表格/矩阵主体高度通常不低于 520px，底边通常达到 `y≈740-800`；不要把行区压到上半屏，
也不要靠底部 source-note 制造“已经用满”的错觉。

## SVG说明

分组：`before-panel`、`after-panel`、`gap-label`、`fix-action`。
若是多列多行对比表，使用 `comparison-matrix` / `table-region` / `insight-bar`
等语义分组，并让 `table-region` 或底部 insight/action 条延展到 `y≈760` 附近。

## N×M 表格矩阵合同（comparison_subjects≥3）

`table_insight` 一旦对比对象达到 3 个及以上（如竞品功能价格对比、方案评估矩阵、尽调清单核对表），
不能再用左右两栏承载——两栏结构上只能表达 2 个对象，装不下第 3 个。此时按本节收口：

- **渲染路线固定为 native-table-slot，不手绘表格**：真实表头/单元格数据写入当前页 `tables[]`
  JSON（`slot_id`/`columns`/`rows`），SVG 只声明 slot 位置与占位说明；技法与归属契约、JSON 结构、
  金标示例见 `layout-native-chart-slot.md`（`chart_types` 白名单已含 table，为非阻塞能力）。
  不要用 `rect + line + text` 手绘表格线或用 `✓/✕/~` 符号伪装单元格状态。
- **容量**：6 行以内（含表头行不计），单元格文本 ≤40 字，右侧或下方洞察面板 ≤60 字；超出应拆页
  或精简列数，不要压缩字号硬塞。列数建议 ≤5，列名 ≤15 字。
- **归属**：真实标题在 slot 分组外、box 上方；洞察结论、来源标注同样在 box 外，不写进 `tables[]`
  之外的手绘文字里，也不要摆在 slot box 覆盖范围内。
- **金标示例**：`assets/examples/svg-ppt/decks/scenario-annual-summary/08-evidence-table.svg`、
  `assets/examples/svg-ppt/decks/scenario-government-study/08-policy-table.svg`、
  `assets/examples/svg-ppt/decks/scenario-financing-roadshow/08-financial-table.svg`、
  `assets/examples/svg-ppt/decks/scenario-government-briefing-gold-pages/03-evidence-table-dark-panel.svg`
  ——四份均示范 `comparison-matrix`/`table-region` 分组与 native-table-slot 的组合用法，只参考结构
  与数据拆分方式，不要照抄坐标或把示例数据当业务事实。
- 对象恰为 2 个时仍优先左右两栏（`before-panel`/`after-panel` 或 `pros_cons`），不要为了用表格
  牺牲两栏对比更直观的差异呈现。
