"""单页 SVG 色系一致性确定性自检（warning 级，不阻断渲染）。

背景：生成 deck 出现"并列卡片逐卡换色相、页与页主色漂移"（同页 4-5 个色相）。
这里在 SVG 渲染门禁处用确定性代码提取当前页 fill/stroke/stop-color 的非中性
主色相（HSL 饱和度过滤 + 30° 色相桶聚类、按出现次数加权），与 deck 级
style_manifest.palette 推导的期望色系对比，偏离时产出结构化 warning：

- ``SLIDE_COLOR_SCHEME_DRIFT``：页面最主要色相与 deck 全部允许色相的最小
  环形偏差 > 30°；
- ``SLIDE_COLOR_PALETTE_OVERFLOW``：非中性色相桶数 > 3。

两类都带可机械执行的 ``repair_suggestion.recolor_map``（偏离色 → deck 主色
hex）。deck palette 缺失或全中性时整个检查静默跳过（``checked=False``）。

取舍说明：不复用 theme_polarity_contract 的 "prepare_slide_context 写入 →
renderer 消费" 契约通道 —— 极性合同承载的是多信号**推断结果**，需要固化；
而色系期望是 palette 的纯派生（renderer 经 ``_read_style_manifest_snapshot``
已直达 palette 真源），现算即可，新增契约通道只会多一份需同步的拷贝。
"""
from __future__ import annotations

import re
from collections import Counter
from typing import Any

# ==== 判定阈值（确定性规则，调整时同步更新模块 docstring 与测试） ====
# 中性色判定：低饱和灰阶，或近白 / 近黑（含深色主题的深蓝黑背景基色）。
NEUTRAL_SATURATION_MAX = 0.15
NEUTRAL_LIGHTNESS_MAX = 0.92
NEUTRAL_LIGHTNESS_MIN = 0.12
# 色相聚类桶宽与主色相偏差容忍（需求口径：>30° 判漂移）。
HUE_BUCKET_DEGREES = 30
HUE_DRIFT_TOLERANCE_DEGREES = 30.0
# 单页非中性色相桶数上限（需求口径：>3 判配色过散）。
CHROMATIC_HUE_BUCKET_MAX = 3
# recolor_map 中每桶最多列出的样本色，避免膨胀模型上下文。
_RECOLOR_SAMPLE_LIMIT = 6

# fill= / stroke= / stop-color= 属性形式；\b 保证不误吞 fill-opacity 等。
_COLOR_ATTR_RE = re.compile(r"""\b(?:fill|stroke|stop-color)\s*=\s*["']([^"']+)["']""", re.IGNORECASE)
# CSS 声明形式（style="fill:..." 内联与 <style> 块共用）；fill 后必须紧跟
# 冒号，fill-opacity / stroke-width 等派生属性天然不命中。
_COLOR_DECL_RE = re.compile(r"""(?:fill|stroke|stop-color)\s*:\s*([^;"'}]+)""", re.IGNORECASE)
_HEX_RE = re.compile(r"#(?:[0-9a-fA-F]{6}|[0-9a-fA-F]{3})\b")
_RGB_FUNC_RE = re.compile(r"rgba?\(\s*(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*(\d{1,3})\s*(?:,[^)]*)?\)", re.IGNORECASE)
_SKIP_TOKENS = {"none", "transparent", "currentcolor", "inherit"}


def build_color_scheme_report(
    svg_text: str,
    *,
    style_manifest_snapshot: dict[str, Any] | None,
) -> dict[str, Any]:
    """构建当前页色系一致性报告（纯函数，永不抛出业务异常）。

    返回 ``checked=False`` 表示 deck 期望色系不可用，调用方应静默跳过；
    ``checked=True`` 时 ``warnings`` 为空即通过。
    """
    expected = _expected_scheme_from_palette(style_manifest_snapshot)
    if expected is None:
        return {"checked": False, "skip_reason": "deck_palette_unavailable", "warnings": []}

    observed = _observe_svg_colors(svg_text)
    warnings = [*_drift_warnings(observed, expected), *_overflow_warnings(observed, expected)]
    return {
        "checked": True,
        "expected": {
            "source": "style_manifest.palette",
            "primary_hex": expected["primary_hex"],
            "allowed_hex": [hex_value for hex_value, _hue in expected["allowed"]],
            "allowed_hues": [round(hue) for _hex, hue in expected["allowed"]],
        },
        "observed": observed,
        "warnings": warnings,
    }


# ==== deck 期望色系：palette 全部非中性槽位色相 + 收敛目标主色 ====

def _expected_scheme_from_palette(
    style_manifest_snapshot: dict[str, Any] | None,
) -> dict[str, Any] | None:
    if not isinstance(style_manifest_snapshot, dict):
        return None
    palette = style_manifest_snapshot.get("palette")
    if not isinstance(palette, dict) or not palette:
        return None

    allowed: list[tuple[str, float]] = []
    seen: set[str] = set()
    hex_by_slot: dict[str, str] = {}
    for slot, raw_value in palette.items():
        hex_value = _palette_hex_value(raw_value)
        if hex_value is None:
            continue
        hex_by_slot[str(slot)] = hex_value
        hue, saturation, lightness = _hex_to_hsl(hex_value)
        if _is_neutral(saturation, lightness) or hex_value in seen:
            continue
        seen.add(hex_value)
        allowed.append((hex_value, hue))
    if not allowed:
        return None

    # 收敛目标：primary 槽位优先，其次 accent；两者缺失或为中性时退回
    # 第一个非中性 palette 色。与需求口径"哪些色收敛到哪个主色 hex"对齐。
    primary_hex = None
    for slot in ("primary", "accent"):
        candidate = hex_by_slot.get(slot)
        if candidate is not None and candidate in seen:
            primary_hex = candidate
            break
    if primary_hex is None:
        primary_hex = allowed[0][0]
    return {"allowed": allowed, "primary_hex": primary_hex}


def _palette_hex_value(value: Any) -> str | None:
    """palette 槽位取色：字符串直接解析；渐变 dict 取首个可解析颜色。"""
    if isinstance(value, str):
        return _parse_color_token(value)
    if isinstance(value, dict):
        colors = value.get("colors")
        if isinstance(colors, list):
            for item in colors:
                parsed = _palette_hex_value(item)
                if parsed is not None:
                    return parsed
        for key in ("from", "start", "to", "end", "color"):
            parsed = _palette_hex_value(value.get(key))
            if parsed is not None:
                return parsed
    return None


# ==== SVG 侧观测：颜色出现次数 → 非中性色相桶 ====

def _observe_svg_colors(svg_text: str) -> dict[str, Any]:
    weight_by_hex: Counter[str] = Counter()
    for match in _COLOR_ATTR_RE.finditer(svg_text or ""):
        parsed = _parse_color_token(match.group(1))
        if parsed is not None:
            weight_by_hex[parsed] += 1
    for match in _COLOR_DECL_RE.finditer(svg_text or ""):
        parsed = _parse_color_token(match.group(1))
        if parsed is not None:
            weight_by_hex[parsed] += 1

    bucket_weights: Counter[int] = Counter()
    bucket_colors: dict[int, Counter[str]] = {}
    hue_by_hex: dict[str, float] = {}
    chromatic_occurrences = 0
    for hex_value, weight in weight_by_hex.items():
        hue, saturation, lightness = _hex_to_hsl(hex_value)
        if _is_neutral(saturation, lightness):
            continue
        chromatic_occurrences += weight
        hue_by_hex[hex_value] = hue
        bucket = int(hue // HUE_BUCKET_DEGREES) * HUE_BUCKET_DEGREES
        bucket_weights[bucket] += weight
        bucket_colors.setdefault(bucket, Counter())[hex_value] += weight

    hue_buckets: list[dict[str, Any]] = []
    for bucket, weight in bucket_weights.most_common():
        colors = bucket_colors[bucket]
        representative_hex = colors.most_common(1)[0][0]
        hue_buckets.append(
            {
                "bucket": bucket,
                "weight": weight,
                "representative_hex": representative_hex,
                "hue": round(hue_by_hex[representative_hex]),
                "hex_samples": [h for h, _w in colors.most_common()][:_RECOLOR_SAMPLE_LIMIT],
            }
        )

    dominant = None
    if hue_buckets:
        top = hue_buckets[0]
        dominant = {
            "hex": top["representative_hex"],
            "hue": top["hue"],
            "weight": top["weight"],
        }
    return {
        "chromatic_occurrence_count": chromatic_occurrences,
        "hue_buckets": hue_buckets,
        "dominant": dominant,
    }


# ==== warning 判定 ====

def _drift_warnings(observed: dict[str, Any], expected: dict[str, Any]) -> list[dict[str, Any]]:
    dominant = observed.get("dominant")
    if not dominant:
        return []
    nearest_hex, nearest_hue, delta = _nearest_allowed(float(dominant["hue"]), expected["allowed"])
    if delta <= HUE_DRIFT_TOLERANCE_DEGREES:
        return []
    top_bucket = observed["hue_buckets"][0]
    return [
        {
            "code": "SLIDE_COLOR_SCHEME_DRIFT",
            "severity": "warning",
            "message": (
                f"页面主色相 h≈{dominant['hue']}°（{dominant['hex']}，"
                f"权重 {dominant['weight']}）与 deck 色系最近允许色相 "
                f"h≈{round(nearest_hue)}°（{nearest_hex}）偏差 {round(delta)}°，"
                f"超过 {round(HUE_DRIFT_TOLERANCE_DEGREES)}° 阈值；"
                "本页主色调应与整份 deck 保持同一色系。"
            ),
            "observed_hue": dominant["hue"],
            "observed_hex": dominant["hex"],
            "nearest_allowed_hex": nearest_hex,
            "nearest_allowed_hue": round(nearest_hue),
            "hue_delta": round(delta),
            "repair_suggestion": _recolor_suggestion(
                offending_hex=list(top_bucket["hex_samples"]),
                expected=expected,
            ),
        }
    ]


def _overflow_warnings(observed: dict[str, Any], expected: dict[str, Any]) -> list[dict[str, Any]]:
    hue_buckets = observed.get("hue_buckets") or []
    if len(hue_buckets) <= CHROMATIC_HUE_BUCKET_MAX:
        return []
    offending: list[str] = []
    kept_buckets: list[int] = []
    for bucket in hue_buckets:
        _hex, _hue, delta = _nearest_allowed(float(bucket["hue"]), expected["allowed"])
        if delta > HUE_DRIFT_TOLERANCE_DEGREES:
            offending.extend(bucket["hex_samples"])
        else:
            kept_buckets.append(int(bucket["bucket"]))
    bucket_hues = [int(bucket["bucket"]) for bucket in hue_buckets]
    return [
        {
            "code": "SLIDE_COLOR_PALETTE_OVERFLOW",
            "severity": "warning",
            "message": (
                f"页面非中性色相桶达 {len(hue_buckets)} 个"
                f"（>{CHROMATIC_HUE_BUCKET_MAX}，色相桶 {bucket_hues}），配色过散；"
                "并列卡片/模块不要逐卡换色相，应共享 deck 主色，只用透明度或"
                "明度做层次区分。"
            ),
            "hue_bucket_count": len(hue_buckets),
            "hue_buckets": bucket_hues,
            "repair_suggestion": _recolor_suggestion(
                offending_hex=offending,
                expected=expected,
                keep_hue_buckets=kept_buckets,
            ),
        }
    ]


def _recolor_suggestion(
    *,
    offending_hex: list[str],
    expected: dict[str, Any],
    keep_hue_buckets: list[int] | None = None,
) -> dict[str, Any]:
    primary_hex = expected["primary_hex"]
    suggestion: dict[str, Any] = {
        "action": (
            f"把偏离 deck 色系的颜色统一收敛到主色 {primary_hex}"
            "（层次差异改用同色系明度/透明度表达）"
        ),
        "recolor_map": (
            [{"from_hex": offending_hex[:_RECOLOR_SAMPLE_LIMIT], "to_hex": primary_hex}]
            if offending_hex
            else []
        ),
        "allowed_hex": [hex_value for hex_value, _hue in expected["allowed"]],
    }
    if keep_hue_buckets is not None:
        suggestion["keep_hue_buckets"] = keep_hue_buckets
    return suggestion


def _nearest_allowed(hue: float, allowed: list[tuple[str, float]]) -> tuple[str, float, float]:
    best_hex, best_hue = allowed[0]
    best_delta = _hue_distance(hue, best_hue)
    for hex_value, allowed_hue in allowed[1:]:
        delta = _hue_distance(hue, allowed_hue)
        if delta < best_delta:
            best_hex, best_hue, best_delta = hex_value, allowed_hue, delta
    return best_hex, best_hue, best_delta


# ==== 颜色原语 ====

def _parse_color_token(token: Any) -> str | None:
    """把 CSS 颜色 token 归一为大写 ``#RRGGBB``；不可解析返回 None。"""
    if not isinstance(token, str):
        return None
    text = token.strip()
    if not text:
        return None
    lowered = text.lower()
    if lowered in _SKIP_TOKENS or lowered.startswith("url("):
        return None
    hex_match = _HEX_RE.search(text)
    if hex_match:
        raw = hex_match.group(0)[1:]
        if len(raw) == 3:
            raw = "".join(ch * 2 for ch in raw)
        return f"#{raw.upper()}"
    rgb_match = _RGB_FUNC_RE.search(text)
    if rgb_match:
        channels = [min(255, int(part)) for part in rgb_match.groups()]
        return "#{:02X}{:02X}{:02X}".format(*channels)
    return None


def _hex_to_hsl(hex_value: str) -> tuple[float, float, float]:
    raw = hex_value.lstrip("#")
    r = int(raw[0:2], 16) / 255.0
    g = int(raw[2:4], 16) / 255.0
    b = int(raw[4:6], 16) / 255.0
    max_c = max(r, g, b)
    min_c = min(r, g, b)
    lightness = (max_c + min_c) / 2.0
    if max_c == min_c:
        return 0.0, 0.0, lightness
    delta = max_c - min_c
    saturation = delta / (1.0 - abs(2.0 * lightness - 1.0))
    if max_c == r:
        hue = ((g - b) / delta) % 6.0
    elif max_c == g:
        hue = (b - r) / delta + 2.0
    else:
        hue = (r - g) / delta + 4.0
    return (hue * 60.0) % 360.0, saturation, lightness


def _is_neutral(saturation: float, lightness: float) -> bool:
    return (
        saturation < NEUTRAL_SATURATION_MAX
        or lightness > NEUTRAL_LIGHTNESS_MAX
        or lightness < NEUTRAL_LIGHTNESS_MIN
    )


def _hue_distance(a: float, b: float) -> float:
    diff = abs(a - b) % 360.0
    return min(diff, 360.0 - diff)
