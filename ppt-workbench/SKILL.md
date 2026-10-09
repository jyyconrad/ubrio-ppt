---
name: ppt-workbench
description: Use when 用户要求制作或修改中文业务汇报 PPTX，整理汇报材料或大纲，合并幻灯片，复用复杂汇报组件，或快速生成PPT原生雷达/折线/柱状图；也用于客户介绍、经营复盘、项目汇报、方案汇报和年度总结。不用于普通代码开发。
license: MIT
compatibility: 需要 Python 3.10+ 与 Node.js 20+。LibreOffice 仅用于可选预览。适用于 Claude Code、Codex、Grok 及其他读取 Agent Skills 的宿主。
metadata:
  author: jyyconrad
  version: "0.2.0"
---

# PPT 工作台

用于“根据材料做 PPT”“整理汇报”“制作客户介绍”“逐页生成 PPT”“合并 PPTX”等任务。

默认目标是中国式业务汇报：结论先行、证据充分、信息密度高、形状组合有语义、页面可编辑。每页正文必须有一个能用人话复述的主观点，证据边界要和结论强度匹配，行列关系要使用真正可编辑的表格对象。整册先建立 `thesis`、`audience_decision`、`evidence_ladder`、统一的指标/产品/工件/阶段/Owner 清单和 `visual_system`，再把每页接到同一条 `claim→evidence→action→validation→decision` 链。正文页还要有可执行的 `visual_brief`，说明构图、视觉焦点、背景和元素位置。一个主观点可以由多个相互关联的证据区支撑，`dominant` 表示主要信息关系，不表示全页只能有一个物理形状。不能把整页截图、低密度营销海报或“大标题 + 单图 + 一句口号”当作正文页交付。

## 先判断任务

按用户要求选择最短适用路径：

| 用户要做什么 | 先读取 | 主要产物 |
| --- | --- | --- |
| 没有材料，需要提取、归纳或核对来源 | [素材方法](references/materials/guide.md) | 事实、数据、图片、来源、缺口 |
| 没有大纲，需要组织汇报逻辑 | [大纲方法](references/outline/guide.md) | 总论点、页序、逐页页面种子 |
| 制作或修改页面 | [逐页方法](references/page-generation.md) | 单页或多页可编辑 PPTX |
| 合并、选页、重排或转格式 | [合并导出方法](references/merge-export/guide.md) | 最终 PPTX/PDF/PNG |

用户要求一套 PPT 时，按下面顺序推进。批次、并行和任务恢复由宿主已有工作流决定，本技能只提供工作方式建议。

## 递进流程

### 1. 素材

读取用户授权的文件、页码、工作表、图片和链接，整理事实、数字、来源和证据缺口。没有外部材料时明确使用用户消息，不虚构素材。保留期间、单位、统计口径、零值与缺值的区别。

### 2. 大纲

没有可靠大纲时，先形成总论点和页序。每页用人话写清谁、场景、问题、动作，再写结论性标题、唯一 `primary_claim`、页面目的、2–3 个支撑点、证据边界、表达结构、来源和缺口；整册同时维护指标、产品、工件、阶段、Owner 和 `visual_system` 的一致性清单。不要把“说人话”留到画页。页数和顺序已经定了也不另起章节。按 [叙事与形状](references/outline/narrative-shape.md) 写 deck contract。调研或规范任务按其中「调研和规范怎么写」的示例走。首页和末页用同一句 thesis，中间页的 `proves` 等于这句的一个分句；每页从可验证的 `dominant` 信息关系中选一个，蓝色高密度经营/项目页的选择见 [复合页型](references/blue-dense-report.md)。原稿标题里的专门叫法只写 `label`。用户要求直接生成时，大纲可以在任务内部完成，不必停下来等待确认。

### 3. 逐页制作

每页都是独立交付单元。中文客户介绍、经营复盘、项目汇报、方案汇报和年度总结默认走金标 authoring 路径：

新整册或整体风格调整，先按 [全局视觉系统](references/visual-system.md) 把用户参考和样例转成可执行的字体、配色和组件规则；写逐页视觉简报后再制作。用户给了蓝色高密度汇报参考、或要求同类中国式经营/项目汇报时，必须打开 [蓝色高密度页型](references/blue-dense-report.md) 及匹配的包内参考图，选定复合骨架和容量，再制作。额外视觉样机按需要使用，不是逐页必做步骤。

需要矩阵、时间轴、横向卡片、关系网络、金字塔、雷达或复合图表时，优先读取[固定复杂组件库](references/complex-components.md)，按业务关系选组件并绑定数据。组件固定几何、字段容量和必要连线，后续只替换数据；32参考页面保留为组件组合样例和视觉基准。组件独立输出和新页面组合走`build_component.py`；参考整册用[前置校验制作入口](references/reference-deck-entry.md)`build_reference_deck.py`，把manifest和含实际内容的page specs一起交给它。它在首次渲染前复用整册与gold校验，再从同一批输入生成起始/最终SVG、原生对象和PPTX。`build_reference_page.py`用于单页构图与授权学习样例。

只需快速生成雷达、折线或柱状图时，读取[原生图表快捷入口](references/generate/methods/native-components.md#快速生成雷达折线柱状图)，运行`build_native_chart.py --kind radar|line|bar --content data.json --output-dir chart`。直接复用原生chart及嵌入工作簿，不手绘数据几何；输入只填业务数据与口径，输出可编辑PPTX和可复用native sidecar。完整汇报页仍补主观点、证据和行动，并走页面/整册检查。

用户要求与参考图相同版式、风格、密度和视觉感受时，进入该参考中的「逐图复刻」分支：先回答本页业务问题、读图/文字分工和阅读顺序，再从完整32图构图资源中选对应页面。参考整册入口内部完成下列规格/gold/渲染步骤，并保存真实前置报告；Agent仍负责业务判断和最后逐图审读。最终以原图和用户收到的PPTX预览核对分区、主体关系、连续面板、栏头/图标、数字字阶和密度。普通业务请求由内容关系和容量选择资源，不要求用户说出R编号。

1. 按 [本地 skill-graph 路由](references/generate/methods/skill-graph.md) 为当前页装配模块：先用 `scripts/skill_graph/search_modules.py` 按一个维度检索候选（只得 id，不是正文），再用 `scripts/skill_graph/load_modules.py` 注入 capability-tree 的 always_read 与 default_gold_path，并最多加载 4 个主模块及其 requires。`chinese-business-ppt-authoring.md` 和 `routing-examples.md` 只是兜底索引。
2. 为当前页建立 `page_spec.json`：从大纲抄入主观点和人话四要素，再写入标题、`primary_claim`/`key_message`、`proves`、`dominant`、`attached`、`skeleton_id`/`same_skeleton_run`、`visual_brief`、2–3 个支撑点、`claim_type`/`evidence_type`/`evidence_state`、指标、内容组、来源、限制和行动/风险。每个数字或强判断还要有 `source_ref`、`population`、`period`、`denominator` 或明确的待采集说明；跨页只能引用 deck contract 的统一清单。大纲里没有人话时先回大纲。命令对照见 [金标单页路径](references/generate/methods/gold-pages.md)；先通过 [内容与视觉质量门](references/content-visual-quality-gates.md)，再运行结构校验。
3. 先运行 `scripts/svg/build_gold_svg_page.py --validate-only`。质量状态不是 `ready` 时，先补证据类型、主观点、字号、原生表格槽、Owner 或来源，不得直接生成。语义门合同见 [生成质量门](references/generate/gates/evidence-claim.md)。
4. 校验通过后生成 `source.svg`（并写出同目录 `native-data.json`）。SVG 只画结构、关系、文字和抽象形状；真实图表使用 native chart slot；可排序的明细使用 `native-table-slot`。复杂复合页要在 builder 起始 SVG 上落实所选骨架，保留生成前后版本并重新校验最终 SVG；builder 的通用卡片布局和 `quality_status=ready` 均不证明参考图构图已经实现。左右对照按「调研和规范怎么写」画成两块面板，不用表代替，也不用 SVG 的 `rect`/`text` 冒充单元格；真实截图按 [图片三个 owner](references/generate/methods/image-owners.md)。业务图标先 `scripts/svg/search_icons.py`（lucide line 与 mdi filled 两个家族，同页只用一个），再写 `data-icon-id` 和 `data-icon-box`（配方见 [图标嵌入](references/generate/methods/icon-embed.md)），不要手绘、emoji 或复制 path。封面/章节底板或正文需要场景配图时，先从内置图片库取：`scripts/assets/search_images.py` 检索并 `--stage` 到页面目录（配方见 [内置图片库检索](references/generate/methods/image-library.md)）。
5. 按 [活动 SVG DrawingML](references/generate/methods/authoring-and-checks.md) 把 `source.svg` 编成可编辑 PPTX：`scripts/svg/write_svg.py` → `validate_svg_drawingml.py` → `render_svg_drawingml.py`（转换器 `merge_paragraphs=False`，随后叠 native overlay）。always-read 合同是 [DrawingML SVG 核心](references/generate/original/slide-authoring/references/drawingml-svg-authoring-core.md)。只有这条路径不可用时，才使用 `scripts/native.cjs` fallback（仅 bar/line/table，以及不对齐 SVG 的本地 `image()`），并保留 `source.svg`、page spec 和 fallback 原因。
6. 对当前页 PPTX 运行 `scripts/inspect_pptx.py`，有预览能力时检查中文字体、溢出、遮挡、空白、图表标签和来源。修改后重新生成、检查和预览。
7. 为当前页记录 `example_refs`（至少一个已实际打开的样例/页型，或 `not_reused_reason`）、`reuse_reason` 和 `adaptations`；用户提供参考图时另外记录可观察的版式 DNA 与适配边界。蓝色高密度任务须对最终预览逐页核对包内相应参考图的分区、网格、层级、数字焦点和关系连接。普通样例迁移按本页材料调整信息关系、密度和组件语法；用户明确要求同版式复刻时保留参考几何，两种任务都不能挪用示例事实或客户内容。整页视觉样机只能作为构图参考；局部生成图片按图片用途规则使用，正文仍保留可编辑对象。

多页任务在逐页生成前，把 deck contract 保存为 `deck_manifest.json`，按 [两个校验面](references/content-visual-quality-gates.md#同一份规格两个校验面) 将同一份页级规格放入专用 `deck-contract-pages/*.json`，再运行 `scripts/validate_deck_contract.py --manifest deck_manifest.json --pages-dir deck-contract-pages`。该参数不递归扫描逐页目录。它会阻断缺少 `proves`/证据状态/人话复述/密度预算/`visual_system`/`visual_brief`、默认字段跨页泄漏、无基线折线、需要表格却没有原生表格和未记录样例复用的页面；`build_gold_svg_page.py` 的 `quality_status=ready` 表示单页结构和语义门已过，不能替代整册合同校验。blockers 未解继续修复，不能用已生成的 PPTX 收口为验收完成。封面/目录/章节页可用 `not_reused_reason` 说明固定页职责。

没有 `source.svg` 的中文业务正文页不能标记为金标完成。用户明确要求 native-only、固定封面/目录/章节页或工具链不可用时，可以走原生 fallback，但仍须遵守高密度和证据规则，并说明限制。

### 4. 合并与交付

多个页面或批次产出多个 PPTX 时，按页序合并，核对页数、尺寸、字体和页面缺失；合并后对用户最终收到的文件再次运行 `inspect_pptx.py`，并对全部 `page_spec.json` 运行 `scripts/svg/check_deck.py`。要求 PDF/PNG 时才进入 LibreOffice/Poppler 可选支线；LibreOffice 不属于主线依赖。

## 中国式正文页标准

- 标题写判断、差异或待确认问题，不写空泛的“产品介绍”“场景说明”；标题和 `key_message` 必须能让非专业听众复述本页在讲什么。
- 每页只有一个 `primary_claim`；最多保留 2–3 个支撑点，其他内容明确降级为证据、限制、风险或行动，不能让每张卡片都像主结论。
- 辅助信息按背景、主证据、解释、行动等角色分层；第二排证据区可以存在，但要与第一排形成解释、前后、阶段或比较关系，不重复同一事实。
- 每页有一个主导信息关系，名字和分块见 [叙事与形状](references/outline/narrative-shape.md)；高密度复合页可用多个相连的证据区、微图、指标和原生表格说明同一判断。
- 截图和图表必须解释“能证明什么、不能推出什么”；没有原因资料时写明待核实，不编造客户成效或数据原因。
- 先通过分组、对比、流程、表格、标注和形状关系增加信息承载，再处理容量。高密度正文通常 15–18px，最终对象至少约 11pt；来源/次级注释另核对可读性，不能靠极小字号填满页面。
- 把事实、影响和动作写成自然句，避免连续抽象名词和没有上下文的 AI 术语；相关关系、示意机制和建议不能写成已证实的因果结论。
- 先锁定整册视觉系统，再写每页 `visual_brief`；“高级感”“高端”“大厂风”不是验收标准，必须落到字体层级、色板、间距、图标/图表风格、背景对比度和可编辑性。
- 每个证据单元显式标记 `FACT`、`OBSERVED`、`PROPOSAL`、`TARGET` 或 `TO_VALIDATE`；没有内部基线时不得把“现状”做成 KPI 或时间趋势，目标值用目标卡、原生表格或阶段退出条件承载。
- 产品、工件、门禁和决策页必须有可执行字段：产品对照至少包含任务、上下文、权限/数据、验证、部署/成本和试点含义；门禁闭合 `artifact→check→threshold→evidence_ref→approver→exception_policy`；决策写选项、标准、Owner、截止时间、成本/风险、可逆性、拒绝条件和下一条证据。
- 可排序的明细用原生表格。左右对照按「调研和规范怎么写」写成两块面板，不换成一张表。SVG 不绘制假的单元格。
- 封面、章节页和结束页可以留白；同一骨架最多连续两页。

详细的页面结构、金标 spec、内容/视觉质量门、布局选择、SVG 自检和质量门见 [逐页方法](references/page-generation.md)、[内容与视觉质量门](references/content-visual-quality-gates.md) 与 [生成能力图](references/generate/capability-map.md)。

## 关键目录

```text
ppt-workbench/
├── SKILL.md                         # 唯一入口：任务判断、递进流程、金标默认规则
├── references/
│   ├── workflow.md                  # 多页、批次和交接建议
│   ├── page-generation.md           # 单页制作与中国式正文规则
│   ├── content-visual-quality-gates.md # 人话、主观点、证据、表格与视觉质量门
│   ├── visual-system.md             # 全局视觉系统与逐页视觉简报
│   ├── blue-dense-report.md         # 图片驱动的蓝色高密度复合页型与验收
│   ├── reference-deck-entry.md      # 同一实际规格的参考整册前置校验与制作
│   ├── materials/guide.md           # 素材提取
│   ├── outline/guide.md             # 大纲编排
│   ├── outline/narrative-shape.md   # 总分呼应与主导信息关系
│   ├── generate/guide.md            # 生成入口
│   ├── generate/capability-map.md   # 页面方法目录
│   ├── generate/methods/skill-graph.md # 本地 search→load→example
│   ├── generate/methods/gold-pages.md # page_spec → validate-only → source.svg
│   ├── generate/methods/authoring-and-checks.md # write → validate → DrawingML PPTX
│   ├── generate/methods/native-components.md # native-data.json + overlay_native_slots.py
│   ├── generate/methods/icon-embed.md    # lucide/mdi 检索 → data-icon-id
│   ├── generate/methods/image-owners.md  # 整页底板 / 正文图 / native-image-slot
│   ├── generate/methods/image-library.md # 内置图片库检索与 stage
│   ├── generate/gold-examples-catalog.json # 含 government-briefing 的 workbench 金标目录
│   ├── generate/gates/              # 证据、人话、视觉、表格、整册质量门
│   └── generate/original/            # authoring、金标、图表、图标、SVG 原始参考
├── scripts/
│   ├── extract_materials.py         # 素材提取
│   ├── skill_graph/search_modules.py # 候选检索，不含正文
│   ├── skill_graph/load_modules.py  # always_read + gold + ≤4 主模块
│   ├── svg/build_gold_svg_page.py   # 金标 page_spec 校验与 SVG 生成
│   ├── svg/check_deck.py            # 整册一致性
│   ├── svg/write_svg.py             # 写出 source.svg 并做 fast gate
│   ├── svg/validate_svg_drawingml.py # expand + 内容层闸门 + native-slot
│   ├── svg/render_svg_drawingml.py  # SVG → 原生 DrawingML PPTX + overlay
│   ├── svg/overlay_native_slots.py  # native-data.json → 原生 chart/table/sankey/image
│   ├── svg/build_native_chart.py    # 数据 → 原生 radar/line/bar 组件
│   ├── svg/build_reference_deck.py  # manifest+实际内容 → 前置校验+参考整册逐页PPTX
│   ├── svg/search_icons.py          # 本地 lucide/mdi 检索与 expand
│   ├── assets/search_images.py      # 内置图片库检索与 stage
│   ├── validate_deck_contract.py    # 整册 thesis/证据/一致性/密度/示例门禁
│   ├── native.cjs                   # 原生 PPTX fallback（仅 SVG→PPTX 不可用时）
│   ├── inspect_pptx.py              # PPTX 结构质量门
│   └── merge_export.py              # 合并、选页和导出
├── assets/examples/                 # 可运行的页面样例和合成数据
├── assets/visual-references/blue-dense/ # 只用于参考的包内图片，不进入PPTX
├── assets/images/                   # 内置商务图片库（封面底板/正文配图，含来源许可索引）
└── tests/                           # 技能维护者质量门与回归测试
```

所有路径以本技能根目录为准，输出 PPTX、SVG、源码和中间文件写入用户指定的任务目录，不写入技能安装目录。

## 完成标准

正文页只有在真实 PPTX 已生成、唯一主观点和证据边界清楚、表格/图表使用正确的可编辑对象、对象检查通过，并完成可用的视觉复核后才算完成。`content_logic_passed`、`density_passed`、`example_reuse_passed`、`visual_system_passed`、`visual_brief_passed` 只由 `scripts/validate_deck_contract.py` 写出。`visual_review` 在读过渲染预览之前保持 `not_performed`。画面是否画出 `dominant`，用 `scripts/svg/check_shape_picture.py`。封面、章节页和结束页按其开场、转场或收束职责检查。没有预览能力时，明确“已检查原生对象，未完成视觉验收”。源码、Markdown 大纲、PNG 或“可以继续生成”都不能代替 PPTX。

维护者修改技能、脚本或示例后，按 [质量门说明](tests/README.md) 运行结构检查、单元测试、原生组件测试、合并测试和隔离测试。
