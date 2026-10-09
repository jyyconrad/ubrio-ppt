<!--
id: theme-background-policy
category: visual-theme
read_when: 需要为单页或整册决定整页背景（纯色/低干扰抽象矢量装饰/暗色影像/纸纹），或准备调用 merge_slide_background_binding / merge_deck_background_default 时
page_roles: cover, agenda, content, section_divider, summary, closing
stage_tags: slide_generation
supports: svg_drawingml
outputs: background_policy
depends_on: contract-visual-token-core.md
relation_specs: requires:contract-visual-token-core
triggers: 整页背景, 逐页背景决策, 每页独立背景, deck默认兜底, 背景图, 全局背景图候选, 背景图入池, 背景图替换, use_case background, 换背景, 缺背景图, 背景占位, 补背景图, 暗色影像背景, 纸纹底, 底纹, 纹理背景, 纯色背景, SVG 背景, 低干扰矢量背景, 背景纹理, 高级感背景, 场景感, 沉浸感, 主题宣讲, 课堂宣讲, 科普, 品牌发布, 文旅, 企业文化, 招商园区, background pattern, 全局背景, 全册背景, 背景主色调, 背景配色, 色系一致, 前后色系不一致
max_use: 只读本文件决定背景形态与参数，不连带读取全部 theme 颗粒
-->

# 整页背景统一策略

> **整页基础背景硬性禁令（产品决策）**：基础底禁透明色（必须严格 `#RRGGBB`）、禁白色斑点/波纹类 `pattern` 底纹（在深色主题上会回退成浅斑点+白底、前景白字不可读）。写入即被 `SLIDE_BACKGROUND_TRANSPARENT_FORBIDDEN` / `SLIDE_BACKGROUND_PATTERN_BASE_FORBIDDEN` 拒绝。存量 pattern spec 仍可渲染，但不要再新写。

## 1. Owner 边界

整页背景 = deck 母版层，SVG 内容层**禁止**画整页 rect / 近满页 `<image>`（硬门 `SVG_FULL_PAGE_BACKGROUND_FORBIDDEN` / `SVG_FULL_PAGE_IMAGE_FORBIDDEN`）。要"自己画背景"就用 `type='svg'` 交给 deck_framework 背景通道，不是塞进内容层 SVG。三个图片 owner：

| 用途 | 工具 |
|---|---|
| 整页背景（纯色/矢量装饰/影像/纸纹） | `merge_slide_background_binding` → `deck_framework.background` |
| 普通正文/证据/书封图 | `merge_slide_picture_binding` |
| SVG 局部精确图文混排 | `merge_native_data_image` |

## 2. 形态选型决策表

| 形态 | use_when | avoid_when |
|---|---|---|
| `solid` 纯色（默认首选） | 信息密度高的页、正文数据页；只要不需要影像/纹理/装饰就用纯色深色/主题色底 | 需要叙事氛围或视觉层次时（改 svg/photo_dark） |
| `svg` 低干扰抽象矢量装饰底 | 只需渐变、几何、网格等抽象装饰且不需要真实影像；零位图、导出后 PowerPoint 原生可编辑 | 需要照片、人物、书封、实景、证据截图或复杂纹理时（用受控图片）；装饰喧宾夺主/含文字信息时 |
| `photo_dark` 暗色影像 | 封面/章节页要叙事氛围；有受控图（入池素材/生图），配 overlay 压暗保字面对比 | 正文数据页（图抢内容）；无受控图不硬凑 |
| `paper_light` 纸纹 | 正文浅底要纸张质感、去"平涂感"；无图直接用内置 `texture_preset`（paper-fiber/fine-grid/dot-grid/diagonal-hatch/noise-soft/cross-hatch），有专门纹理图可绑图 | 暗色 deck（polarity=dark）；纹理 opacity>0.2 会脏 |
| ~~`pattern` 斑点/波纹底纹~~ | **已废止为整页基础背景**：想要几何秩序感改用 `svg`（自己画克制的网格/斜线，更可控） | 任何整页基础底——写入即被拒 |

### 2.1 背景图增益场景

优先考虑真实或可商用背景图片的 deck 类型：课堂宣讲、科普讲座、公开课、品牌/产品发布、文旅/城市推介、展览/文化主题、企业文化/年会、人物故事/读书分享、招商/园区/产业项目、生态环保、医疗健康、公益传播、校园宣讲。它们需要先建立场景、对象、情绪或叙事质感，背景图能明显提升高级感。

这些 deck 的封面、章节页、概念引入页、案例/场景页优先 `photo_dark` 或浅色弱化影像背景；正文解释页可用更高 overlay、`paper_light` 或 `svg` 低干扰底，保证可读。

不应强铺背景图的页面：大表格、密集指标、财务明细、预算测算、复杂流程/架构、法务合规条文、审计风险清单、需要逐字阅读的 SOP 和截图证据页。这些页面只用纯色、`svg` 低干扰矢量底或 `paper_light`。

## 3. 参数决策规则

- **polarity 先行**：dark → solid 深色 / svg 深色装饰 / photo_dark；light → solid 浅色 / svg 浅色装饰 / paper_light。浅色 deck 不要单页突兀铺暗影像（章节转场有意为之除外）。底色与 `theme_polarity_contract.expected` 冲突时写入成功但返回 `SLIDE_BACKGROUND_POLARITY_MISMATCH` warning，非有意反差页请换同极性底色。底色/遮罩色还必须与 palette 主色调配套（同族或中性，规则见 §4.1），冲突时返回 `SLIDE_BACKGROUND_COLOR_SCHEME_MISMATCH` warning。
- **solid**：只有 `base_color`（严格 `#RRGGBB`）。深色/主题色纯底是全册默认背景的首选；缺色或非严格 hex 报 `SLIDE_BACKGROUND_BASE_COLOR_REQUIRED` / `SLIDE_BACKGROUND_TRANSPARENT_FORBIDDEN`。
- **svg**：见下节「§3.1 svg 背景输入契约」。
- **photo_dark**：`overlay_color` 用近黑（如 `#0B0F14`），`overlay_opacity` 0.3-0.5（字面越多越高）；`fit` 默认 cover，主体偏移用 `crop.focal_x/focal_y` 保画面重心。`base_color`/`overlay_color` 必须严格 `#RRGGBB`，透明色报 `SLIDE_BACKGROUND_TRANSPARENT_FORBIDDEN`。
- **paper_light**：`texture_opacity` 0.08-0.2（preset 不给时用库内默认）；`texture_fit`/`texture_crop` 同 photo_dark 口径；`texture_overlay={color,opacity}` 可叠浅色 wash 压纹理对比。`base_color` 严格 `#RRGGBB`。
- 每形态都可给 `base_color` 作图片/纹理未命中时的安全底色（一律严格 `#RRGGBB`，不接受 transparent/none/rgba()/8 位带 alpha）。

### 3.1 svg 背景输入契约（仅低干扰抽象装饰）

**方法要点**：用主题基色铺一层**不透明整页基底**，再叠**低干扰**的几何/渐变装饰（光斑、斜切、网格、径向渐变），呼应本页内容语义但不抢信息焦点。背景是**纯装饰层**，不承载任何文案。

- **输入**：`background={"type":"svg","svg":"<完整 SVG 源>"}`，无需 `image_binding`。
- **viewBox**：必须 16:9 或同比（推荐 `0 0 1280 720`）。
- **必须**：含一个覆盖整页（x≈0 y≈0、宽高≥96%）的**不透明基底 rect**——solid `#RRGGBB` 或内部渐变 `url(#...)`；纯 solid 基底其 fill 会被抽为 `base_color`，**渐变基底必须另给 `background.base_color`（#RRGGBB）**作 slide 兜底底色与极性判定。
- **禁止**：`<image>`、外链/远程/`data:` 引用（只允许内部 `#id` 渐变）、可读 `<text>/<tspan>`、`<script>`/`on*`/`<foreignObject>`。体积 ≤60KB、元素 ≤400。
- **失败检查（均可机械修复）**：`SLIDE_BACKGROUND_SVG_REQUIRED`（缺 svg 源）、`SLIDE_BACKGROUND_SVG_BASE_REQUIRED`（缺不透明整页基底）、`SLIDE_BACKGROUND_SVG_BASE_COLOR_REQUIRED`（渐变基底缺 base_color）、`SLIDE_BACKGROUND_SVG_IMAGE_FORBIDDEN` / `_TEXT_FORBIDDEN` / `_EXTERNAL_REF_FORBIDDEN`、`SLIDE_BACKGROUND_SVG_VIEWBOX_INVALID`、`SLIDE_BACKGROUND_SVG_TOO_LARGE` / `_TOO_COMPLEX`。
- **落地**：renderer 经 SVG→DrawingML 转换把背景形状注入 slide 最底层（所有内容形状之下），`base_color` 同时写入 slide 兜底底色，导出/合并层同源补写。

## 4. Deck 默认兜底，单页逐页决策

背景同时涉及 deck 一致性和单页表达。deck / page-role 默认负责稳定极性、色板和无 override 时的安全兜底；每一页仍必须根据本页叙事、信息密度、可读性、画面主体与可用素材独立决定是否覆盖默认。逐页决策不等于逐页换色系，override 仍需遵循统一 palette。

1. **先读取默认，不机械沿用**：foundation 阶段在 `style_manifest.background_policy` 里定 deck / page-role 默认，并与 `palette` 同轮定稿。slide_generation 先读取该默认作为兜底，再判断当前页是否需要 override；不要求先改全局才能处理当前页。
2. **每页都可 override**：`merge_slide_background_binding` 写 `slide_overrides[page_id]`。有合适背景图、单页特殊叙事、章节转场、案例/场景展示，或密集数据页需要降噪时都可覆盖默认。图片背景、solid、paper_light、低干扰 svg 都是合法单页选择。
3. **相同诉求再上移全局**：若 2 页以上确实要使用同一背景 spec / 同一页型规则，优先改用 `merge_deck_background_default` 减少重复；若各页使用不同且语义匹配的图片，仍应保留逐页 override。要成片改变极性或色系时回 foundation 同步修改 `background_policy` + `palette`。

优先级：**slide_overrides > default_by_page_role > default > theme.background 纯色**。完整的 page role 映射 + 背景合同骨架实例见 `style-literary-documentary-cn.md`。

### 4.1 背景与主色调配套（换背景 = 换配套色板）

背景不是孤立图层：它与 `style_manifest.palette` 是同一份视觉合同的两半。选定背景形态与底色时必须同时核对 palette，四条规则：

- **色相同族或中性**：背景底色（solid/svg 的 `base_color`、photo_dark 的 `overlay_color`）色相必须与 deck 主色（palette 的 accent 或既定 background）同族，或干脆中性（灰阶/近黑/近白），不得引入 palette 之外的第三色相。写入时高饱和底色与 palette 主色色相差 >60° 会返回 `SLIDE_BACKGROUND_COLOR_SCHEME_MISMATCH` warning（附应对齐的主色 hex），收到即改色对齐，除非本页是有意撞色页。
- **深色背景 → 浅色高对比前景**：背景转深（photo_dark / 深色 solid/svg）时，palette 的标题/正文必须用浅色高对比，accent 用亮色变体（同色相提亮），否则字面沉底不可读。
- **换全局背景 = 换配套色板，一次一起改**：换全册背景（尤其换极性或色系）时必须同轮核对并更新 palette（回 foundation 改 `style_manifest`）；只换背景不校色板，正是"前后两套色系"的直接来源。
- **单页 override 只换背景层**：单页特殊背景仍沿用全册 palette——标题/正文/accent 用 palette 已定槽位（深色 override 页切到浅色前景），不得因为换了背景顺手引入新主色。

如果 foundation / outline 阶段已经确定要用背景图，它们应该已经通过 `web_search(mode='image' 或 'mixed', use_case='background', materialize=true)` 把候选写入全局素材池。当前页先复用这些 `selected_image_binding / material_ref`；如果画面主体、深浅极性或标题安全区不适合当前页，可以搜索并入池新的背景候选，再用 `merge_slide_background_binding` 写当前页 override。不要为了保持早期策略而强用不合适的图，也不要在已知要图时空白渲染。

## 5. 工具速查（merge_slide_background_binding / merge_deck_background_default）

- 全册/整组相同背景规则用 `merge_deck_background_default`（省略 `page_roles`=整册 `default`，或指定 cover/agenda/section_divider/content/summary/closing）；每页都可用 `merge_slide_background_binding` 写单页 override，默认背景仅作兜底。
- 无图形态不传 `image_binding`：`{"type":"solid","base_color":"#0A1E45"}`、`{"type":"svg","svg":"<svg viewBox='0 0 1280 720' …>…</svg>"}` 或 `{"type":"paper_light","texture_preset":"paper-fiber","base_color":"#F4EFE7"}`。solid / svg 不含真实图片，**不受** `allow_background_images` 策略限制。
- photo_dark / 绑图 paper_light 必须给受控引用（asset_id / material_id / asset_key / 本地 /v1/files URL）；`remove=True` 删单页 override 回落默认。
- 错误码：`SLIDE_BACKGROUND_PATTERN_BASE_FORBIDDEN`（pattern 底纹已废止，改 solid/svg/photo_dark/paper_light）、`SLIDE_BACKGROUND_TRANSPARENT_FORBIDDEN`（透明色→严格 #RRGGBB）、`SLIDE_BACKGROUND_SVG_*`（见 §3.1）、`SLIDE_BACKGROUND_UNCONTROLLED_URL`（裸外链先 `web_search(mode='image' 或 'mixed', materialize=true)` 入池）、`SLIDE_BACKGROUND_BINDING_AMBIGUOUS`（补 asset_id/selector）、`SLIDE_BACKGROUND_TEXTURE_PRESET_INVALID`（按 detail.allowed 挑）、`BACKGROUND_IMAGES_DISABLED_BY_USER_POLICY`（改 solid/svg 或征询用户）。
- 写入成功后继续 `validate_svg_drawingml` → 渲染；SVG 内容层不再画任何整页背景。

## 6. 缺背景图时的补位顺序

当前页明确要影像背景，但现有素材没有合适图时：

1. 若背景可来自公开图库或公开网页，先用 `web_search(mode='image' 或 'mixed', use_case='background', materialize=true, save_top_k=1-3)` 搜索并入池，查询词写清主体/场景、氛围、深浅极性、16:9、标题安全区和授权要求。
2. 若背景必须是真实地点、真实人物、真实书封或可核验截图，且公开检索没有安全命中，才用 `ask_user` 发**背景占位卡**，说明需要的背景图类型、真实性/授权要求，以及当前候选为什么不合适。
3. 用户补图后，再调用 `merge_slide_background_binding`；不要把用户刚给的 URL 直接塞回 SVG。
4. 若用户允许系统补位，且这页背景只承担氛围或意象，而不承担真实证据职责，可委派 `slide_image_generator` 生成 SVG-friendly 的替代背景资产。
   - 要求画面干净、无文字、主体不压标题区、适合 overlay 压暗或做浅纹理 wash。
   - 当前运行时拿回的是受控图片资产，不是可编辑 SVG 背景文件；生成完成后仍然必须走 `merge_slide_background_binding`。
5. 若背景必须是真实地点、真实人物、真实书封或可核验截图，不要用生成图冒充；继续保留占位卡让用户补图，或改走公开检索。
6. 如果这页本质只需要“有质感的底”，并不坚持真实影像，可直接退回 `solid` 深色/主题色纯底、`svg` 低干扰抽象矢量装饰底或 `paper_light` 纸纹安全方案，而不是硬凑一张伪照片（不要用斑点/波纹 `pattern`）。
