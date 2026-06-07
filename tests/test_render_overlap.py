from after_effects_pipeline.render_overlap import (
    build_render_overlap_audit,
    render_overlap_markdown,
)


def test_render_overlap_finds_similar_metric_pairs():
    payload = build_render_overlap_audit(
        {
            "cases": [
                _case("a", motion=0.05, foreground=0.25, profile="steady"),
                _case("b", motion=0.052, foreground=0.26, profile="steady"),
                _case("c", motion=0.13, foreground=0.05, profile="varied"),
            ]
        },
        threshold=0.86,
    )

    pairs = {(item["a"], item["b"]) for item in payload["potential_overlaps"]}
    assert ("a", "b") in pairs
    assert ("a", "c") not in pairs


def test_render_overlap_marks_same_split_pairs():
    payload = build_render_overlap_audit(
        {"cases": [_case("a", 0.05, 0.25), _case("b", 0.052, 0.26)]},
        split_by_case={"a": "train", "b": "train"},
        threshold=0.86,
    )

    pair = payload["potential_overlaps"][0]
    assert pair["same_split"] is True
    assert payload["summary"]["same_split_overlap_count"] == 1


def test_render_overlap_markdown_describes_empty_result():
    payload = build_render_overlap_audit(
        {"cases": [_case("a", 0.02, 0.12), _case("b", 0.14, 0.44)]},
        threshold=0.99,
    )

    markdown = render_overlap_markdown(payload)

    assert "# Render Overlap Audit" in markdown
    assert "none above threshold" in markdown


def _case(case_id, motion, foreground, profile="steady"):
    return {
        "case_id": case_id,
        "source": {"width": 1920, "height": 1080},
        "warnings": [],
        "render_quality": {"score": 0.9},
        "analysis": {
            "active_frame_ratio": 0.7,
            "blank_frame_ratio": 0.0,
            "brightness": _stats(0.18),
            "center_foreground_ratio": _stats(0.35),
            "component_count": _stats(12),
            "contrast": _stats(0.24),
            "edge_density": _stats(0.08),
            "foreground_ratio": _stats(foreground),
            "largest_component_ratio": _stats(0.12),
            "motion": _stats(motion / 4),
            "motion_area_ratio": _stats(motion),
            "motion_timeline": {
                "motion_profile": profile,
                "longest_stall_ratio": 0.1,
            },
            "saturation": _stats(0.12),
        },
    }


def _stats(value):
    return {"mean": value, "min": value, "max": value, "p95": value}
