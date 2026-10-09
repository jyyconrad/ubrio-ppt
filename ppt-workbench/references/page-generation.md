# 单页制作方法

中文客户介绍、经营复盘、项目汇报和方案汇报默认按金标 authoring 执行。不要把 GUIDE、`chinese-business-ppt-authoring.md` 或整张能力图当作已加载模块。先按 [本地 skill-graph 路由](generate/methods/skill-graph.md) 运行 `scripts/skill_graph/search_modules.py`（一次一个维度，只得候选 id），再 `scripts/skill_graph/load_modules.py` 注入 always_read、default_gold_path 和最多 2–4 个主模块。能力图是目录，不能作为“已完成金标路径”的证明。

人话在大纲完成，见 [大纲方法](outline/outline-method.md)。制页从大纲抄入 `primary_claim` 和人话四要素；缺了或仍是抽象名词堆，回大纲改，不在本页另起一套总结。每页正文先建立 `page_spec.json`，先按 [内容与视觉质量门](content-visual-quality-gates.md) 写清唯一 `primary_claim`、人话化 `key_message` 和 2–3 个支撑点，再按 [金标单页路径](generate/methods/gold-pages.md) 调用 `scripts/svg/build_gold_svg_page.py` 做 `--validate-only`。质量报告会合并语义门（[证据](generate/gates/evidence-claim.md)、[决策](generate/gates/decision-governance.md)、[人话核对](generate/gates/plain-language-and-primary-claim.md)、[视觉](generate/gates/visual-readability.md)、[原生表格](generate/gates/native-table-routing.md)）。根据质量报告补齐证据、结构化字段、行动、Owner、来源和容量，再生成 `source.svg`。结构参考按路径加载 [金标页型](generate/original/slide-authoring/references/gold-page-patterns.md)、[结构层级](generate/original/slide-authoring/references/contract-structure-hierarchy.md) 和对应 `scenario-*-gold-pages`（含 workbench catalog 中的 `scenario-government-briefing-gold-pages`），不要把能力图或目录列表当成已读。可编辑 PPTX 默认走 [活动 SVG DrawingML](generate/methods/authoring-and-checks.md) 的 `write_svg.py` → `validate_svg_drawingml.py` → `render_svg_drawingml.py`；只有该转换器不可用时才使用 `scripts/native.cjs` 做 named fallback，但必须保留 `source.svg`、说明 fallback 原因，并继续执行高密度中国式汇报规则。没有 `source.svg` 的正文页不能标为金标完成。

单页是本技能最重要的工作单元。用户要一页时，直接完成这一页；用户要多页时，重复本方法逐页执行。宿主可以把多个页面放进批次，但不能用一份整册脚本、几张截图或一份空泛大纲代替当前页制作。

## 中国式业务汇报默认

面向客户介绍、经营复盘、方案汇报和需求交流时，页面默认服务于“讲清判断、拿出证据、推动下一步”，不是做成低信息密度的营销海报。封面、章节页和结束页可以采用强品牌或适度留白；正文页按以下规则组织：

- 标题直接写结论、差异或要确认的问题，不把“产品介绍”“场景说明”当作正文标题。
- 每页只保留一个 `primary_claim`。标题、key message、主证据和底部行动必须围绕同一判断；最多 2–3 个支撑点，不能让 KPI、机制、风险、原则和动作同时争夺主层级。
- 文案先写自然主语、动作、对象和结果，再压缩成卡片；避免连续抽象名词、口号和没有上下文的 AI 术语。每页通过非专业听众复述测试后再生成 SVG。
- `attached` 的 1–3 项记录口径、来源、风险或行动；可见辅助区可以是第二排，但须与主证据构成前后、因果假设、比较或阶段关系，不能复制同一层的平等文字卡。
- 每一页先确定一个主导信息关系，再把背景、机制、指标、图表、表格和行动组织成相连的证据区。关系名字见 [叙事与形状](outline/narrative-shape.md)；蓝色高密度汇报按 [复合页型](blue-dense-report.md) 选择区域与容量。
- 截图是证据的一部分，不是整页内容。截图旁边必须有可编辑的标题、标注、关键读数、证据边界或下一步；截图不能占满页面后只在底部加一句口号。
- 数据页不能只放一张图和一个放大的数字。至少补充比较关系、变化解释、来源口径、限制条件或行动含义；没有原因资料时明确写“原因待核实”，不编造解释。
- 公开数据、调查、自报、实验和内部基线要区分 evidence type、样本、期间、分母和限制；不同口径不能用同一 KPI 视觉重量并列。概念机制图要标明“示意/待验证”，不能用无数据折线或端点模拟实证。
- 正文页优先使用可用画布，避免无意的大块空白和单一居中对象。页面有意留白时要服务于强调、对照或客户现场填写，不能只是因为没有继续组织信息。
- 同一套“标题 + 单图 + 底部 takeaway”不能连续复用为整册默认模板；相邻页面至少在信息结构或组件组合上有变化。
- 左右对照用两块 `comparison-panel`。有列标题且至少三行同类数据时才走 `native-table-slot`，见 [原生图表与表格槽](generate/methods/native-components.md)。SVG 不得用多个矩形和文本伪造单元格。

### 参考图与样例驱动

用户参考图先提炼成区域关系，再选择本地样例变体：判断标题、相连的 2–4 个证据区、可解释的连接和由证据推出的收口。蓝色高密度任务打开 [包内参考图与页型](blue-dense-report.md)，选择成效看板、诊断链、阶段路线、机制架构或决策矩阵，并看对应的可编辑示例。不要只复制深蓝色、白卡或整页坐标。正文页在 `page_spec` 留 `example_refs`、`reuse_reason`、`adaptations`；没有合适样例时写 `not_reused_reason`。具体检索和记录合同见 [本地 skill-graph 路由](generate/methods/skill-graph.md)。

内容骨架确定后，按 [全局视觉系统](visual-system.md) 继承整册 `visual_system`，再写每页 `visual_brief`：构图、视觉焦点、背景、元素位置。按需制作视觉样机；正文仍以可编辑文字、形状、原生表格、原生图表和受控图片落地。

页面密度按页面族设预算：契约、门禁阈值和可排序明细用原生表格；左右对照保持两块面板。流程/路线页每个 `process-step` 写一句，不只写阶段名。证据页必须保留独立图片/摘录及“能确认/不能推出”；目标值没有内部基线时使用表格或退出条件，不使用实证折线。记录 `unique_factual_atoms`、`relation_edges`、`evidence_bearing_objects` 和 `tiny_text_ratio`，shape 数量不计为信息密度。

页面密度不是把字缩小。普通内容页标题通常约 28–34pt；蓝色高密度页在 1280×720 上以约 36–44px 标题、15–18px 正文、11–13px 来源为起点，并以最终 PPTX 正文约 11pt 的下限核对。视觉层级、区域预算和容量见 [复合页型](blue-dense-report.md)。先通过分组、对比、流程、表格、标注和形状关系增加信息承载；超过可读容量时删减次要信息、转移到下一页或改组件，不能靠超小字号塞入。

### 页面类型与组合建议

| 页面目的 | 主结构 | 应补的辅助结构 |
|---|---|---|
| 结果/经营判断 | KPI、柱图或折线图 | 差异标注、口径卡、风险/行动栏 |
| 客户场景证明 | 真实截图或运行结果 | 输入→处理→输出关系、关键读数、未验证边界 |
| 功能/能力说明 | 产品截图、能力分组或模块图 | 角色、方法、连接器、适用条件和限制 |
| 流程/共创方案 | 3–5 个原生节点和连接符 | 双方投入、输入输出、验收标准 |
| 访谈/决策页面 | 原生表格或对比结构 | 结论、待确认项、负责人或下一步 |
| 蓝色高密度经营/项目复盘 | 成效看板、诊断链、阶段路线、机制架构或决策矩阵 | 分区导航、证据与关系、关键数/条件、底部洞察；按包内图片逐页核对 |

纯封面、章节页和结束页可以不套用以上正文密度，但必须明确它们承担的是开场、转场或收束职责。

### 稀疏页拒绝检查

在预览或对象检查后，逐页问：本页是否只有一个主对象？是否有超过约四分之一的无意空白？是否只有底部一句 takeaway 承担结论？是否能删掉一半文字而不损失证据关系？若答案显示页面只是“截图/图表 + 大标题”，先补充有证据的辅助结构或改用更合适的页面类型，再交付。不能为了达到密度编造数据、客户成效或产品能力。

## 开始前判断

当前页开始制作前，先明确：

- 大纲里本页的人话四要素和主观点是否已经写好；没有就回大纲；
- 受众和本页要回答的问题；
- 一个主要结论或需要管理层确认的判断；
- 支撑结论的事实、数字、图片和来源位置；
- 期间、单位、空值与零值、计算口径和证据缺口；
- 用户要求的页尺寸、模板、字体、风格和可编辑范围。

材料只有现象时不编造原因；没有原因资料时直接把“原因待补齐”作为证据边界。参考 PPT 只提供样式线索，不能把参考稿的客户名、数字和结论带入新页面。

## 页面表达

先写结论性标题，再决定证据和阅读顺序。根据内容选择合适的页面方法：

- 指标结果：KPI 与差距/状态；
- 趋势或目标对比：`native-chart-slot` + `native-data.json` 的 bar/line，保留完整类别、序列、零值和单位；
- 构成/归因/流向：pie、waterfall 或独立 sankey slot，不要手绘坐标轴；
- 明细证据：`native-table-slot` + `tables[]`，保留列语义和来源；
- 顺序或路径：原生流程、节点和连接关系；
- 两组判断：有明确轴义时使用矩阵，否则使用普通对比；
- 截图或照片证据：按 [图片三个 owner](generate/methods/image-owners.md)。整页底板写页旁 `deck-framework.json`（不要 1280×720 `native-image-slot` 或 SVG 满页 `<image>`）；不对齐 SVG 的正文图用 `scripts/native.cjs` `image()` 本地 PNG/JPEG；SVG 对齐的证据截图写 `native-image-slot` + `native-data.json` `images[]` 本地 `asset_key`，可编辑 caption 写在槽旁（能确认什么、不能推出什么）。禁止 SVG `<image href>`、`previewUrl`、远程 URL。表格走 `native-table-slot`，不要手绘网格。
- 扫读图标：先 `scripts/svg/search_icons.py` 检索捆绑 lucide/`icon-index.json`，再写 `data-icon-id` + `data-icon-box`；同一页只用 line 家族；搜不到用编号圆点。不要 emoji、手绘业务图标、`<use data-icon>`、复制 `path d`，也不要调用 `search_svg_icons` 或猜 `biz/data-bars`。配方见 [图标嵌入](generate/methods/icon-embed.md)。

选择完页面目的后，按 [本地 skill-graph 路由](generate/methods/skill-graph.md) 加载当前页模块，并用 [能力图](generate/capability-map.md) 核对名称；至少确认页面角色、信息结构、容量和证据表达。需要可编辑 PPTX 时以金标 SVG + native slots 为默认，经 `validate_svg_drawingml.py` / `render_svg_drawingml.py` 转 DrawingML 再 overlay。图表/表格用 [原生图表与表格槽](generate/methods/native-components.md)，图片用 [图片三个 owner](generate/methods/image-owners.md)，图标用 [图标嵌入](generate/methods/icon-embed.md) 的 `search_icons.py`。只有 SVG→PPTX 不可用时才使用根 `scripts/native.cjs` fallback。

布局先分配标题、主证据、解释/行动和来源区域，再放入对象。对于复合页，gold builder 产物是语义校验通过后的起始 SVG；其通用布局不自动画出包内参考图的网格和连接，需基于起始 SVG 重排，保存前后版本并校验最终对象。内容过长时先归纳、分组、改写表达或调整区域；不要连续缩小正文，也不要把整页渲染成一张图片来假装可编辑。

## 实际生成

使用 [页面制作参考](generate/guide.md) 和 [活动 SVG DrawingML](generate/methods/authoring-and-checks.md) 的 `render_svg_drawingml.py`。`scripts/native.cjs` / PptxGenJS 只是 named fallback。生成源码应在用户指定的任务目录或宿主临时目录中，依赖从 [运行说明](runtime.md) 读取，不写入技能安装目录，不下载字体或隐式安装 Office。

页面生成至少要产生一个真实 `.pptx`。文字、形状、表格、图表和图片按实际需要保持为原生对象；图表数据与页面文案同步，图片保留来源和比例。修改已有 PPTX 时，先确认原位编辑能力和保真边界；无法安全保留复杂母版、动画或对象时，明确重建风险。

## 页面检查

生成后针对当前页的最终 PPTX 执行 `scripts/inspect_pptx.py`。多页时再对按页序排列的 `page_spec.json` 运行 `scripts/svg/check_deck.py`（[整册一致性](generate/gates/deck-consistency.md)）。检查：

- 页尺寸、页序和页面是否为空；
- 标题、正文、来源和数字是否存在且与证据一致；
- 标题和 key message 是否是同一个可复述的主观点，文案是否有自然主语和动作；
- 数字旁是否有证据类型、口径和限制，相关/示意内容是否被误写成因果或现状；
- 原生表格、图表、图片、备注、字体和内部关系是否存在；
- 表格场景是否真的生成了可编辑表格对象，而不是 SVG 网格和文本；
- 文本容量、顶层边界、缺失资源、非有限数值和外部关系错误。

有宿主预览能力时查看最终页面，关注中文缺字、截断、重叠、标签、对比度、图表刻度、来源可读性、3 秒主观点复述和远距阅读。蓝色高密度任务还要将最终 PNG 与实际打开的参考图并排核对分区层次、网格、数字焦点、连接与字体；逐页记录相似点及适配理由。修改后重新生成并重新检查；最多两轮自动修订，仍有问题就交代阻塞。没有预览能力时可以交付结构检查通过的 PPTX，但必须标注“已检查原生对象，未完成视觉验收”。LibreOffice/Poppler 是可选预览或转换支线，不是单页生成前提。
最终状态分开记录 `content_logic_passed`、`density_passed`、`example_reuse_passed`、`visual_system_passed`、`visual_brief_passed`、`structure_passed`、`visual_review` 和 `powerpoint_roundtrip`；结构通过且 `visual_review=not_performed` 时只能报告“原生对象已检查，视觉未验收”。

## 单页完成条件

当前页只有在真实 PPTX 已生成、证据边界已落实、原生对象检查通过，并按能力完成或明确记录视觉检查后，才可标记为完成。交付时返回文件路径、页面结论、来源摘要、对象检查状态和未验证风险。源码、Markdown 大纲、PNG 或“可以继续生成”都不能替代这一页的 PPTX。
