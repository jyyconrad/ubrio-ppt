# 本地 skill-graph 路由

宿主没有 `search_knowledge_base` / `load_skill_references` / `load_skill_example` 时，用本技能脚本完成同一套 search → load → example。不要把检索命中、目录列表或兼容索引当成已加载正文。

## 两份名单

| 名单 | 含义 | 来源 |
| --- | --- | --- |
| candidates | 只知道 id，还没有正文 | `search_modules.py` 的 `candidate_module_ids` |
| loaded | 正文已在当前页上下文 | `load_modules.py` 返回且带 `content` 的 `loaded_module_ids` |

`deferred_module_ids`、`example_refs`、能力图链接、`chinese-business-ppt-authoring.md` 和 `routing-examples.md` 都不是 loaded。

## 当前页步骤

1. 写下本页 `page_role`（cover / agenda / content / section_divider / summary / closing）。多页时每页单独传，不复用第 1 页角色。
2. 只针对一个缺口维度检索：`layout` | `theme` | `qa` | `content` | `contract`。返回只有 `module_id`、`title`、1–2 句 `excerpt`、`why_matched`，没有正文。

```bash
python3 scripts/skill_graph/search_modules.py \
  --query "渠道转化排名柱状图" --page-role content --dimension layout --top-k 3
```

3. 用命中的 id 一次加载。主模块 ≤4；未解析的 id 再搜，不要猜名字。load 总是注入 capability-tree 的 `always_read`（`drawingml-svg-authoring-core`、`contract-visual-token-core`）和 `default_gold_path`（`contract-gold-svg-builder`、`contract-structure-hierarchy`），再加上主模块及其 `requires`。不要靠关掉 supporting 来实现“少读一点”。

```bash
python3 scripts/skill_graph/load_modules.py \
  --module-ids chart-bar-comparison,layout-native-chart-slot --page-role content
```

4. 若结果含 `example_refs` 或金标 SVG 路径，按路径只读打开，单份约12KB。一般迁移借用层级和密度，不照抄坐标或事实。用户明确要求原图同版式时，按[逐图复刻](../../blue-dense-report.md#逐图复刻先解释再绑定内容)运行`build_reference_page.py --list/--describe`选择具体构图，再实际打开该原图和相应可编辑示例。此分支由稳定构图保留几何，Agent判断业务问题/文字角色/关系；本地search不索引这些图片，未打开不算使用。

```bash
python3 scripts/skill_graph/load_modules.py \
  --example assets/examples/svg-ppt/decks/scenario-chart-type-gold-pages/01-bar-comparison.svg
```

检索为空且未设严格过滤时，search 只把 `default_gold_path` 标成候选，仍然要 load 才会有正文。金标路径是内容页起手，不能代替已命中的 layout/theme 模块。

## Example-driven 记录

样例检索和用户参考图是页面选择的证据链，不是“看过目录”即可跳过的装饰步骤。每个正文页在 `page_spec.json` 留一条选择记录：

```json
{
  "example_refs": [
    {
      "example_id": "05-table",
      "source": "assets/examples/output/05-table.pptx",
      "reuse_reason": "复用原生单元格、状态列和中文容量",
      "adaptations": ["把项目行换成产品行", "增加证据状态列"],
      "not_reused_reason": null
    }
  ],
  "reference_assets": [],
  "reference_dna": ["标题判断", "证据面板", "关系连接", "底部推论条"]
}
```

`example_id` 只有在实际读取了对应 PPTX/PNG 或金标 SVG 后才算有效；候选 id、目录行和 `example_refs` 搜索结果不等于已加载。`reuse_reason` 写复用的信息关系或对象类型，`adaptations` 写本页如何适配内容、证据状态、数据口径和阅读方向；没有合适样例时必须填写 `not_reused_reason`，不能静默跳过。

参考图只证明可观察的版式DNA，不能证明原PPT对象或客户事实。蓝色高密度任务先按[包内图片选择表](../../blue-dense-report.md#参考范围与选择)选主参考；原图同构按上述分支复用几何，一般迁移按本页内容适配。客户文本、数字、水印或整页底图不进入新稿；只复制颜色而没有层级和关系视为未复用。样例数据只用于用户授权的合成演示，真实材料任务逐项核对来源。

常见任务优先路由：可排序的明细、契约和门禁阈值使用 `05-table` 或 `11-dense`；左右对照的两列判断用 `comparison-panel`，不进表；流程和路线使用 `06-process`；责任链使用 `08-structure`；拍板矩阵使用 `07-matrix`；证据截图使用 `09-evidence`；真实时间序列才使用 `02-trend`/`04-multiseries`；目标/实际比较使用 `03-target`。要求蓝色高密度复盘时，优先从包内图片选择成效看板、诊断链、阶段路线、机制架构或决策矩阵，并打开可编辑 `blue-dense` 示例观察对象层级；现有 `05-table`/`11-dense` 不能单独证明复合结构。每次仍要按当前证据和容量说明适配理由。

## 兜底索引

脚本不可用时，才打开这些索引，然后仍按 id 去 load 2–4 个平铺 reference：

- `_index/capability-tree.json`：看类别和当前 `page_role`，不要当正文
- `chinese-business-ppt-authoring.md`：旧入口缺口表
- `_index/routing-examples.md`：常见问题对照

不要一次读全部 `scenario-*` / `layout-*` / `theme-*`。GUIDE.md 不是每页必装正文。

## 禁止

- 把 GUIDE + 金标合同 + chinese-business 三件套当作每页默认已加载
- 调用宿主 `search_knowledge_base` / `load_skill_references` / `load_skill_example` / `route_skill_references`（本技能不注册它们）
- 把候选 id 或索引表行当成已经读过模块正文
