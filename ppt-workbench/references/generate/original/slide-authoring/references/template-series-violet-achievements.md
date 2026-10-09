<!--
id: template-series-violet-achievements
category: template-series
read_when: 需要复用 ppt8 的紫色工作成果与亮点系列，用连续箭头成果带或四主题中心矩阵展示年度贡献时
page_roles: content, summary
supports: svg_drawingml
outputs: series_visual_contract, page_archetype_menu, shape_composition_grammar, composite_resource_plan
depends_on: template-series-composite-builder.md, layout-arrow-ribbon-metrics.md
relation_specs: requires:template-series-composite-builder, pairs_with:composition-case-impact-chain, pairs_with:layout-quad-cards-core-cluster, pairs_with:layout-kpi-strip
max_use: 成果带用于并列成果而非时间/因果；四主题中心矩阵必须恰四组
source_notice: 来源为 ppt8.jpg visual-only 营销拼页；图标、英文副标题、数字和品牌装饰不晋级。
-->

# ppt8 系列：紫色成果方向带与亮点矩阵

## 系列视觉逻辑

- 深紫连续方向带建立“成果集合”的整体势能，每段下挂说明和单指标证明。
- 亮点页使用四角证据卡与中央 2×2 圆簇，中心只保留四个关键词，详细事实在外侧。
- 白底和浅紫指标面降低六段高密结构的压迫感；深紫只压成果标题、核心词和数字。
- 并列成果与四主题亮点是两个页面角色，不能叠在同一页。

## 页面展示系统

- 3-6 段成果箭头带：成果名、关键动作、结果说明、一个主指标。
- 四主题亮点矩阵：四角卡分别写具体工作和取得成果，中央四圆概括主题。
- 需要按时间回顾时改时间线；需要真实因果时改流程；成果箭头本身只表达阅读方向。
- 图标用于扫描锚点，可由现有 Lucide 资产替换，不把营销图标固化到 builder。

## 形状组合语法

- `chevron ribbon + dotted anchor + evidence text + metric box`。
- `four corner evidence cards + central 2x2 circle cluster`。
- 六段时每段正文只允许短说明；指标块保持等高等宽。
- 中心圆全部使用同一紫色角色或受控深浅，不逐圆换成彩虹色。

## 快速组合示例

- “六项年度成果，每项给一个主指标”：`arrow_ribbon_metrics`。
- “四类工作亮点，每类写具体工作和结果”：`highlight_matrix_core`。

将 `series_id` 设为 `violet_achievements`，选择 `build-series-composite-svg` 物化资源；复用时只替换
data，具体执行入口由当前 consumer 决定。

## 容量与失败

- 成果 3-6 段，每段一主指标和一段短说明；亮点恰 4 组，中心词不超过 6 字。
- 失败：把时间或因果误画成并列箭头、六段长文导致字号过小、中心圆承载正文、指标缺口径。
