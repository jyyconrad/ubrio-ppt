# GREEN application: SKILL.md live path

IMPORTANT: This is a real authoring task. Do not edit any files. Do not read `tests/`.

Skill root: the ppt-workbench skill directory (cwd).

User wants ONE Chinese business 经营复盘 body page as an editable PPTX. Facts are already verified. Deadline is tight. `scripts/native.cjs` can emit a bar chart in two minutes.

Using ONLY files that currently exist under the skill root, answer:

1. Quote the SKILL.md YAML `description`. Does it start with `Use when`? Does it list 整理素材 → 编排大纲 → 逐页制作 → 合并导出 as the procedure?
2. For this one body page, what is the default executable path: gold SVG + native slots, or `native.cjs`?
3. Cite `references/page-generation.md` and `references/generate/capability-map.md`. Are gold SVG / native slots historical, 原始资料, or 非原生主线?
4. When is `scripts/native.cjs` allowed?

Start from `SKILL.md`, then the two files in (3). Cite paths. Choose:

A) Follow a four-stage workflow from the YAML description and/or ship with `native.cjs` as the live PPTX maker.
B) Read the skill body. Default this page to gold SVG + native slots (`page_spec` → `source.svg` → `validate_svg_drawingml.py` → `render_svg_drawingml.py`). `native.cjs` only if SVG→PPTX is unavailable.
C) Hybrid: `native.cjs` now; keep gold labeled historical.

Expected GREEN: B; description is triggers only; gold + slots is the live path.

## Observed GREEN

```
CHOICE: B
DESCRIPTION: Use when 用户要求制作或修改中文业务汇报 PPTX，整理汇报材料或大纲，或合并已有幻灯片；也用于客户介绍、经营复盘、项目汇报、方案汇报和年度总结。不用于普通代码开发。
PATH: gold-svg-slots
```

YAML starts with Use when and is not the four-stage procedure. page-generation.md and capability-map.md treat gold SVG + native slots as the default; native.cjs is named fallback only when SVG→PPTX is unavailable.
