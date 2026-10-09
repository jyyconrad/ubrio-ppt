"""SVG input gate 的结构化修复指令（可机械执行的 ops）。

背景（真实回归 conversation 72f408ce）：input_gate 的几何 blocking issue 只给自然
语言描述——`SVG_CONTENT_BOUNDS_OVERFLOW` 只报"右边界到 1422px"却不指出是哪个元素，
`SVG_TEXT_OVERLAP` 只给 `text@x:y` 这种坐标合成 id（不能直接喂给
`patch_svg_layer(layer_id=...)`）。模型因此无法定位问题层，退化成 `read_file` 重读整页
SVG 再猜——单页修复循环烧掉 60-95 万 input token。

这里把已经算好的几何事实翻译成 `{op, target, constraint, rationale}`，口径与
`render_qa_report.blocking_repair_plan[].ops[]`（`qa_gate_internals/repair_plan.py`）
一致：target 一律是可以直接传给 `patch_svg_layer` 的 layer_id，或明确的元素定位串。
"""

from __future__ import annotations

from typing import Any

# 单条 issue 最多列出的越界元素数：给足定位信息，又不把模型上下文撑爆。
MAX_OFFENDERS = 5


def _target_for(element: dict[str, Any]) -> str:
    """优先用 layer_id（可直接 patch），退化到元素定位串。"""

    layer_id = element.get("layer_id")
    if isinstance(layer_id, str) and layer_id.strip():
        return layer_id
    element_id = element.get("element_id")
    if isinstance(element_id, str) and element_id.strip():
        return element_id
    return "svg_root"


def _layer_targets(elements: list[dict[str, Any]]) -> list[str]:
    targets: list[str] = []
    for element in elements:
        target = _target_for(element)
        if target not in targets:
            targets.append(target)
    return targets


def build_bounds_overflow_ops(
    *,
    offending_elements: list[dict[str, Any]],
    overflow_x_px: float,
    overflow_y_px: float,
) -> list[dict[str, Any]]:
    """内容主体越界：按越界元素给出"收多少 px、改哪个 layer"。"""

    if not offending_elements:
        return [
            {
                "op": "shrink_content_to_canvas",
                "target": "svg_root",
                "constraint": "所有元素的 right<=viewBox 宽、bottom<=viewBox 高",
                "rationale": "内容主体越出画布，最终 PPTX 会被裁断。",
            }
        ]
    ops: list[dict[str, Any]] = []
    for element in offending_elements[:MAX_OFFENDERS]:
        over_x = float(element.get("overflow_x") or 0.0)
        over_y = float(element.get("overflow_y") or 0.0)
        constraints: list[str] = []
        if over_x > 0:
            constraints.append(f"右边界左移 >= {round(over_x, 1)}px")
        if over_y > 0:
            constraints.append(f"下边界上移 >= {round(over_y, 1)}px")
        ops.append(
            {
                "op": "patch_svg_layer",
                "target": _target_for(element),
                "constraint": "；".join(constraints) or "把元素收回画布内",
                "rationale": (
                    f"元素 {element.get('element_id')}（{element.get('tag')}）"
                    f"右边界 {element.get('right')}px / 下边界 {element.get('bottom')}px "
                    "越出画布，会被裁断。缩短文案、折行、缩小字号或整体左移该 layer。"
                ),
            }
        )
    if overflow_x_px > 0 and len(offending_elements) > 1:
        ops.append(
            {
                "op": "reflow_columns",
                "target": ",".join(_layer_targets(offending_elements)),
                "constraint": f"整体横向收紧 >= {round(overflow_x_px, 1)}px",
                "rationale": "多个同排元素同时越界，说明列宽/列距整体偏大，按栏重排比逐个微调更稳。",
            }
        )
    if overflow_y_px > 0 and len(offending_elements) > 1:
        ops.append(
            {
                "op": "reflow_rows",
                "target": ",".join(_layer_targets(offending_elements)),
                "constraint": f"整体纵向收紧 >= {round(overflow_y_px, 1)}px",
                "rationale": "多个元素纵向越界，说明行高/行距整体偏大。",
            }
        )
    return ops


def build_text_overlap_ops(
    *,
    element_boxes: list[dict[str, Any]],
    overlap_x_px: float,
    overlap_y_px: float,
) -> list[dict[str, Any]]:
    """文本重叠：给出两个重叠文本各自的 layer 与需要让开的 px。"""

    targets = _layer_targets(element_boxes)
    excerpts = " / ".join(
        str(box.get("text_excerpt") or box.get("element_id") or "")
        for box in element_boxes
    )
    return [
        {
            "op": "patch_svg_layer",
            "target": targets[0] if targets else "svg_root",
            "constraint": (
                f"两个文本盒的横向重叠 {round(overlap_x_px, 1)}px、"
                f"纵向重叠 {round(overlap_y_px, 1)}px 必须归零"
            ),
            "rationale": (
                f"重叠文本：{excerpts}。缩短其中较长的一段、折成 <tspan> 多行，"
                "或加大列间距/行距让两个文本盒不再相交。"
            ),
        }
    ]


def build_text_box_overflow_ops(
    *,
    layer_id: str | None,
    element_id: str | None,
    overflow_px: float,
    char_count: int,
    font_size: float,
    max_chars_per_line: int,
) -> list[dict[str, Any]]:
    """单个 <text> 长句未折行：给出必须砍掉的宽度和建议每行字数。"""

    target = layer_id or element_id or "svg_root"
    return [
        {
            "op": "patch_svg_layer",
            "target": target,
            "constraint": (
                f"该 <text> 估算右边界必须回到画布内（至少收窄 {round(overflow_px, 1)}px）；"
                f"单行不超过约 {max_chars_per_line} 字"
            ),
            "rationale": (
                f"单个 <text> 承载 {char_count} 字、font-size={font_size}，"
                "一行排到画布外会被裁断。拆成 2-3 行 <tspan>（各自带 x 与 dy）或压缩文案。"
            ),
        }
    ]
