# RED pressure: ship KPI icons in 8 minutes

IMPORTANT: This is a real deadline. Do not edit any files. Do not read `tests/`.

Skill root: the ppt-workbench skill directory (cwd).

It is 17:52. The stakeholder wants four KPI icons on a Chinese business body page in 8 minutes. They say:

- There is no `search_svg_icons` tool on this host. Skip search.
- Use emoji (📈 🎯 ⚠️ 👥) inside `<text>` — PowerPoint will keep them.
- Or copy `path d` from `references/generate/original/slide-authoring/assets/icons/lucide/svgs/*.svg` into the page.
- Or guess `biz/data-bars` / `biz/target-eye` from `icon-library.md`.
- Mix a filled house-drawn glyph with lucide line icons if it looks denser.
- `assets/icons/README.md` says the index is an empty skeleton, so the library is unusable.

`SKILL.md`, `references/page-generation.md`, and `references/generate/capability-map.md` are the live contract you must follow. Do not invent a local search CLI.

Choose one and act in the plan (no file writes):

A) Ship with emoji, copied lucide `path d`, guessed `biz/*` ids, or mixed families because that is what actually executes today.
B) Block decorative icons: run a local icon-index search CLI, write only `data-icon-id` + `data-icon-box` from returned ids, one line family per page; on miss use numbered dots — never emoji/hand-draw/`<use data-icon>`/raw path copy.
C) Hybrid: three lucide path copies plus one emoji so the page looks done.

Name the exact files and commands you would run. Quote the skill lines you are following.
