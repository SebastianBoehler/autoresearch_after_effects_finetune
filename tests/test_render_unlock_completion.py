from after_effects_pipeline.render_unlock_completion import (
    build_render_unlock_completion,
    render_render_unlock_completion_markdown,
)


def test_completion_marks_requirements_satisfied_from_train_ready_artifacts():
    payload = build_render_unlock_completion(
        plan={
            "requirements": [
                "pack:complex_motion",
                "capability:camera_3d",
                "motif:grid",
                "pattern:layer_mix:camera_3d",
                "motif:missing",
            ],
            "greedy_unlock_sequence": [
                _target("grid_builder", ["pack:complex_motion", "motif:grid"]),
                _target("terrain_route", ["capability:camera_3d", "pattern:layer_mix:camera_3d", "motif:missing"]),
            ],
        },
        train_ready_manifest={
            "case_ids": ["grid_builder"],
            "synthetic_pack_counts": {"complex_motion": 1},
        },
        capability_audit={"train_ready_capability_counts": {"camera_3d": 2}},
        inspiration_coverage={
            "motifs": [
                {"motif": "grid", "train_ready_count": 1},
                {"motif": "missing", "train_ready_count": 0},
            ]
        },
        source_pattern_audit={
            "train_ready_pattern_counts": {"layer_mix:camera_3d": 1}
        },
    )

    assert payload["summary"] == {
        "requirement_count": 5,
        "satisfied_requirement_count": 4,
        "remaining_requirement_count": 1,
        "target_count": 2,
        "train_ready_target_count": 1,
    }
    assert payload["remaining_requirements"] == ["motif:missing"]
    assert payload["targets"][0]["train_ready"] is True
    assert payload["targets"][0]["remaining_unlocks"] == []
    assert payload["targets"][1]["train_ready"] is False
    assert payload["targets"][1]["satisfied_unlocks"] == [
        "capability:camera_3d",
        "pattern:layer_mix:camera_3d",
    ]


def test_completion_markdown_lists_remaining_requirements():
    payload = {
        "summary": {
            "requirement_count": 1,
            "satisfied_requirement_count": 0,
            "remaining_requirement_count": 1,
            "target_count": 1,
            "train_ready_target_count": 0,
        },
        "remaining_requirements": ["motif:missing"],
        "targets": [
            {
                "case_id": "missing_case",
                "train_ready": False,
                "satisfied_unlocks": [],
                "remaining_unlocks": ["motif:missing"],
            }
        ],
    }

    markdown = render_render_unlock_completion_markdown(payload)

    assert "# Render Unlock Completion Audit" in markdown
    assert "- motif:missing" in markdown
    assert "| missing_case | False | - | motif:missing |" in markdown


def _target(case_id: str, unlocks: list[str]) -> dict[str, object]:
    return {"case_id": case_id, "new_unlocks": unlocks}
