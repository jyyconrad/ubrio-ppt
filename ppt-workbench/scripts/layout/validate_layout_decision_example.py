#!/usr/bin/env python3
"""校验 layout-decision example；脚本不决定构图，只复用生产合同验证声明。"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

BACKEND_ROOT = Path(__file__).resolve().parents[5]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

def validate_examples(path: Path) -> dict[str, Any]:
    from app.contexts.rendering.geometry.layout_decision import validate_layout_decision

    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("example 顶层必须是对象")
    results: dict[str, Any] = {}
    for name, decision in raw.items():
        if not isinstance(decision, dict):
            raise ValueError(f"{name} 必须是对象")
        layout_id = decision.get("layout_id")
        results[name] = validate_layout_decision(
            decision,
            recommended_layout={"layout_id": layout_id} if layout_id else None,
            candidate_structures=[{"layout_id": layout_id}] if layout_id else [],
            source_contents="<svg />",
        )
    return results


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("example", type=Path)
    args = parser.parse_args()
    results = validate_examples(args.example)
    print(json.dumps(results, ensure_ascii=False, indent=2))
    return 0 if all(result.get("ok") for result in results.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
