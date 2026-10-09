<!--
id: theme-structure-separation
category: capability
stage: slide_generation
read_when: 避免用主题名(深色商务/科技风)去选版式、把同一结构按主题复制成多份、或忽略主题极性(深色禁浅底)硬约束；理解主题与信息结构正交
page_roles: content, summary
supports: svg_drawingml
outputs: theme_structure_orthogonality, polarity_contract
relation_specs: pairs_with:layout-routing-method, pairs_with:theme-background-policy, pairs_with:contract-visual-token-core
max_use: 只讲主题与结构分轴及极性合同边界；主题 token 与背景机制读 theme-background-policy / contract-visual-token-core
-->

# 主题与结构正交

主题（`theme_family`：色彩 token、极性、密度、字体、图表色序）与信息结构（`composition_family` / `layout`）是**两条正交的轴**。一个不该决定另一个。

## 核心原则

- **不要用主题名选版式**："深色商务风""科技风"是主题，不是结构。同一个 2×2 矩阵在浅色蓝、深色简报、瑞士信息设计主题下都成立，通过"结构 × 主题兼容"组合，不为每个主题复制一份业务合同。
- **主题不是版式的父目录**：换主题 = 换配套色板与极性，不是换一套新版式。选版式看的是 role/pattern/data_shape/容量，主题只在最后决定这套结构穿什么"皮"。
- **只有主题真正改变结构时**，才新增该主题专属变体；否则同结构复用。

## 极性是硬约束

主题极性（深/浅）是渲染期硬门禁，不是建议：

- 深色主题 → 禁浅底、禁黑字；浅色主题 → 禁深底浅灰正文。极性由代码在渲染期自动提取并阻断漂移，你**声明意图、不与它对抗**：选的结构和配色要和已定主题极性一致，冲突时改配色不是改门禁。
- 用背景图的 deck 先定全册默认背景（全局机制），再谈逐页 override；"换全局背景"要连带"换配套色板"，palette 与背景同轮敲定、互相校验。

## 一册一主色

- 全 deck 一个主色（真源在 `style_manifest.palette`），功能辅助色只作语义标记（正负/风险/状态），并列同级模块**默认同色**，禁逐卡换色相（彩虹排布，见 `anti-pattern-rainbow-parallel-modules`）。
- 主题 token 的运行时真源在 style manifest 与 renderer，**不在 layout**。选版式时不搬 token 表、不写具体色值坐标；把配色一致性交给 visual token 合同（见 `contract-visual-token-core`）。

## 失败信号

- 因为"这是深色科技风"就默认选某种炫酷版式，跳过 role/pattern 判断。
- 把同一信息结构按 12 套主题复制成 12 份近似合同。
- 选的结构/配色与已定主题极性冲突，靠改极性门禁而不是改配色来"通过"。
