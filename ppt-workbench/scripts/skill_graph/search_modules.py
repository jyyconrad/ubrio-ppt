#!/usr/bin/env python3
"""Score capability-tree nodes. Return candidates only; never module bodies."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

import catalog as _catalog  # noqa: E402


_TOKEN = re.compile(r"[a-z0-9]+|[A-Za-z]+|[\u4e00-\u9fff]{2,}")
_DIMENSIONS = tuple(_catalog.DIMENSION_CATEGORIES)


def _tokens(text: str) -> list[str]:
    return [part.lower() for part in _TOKEN.findall(text or "") if part]


def _score_node(
    node: dict[str, Any],
    *,
    query: str,
    page_role: str | None,
    dimension: str | None,
) -> tuple[float, list[str]]:
    query_l = query.lower()
    score = 0.0
    reasons: list[str] = []
    for trigger in node.get("triggers") or []:
        lowered = str(trigger).lower()
        if lowered and lowered in query_l:
            score += 6.0
            reasons.append(f"trigger:{trigger}")
    role = (page_role or "").strip().lower()
    if role and role in {item.lower() for item in node.get("page_roles") or []}:
        score += 2.0
        reasons.append(f"page_role:{role}")
    category = str(node.get("category") or "")
    if dimension:
        allowed = _catalog.DIMENSION_CATEGORIES[dimension]
        if category in allowed:
            score += 3.0
            reasons.append(f"category:{category}")
        else:
            return 0.0, []
    haystack = " ".join(
        [
            str(node.get("intent") or ""),
            str(node.get("title") or ""),
            " ".join(node.get("triggers") or []),
        ]
    ).lower()
    for token in _tokens(query):
        if token in haystack:
            score += 1.0
    score += _catalog.PRIORITY_SCORE.get(str(node.get("priority") or ""), 0.0)
    if node.get("priority"):
        reasons.append(f"priority:{node['priority']}")
    return score, reasons


def search_modules(
    query: str,
    page_role: str | None = None,
    dimension: str | None = None,
    top_k: int = 3,
    strict: bool = False,
    root: Path | None = None,
) -> dict[str, Any]:
    requirement = str(query or "").strip()
    dim = str(dimension or "").strip().lower() or None
    if dim and dim not in _catalog.DIMENSION_CATEGORIES:
        raise ValueError(f"unknown dimension: {dimension}; use one of {', '.join(_DIMENSIONS)}")
    if dim and "," in str(dimension):
        raise ValueError("one dimension per query")
    k = max(1, min(int(top_k), 8))
    root_path = root or _catalog.skill_root()
    scored: list[tuple[float, dict[str, Any], list[str]]] = []
    for node in _catalog.catalog_nodes(str(root_path)):
        total, reasons = _score_node(
            node,
            query=requirement,
            page_role=page_role,
            dimension=dim,
        )
        if total <= 0:
            continue
        scored.append((total, node, reasons))
    scored.sort(key=lambda item: (-item[0], item[1]["module_id"]))
    selected = scored[:k]
    match_mode = "lexical"
    if not selected:
        if strict or page_role or dim:
            match_mode = "empty"
            selected = []
        else:
            match_mode = "fallback"
            index = _catalog.node_index(root_path)
            for module_id in _catalog.default_gold_ids():
                node = index.get(module_id)
                if node is not None:
                    selected.append((0.0, node, ["fallback:default_gold_path"]))

    candidates = []
    for total, node, reasons in selected:
        why = "; ".join(reasons[:4]) if reasons else "lexical"
        candidates.append(
            {
                "module_id": node["module_id"],
                "title": node["title"],
                "excerpt": node["excerpt"],
                "why_matched": why,
            }
        )
    ids = [item["module_id"] for item in candidates]
    return {
        "query": requirement,
        "page_role": (page_role or "").strip() or None,
        "dimension": dim,
        "match_mode": match_mode,
        "candidates": candidates,
        "candidate_module_ids": ids,
        "loaded_module_ids": [],
        "top_score": round(selected[0][0], 2) if selected else 0.0,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Search slide-authoring capability-tree nodes. Prints candidates only."
    )
    parser.add_argument("--query", required=True, help="one page requirement")
    parser.add_argument("--page-role", default=None)
    parser.add_argument("--dimension", choices=_DIMENSIONS, default=None)
    parser.add_argument("--top-k", type=int, default=3)
    parser.add_argument(
        "--strict",
        action="store_true",
        help="do not fall back to default_gold_path when filters miss",
    )
    args = parser.parse_args(argv)
    payload = search_modules(
        query=args.query,
        page_role=args.page_role,
        dimension=args.dimension,
        top_k=args.top_k,
        strict=args.strict,
    )
    json.dump(payload, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
