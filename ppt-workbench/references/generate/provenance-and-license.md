# 来源、版本与再分发状态

本包版本 0.2.0，随 https://github.com/jyyconrad/ubrio-ppt 发布。仓库根 LICENSE 的 MIT 适用于本技能自行编写的说明、脚本和合成样例；第三方组件、图标、图片和版式参考仍保留各自许可，见仓库 THIRD_PARTY_NOTICES.md。不能把第三方许可改写成仓库许可，也不能把合成样例说成真实客户案例。

- 原始方法、索引、脚本与资产完整来源映射和逐文件哈希见 [source-map.md](source-map.md) 与 [original-manifest.json](original-manifest.json)。保留原文不等于认可平台专用指令可执行。
- `scripts/native.cjs`、`inspect_pptx.py`、可选的 `scripts/optional/render_with_libreoffice.py` 和合成样例是本次新整理的独立实现；未导入 Ubrio 应用代码、私有 SDK 或兄弟技能。
- PptxGenJS 4.0.1、fontkit 2.0.4 使用公开 npm 依赖，精确依赖树见 package-lock.json。上游项目标为MIT；本包不据此对原始资料和其他资产授予MIT许可。
- LibreOffice、Poppler、字体为用户独立安装的系统组件，不随包再分发。字体实际仅用于度量和渲染，本包不复制或嵌入系统字体文件。
- `assets/examples/cases.json` 是明确标注的合成业务数据；`evidence-synthetic.png` 来自对应合成台账PPTX的实际渲染，不是真实客户截图。源码、PPTX、PNG共同用于验证，不得包装成客户案例。

相关上游：[PptxGenJS](https://github.com/gitbrent/PptxGenJS)、[fontkit](https://github.com/foliojs/fontkit)、[LibreOffice](https://www.libreoffice.org/about-us/licenses/)、[Poppler](https://poppler.freedesktop.org/)。安装依赖时保留各依赖自带许可。合成内容无真实客户敏感数据。
