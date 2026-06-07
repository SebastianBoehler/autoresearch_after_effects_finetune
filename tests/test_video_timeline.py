from after_effects_pipeline.video_timeline import build_frame_timeline, build_motion_timeline


def test_motion_timeline_reports_longest_stall_source_frames():
    reports = [_report(0.0), _report(0.02), _report(0.0), _report(0.0), _report(0.03)]

    timeline = build_motion_timeline(reports, frame_step=3)

    assert timeline["motion_profile"] == "stalled_sections"
    assert timeline["first_active_source_frame"] == 3
    assert timeline["last_active_source_frame"] == 12
    assert timeline["longest_stall"] == {
        "sample_start": 2,
        "sample_end": 3,
        "source_start_frame": 6,
        "source_end_frame": 9,
        "length": 2,
    }


def test_motion_timeline_labels_steady_motion():
    timeline = build_motion_timeline(
        [_report(0.0), _report(0.03), _report(0.02), _report(0.04)],
        frame_step=3,
    )

    assert timeline["motion_profile"] == "steady"
    assert timeline["longest_stall_ratio"] == 0.0


def test_frame_timeline_reports_sample_phases_and_peaks():
    timeline = build_frame_timeline(
        [
            _report(0.0, foreground_ratio=0.01, contrast=0.01),
            _report(0.02, foreground_ratio=0.20),
            _report(0.01, foreground_ratio=0.10),
            _report(0.04, foreground_ratio=0.30),
        ],
        frame_step=3,
        peak_count=2,
    )

    assert timeline["sample_count"] == 4
    assert [sample["source_frame"] for sample in timeline["samples"]] == [0, 3, 6, 9]
    assert [sample["phase"] for sample in timeline["samples"]] == [
        "intro",
        "middle",
        "outro",
        "outro",
    ]
    assert timeline["samples"][0]["blank"] is True
    assert timeline["samples"][1]["active"] is True
    assert timeline["motion_peaks"][0] == {
        "source_frame": 9,
        "motion_area_ratio": 0.04,
        "phase": "outro",
    }
    assert timeline["foreground_peaks"][0]["source_frame"] == 9
    assert timeline["phase_summary"][2]["phase"] == "outro"
    assert timeline["phase_summary"][2]["active_count"] == 1
    assert timeline["phase_summary"][2]["peak_motion_source_frame"] == 9


def _report(motion_area_ratio, *, foreground_ratio=0.1, contrast=0.1):
    return {
        "motion_area_ratio": motion_area_ratio,
        "motion": motion_area_ratio,
        "foreground_ratio": foreground_ratio,
        "center_foreground_ratio": foreground_ratio / 2,
        "component_count": 2,
        "largest_component_ratio": foreground_ratio / 3,
        "brightness": 0.5,
        "contrast": contrast,
        "saturation": 0.1,
    }
