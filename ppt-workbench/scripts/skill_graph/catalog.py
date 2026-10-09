"""Local capability-tree catalog. File-backed; no host index stack."""

from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path
from typing import Any


DIMENSION_CATEGORIES: dict[str, frozenset[str]] = {
    "layout": frozenset(
        {
            "layout",
            "composition-branch",
            "composition-system",
            "shape-patterns",
            "shape-component-library",
        }
    ),
    "theme": frozenset({"visual-theme", "template-series", "asset-reference"}),
    "qa": frozenset({"anti-pattern-qa"}),
    "content": frozenset({"content-structure", "scenario-template"}),
    "contract": frozenset({"execution-contract"}),
}
PRIORITY_SCORE = {"P0": 3.0, "P1": 2.0, "P2": 1.0}
_CSV_SPLIT = re.compile(r"[,;，、]")
_HEADING = re.compile(r"^#\s+(.+)$", re.M)
_EXAMPLE_PATH = re.compile(r"assets/examples/[A-Za-z0-9_./\-]+?\.(?:svg|json)")


def skill_root() -> Path:
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / "SKILL.md").is_file() and (parent / "references").is_dir():
            return parent
    raise FileNotFoundError("ppt-workbench SKILL.md not found")


def slide_authoring_root(root: Path | None = None) -> Path:
    base = root or skill_root()
    return base / "references" / "generate" / "original" / "slide-authoring"


def references_dir(root: Path | None = None) -> Path:
    return slide_authoring_root(root) / "references"


def examples_root(root: Path | None = None) -> Path:
    return slide_authoring_root(root) / "assets" / "examples"


def tree_path(root: Path | None = None) -> Path:
    return references_dir(root) / "_index" / "capability-tree.json"


def as_module_id(value: str) -> str:
    text = str(value or "").strip().replace("\\", "/")
    if ":" in text and not text.startswith("assets/"):
        prefix, _, rest = text.partition(":")
        if rest:
            text = rest
    name = text.split("/")[-1]
    if name.endswith(".md"):
        name = name[:-3]
    return name.strip()


def split_csv(value: Any) -> list[str]:
    if isinstance(value, (list, tuple)):
        items = [str(item).strip() for item in value]
    else:
        items = [part.strip() for part in _CSV_SPLIT.split(str(value or ""))]
    out: list[str] = []
    for item in items:
        item = item.strip().strip("`")
        if item and item.lower() != "none" and item not in out:
            out.append(item)
    return out


def parse_html_meta(text: str) -> dict[str, str]:
    blob = text.lstrip()
    if not blob.startswith("<!--"):
        return {}
    end = blob.find("-->")
    if end < 0:
        return {}
    meta: dict[str, str] = {}
    for raw in blob[4:end].splitlines():
        line = raw.strip().lstrip("*").strip()
        if not line or ":" not in line:
            continue
        key, _, value = line.partition(":")
        key = key.strip()
        if key:
            meta[key] = value.strip()
    return meta


def first_heading(text: str) -> str:
    match = _HEADING.search(text)
    return match.group(1).strip() if match else ""


def excerpt_text(text: str, limit: int = 220) -> str:
    compact = " ".join(str(text or "").split())
    if not compact:
        return ""
    parts = re.split(r"(?<=[。！？.!?])\s+", compact)
    chosen = "".join(parts[:2]) if parts else compact
    if len(chosen) > limit:
        return chosen[: limit - 3] + "..."
    return chosen


def _file_stem_id(file_name: str) -> str:
    return as_module_id(file_name)


@lru_cache(maxsize=1)
def load_tree(root_str: str | None = None) -> dict[str, Any]:
    path = tree_path(Path(root_str) if root_str else None)
    return json.loads(path.read_text(encoding="utf-8"))


def always_read_ids(tree: dict[str, Any] | None = None) -> list[str]:
    data = tree if tree is not None else load_tree()
    return [
        _file_stem_id(str(item.get("file") or ""))
        for item in data.get("always_read") or []
        if isinstance(item, dict) and item.get("file")
    ]


def default_gold_ids(tree: dict[str, Any] | None = None) -> list[str]:
    data = tree if tree is not None else load_tree()
    return [
        _file_stem_id(str(item.get("file") or ""))
        for item in data.get("default_gold_path") or []
        if isinstance(item, dict) and item.get("file")
    ]


def _merge_node(node: dict[str, Any], refs: Path) -> dict[str, Any]:
    file_name = str(node.get("file") or "").strip()
    path = refs / file_name if file_name else None
    markdown = ""
    meta: dict[str, str] = {}
    title = ""
    if path is not None and path.is_file():
        markdown = path.read_text(encoding="utf-8")
        meta = parse_html_meta(markdown)
        title = first_heading(markdown)
    triggers = split_csv(node.get("triggers"))
    triggers.extend(split_csv(meta.get("triggers")))
    requires = split_csv(node.get("requires"))
    requires.extend(as_module_id(item) for item in split_csv(meta.get("requires")))
    page_roles = [item.lower() for item in split_csv(node.get("page_roles"))]
    page_roles.extend(item.lower() for item in split_csv(meta.get("page_roles")))
    module_id = str(node.get("id") or meta.get("id") or _file_stem_id(file_name))
    category = str(node.get("category") or meta.get("category") or "")
    intent = str(node.get("intent") or meta.get("read_when") or "").strip()
    return {
        "module_id": module_id,
        "file": file_name,
        "path": str(path) if path is not None else "",
        "title": title or module_id,
        "category": category,
        "intent": intent,
        "excerpt": excerpt_text(intent or title),
        "page_roles": list(dict.fromkeys(page_roles)),
        "triggers": list(dict.fromkeys(triggers)),
        "requires": list(dict.fromkeys(as_module_id(item) for item in requires if item)),
        "priority": str(node.get("priority") or "P2"),
        "outputs": split_csv(node.get("outputs")),
    }


def _node_from_file(file_name: str, refs: Path, extra: dict[str, Any] | None = None) -> dict[str, Any]:
    path = refs / file_name
    markdown = path.read_text(encoding="utf-8") if path.is_file() else ""
    meta = parse_html_meta(markdown)
    payload = {
        "id": meta.get("id") or as_module_id(file_name),
        "file": file_name,
        "category": meta.get("category") or "",
        "intent": (extra or {}).get("reason") or meta.get("read_when") or "",
        "page_roles": split_csv(meta.get("page_roles")),
        "triggers": split_csv(meta.get("triggers")),
        "requires": split_csv(meta.get("requires")),
        "outputs": split_csv(meta.get("outputs")),
        "priority": "P0",
    }
    if extra:
        payload["intent"] = str(extra.get("reason") or payload["intent"])
    return _merge_node(payload, refs)


@lru_cache(maxsize=1)
def catalog_nodes(root_str: str | None = None) -> tuple[dict[str, Any], ...]:
    root = Path(root_str) if root_str else skill_root()
    tree = load_tree(str(root))
    refs = references_dir(root)
    nodes = []
    seen_files: set[str] = set()
    seen_ids: set[str] = set()
    for raw in tree.get("nodes") or []:
        if not isinstance(raw, dict) or not raw.get("id"):
            continue
        node = _merge_node(raw, refs)
        nodes.append(node)
        seen_ids.add(node["module_id"])
        if node.get("file"):
            seen_files.add(str(node["file"]))
    for key in ("always_read", "default_gold_path"):
        for item in tree.get(key) or []:
            if not isinstance(item, dict) or not item.get("file"):
                continue
            file_name = str(item["file"])
            stem = as_module_id(file_name)
            if file_name in seen_files or stem in seen_ids:
                continue
            node = _node_from_file(file_name, refs, extra=item)
            nodes.append(node)
            seen_ids.add(node["module_id"])
            seen_files.add(file_name)
    return tuple(nodes)


def node_index(root: Path | None = None) -> dict[str, dict[str, Any]]:
    root_str = str(root or skill_root())
    index: dict[str, dict[str, Any]] = {}
    for node in catalog_nodes(root_str):
        index[node["module_id"]] = node
        if node.get("file"):
            index.setdefault(as_module_id(node["file"]), node)
            index.setdefault(str(node["file"]), node)
    return index


def resolve_node(identifier: str, root: Path | None = None) -> dict[str, Any] | None:
    key = as_module_id(identifier)
    index = node_index(root)
    return index.get(key) or index.get(identifier.strip())


def gold_examples_overlay_path(root: Path | None = None) -> Path:
    return (root or skill_root()) / "references" / "generate" / "gold-examples-catalog.json"


def gold_examples(root: Path | None = None) -> list[dict[str, Any]]:
    """Merge SHA-frozen examples-manifest gold_examples with the workbench overlay."""

    base = root or skill_root()
    merged: dict[str, dict[str, Any]] = {}
    original = examples_root(base) / "svg-ppt" / "examples-manifest.json"
    if original.is_file():
        data = json.loads(original.read_text(encoding="utf-8"))
        for item in data.get("gold_examples") or []:
            if isinstance(item, dict) and item.get("id"):
                merged[str(item["id"])] = item
    overlay = gold_examples_overlay_path(base)
    if overlay.is_file():
        data = json.loads(overlay.read_text(encoding="utf-8"))
        for item in data.get("gold_examples") or []:
            if isinstance(item, dict) and item.get("id"):
                merged[str(item["id"])] = item
    return list(merged.values())


def example_refs_in(markdown: str, root: Path | None = None) -> list[dict[str, Any]]:
    authoring = slide_authoring_root(root)
    found: list[dict[str, Any]] = []
    seen: set[str] = set()
    for match in _EXAMPLE_PATH.findall(markdown or ""):
        if match in seen:
            continue
        seen.add(match)
        resolved = (authoring / match).resolve()
        found.append(
            {
                "path": match,
                "exists": resolved.is_file(),
            }
        )
    return found
