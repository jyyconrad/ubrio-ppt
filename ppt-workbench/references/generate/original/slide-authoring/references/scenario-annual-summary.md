<!--
id: scenario-annual-summary
category: scenario-template
read_when: 年终总结、年度复盘、述职、经营总结、KPI、来年计划
page_roles: content, summary
supports: svg_drawingml
outputs: page_outline
depends_on: content-pyramid-claim-evidence-action.md
max_use: 只读取本文件，不要连带读取同类全部文件
-->

# Scenario: Annual Summary

## 内容说明

写结果、差距、原因和来年抓手。避免只写荣誉清单。
年度总结必须服务经营复盘，不是年会演讲稿。正文页至少覆盖：

- 结果：收入、结构、效率、复购、回款或毛利中的 3-5 个指标。
- 差距：写清未达项、口径缺口、责任缺口或机制短板。
- 原因：说明为什么结果成立，不能只写“团队努力、市场向好”。
- 证据：每个经营判断绑定财务月报、CRM 合同清单、PMO 台账、客户成功台账等来源。
- 行动：来年抓手必须有 Owner、时限、交付物、检查标准和复盘节奏。

正文页常用标题：

- “全年总体达成：收入稳步增长，结构持续优化”
- “三类关键动作支撑年度目标达成”
- “短板集中在效率、协同和复购三方面”

## 视觉说明

正式稳健，高密度，数据和行动并重。适合浅底商务蓝或金融银蓝。
视觉主题选定后必须写清：

- `background`: `#F6F8FB`
- `surface`: `#FFFFFF`
- `title_text`: `#0F172A`, 主标题 `38-42px`
- `body_text`: `#334155`, 正文 `12-18px`
- `source_text`: `#64748B`, 来源文字 `12px`
- `accent`: `#2563EB`
- `warning`: `#B91C1C`
- `border`: `#D9E2EC`

所有文字和图形必须显式 `fill` 或 `stroke` 并可见。顶部阶段信息只写入
`stage_label` 供框架层页眉使用，SVG 不渲染顶部胶囊、页码或进度。禁止添加无意义的
整页左侧竖条、侧边框或外框。

## SVG说明

优先布局：`layout-three-cards-action-bar.md`、`layout-left-claim-right-evidence.md`。
内容结构优先：`content-pyramid-claim-evidence-action.md`。

通用 SVG 函数只是基础能力，只保证页面可转换、基础元素可见；形成金标效果的 PPTX
必须来自本场景高级 skill 的经验沉淀：年度经营内容槽、固定坐标区、素材口径、反模式、
转换器避坑和 PNG 复查结论。不要把通用模板当作最终效果。

年度总结推荐页型：

- 封面：先给年度经营判断、贡献来源和风险缺口；不能只有大标题和三张空卡。
- 目录：目录本身要表达经营问题链：结果 -> 诊断 -> 计划 -> 闭环。
- 章节页：章节页要说明本章节回答什么问题，并给证据阅读路径。
- 经营驾驶舱：顶部 4 个指标 + 左侧经营判断 + 中部趋势/结构图 + 右侧差距转行动 + 底部来源条。
- 差距矩阵：按影响/推进难度写差距、来源、Owner 和复盘节奏。
- 原因分析：左侧给机制判断，右侧用行业选择、交付机制、复购运营三条证据解释。
- 证据口径表：经营结论、来源/口径、解释、缺口、Owner 五列，不少于 5 行。
- 行动复盘台账：事项、责任人、关键动作、检查标准、节奏五列，右侧补复盘闭环。
- 来年路线图：Q1-Q4 每季写交付物和验收口径，不用只写“推进、深化、加强”。
- 附录：列出真实素材 metadata 和待补口径，不做泛泛“素材清单”。

完整 deck 质量下限：除封面外，每一页都必须出现年度经营素材来源、证据口径、
Owner/责任部门、缺口或行动闭环中的至少 3 类；不能只有标题、两张卡片或空表格。

更细的逐步复现手册见 `scenario-annual-summary-gold-pages.md`。当目标是复现年度总结
截图级示例时，先读该文件，再打开 gold SVG，不要只读完整 deck。

## SVG-PPT 套装示例

- SVG deck：`assets/examples/svg-ppt/decks/scenario-annual-summary/`
- PPTX：`assets/examples/svg-ppt/pptx/scenario-annual-summary.pptx`
- 截图级 3 页金标示例：`scenario-annual-summary-gold-pages.md`
- 页型：封面、目录、章节页、经营仪表盘、差距矩阵、原因分析、来年路线图、证据表、行动台账、附录。
- 学习点：年度总结套件必须同时覆盖结果、差距、原因、计划和责任闭环。

金标页学习点：

- `04-dashboard.svg`：年度经营驾驶舱，指标不能被 PPTX 转换成竖排；数字和单位要拆开表达。
- `08-evidence-table.svg`：经营结论必须对应来源、解释、缺口和 Owner。
- `09-actions.svg`：行动页必须形成来年复盘台账，禁止只写口号或荣誉总结。
