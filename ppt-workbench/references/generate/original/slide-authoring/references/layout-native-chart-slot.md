<!--
id: layout-native-chart-slot
category: layout
read_when: 需要柱线饼/趋势/瀑布等 PowerPoint 原生图表，或逐单元格可编辑表格
page_roles: content, summary
supports: svg_drawingml
chart_types: bar, line, pie, waterfall, table
outputs: svg_layout, native_chart_slots, native_table_slots, native_data_json
depends_on: drawingml-svg-authoring.md
max_use: 只读取本文件，不要连带读取同类全部文件
-->

# Layout: Native Chart / Table Slot

## 核心契约

SVG 只负责页面结构和 slot 位置；真实图表/表格数据写入当前页独立 JSON 文件，例如
`slide-generation/page-6/native-data.json`，SVG 根节点或 slot 写 `data-native-data-ref` 指向它。
renderer 按 slot 的 `id` 与 JSON 中的 `slot_id` 自动匹配位置和数据，叠加为 PowerPoint 原生 chart/table。

- 多个图表/表格写在同一个 JSON，使用 `charts[]`、`tables[]` 分组；`data-x/y/w/h` 或
  `x/y/width/height` 使用 1280x720 坐标，JSON 不必重复位置。
- slot box 必须完整落在画布内，越界会被 `NATIVE_SLOT_BOX_OUT_OF_CANVAS` 阻断渲染。
- 只有逐单元格可编辑表格和柱线饼/趋势等真实数据图表走本分支；少量标签/流程框仍用 SVG shape。

## 归属契约：谁展示什么

slot box 是原生内容的独占区域，渲染时原生 chart/table 会在 box 原位叠加：

- slot 分组内只放底板/外框形状（保留，作为图表底板）和至多一两行占位说明；组内 `<text>` 渲染时被自动移除，不进入最终 PPTX。
- 真实标题、结论、洞察、来源永远写在 slot 分组之外：标题在 box 上方独立一行，来源/洞察在 box 下方或侧栏卡；写进组内等于丢内容。
- 原生图表默认不显示自带标题（渲染层已显式删除 Office 自动标题），也不带图表区底色（透明，底板由 slot 外框 rect 与页面背景承担）；确需图表内标题时在 JSON `options` 写 `"show_title": true` 显式声明。
- 剥离后仍有文字锚点落在 slot box 内会收到 `NATIVE_SLOT_TEXT_OVERLAP` 告警：该文字会被原生内容盖住，必须移出 box。

## 区域容量预算

按「标题行 + 图表 box + 注脚行」做纵向预算，避免图表与相邻内容挤占：

- 标题行：box 上方预留 28-40px（18px 字号 + 呼吸空间），标题基线与 box 顶边间距 ≥12px。
- 图表 box：柱/线图不小于 320x200（过小触发 `NATIVE_CHART_SLOT_TOO_SMALL`，坐标轴与图例挤压不可读）；两条以上系列默认显示图例，box 高度再加约 15%；饼图宽高比取 1:1 到 1.3:1。
- 注脚行：来源/洞察在 box 下方预留 ≥36px；box 与相邻卡片间距 ≥24px。
- 类目多、类目名长时优先精简类目或改横向条形，不要靠压小 box 硬塞。

## JSON 结构

推荐先写 JSON，再写 SVG slot。`slot_id` 绑定 SVG，`kind` 表示图表类型（bar/line/pie/trend），
`labels` 是横轴/分类，`series` 是数据序列，`style/options` 放视觉和通用配置。
深色或单一色系主题下必须显式写图表文字和网格线样式，避免 Office 默认黑字落在深底图表上。

```json
{
  "version": 1,
  "charts": [
    {
      "slot_id": "bar-slot-1",
      "kind": "bar",
      "title": "渠道转化对比",
      "labels": ["公域投放", "私域触达", "老客转介"],
      "series": [
        {"name": "转化率", "values": [18, 31, 42], "color": "#3B82F6"},
        {"name": "成交率", "values": [9, 22, 30], "color": "#22C55E"}
      ],
      "source": "CRM 线索转化统计",
      "insight": "私域和老客转介贡献更高。",
      "style": {
        "title_text_color": "#F8FAFC",
        "axis_text_color": "#D8E7FF",
        "legend_text_color": "#D8E7FF",
        "grid_color": "#8FA8CC"
      },
      "options": {"value_axis": {"format": "0%"}}
    }
  ],
  "tables": [
    {
      "slot_id": "table-slot-1",
      "title": "方案对比矩阵",
      "columns": ["维度", "方案A", "方案B"],
      "rows": [["开放性", "优势", "短板"], ["成本", "中等", "优势"]],
      "style": {
        "header_fill": "#1E3A5F",
        "body_fill": "#0F1D2F",
        "text_color": "#D8E7FF",
        "header_text_color": "#F8FAFC",
        "font_size": 9
      },
      "options": {"fit": "shrink"}
    }
  ]
}
```

## SVG Slot 写法

真实标题在 slot 分组外、box 上方；组内只留底板和占位说明（渲染时移除）：

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1280 720"
     data-native-data-ref="slide-generation/page-6/native-data.json">
  <text x="680" y="252" fill="#0F172A" font-family="Microsoft YaHei, Arial"
        font-size="18" font-weight="700">渠道转化对比</text>
  <g id="bar-slot-1" data-role="native-chart-slot" data-native-chart="true"
     data-x="680" data-y="268" data-w="520" data-h="300">
    <rect x="680" y="268" width="520" height="300" fill="none" stroke="#1E3A5F"/>
    <text x="700" y="300" fill="#94A3B8" font-size="13">占位说明：此区域渲染为原生柱状图，本行文字会被自动移除。</text>
  </g>
  <text x="680" y="600" fill="#64748B" font-size="13">来源：CRM 线索转化统计</text>
  <rect id="table-slot-1" data-role="native-table-slot" data-native-table="true"
        data-x="110" data-y="560" data-w="520" data-h="130" fill="none" stroke="#1E3A5F"/>
</svg>
```

## 类型选择

- 表格：指标对比、评估矩阵、清单、责任台账、方案多列对比，写入 `tables[]`。
- 饼图：结构占比、份额拆分、渠道构成，`kind="pie"`；通常只用一个 series。
- 柱状图：类别对比、阶段对比、排名，`kind="bar"`。
- 折线/趋势图：连续时间序列、月度/季度走势用 `kind="line"`；多指标时间趋势、增长曲线用 `kind="trend"`（renderer 按原生 line chart 处理）。
- 瀑布图：单一核心指标从期初到期末的归因拆解（营收桥、利润桥、现金流），`kind="waterfall"`，段写入 `segments[]`（详见 `chart-waterfall.md`）；renderer 落成真·可编辑 COLUMN_STACKED 浮动柱。
- 桑基流向图**不走本文件的 chart slot**：它无 python-pptx 原生图表对象，改用独立的 `data-role="native-sankey-slot"`（`data-native-sankey="true"`），flows 写入 `native-data.json` 的 `sankeys[]`，由确定性几何 overlay 渲染（详见 `chart-sankey.md`）。
- 其他通用配置写进 `options`（legend、axis、number_format、stacked、unit 等）；renderer 不保证全部原生支持，未支持项保留给脚本层扩展。写未支持的 `kind`（如 bubble/radar/gauge）会被 `NATIVE_CHART_SLOT_UNSUPPORTED_TYPE` 阻断，不再静默渲成柱状图。
- 图表 `style.title_text_color`、`axis_text_color`、`legend_text_color`、`grid_color` 必须来自 `contract-visual-token.md` 的高对比 token；单一色系时 series 可用主强调色，但标题/坐标轴/图例不用深紫或黑色，对比系列用 `contrast_accent` / `risk_accent`。

## 禁止

- 不要把完整数据 JSON 塞进 SVG 属性；SVG 属性只放 slot id、位置和 `data-native-data-ref`。
- 不要用 SVG 手绘坐标轴、图例、柱线饼、数据标签，也不要用多个 `rect + line + text` 手绘整张表。
- 不要用 `✓/✕/~` 文本符号在 SVG 里伪装状态表；写入 table JSON，后续由代码层样式化。
- 不要只写 `<rect data-role="native-chart-slot" data-x/y/w/h>` 而不写 JSON；缺数据会被 renderer 阻断。
- 不要把真实标题、结论、洞察、来源写进 slot 分组内部，也不要摆在 slot box 覆盖范围内——组内文字渲染时被移除，box 内文字会被原生内容盖住。
- 不要依赖原生图表自带标题承载页面信息；确需图表内标题用 `options.show_title=true` 显式声明。

## 金标示例

- 示例路径：`assets/examples/svg-ppt/decks/scenario-government-briefing-gold-pages/03-evidence-table-dark-panel.svg`
- 需要查看结构时调用：`load_skill_example(path="assets/examples/svg-ppt/decks/scenario-government-briefing-gold-pages/03-evidence-table-dark-panel.svg")`
- 表格槽示例：手绘报价表改写为 `data-role="native-table-slot" data-native-table="true"` 的 slot，逐单元格数据写入 `tables[]`（真实表头由 `tables[].columns` 生成）；不要在 SVG 里手绘表格线或用符号伪装单元格。右侧深色账单大屏是静态证据承载，与表格槽并列。
- 注意：该示例的组内标题/洞察写法早于归属契约，只参考它的 slot 结构和数据拆分；文字位置一律以本文件「归属契约」为准。图表侧标题位置参照 `scenario-chart-type-gold-pages` 四页（标题均在 box 上方分组外）。
- 勿照抄示例首行 `<rect x="0" y="0" width="1280" height="720">`：它只是离线预览底色。运行时整页背景由 `deck_framework.background` 承载，提交 `render_svg_drawingml_slide` 的 SVG 不画满页背景矩形，否则触发 `SVG_FULL_PAGE_BACKGROUND_FORBIDDEN`（同 `drawingml-svg-authoring-core.md`）。
