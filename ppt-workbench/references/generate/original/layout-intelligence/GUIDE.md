---
name: layout-intelligence
description: Use in outline and slide_generation to identify page role and business pattern, evaluate code-provided layout candidates, choose a validated catalog variant or design an explicit custom composition, fill within capacity, and fall back or split pages when blocked. Disambiguate analysis frameworks and never impersonate a catalog layout id.
enabled: true
stage: outline, slide_generation
runtime_scope: mainline
skill_kind: method
---

# 版式智能（Layout Intelligence）

本 Skill 是**选版方法**语料：教你把当前页从"要证明的业务判断"稳定收窄到"用哪种信息结构/版式"，并按 slot 与容量填充。它按需检索进入上下文，只承载可复制方法，不承载版式库全文、主题 token 表或坐标。

它与写作/落版分工明确：本 Skill 负责**选** role → pattern → composition → variant；`slide-authoring` 负责把选定结构手写成可编辑 SVG；`content-writing` 负责 claim/evidence/action 等业务内容槽。三者配合，不互相替代。

## 选版方法骨架

```text
识别业务问题
  → 确认 page role（业务职责，20 类稳定角色）
  → 选择 business pattern（分析/论证模型，可多候选、可留空）
  → 核对 data / evidence shape（证据结构是否达标）
  → 评估系统返回的 composition / layout shortlist（高置信候选，不是固定答案）
  → 采用可验证 catalog variant，或声明 custom composition
  → 按已声明合同 / 通用可读性与容量规则填充
  → blocking 时压缩 / 换结构 / 拆页 / 询问用户
```

完整六步与路由指纹清单读 `references/layout-routing-method.md`。

## 消费系统注入的路由信息

当前页任务包里可能带有系统按代码算好的**路由指纹**和**候选版式（shortlist：一个主推荐 + 2~4 个备选）**。它们是高置信能力候选，不是固定模板答案：先核对表达主轴、证据结构、容量与主题；适配就采用其中一个 catalog variant，不适配就按需加载方法、example 和验证支持，设计 `custom_composition`。不要自己猜不存在的 layout id，也不要把自定义结构冒充成某个目录版式。

role/pattern 与业务语义不符时，可带更准确的判断让系统重算候选。最终用 `layout_decision.v1` 声明实际选择：目录版式填真实 `layout_id`，自定义结构不填 `layout_id`，只写结构摘要、理由和引用的参考。代码负责校验、落账和 renderer/QA 闭环。

## 质量覆盖路由

按当前页缺口选读 reference（每次挑最相关的 1~2 个，不贪多）：

- 选版方法骨架与 shortlist 消费纪律 → `references/layout-routing-method.md`
- shortlist 不适配时如何声明自定义结构、避免冒用目录合同 → `references/layout-decision-and-custom-composition.md`
- 判断当前页属于哪类角色、区分相邻角色、分离视觉形态 → `references/page-role-disambiguation.md`
- 选具体业务模型、区分 SWOT/PESTEL/五力、桑基/漏斗/树状图 → `references/business-pattern-selection.md`
- 装不下时的压缩/换结构/拆页/询问决策 → `references/capacity-and-fallback.md`
- 主题与结构正交、极性硬约束、一册一主色 → `references/theme-structure-separation.md`
- 证据型版式的证据合同与缺口动作 → `references/evidence-layout-contract.md`
- "只看标题就套版式"的纠偏 → `references/anti-pattern-layout-by-title-only.md`

## 边界（本 Skill 不写什么）

- 不列 80 个 layout id 清单，不背具体版式库；具体候选由系统 shortlist 返回。
- 不写 12 套主题的完整 token 表、不写具体坐标；主题 token 真源在 style manifest 与 renderer，几何在 builder。
- 不承载 renderer 内部实现与 slot 合同全文；选中版式的 slot/容量合同由代码解析后随任务包给出。
- 不把 shortlist 当唯一答案，也不把 custom composition 固化为另一套模板；Skill 只给判断方法、example 与失败检查。
- 不做运行时事实声明（如"某工具此刻一定可调""渲染后一定弹某卡片"）；运行时真源以阶段状态机、工具返回和阶段执行合同为准，本 Skill 只写方法。

## Outline 阶段的用法

大纲阶段可用同一套判别为每页标注稳定 `page_role`、可识别时给 `business_pattern` 候选、给 data/evidence 提示，但**不选具体 layout**——过早锁版式会限制后续按容量与证据优化的空间。判别方法同 `page-role-disambiguation.md` 与 `business-pattern-selection.md`。
