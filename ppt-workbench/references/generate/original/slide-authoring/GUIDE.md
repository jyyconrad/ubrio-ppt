---
name: slide-authoring
description: Use in slide_generation when a current Chinese business-reporting slide needs editable SVG DrawingML content and a clear authoring method.
enabled: true
stage: slide_generation
---

# SVG DrawingML Authoring

本 Skill 用于把当前页的业务结论和证据组织成可编辑的 SVG DrawingML 内容。它描述页面方法、结构决策和质量标准，不描述运行时装配或执行时序。

## 输入合同

开始编写前确认：

- 整套 PPT 的主题、受众、场景、沟通目标、整体叙事逻辑和视觉基调。
- 当前页的页码、页面角色、核心观点、当前页承接关系，以及后续页面如何递进。
- 已确认的标题、正文、数据、事实、案例、来源和素材。
- 页面类型、信息密度、内容安全区、可编辑性目标和不能丢失的对象。
- 视觉槽位：`background-color`、`accent-color`、`title_text-color`、`body_text-color`，以及字体、间距和图标风格。

缺少关键结论、必要证据或品牌硬约束时，先标明缺口；不要用装饰掩盖内容不足。

## 页面方法

1. 明确当前页承担什么角色：提出结论、解释原因、展示证据、比较方案、说明进度，还是收口行动与风险。
2. 把标题写成观点句，再用一句话定义页面证明目标。
3. 将内容拆成结论、证据、解释、影响、行动或风险等语义块；删除与证明目标无关的内容。
4. 需要沿用成熟汇报模板时，先选择一个 `template-series-*`：继承的是整册视觉节奏、页型菜单、页面展示系统和形状组合语法，不是只复制主色或三卡/四卡骨架。
5. 为当前页选择一个 composition branch，明确它证明什么；再按关系选择 layout 或复杂 pattern：并列用卡片或矩阵，对比用左右或表格，递进用阶梯或时间线，因果用链路或闭环，指标用数字与图表，行动用责任与节点。
6. 先确定阅读路径和主视觉锚点，再安排局部组件；不要从零散装饰开始。技能图保持两层：`template-series-*` 负责整页外围和跨页视觉合同，组件节点只负责调用方 `region` 内的一类复杂组合形状。需要“左侧折线/柱状主图 + 右侧 2-3 张说明卡”时，选择 `composition-chart-insight-rail.md`，组合一个 `native_chart_panel` 和多张 `insight_text_card`；需要“大分区卡套证据小卡 + 底部流程”时，用 `layout-sectioned-evidence-dashboard.md` 分配区域，再分别生成多张 `chart_insight_card` 和一条 `full_width_rect_step_flow`。
7. 只在图片能够提供证据、场景或必要视觉解释时使用图片；照片、肖像、书封、真实场景、证据截图和复杂纹理由受控位图承载，不手绘 SVG 模仿。已有合适图片绑定发生素材/overlay 错误时保留相同图片 ID 修复或替换。
8. 每页都评估背景是否需要覆盖 deck 默认：有合适图片且不影响阅读时优先考虑图片背景；否则使用纯色、纸纹或低干扰抽象 SVG。deck 默认只作兜底，不强求每页同形态或每页有图。

整套 PPT 的整体编写思路、当前页承接关系和页面准备方案明确后，可用简短业务语言告知用户整套 PPT 将按什么叙事逻辑组织、当前页承担什么角色、后续页面如何递进。只总结业务组织，不解释内部工具、文件路径、检查步骤或执行过程。

## 结构与证据决策

- **结论先行**：标题给判断，首屏信息给关键证据，解释与行动围绕同一结论展开。
- **证据匹配**：数据证明规模和变化，事实与案例证明存在性，机制与政策证明因果或约束；不要让弱证据承担强结论。
- **容量控制**：一个模块只保留一个主旨；优先删除重复说明，再压缩次要文字，仍超载则拆页。
- **可编辑建模**：文本、数字、形状、连接符、图表、表格、独立 SVG 和图片按语义拆分；不要把多个可编辑对象压成一张图。
- **图片保护**：SVG 只画结构、关系、文字、形状和抽象装饰；不得删除合适图片后，用 SVG 仿造照片、人物、书封、实景或证据截图。
- **视觉聚焦**：强调色只服务关键数字、关系或结论；避免每个模块都抢注意力。
- **草稿态文案**：可在组织阶段保留候选表达，但进入最终页面前必须清除待补、占位、示例和未经确认数字。

详细业务写作方法见 `references/chinese-business-ppt-authoring.md`，容量判断见 `references/contract-content-density.md`，视觉槽位见 `references/contract-visual-token-core.md`。

## 金标能力总览

| 能力 | 用途 | 产物 | 详细地址 |
|---|---|---|---|
| 固定封面/目录 | 封面、目录、简介等低变体固定页；使用已确认的标题、条目和视觉槽位 | 稳定槽位和结构约束 | `references/layout-fixed-cover-agenda.md` |
| 金标单页 builder | 将已确认内容装入可复用页面结构 | 可编辑单页骨架 | `references/contract-gold-svg-builder.md` |
| 中国式业务汇报 | 结论、证据、解释、行动闭环 | 高密度业务正文页 | `references/chinese-business-ppt-authoring.md` |
| SVG DrawingML 编写 | 几何结构、连接关系和对象分组 | 可转换 SVG 内容层 | `references/drawingml-svg-authoring.md` |
| SVG 结构模式 | 流程、指标、证据卡、风险行动条 | 组合结构示例 | `references/svg-shape-patterns.md` |
| 模板视觉系列 | 复用整册视觉节奏、页面展示菜单、强调方式和形状语言；当前覆盖汇报模板系列及 ppt1-ppt8 九个系列 | 系列视觉合同 + 页型菜单 + 形状组合语法 | `references/template-series-rd-efficiency-blue.md`、`references/template-series-blue-summary-pyramid.md` 至 `references/template-series-violet-achievements.md` |
| 复杂组合 SVG builder | 用结构化基础数据生成单一内容区复杂组件，包括阶段矩阵、诊断网格、平台架构、门径 scorecard、operating model、跨月日历、主体原生图表、图表侧栏洞察卡和横向矩形流程等；不生成整页 PPT | `series_composite_svg/v1` + 单个 region-local 分组 SVG + 可选 native-data + 稳定 group ID | `references/template-series-composite-builder.md` |
| 项目汇报金标页 | 项目进展、里程碑、问题与行动 | 项目汇报页面方法 | `references/scenario-project-report-gold-pages.md` |
| 年度总结金标页 | 业绩、复盘、增长与计划 | 年度总结页面方法 | `references/scenario-annual-summary-gold-pages.md` |
| SVG 自检 | 文案、可读性、图标和来源检查 | 提交前检查清单 | `references/contract-svg-self-qa.md` |

项目汇报示例位于 `assets/examples/svg-ppt/decks/scenario-project-report-gold-pages/`，模板系列组合组件示例位于
`assets/examples/svg-ppt/decks/template-series-composite-library/`。能力索引位于
`references/_index/capability-tree.json`，选择示例位于 `references/_index/routing-examples.md`；只查看与当前页类型和缺口直接相关的参考。

## 质量与失败条件

完成前检查：

- 标题是否是结论，证据是否真正支撑标题。
- 阅读顺序是否唯一，信息层级是否能在数秒内被看懂。
- 正文、图表、图标和来源是否清晰可读，没有遮挡、越界和无意义留白。
- 同类组件的圆角、边距、字号、色彩和对齐是否一致。
- 系列页面是否保持同一视觉语法，又通过页型切换形成跨页节奏；不能只统一颜色，也不能每页都套同一种基础卡片。
- 复杂组合形状的几何是否来自真实数据关系，group ID、容量错误和 native slot 边界是否保留。
- 嵌套卡片是否形成清晰父子层级；外层只负责分区，内层每卡只保留一个子观点、一个证据介质和一句洞察，不能卡套卡后继续堆长文。
- 是否保留可编辑语义，避免整页或大区域无必要地位图化。
- 图片绑定是否被正确保留，背景是否按本页叙事与密度独立决策，而不是机械沿用或机械铺图。
- 是否完成 `references/contract-svg-self-qa.md` 中的最终态检查。

出现以下任一情况不得视为完成：核心观点不成立；关键证据缺失或来源不明；内容超出容量；必需素材不可用；页面只能靠小字号勉强容纳；对象结构无法表达原意；最终页面仍保留草稿态文案、占位符或待补数字。
