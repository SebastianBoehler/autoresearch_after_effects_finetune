from after_effects_pipeline.training_curriculum import (
    build_training_curriculum,
    render_training_curriculum_markdown,
)


def test_training_curriculum_downweights_common_overlap_cases_and_keeps_rare_anchors():
    payload = build_training_curriculum(
        diagnosis={
            "cases": [
                _ready("a", ["dashboard_data"], "continuous_motion", "steady", 2),
                _ready("b", ["dashboard_data"], "continuous_motion", "steady", 0),
                _ready("c", ["dashboard_data", "sports_replay"], "varied_sequence", "varied", 0),
                _ready("d", ["dashboard_data"], "continuous_motion", "steady", 1),
                _planned("finance_market_reel", ["theme:finance_market"], 150),
            ]
        },
        split_safety={"ok": True},
        quality_gate={
            "summary": {
                "technical_trainable_subset": True,
                "high_quality_trainable_subset": True,
                "full_dataset_ready": False,
            }
        },
    )

    weights = {item["case_id"]: item["weight"] for item in payload["sampling_weights"]}
    assert weights["a"] < weights["c"]
    assert payload["summary"]["anchor_count"] == 2
    assert payload["summary"]["overlap_watch_count"] == 2
    assert payload["post_render_promotions"][0]["case_id"] == "finance_market_reel"
    assert payload["post_render_promotions"][0]["unlock_types"] == ["theme"]


def test_training_curriculum_markdown_lists_weights_and_promotions():
    payload = build_training_curriculum(
        diagnosis={"cases": [_ready("anchor", ["audio_music"], "varied_sequence", "varied", 0)]},
        split_safety={"summary": {"ok": True}},
        quality_gate={"summary": {"technical_trainable_subset": True}},
    )

    markdown = render_training_curriculum_markdown(payload)

    assert "# Training Curriculum" in markdown
    assert "anchor" in markdown
    assert "Current Sampling Weights" in markdown
    assert payload["summary"]["split_safe"] is True


def _ready(case_id, themes, archetype, motion_profile, overlaps):
    return {
        "case_id": case_id,
        "train_ready": True,
        "themes": themes,
        "archetype": archetype,
        "motion_profile": motion_profile,
        "aspect": "landscape",
        "overlap_pair_count": overlaps,
        "max_overlap_score": 0.9 if overlaps else 0.0,
    }


def _planned(case_id, unlocks, priority):
    return {
        "case_id": case_id,
        "train_ready": False,
        "new_unlocks": unlocks,
        "priority": priority,
        "decision": "render_missing",
    }
