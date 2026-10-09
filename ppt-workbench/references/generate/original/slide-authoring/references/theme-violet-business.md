<!--
id: theme-violet-business
category: visual-theme
module_type: style_family
read_when: 紫色商务季度/半年/年度经营汇报，内敛专业又要一点活力
page_roles: cover, agenda, content, section_divider, summary, closing
stage_tags: slide_generation
supports: svg_drawingml
outputs: visual_tokens, background_policy
depends_on: contract-visual-token-core.md, anti-pattern-dark-background-black-text.md
relation_specs: requires:contract-visual-token-core, pairs_with:layout-kpi-strip, conflicts_with:theme-red-gold-government
triggers: 紫色, 紫色商务, 紫调, 商务汇报, 季度汇报, 半年汇报, 年度汇报, 经营汇报, violet, purple, business purple, quarterly review
max_use: 只读取本文件，不要连带读取同类全部 theme
source_notice: 参考公开职场汇报模板的结构组织方式与配色体系，已抽象为本项目可复制方法；原作固定话术、示例文案、品牌水印一律作为分析输入后丢弃，不入语料。
-->

# Violet Business Theme

## 适用判断

- use_when：职场季度/半年/年度经营汇报、复盘述职，需要内敛专业又保留一点活力与设计感。
- avoid_when：党政红金正式宣贯（用 theme-red-gold-government）、科技暗夜/霓虹场景（用 theme-tech-dark-neon）。
- 与相邻主题区分：比 theme-light-business-blue 多一层品牌活力与层次（靠紫色渐变卡而非纯蓝白）；与 theme-dark-business-blue 相反，本主题 polarity=light，深紫只作横幅/收口条等框架层 chrome，不整页铺深；整页背景选型与参数统一见 theme-background-policy 颗粒（photo_dark/paper_light/pattern/纯色四形态）。

## 视觉 token（polarity = light）

- accent 主紫：`#6B2D9C`（圆点、箭头、主填充、巨数）
- accent_strong 深紫：`#2E1B5E`（渐变暗端、深色收口条/横幅）
- accent_mid 中紫：`#5B3391`（渐变中段、次级强调）
- surface 白卡：`#FFFFFF`；surface_alt 浅紫：`#EFE9F7`（KPI/胶囊浅底）
- border 浅紫描边：`#D8CCEA`
- title_text 近黑紫：`#241238`，36-46px；body_text 正文：`#3B2A4D`，15-19px
- background 页底浅灰：`#EAEAEC`（框架层判断用，不在 SVG 画整页 rect）

## 分工规则（核心方法）

- 渐变卡：浅紫→深紫对角 linearGradient，承载 KPI/强调块；卡上巨数与标签用白/浅紫文字保证对比。
- 文本卡：白底 + 浅紫细描边（≤1.2px）；层级靠卡内文字权重和留白分组，不叠加左侧/顶部装饰竖条。正文用近黑紫，巨数用 60-80px 粗体主紫、单位小一号紧贴。
- 紫色胶囊 tag（浅紫底圆角 rect + 主紫字）作字段标签或分类。
- 同页需要区分正负或多阵营时引功能色（cyan 增长 / amber-orange 风险），不要一片同紫。

## SVG 落地与降级

- 每个 `<text>` 显式 fill/font-family/font-size；渐变用 defs 内 linearGradient；如需强调可用单个 `feGaussianBlur`（可选 `feOffset`）做外发光/投影，禁毛玻璃、内发光（`innerShdw`）与多滤镜堆叠模拟质感。
- 深紫横幅、页码、外框属框架层；SVG 内容层不画整页背景 rect 与页面级外框。
- 金标示例：`load_skill_example(path="assets/examples/svg-ppt/decks/scenario-report-structure-gold-pages/01-kpi-strip.svg")` —— 参考紫色渐变折角卡、深紫结论条与胶囊 tag 的上色分工；不要照抄坐标与占位数据，也勿照抄首行整页背景 rect（仅离线预览底色，运行时触发 `SVG_FULL_PAGE_BACKGROUND_FORBIDDEN`）。
