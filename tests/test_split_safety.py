from after_effects_pipeline.split_safety import (
    build_split_safety_audit,
    split_safety_markdown,
)


def test_split_safety_passes_when_overlaps_are_cross_split_and_signatures_are_spread():
    payload = build_split_safety_audit(
        {
            "cases": [
                _case("a", "landscape/steady/high/center"),
                _case("b", "landscape/steady/high/center"),
                _case("c", "square/varied/high/open"),
            ],
            "potential_overlaps": [
                {
                    "a": "a",
                    "b": "b",
                    "split_a": "train",
                    "split_b": "valid",
                    "same_split": False,
                    "score": 0.91,
                }
            ],
        },
        split_by_case={"a": "train", "b": "valid", "c": "train"},
    )

    assert payload["summary"]["ok"] is True
    assert payload["summary"]["same_split_overlap_count"] == 0
    assert payload["issues"] == []


def test_split_safety_flags_same_split_overlaps_and_repeated_signatures():
    payload = build_split_safety_audit(
        {
            "cases": [
                _case("a", "landscape/steady/high/center"),
                _case("b", "landscape/steady/high/center"),
                _case("c", "landscape/steady/high/center"),
                _case("d", "square/varied/high/open"),
            ],
            "potential_overlaps": [
                {
                    "a": "a",
                    "b": "b",
                    "split_a": "train",
                    "split_b": "train",
                    "same_split": True,
                    "score": 0.93,
                    "shared_signals": ["animation_signature=landscape/steady/high/center"],
                }
            ],
        },
        split_by_case={"a": "train", "b": "train", "c": "train", "d": "valid"},
    )

    assert payload["summary"]["ok"] is False
    assert payload["summary"]["same_split_overlap_count"] == 1
    assert payload["summary"]["repeated_signature_issue_count"] == 1
    assert [issue["type"] for issue in payload["issues"]] == [
        "same_split_overlap",
        "repeated_animation_signature",
    ]


def test_split_safety_markdown_lists_issues():
    payload = build_split_safety_audit(
        {
            "cases": [_case("a", "sig"), _case("b", "sig"), _case("c", "sig")],
            "potential_overlaps": [],
        },
        split_by_case={"a": "test", "b": "test", "c": "test"},
    )

    markdown = split_safety_markdown(payload)

    assert "# Train-Ready Split Safety Audit" in markdown
    assert "repeated_animation_signature" in markdown


def _case(case_id, signature):
    return {"case_id": case_id, "animation_signature": signature}
