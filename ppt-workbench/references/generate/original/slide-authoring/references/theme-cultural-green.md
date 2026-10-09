<!--
id: theme-cultural-green
category: visual-theme
read_when: 文化、品牌、传统表达、文旅或价值观页面
page_roles: content, section_divider
supports: svg_drawingml
outputs: visual_tokens
depends_on: contract-visual-token.md
max_use: 只读取本文件，不要连带读取同类全部文件
-->

# Cultural Green Theme

## 内容说明

适合文化表达、品牌理念、传统主题和文旅材料。典故或引语只能引出观点，不替代业务证据。

## 视觉说明

视觉 token：

- `background`: `#F7F2E8`
- `surface`: `#FFFFFF`
- `title_text`: `#1F2933`, `38-48px`
- `body_text`: `#2F3A3D`, `15-19px`
- `source_text`: `#6B6258`, `11-13px`
- `accent`: `#2E7D6B`
- `border`: `#D8D0C3`

可少量使用朱砂 `#B91C1C` 点题。正文仍优先可读，不用浅米色小字。

## SVG说明

背景可加低透明纹理色块（整页背景选型与参数统一见 theme-background-policy 颗粒：photo_dark/paper_light/pattern/纯色四形态），但所有文本必须高对比。不要用 `feTurbulence`/`feColorMatrix` 等复杂滤镜模拟水墨质感；如需克制的强调发光/投影仍可用单个 `feGaussianBlur`。
