<!--
id: chinese-business-ppt-case-templates
category: compatibility-index
runtime_scope: legacy
skill_kind: compatibility_index
read_when: 旧提示要求实践案例、场景大纲或单页执行模板
page_roles: content, section_divider, summary
supports: svg_drawingml
outputs: scenario_reference_route
depends_on: _index/capability-tree.json
max_use: 只读取本索引和 1 个 scenario-* 文件，不要读取全部案例
-->

# Chinese Business PPT Case Templates

本文件是旧案例入口。具体场景模板已拆到 `scenario-*` 文件。

## 内容说明

标准工作流：场景判断 -> 结构生成 -> 单页内容+布局 -> 视觉风格建议 -> SVG输出。

单页执行模板：

```text
页面角色：[内容页/过渡页/总结页]
场景：[年终总结/项目汇报/融资路演/...]
本页观点：[一句判断标题]
论证结构：[金字塔/PREP/对比/SCQA/SWOT/3C/PEST]
内容组：[短标题 + 判断句 + 2-3 条证据 + 动作/风险]
布局：[layout-*]
视觉 token：[background/surface/title_text/body_text/source_text/accent/border]
SVG 落地：[main-title/key-message/content-group-*/actions/source-note]
```

## 视觉说明

模板只决定页面逻辑，不决定最终配色。最终配色服从 deck 主题和 `contract-visual-token.md`。

## SVG说明

不要把模板说明文字写进 SVG，只写当前页真实业务内容。
