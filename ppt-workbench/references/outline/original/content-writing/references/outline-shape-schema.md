<!--
id: skill-section/outline-shape
module_type: skill_section
category: content-structure
stage: outline
page_roles: cover,agenda,content,summary,closing
ppt_types: business_consulting
content_categories: outline_schema,content_structure
skill_types: content_writing,skill_section
summary_categories: skill_section_summary,outline_schema
triggers: 封面,目录,大纲结构,canonical outline,sections,slides,key_message
priority: P0
read_when: outline 阶段需要确认 canonical outline 的结构骨架和固定页边界时
max_use: 只用于大纲结构，不替代逐页内容生成
depends_on: slide-authoring:layout-fixed-cover-agenda
-->

# Outline Shape Schema

outline 阶段的模型草稿结构固定为：

`topic -> sections[].title -> sections[].pages[]`

其中：

- `cover` 和 `agenda` 必须作为独立页面显式出现，不能省略。
- `pages[]` 使用 `type / title / content`；正文页的观点、写作要求、证据、素材锚点和缺口统一写进 `content` 文本。
- `background_image / background_color / theme` 是可选的页级视觉意图。
- `page_role_id / business_pattern_candidates / data_shape_hint / visual_mode_hint` 是可选路由信号，只有判断明确时才填写，不能用来锁定具体 layout。
- page_id、页码、状态、版本、会话归属等系统字段由工具层补齐，不由模型手写。

固定页只保留固定内容，不给它们补素材证据或正文展开。封面、目录的真实落版边界以后续 `slide-authoring` 的固定页合同为准。

## 页级表达示例

叙事型 deck 仍必须有清晰论点。视觉意图写成浅层字段或 `content` 中的自然语言，不扩展内部对象：

```json
{
  "title": "人物如何被命运推着走",
  "type": "content",
  "content": "概要：人物并不是选择了命运，而是在每次关系中把命运生出来。\n写作要求：解释主题判断，并用文本细节支撑。\n图片用途：inline_picture。\n图片意图：书封、人物剪影或地点意象。",
  "page_role_id": "statement",
  "visual_mode_hint": "image_dominant",
  "theme": "纸张质感、克制叙事"
}
```

- 视觉意图要落到可理解的结构或画面语义，不要只写氛围形容词。
- 素材 ID、binding、来源和许可写入 support 材料或由工具结果维护，不把裸外链和内部绑定对象塞进草稿。

这些字段只表达内容和视觉意图，具体素材绑定、版式和渲染路线由后续阶段决定。
