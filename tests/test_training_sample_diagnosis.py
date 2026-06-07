from after_effects_pipeline.training_sample_diagnosis import (
    build_training_sample_diagnosis,
    render_training_sample_diagnosis_markdown,
)


def test_training_sample_diagnosis_prioritizes_gap_targets_and_overlap_watches():
    payload = build_training_sample_diagnosis(
        render_analysis={
            "cases": [
                {
                    "case_id": "ready_a",
                    "analysis": {"active_frame_ratio": 0.8, "motion_timeline": {"motion_profile": "steady"}},
                },
                {
                    "case_id": "ready_b",
                    "analysis": {"active_frame_ratio": 0.7, "motion_timeline": {"motion_profile": "steady"}},
                },
            ]
        },
        queue={
            "items": [
                {"case_id": "ready_a", "decision": "promote_rendered", "train_ready": True},
                {"case_id": "ready_b", "decision": "promote_rendered", "train_ready": True},
                {"case_id": "finance_market_reel", "decision": "render_missing", "train_ready": False},
            ]
        },
        render_overlap={
            "potential_overlaps": [
                {"a": "ready_a", "b": "ready_b", "score": 0.91, "shared_signals": ["motion_profile=steady"]}
            ]
        },
        animation_anatomy={
            "cases": [
                {"case_id": "ready_a", "archetype": "continuous_motion"},
                {"case_id": "ready_b", "archetype": "continuous_motion"},
            ],
            "train_ready_archetype_gaps": [
                {"archetype": "dense_continuous", "first_unlock_case": "lyric_waveform_poster"}
            ],
        },
        theme_motion_audit={
            "cases": [
                {"case_id": "ready_a", "themes": ["typography_title"], "aspect": "landscape"},
                {"case_id": "ready_b", "themes": ["typography_title"], "aspect": "landscape"},
                {"case_id": "finance_market_reel", "themes": ["finance_market"], "aspect": "vertical"},
            ],
            "train_ready_theme_gaps": [
                {
                    "theme": "finance_market",
                    "first_planned_target": "finance_market_reel",
                    "candidate_cases": ["finance_market_reel"],
                }
            ],
        },
        quality_gap_matrix={
            "items": [
                {
                    "case_id": "finance_market_reel",
                    "priority": 155,
                    "action": "render_unlock_requirement",
                    "new_unlocks": ["theme:finance_market"],
                }
            ]
        },
    )

    assert payload["summary"]["train_ready_overlap_watch_count"] == 2
    assert payload["summary"]["theme_gap_count"] == 1
    assert payload["theme_gap_cases"] == [{"theme": "finance_market", "case_id": "finance_market_reel"}]
    assert payload["top_diagnoses"][0]["case_id"] == "finance_market_reel"
    assert "render_unlock_requirement" in payload["top_diagnoses"][0]["diagnoses"]


def test_training_sample_diagnosis_markdown_includes_distribution_and_gaps():
    payload = build_training_sample_diagnosis(
        render_analysis={"cases": []},
        queue={"items": [{"case_id": "missing", "decision": "render_missing", "train_ready": False}]},
        render_overlap={"potential_overlaps": []},
        animation_anatomy={"cases": [], "train_ready_archetype_gaps": []},
        theme_motion_audit={"cases": [], "train_ready_theme_gaps": []},
        quality_gap_matrix={"items": []},
    )

    markdown = render_training_sample_diagnosis_markdown(payload)

    assert "# Training Sample Diagnosis" in markdown
    assert "Train-Ready Distribution" in markdown
    assert "theme gaps: none" in markdown
