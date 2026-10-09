# 金标单页路径

Ubrio `validate-gold-page-spec` / `build-gold-svg-page` 在本技能就是下面的本地 CLI。不要把 `contract-gold-svg-builder.md` 里的 resource ID 当可执行入口。

中文业务正文页默认走这条路径。没有 `source.svg` 的中文业务正文页不能标为金标完成。`scripts/native.cjs` 只在 SVG→PPTX 不可用时 fallback。

## 命令

先 `page_spec.json`，再校验，ready 后才写 `source.svg`。有原生槽位时，`--output source.svg` 同时写出同目录 `native-data.json`；没有槽位时，转换命令省略 `--native-data`。

```bash
python3 scripts/svg/build_gold_svg_page.py \
  --spec page_spec.json --validate-only \
  --write-normalized page_spec.normalized.json \
  --write-repair-patch patch.json \
  --write-fill-plan page_spec.fill_plan.json

python3 scripts/svg/build_gold_svg_page.py \
  --spec page_spec.json --output source.svg \
  --write-normalized page_spec.normalized.json
```

质量状态不是 `ready` 时先按报告补证据、结构、Owner、行动或来源，不得直接 `--output`。
`ready` 只表示结构化字段达到脚本目标；仍需通过 [内容与视觉质量门](../../content-visual-quality-gates.md) 的主观点、人话、证据边界和表格语义检查。

## 无指标的左右对照页

当正文比较两种判断或推进方法，使用 `layout: gold_comparison`。`dominant: 左右对照` 配合默认 `gold_cards` 也会路由到此布局。它直接生成两块连续 `comparison-panel`，每块承载判断、证据和动作，底部共享限制与下一步；不需要为了校验补三张 KPI 或状态卡。

下面是可直接保存为 `page_spec.json` 的合成示例。只迁移字段和信息关系，替换业务内容及来源；叙事判断仍按 [调研和规范怎么写](../../outline/narrative-shape.md#调研和规范怎么写)。

```json
{
  "layout": "gold_comparison",
  "page_role": "content",
  "dominant": "左右对照",
  "theme_id": "business_blue",
  "title": "先添设备还是先调排程，要先查清订单等在哪",
  "primary_claim": "先添设备还是先调排程，要先查清订单等在哪",
  "key_message": "两种做法针对的等待环节不同，先核对一张订单的记录。",
  "audience_takeaway": "生产和计划团队先补齐同一张订单的记录，本次不决定采购。",
  "plain_language_who_scene_problem_action": {
    "who": "生产和计划团队",
    "scene": "讨论订单等待问题",
    "problem": "还没有逐段等待记录，无法判断设备是否不足",
    "action": "先核对同一张订单的等待记录，负责人和时间后续确认"
  },
  "claim_type": "proposal",
  "evidence_state": "PROPOSAL",
  "metrics": [],
  "groups": [
    {
      "title": "先添设备",
      "claim": "建议先核对设备负荷，再评估是否增加产能。",
      "evidence": ["假设：订单主要等在同一台设备前。", "缺口：尚无逐段等待记录，采购成本待询价。"],
      "action": "核对设备前后的等待记录，再讨论采购。",
      "role": "support"
    },
    {
      "title": "先调排程",
      "claim": "建议先核对任务衔接，再评估排程能否减少等待。",
      "evidence": ["假设：订单主要等在任务交接之间。", "缺口：尚无排程对照样本，调整成本待评估。"],
      "action": "核对交接前后的等待记录，再讨论试排。",
      "role": "support"
    }
  ],
  "boundary": "两种做法均为建议，没有实测基线或收益结论。",
  "action": "生产和计划团队先补一张订单的记录，本次不决定采购。",
  "typography": {"body_px": 22, "title_px": 32, "source_px": 11, "font_family": "Noto Sans CJK SC"},
  "sources": ["合成教学示例；不代表任何企业的实际情况"],
  "example_refs": [{
    "example_id": "gold-comparison-text",
    "source": "references/generate/methods/gold-pages.md#无指标的左右对照页",
    "reuse_reason": "复用两块连续面板与共享限制、行动的关系。",
    "adaptations": ["替换方案、证据边界和来源，保留单一主观点。"]
  }]
}
```

按上面的 validate-only、build 命令生成，再执行：

```bash
python3 scripts/svg/check_shape_picture.py --dominant 左右对照 --svg source.svg
python3 scripts/svg/validate_svg_drawingml.py --svg source.svg --mode full
python3 scripts/svg/render_svg_drawingml.py --svg source.svg --output page.pptx
python3 scripts/inspect_pptx.py page.pptx
```

这一路径处理两组文字对照；图表、图片和明细槽位走各自现有布局。`boundary` 和 `action` 分别进入共享限制、下一步；`attached` 是叙事挂载说明，不能代替这两个可见内容字段。每组 `explanation/implication/risk` 若有正文，会保留到证据列表一起核验容量。内容超限时先合并表达或调整页数，不能截掉后半句或缩小字号；具体修复位置由 `missing` 返回。其他正文布局确实没有数值指标时，可显式设置 `quality_targets.metrics_min: 0`，已有指标仍接受完整的来源检查。

示例使用 Noto Sans CJK SC；执行时按用户字体合同及已安装字体设置 `typography.font_family`，它会进入 SVG 和可编辑 PPTX。未设置时沿用既有默认字体。预览出现字体替换时，按 [预览路线](../preview-options.md) 核对实际字体并处理环境。

生成器已检查两块面板各有正文且实际左右排列；这只证明形状合同。最后一次修改后，对最终 PPTX 重新做对象检查，并按 [预览路线](../preview-options.md) 渲染、读图。没有实际运行 deck validator 时不自填其 `*_passed` 字段；LibreOffice 预览与 PowerPoint 编辑往返分别报告。

## 当前页结构参考（按路径加载）

加载 skill-graph 的 always_read / default_gold_path 之后，按路径打开，不要当目录列表已读：

- [金标页型](../original/slide-authoring/references/gold-page-patterns.md)
- [结构层级](../original/slide-authoring/references/contract-structure-hierarchy.md)
- 对应 `scenario-*-gold-pages` SVG（chart-type / report-structure / government-briefing 等）

示例从 [workbench 金标目录](../gold-examples-catalog.json) 与 SHA-frozen `examples-manifest.json` 的 `gold_examples` 合并读取。`scenario-government-briefing-gold-pages` 只登记在 workbench catalog，不要改原始 manifest。打开 SVG 只抄层级和密度，不抄 x/y，也不照抄整页预览 rect。

## 产物与槽位

| 文件 | 内容 |
| --- | --- |
| `page_spec.json` | 标题、`primary_claim`、key_message、`proves`、`dominant`、`attached`、`claim_type`/`evidence_type`/`evidence_state`、`skeleton_id`/`same_skeleton_run`、`visual_brief`、structure_hierarchy、2–3 个支撑点、metrics、groups/rows/steps、证据边界、来源、`example_refs`/`not_reused_reason` |
| `source.svg` | 1280×720 内容层；slot 组内只留外框；标题在上、来源/洞察在下 |
| `native-data.json` | `charts[]` / `tables[]` / `images[]`，`slot_id` 对 SVG `id`；图标不进此文件。证据截图只有本地 `asset_key` 时才写 `native-image-slot`，见 [图片三个 owner](image-owners.md) |

图表/表格槽的预检与叠加（Ubrio `validate_svg_drawingml` / `render_svg_drawingml_slide` 在本技能就是下面的 CLI；overlay 由 render 调用）：

```bash
python3 scripts/svg/validate_svg_drawingml.py --svg source.svg --mode full
python3 scripts/svg/render_svg_drawingml.py \
  --svg source.svg --native-data native-data.json --output page.pptx

python3 scripts/svg/overlay_native_slots.py \
  --svg source.svg --native-data native-data.json --validate-only
```

禁止：图表数据写进 SVG 属性、整页预览底色 rect、标题/来源写进 slot 分组、`charts[].kind` 写成 combo/sankey/bubble，或用多个 `rect`/`text` 绘制假的表格数据。雷达的同量尺数据与系列要求见[原生图表与表格槽](native-components.md)。图标走 [图标嵌入](icon-embed.md)：`search_icons.py` → `data-icon-id`，不要 `search_svg_icons`。金标 `evidence_asset_slots` 有本地 `asset_key` 时写成 `native-image-slot`，没有本地文件就跳过，不要 `evidence-asset-slot` 或 SVG `<image href>`。
