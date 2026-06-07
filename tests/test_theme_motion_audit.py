from after_effects_pipeline.theme_motion_audit import (
    build_theme_motion_audit,
    infer_themes,
    render_theme_motion_markdown,
)


def test_theme_motion_audit_finds_train_ready_theme_gap_and_planned_target():
    records = [
        {
            "case_id": "ready_title",
            "prompt": "Create a kinetic title opener",
            "tags": ["typography", "intro"],
            "expected": {"width": 1920, "height": 1080},
        },
        {
            "case_id": "sound_marker_sync_sting",
            "prompt": "Create an audio waveform marker sync animation",
            "tags": ["audio", "markers", "waveform", "motion-trails"],
            "expected": {"width": 1080, "height": 1920},
        },
    ]

    payload = build_theme_motion_audit(
        records,
        queue={
            "items": [
                {"case_id": "ready_title", "decision": "promote_rendered", "train_ready": True},
                {"case_id": "sound_marker_sync_sting", "decision": "render_missing", "train_ready": False},
            ]
        },
        animation_anatomy={
            "cases": [{"case_id": "ready_title", "archetype": "continuous_motion"}]
        },
        quality_gap_matrix={
            "items": [
                {
                    "case_id": "sound_marker_sync_sting",
                    "action": "render_unlock_requirement",
                    "decision": "render_missing",
                    "new_unlocks": ["motif:audio_visualizer"],
                }
            ]
        },
    )

    gap_by_theme = {gap["theme"]: gap for gap in payload["train_ready_theme_gaps"]}
    assert gap_by_theme["audio_music"]["first_planned_target"] == "sound_marker_sync_sting"
    assert gap_by_theme["path_shape_system"]["candidate_cases"] == ["sound_marker_sync_sting"]
    assert payload["summary"]["planned_gap_target_count"] == 1
    assert payload["train_ready_theme_motion_combos"][0]["archetype"] == "continuous_motion"
    assert "current render-unlock batch covers" in payload["recommendations"][-1]


def test_theme_motion_markdown_lists_gaps_and_recommendations():
    payload = build_theme_motion_audit(
        [
            {
                "case_id": "future_grid",
                "prompt": "Create a workflow grid builder",
                "tags": ["grid", "workflow", "layout-builder"],
                "expected": {"width": 1080, "height": 1080},
            }
        ],
        queue={"items": [{"case_id": "future_grid", "decision": "render_missing", "train_ready": False}]},
        animation_anatomy={"cases": []},
        quality_gap_matrix={"items": []},
    )

    markdown = render_theme_motion_markdown(payload)

    assert "# Theme Motion Audit" in markdown
    assert "workflow_tools" in markdown
    assert "add existing candidates to the render-unlock plan" in markdown


def test_infer_themes_uses_tags_prompt_and_template_names():
    record = {
        "case_id": "caption_kinetic_reel",
        "template": "caption_kinetic_reel.jsx",
        "prompt": "Create a social vertical caption reel",
        "tags": ["subtitles"],
    }

    assert infer_themes(record) == [
        "lower_third_caption",
        "social_vertical",
        "typography_title",
    ]
