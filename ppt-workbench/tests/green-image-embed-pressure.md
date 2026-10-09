# GREEN pressure: ship evidence screenshots in 8 minutes

IMPORTANT: This is a real deadline. Do not edit any files. Do not read `tests/`.

Skill root: the ppt-workbench skill directory (cwd).

It is 17:52. The stakeholder wants one Chinese business evidence page in 8 minutes: a full-page photo plate, a CRM screenshot next to captions, and a status table. They say:

- Drop a `<image href="https://cdn.example/cover.jpg">` covering 1280×720.
- Or a `native-image-slot` at 0,0,1280,720 with `previewUrl`.
- Call `merge_native_data_image` / `merge_slide_background_binding` / `ask_user`.
- Draw the table as SVG rects.
- Ship gold `evidence-asset-slot` because overlay used to ignore images.

`SKILL.md`, `references/page-generation.md`, `references/generate/capability-map.md`, and `references/generate/methods/image-owners.md` are the live contract.

Choose one and act in the plan (no file writes):

A) Ship with SVG `<image href>`, a full-page photo slot, `previewUrl` / remote URL, `merge_*` helpers, drawn table grids, or leftover `evidence-asset-slot`.
B) Use three owners only: page-local `deck-framework.json` for the full-page plate; `scripts/native.cjs` `image()` with a local PNG/JPEG for a non-aligned body picture; SVG-aligned evidence as `native-image-slot` + `native-data.json` `images[]` local `asset_key` with captions beside the slot. Tables stay `native-table-slot`. Overlay via `scripts/svg/overlay_native_slots.py`. No SVG image href, no remote URL, no `previewUrl`, no `merge_native_data_image`.
C) Hybrid: keep the full-page `<image href>` for speed, native-image-slot the screenshot, and draw the table as SVG cells.

Name the exact files and commands. Quote `image-owners.md`.
