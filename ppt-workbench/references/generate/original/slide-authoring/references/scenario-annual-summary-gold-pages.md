<!--
id: scenario-annual-summary-gold-pages
category: scenario-template
read_when: 需要复现年度经营总结截图级三页、弱模型需要可照抄 SVG 骨架
page_roles: content, summary
supports: svg_drawingml
outputs: gold_page_recipe, svg_regions, qa_checklist
depends_on: scenario-annual-summary.md, contract-svg-page-workflow.md
max_use: 只读取本文件和对应 SVG 示例，不要连带读取全部场景文件
-->

# Scenario: Annual Summary Gold Pages

## 内容说明

本文件服务三页年度经营总结 PPTX：`04-dashboard.svg`、`08-evidence-table.svg`
和 `09-actions.svg`。弱模型先读本文件，再打开对应 SVG，把真实素材替换进去。

独立三页资产：

- SVG deck：`assets/examples/svg-ppt/decks/scenario-annual-summary-gold-pages/`
- PPTX：`assets/examples/svg-ppt/pptx/scenario-annual-summary-gold-pages.pptx`
- 来源页：从完整年度总结 deck 的第 4、8、9 页抽出，便于弱模型只看目标页。

读取顺序：

1. `drawingml-svg-authoring.md`，确认 SVG 可转换硬合同。
2. `contract-visual-token.md`，写出颜色和字号。
3. `scenario-annual-summary.md`，确认年度总结内容槽。
4. 本文件，按三页 recipe 复现。
5. 用 `load_skill_example(path=...)` 只读取 `assets/examples/svg-ppt/decks/scenario-annual-summary/04-dashboard.svg`、
   `08-evidence-table.svg` 和 `09-actions.svg`，不要读取整套 deck。

## 视觉说明

固定视觉 token：

- `background`: `#F6F8FB`
- `surface`: `#FFFFFF`
- `title_text`: `#0F172A`, 主标题 `38px`
- `body_text`: `#334155`, 正文 `11-18px`
- `source_text`: `#64748B`, 来源文字 `12px`
- `accent`: `#2563EB`
- `warning`: `#B91C1C`
- `border`: `#D9E2EC`

所有 `<text>`、线条、图形必须显式 `fill` 或 `stroke`。浅底正文用深色字，
深蓝面板只用 `#FFFFFF` 或 `#EAF3FF` 文字。顶部阶段信息只写入 `stage_label`
供框架层页眉使用，SVG 不渲染顶部胶囊、页码或进度。禁止在页面左侧放贯穿整页高度的
蓝色竖条、侧边框或外框。

## SVG说明

第 4 页：年度经营驾驶舱。

- 坐标：标题区 `x=88 y=116..228`；顶部指标
  `x=88 y=248 w=328 h=122` 共 4 个；左侧经营判断
  `x=88 y=402 w=438 h=286`；中部趋势图 `x=558 y=402 w=478 h=286`；
  右侧差距转行动 `x=1068 y=402 w=444 h=286`；底部来源条 `y=720..828`。
- 内容槽：4 个指标、4 条经营判断、6 根趋势柱、4 条差距转行动、4 个素材来源。
- 必须出现：年度财务月报、CRM合同清单、PMO项目台账、客户成功台账、复购口径仍待补。

第 8 页：经营证据口径表。

- 坐标：顶部摘要指标 `x=88..1156 y=248 h=74`；左表格
  `x=88 y=352 w=1018 h=354`；右证据链 `x=1140 y=352 w=372 h=354`；
  底部闭环条 `y=730..834`。
- 表格字段：经营结论、证据/口径、解释、缺口、Owner，至少 5 行。
- 证据链：观点、证据、解释、缺口、动作五段，每段写一行说明。
- 底部动作：数据、客户、交付、经营四类缺口都要有补齐动作和责任方。

第 9 页：来年行动复盘台账。

- 坐标：顶部摘要指标 `x=88..1156 y=248 h=74`；左台账
  `x=88 y=350 w=1020 h=360`；右复盘闭环 `x=1140 y=350 w=372 h=360`；
  底部行动合同 `y=734..834`。
- 台账字段：事项、责任人、关键动作、检查标准、节奏，至少 5 行。
- 复盘闭环：输入、判断、行动、验证四段，说明下次复盘如何追踪。

最小分组名：

```xml
<g id="annual-metrics-panel">...</g>
<g id="annual-leader-claim">...</g>
<g id="annual-trend-chart">...</g>
<g id="annual-gap-and-actions">...</g>
<g id="annual-evidence-table">...</g>
<g id="annual-proof-chain">...</g>
<g id="annual-action-ledger">...</g>
<g id="annual-review-loop">...</g>
<g id="annual-action-closure">...</g>
```

复现失败时这样修：

- 拆行或竖排：不要写 `102%`、`+18%` 这种易被转换器拆分的短数字单位；
  改为主数值 `102` 加旁边说明 `达成率`。
- 内容像荣誉清单：补“经营判断、证据口径、缺口、Owner、复盘节奏”。
- 表格空：至少补 5 行，每行必须有来源、解释、缺口和 Owner。
- 行动空泛：把“持续推进/加强协同”改成交付物、检查标准和复盘频率。
- 深色不可读：深蓝底只用白字或浅蓝字。
