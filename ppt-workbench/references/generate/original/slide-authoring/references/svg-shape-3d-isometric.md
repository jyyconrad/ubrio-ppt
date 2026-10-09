<!--
id: svg-shape-3d-isometric
category: shape-patterns
read_when: 需要给层级/递进/堆叠语义加"扁平等距立体"体积感（分层立体金字塔、等距立方堆叠、阶梯棱柱），或需要 PowerPoint 原生可编辑的真 3D 浮起/挤出（data-effect-3d 受控预设）
page_roles: content, summary
stage_tags: slide_generation
supports: svg_drawingml
outputs: copyable_svg_fragments, isometric_shape_rules
depends_on: contract-visual-token-core.md, drawingml-svg-authoring.md
relation_specs: requires:contract-visual-token-core, pairs_with:layout-pyramid-hierarchy, pairs_with:layout-timeline-ascending-steps, pairs_with:layout-funnel-stage-stack
triggers: 3D, 立体, 等距, 轴测, 立方体, 阶梯柱, 立体金字塔, 体积感, 明暗渐变, isometric, faux 3d, 真3D, sp3d, bevel, 浮雕, 挤出, 拟物立体, data-effect-3d, 立体卡片, 立体徽标, 3D 凸起
max_use: 只讲 2D 等距/轴测假立体技法与 data-effect-3d 受控真 3D 预设；真实数值比例改 chart，层级语义由 pairs_with 的 layout 承载
source_notice: 参考公开职场汇报模板的立体视觉效果，已抽象为本项目可复制的 2D 等距技法；原作固定话术、示例文案、品牌水印一律作为分析输入后丢弃，不入语料。
-->

# SVG Shape: 3D Isometric（假三维等距技法）

多面 `<polygon>` 拼接 + 每面 `<linearGradient>`，转换后落 freeform + gradFill，完全可编辑；给"层级/递进/堆叠"语义加体积感，非新原语。

## 三面明暗分配（核心规则）

一个等距立方/棱柱三个可见面：**顶面受光最亮、左面中间调、右面背光最暗**。

- 相对基准色：顶面提亮约 +15% 明度、背光面压暗约 −20%；三档明度差要拉开才有体积。
- 明暗靠**渐变方向向量**（`x1/y1/x2/y2`）编码"受光从哪来"，不是只换 stop 颜色。
- **每面各自一条 `linearGradient`**：三面共享一条会穿帮（方向对不上）。
- **同一页所有立体块受光方向一致**：顶/左/右面各自同方向，可跨块复用同一条 def（按 bbox 贴图）。

## 骨架 1：等距立方（可复制，颜色换成当前 token 明暗三档）

```xml
<defs>
  <linearGradient id="iso-top" x1="0" y1="0" x2="0.35" y2="1"><stop offset="0" stop-color="#9E76D6"/><stop offset="1" stop-color="#7E56B4"/></linearGradient>
  <linearGradient id="iso-left" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#6A44A0"/><stop offset="1" stop-color="#472B7C"/></linearGradient>
  <linearGradient id="iso-right" x1="1" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#402A6E"/><stop offset="1" stop-color="#281653"/></linearGradient>
</defs>
<polygon points="380,224 466,267 380,310 294,267" fill="url(#iso-top)"/>   <!-- 顶面菱形 -->
<polygon points="294,267 380,310 380,362 294,319" fill="url(#iso-left)"/> <!-- 左前面 -->
<polygon points="380,310 466,267 466,319 380,362" fill="url(#iso-right)"/><!-- 右前面 -->
```

顶面四点 = 上/右/下/左菱形；左右前面 = 顶面下棱各向下拉高度 H 的平行四边形。

## 骨架 2：分层立体金字塔（能力层级 / 战略分层）

- 自下而上堆 3 个等距立方，越往上越窄（婚礼蛋糕式），露出下层顶面一圈。
- **从底层向顶层依次绘制**（画家算法），上层才能正确遮住下层顶面后缘；三面复用同三条渐变，短标签放露出的顶面前缘或左面中心。

## 骨架 3：阶梯棱柱（逐期走高的增长动能）

- 每期一个立方（正面矩形 + 顶面平行四边形 + 右侧面），柱高随期次递增。
- 只做等距平面拼接，**不做真透视/斜切**；期次标签落柱底，巨数落正面。

## 容量与克制

- 立体块是**语义装置不是装饰**：每页 ≤1 组（一座金字塔 / 一列阶梯 / 一组立方）。
- 块内不塞长文本：面上标签 ≤6 字，描述、证据、来源移到旁栏。
- 立体高度是叙事装置不是数据刻度；真实比例改 `chart-bar-comparison.md`。

## 能到与到不到（如实告知）

- **能到**：扁平设计里的等距/轴测立体，够业务汇报表达堆叠/递进。
- **到不到**：真透视 + 任意光照的拟物 3D；需要 bevel 高光/真挤出时只能走下节受控真 3D 预设，**不要**用任意透视/斜切/filter 硬凑——会转换失败或被拒。

## 真 3D 变体（data-effect-3d，受控预设）

默认仍走上文假 3D（多面 polygon + 渐变）；仅当需要"渲染器造体积"的拟物立体且放映宿主以 PowerPoint 为主时才用真 3D。LibreOffice 缩略图可能把 3D 平面化——那是降级不是失败，不要据缩略图反复重渲。

- 写法：给单个 `rect/circle/ellipse/path/polygon` 挂 `data-effect-3d='{"preset":"card-raised"}'`，转换器生成原生 `<a:scene3d>+<a:sp3d>`（PowerPoint 三维格式面板可编辑）。
- 预设仅三个：`card-raised`（KPI 卡/结论条微浮起，默认首选）、`button-soft`（圆徽标/步骤圆点，饱满圆 bevel）、`block-extruded`（榜首/推荐块等距挤出，可加 `"depth":1|2|3` 与 `"contour_color":"#RRGGBB"`，这两键仅此预设可用；PowerPoint 优先，LO 平面化可接受）。
- 硬约束（input_gate 执法）：每页 ≤3 个声明；只能挂上述五类形状（text/g/line 挂上即报错）；不接受预设之外自由拼 camera/lightRig/bevel。
- 与假 3D 正交：假 3D 自己用多面 polygon 画体积，真 3D 是单个形状交给渲染器造体积；**同一元素禁止两法混用**，同页建议单一路线。目标形状最小边 ≥48px（过小 bevel 成噪点）；不与 glow filter 同挂一个元素。
- 金标：`load_skill_example(path="assets/examples/svg-ppt/decks/scenario-composite-structure-gold-pages/05-effect-3d-preset.svg")`（三档套餐对比：结论条 card-raised、推荐卡 block-extruded、推荐徽标 button-soft，恰好 3 个声明，示范克制用法）。

## 金标示例

- 路径：`assets/examples/svg-ppt/decks/scenario-effects-structure-gold-pages/01-isometric-3d.svg`
- 调用：`load_skill_example(path="assets/examples/svg-ppt/decks/scenario-effects-structure-gold-pages/01-isometric-3d.svg")`
- 只参考三层立体金字塔的三面明暗、短标签在块内/详情在旁栏的分工；不要照抄坐标或把占位数据当业务事实。
- 勿照抄首行整页背景 `<rect>`：那只是离线预览底色，运行时背景由 `deck_framework.background` 承载，内容层画满页背景会触发 `SVG_FULL_PAGE_BACKGROUND_FORBIDDEN`。
