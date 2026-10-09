<!--
id: layout/swiss_svg_drawingml
category: layout
module_type: layout_family
skill_kind: method_reference
runtime_scope: mainline
read_when: 当前页要求 Swiss / 瑞士风 / 高密度信息设计 / 强网格视觉，并且可以走 SVG DrawingML route
page_roles: cover, agenda, content, section_divider, summary
stage: slide_generation
supports: svg_drawingml, validate_svg_drawingml, render_svg_drawingml_slide
outputs: swiss_information_grid, svg_layout, layout_contract, validation_gate
depends_on: layout-swiss-core-grid.md, layout-swiss-standard-structures.md, contract-visual-token-core.md
relation_specs: requires:layout-swiss-core-grid, requires:contract-visual-token-core, pairs_with:layout-swiss-standard-structures, pairs_with:layout-swiss-metric-structures
source_notice: 参考 guizang-ppt-skill 的 MIT Swiss 风格资产与版式语义，已迁移为本项目 SVG DrawingML 主线方法；旧 HTML / PPTX 资产不作为运行时路线。
max_use: 只作为 Swiss 信息设计家族入口；具体网格/结构/视觉分别读取拆分颗粒。
-->

# Layout: Swiss SVG DrawingML

普通 Swiss 风格 PPT 默认走 SVG DrawingML 主线：`render_svg_drawingml_slide` + `swiss_svg_*` 结构合同。不要把 Swiss 页面交给旧 HTML 模板或 native PPTX 版式。

## 选择方法

- 先读 `layout-swiss-core-grid.md`，确定安全区、12/16 列网格、标题区、主体区和来源区。
- 标准结构读 `layout-swiss-standard-structures.md`：cover、toc、statement、four_cards、six_cells、three_support、horizontal_timeline。
- 指标/经营结构读 `layout-swiss-metric-structures.md`：vertical_metric_timeline、argument_metric_columns、kpi_ledger、closing_takeaways。
- 文案口吻读 `narrative-swiss-copywriting.md`；视觉 token 读 `contract-visual-token-core.md`。

## 结构路由

- 封面/章节页：`swiss_svg_cover` 或 `swiss_svg_statement`。
- 目录：`swiss_svg_toc`；即使正好 6 项，也不要画成六格定义。
- 6 个并列定义：`swiss_svg_six_cells`。
- lead + 3 支撑：`swiss_svg_three_support`。
- 4 个并列模块：`swiss_svg_four_cards`。
- 3-7 阶段序列：`swiss_svg_timeline`。
- 需要真实柱线饼、表格或图片证据时，Swiss 只负责标题、洞察和 slot 周边结构，真实对象走 native slot。

## 示例

- Cover：`assets/examples/svg-ppt/decks/scenario-government-study/01-cover.svg`
- Agenda：`assets/examples/svg-ppt/decks/scenario-government-study/02-agenda.svg`
- Timeline：`assets/examples/svg-ppt/decks/scenario-project-report/04-timeline.svg`
- Six-cell：`assets/examples/svg-ppt/decks/scenario-government-study/06-mechanism.svg`
- Four-card：`assets/examples/svg-ppt/decks/scenario-government-study/07-branch-actions.svg`

需要查看结构时调用 `load_skill_example(path="...")`，只参考结构和质量，不复制坐标。

## 禁止

不手写页面级 HTML 或截图页；不在 SVG 内画整页背景、页眉、页码、外框或母版装饰；不跳过 `validate_svg_drawingml`。
