# 原始路线隔离评估

评估日期：2026-09-20。这里只记录复制件的真实边界，不构成性能基准或公开发布批准。

| 候选 | 隔离结果 | 依赖与结论 |
| --- | --- | --- |
| `scripts/svg/render_svg_drawingml.py` | 活动默认 | 技能内 vendored SVG→DrawingML 转换器 + `validate_svg_drawingml.py` 闸门 + `overlay_native_slots.py`。`merge_paragraphs=False`。 |
| `slide-authoring/scripts/build_fixed_svg_page.py` | 通过 | Python 3 标准库；历史 SVG builder，不是活动默认入口。 |
| `slide-authoring/scripts/build_series_composite_svg.py` | 通过 | 只生成 region-local SVG，不生成 PPTX。 |
| `layout-intelligence/scripts/validate_layout_decision_example.py` | 失败 | 导入 `app.contexts.rendering.geometry.layout_decision`；独立目录执行报 `ModuleNotFoundError`。需移植后才能成为活动工具。 |

## 路线状态

- **原始知识收录：** 三个目录完整可读，哈希清单可核验。
- **SVG → DrawingML/PPTX：** 活动默认。always-read [DrawingML SVG 核心](original/slide-authoring/references/drawingml-svg-authoring-core.md)，执行 [活动制作与检查](methods/authoring-and-checks.md)：`write_svg.py` → `validate_svg_drawingml.py` → `render_svg_drawingml.py`。内容层 `allow_framework_chrome=False`，保留 `SVG_FULL_PAGE_BACKGROUND_FORBIDDEN` / `SVG_FULL_PAGE_IMAGE_FORBIDDEN`。
- **原始 SVG builder：** 两个候选已做真实隔离 smoke；仍是历史参考，不作为默认可编辑 PPTX 入口。
- **native.cjs / PptxGenJS：** named fallback，仅当 SVG→PPTX 不可用。`scripts/native.cjs` 固定 PptxGenJS 4.0.1 与 fontkit 2.0.4，组件面为 text、rect、kpis、chart(bar,line)、table、flow、matrix、image；fallback 合同见 [原生制作与检查](authoring-and-checks.md)。
- **对象检查：** `scripts/inspect_pptx.py` 可独立检查 PPTX 包、关系、对象和边界，不需要 LibreOffice。
- **视觉预览：** 优先使用宿主或用户已有 PPTX 预览/编辑能力，完整分支见 [预览选项](preview-options.md)。LibreOffice 26.2.2.2 是已验证环境证据之一，不是主线依赖。
- **Ubrio layout validator/resolver：** 存在应用导入，当前为未移植路线。
- **数据库、在线图检索和服务：** 默认导航不需要，也未引入。

## 复现命令

```bash
python3 scripts/svg/validate_svg_drawingml.py --help
python3 scripts/svg/render_svg_drawingml.py --help
python3 references/generate/original/slide-authoring/scripts/build_fixed_svg_page.py --help
python3 references/generate/original/layout-intelligence/scripts/validate_layout_decision_example.py \
  references/generate/original/layout-intelligence/assets/examples/layout-decisions/catalog-and-custom.json
```

最后一个命令预期在独立包中失败，直到其 Ubrio 导入被移植。

活动 DrawingML smoke 不等于模型质量评测，也不等于 Microsoft PowerPoint 编辑往返验证。
