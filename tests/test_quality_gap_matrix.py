from after_effects_pipeline.quality_gap_matrix import (
    build_quality_gap_matrix,
    render_quality_gap_matrix_markdown,
)


def test_quality_gap_matrix_prioritizes_archetype_unlocks_and_overlap_watches():
    payload = build_quality_gap_matrix(
        queue={
            "items": [
                {"case_id": "ready_a", "decision": "promote_rendered", "train_ready": True},
                {"case_id": "ready_b", "decision": "promote_rendered", "train_ready": True},
                {"case_id": "stale_sparse", "decision": "rerender_stale", "train_ready": False},
            ]
        },
        render_overlap={
            "potential_overlaps": [
                {"a": "ready_a", "b": "ready_b", "same_split": False, "score": 0.91}
            ]
        },
        animation_anatomy={
            "cases": [
                {"case_id": "ready_a", "archetype": "continuous_motion"},
                {"case_id": "ready_b", "archetype": "continuous_motion"},
                {"case_id": "stale_sparse", "archetype": "middle_sparse_motion"},
            ],
            "train_ready_archetype_gaps": [
                {
                    "archetype": "middle_sparse_motion",
                    "first_unlock_case": "stale_sparse",
                    "case_ids": ["stale_sparse"],
                }
            ],
        },
        render_progression={
            "cases": [{"case_id": "stale_sparse", "issues": ["sparse_progression"]}]
        },
        render_unlock_plan={
            "summary": {"covered_requirement_count": 1, "requirement_count": 1},
            "greedy_unlock_sequence": [
                {
                    "case_id": "stale_sparse",
                    "decision": "rerender_stale",
                    "new_unlocks": ["archetype:middle_sparse_motion"],
                    "archetype_unlocks": ["middle_sparse_motion"],
                    "source_repo_path": "data/synthetic/templates/stale_sparse.jsx",
                }
            ],
        },
    )

    assert payload["summary"]["train_ready_overlap_watch_count"] == 2
    assert payload["summary"]["archetype_unlock_target_count"] == 1
    assert payload["items"][0]["case_id"] == "stale_sparse"
    assert payload["items"][0]["action"] == "render_unlock_archetype_gap"
    assert {item["action"] for item in payload["items"][1:]} == {"watch_train_ready_overlap"}
    assert "prefer rendering over adding new source cases" in payload["recommendations"][-1]


def test_quality_gap_matrix_markdown_lists_priority_actions():
    payload = build_quality_gap_matrix(
        queue={"items": [{"case_id": "ready", "decision": "promote_rendered", "train_ready": True}]},
        render_overlap={"potential_overlaps": []},
        animation_anatomy={"cases": [{"case_id": "ready", "archetype": "varied_sequence"}]},
        render_progression={"cases": []},
        render_unlock_plan={"summary": {"covered_requirement_count": 0, "requirement_count": 1}},
    )

    markdown = render_quality_gap_matrix_markdown(payload)

    assert "# Quality Gap Matrix" in markdown
    assert "keep_train_ready" in markdown
