<!--
id: current-slide-quality-scope
category: quality-scope
read_when: slide_generation 当前页缺证据、信息密度高、视觉不稳、或渲染前需要全范围自检
page_roles: content, section_divider, summary
supports: svg_drawingml
outputs: quality_scope_checklist
max_use: 只读本文件；具体 SVG 细则再读取 slide-authoring/references/contract-svg-self-qa.md
-->

# Current Slide Quality Scope

页级质量覆盖不是让代码替模型做全部判断。代码 QA 只覆盖稳定信号；模型在生成和渲染前必须覆盖以下 8 类范围。

1. **证据范围**：硬指标、价格、比例、时间、样本、排名、技术机制、竞品对比必须来自用户素材、公开来源、工具结果或明确假设。缺证据先补证据；仍不足再询问用户或降级为风险边界。
2. **最终文案范围**：最终 PPTX 正文不得保留草稿词、内部推理、工具说明、路径、状态机字段或“示意/合理推断/预计”式未确认结论。
3. **结构范围**：标题是观点句，主体至少有结论、支撑、解释、影响、行动/风险中的 3 类；卡片、流程、图表和结论条要形成清晰阅读路径。
4. **容量范围**：不用小字硬塞；正文、流程标签、来源说明和图表标签必须可读。内容过载时重排、摘要化、拆页或询问用户。
   SVG 页必须估算主体 bbox 的宽高和比例，不能只凭肉眼判断“差不多铺满”；页面底部/右侧约超 1/4 画布的连续空白按必改处理，内容少先放大字号、增大卡片撑满版面。
5. **视觉范围**：同一 deck 统一主题、色彩、图标、编号、卡片样式和强调方式；色彩守 deck 配额——`accent` 与 foundation palette 主色一致，非中性色相 ≤3 个，并列同级项同色、不逐卡换色相；不用 emoji 或临场手绘图标替代正式视觉语言；不用整圈粗描边（`stroke-width` ≥2px 包住卡片/容器四边）或卡片左缘/顶缘装饰色条制造强调，层级靠填充深浅分层、留白分组和字重字号表达，细则见 `slide-authoring` 的 `contract-svg-self-qa.md`。
6. **框架范围**：SVG 只画内容层；背景、页眉、页脚、页码、章节胶囊、进度导航和外框只由 `deck_framework_snapshot` 在框架层处理一次。
7. **来源范围**：每页最多一个来源说明，最多一句，放在内容区底部弱化；不要生成多行脚注、页脚或来源墙。
8. **交付范围**：最终确认只能来自渲染工具自动展示的 PPTX 预览；用户确认前不推进页面、不切阶段、不把中间文件当交付。

如果其中任一范围无法判断，先补材料、读对应 reference 或询问用户，不要带着不确定性调用 renderer。
