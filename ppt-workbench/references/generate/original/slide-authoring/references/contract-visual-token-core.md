<!--
id: contract-visual-token-core
category: visual-theme
module_type: style_family
read_when: 需要确定 SVG 内容层颜色、字号、surface、accent 和基础可见性
page_roles: cover, agenda, content, section_divider, summary, closing
supports: svg_drawingml
outputs: visual_tokens, visibility_checklist
policy_refs: decorative_card_edge_bar
depends_on: drawingml-svg-authoring-core.md
relation_specs: requires:drawingml-svg-authoring-core
max_use: 只讲通用视觉 token，不讲图表/表格专门可见性
-->

# Visual Token Core

每页必须有一组可解释 token。`background` 是框架层背景判断，不在 SVG 内画整页 rect；SVG 只画内容层 `surface`、文字、形状、图标和必要分割线。

## Token

- `background`：框架层背景 token，用于对比度判断。
- `surface` / `surface_alt`：卡片、面板或局部浅底；必须与背景拉开明度。
- `title_text`：主标题颜色与字号，内容页通常 `36-46px`。
- `body_text`：正文颜色与字号，通常 `15-20px`。
- `source_text`：来源/口径文字，通常 `11-13px`。
- `accent`：重点数字、短标签、箭头或关键线条。
- `border`：内容块描边、分割线、弱坐标线；不得画页面级外框。

## Deck 级色彩配额

整册的彩色预算先于单页配色决策；逐页各自发挥主色会直接毁掉整册观感。

- 一册一主色：`accent` 的唯一真源是 foundation `style_manifest.palette`（`accent-color`）；每页直接引用，不得自定新主色，也不得换色相“演绎”同类强调。
- 正文与承载面由中性色阶承担：`title_text`、`body_text`、`surface`、`surface_alt`、`border` 用灰/近灰深浅分层，不占彩色配额。
- 功能辅助色全册 ≤2 个，且只允许语义用途——风险/警示、正负对比、增长/下降；禁止拿功能色做装饰、点缀或区分并列项。
- 并列同级卡片/条目默认同色：同 `surface`、同 `accent`、同描边；差异用编号、明度分层或图标形状表达，禁止逐卡换色相（彩虹排布）。仅当条目之间存在真正语义对立（正负、风险与收益）时才可用功能色区分，且仍受 ≤2 个配额约束。
- 功能色只能小面积落在状态点、数值、图例、短标签或局部图形上；若功能色覆盖整张卡片、整栏、大片底色或完整装饰边框，它就已经成为第二主色，必须收回主色系或中性色。汇报型 deck 的缩略图总览应先读出一个连续主色系，再读到少量局部语义色。
- **默认禁止卡片边缘色条语法**：不得在卡片左缘、右缘、顶缘或底缘叠加全高/全宽彩条，也不得把同一彩条复制到并列卡片。这类色条不承载独立数据、状态或图例语义，只会重复卡片边界并制造模板感。需要强调时改用 `surface/surface_alt` 明度差、留白、字重字号、编号或小面积语义标签；风险、状态和选中态也使用状态点/胶囊标签，不使用整条卡片边条。
- 页与页之间主色不得漂移；全册非中性色相总数（主色 + 功能色）不超过 3 个。

## 单一色系规则

用户说“紫色/蓝色/绿色系列”只表示强调色倾向，不表示整页同色。`background`、`surface`、`surface_alt` 至少拉开两档明度；正文优先用高对比中性深浅色；主色只用于 `accent`、重点数字、短标签和少量标题强调。

同页需要区分正负、前后、两条曲线或多个真正语义对立的阵营时，才引入功能色辅助，例如 cyan/blue 表示增长或能力，amber/orange/red 表示风险或传统劣势。若视觉上已“一片同色”，优先用中性 surface 分层和更强明度差化解；跨色相功能色只留给真正的语义对立，不用来区分并列项。

安全例子：

- 深色页：`background=#0B1220`，`surface=#172033`，`title_text=#FFFFFF`，`body_text=#EDE7FF`，`source_text=#B8A9D9`，`accent=#A855F7`，`contrast_accent=#22D3EE`，`risk_accent=#F97316`（主色 + 两个功能色，已达非中性色相上限）。
- 浅色页：`background=#F8F5FF`，`surface=#FFFFFF`，`title_text=#241238`，`body_text=#3B2A4D`，`accent=#7C3AED`，`border=#DDD6FE`。

## SVG 落地

每个 `<text>` 显式写 `fill`、`font-family`、`font-size`；shape 的 `fill`、`stroke` 来自 token 或透明变体。禁止覆盖全页背景 rect、页面级外框、贴边竖条或侧边框；同样禁止卡片左/右/顶/底边的全高或全宽装饰色条。
