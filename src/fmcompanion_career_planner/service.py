from __future__ import annotations
from typing import Any
from .planner import build_career_plan, rank_club_candidates


def create_career_plan(*, manager: dict[str, Any], current_context: dict[str, Any], preferences: dict[str, Any], club_candidates: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    plan = build_career_plan({"manager": manager, "current_context": current_context, "preferences": preferences})
    if club_candidates is not None:
        plan["ranked_club_candidates"] = rank_club_candidates(plan, club_candidates)
    return plan
