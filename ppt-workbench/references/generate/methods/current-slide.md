# L2 当前页表达与质量

## 最小阅读

1. 必读：[页面表达](../original/slide-generation-core/references/page-expression.md)。
2. 必读：[当前页质量范围](../original/slide-generation-core/references/current-slide-quality-scope.md)。

按需追加：

- 需要对象拆分时：[版面建模](../original/slide-generation-core/references/layout-modeling.md)。
- 需要理解历史 SVG 提交门时：[预渲染门](../original/slide-generation-core/references/pre-render-gate.md)。它不是原生 PptxGenJS 页面的必读依赖。

## 使用判断

- 先确定当前页唯一主判断，再选择证据和结构。
- 普通独立技能任务不要求 Ubrio workspace、阶段状态或 Turbo 账本；原文中的这些运行时描述只作历史背景。
- `pre-render-gate.md` 对 `slide-authoring:drawingml-svg-authoring` 和 `slide-authoring:svg-self-qa` 的引用，在包内分别对应 [DrawingML SVG](../original/slide-authoring/references/drawingml-svg-authoring.md) 与 [SVG 自检](../original/slide-authoring/references/contract-svg-self-qa.md)。

## 状态

- 原文：已完整收录、可直接阅读。
- 原生 PPTX：由活动 PptxGenJS 组件承担；固定合成样例 smoke 已存在，但不代表模型质量或 PowerPoint 验证。
- Turbo 和 Ubrio 阶段推进：未移植，也不是独立技能要求。
