<!--
id: anti-pattern-layout-overflow
category: anti-pattern-qa
read_when: 元素越界、重叠、第四卡超出画布、文字被遮挡
page_roles: content
supports: svg_drawingml
outputs: fix_rules
depends_on: drawingml-svg-authoring.md
max_use: 只读取本文件，不要连带读取同类全部文件
-->

# Anti Pattern: Layout Overflow

## 内容说明

越界和重叠会让业务内容丢失或不可读。修几何时不能删除输入里的关键字段。

## 视觉说明

常见错误：

- 四卡并列总宽超过 1600。
- 标题与核心结论重叠。
- 底部结论条里，短标签和长正文使用同一 baseline 的两个 `<text>`，正文从标签内部开始。
- `source-note` 或底部行动条压住主体。
- 箭头穿过正文。
- 封面/放射图连线穿过中心主文字 bbox。
- 封面核心判断卡两行大字（如两行 30px）贴底或溢出卡片，底部没有留 padding。

## SVG说明

修正规则：

- 四卡用 `x=86/450/814/1178 w=336 gap=28`。
- 主标题区保留到 `y=160` 左右，主体从 `y=260..320` 开始。
- 所有元素坐标必须在 `0..1280`、`0..720` 内。
- 长文本拆短行，不靠缩到不可读字号。
- 标签后接长句时，优先用一个 `<text>` 加内联 `<tspan>`；拆成两个 `<text>` 时，
  先按标签字号估算宽度，再把正文起点右移并保留 12-16px 间距。
- 连线穿过中心主文字时，把连线起点退到文字 bbox 外断开，或给中心文字加遮罩底板压在连线之上。
- 封面核心判断卡：卡片底部预留 padding，文字不贴底。两行 30px 放不下时降到 26px，
  或改成 1 行主判断 + 1 行副解释并分层留行距，不让大字溢出卡片。
