<!--
id: layout-retrospect-outlook-pyramid
category: layout
module_type: layout_family
read_when: 三时段叙事栏（回顾-成果-展望）+ 中央递进金字塔串联；金字塔是中央递进装置，非静态层级主体
page_roles: content, summary
stage_tags: slide_generation
supports: svg_drawingml
outputs: svg_layout, retrospect_outlook_pyramid_structure
depends_on: contract-layout-density.md, contract-visual-token-core.md
relation_specs: requires:contract-visual-token-core, conflicts_with:layout-pyramid-hierarchy, pairs_with:svg-shape-3d-isometric
triggers: 回顾成果展望三栏, 复盘成果规划三段, 过去现在未来三栏, 中央金字塔串起三段, 递进金字塔配三栏叙事, 三时段递进金字塔, retro outcome outlook pyramid, 回顾展望, 复盘展望
max_use: 只讲三时段叙事 + 中央递进金字塔串联；静态层级支撑主体读 layout-pyramid-hierarchy.md，向下收窄流失读 layout-funnel-stage-stack.md
source_notice: 参考公开职场汇报模板的结构组织方式与配色体系，已抽象为本项目可复制方法；原作固定话术、示例文案、品牌水印一律作为分析输入后丢弃，不入语料。
-->

# Layout: Retrospect Outlook Pyramid（回顾-成果-展望 + 中央递进金字塔）

## 适用判断

- use_when：一页讲**三个时段的叙事**——回顾（过去积累）→ 成果（当期跃升）→ 展望（未来规划），并用一座**中央递进金字塔**把三段串成"层层垫高"的因果线。金字塔是串联三段的**递进装置**，三栏才是详情主体。
- avoid_when：
  - 金字塔是**静态层级支撑主体**（顶层目标 / 中层抓手 / 底层证据，非时段递进）→ `layout-pyramid-hierarchy.md`；
  - **向下收窄 / 逐层流失**的转化漏斗 → `layout-funnel-stage-stack.md`；
  - 只有两段（现状 vs 目标）无中央装置 → `layout-diagonal-duo-panels.md`。
- **一句判据**："三段是否按时间递进、金字塔是否只做串联而详情在栏里"——是则本颗粒，否则回 pyramid-hierarchy。

## 骨架（画法与比例逻辑）

- 顶部 14-18% 标题带：观点标题 +（可选）年度 / 周期徽标。
- 主体两种排布择一：**上金字塔 + 下三栏**（中上部金字塔占中 `cx≈640`，下方三等宽栏平铺三段）；或**中央金字塔 + 左右两栏**（金字塔占中做脊柱，两侧挂时段栏，第三段做中央收口条）。
- 中央金字塔 **3 层递进**，自下而上对应**回顾（底，最宽）→ 成果（中）→ 展望（顶，最窄）**；层内只放层标签 ≤6 字，详情落三栏。
- 立体版读 `svg-shape-3d-isometric` **骨架 2（分层立体金字塔）**：3 个等距立方从底到顶堆叠、越往上越窄，从底层向顶层顺序绘制（画家算法），三面各一条 `linearGradient`（顶面受光最亮 / 左面中间调 / 右面背光最暗），**转换后落 freeform + gradFill，保持可编辑**。
- 三栏各自：圆形编号徽标（时段色档实心圆 + 反白序号）+ 时段标题 ≤8 字（标题文字用同一时段色档）+ 2-3 条要点 ≤22 字（≤1 行）；栏体本身白底细描边，不叠加左侧/顶部装饰色条，时段区分靠徽标和标题的明度档差，色档取自主色系分层（见下节），不逐栏换色相。

## 容量

- 恰 **3 段 / 3 栏 / 金字塔 3 层**；层多于 3 先并为回顾 / 成果 / 展望三类，不切薄片。
- 三栏标题 ≤8 字、每栏要点 2-3 条每条 ≤22 字；金字塔层标签 ≤6 字。
- 金字塔内不塞长文本、证据、来源；块面标签 ≤6 字，其余移三栏。每页 ≤1 座金字塔。

## 配色（时段主色内分层 + 金字塔单色递进）

- 三栏时段区分**默认走主色系内明度分层**：回顾用中性 / 主色暗档（过去、根基），成果用 `accent`（当期高光），展望用主色亮档或中性反衬（未来、蓄势）。时段递进不算语义对立，不为它引入新色相；只有 deck 配额内已存在的功能色（如风险 / 正负）恰好与时段语义重合时才可复用。引 theme token，不内联死 hex，全册非中性色相总数仍受 deck 级配额（≤3）约束。
- 中央金字塔**单色系递进渐变**（自底向顶同色加深或提亮方向一致），表"层层垫高、同一条主线递进"；**禁三层三色**（会读成并列分类而非递进）。
- 每个 `<text>` 显式 `fill` / `font-family` / `font-size`；金字塔层标签反白居中。

## 金字塔画法纪律

- 金字塔主体必须是**闭合 `<polygon>`**（立体版为多面 polygon 拼接），转换后成可编辑 freeform。
- **禁三层矩形卡片冒充金字塔**；**禁真透视 / 斜切 / filter 硬凑立体**（转换会失败或被拒），只做等距平面拼接。

## 金标示例

- 路径：`assets/examples/svg-ppt/decks/scenario-composite-structure-gold-pages/04-retrospect-outlook-pyramid.svg`
- 调用：`load_skill_example(path="assets/examples/svg-ppt/decks/scenario-composite-structure-gold-pages/04-retrospect-outlook-pyramid.svg")`
- 只参考中央三层立体金字塔（回顾 / 成果 / 展望层标签）串联下方三栏叙事、三面明暗与单色递进的组织；不要照抄坐标或把占位数据当业务事实，也勿照抄首行整页背景 `<rect>`（离线底色，运行时触发 `SVG_FULL_PAGE_BACKGROUND_FORBIDDEN`）。

## 反模式

- 金字塔当静态层级主体、三栏沦为附注（该读 pyramid-hierarchy）；金字塔做成向下收窄漏斗（该读 funnel-stage-stack）。
- 三层矩形冒充金字塔 / 真透视立体；金字塔三层三色丢失递进语义；层内塞长文本；三栏时序错乱（非回顾→成果→展望）。
