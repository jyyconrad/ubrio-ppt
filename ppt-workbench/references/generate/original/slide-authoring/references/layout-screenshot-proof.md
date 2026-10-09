<!--
id: layout-screenshot-proof
category: layout
read_when: 截图证明、系统记录、案例证据、材料截图占位
page_roles: content
supports: svg_drawingml
outputs: svg_layout, evidence_asset_slots
depends_on: contract-layout-density.md
relation_specs: requires:contract-gold-svg-builder, requires:structure-hierarchy
max_use: 只读取本文件，不要连带读取同类全部文件
-->

# Layout: Screenshot Proof

## 内容说明

左侧写主判断和证据解读，右侧留截图/系统记录占位。截图必须有来源、时间、口径和说明。

## 视觉说明

截图区域像证据框，不像装饰图。边框、标题、标注线和结论标签要把“证明了什么”说清楚。

## SVG说明

按 1280×720 画布用比例/安全区描述左右分栏，不写死坐标：

- 左栏 `proof-claim`：占左侧约 40%W，纵向从标题带下方延展至底部安全区，写主判断与证据解读。
- 右栏 `screenshot-proof-1`：占右侧约 55%W 的主体高度，作截图/系统记录证据区。
- 截图占位用 `rect fill="none"`，可加 `data-role="evidence-asset-slot"`。
- 右栏底部留一条 `proof-source`（约 0.95H 一线），写来源、时间、口径。

分组命名：`proof-claim`、`screenshot-proof-1`、`proof-callout-1..N`、`proof-source`。

禁止：不要伪造截图内容。没有真实截图时不写“待补截图/来源/时间”等草稿词（最终态硬禁词，会被自检拦截）——改走两条降级路径之一：(a) 通过 ask_user 补齐真实截图；(b) 降级为口径明示的能力示意结构，用真实可讲的能力/流程要点画示意图并加“能力示意，非真实统计”类口径徽章，占位框可保留但不落任何“待补”类文案。
