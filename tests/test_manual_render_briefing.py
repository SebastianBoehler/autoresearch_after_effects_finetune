from after_effects_pipeline.manual_render_briefing import (
    build_manual_render_briefing,
    render_manual_render_briefing_markdown,
)


def test_manual_render_briefing_splits_archetype_targets_first():
    payload = build_manual_render_briefing(
        quality_gap_matrix={
            "items": [
                {
                    "case_id": "sparse",
                    "priority": 200,
                    "action": "render_unlock_archetype_gap",
                    "decision": "rerender_stale",
                    "archetype": "middle_sparse_motion",
                    "new_unlocks": ["archetype:middle_sparse_motion"],
                    "progression_issues": ["sparse_progression"],
                    "warnings": [],
                },
                {
                    "case_id": "grid",
                    "priority": 160,
                    "action": "render_unlock_requirement",
                    "decision": "render_missing",
                    "archetype": "",
                    "new_unlocks": ["motif:grid_layout_builder"],
                    "progression_issues": [],
                    "warnings": [],
                },
            ]
        },
        batch_status={
            "summary": {
                "renderable_count": 0,
                "batch_stage": "blocked_prepare_projects",
                "blocker": {"reason": "missing_runner_report"},
            },
            "cases": [
                _status("sparse", "refresh_project", "stale_project"),
                _status("grid", "create_project", "not_run"),
            ],
        },
        runner_path="/tmp/run_all_harnesses.jsx",
    )

    assert payload["summary"]["first_pass_count"] == 1
    assert payload["summary"]["second_pass_count"] == 1
    assert payload["summary"]["refresh_project_count"] == 1
    assert payload["first_pass_targets"][0]["case_id"] == "sparse"
    assert payload["second_pass_targets"][0]["case_id"] == "grid"


def test_manual_render_briefing_markdown_includes_runner_and_commands():
    payload = build_manual_render_briefing(
        quality_gap_matrix={"items": []},
        batch_status={"summary": {}, "cases": []},
        runner_path="/tmp/run_all_harnesses.jsx",
    )

    markdown = render_manual_render_briefing_markdown(payload)

    assert "# Manual AE Render Briefing" in markdown
    assert "/tmp/run_all_harnesses.jsx" in markdown
    assert "refresh_after_manual_harnesses.py" in markdown


def _status(case_id, next_action, status):
    return {
        "case_id": case_id,
        "next_action": next_action,
        "status": status,
        "source_repo_path": f"data/synthetic/templates/{case_id}.jsx",
        "project_path": f"artifacts/ae_live_checks/{case_id}/project.aep",
        "render_path": f"artifacts/ae_live_checks/{case_id}/render.mp4",
    }
