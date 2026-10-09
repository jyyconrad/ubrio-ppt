# 来源、版本与再分发状态

本包版本 0.1.0，状态为内部整理候选；没有自动公开发布或授予开源许可。

- 原始方法、索引、脚本与资产完整来源映射和逐文件哈希见 [source-map.md](source-map.md) 与 [original-manifest.json](original-manifest.json)。保留原文不等于认可平台专用指令可执行。
- `scripts/native.cjs`、`inspect_pptx.py`、可选的 `scripts/optional/render_with_libreoffice.py` 和合成样例是本次新整理的独立实现；未导入 Ubrio 应用代码、私有 SDK 或兄弟技能。
- PptxGenJS 4.0.1、fontkit 2.0.4 使用公开 npm 依赖，精确依赖树见 package-lock.json。上游项目标为MIT；本包不据此对原始资料和其他资产授予MIT许可。
- LibreOffice、Poppler、字体为用户独立安装的系统组件，不随包再分发。字体实际仅用于度量和渲染，本包不复制或嵌入系统字体文件。
- `assets/examples/cases.json` 是明确标注的合成业务数据；`evidence-synthetic.png` 来自对应合成台账PPTX的实际渲染，不是真实客户截图。源码、PPTX、PNG共同用于验证，不得包装成客户案例。
- 原技能的第三方模板、截图、图标、案例、知识文本和脚本可能具有不同许可。未逐项核清的资产不适合直接公开；本次复制用于用户授权的仓库内整理，不能声称已通过完整权利审查。

禁止公开打包之前，维护者需为每项受限资产补充可再分发依据，或经权利人/用户确认剔除并记录对完整收录与执行能力的影响。不能偷偷删除原件的来源或把所有文件改写成新许可。

相关上游：[PptxGenJS](https://github.com/gitbrent/PptxGenJS)、[fontkit](https://github.com/foliojs/fontkit)、[LibreOffice](https://www.libreoffice.org/about-us/licenses/)、[Poppler](https://poppler.freedesktop.org/)。安装依赖时保留各依赖自带许可。合成内容无真实客户敏感数据，但仍待仓库权利人决定本包的正式发布许可。
