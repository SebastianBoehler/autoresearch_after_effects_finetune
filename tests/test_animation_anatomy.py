from after_effects_pipeline.animation_anatomy import (
    build_animation_anatomy_audit,
    render_animation_anatomy_markdown,
)


def test_animation_anatomy_tracks_train_ready_archetype_gaps():
    payload = build_animation_anatomy_audit(
        {
            "cases": [
                _case("ready", "steady", {"intro": 0.9, "middle": 0.9, "outro": 0.9}, 0.8),
                _case("sparse", "sparse", {"intro": 0.5, "middle": 0.1, "outro": 0.0}, 0.16),
            ]
        },
        render_queue={
            "items": [
                {"case_id": "ready", "decision": "promote_rendered", "train_ready": True, "quality_score": 1.0},
                {"case_id": "sparse", "decision": "rerender_stale", "quality_priority": "review", "quality_score": 0.6},
            ]
        },
    )

    assert payload["summary"]["case_count"] == 2
    assert payload["summary"]["train_ready_count"] == 1
    assert payload["summary"]["train_ready_archetype_gap_count"] == 1
    assert payload["train_ready_archetype_gaps"][0]["first_unlock_case"] == "sparse"
    assert payload["cases"][1]["next_action"] == "rerender_then_review"


def test_animation_anatomy_classifies_late_reveal_and_markdown():
    payload = build_animation_anatomy_audit(
        {
            "cases": [
                _case(
                    "late",
                    "varied",
                    {"intro": 0.1, "middle": 0.4, "outro": 0.8},
                    0.5,
                    dominant="outro",
                )
            ]
        },
        render_queue={"items": [{"case_id": "late", "decision": "render_missing"}]},
    )

    assert payload["cases"][0]["archetype"] == "late_reveal"
    markdown = render_animation_anatomy_markdown(payload)
    assert "# Animation Anatomy Audit" in markdown
    assert "late_reveal" in markdown
    assert "intro:low/middle:mid/outro:high" in markdown


def _case(case_id, profile, phase_active, active_ratio, *, dominant="intro"):
    phase_motion = {phase: (0.08 if phase == dominant else 0.02) for phase in phase_active}
    return {
        "case_id": case_id,
        "analysis": {
            "active_frame_ratio": active_ratio,
            "foreground_ratio": {"p95": 0.3},
            "motion_area_ratio": {"p95": 0.05},
            "motion_timeline": {
                "motion_profile": profile,
                "longest_stall_ratio": 0.5 if profile == "sparse" else 0.1,
            },
            "frame_timeline": {
                "phase_summary": [
                    {
                        "phase": phase,
                        "sample_count": 10,
                        "active_count": int(ratio * 10),
                        "mean_motion_area_ratio": phase_motion[phase],
                    }
                    for phase, ratio in phase_active.items()
                ]
            },
        },
    }
