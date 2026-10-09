# PPT 工作台

给 Agent 使用的中文业务汇报技能。读取用户给出的材料，整理事实和大纲，生成可编辑的 PPTX，也可以合并、选页和导出。

默认是结论先行的经营、项目和方案汇报：一页一个主观点，用卡片、指标、图表、表格和来源承载证据。整页截图、低密度海报和“大标题加一句口号”不是正文页的交付标准。

给人看的安装和开口方式在 [快速使用手册](docs/quickstart.md)。效果图在 [docs/screenshots](docs/screenshots/captions.md)：分类按技能图场景节点，每一张是一份 6 页合成演示的整册概览。版式参考仍在 `assets/visual-references`。Agent 从 [SKILL.md](SKILL.md) 进入。

## 目录

```text
ppt-workbench/
├── SKILL.md                 # 唯一入口
├── docs/quickstart.md       # 给人看的快速使用手册
├── docs/screenshots/        # 高密度效果图
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
npm ci --ignore-scripts --no-audit --no-fund
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

本包随 <https://github.com/jyyconrad/ubrio-ppt> 发布。仓库根目录 `LICENSE` 的 MIT 适用于本技能自行编写的说明、脚本和合成样例。第三方图标、图片、npm 依赖、vendor 代码和带水印的版式参考仍按各自许可使用，见仓库 `THIRD_PARTY_NOTICES.md` 与 [来源说明](references/generate/provenance-and-license.md)。
