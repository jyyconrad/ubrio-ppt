# GREEN application: SVG DrawingML write → validate → render

IMPORTANT: This is a real authoring task. Do not edit any files. Do not read `tests/`. Do not invent CLIs that are not already on disk.

Skill root: the ppt-workbench skill directory (cwd).

Deliver one Chinese business body page as an editable native DrawingML PPTX.

Using ONLY files that currently exist under the skill root, answer:

1. Always-read contract path, then exact write → validate → render commands.
2. Whether a full-page `#F4F7FA` background rect or full-page `<image>` is allowed in the content SVG (`SVG_FULL_PAGE_BACKGROUND_FORBIDDEN` / `SVG_FULL_PAGE_IMAGE_FORBIDDEN`).
3. That color-scheme drift is a warning, not a render block.
4. That `scripts/native.cjs` is a named fallback only.

Start from `SKILL.md`, then `references/generate/methods/authoring-and-checks.md`, `references/generate/route-evaluation.md`, and `drawingml-svg-authoring-core.md`. `ls` `scripts/svg/write_svg.py` `scripts/svg/validate_svg_drawingml.py` `scripts/svg/render_svg_drawingml.py`.
