<!--
id: chinese-business-ppt-scenarios
category: compatibility-index
runtime_scope: legacy
skill_kind: compatibility_index
read_when: 旧提示要求判断中国式 PPT 场景、受众、正式程度
page_roles: content, section_divider, summary
supports: svg_drawingml
outputs: scenario_reference_route
depends_on: _index/capability-tree.json
max_use: 只读取本索引和 1 个 scenario-* 文件，不要读取全部场景
-->

# Chinese Business PPT Scenarios

本文件是旧场景入口。具体内容已拆到 `scenario-*` 文件。

## 内容说明

根据关键词读取一个场景模板：

- 年终、年度复盘、述职、经营总结、KPI：`scenario-annual-summary.md`
- 项目进展、周报、里程碑、风险、交付：`scenario-project-report.md`
- BP、融资、商业模式、市场规模、增长：`scenario-financing-roadshow.md`
- 新品、发布会、功能亮点、用户价值：`scenario-product-launch.md`
- 论文、研究、实验、模型、答辩：`scenario-academic-defense.md`
- 学习贯彻、精神、党建、落实、党政：`scenario-government-study.md`
- 培训、课程、SOP、练习：`scenario-training-course.md`

## 视觉说明

场景决定语气，但最终配色服从当前 deck 视觉 token。领导/政务要庄重，投资人/客户要专业，
培训要清晰易学。

## SVG说明

场景标签只做 `scenario-tag` 或 `eyebrow`，不要抢 `main-title`。每页至少保留标题、
核心结论、证据或行动。
