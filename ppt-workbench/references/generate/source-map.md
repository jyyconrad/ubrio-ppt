# 原始来源映射与发布门

## 收录范围

| 源目录 | 包内目录 | 状态 |
| --- | --- | --- |
| `backend/resources/agent-content/skills/slide-generation-core/` | `original/slide-generation-core/` | 完整复制 |
| `backend/resources/agent-content/skills/slide-authoring/` | `original/slide-authoring/` | 完整复制 |
| `backend/resources/agent-content/skills/layout-intelligence/` | `original/layout-intelligence/` | 完整复制 |

逐文件路径和 SHA-256 见 [original-manifest.json](original-manifest.json)。目标共 2,096 个文件；源与目标已用 `diff -qr` 比对。

## 明确排除

- 7 个 `scripts/__pycache__/*.pyc`：解释器缓存，不是源码或运行资源。
- 2 个 `.DS_Store`：macOS 目录元数据。

排除不影响 Markdown、JSON、Python 源码、SVG、图片、PPTX、trace、索引或资源声明。

## 引用闭包

三份入口和能力树的页面制作方法均能在这三个目录中定位。未额外复制 `content-writing` 等运行时技能：它们在原 `SKILL.md` 中是 Ubrio 协作边界，不是独立生成技能阅读这些方法的文件依赖。跨技能引用已在 `methods/` 中解析到本包真实文件。

## 权利与隐私检查

- 三个源目录没有统一顶层 `LICENSE`、`NOTICE` 或逐文件授权清单。**在权利归属确认前，不得把“已复制”表述为“获准公开发布”。**
- `slide-authoring/assets/icons/lucide/` 含第三方图标资源，但复制目录内未发现随附许可证；发布前需补齐对应版本和许可证文本。
- 示例图片、PPTX、SVG 和模板系列没有完整逐项来源/许可台账；发布前必须审计或替换。
- `slide-authoring` 的 7 个 benchmark `*.trace.json` 含维护者绝对路径 `/Users/jiangyayun/...`。为满足字节级原件保留未修改；公开包发布前应由发布负责人决定排除这些 trace，并重新生成 manifest，不能静默发布私人路径。
- 未在文本候选中发现 API key、密码或 token 值；这不是对二进制文件内容和版权的充分审计。

## 历史运行时边界

原文包含 `route_skill_references`、workspace manifest、阶段工具和 Ubrio resource ID 等描述。它们作为来源证据保留，不是独立技能的活动依赖；默认导航只要求本地文件读取。
