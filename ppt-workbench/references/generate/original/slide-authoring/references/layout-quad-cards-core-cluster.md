<!--
id: layout-quad-cards-core-cluster
category: layout
read_when: 恰四组要点，中心四词圆簇提炼主线 + 四角详情卡分述（如具体工作/取得成果）
page_roles: content, summary
supports: svg_drawingml
outputs: svg_layout, quad_cards_core_cluster_structure
depends_on: contract-layout-density.md, contract-visual-token-core.md
relation_specs: conflicts_with:layout-center-radial, pairs_with:layout-four-cards-grid, depends_on:contract-layout-density, depends_on:contract-visual-token-core
triggers: 四大亮点, 四大板块, 中心关键词, 四角详情, 圆形关键词, 四位一体, 亮点矩阵, quad cluster, four highlights, 工作亮点, 四个关键词, 具体工作, 取得成果
max_use: 只讲“恰 4 组、中心关键词圆簇+四角详情卡”的组合；纯四卡网格读 layout-four-cards-grid.md，单核放射读 layout-center-radial.md
source_notice: 参考公开职场汇报模板的结构组织方式，已抽象为本项目可复制方法；原作固定话术、示例文案、品牌水印一律作为分析输入后丢弃，不入语料。
-->

# Layout: Quad Cards Core Cluster（四角详情卡 + 中心四圆簇）

## 适用判断

- use_when：**恰 4 组**要点，既要中心四关键词凝练主线（“四位一体”），又要四角各一卡分述细节。卡是主内容、圆是关键词代理。
- avoid_when：纯 4 卡并列无中心提炼 → `layout-four-cards-grid.md`；单中心 + 一圈卫星（中心主、卫星次，主次相反）→ `layout-center-radial.md`；组数 ≠ 4 → 三卡 / 多卡网格 / 拆页，不硬塞第 5 圆。

## 页面结构（画法与比例逻辑）

- 四角各一张等宽等高详情卡，**01 左上、02 左下、03 右上、04 右下**（列优先）；左列右对齐、右列左对齐，让出中央方形空区。
- 中央空区放 **2×2 紧密相切等径同色实心圆簇**（小间隙、非交叠、无中心 hub），簇几何中心 = 页面几何中心。
- 中心向四角射 **4 枚淡色三角楔**（浅色 polygon，apex=中心、底边朝对应角卡）建立圆↔卡配对——非放射连线。
- 角卡 = 角外侧序号徽标 + 标题 + 两带标签信息槽。
- 比例：簇总宽 ≈ 中央空区宽；单圆直径 ≈ 中央空区宽 ×0.42~0.46。

## 容量

- **恰 4 组**；圆内关键词 ≤4 字（2×2 字最稳）+ 英文注 ≤2 词；角卡标题 ≤14 字；每信息槽 ≤44 字且 ≤3 行。超载先压短语或减槽，不缩到不可读、不凑对称编造第 5 组。

## 配色语义（引 theme token，不内联死 hex）

- 4 圆同一主题主色实心同色表“四位一体”，**禁四色分**；楔用主色极浅同色；角卡浅底深字 + 主色实心圆序号徽标（反白数字）+ 浅色细描边；深色圆上关键词反白，圆内只放文字。
- 紫商务引 `theme-violet-business`，蓝绿撞色引 `theme-blue-green-duotone`。

## 中心圆簇 motif（可复制片段）

```
<!-- 中心(640,384)=页面几何中心，r≈中央空区宽×0.44，圆心间距=2r+小间隙；楔先画后被圆/卡盖住仅中央十字可见；等比缩放不背死坐标 -->
<polygon points="640,384 462.8,266.6 430.4,348.4" fill="#E4D9F3"/>
<polygon points="640,384 849.6,348.4 817.2,266.6" fill="#E4D9F3"/>
<polygon points="640,384 430.4,419.6 462.8,501.4" fill="#E4D9F3"/>
<polygon points="640,384 817.2,501.4 849.6,419.6" fill="#E4D9F3"/>
<circle cx="564" cy="308" r="72" fill="#6B2D9C"/>
<circle cx="716" cy="308" r="72" fill="#6B2D9C"/>
<circle cx="564" cy="460" r="72" fill="#6B2D9C"/>
<circle cx="716" cy="460" r="72" fill="#6B2D9C"/>
<text x="564" y="312" fill="#FFFFFF" font-family="Microsoft YaHei, Arial" font-size="30" font-weight="700" text-anchor="middle">提效</text>
<!-- 余 3 圆同法：降本/合规/创新，各配英文小注一行 -->
```

## 金标示例

- `load_skill_example(path="assets/examples/svg-ppt/decks/scenario-effects-structure-gold-pages/05-quad-cards-core-cluster.svg")`
- 只参考分区、蝶形楔配对与信息层级；不照抄坐标或把占位数据当业务事实，也勿照抄首行整页背景 `<rect>`（离线底色，运行时触发 `SVG_FULL_PAGE_BACKGROUND_FORBIDDEN`）。

## 反模式

- 4 圆四种色（丢“四位一体”）；圆当主体、卡沦陪衬（center-radial 反转）；楔成放射连线穿字。
