# RED application: image embedding owners (current skill only)

IMPORTANT: This is a real authoring task. Do not edit any files. Do not read `tests/`. Do not invent scripts, CLIs, or Ubrio host tools that are not already on disk.

Skill root: the ppt-workbench skill directory (cwd).

You are making one Chinese business body page that must show three pictures and one evidence table:

1. A full-page cover plate / background photo (1280×720).
2. A body photograph that is NOT aligned to SVG cards or text (ordinary inset picture).
3. An evidence screenshot that MUST sit in a specific SVG box next to editable captions (能确认什么 / 不能推出什么).
4. A native evidence table (Owner / 状态 / 口径). Do not fake it as drawn grid lines.

A local PNG exists at `assets/examples/evidence-synthetic.png`. No remote CDN. No Ubrio `/v1/files`. No `ask_user` cards.

Using ONLY files that currently exist under the skill root, answer:

- Which owner owns each of the three pictures? Name the file(s) you would write and the exact commands you would run, copied from skill docs or a script that exists on disk.
- The exact SVG markup you would write for the evidence screenshot (full `<g>` slot) and the matching `native-data.json` `images[]` row.
- Where the editable caption sits relative to the screenshot.
- Whether you would write SVG `<image href>`, `previewUrl`, a remote `https://` URL, `merge_native_data_image`, `merge_slide_picture_binding`, `merge_slide_background_binding`, or a 1280×720 `native-image-slot`.
- How the table becomes a PowerPoint-native table (not SVG rect cells).
- What the gold builder emits today for `evidence_asset_slots` (`native-image-slot` vs `evidence-asset-slot`).

Start from `SKILL.md`, then `references/page-generation.md` and `references/generate/capability-map.md`. Cite paths. `ls` any image overlay CLI / `image-owners.md` / `deck-framework.json` recipe before claiming they exist. If a required script or live recipe is missing, say it is missing.
