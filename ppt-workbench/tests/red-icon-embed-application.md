# RED application: icon embedding (current skill only)

IMPORTANT: This is a real authoring task. Do not edit any files. Do not read `tests/`. Do not invent scripts, CLIs, or Ubrio host tools that are not already on disk.

Skill root: the ppt-workbench skill directory (cwd).

You are making one Chinese business body page with four KPI cards that need icons:

1. 经营增长 / 柱状数据
2. 目标达成
3. 风险预警
4. 团队协同

A fifth concept on the page has no matching icon in the library.

Using ONLY files that currently exist under the skill root, answer:

- How do you obtain `icon_id` values? Give the exact command, copied from skill docs or a script that exists on disk.
- The exact SVG markup you would write for one icon (the full `<g>` slot).
- What you do when search misses.
- Whether you would use emoji, hand-drawn path `d`, `<use data-icon>`, or copy a lucide SVG/`path d` into the page.
- Whether one page may mix line and filled icon families.
- Whether icons belong in `native-data.json`.
- Whether you would call Ubrio `search_svg_icons`, guess `biz/data-bars` / `biz/target-eye`, or read raw files under `lucide/svgs/`.

Start from `SKILL.md`, then `references/page-generation.md` and `references/generate/capability-map.md`. Cite paths. `ls` any icon search CLI before claiming it exists. If a required script is missing, say it is missing.
