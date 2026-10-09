<!--
id: chart-sankey
category: layout
read_when: 当前页需要桑基/流向/资金流向/预算分流/多对多流转/生态流向图
page_roles: content, relationship
chart_types: sankey
visual_tags: chart, flow
supports: svg_drawingml, native_sankey_slot
outputs: chart_type_decision, native_sankey_slots, sankey_layout_rules
depends_on: layout-native-chart-slot.md, contract-visual-token.md
triggers: 桑基, 桑基图, sankey, 流向, 流向图, 资金流向, 预算流向, 分流, 多对多流转, 生态流向
max_use: 只讲 sankey 分型与 flows 合同；桑基走独立 native-sankey-slot，不是 chart slot
-->

# Chart: Sankey（桑基流向）

## 适用判断

- 可加总的量化对象（资金、用户、物料、能量）在两个以上类别/阶段之间的**分流与汇聚**，连接宽度按流量编码规模，天然支持多对多、分叉后再汇聚。
- 判别信号：数据能拆成 **source-target-value 三元组**且存在真实的多对多流向。
- 退化规则（数据不满足时**不要硬画桑基**）：
  - 只是类别占比、缺明确来源→去向语义 → 退化为占比图/树状图（treemap 语义），用柱状或饼图承载。
  - 单一路径单调收窄（每层只减不分叉）→ 是漏斗，用 `layout-funnel-stage-stack.md`。
  - 单序列递增递减归因 → 是瀑布，用 `chart-waterfall.md`。
  - 严格父子层级、无跨枝汇聚 → 是层级/架构图。
- 单页承载 3~12 条流向路径；超出把长尾节点聚合为「其他」或拆页，避免连线过密难辨读。

## 桑基走独立 slot（不是 chart slot）

桑基无 python-pptx 原生图表对象，走**独立的 native-sankey-slot**，由确定性几何 overlay 渲染（代码算节点分层 + 缎带几何，缎带宽 ∝ value），落成原生可编辑 freeform 缎带 + rect 节点 + 节点标签。

- SVG 声明：`data-role="native-sankey-slot"`（或 `data-native-sankey="true"`），只给 slot 的 `id` 与 `data-x/y/w/h`（1280x720 坐标），不要在 SVG 里手绘缎带或节点。
- 数据写入 `native-data.json` 的 `sankeys[]`，按 `slot_id` 匹配。
- 节点位置、缎带宽度、颜色全部由代码确定性计算，模型只提供 flows 数据。

```json
{
  "version": 1,
  "sankeys": [
    {
      "slot_id": "sankey-slot-1",
      "title": "预算资金流向",
      "flows": [
        {"source": "总预算", "target": "研发", "value": 480},
        {"source": "总预算", "target": "市场", "value": 300},
        {"source": "研发", "target": "平台产品", "value": 300},
        {"source": "研发", "target": "创新实验室", "value": 180},
        {"source": "市场", "target": "品牌投放", "value": 300}
      ],
      "source": "FY25 预算规划"
    }
  ]
}
```

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1280 720"
     data-native-data-ref="slide-generation/page-6/native-data.json">
  <text x="120" y="90" fill="#0F172A" font-size="30" font-weight="700">预算资金流向</text>
  <g id="sankey-slot-1" data-role="native-sankey-slot" data-native-sankey="true"
     data-x="120" data-y="200" data-w="1040" data-h="440">
    <rect x="120" y="200" width="1040" height="440" fill="none" stroke="#CBD5E1"/>
  </g>
</svg>
```

## 几何与视觉

- flows 的 source→target 拓扑决定分层（列）：无入边的源节点在第 0 列，逐层向右推进；节点高 ∝ 吞吐量（进/出取大者），缎带宽 ∝ value。
- 缎带半透明，节点用主强调/分层配色；缺 `flow_value` 无法确定宽度的连接不画。
- 缎带默认直边多边形（MVP）；曲线缎带是 follow-up。节点标签落在节点旁（首列/中列在右、末列在左）。

## 区域容量预算

- slot box 要足够宽（横向承载 2~4 列节点 + 缎带），建议 ≥ 900px 宽、≥ 360px 高（1280x720 坐标）。
- 节点数多、名称长时优先聚合长尾节点，避免标签与缎带互相压叠。

## 反模式

- 不要用 chart slot 的 `kind: "sankey"`——桑基走 `native-sankey-slot`，写 chart slot 的未支持 kind 会被 `NATIVE_CHART_SLOT_UNSUPPORTED_TYPE` 阻断。
- 不要用 SVG 手绘缎带、节点、连接曲线。
- 数据不是真多对多流向时不要硬画桑基（按上面退化规则改图）。
- flow 的 value 缺失或非正数时该连接被丢弃，不要指望它出现。

## 金标示例

- **暂无金标示例（§11.5 待补）**：桑基几何 overlay 为新增能力，尚未经真机内容→渲染→PNG 目检验收，不要伪造金标路径。结构参照本文件 flows 合同；配色参照 `contract-visual-token.md`。
