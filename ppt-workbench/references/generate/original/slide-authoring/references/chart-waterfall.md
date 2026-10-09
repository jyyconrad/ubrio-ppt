<!--
id: chart-waterfall
category: layout
read_when: 当前页需要瀑布/桥接/利润桥/营收桥/现金流构成/归因拆解图表
page_roles: content, summary
chart_types: waterfall
visual_tags: chart
supports: svg_drawingml, native_chart_slot
outputs: chart_type_decision, native_chart_slots, waterfall_layout_rules
depends_on: layout-native-chart-slot.md, contract-visual-token.md
triggers: 瀑布, 瀑布图, 桥接图, 利润桥, 营收桥, 现金流桥, waterfall, bridge, 归因拆解, 增减拆解, 变化归因
max_use: 只讲 waterfall 分型与 segments 合同；slot JSON 位置合同仍以 layout-native-chart-slot.md 为准
-->

# Chart: Waterfall（瀑布/桥接）

## 适用判断

- 单一核心指标（营收、净利润、现金流、用户数）从**期初到期末**的构成路径，用若干正负增减项说明「变化从何而来」，强调归因。
- 判别信号：各增减项之和必须能**精确复原期末值**（离散归因、数值可对账）。只是连续走势、不要求逐项可加总 → 用 `chart-line-trend.md`；只有期初/期末两点、无法归因中间过程 → 用前后对比卡。
- 多节点之间的**分流/汇聚**（多对多流向）不是瀑布，用 `chart-sankey.md`。
- 典型容量 4~8 根柱（1 期初 + 2~6 项增减 + 1 期末）；超出先把小项归并为「其他」或改表格。

## 数据结构（native-data.json）

`kind: "waterfall"`，段写入 `segments[]`（有序，从左到右即柱子顺序）。每段：

- `type`：`total`（期初/期末/子总计，用 `value` 给绝对值；期末可省略 `value`，renderer 用累积值收口）、`increase`（上涨，用带符号 `delta`）、`decrease`（下跌，`delta` 写负数）。
- `label`：柱子标签；也可只在顶层 `labels[]` 按顺序给，段内省略。
- 无 `type` 时按 `delta` 符号推断（正=increase、负=decrease、缺=total），但**推荐显式写 type**避免歧义。

```json
{
  "version": 1,
  "charts": [
    {
      "slot_id": "waterfall-slot-1",
      "kind": "waterfall",
      "title": "2024 营收桥",
      "labels": ["期初收入", "新增订阅", "增值服务", "客户流失", "价格调整", "期末收入"],
      "segments": [
        {"type": "total", "value": 320},
        {"type": "increase", "delta": 95},
        {"type": "increase", "delta": 42},
        {"type": "decrease", "delta": -58},
        {"type": "decrease", "delta": -19},
        {"type": "total"}
      ],
      "source": "财务快报 FY24",
      "insight": "新增订阅是主要拉动，客户流失抵消近三分之一增量。",
      "waterfall": {"increase_color": "#22C55E", "decrease_color": "#EF4444", "total_color": "#64748B"}
    }
  ]
}
```

## 渲染路线与视觉

- renderer 把瀑布落成真·可编辑的原生 **COLUMN_STACKED**：一个隐形垫托序列（累积基座，noFill）+ 一个可见 delta 序列（浮动柱）。浮动柱本身表达瀑布语义，无需手绘。
- 逐柱上色由 `type` 决定：涨绿、跌红、总计中性；默认取高对比 token，可用 `waterfall.increase_color/decrease_color/total_color` 覆盖，颜色仍从 `contract-visual-token.md` 取。
- 涨跌连接线（柱间水平虚线）当前**未实现**（follow-up），MVP 不依赖它；用清晰的柱标签和期末总计柱表达收口即可。
- SVG 侧只声明 slot 位置 + 标题/来源（写在 slot 分组外、box 上下方），组内只留底板 rect 和一行占位说明（渲染时移除）。位置/归属合同同 `layout-native-chart-slot.md`。

## 区域容量预算

- slot box 与柱线饼同档：不小于 320x200（1280x720 坐标），否则柱与标签挤压。
- 柱多（接近 8）时横轴标签易挤，优先精简增减项或缩短标签，不要压小 box。

## 反模式

- 不要用 `kind: "bar"` + 手算堆叠冒充瀑布——现在有原生 `kind: "waterfall"`。
- 不要让增减项之和对不上期末值（瀑布的可信度全在数值对账）。
- 不要把多主体分流硬塞进瀑布（那是桑基）。
- 不要用 SVG 手绘悬浮柱、连接线、坐标轴。

## 金标示例

- **暂无金标示例（§11.5 待补）**：本技法为新增渲染能力，尚未经真机内容→渲染→PNG 目检验收，不要伪造金标路径。结构参照本文件 JSON 合同 + `layout-native-chart-slot.md` 的 slot 归属契约；配色参照 `contract-visual-token.md`。
