# 运行说明

所有路径以本技能目录为准。当前安装在 `~/.codex/skills/ppt-workbench`；该目录是独立副本，不依赖源码仓库或 Ubrio 服务。

```bash
PPT_WORKBENCH="$HOME/.codex/skills/ppt-workbench"
PPT_PYTHON="$PPT_WORKBENCH/.venv/bin/python"
```

## 已准备的主线依赖

- 根目录 `.venv`：固定版本的 python-pptx、openpyxl、python-docx、pypdf，用于素材读取与 PPTX 合并预检；精确版本见 `requirements.txt`。
- 根目录 `node_modules`：PptxGenJS 4.0.1、fontkit 2.0.4、pptx-automizer 0.9.3，按根目录 `package.json` 和锁文件准备。
- Node 使用宿主已有运行时；对象检查仅需 Python 标准库。字体读取用户已有授权字体，不复制、下载或嵌入字体。

本技能保留各能力的安装说明，并优先使用根目录已准备的依赖，无需每次任务重复安装。纯文本和大纲任务不必启动其他工具。

## 常用命令

```bash
# 素材提取，范围参数见 references/materials/guide.md。
"$PPT_PYTHON" "$PPT_WORKBENCH/scripts/extract_materials.py" "$INPUT_FILE"

# 正文页默认：金标 SVG → DrawingML PPTX。完整顺序见 references/generate/methods/authoring-and-checks.md。
"$PPT_PYTHON" "$PPT_WORKBENCH/scripts/svg/validate_svg_drawingml.py" --svg "$PAGE/source.svg" --mode full
"$PPT_PYTHON" "$PPT_WORKBENCH/scripts/svg/render_svg_drawingml.py" --svg "$PAGE/source.svg" --output "$SLIDE_PPTX"

# 检查最终 PPTX 对象，无需 Office。
"$PPT_PYTHON" "$PPT_WORKBENCH/scripts/inspect_pptx.py" "$PPTX_FILE"

# 合并已有文件，保留原生对象。
"$PPT_PYTHON" "$PPT_WORKBENCH/scripts/merge_export.py" merge \
  --input "$INPUT_A" --input "$INPUT_B" --output "$OUTPUT_PPTX"
```

正文页 PPTX 默认用 `scripts/svg/render_svg_drawingml.py`。仅当 SVG→PPTX 不可用时才从 `scripts/native.cjs` 加载 `NativeDeck`。不要把案例 JSON 变成用户必填协议。Node 会从根目录加载锁定依赖，源码可以在任意任务目录。

根 Python 环境需要重建时，按宿主授权执行：

```bash
python3 -m venv "$PPT_WORKBENCH/.venv"
"$PPT_WORKBENCH/.venv/bin/python" -m pip install -r "$PPT_WORKBENCH/requirements.txt"
```

Node 依赖按根目录锁文件本地安装，不改全局 Node 包。安装可能联网，仅在安装或明确修复环境时执行，不在普通材料处理过程中隐式触发。

## 可选转换

LibreOffice 和 Poppler 不属于主线安装。宿主已有预览能力优先；`scripts/optional/` 下的转换脚本仅在本次明确选择该路线时调用。缺少预览不阻止 PPTX 交付，必须标注视觉未验证。

合并导出的可选 PDF 页数检查以 pypdf 6.11.0 验证；根环境主线保留素材读取所需依赖，导出支线需要时按 `requirements-export.txt` 准备。用户只要求 PPTX 时不做这一步。

## 维护者质量门

维护者质量门只用于维护或升级本技能，不是每次用户制稿都要运行的整套回归。模型制作单页时执行页面级门禁：运行 `inspect_pptx.py`，有预览就目检并修复，再检查；制作整册或合并批次后对最终文件重复一次。以下命令应在技能根目录执行；需要 Python 开发依赖时先运行 `python3 -m pip install -r requirements-dev.txt`。隔离回归脚本的文件入口是 `tests/test_generation_isolation.py`。

```bash
python3 "$PPT_WORKBENCH/tests/check_skill.py"
python3 -m unittest tests.test_extract_materials tests.test_inspection tests.test_skill -v
python3 -m pytest "$PPT_WORKBENCH/tests/test_merge_export.py" -q
node --test "$PPT_WORKBENCH/tests/native.test.cjs"
python3 "$PPT_WORKBENCH/tests/verify_examples.py"
PPT_FONT_PATH="$FONT_FILE" PPT_FONT_NAME="$FONT_NAME" \
  python3 -m unittest tests.test_generation_isolation -v
```

设置 `PPT_WORKBENCH_SOURCE_ROOT` 时，`check_skill.py` 会对照原始仓库副本做文件集合和 SHA-256 校验。需要图表、图标或 SVG 参考时读取 `references/generate/capability-map.md`，活动 SVG DrawingML 在 `scripts/svg/render_svg_drawingml.py`；布局决策校验脚本在 `scripts/layout/`，它依赖 Ubrio 应用导入，不是默认生成入口。
