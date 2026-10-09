#!/usr/bin/env python3
"""Load always_read + default_gold_path + ≤4 primaries and requires. Examples by path."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any


_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

import catalog as _catalog  # noqa: E402


DEFAULT_EXAMPLE_BYTES = 12288
MAX_PRIMARY = 4
_ALLOWED_EXAMPLE_SUFFIXES = {".svg", ".json"}


def _read_module(node: dict[str, Any], role: str) -> dict[str, Any]:
    path = Path(node["path"]) if node.get("path") else None
    content = path.read_text(encoding="utf-8") if path is not None and path.is_file() else ""
    rel = ""
    if path is not None and path.is_file():
        try:
            rel = path.resolve().relative_to(_catalog.skill_root()).as_posix()
        except ValueError:
            rel = str(path)
    return {
        "role": role,
        "module_id": node["module_id"],
        "title": node["title"],
        "path": rel,
        "content": content,
        "truncated": False,
        "read_more": None,
    }


def _claim(
    module_id: str,
    role: str,
    *,
    index: dict[str, dict[str, Any]],
    claimed: set[str],
    modules: list[dict[str, Any]],
    unresolved: list[str],
) -> bool:
    node = _catalog.resolve_node(module_id) if module_id not in index else index.get(module_id)
    if node is None:
        node = index.get(_catalog.as_module_id(module_id))
    if node is None:
        if module_id not in unresolved:
            unresolved.append(module_id)
        return False
    real_id = node["module_id"]
    if real_id in claimed:
        return False
    claimed.add(real_id)
    modules.append(_read_module(node, role))
    return True


def _expand_requires(
    primary_ids: list[str],
    index: dict[str, dict[str, Any]],
) -> list[str]:
    out: list[str] = []
    seen = set(primary_ids)
    queue = list(primary_ids)
    while queue:
        current = queue.pop(0)
        node = index.get(current) or _catalog.resolve_node(current)
        if node is None:
            continue
        for req in node.get("requires") or []:
            rid = _catalog.as_module_id(req)
            if not rid or rid in seen:
                continue
            seen.add(rid)
            out.append(rid)
            queue.append(rid)
    return out


def load_modules(
    module_ids: list[str] | tuple[str, ...] | None = None,
    page_role: str | None = None,
    example: str | None = None,
    max_bytes: int = DEFAULT_EXAMPLE_BYTES,
    root: Path | None = None,
) -> dict[str, Any]:
    root_path = root or _catalog.skill_root()
    tree = _catalog.load_tree(str(root_path))
    index = _catalog.node_index(root_path)
    requested = [_catalog.as_module_id(item) for item in (module_ids or []) if str(item).strip()]
    unresolved: list[str] = []
    modules: list[dict[str, Any]] = []
    claimed: set[str] = set()

    for module_id in _catalog.always_read_ids(tree):
        _claim(module_id, "baseline", index=index, claimed=claimed, modules=modules, unresolved=unresolved)
    for module_id in _catalog.default_gold_ids(tree):
        _claim(module_id, "gold_path", index=index, claimed=claimed, modules=modules, unresolved=unresolved)

    resolved_requested: list[str] = []
    for module_id in requested:
        node = index.get(module_id) or _catalog.resolve_node(module_id)
        if node is None:
            if module_id not in unresolved:
                unresolved.append(module_id)
            continue
        resolved_requested.append(node["module_id"])

    primaries = resolved_requested[:MAX_PRIMARY]
    deferred = resolved_requested[MAX_PRIMARY:]
    for module_id in primaries:
        _claim(module_id, "primary", index=index, claimed=claimed, modules=modules, unresolved=unresolved)
    for module_id in _expand_requires(primaries, index):
        _claim(module_id, "requires", index=index, claimed=claimed, modules=modules, unresolved=unresolved)

    example_refs: list[dict[str, Any]] = []
    seen_refs: set[str] = set()
    for item in modules:
        for ref in _catalog.example_refs_in(item.get("content") or "", root_path):
            path = ref["path"]
            if path in seen_refs:
                continue
            seen_refs.add(path)
            example_refs.append(ref)

    examples = []
    if example:
        loaded_example = load_example(example, max_bytes=max_bytes, root=root_path)
        examples.append(loaded_example)

    loaded_ids: list[str] = []
    for item in modules:
        for alias in (item["module_id"], _catalog.as_module_id(Path(item["path"]).name)):
            if alias and alias not in loaded_ids:
                loaded_ids.append(alias)
    return {
        "page_role": (page_role or "").strip() or None,
        "primary_module_ids": primaries,
        "loaded_module_ids": loaded_ids,
        "deferred_module_ids": deferred,
        "candidate_module_ids": list(dict.fromkeys([*deferred, *unresolved])),
        "unresolved_module_ids": unresolved,
        "modules": modules,
        "example_refs": example_refs,
        "examples": examples,
        "next_action": (
            "example_refs are pointers; open with --example. Copy hierarchy, not x/y."
            if example_refs and not examples
            else None
        ),
    }


def load_example(
    path: str,
    max_bytes: int = DEFAULT_EXAMPLE_BYTES,
    root: Path | None = None,
) -> dict[str, Any]:
    raw = str(path or "").strip().replace("\\", "/")
    if ":" in raw:
        prefix, _, rest = raw.partition(":")
        if rest.strip() and prefix in {"slide-authoring", "ppt-workbench"}:
            raw = rest.strip()
    raw = raw.lstrip("/")
    while raw.startswith("./"):
        raw = raw[2:]
    if not raw:
        return {"ok": False, "error_code": "empty_path", "error": "path 不能为空"}

    authoring = _catalog.slide_authoring_root(root)
    examples = _catalog.examples_root(root)
    try:
        examples_resolved = examples.resolve()
    except OSError:
        return {"ok": False, "error_code": "examples_root_missing", "error": "assets/examples 不存在"}

    candidates = [authoring / raw]
    if not raw.startswith("assets/"):
        candidates.append(examples / raw)
    resolved: Path | None = None
    for candidate in candidates:
        try:
            candidate_resolved = candidate.resolve()
        except OSError:
            continue
        try:
            candidate_resolved.relative_to(examples_resolved)
        except ValueError:
            continue
        resolved = candidate_resolved
        break
    if resolved is None:
        return {
            "ok": False,
            "error_code": "outside_whitelist",
            "error": "路径必须落在 slide-authoring/assets/examples 下",
            "requested_path": raw,
        }
    if resolved.suffix.lower() not in _ALLOWED_EXAMPLE_SUFFIXES:
        return {
            "ok": False,
            "error_code": "unsupported_extension",
            "error": "只允许 .svg 或 .json",
            "requested_path": raw,
        }
    if not resolved.is_file():
        return {
            "ok": False,
            "error_code": "not_found",
            "error": f"金标示例不存在: {raw}",
            "requested_path": raw,
        }

    limit = max(1024, min(int(max_bytes), 65536))
    raw_bytes = resolved.read_bytes()
    truncated = len(raw_bytes) > limit
    payload = raw_bytes[:limit] if truncated else raw_bytes
    try:
        rel = resolved.relative_to(authoring.resolve()).as_posix()
    except ValueError:
        rel = raw
    return {
        "ok": True,
        "path": rel,
        "media_type": "manifest_json" if resolved.suffix.lower() == ".json" else "svg_example",
        "content": payload.decode("utf-8", errors="ignore"),
        "total_bytes": len(raw_bytes),
        "returned_bytes": len(payload),
        "truncated": truncated,
        "sha256": hashlib.sha256(raw_bytes).hexdigest(),
        "next_action": "structure reference; copy hierarchy and density, not coordinates",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Load always_read cores, default gold path, then ≤4 primaries and requires."
    )
    parser.add_argument("--module-ids", default="", help="comma-separated candidate ids from search")
    parser.add_argument("--page-role", default=None)
    parser.add_argument("--example", default=None, help="path under assets/examples")
    parser.add_argument("--max-bytes", type=int, default=DEFAULT_EXAMPLE_BYTES)
    args = parser.parse_args(argv)
    ids = [part.strip() for part in str(args.module_ids).split(",") if part.strip()]
    if args.example and not ids:
        json.dump(
            load_example(args.example, max_bytes=args.max_bytes),
            sys.stdout,
            ensure_ascii=False,
            indent=2,
        )
        sys.stdout.write("\n")
        return 0
    payload = load_modules(
        module_ids=ids,
        page_role=args.page_role,
        example=args.example,
        max_bytes=args.max_bytes,
    )
    json.dump(payload, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
