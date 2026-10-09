# 本地提取器说明

## 适用范围

`scripts/extract_materials.py` 是有界、只读的材料提取工具。普通文本任务无需安装完整依赖；Office/PDF 文件按需安装 `requirements.txt` 中的公开依赖。

## 常用命令

```bash
SKILL_DIR="/path/to/ppt-materials"

# 单个文件，打印 Markdown 到标准输出
python "$SKILL_DIR/scripts/extract_materials.py" "材料/经营说明.md"

# 只读指定工作表
python "$SKILL_DIR/scripts/extract_materials.py" "经营数据.xlsx" --sheet "区域销售"

# 只读 PDF/PPTX 的第 8-12 页
python "$SKILL_DIR/scripts/extract_materials.py" "调研报告.pdf" --pages 8-12

# 从 DOCX/PPTX 提取可访问图片；PDF 当前不支持图片提取
python "$SKILL_DIR/scripts/extract_materials.py" "参考稿.pptx" --extract-images extracted-images
```

## 按需安装解析依赖

TXT、Markdown 和 CSV 只使用 Python 标准库，不需要安装附加包。读取 XLSX、PPTX、DOCX 或 PDF 时，在当前任务目录创建独立 venv，并从单包内固定版本清单安装；不要安装到全局 Python，也不要假定技能目录可写：

```bash
SKILL_DIR="/path/to/ppt-materials"
VENV_DIR="$PWD/.venv-ppt-materials"

python -m venv "$VENV_DIR"
"$VENV_DIR/bin/python" -m pip install --disable-pip-version-check -r "$SKILL_DIR/requirements.txt"
"$VENV_DIR/bin/python" "$SKILL_DIR/scripts/extract_materials.py" "经营数据.xlsx"
```

`requirements.txt` 使用精确版本号锁定解析依赖。创建 venv 和安装包会访问本地 Python/pip 配置及用户明确配置的软件源；技能不会自行安装、升级或隐式联网。Windows 宿主使用对应 venv 的 `Scripts/python.exe`。

`--include` 接受逗号分隔的扩展名，例如 `.pdf,.xlsx`。`--max-chars` 是每个文件的文字上限，达到后会在输出中标记截断。页码按用户习惯从 1 开始；空页码、超过 100000 的页码、单个范围或最终集合超过 10000 页都会在范围物化前拒绝。

## 定位与警告

- 文本/Markdown：行号区间。
- CSV：行号；解析遵守 CSV 引号规则。
- XLSX：工作表名和实际读取单元格范围；公式缓存缺失单独列出。
- PPTX：幻灯片页码、形状或表格序号；备注按页记录。
- DOCX：段落号和表格号；DOCX 本身不保存可靠的最终分页，因此不伪造页码。
- PDF：真实 PDF 页码；页面无可提取文字时提示扫描件或字体编码风险。

脚本不会运行宏、刷新外部链接、计算公式、OCR、联网或修改输入文件。加密、损坏、依赖缺失和不支持格式均以非零退出码或文件级错误呈现。公式重算、OCR 和渲染可由宿主按需提供，但不是本技能依赖，也不要求安装 Microsoft Office 或 LibreOffice。

输入文件、OOXML ZIP 成员数和展开总量在解析前有默认上限，可用 `--max-input-bytes`、`--max-ooxml-members`、`--max-ooxml-expanded-bytes` 进一步收紧。目录发现跳过所有符号链接，避免越出用户指定目录。
