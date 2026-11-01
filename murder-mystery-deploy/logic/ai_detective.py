"""
AI Detective: the computer plays the detective while the player feeds it hints.

The AI keeps a set of *possible worlds* (who, where, what). It starts by
reading only the first clue of the case, then

  * every clue it is shown removes impossible worlds (classic model
    elimination over the propositional clue set), and
  * every hint the player types adds an extra constraint parsed by
    :mod:`logic.nlu` (for example "Ravi is innocent" removes every world in
    which Ravi is the killer).

The remaining worlds are turned into a ranked guess with a confidence score,
so the player can see the computer reason instead of just announcing an answer.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional

from data import CATEGORIES
from logic.solvers import BruteForceSolver

CAT_INDEX = {"WHO": 0, "WHERE": 1, "WHAT": 2}
SIGN_LABEL = {"exclude": "ruled out", "confirm": "locked in"}


@dataclass
class Guess:
    total_worlds: int
    best: Optional[Tuple[str, str, str]]
    who: Tuple[str, int, float]
    where: Tuple[str, int, float]
    what: Tuple[str, int, float]
    ranking: List[Tuple[str, int, float]] = field(default_factory=list)

    @property
    def confidence(self) -> float:
        return self.who[2]


class AIDetective:
    """Model-elimination detective with a visible line of reasoning."""

    def __init__(self, clues, revealed: int = 1):
        self.clues = list(clues)
        self.revealed = max(1, min(revealed, len(self.clues))) if self.clues else 0
        self.hints: List[Dict[str, str]] = []
        self._solver = BruteForceSolver(CATEGORIES)

    # ------------------------------------------------------------ evidence
    def visible_clues(self):
        return self.clues[: self.revealed]

    def hidden_count(self) -> int:
        return max(0, len(self.clues) - self.revealed)

    def reveal_next(self) -> bool:
        if self.revealed < len(self.clues):
            self.revealed += 1
            return True
        return False

    def base_worlds(self) -> List[Tuple[str, str, str]]:
        return self._solver.solve(self.visible_clues()).solutions

    def worlds(self) -> List[Tuple[str, str, str]]:
        worlds = self.base_worlds()
        for h in self.hints:
            idx = CAT_INDEX[h["category"]]
            if h["sign"] == "exclude":
                worlds = [w for w in worlds if w[idx] != h["value"]]
            else:
                worlds = [w for w in worlds if w[idx] == h["value"]]
        return worlds

    # --------------------------------------------------------------- hints
    def _would_be_empty(self, hints: List[Dict[str, str]]) -> bool:
        worlds = self.base_worlds()
        for h in hints:
            idx = CAT_INDEX[h["category"]]
            if h["sign"] == "exclude":
                worlds = [w for w in worlds if w[idx] != h["value"]]
            else:
                worlds = [w for w in worlds if w[idx] == h["value"]]
            if not worlds:
                return True
        return not worlds

    def add_hint(self, effects, raw: str) -> Tuple[bool, List[Tuple[str, str, str]], str]:
        """Apply parsed effects. Returns (accepted, applied_effects, message)."""
        clean = []
        for sign, cat, item in effects:
            if any(h["sign"] == sign and h["category"] == cat and h["value"] == item for h in self.hints):
                continue
            clean.append((sign, cat, item))

        if not clean:
            return False, [], "I already knew that. Try a different hint."

        proposed = list(self.hints) + [
            {"sign": s, "category": c, "value": i, "text": raw} for s, c, i in clean
        ]
        if self._would_be_empty(proposed):
            return (
                False,
                [],
                "That hint contradicts the evidence I already have, so I am ignoring it. "
                "Feed me a different observation.",
            )

        self.hints = proposed
        return True, clean, "Hint accepted."

    def reset_hints(self) -> None:
        self.hints = []

    # ------------------------------------------------------------- guessing
    def _marginal(self, cat: str):
        worlds = self.worlds()
        n = max(1, len(worlds))
        idx = CAT_INDEX[cat]
        counts: Dict[str, int] = {}
        for w in worlds:
            counts[w[idx]] = counts.get(w[idx], 0) + 1
        ranked = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
        if not ranked:
            return ("?", 0, 0.0), []
        best = (ranked[0][0], ranked[0][1], ranked[0][1] / n)
        return best, [(name, c, c / n) for name, c in ranked]

    def guess(self) -> Guess:
        worlds = self.worlds()
        who, who_rank = self._marginal("WHO")
        where, _ = self._marginal("WHERE")
        what, _ = self._marginal("WHAT")

        best = None
        if worlds:
            # most frequent full world, deterministic tie-break
            counts: Dict[Tuple[str, str, str], int] = {}
            for w in worlds:
                counts[w] = counts.get(w, 0) + 1
            best = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))[0][0]

        return Guess(
            total_worlds=len(worlds),
            best=best,
            who=who,
            where=where,
            what=what,
            ranking=who_rank,
        )

    # --------------------------------------------------------------- status
    def status_line(self) -> str:
        g = self.guess()
        read = self.revealed
        total = len(self.clues)
        return (
            f"I have read **{read} of {total}** clues and hold **{g.total_worlds}** "
            f"possible versions of the crime. My confidence in **{g.who[0]}** is "
            f"**{g.who[2]*100:.0f}%**."
        )
