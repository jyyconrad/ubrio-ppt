"""Check a deck of page_spec JSON files for homology and rhythm."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_HOME = Path(__file__).resolve().parent
if str(_HOME) not in sys.path:
    sys.path.insert(0, str(_HOME))

from gates.deck_consistency import check_deck  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Deck-level ppt-workbench consistency gate.")
    parser.add_argument("specs", nargs="+", type=Path, help="page_spec.json files in page order")
    args = parser.parse_args()
    specs = []
    for path in args.specs:
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise SystemExit(f"{path} must contain a JSON object")
        specs.append(data)
    result = check_deck(specs)
    print(
        json.dumps(
            {
                "ok": not result.missing,
                "missing": result.missing,
                "warnings": result.warnings,
                "details": result.details,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    raise SystemExit(0 if not result.missing else 2)


if __name__ == "__main__":
    main()
