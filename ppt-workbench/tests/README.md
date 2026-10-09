# 质量门与回归

这些测试随统一技能保留，供维护者在技能根目录运行；普通用户只需使用 `SKILL.md`，不需要加载测试文件。

维护者环境先安装 `requirements-dev.txt`。模型制作单页或整册时执行的是 `scripts/inspect_pptx.py` 加可用预览复核；下面的整套回归用于修改技能、脚本、示例或原始副本之后的质量确认。

## 快速质量门

```bash
python tests/check_skill.py
python -m unittest discover -s tests -p 'test_*.py' -v
python -m pytest tests/test_merge_export.py -q
node --test tests/native.test.cjs
```

`check_skill.py` 检查唯一入口、根目录结构、参考链接、活动脚本、样例、原始复制件和图标索引。设置 `PPT_WORKBENCH_SOURCE_ROOT` 后，还会逐文件 SHA-256 对照仓库原始技能副本。

多页汇报还应对任务目录中的 `deck_manifest.json` 和 page specs 运行 `python3 scripts/validate_deck_contract.py --manifest deck_manifest.json --pages-dir pages`；单页 `quality_status=ready` 不等于整册合同通过。

## 样例与隔离

```bash
python tests/verify_examples.py
PPT_FONT_PATH="$FONT_FILE" PPT_FONT_NAME="$FONT_NAME" \
  python -m unittest tests.test_generation_isolation -v
```

默认只做对象检查；明确选择 LibreOffice 时，才向 `tests/verify_examples.py` 传入 `--soffice`。隔离测试把整个技能复制到中文/空格路径、清空 Office PATH，并验证只读技能目录不会被生成过程写入。

## SVG、图表与图标

- 正文页默认：金标 SVG + native slots。`scripts/svg/write_svg.py` → `validate_svg_drawingml.py` → `render_svg_drawingml.py`；配方见 `references/generate/methods/authoring-and-checks.md`。
- 语义门：`scripts/svg/gates/` 与 `references/generate/gates/`，由 `build_gold_svg_page.py` 的 `quality_report` 合并；整册另跑 `scripts/svg/check_deck.py`。
- 图表/表格槽：`scripts/svg/overlay_native_slots.py`，配方见 `references/generate/methods/native-components.md`。
- 图标：`scripts/svg/search_icons.py` 检索 `icon-index.json`（lucide line + mdi filled 两个家族），validate/render expand `data-icon-id`；配方见 `references/generate/methods/icon-embed.md`。
- 图片：三个 owner 见 `references/generate/methods/image-owners.md`；`overlay_native_slots.py` 叠 `native-image-slot` 本地 PNG/JPEG。内置图片库（`assets/images/` + `image-index.json`）由 `scripts/assets/search_images.py` 检索与 stage；索引完整性、许可边界与 stage 回归在 `tests/test_image_library.py`。
- `scripts/native.cjs` 只在 SVG→PPTX 不可用时 fallback（bar/line/table）；`scripts/inspect_pptx.py` 检查对象。
- SVG 页面参考：`scripts/svg/` 其余 builder 与 `references/generate/original/`。
- 布局决策示例校验：`scripts/layout/validate_layout_decision_example.py`；它依赖 Ubrio 应用导入，独立技能环境中若未移植会明确失败，不作为默认 PPTX 生成入口。
- 图表和图标资源必须保留来源、版本和许可边界；不能因脚本或图标文件已复制就宣称已经获得公开再分发权。

新增合同回归覆盖：`tests.test_deck_contract` 会用正例/负例检查整册 contract、无基线趋势、原生表格、示例/参考图复用、默认字段泄漏、连续同骨架和视觉系统/逐页视觉简报。视觉字段检查只验证声明完整性，报告 `validation_scope=declared_contract_only`，不能替代渲染目检或证明参数已进入渲染器。
