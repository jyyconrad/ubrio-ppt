# RED application: SKILL.md live path (current skill, before description rewrite)

IMPORTANT: This is a real authoring task. Do not edit any files. Do not read `tests/`.

Skill root: the ppt-workbench skill directory (cwd).

User wants ONE Chinese business 经营复盘 body page as editable PPTX in minutes. Facts are already verified.

## What RED is measuring

1. YAML `description` starts with `Use when` and does **not** summarize the 素材→大纲→逐页→合并 workflow.
2. `references/page-generation.md` and `references/generate/capability-map.md` treat gold SVG + native slots as the default executable path, not historical.
3. `scripts/native.cjs` is fallback only.

## Observed RED (verbatim)

Unit tests against the pre-edit skill:

```
FAIL test_skill_description_is_use_when_triggers_not_workflow
AssertionError: 4 not less than or equal to 1 : description summarizes the four-stage workflow: ['整理 PPT 素材', '编排汇报大纲', '逐页制作', '合并导出']

FAIL test_live_docs_default_gold_svg_slots_native_cjs_fallback
AssertionError: '原生 PPTX 路线' unexpectedly found in tests/README.md
```

Catalog description used in RED (verbatim):

```
Use when 用户要求整理 PPT 素材、编排汇报大纲、逐页制作或修改中文业务汇报，或合并导出可编辑 PPTX；也用于客户介绍、经营复盘、项目汇报、方案汇报和年度总结。不用于普通代码开发。
```

Description-only subagent (`working_dir=/tmp`, no skill files):

```
1. FIRST_STEPS: skip material collection, skip outline, do not write files, do not call an assumed pptx script
2. PPTX_MAKER: none
3. PHRASES: none
4. SKIP_SKILL_BODY: no
```

The injected description listed the four-stage pipeline and never named gold SVG, so a catalog-only agent would not ship `source.svg` → DrawingML. Body docs already default Chinese business pages to gold when opened; `tests/README.md` still led with `原生 PPTX 路线：scripts/native.cjs`.
