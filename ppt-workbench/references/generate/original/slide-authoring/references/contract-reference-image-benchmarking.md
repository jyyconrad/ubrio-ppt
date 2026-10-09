<!--
id: contract-reference-image-benchmarking
category: execution-contract
stage: materials, outline, slide_generation
read_when: 用户提供参考效果图/示例截图/竞品 PPT，要求"照这个风格做"；或整册重写、批量生成前需要统一多页视觉与组件语言，或多页出现风格漂移时
page_roles: cover, content, section_divider, summary
supports: svg_drawingml
outputs: deck_design_contract, component_fragment_library
depends_on: contract-visual-token-core.md, theme-background-policy.md
relation_specs: requires:contract-visual-token-core, pairs_with:svg-component-library-method
triggers: 参考图, 效果图, 照着这个风格, 对标, 这个感觉, 视觉基准, 参考这张图, 竞品截图, 学习这个模板, 风格对标, 设计契约, deck级视觉, 整册统一, 风格漂移, 组件语汇
max_use: 只讲 deck 级设计契约提炼法与参考图对标纪律，不复述单页 token、不写死任何具体色值
-->

# Reference Image Benchmarking Contract

单页 reference 管一页长什么样；**"整套 20 页如何长得像一套"没有单页颗粒能覆盖**。整册重写或批量生成前，先把参考图和用户要求提炼成一份 deck 级设计契约（deck design contract），之后每页向它对齐。契约是方法产物，不是本次某张参考图的配色抄本。

## 提炼六件套（方法，不是本次配色）

从参考图 / 用户要求提炼出六节，写进 deck 设计契约：

1. **色彩 token**：浅底、深底两套 + 功能色（增长 / 风险 / 中性）+ **使用规则**（哪类页用深、强调用哪个功能色）。写 token 名与语义角色，不把某次"品牌某蓝"具体 hex 固化进契约——那是本次输入的一次性结果，写进去等于教下一份不相关的 deck 抄它。
2. **版式骨架**：标题带 / 主体带 / 结论带 / 来源行的**纵向分带**及安全区。写各带的**带宽比例**（如"标题带约占 0.18H"）与主次权重，不写死绝对 y 坐标。
3. **组件语汇线索**：清点参考图高频出现的组件类型（指标卡 / 论证卡 / 徽章 / 进度环 / 表头…）。此处只记语汇清单；把它们落成可复制 `<g>` 片段的方法与查重纪律见 `svg-component-library-method.md`。
4. **密度与口径纪律**：引用密度合同与口径脚注规则，声明本 deck 的正文密度基线和"哪些数字必须带口径"，让每页 reviewer 有统一标尺。
5. **技法克制清单**：明确**允许**（数据语义描边、hairline 分隔、小面积状态标记）与**禁止**（无语义整圈粗描边、纯装饰色条、emoji 图标、混合图标风格）两栏。
6. **技术边界指针**：一句话指向校验器 / 硬合同文件（`drawingml-svg-authoring-core.md`、`theme-background-policy.md`、self-qa），**不复述**其规则。规则漂移时改那些文件，契约不跟着改。

## 参考图用法纪律

- **学结构语汇和冲击力基准，不抄配色与内容**。参考图给的是"强标题分隔、大数字指标卡、渐变结论带、深色数据大屏"这类**结构性冲击力**基准，把它沉进契约；配色、文案、业务数据一律不抄。
- **用户点名的色彩体系优先，参考图只定气质**。用户若指定了品牌色系，以用户为准；参考图只用来定明暗节奏、密度和组件气质。
- **多图选一张主基准**。给了多张参考图时，选一张作主基准定骨架，其余只作局部语汇补充，避免多套骨架打架。

## deck 级节奏规则

- **深浅页交替**：不让整册一个明度平铺到底，用深底页 / 浅底页交替制造节奏。整页背景由 `deck_framework.background` / `theme-background-policy.md` 承载，不在 SVG 内容层铺整页 rect。
- **每页至少一处深色 / 渐变强调变体**：即便是浅底正文页，也保留一处深色条 / 渐变块 / 强调徽章制造明暗层次。这是 deck 维度纪律，单页 reference 看不到。

## 失败检查

- **总览拼图查风格漂移**：把全 deck 缩略图拼一屏通览，任何一页明显跳出契约（配色、密度、明暗节奏偏离）即返修。
- **同组件跨页参数漂移视为违约**：同一类组件（如指标卡）在不同页出现**圆角 / 投影 / 字重 / 边距不一致**，即判违约——一致性靠复制同一片段实现，不靠每页重画。修复见 `svg-component-library-method.md` 的片段归档法。
