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


check_motif_gap_harnesses = _load_script("check_motif_gap_harnesses")


def test_motif_gap_status_targets_unique_first_unlock_cases():
    inspiration = {
        "train_ready_gaps": [
            {"motif": "one", "first_unlock_case": "a"},
            {"motif": "two", "first_unlock_case": "a"},
            {"motif": "three", "first_unlock_case": "b"},
            {"motif": "empty", "first_unlock_case": ""},
        ]
    }

    assert check_motif_gap_harnesses._target_case_ids(inspiration) == ["a", "b"]
    assert check_motif_gap_harnesses._readiness(["a", "b"]) == {
        "render_debt": [{"case_id": "a"}, {"case_id": "b"}]
    }


def test_motif_gap_status_markdown_uses_specific_title():
    status_module = check_motif_gap_harnesses._load_status_module()
    report = {
        "summary": {
            "target_count": 1,
            "status_counts": {"not_run": 1},
            "runner_report_exists": False,
            "runner_completed_chunks": 0,
            "runner_error_chunks": 0,
        },
        "cases": [
            {
                "status": "not_run",
                "case_id": "a",
                "decision": "render_missing",
                "ae_error": "",
            }
        ],
    }

    markdown = check_motif_gap_harnesses._markdown(status_module, report)

    assert "# Manual AE Motif-Gap Harness Status" in markdown
    assert "| not_run | a | render_missing | - |" in markdown
