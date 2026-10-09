# 叙事与形状

用户已经规定页数和顺序时，不改页序，也不另起章节。用户要求保持原稿用词、每个点各做一页，或把页面做满时，同样按下面四格写。原稿里的专门叫法只放 `label`。

这些键名原样出现在大纲种子或 `page_spec` 里：`thesis`、`audience_decision`、`evidence_ladder`、`proves`、`dominant`、`attached`、`label`。标题和口述是另外两行。

## Deck contract

大纲开始前先写整册合同：

```yaml
thesis: "整册只回答一个判断"
audience_decision: "会议结束前要拍板的事项；用户没要求拍板时写 本次不拍板"
evidence_ladder: [external_fact, internal_observation, proposal, pilot_target]
canonical_metrics: []
canonical_products: []
canonical_artifacts: []
canonical_stages: []
canonical_owners: []
reference_assets: []
```

`evidence_ladder` 让外部事实、内部观察、方案建议和试点目标不再使用同一种语气或视觉重量。每页都要能接入 `claim→evidence→action→validation→decision`：没有上游证据的方案降为假设，没有下游动作的背景页补证据、合并或删除。`canonical_*` 是跨页唯一清单，产品、指标、工件、阶段和 Owner 不能在后续页面临时改名。

以上是内容部分；开始制作前再按 [全局视觉系统](../visual-system.md) 填写整册 `visual_system` 和逐页 `visual_brief`，将用户参考及样例的视觉规则接入每页设计。

## 调研和规范怎么写

用户要的是产品调研和未来规范，材料里没有内部账本，也没有要求当场拍板。按下面这一册的写法往下做。

```yaml
thesis: "公开实验只覆盖单次写码，全流程用法还要单独定"
audience_decision: "本次不拍板"
canonical_metrics: ["单次写码用时", "熟手任务用时"]
canonical_products: ["GitHub Copilot", "Cursor"]
```

`单次写码用时` 来自材料里的实验。产品名留到对照页展开：每家写它覆盖哪一段、权限和数据落在哪、怎么验证。

证据页这样写：

```yaml
title: "公开实验证明的是单次写码，不是整段交付"
proves: "公开实验只覆盖单次写码"
dominant: "不可比证据"
frames:
  - {label: "实验", claim: "同一道新任务，处理组更快", bound: "不能外推到老库和发布"}
  - {label: "熟手老库", claim: "允许使用工具的任务更慢", bound: "样本后来有选择偏差"}
  - {label: "调查", claim: "自报吞吐上升，稳定相关为负", bound: "这是相关，不是这家组织的数"}
```

四块外框各写自己的口径。数字贴在对应口径旁边。

对照页这样写：

```yaml
title: "先换工具和先定交接，不是同一条路"
proves: "全流程用法还要单独定"
dominant: "左右对照"
panels:
  - {title: "先换工具", sentence: "成绩会被看成采纳了多少建议。"}
  - {title: "先定交接", sentence: "成绩会被看成每一段有没有留下记录。"}
boundary: "两条路都还不是内部观察"
```

左块和右块各是一块面板，分界上写本页结论。

规范页这样写：

```yaml
title: "六段交接里，评审和发布还接不上"
proves: "全流程用法还要单独定"
dominant: "流程断点"
steps:
  - {name: "需求澄清", sentence: "任务单还没有同一套字段。"}
  - {name: "变更评审", sentence: "没有人读过差异，就不知道模型改了什么。"}
  - {name: "发布回看", sentence: "线上问题不会回到下一张任务单。"}
```

每一段写交出什么、谁接着用。没有内部样本的段，先点明它依据的是哪条公开事实，再写成建议。

画完按 [全局视觉系统](../visual-system.md) 把箭头段和对照块放进 SVG。

## 四格

1. 第一页写 `thesis=`，只留一个判断：谁，在什么场合，要决定什么。后面各页才要证明的发现不要用逗号串进这句。最后一页的口述以这句 thesis 原样开头，后面接决定（做、不做，或有条件做）。
2. 中间每一页写 `proves=`，等于 thesis 按逗号或句号切开后的一个分句。不从句子中间切四个字。
3. 每一页以 `dominant=` 开头，从下面的信息关系中选一个，并写出它由哪些相连证据区组成。最多再写 3 个 `attached=` 合同项。`dominant` 是叙事主线，不是单个几何对象；需要的背景、机制、指标和行动可以占多个区域，但不能各说一个无关结论。
4. 标题和口述只写具体的人和事：谁做了什么，哪一步断了，下一步做什么。原稿标题和要点里用来起名的组合整段放进 `label`，不留在 thesis、标题和口述里。盖住 `label` 之后，口述仍然完整。

每页正文的最小合同是：

```yaml
primary_claim: "一句且仅一句判断"
key_message: "与 primary_claim 同义的口述"
proves: "thesis 的一个分句"
dominant: "不可比证据|流程断点|左右对照|门禁|决定章|成效看板|诊断链|阶段路线|机制架构|决策矩阵"
attached: ["口径/限制", "来源/工件", "行动/决策"]
claim_type: "external_fact|internal_observation|proposal|target|to_validate"
evidence_type: "实验/调查/内部基线/公开资料/政策/专家输入"
evidence_state: "FACT|OBSERVED|PROPOSAL|TARGET|TO_VALIDATE"
```

`attached` 最多 3 项，用于记录口径、限制和行动，不是页面可见证据区的数量上限。第二排可以承载指标、案例、根因或退出条件，但须解释第一排并有阅读关系。缺少本页专属证据、限制和动作时，不得用整册默认 `metrics`、`evidence_boundary` 或 `action` 补齐。

如果 `reference_assets` 非空，每个正文页再写 `reference_dna`，说明复用了哪些面板层级、关系连接、组件语法或阅读节奏；只复用颜色不算参考图复用。

| dominant | 形状分成哪几块 |
| --- | --- |
| 不可比证据 | 几块不同外框，外框上写清各自口径；不要排成等高数字条 |
| 流程断点 | 一条箭头链。每一段是 `process-step`，里面有一句，不只写阶段名；断点做成缺口 |
| 左右对照 | 左右两块 `comparison-panel`，各有一句。原生表不能代替这两块 |
| 门禁 | 一串门；没有名字或阈值的门留空 |
| 决定章 | 一个大章，条件是章上的小标签 |
| 成效看板 | 背景/口径、举措、指标/小图、推论四层；至少两层有可见连接 |
| 诊断链 | 现象、根因或待核实假设、整改、验证/目标按证据状态递进 |
| 阶段路线 | 阶段轴与各阶段动作、产出、Owner/风险、退出条件对齐 |
| 机制架构 | 中央层级/网络/循环与两侧输入输出或责任、底部护栏相连 |
| 决策矩阵 | 选择轴、证据行列、取舍标准和后续复核条件共同说明决定 |

后五种的区域与容量见 [蓝色高密度复合页型](../blue-dense-report.md)。行列比较、需要编辑的明细仍用原生表格；表格可以是证据主区，但其标题、判断、口径与决策不能消失。`check_shape_picture.py` 对原有的左右对照、流程断点检查局部几何；新增关系的复合结构须对最终预览逐页核对，不能以脚本无报错代替视觉证明。

## 例子

thesis=华东增长填不上华北下滑，全国目标仍差一截

PAGE 3
TITLE: 华北在掉，华东的增长填不上
OBJECTS: dominant=左右对照 proves=华东增长填不上华北下滑 左=华东销售额升 右=华北销售额降 分界=全国仍未达标 attached=两个区域分开报 attached=目标完成率是内部测算 label=原稿称结构性对冲
SAY: 华东在涨，华北在掉，全国目标还是没到。

最后一页口述必须以「华东增长填不上华北下滑，全国目标仍差一截」开头。
