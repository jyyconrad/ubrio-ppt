<!--
id: anti-pattern-rainbow-parallel-modules
category: anti-pattern-qa
stage: slide_generation
read_when: 汇报型 PPT 的并列痛点、能力、举措、模块或卡片被画成每个模块一种颜色、四个痛点四种颜色、逐卡换色或彩虹卡片
page_roles: content, summary
content_categories: anti_pattern, quality_gate, visual_theme
supports: svg_drawingml
outputs: recolor_rules, parallel_module_color_checklist
depends_on: contract-visual-token-core.md
relation_specs: requires:contract-visual-token-core
max_use: 只处理并列同级模块的装饰性多色问题；真正正负/风险收益二元对立仍按 visual token 功能色规则处理
-->

# Anti Pattern: Rainbow Parallel Modules

## 失败信号

汇报型 PPT 中，四个并列痛点、能力、举措或其他同级模块被画成“每个模块一种颜色”：红、橙、黄、紫或蓝、绿、紫、橙轮换出现在整张卡片、顶边条、描边、标题和图标上。颜色没有对应正负、风险、状态或数据系列，只是在替代结构分组。

这会把同一层级误读成多个视觉主题，并使整套 deck 从封面到收尾失去一个连续主色系。

## 修复算法

1. 从 foundation `style_manifest.palette` 读取唯一 `accent-color`，不得为当前页重选主色。
2. 所有并列卡片统一使用中性 `surface`、`border` 和同一主色 `accent`；删除逐卡色相差异。
3. 模块差异改用编号、短标题、单色图标、留白、字重或同色系明度层级表达。
4. 只有风险/警示、正负、增长/下降等真实语义允许功能色；功能色只落在状态点、数值、图例或短标签，不覆盖整张卡片、整栏或完整边框。
5. 执行 `validate_svg_drawingml(mode='full')`。仍有 `SLIDE_COLOR_SCHEME_DRIFT` 或 `SLIDE_COLOR_PALETTE_OVERFLOW` 时按 `repair_suggestion` 改色并重验，warning 清零前不调用 renderer。

## 允许例外

两个区域确实表达正负、问题与改进、风险与收益等二元语义对立时，可以使用一个主色加一个功能色；这不是四个并列模块逐卡换色的理由。三个以上同级模块默认回到同一主色系。

## QA

- 缩略图总览是否先读出一个贯穿全册的主色系？
- 同级卡片是否共享同一 `surface`、`accent` 和 `border`？
- 每个额外色相能否说明独立业务语义？说不出就删除。
- 功能色是否只占局部，而没有变成第二块大面积主色？
