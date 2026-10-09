"""Spoken Chinese + one primary claim (session-884 U-01/U-02).

Write 人话 at outline time (`check_outline`). Page authoring copies those fields
and `check()` also verifies group roles. Banned jargon lives in `BANNED_JARGON`.
Do not import `build_gold_svg_page`.
"""

from __future__ import annotations

import re
from typing import Any

try:
    from . import CONTENT_ROLES, COVER_ROLES, GateResult
except ImportError:  # pragma: no cover - loose-file load
    import importlib.util
    from pathlib import Path

    _spec = importlib.util.spec_from_file_location(
        "_ppt_workbench_svg_gates",
        Path(__file__).with_name("__init__.py"),
    )
    _gates = importlib.util.module_from_spec(_spec)
    assert _spec.loader is not None
    _spec.loader.exec_module(_gates)
    CONTENT_ROLES = _gates.CONTENT_ROLES
    COVER_ROLES = _gates.COVER_ROLES
    GateResult = _gates.GateResult


BANNED_JARGON: frozenset[str] = frozenset(
    {
        "收编",
        "免疫机制",
        "吞吐线",
        "责任回流",
        "作业系统",
        "端到端收益",
        "抓手",
        "飞轮",
        "底座",
        "赋能",
        "闭环",
        "护城河",
    }
)

GROUP_ROLES: frozenset[str] = frozenset(
    {"support", "evidence", "limitation", "action", "context"}
)
NUMBER_ROLES: frozenset[str] = frozenset({"evidence", "constraint", "decision"})
WHO_SCENE_KEYS: tuple[str, ...] = ("who", "scene", "problem", "action")
FACT_KEYS: tuple[str, ...] = ("evidence", "fact", "facts", "proof", "data")
ACTION_KEYS: tuple[str, ...] = ("action", "action_or_risk", "next_action")

# Abstract-noun lexicon for the 3+ consecutive-noun heuristic. Precision over recall:
# only strategy/mechanism nouns, not ordinary objects like 验收/缺陷/清单.
ABSTRACT_NOUNS: frozenset[str] = frozenset(
    {
        "收编",
        "免疫",
        "机制",
        "吞吐",
        "吞吐线",
        "责任",
        "回流",
        "作业",
        "系统",
        "收益",
        "抓手",
        "飞轮",
        "底座",
        "赋能",
        "闭环",
        "协同",
        "能力",
        "路径",
        "体系",
        "模式",
        "中台",
        "杠杆",
        "韧性",
        "链路",
        "颗粒",
        "沉淀",
        "打法",
        "对齐",
        "矩阵",
        "升级",
        "组织",
        "价值",
        "效能",
        "生态",
        "引擎",
        "护城河",
        "盘点",
        "框架",
        "策略",
        "口径",
        "门禁",
        "规范",
        "免疫机制",
        "责任回流",
        "作业系统",
        "端到端收益",
        "能力层",
        "标准层",
        "组织力",
        "作业面",
        "方法论",
        "操作系统",
    }
)

_PARTICLES = frozenset("的了是要把被")
_PLACEHOLDER_MARKERS = ("待补", "tbd", "todo", "placeholder", "待定", "xxx")
_JUDGMENT_MARKERS = (
    "是",
    "要",
    "应",
    "会",
    "将",
    "不",
    "没",
    "先",
    "再",
    "必须",
    "不能",
    "已",
    "让",
    "把",
    "被",
    "到",
    "没有",
    "不是",
    "需要",
    "才能",
    "立",
    "扩大",
    "缺少",
    "不能当",
)
_WEAK_TITLES = frozenset({"谢谢", "谢谢观看", "结束", "再见", "q&a", "qa", "thank you"})
_NUMBER_RE = re.compile(r"\d+(?:\.\d+)?%?")
_LATIN_RE = re.compile(r"[A-Za-z]{2,}")
_SENTENCE_RE = re.compile(r"[。！？!?；;\n]+")
_WEIGHT_NAMES = {
    "high": 3.0,
    "primary": 3.0,
    "medium": 2.0,
    "low": 1.0,
    "secondary": 1.0,
}
_NOUN_LEXICON = tuple(
    sorted(ABSTRACT_NOUNS | BANNED_JARGON, key=len, reverse=True)
)
_JARGON_LEXICON = tuple(sorted(BANNED_JARGON, key=len, reverse=True))


def check_outline(seed: dict) -> GateResult:
    """Headline 人话 for outline page seeds. Group-role checks are skipped."""
    if not isinstance(seed, dict):
        return GateResult(missing=["primary_claim"], details={"error": "seed must be a dict", "stage": "outline"})
    spec = {
        key: value
        for key, value in seed.items()
        if key not in {"groups", "cards", "steps", "pyramid_layers"}
    }
    result = check(spec)
    result.details["stage"] = "outline"
    return result


def check(spec: dict) -> GateResult:
    if not isinstance(spec, dict):
        return GateResult(missing=["primary_claim"], details={"error": "spec must be a dict"})

    missing: list[str] = []
    warnings: list[str] = []
    details: dict[str, Any] = {}
    role = _page_role(spec)
    content = _is_content(role)
    closing = role in {"closing", "end"}
    frame = role in {"cover", "section_divider"}

    claim = _text(spec.get("primary_claim"))
    title = _text(spec.get("title"))
    key_message = _text(spec.get("key_message"))
    takeaway = _text(spec.get("audience_takeaway"))
    groups = _groups(spec)

    if content:
        if not _filled(claim):
            missing.append("primary_claim")
        if not _filled(takeaway):
            missing.append("audience_takeaway")
        if not _who_scene_complete(spec):
            missing.append("plain_language_who_scene_problem_action")
    elif closing:
        if not _has_takeaway_claim(claim, takeaway, title):
            missing.append("primary_claim")
    elif frame:
        if not _filled(claim) and not _is_judgment_sentence(title):
            missing.append("primary_claim")
    else:
        if not _filled(claim) and not _is_judgment_sentence(title):
            missing.append("primary_claim")

    if content and _filled(claim):
        displayed = " ".join(part for part in (title, key_message) if part)
        if displayed and not _claims_aligned(claim, displayed):
            missing.append("claim_alignment")

    if content:
        support_code = _support_limit_code(groups)
        if support_code:
            missing.append(support_code)
            details["support_count"] = _support_count(groups)

    if content:
        if _action_without_fact(groups):
            missing.append("fact_then_impact_then_action")

    headline_map = {
        "title": title,
        "key_message": key_message,
        "primary_claim": claim,
        "audience_takeaway": takeaway,
    }
    jargon_hits = _headline_jargon_hits(headline_map)
    details["jargon_hits"] = jargon_hits
    if any(len(hits) >= 2 for hits in jargon_hits.values()):
        missing.append("plain_language")
    else:
        body_hits = _body_jargon_hits(groups)
        if any(len(hits) >= 2 for hits in body_hits.values()):
            warnings.append("plain_language")
        elif any(hits for hits in jargon_hits.values()):
            warnings.append("plain_language")

    headline_stacks = {
        key: _abstract_noun_runs(text) for key, text in headline_map.items() if text
    }
    details["abstract_noun_runs"] = {
        key: runs for key, runs in headline_stacks.items() if runs
    }
    if any(headline_stacks.values()):
        missing.append("abstract_noun_stack")
    else:
        body_stacks = [
            run for group in groups for run in _abstract_noun_runs(_group_text(group))
        ]
        if body_stacks:
            warnings.append("abstract_noun_stack")
            details.setdefault("abstract_noun_runs", {})["groups"] = body_stacks

    number_warning = _repeated_number_without_role(title, groups, spec)
    if number_warning:
        warnings.append(number_warning)

    if _filled(takeaway) and not _is_one_sentence(takeaway):
        warnings.append("audience_takeaway")

    return GateResult(
        missing=_unique(missing),
        warnings=_unique(warnings),
        details=details,
    )


def _page_role(spec: dict) -> str:
    return _text(spec.get("page_role") or spec.get("role") or "content").lower()


def _is_content(role: str) -> bool:
    if role in CONTENT_ROLES:
        return True
    if role in COVER_ROLES:
        return False
    return True


def _has_takeaway_claim(claim: str, takeaway: str, title: str) -> bool:
    if _filled(claim) or _filled(takeaway):
        return True
    return _is_judgment_sentence(title) and not _is_weak_title(title)


def _is_weak_title(title: str) -> bool:
    stripped = title.strip().rstrip("。.!！").lower()
    return (not stripped) or stripped in _WEAK_TITLES or len(stripped) <= 2


def _is_judgment_sentence(text: str) -> bool:
    text = _text(text)
    if not text or _is_weak_title(text):
        return False
    if any(marker in text for marker in _JUDGMENT_MARKERS):
        return True
    return ("，" in text) or ("," in text)


def _who_scene_complete(spec: dict) -> bool:
    value = spec.get("plain_language_who_scene_problem_action")
    if not isinstance(value, dict):
        return False
    return all(_filled(value.get(key)) for key in WHO_SCENE_KEYS)


def _groups(spec: dict) -> list[dict]:
    raw = spec.get("groups")
    if not raw:
        raw = spec.get("cards") or spec.get("steps") or spec.get("pyramid_layers") or []
    if isinstance(raw, dict):
        items = list(raw.values())
    elif isinstance(raw, list):
        items = raw
    else:
        items = []
    return [item for item in items if isinstance(item, dict)]


def _group_role(group: dict) -> str:
    role = _text(group.get("role")).lower()
    return role if role in GROUP_ROLES else ""


def _weight(group: dict) -> float:
    value = group.get("weight")
    if value is None or value == "":
        return 1.0
    if isinstance(value, (int, float)):
        return float(value)
    return _WEIGHT_NAMES.get(str(value).strip().lower(), 1.0)


def _support_count(groups: list[dict]) -> int:
    return sum(1 for group in groups if _group_role(group) in {"support", ""})


def _support_limit_code(groups: list[dict]) -> str:
    if _support_count(groups) > 3:
        return "support_limit"
    if len(groups) > 3:
        roles = [_group_role(group) or "support" for group in groups]
        weights = [_weight(group) for group in groups]
        if len(set(roles)) == 1 and len(set(weights)) == 1:
            return "support_limit"
    return ""


def _has_fact(group: dict) -> bool:
    return any(_filled(group.get(key)) for key in FACT_KEYS)


def _has_action(group: dict) -> bool:
    return any(_filled(group.get(key)) for key in ACTION_KEYS)


def _action_without_fact(groups: list[dict]) -> bool:
    return any(_has_action(group) and not _has_fact(group) for group in groups)


def _claims_aligned(claim: str, displayed: str) -> bool:
    left = _content_tokens(claim)
    right = _content_tokens(displayed)
    if not left or not right:
        return False
    shared = left & right
    if len(shared) >= 2:
        return True
    if len(shared) == 1:
        token = next(iter(shared))
        return token.isdigit() or "%" in token or len(token) >= 3
    return False


def _content_tokens(text: str) -> set[str]:
    tokens: set[str] = set()
    for match in _NUMBER_RE.finditer(text):
        tokens.add(match.group())
    for match in _LATIN_RE.finditer(text):
        tokens.add(match.group().lower())
    run: list[str] = []

    def flush() -> None:
        chunk = "".join(run)
        run.clear()
        if len(chunk) < 2:
            return
        tokens.add(chunk)
        for index in range(len(chunk) - 1):
            gram = chunk[index : index + 2]
            if gram[0] in _PARTICLES or gram[1] in _PARTICLES:
                continue
            tokens.add(gram)

    for char in text:
        if _is_cjk(char) and char not in _PARTICLES:
            run.append(char)
        else:
            flush()
    flush()
    return tokens


def _headline_jargon_hits(fields: dict[str, str]) -> dict[str, list[str]]:
    hits: dict[str, list[str]] = {}
    for key, text in fields.items():
        if not text:
            continue
        sentence_hits = [
            found for sentence in _sentences(text) if (found := _jargon_in_sentence(sentence))
        ]
        flat: list[str] = []
        for found in sentence_hits:
            flat.extend(found)
        if flat:
            hits[key] = flat
    return hits


def _body_jargon_hits(groups: list[dict]) -> dict[str, list[str]]:
    hits: dict[str, list[str]] = {}
    for index, group in enumerate(groups):
        found = _jargon_in_sentence(_group_text(group))
        if found:
            hits[f"group_{index}"] = found
    return hits


def _sentences(text: str) -> list[str]:
    parts = [part.strip() for part in _SENTENCE_RE.split(text) if part.strip()]
    return parts or ([text.strip()] if text.strip() else [])


def _jargon_in_sentence(sentence: str) -> list[str]:
    hits: list[str] = []
    index = 0
    length = len(sentence)
    while index < length:
        matched = None
        for term in _JARGON_LEXICON:
            if sentence.startswith(term, index):
                matched = term
                break
        if matched is None:
            index += 1
            continue
        if matched == "闭环" and _closed_loop_allowed(sentence, index):
            index += len(matched)
            continue
        hits.append(matched)
        index += len(matched)
    return hits


def _closed_loop_allowed(text: str, index: int) -> bool:
    """Allow 闭环 only when attached to a concrete object (e.g. 缺陷闭环)."""
    prefix: list[str] = []
    for char in reversed(text[:index]):
        if _is_cjk(char) and char not in _PARTICLES:
            prefix.append(char)
        else:
            break
    prefix_text = "".join(reversed(prefix))
    if len(prefix_text) >= 2 and prefix_text not in BANNED_JARGON:
        return True
    suffix: list[str] = []
    for char in text[index + 2 :]:
        if _is_cjk(char) and char not in _PARTICLES:
            suffix.append(char)
        else:
            break
    return len(suffix) >= 2


def _abstract_noun_runs(text: str) -> list[list[str]]:
    runs: list[list[str]] = []
    current: list[str] = []
    index = 0
    length = len(text)
    while index < length:
        char = text[index]
        if char in _PARTICLES or not _is_cjk(char):
            if len(current) >= 3:
                runs.append(current)
            current = []
            index += 1
            continue
        matched = None
        for noun in _NOUN_LEXICON:
            if text.startswith(noun, index):
                matched = noun
                break
        if matched is None:
            if len(current) >= 3:
                runs.append(current)
            current = []
            index += 1
            continue
        current.append(matched)
        index += len(matched)
    if len(current) >= 3:
        runs.append(current)
    return runs


def _repeated_number_without_role(
    title: str, groups: list[dict], spec: dict
) -> str:
    if not groups:
        return ""
    title_numbers = set(_NUMBER_RE.findall(title))
    if not title_numbers:
        return ""
    repeated = [
        number
        for number in title_numbers
        if all(number in _NUMBER_RE.findall(_group_text(group)) for group in groups)
    ]
    if not repeated:
        return ""
    if _has_number_role(spec, groups):
        return ""
    return "number_role"


def _has_number_role(spec: dict, groups: list[dict]) -> bool:
    if _text(spec.get("number_role")).lower() in NUMBER_ROLES:
        return True
    return any(_text(group.get("number_role")).lower() in NUMBER_ROLES for group in groups)


def _group_text(group: dict) -> str:
    parts: list[str] = []
    for value in group.values():
        if isinstance(value, dict):
            parts.append(_text(value))
        elif isinstance(value, list):
            parts.extend(_text(item) for item in value)
        else:
            parts.append(_text(value))
    return " ".join(part for part in parts if part)


def _is_one_sentence(text: str) -> bool:
    parts = [part for part in _SENTENCE_RE.split(text.strip()) if part.strip()]
    return len(parts) <= 1


def _text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return str(value)
    if isinstance(value, (list, tuple)):
        return " ".join(part for part in (_text(item) for item in value) if part)
    if isinstance(value, dict):
        return " ".join(part for part in (_text(item) for item in value.values()) if part)
    return str(value).strip()


def _filled(value: Any) -> bool:
    text = _text(value)
    if not text:
        return False
    lowered = text.lower()
    return not any(marker in lowered for marker in _PLACEHOLDER_MARKERS)


def _is_cjk(char: str) -> bool:
    return "\u4e00" <= char <= "\u9fff"


def _unique(items: list[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            ordered.append(item)
    return ordered
