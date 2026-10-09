<!--
id: scenario-project-report-gold-pages
category: scenario-template
read_when: 需要复现项目汇报截图级两页、弱模型需要可照抄 SVG 骨架
page_roles: content, summary
supports: svg_drawingml
outputs: gold_page_recipe, svg_regions, qa_checklist
depends_on: scenario-project-report.md, contract-svg-page-workflow.md
max_use: 只读取本文件和对应 SVG 示例，不要连带读取全部场景文件
-->

# Scenario: Project Report Gold Pages

## 内容说明

本文件专门服务两页内容充实的项目汇报 PPTX：`04-timeline.svg` 和
`08-issue-log.svg`。弱模型先读本文件，再打开对应 SVG，把真实素材替换进去。

独立两页资产：

- SVG deck：`assets/examples/svg-ppt/decks/scenario-project-report-gold-pages/`
- PPTX：`assets/examples/svg-ppt/pptx/scenario-project-report-gold-pages.pptx`
- 来源页：从完整项目汇报 deck 的第 4 页和第 8 页抽出，便于弱模型只看目标两页。

读取顺序：

1. `drawingml-svg-authoring.md`，确认 SVG 可转换硬合同。
2. `contract-visual-token.md`，写出颜色和字号。
3. `scenario-project-report.md`，确认项目汇报内容槽。
4. 本文件，按两页 recipe 复现。
5. 用 `load_skill_example(path=...)` 只读取 `assets/examples/svg-ppt/decks/scenario-project-report/04-timeline.svg`
   和 `08-issue-log.svg`，不要读取整套 deck。

## 视觉说明

固定视觉 token：

- `background`: `#F4F7FA`
- `surface`: `#FFFFFF`
- `title_text`: `#003D79`, 主标题 `38px`
- `body_text`: `#243447`, 正文 `13-18px`
- `source_text`: `#6B7A90`, 来源文字 `12px`
- `accent`: `#2F80ED`
- `warning`: `#B91C1C`
- `border`: `#D7DEE8`

所有 `<text>`、线条、图形必须显式 `fill` 或 `stroke`。深蓝面板必须白字；浅底正文用
深色字。不要用 `11/14 已关` 这类易被转换器拆行的短数字+中文组合；改成 `78%`
加一句中文说明。
禁止在页面左侧放贯穿整页高度的蓝色竖条；它会形成无意义装饰并挤压视觉重心。
顶部阶段信息只写入 `stage_label` 供框架层页眉使用，SVG 不渲染顶部胶囊、页码或进度。

## SVG说明

第 4 页：验收总览驾驶舱。

- 坐标：标题区 `x=88 y=118..230`；顶部指标 `x=88 y=240 w=300 h=108`
  共 4 个；左结论 `x=88 y=374 w=430 h=328`；中里程碑表
  `x=552 y=374 w=584 h=328`；右趋势图 `x=1170 y=374 w=342 h=328`；
  底部来源条 `y=724..834`。
- 内容槽：4 个指标、4 条领导结论、4 行里程碑、5 根趋势柱、4 个素材来源、1 条倒排判断。
- 必须出现：项目周报台账、联调问题清单、PMO排期表、验收证据包、红色阻塞。

第 8 页：问题-证据-行动闭环表。

- 坐标：顶部指标 `x=88..1232 y=244 h=82`；左表格
  `x=88 y=350 w=970 h=366`；右证据链 `x=1090 y=350 w=422 h=366`；
  底部行动条 `y=736..788`；深蓝合同条 `y=800..834`。
- 表格字段：编号、问题、来源/证据、影响、Owner、时限、状态，至少 6 行。
- 证据链：来源、判断、动作、验收四段，每段写一行解释。
- 行动条：红色阻塞、黄色跟踪、蓝色归档都要有 Owner、短时限、交付物或验收标准。

最小分组名：

```xml
<g id="metrics-panel">...</g>
<g id="leader-claim">...</g>
<g id="milestone-table">...</g>
<g id="trend-chart">...</g>
<g id="issue-table">...</g>
<g id="evidence-chain">...</g>
<g id="action-closure">...</g>
<g id="source-note">...</g>
```

复现失败时这样修：

- 拆行或竖排：把数字中文组合拆成百分比主数值 + 中文说明。
- 表格空：至少补 6 行，每行必须有来源、影响、Owner、状态。
- 卡片空白：补素材来源、证据口径、Owner 或验收标准。
- 深色不可读：深蓝底只用 `#FFFFFF` 或 `#EAF3FF` 文字。
