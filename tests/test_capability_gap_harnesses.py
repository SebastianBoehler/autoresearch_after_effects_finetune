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


builder = _load_script("build_capability_gap_harnesses")
checker = _load_script("check_capability_gap_harnesses")


def test_capability_gap_harness_selects_first_available_unlock_per_gap():
    records = [_record("a"), _record("b"), _record("c")]
    capability = {
        "train_ready_gap_unlocks": [
            {"capability": "camera_3d", "case_ids": ["a", "b"]},
            {"capability": "markers", "case_ids": ["a", "c"]},
            {"capability": "time_remap", "case_ids": ["c"]},
        ]
    }
    queue = {
        "items": [
            {"case_id": "a", "decision": "promote_rendered"},
            {"case_id": "b", "decision": "render_missing"},
            {"case_id": "c", "decision": "rerender_stale"},
        ]
    }

    targets = builder._select_targets(records, capability, queue, {"render_missing", "rerender_stale"})

    assert [target["case_id"] for target in targets] == ["b", "c"]


def test_capability_gap_status_targets_unique_first_unlock_cases():
    capability = {
        "train_ready_gap_unlocks": [
            {"capability": "camera_3d", "case_ids": ["a", "b"]},
            {"capability": "markers", "case_ids": ["a"]},
            {"capability": "empty", "case_ids": []},
        ]
    }

    assert checker._target_case_ids(capability) == ["a"]
    assert checker._readiness(["a"]) == {"render_debt": [{"case_id": "a"}]}


def test_capability_gap_index_and_markdown_use_specific_titles(tmp_path):
    runner = tmp_path / "run_all_harnesses.jsx"
    chunk = tmp_path / "manual_harness_01.jsx"

    builder._write_index(
        [chunk],
        runner,
        [_record("a")],
        {"summary": {"train_ready_core_gap_count": 2}},
        tmp_path,
    )
    markdown = (tmp_path / "README.md").read_text()
    assert "Manual AE Capability-Gap Harnesses" in markdown
    assert "first-unlock cases for 2 missing train-ready" in markdown

    report = {
        "summary": {
            "target_count": 1,
            "status_counts": {"not_run": 1},
            "runner_report_exists": False,
            "runner_completed_chunks": 0,
            "runner_error_chunks": 0,
        },
        "cases": [{"status": "not_run", "case_id": "a", "decision": "render_missing", "ae_error": ""}],
    }
    status_module = checker._load_status_module()
    assert "# Manual AE Capability-Gap Harness Status" in checker._markdown(status_module, report)


def _record(case_id):
    return {"case_id": case_id, "completion": "", "expected": {}, "tags": []}
