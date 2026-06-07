from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[1]


def _load_script(name):
    path = REPO_ROOT / "scripts" / f"{name}.py"
    spec = spec_from_file_location(name, path)
    module = module_from_spec(spec)
    assert spec and spec.loader
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


build_visual_review_dashboard = _load_script("build_visual_review_dashboard")


def test_visual_dashboard_groups_pack_coverage_and_priority_items():
    queue = {
        "case_count": 3,
        "train_ready_count": 1,
        "decision_counts": {"promote_rendered": 1, "render_missing": 1, "watch_quality": 1},
        "items": [
            {
                **_item("ready", "promote_rendered", True, ["synthetic-v1"], 0.95),
                "render_path": "/tmp/ready.mp4",
            },
            _item("missing", "render_missing", False, ["synthetic-v9"], 0.0),
            {
                **_item("watch", "watch_quality", False, ["synthetic-v1"], 0.72),
                "warnings": ["center_crowding"],
                "render_path": "/tmp/watch.mp4",
                "contact_sheet_path": "/tmp/watch.png",
            },
        ],
    }
    render_analysis = {
        "cases": [
            {"case_id": "ready", "analysis": {"sampled_frames": 20}},
            {
                "case_id": "watch",
                "analysis": {
                    "sampled_frames": 20,
                    "frame_timeline": _timeline(),
                },
            },
        ]
    }

    dashboard = build_visual_review_dashboard._build_dashboard(
        queue=queue,
        render_analysis=render_analysis,
        readiness_report={
            "coverage_gaps": {"synthetic_packs": ["synthetic-v9"]},
            "render_debt": [{"case_id": "missing"}],
        },
        harness_status={"summary": {"status_counts": {"not_run": 1}}},
    )

    assert dashboard["summary"]["rendered_case_count"] == 2
    assert dashboard["summary"]["train_ready_watchlist_count"] == 0
    assert dashboard["summary"]["timeline_risk_count"] == 1
    assert dashboard["summary"]["warning_counts"] == {"center_crowding": 1}
    assert dashboard["summary"]["missing_train_ready_packs"] == ["synthetic-v9"]
    assert dashboard["pack_coverage"]["synthetic-v1"]["train_ready"] == 1
    assert dashboard["pack_coverage"]["synthetic-v1"]["rendered"] == 2
    assert dashboard["pack_coverage"]["synthetic-v9"]["render_missing"] == 1
    assert dashboard["timeline_risks"][0]["case_id"] == "watch"
    assert dashboard["timeline_risks"][0]["phase_activity"] == (
        "intro 1/10 active 3 blank; middle 9/10 active 0 blank"
    )
    assert dashboard["timeline_risks"][0]["motion_peaks"] == "f12 0.420 intro"
    assert [item["case_id"] for item in dashboard["priority_review"][:2]] == ["missing", "watch"]


def test_visual_dashboard_markdown_links_contact_sheets():
    dashboard = {
        "summary": {
            "case_count": 1,
            "rendered_case_count": 1,
            "train_ready_count": 0,
            "train_ready_watchlist_count": 1,
            "decision_counts": {"watch_quality": 1},
            "warning_counts": {"dense_foreground": 1},
            "motion_profile_counts": {"steady": 1},
            "motif_harness_status_counts": {"not_run": 1},
            "missing_train_ready_packs": [],
            "timeline_risk_count": 1,
        },
        "pack_coverage": {"synthetic-v1": {"all": 1, "rendered": 1, "train_ready": 0}},
        "train_ready_watchlist": [
            {
                "decision": "promote_reviewed",
                "case_id": "weak",
                "quality_score": 0.66,
                "motion_profile": "sparse",
                "longest_stall_ratio": 0.5,
                "warnings": [],
                "reasons": ["manual accepted"],
                "contact_sheet_path": "/tmp/weak.png",
            }
        ],
        "priority_review": [
            {
                "decision": "watch_quality",
                "case_id": "case",
                "quality_score": 0.7,
                "motion_profile": "steady",
                "warnings": ["dense_foreground"],
                "reasons": ["review"],
                "contact_sheet_path": "/tmp/case.png",
            }
        ],
        "motif_harness_cases": [
            {
                "status": "not_run",
                "case_id": "motif",
                "decision": "render_missing",
                "ae_error": "",
            }
        ],
        "timeline_risks": [
            {
                "decision": "watch_quality",
                "case_id": "case",
                "timeline_risks": ["intro_blank_start"],
                "phase_activity": "intro 1/10 active 3 blank",
                "motion_peaks": "f12 0.420 intro",
                "contact_sheet_path": "/tmp/case.png",
            }
        ],
    }

    markdown = build_visual_review_dashboard._markdown(dashboard)

    assert "# Visual Review Dashboard" in markdown
    assert "| weak | promote_reviewed | 0.660 | sparse | 0.500 | - | manual accepted | [open](contact_sheets/weak.png) |" in markdown
    assert "| not_run | motif | render_missing | - |" in markdown
    assert "[open](contact_sheets/case.png)" in markdown
    assert "| case | watch_quality | intro_blank_start | intro 1/10 active 3 blank | f12 0.420 intro | [open](contact_sheets/case.png) |" in markdown


def _item(case_id, decision, train_ready, tags, score):
    return {
        "case_id": case_id,
        "decision": decision,
        "train_ready": train_ready,
        "quality_score": score,
        "quality_priority": "pass",
        "motion_profile": "steady",
        "active_frame_ratio": 0.8,
        "longest_stall_ratio": 0.1,
        "warnings": [],
        "notes": [],
        "reasons": [],
        "tags": tags,
        "render_path": None,
        "contact_sheet_path": None,
    }


def _timeline():
    return {
        "phase_summary": [
            {
                "phase": "intro",
                "sample_count": 10,
                "active_count": 1,
                "blank_count": 3,
                "mean_foreground_ratio": 0.1,
            },
            {
                "phase": "middle",
                "sample_count": 10,
                "active_count": 9,
                "blank_count": 0,
                "mean_foreground_ratio": 0.2,
            },
        ],
        "motion_peaks": [
            {"source_frame": 12, "motion_area_ratio": 0.42, "phase": "intro"}
        ],
    }
