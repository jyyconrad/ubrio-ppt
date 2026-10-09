# 快速使用手册

## 这个技能做什么

ppt-workbench 用来做中文业务汇报：结论先行，一页一个主观点，图表、表格、流程和指标用可编辑对象。适合客户介绍、经营复盘、项目汇报、方案汇报、年度总结。不负责普通代码开发。产物写到你指定的任务目录，不写回技能目录。

## 安装

主路径用 skills CLI（来自 https://github.com/vercel-labs/skills）：

```bash
npx skills add jyyconrad/ubrio-ppt
```

指定宿主时：

```bash
npx skills add https://github.com/jyyconrad/ubrio-ppt/tree/main/ppt-workbench -g -a claude-code -a codex -a grok -y
```

也可以把仓库里的 `ppt-workbench/` 整个目录复制到宿主的技能目录：

- Claude Code：`~/.claude/skills/ppt-workbench`
- Codex：`~/.codex/skills/ppt-workbench`（skills CLI 的 Codex 全局目录也可能是 `~/.agents/skills/ppt-workbench`）
- Grok：`~/.grok/skills/ppt-workbench`

Claude Code 还可以把仓库登记为插件市场：

```text
/plugin marketplace add jyyconrad/ubrio-ppt
```

目录名必须是 `ppt-workbench`，因为 SKILL.md 的 name 必须和父目录同名。装好后确认该目录里有 `SKILL.md`，再新开一轮对话，让宿主重新发现技能。

## 准备依赖

在技能根目录（含 `SKILL.md`、`requirements.txt` 和 `package.json` 的那个 `ppt-workbench/`）执行：

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
npm ci --ignore-scripts --no-audit --no-fund
```

需要 Python 3.10+ 和 Node.js 20+。LibreOffice 只用于可选预览，不是安装前提。字体使用机器上已经安装的中文字体，技能不附带字体文件。

依赖可以留在技能目录。纪要、数据和成品 PPTX 不要放这里，另建一个任务目录。

## 怎么开口

把材料放进任务目录，然后把下面任意一条直接发给 Agent。每条都要求可编辑 PPTX，并要求保留口径、单位和证据边界，不要编造客户案例。

> 请使用 ppt-workbench。阅读任务目录里的 `纪要.md`，做成 8 页经营复盘，输出可编辑 PPTX 到任务目录的 `经营复盘.pptx`。结论先行，一页一个主观点。只用纪要里的事实和数字，保留原有口径、单位和证据边界；纪要没写的原因和客户案例不要编造。做完后运行技能里的 `scripts/inspect_pptx.py`。没有预览时说明已检查对象、尚未完成视觉验收。

> 只改任务目录 `经营复盘.pptx` 的第 3 页，其他页不动。结论改为「毛利率较上季下降 1.8 个百分点；折扣加深仍待核实，费用口径未变」。这一页的数字只改为上季 18.2%、本季 16.4%，单位仍是「%」，口径仍是「不含税毛利率」。不要把待核实写成已证实原因，不要编造客户案例。另存为任务目录里的可编辑 PPTX `经营复盘-修订.pptx`，不要覆盖原文件。做完后运行 `scripts/inspect_pptx.py`。

> 把任务目录里的 `上半年.pptx`、`三季度.pptx`、`四季度.pptx` 按这个页序合并成一份可编辑 PPTX，写到任务目录的 `全年合并.pptx`。不要改各页正文，保留每一页原来的口径、单位和证据边界，不要补写或编造客户案例。合并后对最终文件运行 `scripts/inspect_pptx.py`。

> 用下面这组数据做一页可编辑 PPTX，图表必须是原生折线图，不要用图片或手绘折线代替。输出到任务目录的 `毛利率走势.pptx`。标题写结论。口径写「毛利率，不含税，自然季度」，单位写「%」，来源写「内部经营月报，2025Q1–Q4」。材料只给了变化、没给原因，就标明原因待核实，不要编造客户案例。做完后运行 `scripts/inspect_pptx.py`。数据：2025Q1 18.2，Q2 17.6，Q3 16.4，Q4 16.9。

## 你会得到什么

一页或整册 `.pptx`。正文默认走金标 SVG，再转成可编辑 DrawingML；图表、表格、图片是原生对象，可在 PowerPoint 或 WPS 里改文字和数据。做完后 Agent 应运行技能里的 `scripts/inspect_pptx.py`。没有预览时要说明已检查对象、尚未完成视觉验收。大纲、SVG 或 PNG 不能代替这份 PPTX。

## 效果图

![技能实际导出的经营复盘页](screenshots/01-skill-export-operating-review.png)

[01-skill-export-operating-review.png](screenshots/01-skill-export-operating-review.png)：技能实际导出的经营复盘页。标题是结论，行动和指标对比是可编辑对象；页内数字标为合成演示，不是真实客户。

![七阶路线版式参考](screenshots/04-roadmap.jpg)

[04-roadmap.jpg](screenshots/04-roadmap.jpg)：七阶路线版式参考。上方是七个门径，中间对比串行与并行，下方用周期和变更说明效果。

![指标盘版式参考](screenshots/05-metric-dashboard.jpg)

[05-metric-dashboard.jpg](screenshots/05-metric-dashboard.jpg)：指标盘版式参考。上半部分并列效率与质量趋势，下半部分把一次延期拆到根因和整改。

其余高密度版式见 [效果图说明](screenshots/captions.md)。

后两张是包内高密度版式参考，页脚可能保留原图水印，不是交付稿，数字都是演示。做自己的页时只借用分区和阅读顺序，换成你的材料和口径。

## 不要这样做

- 不要把整页截图、大标题加一句口号当成正文页。
- 不要把合成样例说成真实客户。
- 不要在没有证据时写因果结论。
- 不要把产物写进技能安装目录。

## 进一步阅读

- [技能入口](../SKILL.md)
- [运行环境与准备](../references/generate/setup.md)
- [单页制作方法](../references/page-generation.md)
- [质量门与回归](../tests/README.md)

普通做页不用跑 `tests/`。那一组检查给改技能、脚本或示例的人用。
