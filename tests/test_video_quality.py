from after_effects_pipeline.video_quality import score_render_quality


def test_score_render_quality_prioritizes_sparse_motion():
    quality = score_render_quality(_analysis("sparse", 0.8), [])

    assert quality["priority"] == "review"
    assert "sparse motion profile" in quality["reasons"]
    assert quality["score"] < 0.7


def test_score_render_quality_marks_actionable_warning_fix():
    quality = score_render_quality(_analysis("steady", 0.0), ["low_motion"])

    assert quality["priority"] == "fix"
    assert "warning: low_motion" in quality["reasons"]


def test_score_render_quality_passes_healthy_motion():
    quality = score_render_quality(_analysis("steady", 0.1), [])

    assert quality["priority"] == "pass"
    assert quality["score"] > 0.9


def _analysis(profile, stall_ratio):
    return {
        "blank_frame_ratio": 0.0,
        "foreground_ratio": {"p95": 0.2},
        "largest_component_ratio": {"p95": 0.1},
        "motion_timeline": {
            "motion_profile": profile,
            "longest_stall_ratio": stall_ratio,
        },
    }
