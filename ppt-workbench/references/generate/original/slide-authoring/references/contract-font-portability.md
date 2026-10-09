<!--
id: contract-font-portability
category: execution-contract
read_when: 需要在 SVG 里写中文/西文 font-family、扩充字体集合，或排查多宿主（渲染主机预览 / 导出 PPTX / 换台电脑查看）字体回退、宋体化时
page_roles: content, section_divider, summary, cover
supports: svg_drawingml, render_svg_drawingml_slide
outputs: font_policy, font_whitelist_rules
depends_on: drawingml-svg-authoring-core.md
relation_specs: requires:drawingml-svg-authoring-core
triggers: 字体, 字体名, font-family, 中文字体, 衬线, 无衬线, 宋体, 字体不显示, 字体回退, 字体缺失, 导出后字体变了, 换台电脑字体不对, 字体白名单, Microsoft YaHei, Noto Serif CJK
max_use: 只讲字体跨宿主约束与白名单纪律，不复述 SVG 几何或视觉 token 规则
-->

# Font Portability Contract

`drawingml-svg-authoring-core.md` 只要求每个 `<text>` 显式写 `font-family`，没说**该写哪个字体名**。字体名不是审美偏好，是跨宿主的可移植性约束：写错的字体名不会报错，只会静默降级。

## 两个宿主，两套约束

一个字体名要同时满足两个不同主机才算安全，两者靠导出期 typeface 映射连接，不能指望一套字体名通吃：

1. **编写 / 预览宿主 = 渲染主机**。SVG→PPTX→缩略图链路在渲染主机上跑（LibreOffice + fontconfig）。字体名必须是渲染主机**真实安装**的字体，否则 fontconfig 静默回退，预览与缩略图失真——你看到的不是交付稿真实样子。
2. **交付宿主 = 观看主机**。用户最终打开 PPTX 的电脑，无法预设，**默认按 Windows PowerPoint 基线**。字体名必须是该主机普遍可用的字体，否则 PowerPoint 回退到宋体，交付稿风格全崩。

**连接机制**：导出期把编写字体映射为交付字体。漏映射的中文字体名 = Windows 端宋体。所以选字体名时同时问两句：渲染主机装了吗（预览真不真）？观看主机认得吗（交付崩不崩）？

## 为什么无衬线默认是 Microsoft YaHei

Microsoft YaHei 是 **Windows PowerPoint 的中文无衬线事实基线**——观看宿主几乎必然装它，回退风险最低。全语料默认把无衬线中文写成 `Microsoft YaHei` 是这个交付端事实决定的，不是好看。任何不在观看宿主基线内的中文字体名，交付端都会掉回宋体。西文陪衬统一收尾到 `Arial`（同为 Windows 基线），写成 `Microsoft YaHei, Arial`。

## 中文衬线场景

文学纪录片 / 人文叙事风格的灵魂是衬线中文，此时无衬线基线不适用：优先 `Noto Serif SC` / `Source Han Serif SC`，用法与降级次序对齐 `style-literary-documentary-cn.md`（缺字体可降级到 `Songti SC` / `Microsoft YaHei`，但不要把全篇改回默认无衬线商务风）。衬线中文对渲染主机有硬要求——渲染主机若无任何衬线 CJK 字体，缩略图会静默回退，见下节校验。

## 新字体上线前先过渲染 host 校验

字体集合不是随手扩的偏好清单，是**导出链验证产物**。引入任何新字体名前：

- 先跑 `scripts/check-render-fonts.sh` 确认渲染主机真装了它（衬线 CJK 是硬性要求，缺失非零退出并给安装指引）。
- 再跑一遍完整导出 + 跨宿主验证（导出 PDF / PowerPoint 抽查封面、图表页、深色页，判读无宋体 fallback）。
- 两关都过，字体名才允许进白名单。**扩集合 = 改导出链契约**，不是改文案。

## 字体缺失是降级不是失败

`render_svg_drawingml_slide` 的 `conversion_report.font_availability` 会给出 `{requested, resolved, missing, serif_cjk_available, checked}` 诊断；渲染主机缺衬线 CJK 时报 **`SERIF_CJK_FONT_MISSING`（severity=warning，非阻塞）**，其他请求字体缺失报 `REQUESTED_FONT_MISSING`。

- 这些是**降级信号，不是渲染失败**。字体回退不影响元素结构、坐标或可编辑性，只影响字形观感。
- 模型不应据此判定"渲染出错"而盲目重试或推翻整页——重试不会让缺失字体凭空出现。正确处置是：要么接受降级（观感损失可控时），要么修渲染主机字体安装（运维动作，非模型动作），二者都不是重画 SVG。

## 数字质感技法

数字、金额、KPI 巨数可用**西文优先栈 + 中文回退**做出更紧凑锐利的质感，如 `Helvetica Neue, Microsoft YaHei`：西文数字先由 Helvetica Neue 承接，遇中文单位或缺字体时回退到中文主字体。硬约束：**栈里的西文字体必须已在白名单内**（同样过双宿主校验），不能为了质感临时塞一个渲染主机 / 观看宿主未验证的西文字体名。

## 最小集合形态

一套 deck 的字体集合保持小而受控：**1 个中文主字体（无衬线基线或衬线基线）+ 2-3 个白名单内西文数字字体**。集合越小，跨宿主回退面越小；需要更多字形差异时优先用字重 / 字号 / 颜色分层，而不是引入新字体名。
