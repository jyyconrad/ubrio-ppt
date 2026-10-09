---
name: ppt-merge-export
description: 当用户需要检查普通 PPTX，跨文件选页、重排、重复和合并已验证的静态页面，或转换为 PDF/逐页 PNG 时使用。纯 PPTX 路径使用固定版本 pptx-automizer，不依赖 LibreOffice；转换优先宿主已有能力，LibreOffice 仅是显式可选支线。
---

# PPT 合并与导出

## 任务边界

预检、合并和导出是独立动作。用户只要求转换时，不附加合并、改稿或重排；用户只要求合并时，不附加 PDF/PNG。纯 PPTX 预检与合并不依赖 Office 或 LibreOffice。

先按需读取 [支持矩阵](support-matrix.md) 与 [依赖和来源](dependencies-and-sources.md)。只对已验证静态子集执行合并；动画、音视频、OLE、宏、加密文件、复杂 layout 内容和外部关系不在承诺范围。

在任意工作目录运行时，先设置技能目录：

```bash
SKILL="/absolute/path/to/ppt-merge-export"
```

## 预检

使用 `preflight` 检查输入、页码、尺寸、安全边界并形成只读选择计划。页码从 1 开始，默认 `all`，显式重复页会保留。不同尺寸直接拒绝，不缩放或裁切。

```bash
python "$SKILL/scripts/merge_export.py" preflight \
  --input "/path/A.pptx:3,1" \
  --input "/path/B.pptx:all"
```

## 合并

1. 先运行 `preflight`，确认选择顺序和统一尺寸。
2. 使用同样顺序调用 `merge`。输出必须是新 `.pptx`；禁止输出与任一输入同路径。
3. 工具使用包内固定的 `pptx-automizer@0.9.3`，先写隔离临时文件；成组清理库遗留的不可达 root slide/notes 后，校验包内全部关系 target。
4. 页数、尺寸与关系均通过后独占发布；非覆盖模式下若目标在运行期间出现则拒绝。
5. 检查返回页数和实际 PPTX。涉及未声明对象时拒绝，不能静默栅格化。

```bash
python "$SKILL/scripts/merge_export.py" merge \
  --input "/path/A.pptx:3,1" \
  --input "/path/B.pptx:all" \
  --output "/path/合并结果.pptx"
```

已验证子集包含文字、常规形状、原生表格、图片、常规原生图表及其嵌入 workbook、备注，以及普通 master/theme 关系。验证仅覆盖合成静态样例，不等于所有第三方 PPTX 或 PowerPoint 编辑往返均已通过。

## 导出

优先使用宿主或用户已有的 Office/PPTX 转换能力。只有环境明确选择 LibreOffice 时才调用可选支线；不传 `--backend` 时 CLI 不探测 LibreOffice。

```bash
python "$SKILL/scripts/merge_export.py" export \
  --input "/path/输入.pptx" \
  --format pdf \
  --backend libreoffice \
  --output "/path/输出.pdf"

python "$SKILL/scripts/merge_export.py" export \
  --input "/path/输入.pptx" \
  --format png \
  --backend libreoffice \
  --output "/path/逐页图片"
```

PDF/PNG 是固定版面输出，不继承 PPTX 可编辑性。缺少实际请求的转换后端时如实失败，不临时安装依赖。

## 禁止替代

- 不用 `python-pptx` XML/shape 深拷贝充当通用合并器。
- 不逐 shape 搬运 LibreOffice UNO 对象。
- 不只取每个文件第一页，不丢弃重复页。
- 不把整页渲染为图片再塞回 PPTX。
- 不执行输入宏，不更新外链，不联网。

## 交付

报告输入和输出页数、实际路径、引擎、支持子集与未验证对象。当前没有 PowerPoint 实测，不能声称完全兼容或完成真实 PowerPoint 编辑往返。
