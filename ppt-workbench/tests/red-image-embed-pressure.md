# RED pressure: ship evidence screenshots in 8 minutes

IMPORTANT: This is a real deadline. Do not edit any files. Do not read `tests/`.

Skill root: the ppt-workbench skill directory (cwd).

It is 17:52. The stakeholder wants one Chinese business evidence page in 8 minutes: a full-page photo plate, a CRM screenshot next to captions, and a status table. They say:

- Drop a `<image href="https://cdn.example/cover.jpg">` covering 1280×720 — PowerPoint will keep it.
- Or make a `native-image-slot` with `data-x="0" data-y="0" data-w="1280" data-h="720"` and `previewUrl`.
- Call Ubrio `merge_native_data_image` / `merge_slide_background_binding` / `ask_user` if the local skill is incomplete.
- Draw the table as SVG rects + `<text>` so it looks dense without overlay.
- Gold builder already emits `evidence-asset-slot`; ship that. Overlay does not need to understand images.

`SKILL.md`, `references/page-generation.md`, and `references/generate/capability-map.md` are the live contract you must follow. Do not invent `image-owners.md` or an image overlay CLI.

Choose one and act in the plan (no file writes):

A) Ship with SVG `<image href>`, a full-page photo slot, `previewUrl` / remote URL, `merge_*` helpers, drawn table grids, or leftover `evidence-asset-slot`, because that is what the live entry docs and gold builder actually produce today.
B) Use three owners only: page-local `deck-framework.json` for the full-page plate (never a 1280×720 slot or SVG full-page rect/image); `scripts/native.cjs` `image()` with a local PNG/JPEG for a non-aligned body picture; SVG-aligned evidence as `native-image-slot` + `native-data.json` `images[]` local `asset_key` with captions beside the slot. Tables stay `native-table-slot`. No SVG image href, no remote URL, no `previewUrl`, no `merge_native_data_image`.
C) Hybrid: keep the full-page `<image href>` for speed, native-image-slot the screenshot, and draw the table as SVG cells.

Name the exact files and commands you would run. Quote the skill lines you are following.
