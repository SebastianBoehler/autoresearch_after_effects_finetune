from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import os
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


check_ae_manual_harnesses = _load_script("check_ae_manual_harnesses")


def test_manual_harness_status_classifies_cases_and_runner(tmp_path):
    old_root = check_ae_manual_harnesses.REPO_ROOT
    check_ae_manual_harnesses.REPO_ROOT = tmp_path
    try:
        records = [
            _record("not_run"),
            _record("script_error"),
            _record("stale_project"),
            _record("project_ready"),
            _record("render_ready"),
        ]
        for record in records:
            source = tmp_path / record["source_repo_path"]
            source.parent.mkdir(parents=True, exist_ok=True)
            source.write_text("// source\n")

        _write_case_report(tmp_path, "script_error", "ok=false\nerror=bad layer\n")
        _write_project(tmp_path, "stale_project", mtime=100)
        os.utime(tmp_path / "data/stale_project.jsx", (200, 200))
        _write_project(tmp_path, "project_ready", mtime=300)
        os.utime(tmp_path / "data/project_ready.jsx", (100, 100))
        _write_project(tmp_path, "render_ready", mtime=300)
        _write_render(tmp_path, "render_ready", mtime=400)
        os.utime(tmp_path / "data/render_ready.jsx", (100, 100))

        harness_dir = tmp_path / "artifacts/ae_live_checks/_manual_harnesses"
        harness_dir.mkdir(parents=True)
        (harness_dir / "runner_report.txt").write_text("ok:one.jsx\nerror:two.jsx:bad\n")
        queue = {"items": [_queue_item(record["case_id"]) for record in records]}
        readiness = {"render_debt": [{"case_id": record["case_id"]} for record in records]}

        report = check_ae_manual_harnesses._build_report(
            records=records,
            queue=queue,
            readiness=readiness,
            decisions={"render_missing"},
            harness_dir=harness_dir,
        )

        assert report["summary"]["runner_report_exists"] is True
        assert report["summary"]["runner_completed_chunks"] == 1
        assert report["summary"]["runner_error_chunks"] == 1
        assert report["summary"]["status_counts"] == {
            "not_run": 1,
            "project_ready": 1,
            "render_ready": 1,
            "script_error": 1,
            "stale_project": 1,
        }
        assert _status_by_id(report)["script_error"]["ae_error"] == "bad layer"
    finally:
        check_ae_manual_harnesses.REPO_ROOT = old_root


def test_manual_harness_status_treats_dataset_jsonl_as_source(tmp_path):
    old_root = check_ae_manual_harnesses.REPO_ROOT
    check_ae_manual_harnesses.REPO_ROOT = tmp_path
    try:
        record = _record("dataset_stale")
        source = tmp_path / record["source_repo_path"]
        source.parent.mkdir(parents=True, exist_ok=True)
        source.write_text("// source\n")
        dataset = tmp_path / "data/cases.jsonl"
        dataset.write_text("{}\n")
        _write_project(tmp_path, "dataset_stale", mtime=100)
        os.utime(source, (50, 50))
        os.utime(dataset, (200, 200))

        report = check_ae_manual_harnesses._build_report(
            records=[record],
            queue={"items": [_queue_item("dataset_stale")]},
            readiness={"render_debt": [{"case_id": "dataset_stale"}]},
            decisions={"render_missing"},
            harness_dir=tmp_path,
            dataset_path=dataset,
        )

        assert _status_by_id(report)["dataset_stale"]["status"] == "stale_project"
    finally:
        check_ae_manual_harnesses.REPO_ROOT = old_root


def test_manual_harness_status_markdown_lists_cases():
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
                "case_id": "missing_case",
                "decision": "render_missing",
                "ae_error": "",
            }
        ],
    }

    markdown = check_ae_manual_harnesses._markdown(report)

    assert "# Manual AE Harness Status" in markdown
    assert "| not_run | missing_case | render_missing | - |" in markdown


def _record(case_id):
    return {
        "case_id": case_id,
        "source_repo_path": f"data/{case_id}.jsx",
    }


def _queue_item(case_id):
    return {"case_id": case_id, "decision": "render_missing"}


def _case_dir(root, case_id):
    path = root / "artifacts/ae_live_checks" / case_id
    path.mkdir(parents=True, exist_ok=True)
    return path


def _write_case_report(root, case_id, text):
    (_case_dir(root, case_id) / "report.txt").write_text(text)


def _write_project(root, case_id, mtime):
    path = _case_dir(root, case_id) / "project.aep"
    path.write_text("project\n")
    os.utime(path, (mtime, mtime))


def _write_render(root, case_id, mtime):
    path = _case_dir(root, case_id) / "render.mp4"
    path.write_text("render\n")
    os.utime(path, (mtime, mtime))


def _status_by_id(report):
    return {case["case_id"]: case for case in report["cases"]}
