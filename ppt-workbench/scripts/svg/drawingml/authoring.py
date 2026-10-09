"""SVG authoring helpers for route-aware write, inspect, and layer patch.

本模块只处理模型编写的 SVG XML 文本：解析、分层摘要和按 id 局部 patch。
它不读取 workspace、不触发 renderer、不生成 PPTX，避免把 authoring 层逻辑继续塞进
SVG DrawingML 编译主流程。
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from typing import Any


class SvgAuthoringPatchError(ValueError):
    """可转成模型可读 issue 的 SVG patch 错误。"""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(f"{code}: {message}")
        self.code = code
        self.message = message


def validate_svg_string_for_authoring(svg: str) -> tuple[bool, dict[str, Any] | None]:
    if not isinstance(svg, str) or not svg.strip():
        return False, {
            "code": "SVG_INVALID_XML",
            "message": "SVG 内容为空或不是字符串。",
            "fix_hint": "用 write_svg 重写完整 SVG 壳，确保只有一个 <svg> 根节点。",
        }
    try:
        ET.fromstring(svg)
    except ET.ParseError as exc:
        return False, {
            "code": "SVG_INVALID_XML",
            "message": str(exc),
            "fix_hint": "修复 XML 不良构；必要时用 write_svg 重写完整 SVG 壳。",
        }
    return True, None


def patch_svg_layer_text(
    svg: str,
    *,
    layer_id: str,
    operation: str,
    svg_fragment: str | None = None,
    anchor_layer_id: str | None = None,
) -> tuple[str, dict[str, Any]]:
    ET.register_namespace("", "http://www.w3.org/2000/svg")
    try:
        root = ET.fromstring(svg)
    except ET.ParseError as exc:
        raise SvgAuthoringPatchError("SVG_INVALID_XML", f"原 SVG XML 不良构：{exc}") from exc
    matches = find_elements_by_id(root, layer_id)
    operation = (operation or "").strip()
    fragment = None
    if operation != "remove":
        if not svg_fragment or not svg_fragment.strip():
            raise SvgAuthoringPatchError("SVG_FRAGMENT_REQUIRED", "svg_fragment 不能为空。")
        try:
            fragment = ET.fromstring(svg_fragment)
        except ET.ParseError as exc:
            raise SvgAuthoringPatchError("SVG_INVALID_FRAGMENT", f"svg_fragment XML 不良构：{exc}") from exc
        if fragment.attrib.get("id") != layer_id and operation in {"replace", "append"}:
            fragment.attrib["id"] = layer_id
        _reject_duplicate_fragment_id(root, fragment, layer_id=layer_id, operation=operation)
    if operation == "replace":
        if len(matches) != 1:
            raise SvgAuthoringPatchError("SVG_LAYER_ID_NOT_UNIQUE", "replace 要求 layer_id 唯一存在。")
        parent, index = find_parent_and_index(root, matches[0])
        assert parent is not None and index is not None and fragment is not None
        sibling_count = max(len(list(parent)) - 1, 0)
        parent.remove(matches[0])
        parent.insert(index, fragment)
    elif operation == "remove":
        if len(matches) != 1:
            raise SvgAuthoringPatchError("SVG_LAYER_ID_NOT_UNIQUE", "remove 要求 layer_id 唯一存在。")
        parent, _index = find_parent_and_index(root, matches[0])
        if parent is None:
            raise SvgAuthoringPatchError("SVG_ROOT_REMOVE_FORBIDDEN", "不允许删除根 <svg>。")
        sibling_count = max(len(list(parent)) - 1, 0)
        parent.remove(matches[0])
    elif operation == "append":
        assert fragment is not None
        parent = root
        if anchor_layer_id:
            parents = find_elements_by_id(root, anchor_layer_id)
            if len(parents) != 1:
                raise SvgAuthoringPatchError("SVG_ANCHOR_LAYER_NOT_UNIQUE", "append 父 layer 必须唯一存在。")
            parent = parents[0]
        sibling_count = len(list(parent))
        parent.append(fragment)
    elif operation in {"insert_before", "insert_after"}:
        assert fragment is not None
        anchor = anchor_layer_id or layer_id
        anchors = find_elements_by_id(root, anchor)
        if len(anchors) != 1:
            raise SvgAuthoringPatchError("SVG_ANCHOR_LAYER_NOT_UNIQUE", "insert 锚点 layer 必须唯一存在。")
        parent, index = find_parent_and_index(root, anchors[0])
        if parent is None or index is None:
            raise SvgAuthoringPatchError("SVG_ROOT_INSERT_FORBIDDEN", "不允许在根 <svg> 外插入。")
        sibling_count = len(list(parent))
        parent.insert(index if operation == "insert_before" else index + 1, fragment)
    else:
        raise SvgAuthoringPatchError(
            "SVG_PATCH_OPERATION_INVALID",
            "operation 只能是 replace/append/insert_before/insert_after/remove。",
        )
    return ET.tostring(root, encoding="unicode"), {
        "layer_id": layer_id,
        "operation": operation,
        "preserved_sibling_count": sibling_count,
    }


def inspect_svg_layers(
    root: ET.Element,
    *,
    include_text_excerpt: bool,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    layers: list[dict[str, Any]] = []
    seen: dict[str, int] = {}
    for element in root.iter():
        element_id = element.attrib.get("id")
        if not isinstance(element_id, str) or not element_id.strip():
            continue
        seen[element_id] = seen.get(element_id, 0) + 1
        item: dict[str, Any] = {
            "id": element_id,
            "tag": svg_local_name(element.tag),
            "child_count": len(list(element)),
        }
        if include_text_excerpt:
            excerpt = element_text_excerpt(element)
            if excerpt:
                item["text_excerpt"] = excerpt
        layers.append(item)
    warnings = [
        {
            "code": "SVG_LAYER_ID_DUPLICATED",
            "message": f"id={element_id} 出现 {count} 次；patch 前需保证目标 id 唯一。",
            "layer_id": element_id,
        }
        for element_id, count in seen.items()
        if count > 1
    ]
    return layers[:80], warnings[:20]


def find_elements_by_id(root: ET.Element, element_id: str) -> list[ET.Element]:
    return [element for element in root.iter() if element.attrib.get("id") == element_id]


def _reject_duplicate_fragment_id(
    root: ET.Element,
    fragment: ET.Element,
    *,
    layer_id: str,
    operation: str,
) -> None:
    fragment_id = fragment.attrib.get("id")
    if not isinstance(fragment_id, str) or not fragment_id:
        return
    existing = find_elements_by_id(root, fragment_id)
    if operation == "replace" and fragment_id == layer_id and len(existing) == 1:
        return
    if existing:
        raise SvgAuthoringPatchError(
            "SVG_LAYER_ID_DUPLICATED",
            f"svg_fragment id={fragment_id} 会造成重复 layer id。",
        )


def find_parent_and_index(
    root: ET.Element,
    target: ET.Element,
) -> tuple[ET.Element | None, int | None]:
    for parent in root.iter():
        children = list(parent)
        for index, child in enumerate(children):
            if child is target:
                return parent, index
    return None, None


def element_text_excerpt(element: ET.Element) -> str:
    texts = [" ".join(str(text).split()) for text in element.itertext() if str(text).strip()]
    return " / ".join(texts)[:120]


def svg_local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1] if "}" in tag else tag
