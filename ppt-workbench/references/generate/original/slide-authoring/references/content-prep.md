<!--
id: content-prep
category: content-structure
read_when: 需要观点、理由、案例、重申
page_roles: content
supports: svg_drawingml
outputs: content_slots
depends_on: contract-content-density.md
max_use: 只读取本文件，不要连带读取同类全部文件
-->

# Content: PREP

## 内容说明

结构：Point 观点 -> Reason 理由 -> Example 案例 -> Point 重申。

模板：

```text
观点：我们判断 [X] 是下一阶段突破口。
理由：因为 [A/B/C]。
案例：以 [项目/客户/场景] 为例，已验证 [结果]。
重申：因此建议 [动作/资源/决策]。
```

## 视觉说明

左侧主观点，右侧理由/案例/行动三块，底部重申结论。

## SVG说明

分组：`point-panel`、`reason-card`、`example-card`、`action-card`。
