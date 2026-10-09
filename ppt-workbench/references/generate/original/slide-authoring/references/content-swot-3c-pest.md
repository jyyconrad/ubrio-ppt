<!--
id: content-swot-3c-pest
category: content-structure
read_when: SWOT、3C、PEST 分析或宏观/市场/竞品判断
page_roles: content
supports: svg_drawingml
outputs: content_slots
depends_on: layout-matrix-quadrant.md
max_use: 只读取本文件，不要连带读取同类全部文件
-->

# Content: SWOT / 3C / PEST

## 内容说明

- SWOT：优势、劣势、机会、威胁，每象限 2-3 条。
- 3C：Customer、Company、Competitor，每列写需求、我方能力、竞品差异。
- PEST：政策、经济、社会、技术，每块写趋势、影响、动作。

每块必须有事实或推理，不只写名词。

## 视觉说明

SWOT 适合四象限；3C 适合三列；PEST 适合四卡或矩阵。重点结论放顶部或右侧说明。

## 维度卡（影响+动作槽）布局合同

当模型是「若干**具名维度**、每维度都要给影响与行动」时（PEST/PESTEL、波特五力、价值链等
`categorical_dimensions` 结构），用**维度卡网格**，而不是通用 icon_grid（图标+标签+描述）——
后者没有结构化的影响/行动槽，会把分析退化成图标海报。每张卡固定三槽：

- **维度名**：该维度的名字（如「政策」「新进入者威胁」），≤ 8 个中文字符。
- **现状/影响**：这一维度当前的态势与对我方的影响，1-2 句、给事实或推理，不只写名词。
- **动作/启示**：据此该做什么或该警惕什么，1 句可执行结论。

容量与拆分：

- 一页承载 **4~6 张维度卡**（PESTEL 4 必填「政策/经济/社会/技术」+ 可选「环境/法律」共 6；
  五力固定 5「现有竞争/新进入者/替代品/买方议价/供方议价」；价值链 5 环节）。
- 超过 6 个维度、或某维度影响+动作超过 3 行时，**拆页或按维度分组**，不要压字号硬塞。
- 卡片信息密度要接近，禁止某张卡只有维度名而无影响/动作（空卡见 `anti-pattern-empty-cards.md`）。
- 五力有中心-辐射诉求时改读 `layout-center-radial.md`；只是并列展示则维度卡即可。

顶部写一句总判断（如「政策与技术双重利好、竞争结构趋紧」），维度卡网格占主体，底部或右侧
`insight-bar` 收束成整体行动。缺数据时标注判断边界，不编造硬指标。

## SVG说明

分组：`quadrant-1..4`、`customer/company/competitor`，或维度卡的
`dimension-card-1..6`（每卡含 `dim-name/dim-impact/dim-action` 三个子槽），来源放入 `source-note`。
