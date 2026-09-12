from __future__ import annotations

from typing import Any, Iterable

ROUTE_LABELS = {
    "dynasty": "Build a Dynasty",
    "stepping_stone": "Stepping-Stone Career",
    "journeyman": "Journeyman",
    "youth_builder": "Youth Developer",
    "fallen_giant": "Fallen Giant Rebuild",
    "trophy_hunter": "Trophy Hunter",
    "realistic_climber": "Realistic Career Climb",
}

LEVEL_ORDER = {
    "semi_pro": 1,
    "lower_league": 2,
    "second_tier": 3,
    "top_flight_lower": 4,
    "top_flight_mid": 5,
    "continental_challenger": 6,
    "title_challenger": 7,
    "elite": 8,
}


def _num(value: Any) -> float | None:
    try:
        return float(value) if value is not None else None
    except (TypeError, ValueError):
        return None


def _level_rank(level: str | None) -> int | None:
    return LEVEL_ORDER.get(level or "")


def _confidence(values: Iterable[Any]) -> str:
    vals = list(values)
    known = sum(v not in (None, "", [], {}) for v in vals)
    ratio = known / max(1, len(vals))
    if ratio >= 0.8:
        return "high"
    if ratio >= 0.5:
        return "medium"
    return "low"


def _achievement_score(context: dict[str, Any]) -> float:
    achievements = context.get("achievements") or []
    score = 0.0
    weights = {
        "promotion": 1.5,
        "league_title": 2.5,
        "domestic_cup": 2.0,
        "continental_qualification": 1.5,
        "continental_trophy": 3.0,
        "survival": 0.8,
        "overachievement": 1.2,
    }
    for item in achievements:
        if isinstance(item, str):
            score += weights.get(item, 0.5)
        elif isinstance(item, dict):
            score += weights.get(str(item.get("type")), 0.5)
    return score


def _project_completion(context: dict[str, Any], prefs: dict[str, Any]) -> dict[str, Any]:
    tenure = _num(context.get("tenure_seasons")) or 0
    achievement_score = _achievement_score(context)
    board = context.get("board_status")
    squad = context.get("squad_outlook") or {}
    squad_ready = squad.get("core_age_balance") in {"healthy", "mature"}
    youth_ready = squad.get("youth_pipeline") in {"strong", "excellent"}
    route = prefs.get("route", "realistic_climber")

    score = min(10.0, tenure * 1.1 + achievement_score)
    if board == "untouchable":
        score += 0.4
    if squad_ready:
        score += 0.5
    if route == "youth_builder" and youth_ready:
        score += 0.8
    score = round(min(10.0, score), 1)

    if score >= 7.5:
        stage = "project_mature"
    elif score >= 4.5:
        stage = "project_established"
    else:
        stage = "project_building"
    return {"score": score, "stage": stage}


def _readiness(context: dict[str, Any]) -> dict[str, Any]:
    current_level = _level_rank(context.get("club_level"))
    rep = _num(context.get("manager_reputation"))
    badges = context.get("coaching_badge_level")
    achievement_score = _achievement_score(context)
    tenure = _num(context.get("tenure_seasons")) or 0

    points = achievement_score + min(2.5, tenure * 0.6)
    if rep is not None:
        points += min(3.0, rep / 2500.0)
    if badges in {"continental_pro", "continental_a"}:
        points += 1.0
    if current_level is not None:
        points += current_level * 0.35

    if points >= 8.5:
        label = "ready_for_major_step"
    elif points >= 5.5:
        label = "ready_for_step_up"
    elif points >= 3.0:
        label = "credible_for_peer_move"
    else:
        label = "build_cv_first"
    return {"score": round(min(10.0, points), 1), "label": label}


def _next_level(context: dict[str, Any], readiness: dict[str, Any], prefs: dict[str, Any]) -> str | None:
    current = _level_rank(context.get("club_level"))
    if current is None:
        return None
    step = 0
    if readiness["label"] in {"ready_for_step_up", "ready_for_major_step"}:
        step = 1
    if readiness["label"] == "ready_for_major_step" and prefs.get("ambition") == "aggressive":
        step = 2
    target_rank = min(8, current + step)
    return next((k for k, v in LEVEL_ORDER.items() if v == target_rank), None)


def _stay_leave(context: dict[str, Any], prefs: dict[str, Any], completion: dict[str, Any], readiness: dict[str, Any]) -> dict[str, Any]:
    route = prefs.get("route", "realistic_climber")
    contract = _num(context.get("contract_years_remaining"))
    current_goal = context.get("current_project_goal")
    achieved_goal = bool(context.get("current_project_goal_achieved"))

    if route == "dynasty":
        recommendation = "stay"
        rationale = "Your chosen route prioritises building a long-term dynasty; move only for a clearly superior personal goal."
    elif completion["stage"] == "project_mature" and readiness["label"] in {"ready_for_step_up", "ready_for_major_step"}:
        recommendation = "explore_next_move"
        rationale = "The current project is mature and your CV supports testing the next level."
    elif achieved_goal and readiness["label"] != "build_cv_first":
        recommendation = "open_to_offers"
        rationale = "You have completed the main project objective and are credible for a new challenge."
    else:
        recommendation = "stay_and_build"
        rationale = "The current project still has meaningful milestones that can strengthen the next move."

    if contract is not None and contract < 1 and recommendation == "stay_and_build":
        recommendation = "decide_contract_or_move"
        rationale = "The project may still have value, but the contract horizon means a deliberate stay-or-go decision is due."

    return {"recommendation": recommendation, "rationale": rationale, "current_project_goal": current_goal}


def _milestones(context: dict[str, Any], prefs: dict[str, Any]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    goal = context.get("current_project_goal")
    if goal and not context.get("current_project_goal_achieved"):
        out.append({"priority": 1, "milestone": goal, "reason": "Finish the defining objective of the current job before judging the next move."})
    if not context.get("tactical_identity_established"):
        out.append({"priority": 2, "milestone": "Establish a clear tactical identity", "reason": "A repeatable identity makes career progression feel earned and gives future club choices a clearer fit."})
    if (context.get("squad_outlook") or {}).get("youth_pipeline") in {None, "weak"} and prefs.get("route") == "youth_builder":
        out.append({"priority": 2, "milestone": "Create a credible youth pathway", "reason": "Youth development is central to the selected career route."})
    if not out:
        out.append({"priority": 1, "milestone": "Set the next measurable achievement", "reason": "The current project lacks an unfinished milestone in the supplied data."})
    return out[:5]


def _finder_prompt(level: str | None, regions: list[str], identities: list[str], prefs: dict[str, Any]) -> str:
    bits = []
    if level:
        bits.append(f"a {level.replace('_', ' ')} club")
    if regions:
        bits.append("in " + ", ".join(regions))
    if identities:
        bits.append("with " + ", ".join(identities) + " characteristics")
    route = ROUTE_LABELS.get(prefs.get("route", "realistic_climber"), "Realistic Career Climb")
    core = " ".join(bits) if bits else "a realistic next club"
    return f"Find {core} that fits a {route} career path and represents a credible next step rather than an arbitrary jump."


def _club_finder_brief(prefs: dict[str, Any], next_level: str | None) -> dict[str, Any]:
    regions = prefs.get("preferred_regions") or []
    identities = prefs.get("club_identities") or []
    return {
        "target_level": next_level,
        "preferred_regions": regions,
        "avoid_regions": prefs.get("avoid_regions") or [],
        "club_identities": identities,
        "minimum_youth_focus": prefs.get("minimum_youth_focus"),
        "competition_preference": prefs.get("competition_preference"),
        "job_security_preference": prefs.get("job_security_preference", "balanced"),
        "search_prompt": _finder_prompt(next_level, regions, identities, prefs),
    }


def build_career_plan(payload: dict[str, Any]) -> dict[str, Any]:
    context = payload.get("current_context") or {}
    prefs = payload.get("preferences") or {}
    completion = _project_completion(context, prefs)
    readiness = _readiness(context)
    target_level = _next_level(context, readiness, prefs)

    known_for_confidence = [
        context.get("club_level"), context.get("tenure_seasons"), context.get("achievements"),
        context.get("manager_reputation"), context.get("current_project_goal"), prefs.get("route"),
    ]

    return {
        "schema_version": "fmcompanion.career-plan.v1",
        "manager": payload.get("manager") or {},
        "current_context": context,
        "preferences": prefs,
        "career_route": ROUTE_LABELS.get(prefs.get("route", "realistic_climber"), "Realistic Career Climb"),
        "project_completion": completion,
        "manager_readiness": readiness,
        "stay_or_leave": _stay_leave(context, prefs, completion, readiness),
        "current_job_milestones": _milestones(context, prefs),
        "next_move_profile": {
            "target_club_level": target_level,
            "max_level_jump": 2 if prefs.get("ambition") == "aggressive" else 1,
            "must_haves": prefs.get("next_club_must_haves") or [],
            "avoid": prefs.get("next_club_avoid") or [],
        },
        "club_finder_brief": _club_finder_brief(prefs, target_level),
        "long_term_path": {
            "destination_level": prefs.get("long_term_destination_level", "elite"),
            "destination_regions": prefs.get("long_term_regions") or prefs.get("preferred_regions") or [],
            "career_identity": ROUTE_LABELS.get(prefs.get("route", "realistic_climber"), "Realistic Career Climb"),
        },
        "confidence": _confidence(known_for_confidence),
        "confidence_notes": [
            "Career Planner only uses supplied/decoded facts and explicit user preferences.",
            "Missing reputation, history, finances or club context stays unknown rather than being guessed.",
            "Club Finder results should be ranked against this brief, not invented inside Career Planner.",
        ],
    }


def rank_club_candidates(plan: dict[str, Any], clubs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    brief = plan.get("club_finder_brief") or {}
    target = _level_rank(brief.get("target_level"))
    preferred_regions = set(brief.get("preferred_regions") or [])
    avoid_regions = set(brief.get("avoid_regions") or [])
    identities = set(brief.get("club_identities") or [])

    ranked = []
    for club in clubs:
        score = 5.0
        reasons = []
        level = _level_rank(club.get("club_level"))
        if target is not None and level is not None:
            gap = abs(target - level)
            score += max(-2.0, 2.2 - gap * 1.1)
            if gap == 0:
                reasons.append("matches target career level")
        region = club.get("region")
        if region in preferred_regions:
            score += 1.0
            reasons.append("preferred region")
        if region in avoid_regions:
            score -= 3.0
            reasons.append("region is on avoid list")
        overlap = identities & set(club.get("identities") or [])
        if overlap:
            score += min(1.5, 0.5 * len(overlap))
            reasons.append("identity fit: " + ", ".join(sorted(overlap)))
        if club.get("is_current_club"):
            score -= 5.0
        ranked.append({**club, "career_fit_score": round(max(0.0, min(10.0, score)), 1), "career_fit_reasons": reasons})
    return sorted(ranked, key=lambda x: x["career_fit_score"], reverse=True)
