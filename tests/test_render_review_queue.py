from after_effects_pipeline.render_review_queue import (
    build_render_review_queue,
    render_review_queue_markdown,
)


def test_render_review_queue_promotes_clean_current_render():
    payload = build_render_review_queue(
        [_record("clean")],
        render_analysis={"cases": [_render_case("clean", 0.92, "pass")]},
        dataset_audit={},
        contact_sheets={"cases": [_sheet("clean")]},
    )

    item = payload["items"][0]

    assert payload["train_ready_count"] == 1
    assert item["decision"] == "promote_rendered"
    assert item["train_ready"] is True
    assert item["contact_sheet_path"].endswith("clean.png")


def test_render_review_queue_keeps_missing_and_stale_out_of_training():
    records = [_record("missing"), _record("stale")]
    audit = {
        "missing_render_cases": ["missing"],
        "stale_render_cases": ["stale"],
        "actionable_render_warning_cases": [],
        "intentional_render_warning_cases": [],
    }

    payload = build_render_review_queue(
        records,
        render_analysis={"cases": [_render_case("stale", 0.96, "pass")]},
        dataset_audit=audit,
    )

    decisions = {item["case_id"]: item["decision"] for item in payload["items"]}

    assert decisions == {"missing": "render_missing", "stale": "rerender_stale"}
    assert payload["train_ready_count"] == 0


def test_render_review_queue_routes_visual_review_priorities():
    records = [_record("fix"), _record("intentional"), _record("watch")]
    audit = {
        "missing_render_cases": [],
        "stale_render_cases": [],
        "actionable_render_warning_cases": [{"case_id": "fix"}],
        "intentional_render_warning_cases": [{"case_id": "intentional"}],
    }
    render_analysis = {
        "cases": [
            _render_case("fix", 0.4, "fix", warnings=["low_motion"]),
            _render_case("intentional", 0.8, "pass", warnings=["dense_foreground"]),
            _render_case("watch", 0.82, "watch"),
        ]
    }

    payload = build_render_review_queue(
        records,
        render_analysis=render_analysis,
        dataset_audit=audit,
    )
    decisions = {item["case_id"]: item["decision"] for item in payload["items"]}

    assert decisions["fix"] == "fix_render"
    assert decisions["intentional"] == "manual_review_render"
    assert decisions["watch"] == "watch_quality"


def test_render_review_queue_promotes_explicit_manual_acceptance():
    audit = {
        "missing_render_cases": [],
        "stale_render_cases": [],
        "actionable_render_warning_cases": [],
        "intentional_render_warning_cases": [{"case_id": "full_frame"}],
    }
    manual = {
        "cases": [
            {
                "case_id": "full_frame",
                "decision": "promote",
                "note": "full-frame transition is intentional",
            }
        ]
    }

    payload = build_render_review_queue(
        [_record("full_frame")],
        render_analysis={
            "cases": [
                _render_case("full_frame", 0.88, "pass", warnings=["dense_foreground"])
            ]
        },
        dataset_audit=audit,
        manual_decisions=manual,
    )

    item = payload["items"][0]

    assert item["decision"] == "promote_reviewed"
    assert item["train_ready"] is True
    assert payload["train_ready_count"] == 1


def test_render_review_queue_markdown_lists_links_and_counts():
    payload = build_render_review_queue(
        [_record("clean")],
        render_analysis={"cases": [_render_case("clean", 0.92, "pass")]},
        contact_sheets={"cases": [_sheet("clean")]},
    )

    markdown = render_review_queue_markdown(payload)

    assert "# Render Review Queue" in markdown
    assert "promote_rendered: 1" in markdown
    assert "[open](contact_sheets/clean.png)" in markdown


def _record(case_id):
    return {
        "case_id": case_id,
        "prompt": f"Create {case_id}",
        "tags": ["synthetic"],
        "source_repo_path": f"data/synthetic/templates/{case_id}.jsx",
    }


def _render_case(case_id, score, priority, warnings=None):
    return {
        "case_id": case_id,
        "video_path": f"/tmp/{case_id}/render.mp4",
        "warnings": warnings or [],
        "notes": ["steady_motion"],
        "analysis": {
            "active_frame_ratio": 0.8,
            "motion_timeline": {
                "motion_profile": "steady",
                "longest_stall_ratio": 0.1,
            },
        },
        "render_quality": {
            "score": score,
            "priority": priority,
            "reasons": [],
        },
    }


def _sheet(case_id):
    return {
        "case_id": case_id,
        "ok": True,
        "output_path": f"/tmp/contact_sheets/{case_id}.png",
    }
