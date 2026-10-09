<!--
id: drawingml-svg-authoring
category: execution-contract
read_when: 需要排查复杂 SVG DrawingML 兼容、图片裁切、marker、渐变或校验失败
page_roles: content, section_divider, summary
supports: svg_drawingml
outputs: svg_compatibility_contract, debugging_rules
depends_on: drawingml-svg-authoring-core.md
max_use: 只补充 always-read core 之外的进阶细则；不承载业务场景、布局或视觉主题
-->

# DrawingML SVG Authoring Reference

先遵守 `drawingml-svg-authoring-core.md`。本文件只处理复杂边界和调试，不重复页型、主题、图表分型或业务写作方法。

## 写作原则与内容保真

业务字段、指标、周期和来源必须原样进入文本节点；几何只负责表达关系，不改写事实。复杂页先估算容量和主体 bbox，再进入 SVG 细化。

## DrawingML 兼容 SVG

- `clipPath` 只用于本地图片裁切，且只含一个基础 shape；非 image 的 clip-path、mask 不要使用。`filter` 仅允许 `feGaussianBlur` 配 `feFlood` 上色（可选叠加 `feOffset`/`feDropShadow`）做外发光/柔和投影，`feColorMatrix`/`feBlend`/`feComposite`/`feTurbulence` 等复杂合成滤镜和多滤镜堆叠仍不要使用。
- 箭头 marker 必须在 `<defs>` 中，`orient="auto"`，marker fill 与线条 stroke 一致。
- 一个逻辑行使用一个 `<text>`；同一行强调用内联 `<tspan>`，不要用多个相邻 text 拼一句话，内联 `<tspan>` 不带 `x/y/dy`。
- 直接子节点优先是语义 `<g id="...">`；主标题组用 `main-title-block` 或 `main-title`，核心判断用 `key-message`，主体组用 `content-group-1..N`。
- 字体栈以 `Microsoft YaHei`、`SimSun`、`Arial`、`Calibri` 等 PowerPoint 常见字体收尾。

## 几何与容量

- 生成前估算主体 bbox：排除 `source-note`、弱注释和框架 chrome 后记录 `x/y/w/h/bottom`。
- 普通内容页、矩阵、对比表和复盘页主体底边通常应达到 `y≈608` 或更低；不能靠来源注释占底部。
- 字号与容器匹配：按 `单行可容纳字符数 ≈ 容器内宽 / 每字宽` 估算；装不下先压短、折行或换低密度版式。
- 复杂架构图、流程图、网络拓扑和时间线可用代码辅助几何生成节点、连接线和 path 坐标；代码只算局部几何，不生成完整 deck。

## Native Slot 边界

- 图表和逐单元格表格走 `layout-native-chart-slot.md`；SVG 只画标题、洞察、slot 外框、来源和必要说明，且标题/洞察/来源必须在 slot 分组外（组内文字是占位，渲染时自动移除）。
- 图标槽位使用 `data-icon-id` / `data-icon-box` / `data-icon-color`；颜色可取 `accent-color`、`title_text-color` 或 `body_text-color`。
- 证据图、书封、正文局部图片先走图片绑定或 `layout-native-image-slot.md`；不要直接写远程 `<image href>`。
- 根节点或 slot 可写 `data-native-data-ref="slide-generation/<page_id>/native-data.json"`，但不要把完整 JSON 塞进 SVG 属性。

## 校验失败处理

- 元素不支持：删除或改成允许元素，不通过 `foreignObject`、`style`、`class`、`use`、`textPath`、动画绕过。
- 文字越界：先缩短文案、折行或重排，不盲目降到不可读字号。
- 对比度失败：回到 `contract-visual-token-core.md` 和 `contract-chart-visibility.md` 调整 token。
- slot 失败：检查 slot `id`、`data-role`、坐标和 `native-data.json` 的 `slot_id` 是否一致。

## 不支持的 SVG 写法

不写页面级背景、页眉、页码、页面侧边框、贴边竖条、整页外框；这些不要进入 SVG。不使用远程资源、超大 data URI、`rgba()`、组级 opacity、emoji、草稿态占位或 renderer 不能转换的 SVG 元素。

## 提交前硬检查

标题、结论、必填字段和来源都在 `<text>` / `<tspan>` 中；无整页背景、页面侧边框、默认黑字、低对比正文、不可读小字或空卡；图标槽位使用 `data-icon-id` / `data-icon-box`；已按校验建议局部修复当前 SVG。
