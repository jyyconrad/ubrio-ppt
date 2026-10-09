#!/usr/bin/env python3
"""Search the built-in image library and stage images into a task directory.

Local stand-in for host image tools. Returns metadata only (no binary);
`--stage` copies the licensed file into the page directory so that
deck-framework.json / native-image-slot keep using local files.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

_ROOT = Path(__file__).resolve().parents[2]
IMG_ROOT = _ROOT / "assets" / "images"
INDEX_PATH = IMG_ROOT / "image-index.json"

_SPLIT_RE = re.compile(r"[\s,，;；/|]+")
_CJK_RE = re.compile(r"[\u4e00-\u9fff]{2,}")
_QUERY_ALIASES = (
    ("封面", "封面底板 城市 夜景 抽象"),
    ("底板", "封面底板 背景"),
    ("章节", "章节页底板"),
    ("会议", "会议 沟通 团队"),
    ("团队", "团队 会议"),
    ("握手", "合作 握手 签约"),
    ("签约", "合作 握手 签约"),
    ("合作", "合作 握手 签约"),
    ("办公", "办公 职场"),
    ("工厂", "工厂 制造 生产"),
    ("制造", "工厂 制造 生产"),
    ("物流", "物流 港口 供应链"),
    ("供应链", "物流 港口 供应链"),
    ("数据", "数据中心 服务器 科技"),
    ("机房", "数据中心 服务器"),
    ("山顶", "山峰 日出 里程碑"),
    ("日出", "山峰 日出 里程碑"),
    ("收官", "山峰 日出 里程碑"),
)


@dataclass(frozen=True)
class ImageSearchResult:
    ok: bool
    images: list[dict[str, Any]] = field(default_factory=list)
    categories: list[dict[str, Any]] = field(default_factory=list)
    message: str = ""


def load_index() -> list[dict[str, Any]]:
    if not INDEX_PATH.is_file():
        raise FileNotFoundError(f"缺少图片索引: {INDEX_PATH}")
    payload = json.loads(INDEX_PATH.read_text(encoding="utf-8"))
    images = payload.get("images")
    if not isinstance(images, list):
        raise ValueError("image-index.json 必须包含 images 数组。")
    return [img for img in images if isinstance(img, dict)]


def _tokenize(value: str) -> list[str]:
    raw = [item for item in _SPLIT_RE.split(str(value or "").strip().lower()) if item]
    blob = str(value or "")
    terms = list(raw)
    for match in _CJK_RE.findall(blob):
        if match.lower() not in terms:
            terms.append(match.lower())
        if len(match) >= 3:
            for i in range(len(match) - 1):
                gram = match[i: i + 2]
                if gram not in terms:
                    terms.append(gram)
    return terms


def _query_terms(query: str) -> list[str]:
    terms = _tokenize(query)
    blob = str(query or "").lower()
    for needle, extra in _QUERY_ALIASES:
        if needle in blob:
            terms.extend(_tokenize(extra))
    seen: set[str] = set()
    ordered = []
    for term in terms:
        if term not in seen:
            seen.add(term)
            ordered.append(term)
    return ordered


def _score(img: dict[str, Any], terms: list[str]) -> int:
    haystack_parts = [
        img.get("image_id"), img.get("title"), img.get("category"),
        img.get("category_label"), img.get("recommended_usage"),
        *(img.get("tags") if isinstance(img.get("tags"), list) else []),
    ]
    haystack = " ".join(str(p).lower() for p in haystack_parts if p)
    image_id = str(img.get("image_id") or "").lower()
    title = str(img.get("title") or "").lower()
    category = str(img.get("category") or "").lower()
    score = 0
    for term in terms:
        if term == image_id or term == category:
            score += 6
        elif term in title:
            score += 3
        elif term in haystack:
            score += 1
    return score


def search_images(
    *,
    query: str,
    category: str | None = None,
    limit: int = 6,
) -> ImageSearchResult:
    images = load_index()
    terms = _query_terms(query)
    requested = str(category or "").strip().lower()
    scored = []
    for img in images:
        if requested and str(img.get("category") or "").lower() != requested:
            continue
        score = _score(img, terms) if terms else 1
        if terms and score <= 0:
            continue
        scored.append((score, img))
    scored.sort(key=lambda item: (-item[0], str(item[1].get("image_id") or "")))
    cap = max(1, min(int(limit or 6), 20))
    picked = []
    for _score_value, img in scored[:cap]:
        picked.append({
            "image_id": img.get("image_id"),
            "title": img.get("title"),
            "category": img.get("category"),
            "category_label": img.get("category_label"),
            "tags": img.get("tags", []),
            "file": img.get("file"),
            "width": img.get("width"),
            "height": img.get("height"),
            "recommended_usage": img.get("recommended_usage"),
            "source": {
                "site": (img.get("source") or {}).get("site"),
                "license": (img.get("source") or {}).get("license"),
            },
        })
    return ImageSearchResult(ok=True, images=picked, message="ok")


def list_categories() -> ImageSearchResult:
    images = load_index()
    cats: dict[str, dict[str, Any]] = {}
    for img in images:
        cat = str(img.get("category") or "")
        entry = cats.setdefault(cat, {
            "category": cat,
            "label": img.get("category_label"),
            "count": 0,
            "usage": img.get("recommended_usage"),
        })
        entry["count"] += 1
    return ImageSearchResult(ok=True, categories=list(cats.values()), message="ok")


def stage_image(image_id: str, dest_dir: str, *, rename: str | None = None) -> dict[str, Any]:
    images = load_index()
    match = next((img for img in images if str(img.get("image_id")) == image_id), None)
    if match is None:
        raise ValueError(f"未找到图片: {image_id}")
    src = IMG_ROOT / str(match.get("file") or "")
    if not src.is_file():
        raise FileNotFoundError(f"图片文件缺失: {src}")
    dest_path = Path(dest_dir)
    dest_path.mkdir(parents=True, exist_ok=True)
    target = dest_path / (rename or src.name)
    if target.resolve() == src.resolve():
        raise ValueError("目标路径不能是技能内置图片库自身。")
    shutil.copyfile(src, target)
    source = match.get("source") or {}
    return {
        "ok": True,
        "image_id": image_id,
        "staged_path": str(target),
        "title": match.get("title"),
        "usage": match.get("recommended_usage"),
        "license": source.get("license"),
        "source_site": source.get("site"),
        "source_page": source.get("page"),
        "note": "通用场景图：不得冒充用户真实证据或截图；CC BY/CC BY-SA 对外交付时保留署名。",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Search built-in ppt-workbench image library; stage images into a task dir"
    )
    parser.add_argument("--query", help="search text (Chinese or English)")
    parser.add_argument("--category", help="category filter, e.g. cover-city")
    parser.add_argument("--list", action="store_true", help="list categories")
    parser.add_argument("--limit", type=int, default=6)
    parser.add_argument("--stage", help="image_id to copy into --dest")
    parser.add_argument("--dest", help="destination directory for --stage")
    parser.add_argument("--rename", help="optional new file name for --stage")
    args = parser.parse_args(argv)

    if args.stage:
        if not args.dest:
            parser.error("--stage requires --dest")
        try:
            payload = stage_image(args.stage, args.dest, rename=args.rename)
        except (ValueError, FileNotFoundError, OSError) as exc:
            json.dump({"ok": False, "error": str(exc)}, sys.stdout, ensure_ascii=False)
            sys.stdout.write("\n")
            return 2
        json.dump(payload, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")
        return 0

    if args.list:
        result = list_categories()
        json.dump({"ok": result.ok, "categories": result.categories},
                  sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")
        return 0

    if not args.query:
        parser.error("--query is required unless --list/--stage")
    result = search_images(query=args.query, category=args.category, limit=args.limit)
    json.dump({"ok": result.ok, "images": result.images, "message": result.message},
              sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
