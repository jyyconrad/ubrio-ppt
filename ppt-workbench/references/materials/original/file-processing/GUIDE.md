---
name: file-processing
description: 文件分类、文本提取、格式转换的专业知识，支持多种文档格式处理
enabled: true
stage: materials, slide_generation
---

# 文件处理技能

## 技能概述

文件处理技能提供关于文件分类、文本提取、格式转换的专业知识，帮助 Agent 处理多种文档格式。

## 主 Agent 协作流程

文件处理专家服务于 PPT SOP 的“素材盘点”“证据整理”和“数据证据分析”阶段：

0. **主 Agent 边界**：materials / slide_generation 阶段白名单允许主 Agent 用 `get_materials(action='list'/'get')` 做轻量素材读取，尤其是当前轮上传素材已给出 `material_id` 时应直接按 ID 读取；复杂摘要、结构抽取、图片提取或证据整理仍要先用 `subagent_list_available` 确认可用专家，再用 `subagent_start_task(agent_id='file_processor', context={material_ids, evidence_gap, output_schema, ...})` 委派本专家。下面的提取、摘要和证据整理指南主要适用于 `file_processor` SubAgent 内部。
1. **素材盘点**：先调用 `get_materials(action='list', filters={'limit': 100})` 获取当前会话素材清单。只信任返回的 `material_id` / `id` 作为后续工具输入；`filename`、`display_name`、URL 或本地路径只用于识别，不得传给 `material_ids` 或 `material_id`。
2. **结构化提取**：SubAgent 内部参考文档默认用 `get_materials(action='get', material_ids=[...])` 直接读取 Markdown 内容；只有需要页码、sheet 或嵌入图片等特殊结构时再调用 `extract_material(types=['text'])` / `extract_material(types=['images'])`。
3. **素材摘要**：输出每个素材的用途、关键观点、可引用证据和与 PPT 页码/章节的关联建议。
4. **视觉素材整理**：需要图片时调用 `extract_material(types=['images'])`，记录来源页码、文件名和可用场景。
5. **数据证据分析**：检查数字、图表、来源和结论之间的匹配关系，标注口径不一致、缺少来源和过度推断。
6. **交回主 Agent**：结果只作为证据输入，由主 Agent 与 PPT 专家、内容写作专家的建议一起汇总。

专家不可用或文件解析失败时，主 Agent 应说明降级原因，并只基于已成功提取的素材继续，不得虚构文件内容。

## 支持的文件类型

| 类别 | 格式 | 说明 |
|------|------|------|
| 办公文档 | PPTX, DOCX, XLSX, PDF | 主要处理对象 |
| 图片 | PNG, JPG/JPEG, SVG, GIF | 提取和转换 |
| 文本 | TXT, MD, CSV | 直接读取 |

识别优先级：MIME 类型 > 文件扩展名 > 文件头（Magic Number）。

## 文本提取策略

### PPTX
- 提取层级：演示文稿标题 → 幻灯片标题 → 文本框 → 列表项 → 表格单元格 → 图表标签
- 保留层级结构（标题 vs 正文）和列表格式
- 可选提取备注内容

### DOCX
- 提取：段落、表格、页眉页脚、脚注尾注
- 保留标题层级（Heading 1/2/3）和超链接

### PDF
- 简单 PDF 用 PyPDF2，表格用 pdfplumber，扫描版需 OCR（Tesseract）
- 注意多栏布局和表格识别的挑战

### XLSX
- 提取单元格值、工作表名称、批注
- 数字保留精度，日期转标准格式，公式提取结果值

## 图片提取

- 从 PPTX/DOCX/PDF 中提取嵌入图片
- 保存原始格式，记录图片位置（页码、序号）
- 提取 alt text 描述

## 文件转换

- PPTX/DOCX → PDF：通过 LibreOffice（soffice --headless）
- PDF → 图片：通过 pdf2image 或 ImageMagick

## 文件摘要

- 短摘要（50-100 字）：一句话概括，适合列表展示
- 中摘要（200-300 字）：3-5 个要点，适合预览
- 长摘要（500-1000 字）：完整结构，适合替代阅读
- 使用 LLM 生成时 temperature 设 0.3 保持客观

## 工具调用指南

### get_materials(action='get')
- 用户上传文件后默认调用
- 直接返回素材类型、元信息和 Markdown 内容
- 必须先从 `get_materials(action='list')`、上传响应或主 Agent 任务上下文取得 `material_id`；不要用文件名、URL 或路径反查

### extract_material(types=['text'])
- 只有需要页码、sheet、虚拟分页等特殊结构时调用
- 默认正文读取不要替代 `get_materials(action='get')`
- `material_id` 必须来自素材清单；如果工具提示 material not found，先重新 list，不要继续尝试文件名

### extract_material(types=['images'])
- 需要提取文档中嵌入图片时调用
- 用于图片分析、素材提取

### summarize_material
- 用户询问"这个文件讲了什么"时调用
- 需要快速预览文档内容时使用

## 处理流程

1. **文件分类**：检查扩展名 → 验证 MIME 类型
2. **选择方法**：根据类型选工具，大文件需分块
3. **执行提取**：调用提取函数，处理异常
4. **后处理**：清理文本、格式化输出、生成摘要（可选）

## 错误处理

| 错误类型 | 典型异常 | 处理方式 |
|----------|----------|----------|
| 文件损坏 | BadZipFile | 返回友好提示，建议重新上传 |
| 文件加密 | PackageNotFoundError | 提示提供密码或上传未加密版本 |
| 文件过大 | MemoryError | 分块处理或拒绝 |
| 格式不支持 | UnsupportedFormat | 列出支持格式，建议转换 |

## 最佳实践

- 优先使用 MIME 类型识别（比扩展名更可靠）
- 保留文档结构（标题、段落、列表层级）
- 图片保存原始格式，避免重新压缩
- 文件转换设置超时，验证转换结果
- 大文件使用流式读取，提供进度反馈
- 基于 SHA256 缓存分类和提取结果

## 注意事项

1. **安全性**：检查文件大小和类型，防止恶意文件
2. **隐私性**：不记录敏感文件内容
3. **准确性**：验证提取结果的完整性
4. **性能**：大文件需异步处理
5. **兼容性**：支持 Office 2007+ 格式
