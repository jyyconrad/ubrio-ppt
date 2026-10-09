# 来源、依赖与许可说明

## 原始资料

本包保留了以下原始技能目录的逐字节副本：

- 源路径：`backend/resources/agent-content/skills/file-processing/`
- 包内路径：`references/original/file-processing/`
- 排除项：无

副本中的 `SKILL.md`、工具名、阶段、`material_id` 和 SubAgent 协作说明属于原应用运行时背景，仅作为来源资料保存，不会被本技能入口自动执行。

逐文件 SHA-256 清单见 [source-manifest.sha256](source-manifest.sha256)。本包测试会比较源目录与副本；公开分发时无法访问原仓库的用户仍可使用副本和独立脚本。

## 依赖

脚本只使用 Python 标准库处理 TXT、Markdown 和 CSV。以下公开 PyPI 包仅在读取对应格式时需要，版本固定在 `requirements.txt`：

- `openpyxl`：XLSX
- `python-pptx`：PPTX
- `python-docx`：DOCX
- `pypdf`：文本型 PDF

这些依赖的许可证由各自项目提供；安装和再分发前应核对相应版本的上游许可。脚本不导入 Ubrio 应用代码。

## 权利状态

仓库当前未提供足以授予这些原始技能资料公开再分发权利的许可证。原始资料及本整理包目前仅用于内部准备，**不得据此宣称可公开分发**。该说明不是新的许可授权，也不改变第三方依赖或用户材料的权利状态。
