# 运行环境与准备

单独取得整个 `ppt-workbench/` 目录即可。不需要 Ubrio、其他技能、PG、Redis、账号、私有 SDK 或全局 Node 包。宿主负责文件读取、授权执行与查看预览。

## 依赖

| 用途 | 本次锁定或实测 | 准备与限制 |
| --- | --- | --- |
| 原生 PPTX | Node >=20；实测24.14.0；PptxGenJS 4.0.1 | package-lock.json 锁定直接和传递依赖 |
| 字体度量 | fontkit 2.0.4 | 读取用户已安装的字体，不附带字体文件 |
| OOXML结构检查、转换包装 | Python >=3.10，标准库 | 不安装整个项目 Python 环境 |
| 可选渲染支线 | 本次选择 LibreOffice 26.2.2.2、Poppler pdftoppm | 非必需、不随包安装；已有宿主预览/Office能力可替代 |
| 字体 | 本次实测 Arial Unicode MS | 宿主已有授权安装；不嵌入、不复制或分发系统字体 |
| 可用时的目视检查 | 宿主图片查看能力 | 缺少时仍可交付PPTX，明确视觉未验证 |

在安装阶段由用户或宿主按权限准备依赖，不能在每次制作中悄悄安装或下载 latest。

```bash
# SKILL 为用户放置的独立包路径；不是用户 PPT 工程目录。
npm ci --prefix "$SKILL" --ignore-scripts --no-audit --no-fund --workspaces=false
node --version
python3 --version
```

只读安装：在可写的暂存副本中准备好依赖，然后将整个包及其 `node_modules` 放到只读位置。任务源码和输出写到另外的获授权工作目录。脚本按自身位置查依赖，不在用户材料目录创建依赖、缓存或修改全局配置。`npm` 下载需安装阶段的明确网络许可。

`NativeDeck` 显式接收 `fontPath`，字体集合另给 `fontName`（PostScript 名最准确）；度量的 family 写入 PPTX。缺字体、缺字形或名称不一致会报错，不默默换字体。字体只用于度量，不自动安装或打包；Office 端仍需相应字体，字体度量不能替代实际渲染。

## 主线最小自检（无需 Office）

```bash
node "$SKILL/assets/examples/make_examples.cjs" \
  --font-path "$FONT_FILE" --font-name "$FONT_NAME" \
  --case 03-target --output-dir "$OUTPUT_DIR"
python3 "$SKILL/scripts/inspect_pptx.py" "$OUTPUT_DIR/03-target.pptx"
```

以上即可得到原生可编辑PPTX与对象检查结果。不会探测或启动LibreOffice。字体文件是度量输入，字体授权安装由用户选择，不代表需要Office或LibreOffice。

预览另按 [可选预览](preview-options.md) 选择宿主已有能力。仅主动选择LibreOffice分支且其已安装时运行：

```bash
python3 "$SKILL/scripts/optional/render_with_libreoffice.py" "$OUTPUT_DIR/03-target.pptx" \
  --output-dir "$PREVIEW_DIR" --soffice "$SOFFICE"
```

输出目录和文件名由任务决定。生成拒绝覆盖已有 PPTX，可选渲染拒绝已有预览目录；需修订时另选位置。可选渲染器只写隔离临时目录和指定输出目录，不改 PPTX 字体或源文件。外部资源关系、损坏包和缺依赖会阻止该分支，但不阻止其他预览方式或已完成PPTX交付。

## 已发现的环境差异

当前 macOS + LibreOffice 26.2.2.2 渲染 Hiragino Sans GB W3 时普通中文笔画有缺损，结构检查不能发现。改用当前机器已有的 Arial Unicode MS 后样例中文正常。不能把所有已安装的 CJK 字体视为渲染质量等价；在用户环境先做含常用中文、数字、单位的 canary，再跑实际页。

脚本不内置本机路径。缺可用字体或预览能力时，返回明确的未验证/未完成说明，不宣称达成最终视觉质量。
