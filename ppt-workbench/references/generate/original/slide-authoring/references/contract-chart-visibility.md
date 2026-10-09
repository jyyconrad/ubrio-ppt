<!--
id: contract-chart-visibility
category: execution-contract
read_when: 页面含 native chart/table，或图表文字、坐标轴、图例、表格文字看不清
page_roles: content, summary
supports: svg_drawingml, native_chart_slots, native_table_slots
outputs: chart_visibility_checklist, table_visibility_checklist
depends_on: contract-visual-token-core.md, layout-native-chart-slot.md
chart_types: bar, line, pie, combo, table
relation_specs: requires:contract-visual-token-core, pairs_with:layout-native-chart-slot
max_use: 只讲图表/表格可见性，不讲图表类型选择
-->

# Chart And Table Visibility

原生 chart/table slot 必须继承当前视觉 token。`native-data.json` 中的 `series.color` / `colors` 只决定数据系列颜色，不等于图表标题、坐标轴、图例、数据标签或表格文字颜色。

## 图表

- 深色页：图表标题、坐标轴、图例和数据标签使用 `title_text` 或 `body_text` 的浅色值；网格线/坐标轴线用 `border` 的低透明变体。
- 浅色页：图表文字使用深色 `title_text` / `body_text`，网格线用浅中性 `border`。
- 两条以上系列不得只靠同一主色的深浅差；至少一个系列使用 `contrast_accent` 或 `risk_accent`。
- 饼/环图必须让标签文字和引导线独立可见，不把浅色标签放在浅色扇区或浅底上。
- 组合图若用纯 SVG 或多个 native slot 拼装，分别校验每个 slot 的文字和系列色。

## 表格

`style.text_color`、`style.header_text_color`、`style.header_fill`、`style.body_fill` 必须与背景形成清晰层级。禁止深底黑字、浅底浅字、默认 Office 黑色标题或图例残留在深底图表上。

## 检查

生成前列出：图表标题色、坐标轴色、图例色、数据标签色、网格线色、表头填充/文字、正文单元格填充/文字。任何一项无法解释来源 token，就先补 token 再渲染。
