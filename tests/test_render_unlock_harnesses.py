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


builder = _load_script("build_render_unlock_harnesses")
checker = _load_script("check_render_unlock_harnesses")


def test_render_unlock_harness_selects_greedy_targets_in_rank_order():
    records = [_record("a"), _record("b"), _record("c")]
    plan = {"greedy_unlock_sequence": [{"case_id": "b"}, {"case_id": "a"}, {"case_id": "c"}]}
    queue = {
        "items": [
            {"case_id": "a", "decision": "render_missing"},
            {"case_id": "b", "decision": "render_missing"},
            {"case_id": "c", "decision": "promote_rendered"},
        ]
    }

    targets = builder._select_targets(records, plan, queue, {"render_missing"})

    assert [target["case_id"] for target in targets] == ["b", "a"]


def test_render_unlock_status_targets_unique_greedy_cases():
    plan = {"greedy_unlock_sequence": [{"case_id": "a"}, {"case_id": "b"}, {"case_id": "a"}]}

    assert checker._target_case_ids(plan) == ["a", "b"]
    assert checker._readiness(["a"]) == {"render_debt": [{"case_id": "a"}]}


def test_render_unlock_index_and_markdown_use_specific_titles(tmp_path):
    runner = tmp_path / "run_all_harnesses.jsx"
    chunk = tmp_path / "manual_harness_01.jsx"
    plan = {
        "summary": {"covered_requirement_count": 2, "requirement_count": 3},
        "greedy_unlock_sequence": [{"case_id": "a", "new_unlocks": ["motif:grid"]}],
    }

    builder._write_index([chunk], runner, [_record("a")], plan, tmp_path)
    markdown = (tmp_path / "README.md").read_text()

    assert "Manual AE Render-Unlock Harnesses" in markdown
    assert "2/3 render-unlock" in markdown
    status_module = checker._load_status_module()
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
    assert "# Manual AE Render-Unlock Harness Status" in checker._markdown(status_module, report)


def test_manual_runner_respects_skip_confirm_and_alert(tmp_path):
    chunk = tmp_path / "manual_harness_01.jsx"
    harnesses = builder._load_harnesses()
    runner = harnesses._write_runner([chunk], tmp_path)
    script = runner.read_text()

    assert "!$.global.AEFT_SKIP_CONFIRM && !confirm" in script
    assert "!$.global.AEFT_SKIP_ALERT" in script


def _record(case_id):
    return {"case_id": case_id, "completion": "", "expected": {}, "tags": []}
