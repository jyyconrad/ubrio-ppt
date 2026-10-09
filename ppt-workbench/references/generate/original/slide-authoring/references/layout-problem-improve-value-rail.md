<!--
id: layout-problem-improve-value-rail
category: layout
read_when: 问题域与改进域内部结构不同、条数可不等的复盘整改页，非对称双撞色大面板承载"存在问题+改进举措"，最右加窄价值轨收束
page_roles: content, summary
supports: svg_drawingml
outputs: svg_layout, problem_improve_value_rail_structure
depends_on: contract-layout-density.md, contract-visual-token-core.md
relation_specs: pairs_with:theme-blue-green-duotone, conflicts_with:layout-problem-solution-benefit, conflicts_with:layout-problem-improve-bilateral
triggers: 不足与改进, 存在问题, 改进措施, 价值收益, 价值轨, 整改承诺, 非对称双面板, 撞色面板, 问题改进价值, problem improve value, value rail
max_use: 只讲非对称双撞色面板+价值轨；三等列因果读 layout-problem-solution-benefit.md，对称转化锚读 layout-problem-improve-bilateral.md
source_notice: 参考公开职场汇报模板的结构组织方式，已抽象为本项目可复制方法；原作固定话术、示例文案、品牌水印一律作为分析输入后丢弃，不入语料。
-->

# Layout: Problem-Improve Value Rail（问题-改进-价值 非对称双面板+价值轨）

## 适用判断

- use_when：问题域与改进域**内部结构不同**——问题=平铺警示列表、改进=编号+子 bullet 措施块，两域条数可不等；最右加窄价值轨收束成效，整体呈"两大撞色面板 + 价值边轨"的非对称排布。
- avoid_when：
  - 问题→方案→收益**三等宽列因果推进**（每段等权、配因果箭头）→ `layout-problem-solution-benefit.md`；
  - 问题↔改进**一一对应对称转化**（中央维恩/循环锚、左 i 右 i 同基线）→ `layout-problem-improve-bilateral.md`；
  - 同一主体量化正反镜像 → `layout-mirror-compare.md`。
- 判据：两域**不对齐、不等数、结构相异**，第三段是轻量价值轨而非对等第三列，才选本颗粒。

## 页面结构（画法与比例逻辑）

- 三段非对称、宽度递减：问题面板 < 改进面板（略宽）> 价值轨（最右、窄，≈单面板宽 0.3），非三等列。
- 段1 问题面板：辅色实底大圆角面板，斜切题条压左上角（略越界）；面内 N 条=白底方标（✗/! 几何徽标）+加粗标题+说明，纯平铺、无编号。
- 段2 改进面板：主色实底大圆角面板，顶部区块头+分隔线；面内 M 条=▶ 方向三角 + No. 编号 + 标题 + 2 子 bullet。
- 段3 价值轨：恰 3 张白卡竖排贴右缘，卡内 ▲ + 两行价值断言；白底主色字、中性，不参与撞色对抗。
- 段间方向标（问题→改进、改进→价值）各一组小箭头表流向、不塞正文；底部主色收束条承载整改承诺/下一步。

## 容量

- 问题 N=3~4；改进 M=3~5；价值恰 3 卡（多/少于 3 改用其它结构）。
- 问题：标题 ≤16 字、说明 ≤34 字且 ≤2 行；改进：标题 ≤12 字、每子 bullet ≤26 字；价值卡每行 ≤8 字、恰 2 行。
- 超载先砍最弱一条或合并子 bullet，不缩字号硬塞、不编造条目凑数。

## 配色语义（双色分工，不内联 hex）

- 问题面板=主题辅色（绿，负面/症结）、改进面板=主题主色（蓝，正面/举措）、价值轨=白底主色字（中性）；色值引用 `theme-blue-green-duotone`。
- 深色实底面板文字/徽标一律浅色反白、**禁黑字**；撞色用实底 fill，不用半透明假装分区。
- ✗/!、▶、▲ 徽标用 `line`/`polygon` 几何图形，禁手绘象形与 `filter`/`blur`/`mask`。

## 金标示例

- 调用：`load_skill_example(path="assets/examples/svg-ppt/decks/scenario-effects-structure-gold-pages/06-problem-improve-value-rail.svg")`
- 只参考三段非对称分区、问题平铺 vs 改进编号的结构差异、价值轨与方向标；勿照抄坐标或占位数据。
- 勿照抄首行整页背景 `<rect>`：那只是离线预览底色，运行时背景由 `deck_framework.background` 承载，内容层画满页背景会触发 `SVG_FULL_PAGE_BACKGROUND_FORBIDDEN`。

## 反模式

- 价值轨做成第 4 个对等大面板；深色面板留黑字；方向标塞文字；价值卡≠3；问题域强行编号凑对称。
