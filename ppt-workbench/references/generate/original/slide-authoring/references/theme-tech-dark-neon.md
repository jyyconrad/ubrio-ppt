<!--
id: theme-tech-dark-neon
category: visual-theme
read_when: 科技、互联网、AI、平台能力、增长飞轮
page_roles: content, section_divider
supports: svg_drawingml
outputs: visual_tokens
depends_on: contract-visual-token.md, anti-pattern-dark-background-black-text.md
max_use: 只读取本文件，不要连带读取同类全部文件
-->

# Tech Dark Neon Theme

## 内容说明

适合技术能力、平台架构、AI 产品、增长模型。内容要写能力、证据、效果和下一步，不只写酷炫词。

## 视觉说明

视觉 token：

- `background`: `#07111F`
- `surface`: `#0F2438`
- `title_text`: `#FFFFFF`, `40-52px`
- `body_text`: `#D8E7FF`, `15-19px`
- `source_text`: `#8CA3C7`, `11-13px`
- `accent`: `#38BDF8`
- `border`: `#1D4ED8`

整页深色底的背景形态选型与参数（photo_dark/paper_light/pattern/纯色四形态）统一见 theme-background-policy 颗粒。

毛玻璃效果用半透明面板和浅描边模拟（真毛玻璃 `backdrop-filter` 无 DrawingML 等价物，不写此类滤镜）；霓虹光晕可用单个 `feGaussianBlur`（可选 `feOffset`）做外发光强调重点，禁多滤镜堆叠或 `feColorMatrix` 等复杂合成。霓虹色只强调重点，不做整页正文。

## SVG说明

面板可用 `fill="#0F2438" fill-opacity="0.82"`，描边 `stroke="#38BDF8" stroke-opacity="0.45"`。
