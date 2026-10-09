<!--
id: skill-section/pre-render-gate
module_type: skill_section
category: execution-contract
stage: slide_generation
page_roles: content,summary
visual_tags: svg_drawingml
content_categories: pre_render_gate,quality_gate
skill_types: slide_generation_core,skill_section
summary_categories: skill_section_summary,quality_gate
triggers: validate_svg_drawingml,render_svg_drawingml_slide,主体 bbox,来源说明,最终态文案
priority: P0
read_when: 调 renderer 前需要确认当前页是否满足预渲染门禁时
max_use: 只约束 renderer 前门禁，不替代 route/load 本身
depends_on: slide-authoring:drawingml-svg-authoring, slide-authoring:svg-self-qa
-->

# Pre Render Gate

在调用 renderer 之前，当前页必须满足：

- 最终态文案已收敛，不能保留草稿词和内部推理。
- 结构、容量、来源说明都已满足当前页交付边界。
- `write_svg / patch_svg_layer -> validate_svg_drawingml(mode='full') -> render_svg_drawingml_slide` 的顺序完整执行。
- SVG 内容层不画整页背景、页眉页脚或框架 chrome；这些由 `deck_framework_snapshot` 负责。
- 色彩配额自检：非中性色相 ≤3 个；并列同级卡片/条目同色，不逐卡换色相；`accent` 与 foundation palette 主色一致；功能色只做小面积语义标记，不覆盖整张卡片或整栏。
- `validate_svg_drawingml(mode='full')` 即使返回 `ok=true`，只要还有 `SLIDE_COLOR_SCHEME_DRIFT` / `SLIDE_COLOR_PALETTE_OVERFLOW` warning，也必须按 `repair_suggestion` 改色并重验，清零前不调用 renderer。
- 铺满自检：主体 bbox 覆盖画布主要区域，页面底部/右侧无约超 1/4 画布的连续空白。

如果以上任一项不满足，不直接 render 试错。

修复审核或 QA 反馈时默认局部修改：优先用 `patch_svg_layer` 只改问题区域，不整页重写（除非反馈明确要求重构某区域）；重新渲染前逐条对照反馈确认每项已处理，并自查未引入新的裁切、重叠或空洞。

## 被门禁拒绝后的标准修复序列

`write_svg` / `patch_svg_layer` / `validate_svg_drawingml` / `render_svg_drawingml_slide`
返回 `ok=false` 时，错误里已经带齐修复所需的全部信息，按下面的顺序做，**一轮修完**：

1. 读 `issues[]`，不是只读 `message` 的第一条。`issues_total` 告诉你一共有几条 blocking；
   门禁一次性把所有 blocking 都返回了，逐条修，不要修一条就重新 validate。
2. 每条 issue 的 `repair_ops[]` 是可直接执行的指令：`target` 就是 `patch_svg_layer(layer_id=...)`
   的入参，`constraint` 给出必须满足的量（要收窄多少 px、单行最多多少字、重叠必须归零）。
   按 target 分组，一个 layer 一次 `patch_svg_layer`。
3. 几何类问题（`SVG_CONTENT_BOUNDS_OVERFLOW` / `SVG_TEXT_BOX_OVERFLOW` / `SVG_TEXT_OVERLAP`）
   直接看 `offending_elements[]` / `element_boxes[]` / `overflow_px`：谁越界、越了多少、在哪个 layer，
   全都给了。同一批越界往往同源（一行长句排到画布外，同时造成越界和重叠），先修最长的那行文本，
   通常一次就清掉多条 issue。
4. `native-data` 类问题（`NATIVE_DATA_FILE_NOT_FOUND` / `NATIVE_*_SLOT_MISSING_DATA`）：
   issue 里带 `native_data_skeleton`，slot_id 已经填好，`save_file` 写进 `native_data_ref`
   指向的路径，把 labels/series/rows 换成真实数据即可。SVG 若还没声明 `data-native-data-ref`，
   `repair_ops` 会同时给出补声明的第二步——两步都要做，只写 JSON 不改 SVG 渲染读不到。
5. 全部 ops 执行完，再调一次 `validate_svg_drawingml(mode='full')` 复查，通过后才 render。

反模式（明确禁止）：

- **不要用 `read_file` 重读整份 SVG 来找问题元素**。issue 已经给了 `layer_id` 和坐标；
  确实需要层清单时调 `inspect_svg_layers`（只回几十行 id + 摘要），不要把整页 SVG 读进上下文。
- 不要因为门禁被拒就整页 `write_svg` 重写。整页重写会引入新的越界和重叠，通常越修越远。
- 不要只修 `message` 里提到的第一条问题就重新 validate；剩下的 issue 下一轮照样把你拦住。
