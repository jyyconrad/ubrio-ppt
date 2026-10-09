# 依赖、来源与许可

## 默认纯 PPTX 路径

| 依赖 | 固定/验证版本 | 用途 | 许可/来源 |
| --- | --- | --- | --- |
| Python | 3.12.8 | CLI、只读预检、页数与尺寸校验 | Python Software Foundation License |
| python-pptx | 1.0.2 | 读取 PPTX，拒绝宏、损坏或不支持输入；不负责跨文件复制 | MIT；https://github.com/scanny/python-pptx |
| Node.js | 24.14.0 | 运行合并器 | Node.js license；https://github.com/nodejs/node |
| pptx-automizer | 0.9.3 | 模板式跨 deck 页面导入、顺序与关系复制 | MIT；https://github.com/singerla/pptx-automizer |

默认依赖在技能目录的本地虚拟环境安装：

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
npm ci --ignore-scripts --no-audit --no-fund --workspaces=false
```

Node 依赖由根目录 `package.json` 和 `package-lock.json` 固定。不全局安装，不在普通任务执行期间隐式联网安装。

## 可选转换支线

| 依赖 | 参考验证版本 | 用途 | 许可/来源 |
| --- | --- | --- | --- |
| LibreOffice | 26.2.2.2 | 显式选择时 PPTX 转 PDF | MPL-2.0；https://www.libreoffice.org/about-us/licenses/ |
| Poppler `pdftoppm` | 25.08.0 | 显式选择时 PDF 分页转 PNG | GPL-2.0-or-later；https://poppler.freedesktop.org/ |
| pypdf | 6.11.0 | PDF 实际页数检查 | BSD-3-Clause；https://github.com/py-pdf/pypdf |

LibreOffice 与 Poppler 不是默认必装依赖。转换优先使用宿主或用户已有能力；只有传 `--backend libreoffice` 时才探测。参考实测使用稳定 LibreOffice 26.2.2.2；PATH 中 bundled alpha 不计入证据。

需要该可选支线时，在同一个本地 venv 中运行：`.venv/bin/python -m pip install -r requirements-export.txt`。`pypdf` 在转换分支内懒导入，未安装不会影响 preflight 或 merge。

## 调研结论

- `python-pptx` 没有成熟的跨 presentation 整页复制 API，因此仅用于输入检查。
- 计划举例的 `pptxcompose` 未在公开 Python 包索引找到可安装发行版，未采用。
- LibreOffice UNO shape 搬运不能证明 notes、masters、chart workbook 与全部关系保留，实验实现已删除。
- `pptx-automizer@0.9.3` 官方文档说明 template/root 模型、按调用顺序导入 slide、charts、images、masters/layouts；官方也列出特殊关系与复杂 layout 限制。本技能仅声明实际样例验证的静态子集。
- 商业 SDK 未纳入，避免未确认的许可、费用和部署边界。

公开发布仍需保留第三方许可与来源说明；本仓库没有授予第三方内容新的许可。
