<!--
id: contract-gold-svg-builder
category: execution-contract
read_when: 每一页可走 SVG DrawingML 时默认读取，用于生成、补充或修正金标单页
page_roles: content, summary
supports: svg_drawingml
outputs: page_spec_template, fill_plan, page_spec_json, normalized_spec_json, quality_report, repair_patch, svg_builder_command
depends_on: drawingml-svg-authoring.md, contract-visual-token.md
max_use: 只读取本文件和一个 layout/scenario reference，不要连带读取全部脚本源码
-->

# Gold SVG Builder Contract

## 核心原则

每一页都按金标页处理，不区分普通和精品。SVG 是内容承载层，只画内容层，不画整页背景；先生成 `page_spec.template.json` 和 `page_spec.fill_plan.json`，再填 `page_spec.json`、校验、补 patch、生成 `source.svg`。

先填 `structure_hierarchy`，再填视觉 token、标题、核心结论、指标、3-5 个内容组或表格/时间线、证据、行动/风险、来源。内容不足时标注证据缺口或口径边界，但不能删除槽位或直接渲染缺口页。

必须先写 `theme_id` 或 `visual_tokens.background/surface/title_text/body_text/source_text/accent/border`：

- `business_blue`：年度总结、经营复盘、通用商务。
- `project_blue`：项目汇报、里程碑、问题闭环。
- `dark_business`：深色强调页，所有正文必须浅色。

`background` 是框架层背景 token；builder 默认不输出整页背景 rect、页眉、章节胶囊、页码、侧边框、贴边竖条或整页外框。

## 声明资源

运行时只调用`resources.json`声明的`validate-gold-page-spec`和`build-gold-svg-page`。模型只传resource ID、当前页ID、manifest逻辑input/output ID与会话相对路径;不能读取/复制helper源码,也不能传脚本路径、argv、shell、解释器或环境变量。

当前页目录放所有生成产物：`page_spec.template.json`、`page_spec.fill_plan.json`、`page_spec.json`、`page_spec.normalized.json`、`patch.json` 和 `source.svg`。

禁止执行`render_svg_ppt_examples.py`、`pip/uv/npm install`、环境探测命令或任何`backend/app`/仓库根目录路径。

## 运行顺序

1. 按本合同补齐`page_spec.json`，至少包含：

```json
{
  "theme_id": "business_blue",
  "layout": "gold_cards",
  "title": "观点句标题",
  "key_message": "一句话核心判断",
  "framework_layer": {"background_owner": "ppt_framework", "draw_full_page_background_in_svg": false},
  "quality_targets": {"metrics_min": 3, "groups_min": 3, "structured_fields_min": 3},
  "metrics": [{"label": "收入达成", "value": "102%", "note": "财务月报"}],
  "groups": [{"title": "经营判断", "claim": "行业复制成为新增收入核心来源", "evidence": ["新增合同 62%"], "action": "沉淀可复制打法"}],
  "rows": [{"cells": ["事项", "证据/口径", "影响", "Owner", "状态"]}],
  "pyramid_region": {"x": 170, "y": 330, "w": 960, "h": 420},
  "pyramid_layers": [{"title": "目标层", "claim": "统一客户价值", "evidence": ["目标客群"], "action": "明确取舍标准"}],
  "native_chart_slots": [{"id": "chart-slot-1", "chart_type": "bar", "box": {"x": 920, "y": 390, "w": 430, "h": 260}, "data": [{"label": "Q1", "value": 31}]}],
  "evidence_asset_slots": [{"id": "screenshot-proof-1", "box": {"x": 680, "y": 245, "w": 360, "h": 220}, "source": "会议纪要"}],
  "sources": ["年度财务月报", "CRM合同清单"]
}
```

2. 调用`run_skill_resource(resource_id="validate-gold-page-spec", parameters={"validate_only":true}, inputs={"spec":<page_spec路径>}, outputs={"normalized_spec":<normalized路径>, "repair_patch":<patch路径>, "fill_plan":<fill-plan路径>}, slide_id=<page_id>)`。
3. `result.quality.quality_status=needs_repair`时,先按`result.repair_patch`或产出的patch补真实素材、证据、Owner、行动和来源,再重验。
4. ready后调用`run_skill_resource(resource_id="build-gold-svg-page", inputs={"spec":<page_spec路径>, "patch":<可选patch路径>}, outputs={"svg":<source.svg路径>, "normalized_spec":<normalized路径>}, parameters={}, slide_id=<page_id>)`。

## 选择布局

- `gold_cards`：3-4 个判断/证据/行动模块。
- `gold_evidence_table`：经营结论、证据口径、解释、缺口、Owner。
- `gold_action_ledger`：事项、责任人、动作、检查标准、节奏。
- `gold_timeline`：里程碑、计划、阶段复盘。
- `pyramid_hierarchy`：先给 `pyramid_region`，再用 `pyramid_layers` 计算三层 `<polygon>`；层内放短标题/claim，证据行动放 proof 区，禁止退化为矩形卡片。

布局只能作为 `structure_hierarchy` 的落地方式。页面像固定模板时，先读 `gold-structure-composition.md` 和 `anti-pattern-fixed-template-monotony.md`，不要只换颜色或重新排列同样卡片。

## 提交前 QA

- 必须通过模型可见工具 `validate_svg_drawingml`；不能有 `<script>`、`foreignObject`、`use/symbol`。
- 所有 `<text>` 显式 `fill`、`font-family`、`font-size`。
- 不输出整页背景 rect、页眉、章节胶囊、页码、贴边竖条、页面侧边框或整页外框。
- 图表用 `native_chart_slots`，SVG 只画 slot 外框和元数据，后端叠加原生 chart。
- 金字塔用 `pyramid_region/pyramid_layers`，SVG 必须有 `pyramid-stack` 和至少 3 个 `<polygon>`。
- 不要用 SVG 手绘真实图表；金字塔不要退化成三层矩形卡片。
- 生成后仍要按当前页真实素材替换示例数据，再调用 `render_svg_drawingml_slide`。
