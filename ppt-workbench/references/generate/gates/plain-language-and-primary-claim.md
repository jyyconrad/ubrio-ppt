# Plain language and primary claim

人话的写法在 [大纲方法](../../outline/outline-method.md)。本文件只说明制页如何核对：从大纲抄字段，用 `check_outline(seed)` 在大纲阶段拦截，用 `check(spec)` 在 `quality_status=ready` 前再核一次。缺人话或仍是抽象名词堆，回大纲，不在 SVG 里重写。

Banned jargon lives in `BANNED_JARGON` in `scripts/svg/gates/plain_language.py`. Do not copy a second list here.

## REQUIRED fields

| Field | Who | What |
| --- | --- | --- |
| `primary_claim` | every page | One spoken sentence. Cover / section divider: title may stand in if it is already a judgment sentence. Closing: one takeaway claim (`primary_claim` or `audience_takeaway`). |
| `audience_takeaway` | content / summary / decision / evidence | One sentence answering 这页要听众记住什么. |
| `plain_language_who_scene_problem_action` | content pages | `{who, scene, problem, action}` — all four filled. |
| `groups[].role` | content pages | `support` \| `evidence` \| `limitation` \| `action` \| `context`. At most 3 `support`. |
| `groups[].weight` | optional | Default equal. Equal missing roles count as unscoped supports. |
| `number_role` | if the same number is in the title and every group | `evidence` \| `constraint` \| `decision`. Missing this is a warning, not a hard block. Cross-page repeats are out of scope. |

`GateResult.missing` blocks ready. Soft abstract-noun hits in card bodies, a single jargon token, and missing `number_role` are warnings.

## Recipe (fill in this order)

1. 在大纲写好 `primary_claim` 和人话四要素（见大纲方法）。制页抄过来，不要另写。
2. Rewrite `title` as that judgment (not a noun stack). `key_message` is the same judgment for the conclusion band. Title, main evidence, and conclusion band must share content words and form one reading path.
3. Keep at most 2–3 `support` cards. Demote everything else: `evidence`, `limitation`, `action`, or `context`. Do not dump KPI + evidence + mechanism + risk + principle + action as equal cards.
4. Each card is fact → impact → action. An `action` with no `evidence` / `fact` fails.
5. Use spoken Chinese. Do not stack three abstract nouns (机制/体系/路径/底座…) with no 的/了/是/要/把/被. Do not put two or more `BANNED_JARGON` terms in one sentence. `闭环` is allowed only as a named object, e.g. 缺陷闭环.
6. Write `audience_takeaway`: one sentence, 这页要听众记住什么. If a title number is repeated on every card, set `number_role`.
