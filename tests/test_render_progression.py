from after_effects_pipeline.render_progression import (
    build_render_progression_audit,
    render_progression_markdown,
)


def test_render_progression_flags_flat_full_frame_outro_stall():
    payload = build_render_progression_audit(
        {
            "cases": [
                _case(
                    "flat_transition",
                    foreground=0.62,
                    active=0.35,
                    stall=0.48,
                    profile="compressed_motion_window",
                    phase_active={"intro": 0.4, "middle": 0.7, "outro": 0.0},
                )
            ]
        },
        render_queue={"items": [{"case_id": "flat_transition", "decision": "rerender_stale"}]},
    )

    case = payload["cases"][0]
    assert case["issues"] == ["full_frame_low_progression", "inactive_outro_stall"]
    assert payload["summary"]["cases_with_issues"] == 1


def test_render_progression_does_not_flag_steady_visualizer_texture():
    payload = build_render_progression_audit(
        {
            "cases": [
                _case(
                    "steady_visualizer",
                    foreground=0.58,
                    active=1.0,
                    stall=0.0,
                    profile="steady",
                    phase_active={"intro": 1.0, "middle": 1.0, "outro": 1.0},
                )
            ]
        },
        render_queue={
            "items": [
                {
                    "case_id": "steady_visualizer",
                    "decision": "promote_rendered",
                    "train_ready": True,
                }
            ]
        },
    )

    assert payload["cases"][0]["issues"] == []
    assert payload["summary"]["train_ready_issue_count"] == 0


def test_render_progression_markdown_lists_issues():
    payload = build_render_progression_audit(
        {
            "cases": [
                _case(
                    "sparse_case",
                    foreground=0.2,
                    active=0.1,
                    stall=0.7,
                    profile="sparse",
                    phase_active={"intro": 0.3, "middle": 0.0, "outro": 0.0},
                )
            ]
        }
    )

    markdown = render_progression_markdown(payload)

    assert "# Render Progression Audit" in markdown
    assert "sparse_progression" in markdown


def _case(case_id, *, foreground, active, stall, profile, phase_active):
    phases = [
        {
            "phase": phase,
            "sample_count": 10,
            "active_count": int(ratio * 10),
            "mean_foreground_ratio": foreground,
            "mean_motion_area_ratio": active * 0.03,
        }
        for phase, ratio in phase_active.items()
    ]
    return {
        "case_id": case_id,
        "analysis": {
            "active_frame_ratio": active,
            "foreground_ratio": {"p95": foreground},
            "center_foreground_ratio": {"p95": foreground},
            "motion_timeline": {
                "motion_profile": profile,
                "longest_stall_ratio": stall,
            },
            "frame_timeline": {
                "samples": [
                    {
                        "foreground_ratio": foreground,
                        "center_foreground_ratio": foreground,
                        "component_count": 20,
                        "saturation": 0.12,
                    }
                ],
                "phase_summary": phases,
            },
        },
    }
