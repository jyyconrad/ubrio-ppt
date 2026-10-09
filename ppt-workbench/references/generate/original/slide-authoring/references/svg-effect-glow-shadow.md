<!--
id: svg-effect-glow-shadow
category: shape-patterns
read_when: 需要给强调卡/徽标/标题加外发光或柔和投影，或需要毛玻璃近似质感时
page_roles: content, section_divider, summary
supports: svg_drawingml
outputs: copyable_svg_fragments, glow_shadow_discipline
depends_on: drawingml-svg-authoring-core.md
relation_specs: pairs_with:theme-tech-dark-neon, requires:contract-visual-token-core
triggers: 发光, 外发光, 光晕, 霓虹, 投影, 柔和阴影, 卡片阴影, 毛玻璃, 磨砂质感, 半透明面板, glow, drop shadow, frosted glass
max_use: 只讲单滤镜发光/投影与半透明近似技法；立体渐变读 svg-shape-3d-isometric.md
-->

# SVG Effect: Glow / Soft Shadow / Frosted Glass

发光、投影、毛玻璃的唯一技法颗粒。渲染器把单个 SVG `filter` 映射为 DrawingML 的
`<a:glow>` 或 `<a:outerShdw>`；颜色/字体必须替换为当前 deck 的视觉 token。凡涉及
「立体、厚度、渐变体积」改读 `svg-shape-3d-isometric.md`。

## 外发光 glow

```xml
<defs>
  <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
    <feGaussianBlur stdDeviation="6"/>
    <feFlood flood-color="#22D3EE" flood-opacity="0.9"/>
  </filter>
</defs>
<rect x="0" y="0" width="240" height="150" rx="18" fill="#0F2438" filter="url(#glow)"/>
```

- **关键坑：发光颜色/浓度默认黑色、浓度 0.3，深底上几乎不可见——有色发光必须补
  `feFlood`**（`flood-color` 定色、`flood-opacity` 定浓）。
- `stdDeviation` 4~8 合适（越大越散），按 1× 映射为 `<a:glow>` 的 rad。

## 柔和投影 outerShdw

```xml
<filter id="ds" x="-50%" y="-50%" width="200%" height="200%">
  <feDropShadow dx="6" dy="8" stdDeviation="7" flood-color="#050B18" flood-opacity="0.5"/>
</filter>
```

- 推荐 `feDropShadow` 一处写全（偏移/模糊/色/浓）；也可 `feGaussianBlur` + `feOffset`，
  但不写 `feFlood` 时色/浓默认黑 0.3。
- **判别规则：filter 内有 `feOffset` 或 `feDropShadow` → 投影（`<a:outerShdw>`），无偏移
  → 发光（`<a:glow>`）**。`stdDeviation` 按 2× 映射为 blurRad。

## 文字发光

- `text` 元素挂**无 `feOffset`** 的 glow filter，即走 run 级发光；文字要发光只用 glow。
- 带 offset 的滤镜会被判为形状级投影，不要给文字用。

## 毛玻璃近似

- 真毛玻璃 `backdrop-filter` 无 DrawingML 等价物，不写此类滤镜。
- 近似：卡片底铺 `fill="#FFFFFF" fill-opacity="0.12~0.2"` + 细描边（浅色 `stroke-opacity`），
  深底上观感接近磨砂玻璃；**不承诺背景模糊**。

## 纪律

- filter 内只放 `feGaussianBlur`/`feFlood`/`feOffset`/`feDropShadow`；混入
  `feColorMatrix`/`feBlend`/`feComposite`/`feTurbulence` 会被静默忽略、误产一圈默认黑色微光（实测）。
- 每页发光/投影 ≤2~3 处，只给徽标、强调卡、标题；大面积折带、箭头带、面板不发光。
- 单元素只挂一个 filter，禁多滤镜堆叠；禁 `rgba()` 与 `<g opacity>` 组透明。

## 金标示例

- 路径：`assets/examples/svg-ppt/decks/scenario-effects-structure-gold-pages/02-glow-soft-shadow.svg`
- 调用：`load_skill_example(path="assets/examples/svg-ppt/decks/scenario-effects-structure-gold-pages/02-glow-soft-shadow.svg")`
- 参考霓虹有色发光强调卡、feDropShadow 白卡、标题文字 glow 与毛玻璃近似面板的上色分工；勿照抄坐标或把占位数据当业务事实。
- 勿照抄首行整页背景 `<rect>`：那只是离线预览底色，运行时背景由 `deck_framework.background` 承载，内容层画满页背景会触发 `SVG_FULL_PAGE_BACKGROUND_FORBIDDEN`。
