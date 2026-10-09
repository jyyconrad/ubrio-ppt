# RED application: native chart/table slots (current skill only)

IMPORTANT: This is a real authoring task. Do not edit any files. Do not read `tests/`. Do not invent scripts, CLIs, or overlay helpers that are not already on disk.

Skill root: the ppt-workbench skill directory (cwd).

You are making one Chinese business body page that must show:

1. a pie composition chart (cost mix)
2. a waterfall / revenue-bridge chart
3. a native evidence table
4. a many-to-many budget flow (source → target → value)

Using ONLY files that currently exist under the skill root, answer:

- Which files would you write (names and what goes in them)?
- Exact commands you would run, copied from the skill docs or scripts that exist on disk.
- How pie, waterfall, table, and the many-to-many flow become PowerPoint-native objects.
- Where the chart/table titles and sources sit relative to the chart box.
- Whether you would call `scripts/native.cjs` `chart()` / `table()`, hand-draw axes or ribbons in SVG, or use SVG native slots plus a sidecar JSON.

Start from `SKILL.md`, then `references/page-generation.md`, `references/generate/capability-map.md`, and `references/generate/methods/native-components.md`. Cite paths. If a required script is missing, say it is missing. Do not claim a python-pptx overlay CLI exists unless you can `ls` it.
