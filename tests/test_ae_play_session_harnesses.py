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


play_harnesses = _load_script("build_ae_play_session_harnesses")


def test_play_harness_selects_unique_first_unlock_targets():
    records = [_record("a"), _record("b"), _record("c")]
    inspiration = {
        "train_ready_gaps": [
            {"motif": "one", "first_unlock_case": "a"},
            {"motif": "two", "first_unlock_case": "a"},
            {"motif": "three", "first_unlock_case": "b"},
            {"motif": "missing", "first_unlock_case": "x"},
        ]
    }

    targets = play_harnesses._select_targets(records, inspiration, limit=0)

    assert [target["case_id"] for target in targets] == ["a", "b"]


def test_play_harness_builds_no_save_or_report_script():
    script = play_harnesses._build_script([_record("a")])

    assert "app.project.save" not in script
    assert "writeReport" not in script
    assert "new File" not in script
    assert "render" not in script.lower()
    assert "AEFT Play Review Index" in script


def test_play_harness_index_lists_chunks_and_targets(tmp_path):
    chunk = tmp_path / "play_review_01.jsx"

    play_harnesses._write_index(
        [chunk],
        [_record("a")],
        {"summary": {"train_ready_gap_count": 3}},
        tmp_path,
    )

    markdown = (tmp_path / "README.md").read_text()
    assert "# AE Play Session Harnesses" in markdown
    assert "first-unlock cases for 3 web-inspired" in markdown
    assert "- a" in markdown


def _record(case_id):
    completion = """(function () {
    app.beginUndoGroup("AEFT Demo");
    var comp = app.project.items.addComp("AEFT Demo", 1920, 1080, 1, 6, 30);
    app.endUndoGroup();
})();"""
    return {
        "case_id": case_id,
        "completion": completion,
        "expected": {"comp_name": "AEFT Demo"},
    }
