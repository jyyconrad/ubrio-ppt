# 原生图表与表格槽

正文页图表/表格的活动配方是 SVG 几何 + `native-data.json` + DrawingML render 里的 `overlay_native_slots.py`。Ubrio `save_file` / `validate_svg_drawingml` / `render_svg_drawingml_slide` 在本技能就是：写本地 sidecar、`scripts/svg/validate_svg_drawingml.py` 预检、`scripts/svg/render_svg_drawingml.py` 转 PPTX 再 overlay。`scripts/native.cjs` 只在 SVG→PPTX 不可用时 fallback，且仅 `bar`/`line`/`table`。图片三个 owner 见 [图片三个 owner](image-owners.md)；本页不重复。

## 快速生成雷达折线柱状图

只需要一个原生图表资产时，用统一入口；无需手写SVG槽或布局坐标：

```bash
python3 scripts/svg/build_native_chart.py --describe
python3 scripts/svg/build_native_chart.py \
  --kind line --content chart-data.json --output-dir chart
```

`--kind`为`radar`、`line`或`bar`。公开字段与容量以`--describe`为准：共同输入为标题、分类`labels`、`series[{name,values}]`、单位`unit`、期间`period`、来源`source`、限制`limitation`；可给`number_format`。雷达必填`scale{minimum,maximum}`且所有维度同量尺；折线和柱状图可填`target{value,label}`，生成原生虚线目标系列。名称原样用于图例，邻近字幕只显示一次格式化参考值和单位。业务调用不填写颜色、字号或坐标。空值、非有限数、长度不符、雷达越界和超容量文字会明确失败，不能补零、改值或缩字。

下例仅为授权合成演示；实际任务替换为用户提供的数据：

```json
{
  "title": "准时率逐期改善，仍需达到目标",
  "labels": ["7月", "8月", "9月"],
  "series": [{"name": "实际", "values": [0.91, 0.94, 0.96]}],
  "unit": "%",
  "period": "2026年7—9月",
  "source": "授权合成履约台账",
  "limitation": "示例数据，不代表真实经营结果",
  "number_format": "0.0%",
  "target": {"value": 0.98, "label": "准时率目标"}
}
```

百分数格式乘以100，`0.96`配`0.0%`才显示96%；原始`96`应配`0"%"`或把单位留在标题说明中。默认`0.##`保留小数，不把原始数当百分比。柱状图覆盖负值并保留零基线；雷达关闭密集逐点标签，精确值保存在原生工作簿。

一次调用产出`page.pptx`、`native-data.json`、`source.svg`、规范化数据和`native-chart-report.json`。复制PPTX中的原生chart可继续编辑数据；组合汇报页可复用sidecar中该chart的业务数据，槽的位置由页面布局统一安排。报告中的`structurally_verified`只说明实际对象检查通过；随后渲染并读取预览，核对图例、分类、单位、目标线及拥挤情况。没有操作PowerPoint打开/编辑/保存时，往返状态保持`not_performed`。图表资产不代替完整汇报页的主观点、证据、行动或整册合同。

## 表格语义先于视觉模拟

左右对照是两块 `comparison-panel`，各写一句，不是表格。有列标题、至少三行同类数据，且读者要复制或排序时，才用 `native-table-slot` + `tables[]`。判断对判断、图标加一句话，留在面板里。SVG 只保留标题、注释、状态标记和槽位外框，不得绘制单元格网格、行列数据或用 `rect`/`text` 组成假的表格。

生成后要在最终 PPTX 中检查真实表格对象、列语义、单位、行高和来源。原生链路不可用时才使用 named fallback，并在任务目录记录原因和可编辑性影响；结构检查通过不能替代表格语义检查。

## 活动步骤

1. 写 `native-data.json`（Ubrio `save_file`）。`charts[]` 允许 `bar`/`line`/`pie`/`waterfall`/`radar`（`trend`/`timeseries` 当 line）。雷达只用于相同量纲和量尺的多维评价，给完整维度、系列、量尺和来源，不把不同单位的数据拼成雷达。`tables[]` 写列和行，`column_widths`可给正数比例；`column_styles`可按列覆盖底色、字色和粗体，例如让类型首列保持深蓝白字，仍是原生表格。桑基走 `sankeys[]`，never charts[].kind=sankey，也不写 combo/bubble。
2. 写 `source.svg`（`viewBox="0 0 1280 720"`，根节点 `data-native-data-ref`）。slot 组只留外框 rect：`data-role="native-chart-slot"` / `native-table-slot` / `native-sankey-slot`，带 `data-x/y/w/h`。不要手绘坐标轴、图例、柱线饼、单元格或缎带。
3. 标题在 box 上方 28–40px（基线距顶 ≥12px），来源/洞察在下方 ≥36px，都在 slot 组外。主图 min 320×200；KPI 微图 `data-native-chart-variant="micro"` 时 min 140×80。表格的`row_heights`可给各行高度比例（含表头），避免窄字段表头占用正文容量；列样式的`margin_left_pt`等内边距可为独立图标留位。微折线可用`options.axes: false`隐藏坐标轴，并用`data_labels: true`及`data_label_position: below`保留逐点数值。百分数格式会乘以100，输入0.67才显示67%；原始输入67时用`0"%"`这样的文字后缀，不得显示6700%。
4. 预检（Ubrio `validate_svg_drawingml`）：

```bash
python3 scripts/svg/validate_svg_drawingml.py --svg source.svg --mode full
python3 scripts/svg/overlay_native_slots.py \
  --svg source.svg --native-data native-data.json --validate-only
```

5. 装配（Ubrio `render_svg_drawingml_slide`）：`render_svg_drawingml.py` 先转 DrawingML 再 overlay。也可对已转换 PPTX 单独 overlay。

```bash
python3 scripts/svg/render_svg_drawingml.py \
  --svg source.svg --native-data native-data.json --output page.pptx
python3 scripts/svg/overlay_native_slots.py \
  --svg source.svg --native-data native-data.json \
  --pptx converted.pptx --output page.pptx
```

样例：`references/generate/original/slide-authoring/assets/examples/svg-ppt/decks/scenario-chart-type-gold-pages/*.native-data.json`（01 bar、02 line、03 pie、04 用 bar+line，不是 kind=combo）。槽契约见 [原生图表槽](../original/slide-authoring/references/layout-native-chart-slot.md)；瀑布 `segments[]` 见 [瀑布图](../original/slide-authoring/references/chart-waterfall.md)；桑基 `sankeys[]` + 几何 overlay 见 [桑基图](../original/slide-authoring/references/chart-sankey.md)。

## 类型

原生柱/线可在`options`声明`target`与`reference_line: true`，生成共享坐标轴的可编辑虚线目标；柱图的`target_category`还可附加一个明确标注的目标柱。目标与实际分别保存在工作簿中，不能把目标写成实绩。仍使用`kind: bar`或`line`，不创建未经支持的`kind: combo`。参考线不显示重复数值标签，不改变实际系列量尺。

密集微图可声明`options.data_label_wrap: false`，保持数字和单位同一行，仍须读取最终预览核对宿主实际显示；不修改数值或靠缩字修补。雷达可用`radar_fill_series_index`仅填充指定系列、`radar_fill_transparency`控制透明度，同时关闭`data_labels`以保留干净的轮廓和图例；数值仍保存在原生工作簿。

固定WBR组件的行内趋势使用`options.sparkline: true`：仅接受一个原生line系列、2至12个分类，隐藏轴/网格/图例，保留真实点值与工作簿；固定槽至少140×48px，点标签9pt并保持单行。普通micro槽仍至少140×80px。需要多系列、轴或目标线时使用普通图表。受信任组件调用同一引擎，业务输入无需提供这些设计选项；真实嵌入预览仍须确认各点能读。

原生表可以给`show_header: false`保留连续body行，首行使用body样式；`columns`仍用于字段映射，`row_heights`此时只对应body行。用于参考页中已有外部栏头的根因/机制表，避免叠加第二条表头。

固定参考样式可声明`options.dashed_series_indices`，用从0开始的实际系列序号区分虚线对照组；序号必须存在，目标系列的虚线仍由目标线选项维护。客户体验三系列雷达固定第三系列为虚线，系列名称和数值来自输入。

带外置维度解释的固定雷达可声明`options.category_labels: false`隐藏重复分类文字、`value_axis.labels: false`隐藏刻度文字；轴、网格、量尺、原生分类和值仍保留。`legend: false`用于已有固定外置图例的组件。外置文字与原生标签只能出现一次，说明槽仍须读最终预览核对。

| 数据 | slot | overlay |
| --- | --- | --- |
| 类别对比 / 排名 | `native-chart-slot` + `charts[].kind=bar` | python-pptx 柱图 |
| 时间趋势 | `kind=line` | 折线 |
| 同量尺多维评价 | `kind=radar` | 原生雷达，维度与系列保存在可编辑工作簿 |
| 构成占比 | `kind=pie` | 饼图 |
| 期初→期末归因 | `kind=waterfall` + `segments[]` | 堆叠浮动柱 |
| 明细/矩阵 | `native-table-slot` + `tables[]` | 原生表格 |
| 多对多流向 | `native-sankey-slot` + `sankeys[]` | 几何缎带；失败则 JSON `sankey_fallback`，不写 kind=sankey |

## Fallback 成对样例

仅当 overlay 不可用时用 [native.cjs](../../../scripts/native.cjs) 的 `bar`/`line`/`table`。输入见 [cases.json](../../../assets/examples/cases.json)。

| 方向 | 输入 case | 配对 PPTX | 必要规则 | 可选原始方法 |
| --- | --- | --- | --- | --- |
| `text` / `rect` / 页面骨架 | `10-cover` | [10-cover.pptx](../../../assets/examples/output/10-cover.pptx) | 标题层级、来源和对象边界 | [固定页](../original/slide-authoring/references/layout-fixed-cover-agenda.md) |
| `kpis` | `01-kpi` | [01-kpi.pptx](../../../assets/examples/output/01-kpi.pptx) | 指标口径、单位、空值不补零 | [KPI 条](../original/slide-authoring/references/layout-kpi-strip.md) |
| `chart(line)` | `02-trend` | [02-trend.pptx](../../../assets/examples/output/02-trend.pptx) | 类别和数值完整、原因不臆测 | [折线趋势](../original/slide-authoring/references/chart-line-trend.md) |
| `chart(bar)` | `03-target` | [03-target.pptx](../../../assets/examples/output/03-target.pptx) | 目标/实际口径一致、零基线 | [柱状比较](../original/slide-authoring/references/chart-bar-comparison.md) |
| 多序列 `chart(line)` | `04-multiseries` | [04-multiseries.pptx](../../../assets/examples/output/04-multiseries.pptx) | 图例、序列和坐标轴一致 | [图表可见性](../original/slide-authoring/references/contract-chart-visibility.md) |
| `table` | `05-table` | [05-table.pptx](../../../assets/examples/output/05-table.pptx) | 列语义、单位、状态与行高 | [证据仪表盘](../original/slide-authoring/references/layout-sectioned-evidence-dashboard.md) |
| `flow` 顺序流程 | `06-process` | [06-process.pptx](../../../assets/examples/output/06-process.pptx) | 节点顺序和验收条件明确 | [过程流](../original/slide-authoring/references/layout-process-flow.md) |
| `matrix` | `07-matrix` | [07-matrix.pptx](../../../assets/examples/output/07-matrix.pptx) | 两轴含义明确，不伪造量化 | [四象限](../original/slide-authoring/references/layout-matrix-quadrant.md) |
| `flow` 责任链 | `08-structure` | [08-structure.pptx](../../../assets/examples/output/08-structure.pptx) | 仅承诺顺序/责任链，不冒充复杂网络 | [结构层级](../original/slide-authoring/references/contract-structure-hierarchy.md) |
| `image` + 原生说明 | `09-evidence` | [09-evidence.pptx](../../../assets/examples/output/09-evidence.pptx) | 不对齐 SVG 的正文图走 `native.cjs` `image()`；SVG 对齐截图走 `native-image-slot` | [图片三个 owner](image-owners.md) |
| 密集中文 `table` | `11-dense` | [11-dense.pptx](../../../assets/examples/output/11-dense.pptx) | 不靠超小字号塞入；保留待核实项 | [内容密度](../original/slide-authoring/references/contract-content-density.md) |
| 主题参数 + `chart(bar)` | `12-style` | [12-style.pptx](../../../assets/examples/output/12-style.pptx) | 只迁移颜色，不混入参考事实 | [主题结构分离](../original/layout-intelligence/references/theme-structure-separation.md) |

这些输出证明固定合成输入能够生成 PPTX，并可接受包内对象检查。它们不是模型对开放材料的质量评测，也不替代 pie/waterfall/sankey 的 overlay 路径。原生生成和对象检查无需 LibreOffice。
