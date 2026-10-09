<!--
id: layout-fixed-cover-agenda
category: layout
read_when: 当前页是 cover/agenda/introduction/toc/目录/简单介绍，或文学纪录片风格的 cover/section_divider/closing 需要固定槽位 helper
page_roles: cover, agenda, section_divider, closing
supports: svg_drawingml
themes/layouts: fixed_cover_agenda, photo_dark_serif
outputs: fixed_page_spec_json,source_svg
depends_on: drawingml-svg-authoring.md, layout-dark-photo-interlude.md
max_use: 只用于 cover/agenda、2-4 项 introduction 或 photo_dark_serif 的章节/收尾固定页；不要扩展成正文页模板
-->

# Fixed Cover / Agenda / Photo Interlude SVG

## 适用

当前页任务包出现 `kind=cover|agenda|introduction`、对应 `page_archetype`、`toc`、`目录`、2-4 项简单介绍，或 `生成路径=template_direct`，但当前可见工具是 SVG DrawingML route 时，使用固定 SVG helper，不走正文页 gold builder。

当 `literary_documentary_cn` 风格命中 `photo_dark` 的封面、章节过渡或收尾页时，也使用 `photo_dark_serif` 变体。它只画衬线标题、小标签、引语和短强调线；整页图片、压暗遮罩和安全底色仍由 `deck_framework.background` 负责。

当任务输入明确提示“当前页已由大纲确定为固定页”时，直接执行本合同：只填少量槽位并调用 `run_skill_resource(resource_id='build-fixed-svg-page')`，不要再走正文页自由构图或多轮版式检索。先读取当前页背景合同；需要图片背景时复用已绑定素材，尚未绑定则先完成素材入池与背景绑定。helper 始终只生成内容层，不把图片、遮罩或整页底色画进 SVG。

## 输入合同

固定页只接收基础字段和 deck 级风格合同。不要把封面/目录当正文页自由排版，也不要传坐标、字号、卡片宽高、列宽、行高、序号位置或复杂布局逻辑。

只填固定槽位：

- cover：`kind`、`title`，可选 `subtitle`、`meta`、`footer`、`theme_id`、`style_manifest`。
- agenda：`kind`、`title`、`items`，可选 `subtitle`、`footer`、`theme_id`、`style_manifest`。
- agenda 的 `items` 可以是字符串，也可以是 `{title, children?}`。
- introduction：`kind=introduction`、`title`、`items`，可选 `subtitle`、`theme_id`、`style_manifest`；`items` 必须是 2-4 个 `{title, subtitle?}` 短项。超过 4 项、需要图表、复杂证据或自由构图时改用正文页，不得冒用固定页快编。
- photo_dark_serif：`kind=cover|section_divider|closing`、`variant=photo_dark_serif`、`title`，可选 `kicker`、`chapter_label`、`subtitle`、`quote_text`、`title_align`、`title_safe_region`、`theme_id`。
- `style_manifest.palette` 只填写关键颜色槽位：`background-color`、`title_text-color`、`body_text-color`，可选 `accent-color`、`surface-color`、`muted_text-color`、`border-color`。
- `style_manifest.object_defaults.fixed_page` 可指定 `background-color-ref`、`title_text-color-ref`、`body_text-color-ref`、`accent-color-ref`。
- `deck_framework.theme` 可作为脚本兜底来源，例如 `surface`、`muted`、`border`、`accent`、`title_text`、`body_text`。
- 兼容保留 `visual_tokens`，但新任务优先传 `style_manifest`。

禁止：

- 传 `x/y/w/h`、`font_size`、`card_width`、`card_height`、`columns`、`line_height`。
- 传背景矩形、页码、章节胶囊、进度条或侧边框。
- 不要自由手写复杂目录 SVG；必须调用 `build_fixed_svg_page.py`。

唯一例外是 `photo_dark_serif.title_safe_region`，它只表示标题组安全区，不能变成自由坐标模板。脚本内部默认使用 wide 16:9 的 `viewBox="0 0 1280 720"`，对应 PPTX `13.333 x 7.5 inch`。目录项较多时仍传入完整 `items`；脚本会自动切换 1/2/3 列、降低字号、隐藏副标题并压缩行距，优先保证所有目录标题在安全区内完整渲染。

## 执行

1. 先执行当前页背景合同：纯色保持纯色；图片背景复用已绑定素材，缺绑定时先补齐并绑定。
2. 写入 `slide-generation/<page_id>/fixed_page_spec.json`。
3. 调用声明资源：`run_skill_resource(skill_id="slide-authoring", resource_id="build-fixed-svg-page", slide_id=<page_id>, inputs={"spec":"slide-generation/<page_id>/fixed_page_spec.json"}, outputs={"svg":"slide-generation/<page_id>/svg_drawingml/source.svg"}, parameters={})`。
4. 不要读取或复制 helper 源码，也不要传脚本路径、argv、shell、解释器、环境变量或仓库绝对路径。

5. 调用 `validate_svg_drawingml(svg_file_ref="slide-generation/<page_id>/svg_drawingml/source.svg", mode="full")`。
6. 只有 validate 返回 `ok=true` 后，才调用 `render_svg_drawingml_slide(svg_file_ref="slide-generation/<page_id>/svg_drawingml/source.svg")`。

如果脚本无法运行，当前页应阻塞并报告工具缺口；不要临场手写复杂目录 SVG 兜底。如果 validate 返回 `ok=false`，只允许修正脚本输入或做很小的 SVG 兼容性修复。

## 最小 spec 示例

```json
{
  "schema_version": "fixed_svg_page/v1",
  "kind": "agenda",
  "theme_id": "tech_dark",
  "style_manifest": {
    "palette": {
      "background-color": "#07111F",
      "title_text-color": "#F8FAFC",
      "body_text-color": "#D8E7FF",
      "accent-color": "#2DD4BF",
      "surface-color": "#101827",
      "border-color": "#164E63"
    },
    "object_defaults": {
      "fixed_page": {
        "background-color-ref": "background-color",
        "title_text-color-ref": "title_text-color",
        "body_text-color-ref": "body_text-color",
        "accent-color-ref": "accent-color"
      }
    }
  },
  "title": "演讲议程",
  "subtitle": "技术分享会",
  "items": [{"title": "痛点开场"}, {"title": "能力拆解"}],
  "footer": "20-25 分钟"
}
```

深色影像章节页：

```json
{
  "schema_version": "fixed_svg_page/v1",
  "kind": "section_divider",
  "variant": "photo_dark_serif",
  "theme_id": "literary_documentary_cn",
  "chapter_label": "第一部分",
  "title": "苦难不是命运的终点",
  "subtitle": "人在命运里如何继续承担",
  "title_align": "left",
  "title_safe_region": {"x": 128, "y": 188, "w": 720, "h": 320}
}
```

`photo_dark_serif` 必须配合 `deck_framework.background` 的 `photo_dark` 背景使用；helper 不读取或写入图片。

## 质量检查

- SVG 不画整页背景、页眉、页码、进度导航、章节胶囊或页面侧边框。
- 标题、目录项、序号和页脚必须是 `<text>`，不能转 path。
- 目录项较多时必须仍完整传入 `items`；脚本负责多列、字号和间距自适配。
- 单个目录标题过长时由脚本按列宽换行或末尾省略；不要缩小到不可读字号硬塞。
- `fixed_page_spec.json` 中不得出现几何字段；出现时先删除，再交给脚本。
