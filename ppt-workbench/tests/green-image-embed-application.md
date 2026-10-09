# GREEN application: image embedding owners (updated skill)

IMPORTANT: This is a real authoring task. Do not edit any files. Do not read `tests/`. Do not invent scripts that are not on disk.

Skill root: the ppt-workbench skill directory (cwd).

You are making one Chinese business body page with:

1. a full-page cover plate
2. a body photograph not aligned to SVG cards
3. an evidence screenshot that must sit in an SVG box next to editable captions
4. a native evidence table (not a drawn grid)

A local PNG exists at `assets/examples/evidence-synthetic.png`.

Using ONLY files that currently exist under the skill root, answer:

- Which owner owns each picture, and which files/commands you would use.
- Exact `native-image-slot` markup and `images[]` row (local `asset_key` only).
- Where the caption sits.
- Whether you would write SVG `<image href>`, `previewUrl`, a remote URL, `merge_native_data_image`, or a 1280×720 image slot.
- How the table becomes a PowerPoint-native table.
- What gold builder emits for `evidence_asset_slots` that have a local `asset_key`.

Start from `SKILL.md`, then `references/page-generation.md`, `references/generate/capability-map.md`, and `references/generate/methods/image-owners.md`. Cite paths. `ls` `scripts/svg/overlay_native_slots.py` before claiming overlay exists.
