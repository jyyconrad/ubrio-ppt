<!--
id: content-literary-documentary-narrative
category: content-structure
stage: outline, slide_generation
read_when: 当前页需要文学/纪录片式论述、主题意象、人物命运、读书分享观点，而不是业务 claim/evidence/action
page_roles: content, section_divider, summary
style_family: literary_documentary_cn
ppt_types: book_analysis, literary_documentary, keynote
visual_tags: literary_documentary_cn, editorial
content_categories: content_structure, narrative
supports: svg_drawingml
outputs: narrative_blocks, page_intent, quote_plan, compression_rules
depends_on: scenario-book-deep-analysis.md
max_use: 只负责内容结构，不规定具体坐标；排版另读 layout reference
-->

# Content: Literary Documentary Narrative

## 核心结构

把页面从“业务证据页”改成“可讲述的一页”。每页至少明确：

- `page_intent`：这一页在整套叙事中推进什么。
- `thesis`：一句可讲的主题判断。
- `narrative_blocks`：2-4 个论述块，每块有小标题和正文。
- `image_intent`：图片要表达的意象或证据作用。
- `quote_or_close`：一句引语、金句或总结判断。

## 页面标题

标题应是判断句或问题句：

- 好：`真正的强大，是在苦难中仍能承接生命`
- 好：`命运不是外部惩罚，而是一次次选择的回声`
- 避免：`苦难与成长`
- 避免：`命运主题分析`

## narrative block 写法

每个 block 控制在一个讲述点内：

- `heading`：不超过 12 个汉字，像小论点。
- `body`：1-3 句，解释“为什么”和“带来什么感受/判断”。
- `evidence_hint`：可选，来自文本、人物、场景或材料。
- `image_link`：可选，说明图片如何服务该 block。

## 压缩规则

- 如果有 5 个以上观点，优先合并成 3 个层级，而不是缩小字号。
- 如果正文太长，保留 thesis、每块第一句和 quote，把补充解释移到讲稿或下一页。
- 如果缺证据，写成“论述页”而非“证据页”，但要保留来源或不确定边界。
- 如果图片只是装饰，删除图片或改为更明确的 `image_intent`。

## 与 business gold 的边界

可以保留观点和来源，但不要强行补：

- metric panel
- owner/action ledger
- risk table
- ROI/效率指标
- 四象限业务判断

当用户明确要求经营汇报、项目复盘、行动计划时，切回 business gold。
