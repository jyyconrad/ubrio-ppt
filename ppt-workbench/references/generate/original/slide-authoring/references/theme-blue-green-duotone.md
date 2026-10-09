<!--
id: theme-blue-green-duotone
category: visual-theme
module_type: style_family
read_when: 蓝绿撞色双主色页，正反/亮点短板/问题改进分区表达
page_roles: cover, agenda, content, section_divider, summary, closing
stage_tags: slide_generation
supports: svg_drawingml
outputs: visual_tokens
depends_on: contract-visual-token-core.md, anti-pattern-dark-background-black-text.md
relation_specs: requires:contract-visual-token-core, pairs_with:layout-kpi-strip, conflicts_with:theme-cultural-green
triggers: 蓝绿, 撞色, 双主色, 蓝绿撞色, 正反对比, 亮点短板, 问题改进, 双色分区, blue green, duotone, dual accent, contrast panel
max_use: 只读取本文件，不要连带读取同类全部 theme
source_notice: 参考公开职场汇报模板的结构组织方式与配色体系，已抽象为本项目可复制方法；原作固定话术、示例文案、品牌水印一律作为分析输入后丢弃，不入语料。
-->

# Blue-Green Duotone Theme

## 适用判断

- use_when：需要蓝、绿两种主色分工的经营/复盘/评估页，尤其是亮点 vs 短板、正面 vs 负面、问题 vs 改进的正反语义分区。
- avoid_when：单色系需求（单蓝走 theme-light/dark-business-blue，单绿人文/文旅走 theme-cultural-green）、党政红金、科技暗夜；四个并列痛点/能力/举措等同级模块也不属于二元对立，禁止为了区分模块使用本双主色主题。
- 与 theme-cultural-green 区分：cultural-green 是单一墨绿点题的人文/文旅浅底风；本主题是蓝+绿两种饱和主色撞色分工，服务数据对比而非文化表达。

## 视觉 token

- accent_blue 蓝：`#2456C8` / `#1F5FD0`（正面、亮点、主体、行动、主判断）
- accent_green 翡翠绿：`#16B98D` / `#25C08A`（负面、短板、问题、点缀；或主蓝辅绿的第二区）
- surface_blue 浅蓝底：`#E5EDFB`；surface_green 浅绿底：`#E8F3EE`；surface 白卡：`#FFFFFF`
- title_text：`#16233B`，36-46px；body_text：`#31414F`，15-19px
- background 页底浅灰白：`#F0F2F5`（框架层判断用，不在 SVG 画整页 rect）

## 撞色分工规则（核心价值）

- 语义绑定固定：蓝担正面/亮点/主体/行动，绿担负面/短板/问题/点缀，不要随机上色。
- 正反语义页（亮点vs短板、问题vs改进、现状vs目标）用左右或上下撞色分区：两区各用对应主色实底大圆角面板 + 对应浅底承载正文。
- 方向用升降三角 ▲（升/正）▼（降/负）配主色，不堆红绿灯。
- 也可主蓝辅绿：主体统一蓝，绿只做关键点缀或唯一强调，避免通篇双色对半、失去主次。
- 问题-改进-价值三段页：问题面板用辅色实底、改进面板用主色实底、价值轨用白底主色字（轻量，不参与撞色对抗），整版结构读 `layout-problem-improve-value-rail.md`。

## SVG 落地与降级

- 大圆角=rect 的 rx（rx==ry 保原生调节柄）；轻投影/外发光用 defs `<filter>` 内单个 `feGaussianBlur`（可选 `feOffset`）转 `outerShdw`/`glow`，或用细描边；禁毛玻璃近似质感、内发光（`innerShdw` 暂无转换器支持）与多滤镜堆叠。
- 撞色面板须保持实底 fill 以维持语义强度，不对撞色面板本身叠加半透明玻璃质感（半透明面板毛玻璃近似技法见 `theme-tech-dark-neon.md`，本主题的语义撞色面板不用）；深色面板上文字与三角显式浅色，不留黑字。
- 金标骨架可复用 `load_skill_example(path="assets/examples/svg-ppt/decks/scenario-report-structure-gold-pages/01-kpi-strip.svg")` 看折角卡与结论条的信息层级（该页为紫调，撞色分区自行按蓝绿 token 替换）；勿照抄坐标与首行整页背景 rect（离线预览底色，运行时触发 `SVG_FULL_PAGE_BACKGROUND_FORBIDDEN`）。
