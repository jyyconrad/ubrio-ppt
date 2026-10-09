"""Page-spec quality gates from session-884 review.

Each page-level module exposes:

    def check(spec: dict) -> GateResult

Deck-level modules also expose:

    def check_deck(specs: list[dict]) -> GateResult

`GateResult.missing` blocks `quality_status=ready`.
Do not import `build_gold_svg_page` from these modules (keeps them unit-testable).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class GateResult:
    missing: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    details: dict[str, Any] = field(default_factory=dict)

    def blocked(self) -> bool:
        return bool(self.missing)


COVER_ROLES = frozenset({"cover", "section_divider", "closing", "end"})
CONTENT_ROLES = frozenset({"content", "summary", "decision", "evidence"})
