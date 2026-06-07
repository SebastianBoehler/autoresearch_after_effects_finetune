from after_effects_pipeline.overlap_remediation import (
    build_overlap_remediation,
    render_overlap_remediation_markdown,
)


def test_overlap_remediation_prioritizes_same_split_pairs():
    payload = build_overlap_remediation(
        render_overlap={
            "potential_overlaps": [
                {
                    "a": "a",
                    "b": "b",
                    "score": 0.94,
                    "same_split": True,
                    "shared_signals": ["motion_profile=steady"],
                }
            ]
        },
        source_pattern_audit={"pattern_overlap_pairs": []},
        render_queue={"items": [_item("a"), _item("b")]},
    )

    pair = payload["pairs"][0]

    assert pair["status"] == "same_split_overlap"
    assert pair["priority"] == "high"
    assert payload["summary"]["high_risk_pair_count"] == 1


def test_overlap_remediation_detects_dual_render_source_overlap():
    payload = build_overlap_remediation(
        render_overlap={"potential_overlaps": [{"a": "a", "b": "b", "score": 0.9}]},
        source_pattern_audit={
            "pattern_overlap_pairs": [
                {"a": "b", "b": "a", "score": 0.95, "shared_patterns": ["layer_mix:mixed_scene"]}
            ]
        },
        render_queue={"items": [_item("a", train_ready=False), _item("b", train_ready=False)]},
    )

    pair = payload["pairs"][0]

    assert pair["status"] == "dual_render_source_overlap"
    assert pair["has_render_overlap"] is True
    assert pair["has_source_pattern_overlap"] is True
    assert payload["summary"]["dual_overlap_pair_count"] == 1


def test_overlap_remediation_markdown_lists_source_only_watch():
    payload = build_overlap_remediation(
        render_overlap={"potential_overlaps": []},
        source_pattern_audit={
            "cases": [
                {"case_id": "a", "layer_mix": "layer_mix:text_system"},
                {"case_id": "b", "layer_mix": "layer_mix:mixed_scene"},
            ],
            "pattern_overlap_pairs": [
                {"a": "a", "b": "b", "score": 1.0, "shared_patterns": ["feature:loop_generated"]}
            ]
        },
        render_queue={"items": [
            _item("a", tags=["vertical", "caption"]),
            _item("b", train_ready=False, tags=["landscape", "broadcast"]),
        ]},
    )

    markdown = render_overlap_remediation_markdown(payload)

    assert "# Overlap Remediation Audit" in markdown
    assert "source_pattern_watch" in markdown
    assert "feature:loop_generated" in markdown
    assert "layer_mix:text_system vs mixed_scene" in markdown
    assert payload["summary"]["source_pattern_contrast_pair_count"] == 1
    assert payload["summary"]["thin_source_pattern_pair_count"] == 0


def test_overlap_remediation_flags_thin_source_pattern_pairs():
    payload = build_overlap_remediation(
        render_overlap={"potential_overlaps": []},
        source_pattern_audit={
            "cases": [
                {"case_id": "a", "layer_mix": "layer_mix:mixed_scene"},
                {"case_id": "b", "layer_mix": "layer_mix:mixed_scene"},
            ],
            "pattern_overlap_pairs": [
                {"a": "a", "b": "b", "score": 1.0, "shared_patterns": ["layer_mix:mixed_scene"]}
            ],
        },
        render_queue={"items": [_item("a"), _item("b", train_ready=False)]},
    )

    assert payload["summary"]["thin_source_pattern_pair_count"] == 1
    assert "thin source-pattern pairs" in payload["recommendations"][-1]


def _item(case_id, *, train_ready=True, tags=None):
    return {
        "case_id": case_id,
        "train_ready": train_ready,
        "decision": "promote_rendered" if train_ready else "render_missing",
        "tags": tags or [],
    }
