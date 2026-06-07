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


builder = _load_script("build_render_unlock_batch_status")


def test_unlock_batch_status_filters_greedy_sequence_and_counts_renderable():
    report = builder._build_report(
        plan={
            "summary": {"covered_requirement_count": 3, "requirement_count": 4},
            "greedy_unlock_sequence": [
                _target("grid", 100, ["motif:grid"]),
                _target("sound", 80, ["capability:markers"]),
                _target("missing", 40, ["motif:missing"]),
            ],
        },
        harness_status={
            "cases": [
                {"case_id": "sound", "status": "render_stale", "decision": "rerender_stale"},
                {"case_id": "grid", "status": "project_ready", "decision": "render_missing"},
                {"case_id": "other", "status": "project_ready", "decision": "render_missing"},
            ]
        },
    )

    assert report["summary"] == {
        "target_count": 3,
        "renderable_count": 2,
        "status_counts": {"missing_status": 1, "project_ready": 1, "render_stale": 1},
        "action_counts": {"create_project": 1, "render": 2},
        "batch_stage": "render_ready",
        "covered_requirement_count": 3,
        "requirement_count": 4,
    }
    assert [case["case_id"] for case in report["cases"]] == ["grid", "sound", "missing"]
    assert report["cases"][0]["unlock_rank"] == 1
    assert report["cases"][0]["next_action"] == "render"
    assert report["cases"][2]["status"] == "missing_status"
    assert report["cases"][2]["next_action"] == "create_project"


def test_unlock_batch_status_marks_project_preparation_stage():
    report = builder._build_report(
        plan={
            "summary": {"covered_requirement_count": 2, "requirement_count": 2},
            "greedy_unlock_sequence": [
                _target("grid", 100, ["motif:grid"]),
                _target("stale", 80, ["capability:camera_3d"]),
            ],
        },
        harness_status={
            "cases": [
                {"case_id": "grid", "status": "not_run", "decision": "render_missing"},
                {"case_id": "stale", "status": "stale_project", "decision": "rerender_stale"},
            ]
        },
    )

    assert report["summary"]["renderable_count"] == 0
    assert report["summary"]["action_counts"] == {"create_project": 1, "refresh_project": 1}
    assert report["summary"]["batch_stage"] == "prepare_projects"


def test_unlock_batch_status_treats_missing_project_as_create_project():
    report = builder._build_report(
        plan={
            "summary": {"covered_requirement_count": 1, "requirement_count": 1},
            "greedy_unlock_sequence": [_target("finance", 50, ["theme:finance_market"])],
        },
        harness_status={"cases": [{"case_id": "finance", "status": "missing_project"}]},
    )

    assert report["summary"]["action_counts"] == {"create_project": 1}
    assert report["cases"][0]["next_action"] == "create_project"


def test_unlock_batch_status_surfaces_runner_blocker():
    report = builder._build_report(
        plan={
            "summary": {"covered_requirement_count": 2, "requirement_count": 2},
            "greedy_unlock_sequence": [_target("grid", 100, ["motif:grid"])],
        },
        harness_status={"cases": [{"case_id": "grid", "status": "not_run"}]},
        runner_status={
            "ok": False,
            "reason": "scripting_access_disabled",
            "javascript_debugger": True,
            "script_file_network_access": None,
        },
    )

    assert report["summary"]["batch_stage"] == "blocked_prepare_projects"
    assert report["summary"]["blocker"]["reason"] == "scripting_access_disabled"
    assert "file/network scripting is not enabled" in report["summary"]["blocker"]["detail"]


def test_unlock_batch_status_reads_nested_runner_summary():
    report = builder._build_report(
        plan={
            "summary": {"covered_requirement_count": 1, "requirement_count": 1},
            "greedy_unlock_sequence": [_target("grid", 100, ["motif:grid"])],
        },
        harness_status={"cases": [{"case_id": "grid", "status": "not_run"}]},
        runner_status={"summary": {"ok": False, "reason": "runner_failed", "returncode": 9}},
    )

    assert report["summary"]["blocker"]["reason"] == "runner_failed"
    assert "return code 9" in report["summary"]["blocker"]["detail"]


def test_unlock_batch_status_explains_missing_runner_report():
    report = builder._build_report(
        plan={
            "summary": {"covered_requirement_count": 1, "requirement_count": 1},
            "greedy_unlock_sequence": [_target("grid", 100, ["motif:grid"])],
        },
        harness_status={"cases": [{"case_id": "grid", "status": "not_run"}]},
        runner_status={
            "summary": {
                "ok": False,
                "reason": "missing_runner_report",
                "returncode": 0,
                "completed_chunks": 0,
            }
        },
    )

    assert report["summary"]["batch_stage"] == "blocked_prepare_projects"
    assert report["summary"]["blocker"]["reason"] == "missing_runner_report"
    assert "runner_report.txt" in report["summary"]["blocker"]["detail"]


def test_unlock_batch_markdown_includes_prepare_and_refresh_commands(tmp_path):
    report = {
        "summary": {
            "target_count": 0,
            "renderable_count": 0,
            "covered_requirement_count": 0,
            "requirement_count": 0,
            "batch_stage": "prepare_projects",
            "status_counts": {},
            "action_counts": {},
        },
        "cases": [],
    }

    markdown = builder._markdown(report, tmp_path / "batch.json")

    assert "run_ae_render_unlock_harnesses.py" in markdown
    assert "refresh_after_manual_harnesses.py" in markdown
    assert "--render-status-report" in markdown


def _target(case_id, score, unlocks):
    return {
        "case_id": case_id,
        "decision": "render_missing",
        "score": score,
        "new_unlocks": unlocks,
        "coverage_keys": unlocks,
        "source_repo_path": f"data/synthetic/templates/{case_id}.jsx",
    }
