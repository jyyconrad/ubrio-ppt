<!--
id: anti-pattern-low-density-slogan
category: anti-pattern-qa
read_when: 页面只有口号、泛标签、缺证据、缺行动
page_roles: content, summary
supports: svg_drawingml
outputs: fix_rules
depends_on: contract-content-density.md
max_use: 只读取本文件，不要连带读取同类全部文件
-->

# Anti Pattern: Low Density Slogan

## 内容说明

错误：页面只有“聚焦增长 / 协同赋能 / 提质增效”等口号。

修正：

- 把口号改成判断句。
- 补 2-3 条事实、数据、案例或动作。
- 缺证据时不要编造。缺口标签（如“需补充”）只用于 outline / 内部修补清单（工作态）；最终页面正文不保留草稿词，只允许口径边界句（如“内部测算，待商务确认”“风险边界/假设条件”）或删槽、ask_user 补料。
- 底部用一句行动或风险收口。
- 本文件管“整页缺证据”的密度问题；页面已有证据但文案仍是对仗口号、热词堆砌或“不是A而是B”套话时，读 `anti-pattern-ai-flavor.md`。

## 视觉说明

不要靠放大口号填满页面。用证据卡、指标胶囊、行动条承载信息。

## SVG说明

检查正文页是否只有 `main-title` 和少量标签。若是，必须补
`content-group-*` 和 `actions`。
