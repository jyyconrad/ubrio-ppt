<!--
id: contract-visual-token
category: execution-contract
read_when: 需要确定视觉主题、统一主色、颜色配额、字号、深浅背景可见性，或发现并列模块每个模块一种颜色/多色卡片/彩虹卡片
page_roles: content, section_divider, summary
supports: svg_drawingml
outputs: visual_tokens, visibility_checklist
depends_on: contract-visual-token-core.md, contract-chart-visibility.md
relation_specs: requires:contract-visual-token-core, pairs_with:contract-chart-visibility
max_use: 只作为视觉 token 家族入口；执行细则读取 core 和 chart visibility 颗粒
-->

# Visual Token Contract

视觉主题服务业务判断：政务强调庄重落实，金融强调稳健可信，科技强调能力和增长，培训强调清晰易学。本入口只做选择和路由，具体 token 读 `contract-visual-token-core.md`，图表/表格可见性读 `contract-chart-visibility.md`。

典型必修问题：汇报型 PPT 中四个并列痛点、四项能力、四项举措或多个同级模块被画成“每个模块一种颜色”。这不是有效分类，而是彩虹卡片反模式；必须统一为 deck 主色系与中性色层级，仅保留小面积语义功能色。

## 使用顺序

1. 先确定框架层 `background` 与内容层 `surface`，SVG 不画整页背景或页面 chrome。
2. 读取 `contract-visual-token-core.md`，写出 `title_text`、`body_text`、`source_text`、`accent`、`border`。
3. 页面含 native chart/table 时，读取 `contract-chart-visibility.md`，单独校验图表标题、坐标轴、图例、数据标签和表格文字。
4. 若用户指定单一色系，只把它当品牌/强调色倾向；必须保留中性文字色和必要功能色。
5. 全册遵守 deck 级色彩配额（细则见 core）：`accent` 唯一真源是 foundation `style_manifest.palette`，功能辅助色 ≤2 个且仅限语义用途，并列同级项默认同色，页与页主色不得漂移。

## 失败信号

- 深色背景黑字、深灰正文、低透明细线。
- 浅色背景浅灰正文、浅描边、低对比图标。
- 主色同时覆盖背景、surface、正文、边框和图表文字。
- 两条以上系列只用同一主色的深浅变化，缩略图里无法区分。
- 并列同级卡片逐卡换色相（彩虹排布）、页与页主色漂移，或全册非中性色相超过 3 个。

## 停止条件

生成 SVG 前列出主标题、正文、来源、图表标题/坐标轴/图例、表格文字的背景与 `fill`。发现默认黑字、低对比或整页同色时，先重配 token，再继续渲染。
