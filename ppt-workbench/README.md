# PPT 工作台

给 Agent 使用的中文业务汇报技能。读取用户给出的材料，整理事实和大纲，生成可编辑的 PPTX，也可以合并、选页和导出。

默认是结论先行的经营、项目和方案汇报：一页一个主观点，用卡片、指标、图表、表格和来源承载证据。整页截图、低密度海报和“大标题加一句口号”不是正文页的交付标准。

Agent 从 [SKILL.md](SKILL.md) 进入。本文件只说明目录、依赖和检查方式，不重复制作流程。

## 目录

```text
ppt-workbench/
├── SKILL.md                 # 唯一入口
├── references/              # 素材、大纲、逐页方法、质量门和原始参考
├── scripts/                 # 提取、金标 SVG、DrawingML、图表、图标、校验、合并
├── assets/                  # 样例、蓝色高密度参考图、内置图片库、组件数据
├── tests/                   # 维护者质量门
├── requirements.txt         # 运行依赖
├── requirements-dev.txt     # 测试依赖
├── requirements-export.txt  # 可选导出依赖
└── package.json             # Node 依赖，需要 Node >= 20
```

路径都以本技能根目录为准。PPTX、SVG 和中间文件写入用户指定的任务目录，不写入技能目录。

## 依赖

```bash
python -m venv .venv
.venv/bin/pip install -r requirements.txt
npm install
```

维护者再安装 `requirements-dev.txt`。需要单独做 PDF 或文本导出时安装 `requirements-export.txt`。LibreOffice 只用于可选预览，不是安装前提。

正文页的默认路线是金标 SVG，再转成可编辑 DrawingML，并叠上原生图表、表格和图片。`scripts/native.cjs` 只在这条路线不可用时作为 fallback。

## 维护者检查

普通使用不需要跑测试。修改技能、脚本或示例后，在技能根目录执行：

```bash
python tests/check_skill.py
python -m unittest discover -s tests -p 'test_*.py' -v
python -m pytest tests/test_merge_export.py -q
node --test tests/native.test.cjs
```

检查项和隔离测试见 [tests/README.md](tests/README.md)。

## 来源与许可

本包是内部整理候选，`package.json` 标记为 `private`，没有在此授予开源许可。第三方模板、图标、图片和原始参考的许可边界见 [references/generate/provenance-and-license.md](references/generate/provenance-and-license.md) 与 [assets/images/README.md](assets/images/README.md)。未逐项核清的资产不能当作已经获准公开再分发。
