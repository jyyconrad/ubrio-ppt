<!--
id: gold-page-patterns
category: scenario-template
read_when: 需要把示例里的金标经验迁移到当前页，而不是直接照抄示例资产
page_roles: content, summary
supports: svg_drawingml
outputs: gold_layout_patterns, density_slots, visual_rules
depends_on: contract-gold-svg-builder.md
max_use: 只读取本文件，不要连带读取全部 scenario 示例
-->

# Gold Page Patterns

## 内容说明

从项目汇报和年度总结金标页抽出的共性：

1. SVG 内容层从主标题和核心判断开始；阶段信息、页码和进度导航只写入元数据，
   由框架层贴顶弱化渲染。
2. 标题下方给一句 `key_message`，必须是结论句，不是名词口号。
3. 主体至少有 3 类结构：`claim/evidence/explanation/action_or_risk`。
4. 表格不是装饰：每行必须有来源、影响、Owner、状态或检查标准。
5. 底部必须有来源、口径、行动合同或风险闭环，不能只放页码。

## 视觉说明

通用金标视觉：

- 浅底页：`background #F4F7FA/#F6F8FB`，正文深色，卡片白底。
- 深色面板：只能使用白字或浅蓝字。
- 主标题 `38-42px`，关键结论 `17-19px`，正文 `12-16px`，来源文字 `12px`。
- 不要左侧整页竖条、页面侧边框或整页外框；同样不要把强调色做成单张卡片的整圈粗描边（`stroke-width` ≥2px 包住卡片四边）或卡片左缘/顶缘的装饰色条——这类"卡片描边"是常见误用，层级应靠填充深浅、留白分组和字重字号表达。强调色用于指标、表头、状态标签和短线。
- 卡片内至少三层：标题、判断、证据/动作；空白超过 35% 就补信息。

## SVG说明

金标页在 1280×720 画布上按纵向分带组织，只写比例与安全区，不写死绝对坐标（坐标漂移时靠版式重排，而不是背模板数字）：

- 左右安全边距约 7%W，主体左对齐同一基线，不贴页边。
- 标题带：主标题落在顶部约 0.16H 以内，其下紧跟一句 `key_message` 结论句。
- 指标带：紧随标题带，收在页面前约 1/3 高度内。
- 主体内容带：从指标带下方起，纵向延展至约 0.85H，是页面主承载区（3 类以上结构都落在这里）。
- 来源行：贴底部安全区（约 0.95H 一线），单行弱化，不扩成页脚。

金标页型不是固定模板，必须先看 `structure_hierarchy` 再选择承载方式：

- 驾驶舱：顶部 4 指标 + 左判断 + 中趋势/证据 + 右行动。
- 证据表：顶部摘要 + 左大表 + 右证据链 + 底部闭环。
- 深色证据面板承载示例：`assets/examples/svg-ppt/decks/scenario-government-briefing-gold-pages/03-evidence-table-dark-panel.svg`——右侧账单大屏示范 gold_evidence_table 在深色面板下的构成行/合计承载（左侧报价表走 native-table-slot）。
- 行动台账：顶部摘要 + 左台账 + 右复盘闭环 + 底部行动合同。
- 里程碑：顶部指标 + 横向时间线 + 每阶段验收标准。
- 对比决策：前后对照 + 证据表 + 决策条。
- 能力模型：中心判断 + 能力环绕 + 风险/推进条件。

弱模型执行法：

1. 先写 `structure_hierarchy`，不要直接写 SVG。
2. 从 `gold-structure-composition.md` 选择组合模式。
3. 再选择 `gold_cards/gold_evidence_table/gold_action_ledger/gold_timeline` 或手写 SVG 分区。
4. 填满指标、内容组、表格行、来源。
5. 用 `build_gold_svg_page.py` 生成初稿。
6. 只用 patch JSON 补信息或换文字，不整体重写。
7. 最后检查 `text_node_count`、`shape_count`、文字 fill、主体承载率和模板重复：`text_node_count`/`shape_count` 的具体过线阈值见 `contract-layout-density.md` 的「机器底线」小节（`<text>` ≥12、shape ≥10、字号 ≥11px，warning 级、非固定页触发即人工过目），不要凭感觉判断“够不够密”。
