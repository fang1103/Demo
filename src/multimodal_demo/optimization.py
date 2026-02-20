from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations


@dataclass(slots=True)
class Action:
    name: str
    cost: float
    impact_score: float
    phase: str


def prioritize_actions(actions: list[Action], budget: float, strategy: str = "greedy") -> list[Action]:
    if strategy == "exact":
        return _exact_select(actions, budget)
    return _greedy_select(actions, budget)


def _greedy_select(actions: list[Action], budget: float) -> list[Action]:
    remaining = budget
    selected: list[Action] = []
    ranked = sorted(actions, key=lambda x: (x.impact_score / x.cost) if x.cost else 0.0, reverse=True)

    for action in ranked:
        if action.cost <= remaining:
            selected.append(action)
            remaining -= action.cost
    return selected


def _exact_select(actions: list[Action], budget: float) -> list[Action]:
    best_combo: tuple[Action, ...] = ()
    best_impact = -1.0

    for r in range(1, len(actions) + 1):
        for combo in combinations(actions, r):
            total_cost = sum(a.cost for a in combo)
            if total_cost > budget:
                continue
            total_impact = sum(a.impact_score for a in combo)
            if total_impact > best_impact:
                best_impact = total_impact
                best_combo = combo

    return list(best_combo)
