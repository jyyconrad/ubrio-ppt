<!--
id: anti-pattern-dark-background-black-text
category: anti-pattern-qa
read_when: 深色背景出现黑字、未设 fill、深灰正文或低对比线条
page_roles: content, section_divider
supports: svg_drawingml
outputs: fix_rules
depends_on: contract-visual-token.md
max_use: 只读取本文件，不要连带读取同类全部文件
-->

# Anti Pattern: Dark Background Black Text

## 内容说明

深色页仍要完整表达标题、结论、证据和行动，不能因为背景深就只放口号。

## 视觉说明

错误：

- 深蓝/黑色背景上使用 `fill="#000000"` 或 `fill="black"`。
- `<text>` 未设 fill，依赖默认黑色。
- 用深灰小字写正文或来源。

修正：

- 主标题用 `#FFFFFF`。
- 正文用 `#D6E4FF`、`#E5F0FF` 等浅色。
- 来源文字用较弱但可读的浅色，如 `#8FA8CC`。
- 线条和图标用 `accent` 或浅描边。

## SVG说明

提交前搜索：`fill="#000000"`、`fill="black"`、`<text ` 未带 `fill`。发现即修。
