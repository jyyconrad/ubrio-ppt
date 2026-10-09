<!--
id: content-title-rewriting
category: content-structure
read_when: 标题是名词、口号或过短标签，需要改成判断句
page_roles: content, summary
supports: svg_drawingml
outputs: title_patterns
depends_on: contract-content-density.md
max_use: 只读取本文件，不要连带读取同类全部文件
-->

# Content: Title Rewriting

## 内容说明

标题要表达判断，不只写名词。保留事实口径，不夸大。

改写例：

- “销售增长” -> “重点客户带动销售逆势增长”
- “项目风险” -> “数据口径与资源排期是当前主要风险”
- “产品能力” -> “三项能力重构端到端协同体验”
- “落实机制” -> “建立责任闭环，确保学习成果转化为岗位实践”

## 视觉说明

主标题 `36-46px`，可断成两行，但不要被章节号、页码或标签压过。

## SVG说明

标题必须在 `main-title` 中作为 `<text>` 保留；副标题或解释放 `subtitle`。
