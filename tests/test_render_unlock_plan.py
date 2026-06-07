from after_effects_pipeline.render_unlock_plan import (
    build_render_unlock_plan,
    render_render_unlock_plan_markdown,
)


def test_render_unlock_plan_combines_capability_motif_pack_and_progression_gaps():
    plan = build_render_unlock_plan(
        readiness_report={
            "coverage_gaps": {"synthetic_packs": ["synthetic-v9"]},
            "coverage_unlocks": [
                {"synthetic_pack": "synthetic-v9", "case_id": "grid", "priority_score": 120}
            ],
            "render_debt": [
                _debt("grid", ["grid_layout_builder"], 150),
                _debt("sound", ["audio_visualizer"], 120),
                _debt("stale", [], 90, decision="rerender_stale"),
            ],
        },
        capability_audit={
            "train_ready_gap_unlocks": [
                {"capability": "null_controls", "case_ids": ["grid", "sound"]},
                {"capability": "markers", "case_ids": ["sound"]},
            ]
        },
        inspiration_coverage={
            "train_ready_gaps": [
                {
                    "motif": "grid_layout_builder",
                    "first_unlock_case": "grid",
                    "render_missing_cases": ["grid"],
                    "rerender_stale_cases": [],
                },
                {
                    "motif": "audio_visualizer",
                    "first_unlock_case": "sound",
                    "render_missing_cases": ["sound"],
                    "rerender_stale_cases": [],
                },
            ]
        },
        render_progression={
            "cases": [{"case_id": "stale", "issues": ["inactive_outro_stall"]}]
        },
        source_pattern_audit={
            "train_ready_pattern_gaps": [
                {"pattern": "feature:dense_layer_system", "case_ids": ["stale"]}
            ]
        },
        animation_anatomy={
            "train_ready_archetype_gaps": [
                {"archetype": "middle_sparse_motion", "case_ids": ["stale"], "first_unlock_case": "stale"}
            ]
        },
        queue={
            "items": [
                {"case_id": "grid", "quality_priority": "pass"},
                {"case_id": "sound", "quality_priority": "pass"},
                {"case_id": "stale", "quality_priority": "review"},
            ]
        },
    )

    assert plan["summary"]["requirement_count"] == 7
    assert plan["summary"]["covered_requirement_count"] == 7
    assert plan["summary"]["progression_issue_target_count"] == 1
    assert [target["case_id"] for target in plan["greedy_unlock_sequence"]] == ["grid", "sound", "stale"]
    assert plan["greedy_unlock_sequence"][0]["new_unlocks"] == [
        "capability:null_controls",
        "motif:grid_layout_builder",
        "pack:synthetic-v9",
    ]
    assert "archetype:middle_sparse_motion" in plan["greedy_unlock_sequence"][2]["new_unlocks"]
    assert "Render Unlock Plan" in render_render_unlock_plan_markdown(plan)


def test_render_unlock_plan_skips_unknown_unlock_cases():
    plan = build_render_unlock_plan(
        readiness_report={"render_debt": [_debt("known", [], 20)]},
        capability_audit={
            "train_ready_gap_unlocks": [{"capability": "camera_3d", "case_ids": ["missing"]}]
        },
        inspiration_coverage={"train_ready_gaps": []},
        render_progression={"cases": []},
        queue={"items": []},
        source_pattern_audit={"train_ready_pattern_gaps": []},
        animation_anatomy={
            "train_ready_archetype_gaps": [
                {"archetype": "late_reveal", "case_ids": ["missing"], "first_unlock_case": "missing"}
            ]
        },
    )

    assert plan["summary"]["requirement_count"] == 2
    assert plan["summary"]["covered_requirement_count"] == 0
    assert plan["greedy_unlock_sequence"] == []


def test_render_unlock_plan_uses_theme_motion_gap_candidates():
    plan = build_render_unlock_plan(
        readiness_report={
            "render_debt": [
                _debt("finance_market_reel", [], 80),
                _debt("other", [], 20),
            ]
        },
        capability_audit={"train_ready_gap_unlocks": []},
        inspiration_coverage={"train_ready_gaps": []},
        render_progression={"cases": []},
        queue={"items": [{"case_id": "finance_market_reel", "quality_priority": "pass"}]},
        theme_motion_audit={
            "train_ready_theme_gaps": [
                {
                    "theme": "finance_market",
                    "first_planned_target": "",
                    "candidate_cases": ["finance_market_reel"],
                }
            ]
        },
    )

    assert plan["requirements"] == ["theme:finance_market"]
    assert plan["summary"]["covered_requirement_count"] == 1
    assert plan["greedy_unlock_sequence"][0]["case_id"] == "finance_market_reel"
    assert plan["greedy_unlock_sequence"][0]["theme_unlocks"] == ["finance_market"]


def _debt(case_id, motifs, score, decision="render_missing"):
    return {
        "case_id": case_id,
        "decision": decision,
        "priority_score": score,
        "motif_gap_unlocks": motifs,
        "coverage_reasons": [f"reason:{case_id}"],
        "source_repo_path": f"data/synthetic/templates/{case_id}.jsx",
    }
