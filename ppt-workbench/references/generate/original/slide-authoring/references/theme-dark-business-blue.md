<!--
id: theme-dark-business-blue
category: visual-theme
read_when: 深蓝强调页、章节页、关键判断页
page_roles: content, section_divider
supports: svg_drawingml
outputs: visual_tokens
depends_on: contract-visual-token.md, anti-pattern-dark-background-black-text.md
max_use: 只读取本文件，不要连带读取同类全部文件
-->

# Dark Business Blue Theme

## 内容说明

适合章节过渡、关键数据强调、战略判断页。正文页使用深色时必须提高文字对比和卡片承载。

## 视觉说明

视觉 token：

- `background`: `#0B1A30`
- `surface`: `#102A43`
- `title_text`: `#FFFFFF`, `42-56px`
- `body_text`: `#D6E4FF`, `16-20px`
- `source_text`: `#8FA8CC`, `11-13px`
- `accent`: `#45D1FF`
- `border`: `#2B4C7E`

整页深色底的背景形态选型与参数（photo_dark/paper_light/pattern/纯色四形态）统一见 theme-background-policy 颗粒。

深色背景上所有文字、线条、图标必须显式浅色。禁止黑字、深灰正文和低透明细线。

## SVG说明

用深色面板承载主体，面板描边可用 `stroke="#2B4C7E"`。正文 fill 使用
`#D6E4FF` 或 `#FFFFFF`，不要省略 fill。
