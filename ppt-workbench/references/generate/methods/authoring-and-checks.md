# 活动 SVG DrawingML 制作与检查

中文业务正文页的可编辑 PPTX 默认走这条本地路径。always-read 合同是 [DrawingML SVG 核心](../original/slide-authoring/references/drawingml-svg-authoring-core.md)；本页只补 write → validate → render 的可执行入口。`scripts/native.cjs` 是 named fallback，不是金标默认。

## 顺序

1. 读 `drawingml-svg-authoring-core.md`（1280×720 内容层、允许元素、native slot、禁止项）。
2. `write_svg.py` 写出完整 `source.svg`。局部改层用 `inspect_svg_layers.py` / `patch_svg_layer.py`。
3. `validate_svg_drawingml.py`（默认 `allow_framework_chrome=False`）。
4. `render_svg_drawingml.py` 转原生 DrawingML PPTX，再叠 native overlay。
5. `scripts/inspect_pptx.py` 检查对象。

```bash
python3 scripts/svg/write_svg.py --output source.svg < source.svg
python3 scripts/svg/inspect_svg_layers.py --svg source.svg
python3 scripts/svg/patch_svg_layer.py --svg source.svg --layer-id title --operation replace --fragment '<text id="title" .../>'
python3 scripts/svg/validate_svg_drawingml.py --svg source.svg --mode full
python3 scripts/svg/render_svg_drawingml.py --svg source.svg --native-data native-data.json --output page.pptx
```

`render_svg_drawingml.py` 固定 `merge_paragraphs=False`、`use_native_shapes=True`、`use_compat_mode=False`。不要把 convert 当 linter；先 validate。

默认画布仍为16:9。用户要保留参考图的3:2架构或2:1裁切时，SVG写真实宽高并向render传`--canvas-format auto`；native overlay使用实际PPT画布定位。不同画布须分别交付，普通PPT每册只有一种尺寸，不能把特殊页横向拉伸合并。预览脚本在macOS且未指定soffice时优先宿主已安装LibreOffice；字体可读性仍要打开最终PNG核对。

## 内容层闸门

`validate_svg_drawingml.py`：expand `data-icon-id` → `validate_svg_input(allow_framework_chrome=False)` → native-slot diagnose → 转换副本剥离 slot 内占位 `<text>`。色系 `SLIDE_COLOR_SCHEME_DRIFT` / `SLIDE_COLOR_PALETTE_OVERFLOW` 只进 warnings，不阻断。

内容 SVG 禁止整页底板与整页图：

- `SVG_FULL_PAGE_BACKGROUND_FORBIDDEN`：近满页实心 `<rect>`（x/y≤2% 且 w/h≥96%）
- `SVG_FULL_PAGE_IMAGE_FORBIDDEN`：近满页 `<image>`

整页照片写页旁 `deck-framework.json`，见 [图片三个 owner](image-owners.md)。图标先 `search_icons.py`，见 [图标嵌入](icon-embed.md)。图表/表格见 [原生图表与表格槽](native-components.md)。

## Fallback

仅当本技能的 SVG→PPTX 转换器不可用时，才用 `scripts/native.cjs`（仅 bar/line/table，以及不对齐 SVG 的本地 `image()`），并保留 `source.svg` 与 fallback 原因。组件参数见 [原生制作与检查](../authoring-and-checks.md)。
