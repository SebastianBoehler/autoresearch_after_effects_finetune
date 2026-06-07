from after_effects_pipeline.render_issue_remediation import (
    build_render_issue_remediation,
    render_render_issue_remediation_markdown,
)


def test_render_issue_remediation_marks_source_fixed_stale_cases():
    payload = build_render_issue_remediation(
        render_progression={"cases": [{"case_id": "fixed", "issues": ["inactive_outro_stall"]}]},
        render_analysis={"cases": [{"case_id": "fixed", "warnings": ["center_crowding"]}]},
        render_queue={
            "items": [
                {
                    "case_id": "fixed",
                    "decision": "rerender_stale",
                    "reasons": ["source changed after render"],
                    "source_repo_path": "data/synthetic/templates/fixed.jsx",
                    "train_ready": False,
                }
            ]
        },
        source_motion={"cases": [{"case_id": "fixed", "profile": "mixed_full_span", "issues": []}]},
        source_quality={"cases": [{"case_id": "fixed", "issues": []}]},
    )

    case = payload["cases"][0]

    assert case["source_remediated"] is True
    assert case["needs_fresh_render"] is True
    assert case["status"] == "source_remediated_needs_rerender"
    assert payload["summary"]["source_remediated_count"] == 1


def test_render_issue_remediation_keeps_source_issues_actionable():
    payload = build_render_issue_remediation(
        render_progression={"cases": [{"case_id": "thin", "issues": ["sparse_progression"]}]},
        render_analysis={"cases": []},
        render_queue={"items": [{"case_id": "thin", "decision": "fix_render", "reasons": []}]},
        source_motion={"cases": [{"case_id": "thin", "profile": "intro_weighted", "issues": ["no_late_motion_signal"]}]},
        source_quality={"cases": [{"case_id": "thin", "issues": ["short_temporal_span"]}]},
    )

    case = payload["cases"][0]

    assert case["source_remediated"] is False
    assert case["status"] == "source_needs_attention"
    assert payload["summary"]["source_issue_count"] == 1


def test_render_issue_remediation_markdown_lists_cases():
    payload = build_render_issue_remediation(
        render_progression={"cases": []},
        render_analysis={"cases": [{"case_id": "warned", "warnings": ["dense_foreground"]}]},
        render_queue={
            "items": [
                {
                    "case_id": "warned",
                    "decision": "rerender_stale",
                    "reasons": ["source changed after render"],
                    "train_ready": False,
                }
            ]
        },
        source_motion={"cases": [{"case_id": "warned", "profile": "expression_rich", "issues": []}]},
        source_quality={"cases": [{"case_id": "warned", "issues": []}]},
    )

    markdown = render_render_issue_remediation_markdown(payload)

    assert "# Render Issue Remediation Audit" in markdown
    assert "warned" in markdown
    assert "source_remediated_needs_rerender" in markdown
