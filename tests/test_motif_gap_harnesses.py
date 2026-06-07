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


build_motif_gap_harnesses = _load_script("build_motif_gap_harnesses")


def test_motif_gap_harness_selects_unique_first_unlock_targets():
    records = [_record("a"), _record("b"), _record("c")]
    inspiration = {
        "train_ready_gaps": [
            {"motif": "one", "first_unlock_case": "a"},
            {"motif": "two", "first_unlock_case": "a"},
            {"motif": "three", "first_unlock_case": "b"},
            {"motif": "done", "first_unlock_case": "c"},
        ]
    }
    queue = {
        "items": [
            {"case_id": "a", "decision": "render_missing"},
            {"case_id": "b", "decision": "rerender_stale"},
            {"case_id": "c", "decision": "promote_rendered"},
        ]
    }

    targets = build_motif_gap_harnesses._select_targets(
        records,
        inspiration,
        queue,
        {"render_missing", "rerender_stale"},
    )

    assert [target["case_id"] for target in targets] == ["a", "b"]


def test_motif_gap_harness_index_names_runner(tmp_path):
    runner = tmp_path / "run_all_harnesses.jsx"
    chunk = tmp_path / "manual_harness_01.jsx"

    build_motif_gap_harnesses._write_index(
        [chunk],
        runner,
        [_record("a")],
        {"summary": {"train_ready_gap_count": 2}},
        tmp_path,
    )

    markdown = (tmp_path / "README.md").read_text()
    assert "Manual AE Motif-Gap Harnesses" in markdown
    assert "first-unlock cases for 2 web-inspired" in markdown
    assert "- a" in markdown


def _record(case_id):
    return {"case_id": case_id, "completion": "", "expected": {}, "tags": []}
