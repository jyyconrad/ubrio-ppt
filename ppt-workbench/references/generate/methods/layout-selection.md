# L2 版式选择

## 阅读顺序

1. 必读：[版式路由方法](../original/layout-intelligence/references/layout-routing-method.md)。
2. 角色不清时：[页面角色判别](../original/layout-intelligence/references/page-role-disambiguation.md)。
3. 分析模型不清时：[业务模式选择](../original/layout-intelligence/references/business-pattern-selection.md)。
4. 内容过载时：[容量与回退](../original/layout-intelligence/references/capacity-and-fallback.md)。
5. 现成结构不适配时：[自定义组合声明](../original/layout-intelligence/references/layout-decision-and-custom-composition.md)。

## 必要与可选

- 必要：业务判断、证据形态、阅读路径、容量边界。
- 可选：历史 catalog ID、shortlist 和 Ubrio `layout_decision.v1`；独立技能可直接描述结构，不得编造目录 ID。
- 可选：主题参考。主题不能替代结构选择。

## 别名解析

- `layout-density` 和历史文本中的 `contract-layout-density` 均指向 [contract-layout-density.md](../original/slide-authoring/references/contract-layout-density.md)。
- `structure-hierarchy` 指向 [contract-structure-hierarchy.md](../original/slide-authoring/references/contract-structure-hierarchy.md)。
- `content-swot-3c-pest` 指向 [content-swot-3c-pest.md](../original/slide-authoring/references/content-swot-3c-pest.md)。

## 状态

方法可读；依赖数据库或在线 resolver 的 shortlist 生成未移植。独立入口使用本地 Markdown 和文件链接完成选择。
