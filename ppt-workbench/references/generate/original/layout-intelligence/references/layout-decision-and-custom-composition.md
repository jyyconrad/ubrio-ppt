<!--
id: layout-decision-and-custom-composition
category: execution-contract
stage: slide_generation
read_when: shortlist 的候选与当前页真实表达主轴不匹配；需要采用 shortlist 外目录版式；或需要自行设计可执行 composition 并诚实记录实际结构
page_roles: content, summary
supports: svg_drawingml
outputs: layout_decision, custom_composition_contract, recommendation_alignment
relation_specs: pairs_with:layout-routing-method, pairs_with:capacity-and-fallback
max_use: 只讲 Recommendation 与实际 Decision 分离及 custom 身份纪律；具体 SVG 几何和视觉 token 读 slide-authoring 对应合同
-->

# 实际 Layout Decision 与自定义 Composition

Router 的 shortlist 是 `LayoutRecommendation`：它回答“哪些已登记能力大概率适合”。你最终画出的结构是 `LayoutDecision`：它回答“这页实际采用了什么”。二者可以一致，也可以有充分理由地不同。

## 两种合法模式

### `catalog_variant`

当你真实采用某个目录版式的语义骨架与容量合同时使用：

- `layout_id` 填 Provider 可解析的真实 id，不根据名字猜。
- 若在 shortlist 外采用，先确认 renderer route、成熟度、容量和固定页型约束仍可执行。
- 目录只提供能力边界，不要求复制固定坐标；但不能把完全不同的信息结构称为“适配了该版式”。

### `custom_composition`

shortlist 全部不适配、而你能基于 SOP/example 设计出更贴表达主轴的结构时使用：

- `layout_id` 必须为空；引用过的示例放在 `reference_module_ids`，不要冒用目录身份。
- 能可靠归入稳定构图族时填写可选 `composition_family_id`，供相邻页多样性检查；
  无法归类时省略，不根据坐标或卡片数量猜一个族名。
- `structure_summary` 简述真实骨架（如“左侧主判断 + 右侧三条证据链 + 底部行动收口”），不写坐标表。
- `rationale` 说明它如何匹配 role/pattern/data/evidence 与容量。
- 自定义不绕过 fixed page、素材真实性、安全、容量、可读性、renderer 或 QA 门禁。

## 决策顺序

1. 比较 shortlist 与真实表达主轴、证据结构、条目/字符载荷。
2. 有适配 catalog variant 就采用并按合同填充。
3. 不适配时，按需加载相关方法与 example，不扫描整个库。
4. 设计 custom composition，明确结构摘要与理由。
5. 随 `write_svg` 提交 `layout-decision.v1`；validate/render 会复用同一决定做确定性校验与落账。

## Example 与验证支持

- 决策形状示例：`assets/examples/layout-decisions/catalog-and-custom.json`
- 发布/开发时可用 `scripts/validate_layout_decision_example.py` 检查示例形状与真实 Provider 可解析性。

示例只展示“如何诚实声明”，不是推荐三卡、两栏或任何固定构图。
