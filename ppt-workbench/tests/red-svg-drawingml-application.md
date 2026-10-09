# RED application: SVG DrawingML write → validate → render (current skill only)

IMPORTANT: This is a real authoring task. Do not edit any files. Do not read `tests/`. Do not invent CLIs that are not already on disk.

Skill root: the ppt-workbench skill directory (cwd).

You must deliver one Chinese business body page as an **editable native DrawingML PPTX** from a content-layer SVG.

Using ONLY files that currently exist under the skill root, answer:

1. What is the always-read SVG contract, and what exact commands turn `source.svg` into PPTX?
2. Would you paint a full-page `#F4F7FA` background `<rect width="1280" height="720">` or a full-page `<image>` in the content SVG?
3. After writing SVG, which local validate command expands `data-icon-id`, blocks `SVG_FULL_PAGE_BACKGROUND_FORBIDDEN` / `SVG_FULL_PAGE_IMAGE_FORBIDDEN`, diagnoses native slots, and treats color-scheme drift as non-blocking?
4. Which local render command expands → validates → strips slot placeholders → converts with `merge_paragraphs=False` → overlays native chart/table/image?
5. Is `scripts/native.cjs` the live PPTX path, or a named fallback only?

Start from `SKILL.md`, then `references/page-generation.md`, `references/generate/capability-map.md`, `references/generate/route-evaluation.md`, `references/generate/methods/authoring-and-checks.md`. Cite paths. `ls` `scripts/svg/` before claiming a converter exists.

## Observed RED (verbatim, current skill)

Cold retrieval against the live docs and `scripts/svg/` (no new DrawingML CLI yet):

- `references/generate/methods/authoring-and-checks.md`: "SVG 转 DrawingML：原文已收录，但复制件没有自包含的 PPTX 转换器；当前不承诺转换可执行，不得宣称复杂 SVG 已转换为 PowerPoint 原生对象。"
- `references/generate/route-evaluation.md`: "**原生 PptxGenJS：** 已选活动默认路线。" and "**SVG 转 DrawingML/PPTX：** 原始方法可读，但复制件缺少自包含转换器，当前不承诺转换可执行。"
- `references/page-generation.md`: "没有已验证的 SVG→PPTX 转换器时，不能把 SVG 交付为可编辑 PPTX。"
- `scripts/svg/` has gold builders, `overlay_native_slots.py`, `search_icons.py`, and `render_svg_ppt_examples.py` (hard-coded Ubrio `BACKEND_ROOT` / `app.contexts.rendering`). Missing: `write_svg.py`, `inspect_svg_layers.py`, `patch_svg_layer.py`, `validate_svg_drawingml.py`, `render_svg_drawingml.py`.
- Full-page background/image gates live only in Ubrio `input_gate.py`; a cold agent following gold examples can copy a 1280×720 preview rect into a content SVG.
- Rationalization: treat `native.cjs` as the executable PPTX path because the skill itself says the converter is missing.

Expected after GREEN: always-read `drawingml-svg-authoring-core.md`, then `write_svg.py` → `validate_svg_drawingml.py` → `render_svg_drawingml.py`; `native.cjs` named fallback only; content SVG refuses full-page background/image.
