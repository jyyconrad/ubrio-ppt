<!--
id: layout-versus-duel
category: layout
read_when: 两个对象或两个时点的对碰式对比（目标 vs 达成、本期 vs 上期、我方 vs 竞品），需要"对决"张力
page_roles: content, summary
supports: svg_drawingml
outputs: svg_layout, versus_duel_structure
depends_on: contract-layout-density.md, contract-visual-token-core.md
relation_specs: pairs_with:content-comparison, pairs_with:theme-violet-business, conflicts_with:layout-mirror-compare
triggers: VS 对决, 对碰对比, 甲方乙方, 我方竞品, 目标与达成, 本期与上期, 自研与采购, versus, duel, head to head, this vs that
max_use: 只讲两个对象的对决式对碰；同一主体正反两面复盘改读 layout-mirror-compare.md
source_notice: 参考公开职场汇报模板的结构组织方式，已抽象为本项目可复制方法；原作固定话术、示例文案、品牌水印一律作为分析输入后丢弃，不入语料。
-->

# Layout: Versus Duel（VS 对决对比）

## 适用判断

- use_when：两个对象或两个时点的对碰——目标 vs 达成、本期 vs 上期、我方 vs 竞品、自研 vs 采购，需要"对决"张力并给一句选择结论。
- avoid_when：
  - 同一主体两面复盘改用 `layout-mirror-compare.md`（自我亮点/短板镜像，非两个对象 PK）；
  - 任一侧指标 >5 个（拆页或改原生表格）；
  - 需要连续刻度/趋势对比改读 `chart-bar-comparison.md` / `chart-line-trend.md`；
  - 只并列两组要点、无"谁更优"判断，改用四卡/多卡网格。

## 页面结构（画法与比例逻辑）

- 中心一枚 VS 圆牌（circle + 粗体"VS"），左右各一条相向对冲箭头带：左"甲方"右指、右"乙方"左指，两条 chevron 相向逼近圆牌。
- 每条箭头带内嵌 3–5 个指标行（"标签 + 值"，值右对齐同基准线），带头留出圆牌间距。
- 下方双列要点分析：左列讲甲方优势、右列讲乙方顾虑，各 2–3 项，chevron 或圆点引导、粗体引导词起头。
- 底部一条结语块，一句判断收口（给一句可执行结论）。
- 比例：箭头带 tip 与 VS 圆牌半径留 ≥ 一个字距间隙；带内指标行等距，标签左对齐、值右对齐到带内右安全线。

## 容量

- 每侧 3–5 指标：标签 ≤5 字，值 ≤7 字符（含单位）。
- 双列分析每侧 2–3 项：粗体引导 ≤8 字，正文 ≤40 字。
- VS 圆牌只写"VS"不加副字；结语 ≤80 字。
- 超载先合并弱指标或减项，不缩字号硬塞；指标必须真实，不为对称编造。

## 配色语义（不内联 hex）

- 两条箭头带用同一主题的深/浅两档区分甲乙，色值引用 `theme-violet-business`，本颗粒不写死 hex。
- VS 圆牌用最深主色压场，结语块深色反白收口；渐变只做带内明暗过渡，不做撞色。

## 渲染原语

- 对冲箭头带 = `polygon`（相向 chevron）；带内明暗 = `linearGradient`；VS 圆牌 = `circle` + `text`；分析项引导 = 小 `polygon` chevron 或圆点。
- 禁斜面高光（伪 3D，转换器不支持）；VS 圆牌等徽标类强调元素可选叠加单个外发光/投影 `filter`（仅 `feGaussianBlur`，可选 `feOffset`），箭头带、渐变带等大面积装饰仍不叠加滤镜以保持克制；渐变只用 `linearGradient` / `radialGradient`。

## 金标示例

- 路径：`assets/examples/svg-ppt/decks/scenario-report-structure-gold-pages/03-versus-duel.svg`
- 调用：`load_skill_example(path="assets/examples/svg-ppt/decks/scenario-report-structure-gold-pages/03-versus-duel.svg")`
- 只参考 VS 圆牌 + 对冲箭头带 + 双列分析 + 结语的组织与信息层级；不要照抄坐标或把示例占位数据当业务事实。
- 勿照抄首行整页背景 `<rect>`：那只是离线预览底色，运行时背景由 `deck_framework.background` 承载，内容层画满页背景会触发 `SVG_FULL_PAGE_BACKGROUND_FORBIDDEN`。

## 反模式

- 把同一主体正反复盘硬塞成 VS（应走 mirror-compare）；一侧指标堆到 6+ 挤爆箭头带。
- VS 圆牌加副标题；结语写成长段落；箭头带做斜面高光或叠加发光/两侧撞色抢焦点（箭头带保持克制，VS 圆牌本身的单发光强调见渲染降级纪律，不算此反模式）。
