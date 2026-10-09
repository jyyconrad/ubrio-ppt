# 蓝色高密度汇报页示例

本目录提供一个仓储订单运营复盘的合成演示页。`result-dashboard.page_spec.json` 是完整金标规格，`result-dashboard.builder.svg` 是 `build_gold_svg_page.py` 依据该规格生成的起始 SVG，`result-dashboard.svg` 是在起始结构上按参考 DNA 重新分区和精排后的 1280×720 最终主稿。精排保留同一主观点、四项证据和三项行动，但改变了几何关系、图表编码和视觉层级。

`deck-manifest.json` 与同一份 page spec 也通过整册合同校验；其中 `proves`、证据角色、baseline、密度预算和人话复述均是作者元数据，不会自动改动 SVG。制作新任务时整体替换事实和 canonical 清单，不能只复制“通过”字段。样例中的小柱形是可编辑前后对比标记；需要坐标轴、序列或数据表的真实图表走 native chart slot。

`result-dashboard.pptx` 由候选技能包的 SVG → DrawingML 管线从最终主稿实际生成，所有文字、底板、柱形、连线与图标均为可编辑对象；`result-dashboard.png` 来自该最终 PPTX 的 macOS Quick Look 实际渲染，不是 SVG 截图。

## 字段槽位

| 区域 | 必填字段 | 容量建议 |
| --- | --- | --- |
| 结论标题 | 一句可由本页证据直接支持的判断 | 24–32 个汉字，避免口号与未经证实的因果 |
| 口径细条 | 范围、期间、比较基准、证据边界 | 3 项，单项 8–16 个汉字 |
| 行动机制区 | 行动名、具体做法、观察点 | 3 项；行动名 4–8 字，做法不超过两行 |
| 指标复合区 | 指标名、起点、当前、单位、变化量 | 4 项；每项配同尺度的简图或可直接比较的刻度 |
| 底部洞察条 | 本页含义、下轮动作或决策请求 | 主句 1 行，补充 1 行 |

## 适用条件

- 适合经营复盘、项目进展、专项改善、供应链与运营类汇报。
- 一页需要同时回答“做了什么、结果怎样、下一步怎么复盘”，且有 3 项左右的机制和 4 项左右的量化指标。
- 指标必须有清楚的单位、期间与比较基准。样例数字全部标为“合成演示”，不能被当作真实经营数据。
- 指标同期改善只能写成并列观察；没有实验、分组或过程证据时，不把行动写成改善结果的原因。

## 参考 DNA

参考 `汇报模板-p4.jpg` 与 `汇报模板-p10.jpg` 的可迁移视觉规律：白底深蓝结论标题、细线分区、行动机制横向编排、指标卡与微型图表组合、底部深蓝洞察条。页面至少形成标题、口径、机制/指标、洞察四层层级；统一 4px 圆角、细描边和 24–30px 区域间距，使高密度仍可扫描。

可以改：业务主题、标题结论、行动数量（2–4 项）、指标数量（3–6 项）、单位、图形尺度、强调色、底部行动文案，以及左右区域宽度。

不可照抄：参考图片里的项目名称、原始指标、结论、图标造型、水印、页码与任何品牌元素；也不能照抄样例中的合成数据到真实汇报。结构学习必须与事实来源分开。

## 验证命令与本次结果

```bash
python scripts/svg/validate_svg_drawingml.py \
  --svg assets/examples/blue-dense/result-dashboard.svg \
  --mode full \
  --assets-dir assets/examples/blue-dense

python scripts/svg/build_gold_svg_page.py \
  --spec assets/examples/blue-dense/result-dashboard.page_spec.json \
  --validate-only

python scripts/validate_deck_contract.py \
  --manifest assets/examples/blue-dense/deck-manifest.json \
  --page-spec assets/examples/blue-dense/result-dashboard.page_spec.json

python scripts/svg/render_svg_drawingml.py \
  --svg assets/examples/blue-dense/result-dashboard.svg \
  --output assets/examples/blue-dense/result-dashboard.pptx \
  --assets-dir assets/examples/blue-dense

python scripts/inspect_pptx.py \
  assets/examples/blue-dense/result-dashboard.pptx

qlmanage -t -s 1280 \
  -o assets/examples/blue-dense/preview \
  assets/examples/blue-dense/result-dashboard.pptx
```

本次 `build_gold_svg_page.py --validate-only` 返回 `quality_status=ready`，全量 SVG DrawingML 预检无 issue、无 warning。PPTX 为 1 页 16:9，包含 51 个文本节点、114 个原生形状、0 张整页图片，文本和形状保持 DrawingML 可编辑。最终 PNG 由同一 PPTX 经 Quick Look 转换并按 1280×720 目检，中文可读、无重叠、无越界。LibreOffice 26.8 的本机预览未正确映射 CJK 字体，因此未作为最终验收图。具体命令输出以同目录 `validation-results.txt` 为准。
