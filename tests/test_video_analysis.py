from after_effects_pipeline.video_analysis import render_markdown_report
from after_effects_pipeline import video_metrics


def test_percentile_uses_nearest_rank():
    assert video_metrics.percentile([0.0, 0.5, 1.0], 0.95) == 1.0


def test_measure_frame_detects_motion_and_foreground():
    previous = bytes([0, 0, 0] * 16)
    current = bytes([0, 0, 0] * 8 + [255, 255, 255] * 8)

    result = video_metrics.measure_frame(current, previous, 4, 4)

    assert result["motion"] > 0.0
    assert result["motion_area_ratio"] > 0.0
    assert result["contrast"] > 0.0
    assert result["foreground_ratio"] > 0.0
    assert result["component_count"] > 0.0


def test_aggregate_reports_active_frame_ratio_excludes_first_frame():
    reports = [
        _report(0.0, 0.1, 0.1),
        _report(0.02, 0.1, 0.1),
        _report(0.0, 0.1, 0.1),
    ]

    analysis = video_metrics.aggregate_frame_reports(reports)

    assert analysis["active_frame_ratio"] == 0.5


def test_quality_notes_describe_motion_and_layout():
    analysis = {
        "blank_frame_ratio": 0.05,
        "active_frame_ratio": 0.75,
        "motion_area_ratio": {"p95": 0.08},
        "foreground_ratio": {"p95": 0.2},
        "center_foreground_ratio": {"p95": 0.7},
    }

    notes = video_metrics.quality_notes_for_analysis(analysis)

    assert "steady_motion" in notes
    assert "center_weighted_layout" in notes
    assert "intentional_intro_blanks" in notes


def test_quality_notes_include_component_layout_clues():
    analysis = {
        "blank_frame_ratio": 0.0,
        "active_frame_ratio": 0.4,
        "motion_area_ratio": {"p95": 0.04},
        "foreground_ratio": {"p95": 0.3},
        "center_foreground_ratio": {"p95": 0.3},
        "largest_component_ratio": {"p95": 0.4},
        "component_count": {"p95": 4},
        "edge_touch_component_ratio": {"p95": 0.7},
    }

    notes = video_metrics.quality_notes_for_analysis(analysis)

    assert "merged_foreground_regions" in notes
    assert "edge_touching_foreground" in notes


def test_warning_for_static_low_contrast_render():
    analysis = {
        "blank_frame_ratio": 0.0,
        "motion": {"mean": 0.0, "p95": 0.0},
        "motion_area_ratio": {"p95": 0.0},
        "foreground_ratio": {"p95": 0.1},
        "center_foreground_ratio": {"p95": 0.1},
        "edge_density": {"p95": 0.0},
        "contrast": {"mean": 0.01},
        "saturation": {"mean": 0.01},
    }

    warnings = video_metrics.warnings_for_analysis(analysis)

    assert "low_motion" in warnings
    assert "low_contrast" in warnings
    assert "low_color_variety" in warnings


def test_centered_subject_is_not_crowding_by_itself():
    analysis = {
        "blank_frame_ratio": 0.0,
        "motion": {"mean": 0.004, "p95": 0.01},
        "motion_area_ratio": {"p95": 0.04},
        "foreground_ratio": {"p95": 0.18},
        "center_foreground_ratio": {"p95": 0.82},
        "edge_density": {"p95": 0.02},
        "contrast": {"mean": 0.12},
        "saturation": {"mean": 0.08},
    }

    assert "center_crowding" not in video_metrics.warnings_for_analysis(analysis)


def test_dense_center_foreground_is_crowding():
    analysis = {
        "blank_frame_ratio": 0.0,
        "motion": {"mean": 0.004, "p95": 0.01},
        "motion_area_ratio": {"p95": 0.04},
        "foreground_ratio": {"p95": 0.32},
        "center_foreground_ratio": {"p95": 0.82},
        "edge_density": {"p95": 0.02},
        "contrast": {"mean": 0.12},
        "saturation": {"mean": 0.08},
    }

    assert "center_crowding" in video_metrics.warnings_for_analysis(analysis)


def test_render_markdown_report_includes_frame_timeline_highlights():
    payload = {
        "frame_step": 3,
        "sample_width": 320,
        "summary": {
            "case_count": 1,
            "mean_motion": 0.02,
            "mean_active_motion_p95": 0.05,
            "mean_active_frame_ratio": 0.5,
            "mean_foreground_p95": 0.3,
            "mean_largest_component_p95": 0.1,
            "mean_component_count_p95": 2.0,
            "cases_with_warnings": 0,
        },
        "cases": [
            {
                "case_id": "sample_case",
                "notes": [],
                "warnings": [],
                "render_quality": {"score": 0.9, "priority": "promote"},
                "analysis": {
                    "sampled_frames": 4,
                    "motion": {"mean": 0.02},
                    "motion_area_ratio": {"p95": 0.2},
                    "active_frame_ratio": 0.5,
                    "foreground_ratio": {"p95": 0.3},
                    "center_foreground_ratio": {"p95": 0.2},
                    "largest_component_ratio": {"p95": 0.1},
                    "component_count": {"p95": 2},
                    "blank_frame_ratio": 0.0,
                    "motion_timeline": {"motion_profile": "varied", "longest_stall_ratio": 0.2},
                    "frame_timeline": {
                        "phase_summary": [
                            {
                                "phase": "intro",
                                "sample_count": 2,
                                "active_count": 1,
                                "blank_count": 0,
                                "mean_motion_area_ratio": 0.01,
                                "mean_foreground_ratio": 0.1,
                            }
                        ],
                        "motion_peaks": [
                            {
                                "source_frame": 3,
                                "motion_area_ratio": 0.2,
                                "phase": "intro",
                            }
                        ],
                        "foreground_peaks": [
                            {
                                "source_frame": 6,
                                "foreground_ratio": 0.3,
                                "phase": "middle",
                            }
                        ],
                    },
                },
            }
        ],
    }

    report = render_markdown_report(payload)

    assert "## Timeline Highlights" in report
    assert "| sample_case | intro m=0.010 fg=0.100 a=1/2 b=0 |" in report
    assert "f3 0.200 intro" in report
    assert "f6 0.300 middle" in report


def _report(motion_area_ratio, foreground_ratio, center_foreground_ratio):
    return {
        "brightness": 0.5,
        "contrast": 0.1,
        "saturation": 0.1,
        "motion": 0.01,
        "motion_area_ratio": motion_area_ratio,
        "foreground_ratio": foreground_ratio,
        "center_foreground_ratio": center_foreground_ratio,
        "edge_density": 0.01,
        "component_count": 3.0,
        "largest_component_ratio": 0.05,
        "largest_component_share": 0.5,
        "edge_touch_component_ratio": 0.0,
    }
