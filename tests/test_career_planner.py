from fmcompanion_career_planner import build_career_plan, rank_club_candidates


def base_payload():
    return {
        "manager": {"name": "Test Manager"},
        "current_context": {
            "club_name": "Test FC",
            "club_level": "top_flight_mid",
            "tenure_seasons": 3,
            "manager_reputation": 5000,
            "coaching_badge_level": "continental_pro",
            "achievements": ["promotion", "continental_qualification"],
            "current_project_goal": "Qualify for Europe",
            "current_project_goal_achieved": True,
            "tactical_identity_established": True,
            "squad_outlook": {"core_age_balance": "healthy", "youth_pipeline": "strong"},
        },
        "preferences": {"route": "realistic_climber", "ambition": "balanced", "preferred_regions": ["England"], "club_identities": ["youth development"]},
    }


def test_plan_has_core_sections():
    plan = build_career_plan(base_payload())
    assert plan["schema_version"] == "fmcompanion.career-plan.v1"
    assert "stay_or_leave" in plan and "club_finder_brief" in plan


def test_mature_project_can_explore_move():
    plan = build_career_plan(base_payload())
    assert plan["stay_or_leave"]["recommendation"] in {"explore_next_move", "open_to_offers"}


def test_dynasty_biases_stay():
    p = base_payload(); p["preferences"]["route"] = "dynasty"
    plan = build_career_plan(p)
    assert plan["stay_or_leave"]["recommendation"] == "stay"


def test_next_level_is_not_arbitrary_jump():
    plan = build_career_plan(base_payload())
    assert plan["next_move_profile"]["target_club_level"] in {"top_flight_mid", "continental_challenger"}


def test_club_ranking_rewards_level_and_region_fit():
    plan = build_career_plan(base_payload())
    clubs = [
        {"club_name": "Fit FC", "club_level": plan["next_move_profile"]["target_club_level"], "region": "England", "identities": ["youth development"]},
        {"club_name": "Random FC", "club_level": "elite", "region": "Brazil", "identities": []},
    ]
    ranked = rank_club_candidates(plan, clubs)
    assert ranked[0]["club_name"] == "Fit FC"


def test_missing_data_does_not_crash_or_invent():
    plan = build_career_plan({"manager": {}, "current_context": {}, "preferences": {"route": "journeyman"}})
    assert plan["next_move_profile"]["target_club_level"] is None
    assert plan["confidence"] == "low"
