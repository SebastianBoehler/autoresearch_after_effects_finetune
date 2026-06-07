from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def _load_script(name):
    path = REPO_ROOT / "scripts" / f"{name}.py"
    spec = spec_from_file_location(name, path)
    module = module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


build_ae_manual_harnesses = _load_script("build_ae_manual_harnesses")
build_training_readiness_report = _load_script("build_training_readiness_report")
export_train_ready_dataset = _load_script("export_train_ready_dataset")
preflight_train_ready_training = _load_script("preflight_train_ready_training")


def test_training_readiness_report_prioritizes_absent_packs():
    records = {
        "ready": _record("ready", ["synthetic-v1", "title"], 1920, 1080),
        "missing_pack": _record(
            "missing_pack",
            ["synthetic-v9", "workflow-ui", "command-palette", "automation"],
            1920,
            1080,
        ),
        "missing_tag": _record("missing_tag", ["synthetic-v1", "reveal"], 1080, 1920),
    }
    queue = {
        "decision_counts": {"promote_rendered": 1, "render_missing": 2},
        "items": [
            _queue_item("ready", "promote_rendered", train_ready=True),
            _queue_item("missing_tag", "render_missing"),
            _queue_item("missing_pack", "render_missing"),
        ],
    }

    report = build_training_readiness_report._build_report(records, queue)

    assert report["train_ready_count"] == 1
    assert report["coverage_gaps"]["synthetic_packs"] == ["synthetic-v9"]
    assert report["coverage_unlocks"] == [
        {
            "synthetic_pack": "synthetic-v9",
            "case_id": "missing_pack",
            "decision": "render_missing",
            "priority_score": 170,
            "aspect_ratio": "landscape_16x9",
            "coverage_reasons": [
                "pack absent from train-ready: synthetic-v9",
                "web motif absent from train-ready: hud_interface",
                "web motif absent from train-ready: workflow_panels",
                "tag absent from train-ready: synthetic-v9",
                "tag absent from train-ready: workflow-ui",
                "tag absent from train-ready: command-palette",
                "tag absent from train-ready: automation",
            ],
        }
    ]
    assert report["render_debt"][0]["case_id"] == "missing_pack"
    assert report["aspect_ratios"]["excluded"] == {
        "landscape_16x9": 1,
        "vertical_9x16": 1,
    }


def test_training_readiness_report_boosts_web_motif_gaps():
    records = {
        "ready": _record("ready", ["synthetic-v1", "title"], 1920, 1080),
        "ordinary": _record("ordinary", ["synthetic-v1", "reveal"], 1920, 1080),
        "stale_music": _record("stale_music", ["synthetic-v1", "music", "visualizer"], 1080, 1080),
    }
    queue = {
        "items": [
            _queue_item("ready", "promote_rendered", train_ready=True),
            _queue_item("ordinary", "render_missing"),
            _queue_item("stale_music", "rerender_stale"),
        ]
    }

    report = build_training_readiness_report._build_report(records, queue)

    assert report["render_debt"][0]["case_id"] == "stale_music"
    assert report["render_debt"][0]["motif_gap_unlocks"] == ["audio_visualizer"]
    assert "web motif absent from train-ready: audio_visualizer" in report["render_debt"][0]["coverage_reasons"]


def test_manual_harness_targets_follow_readiness_priority_and_limit():
    records = [
        _record("low", ["synthetic-v1"], 1920, 1080),
        _record("high", ["synthetic-v9"], 1920, 1080),
    ]
    queue = {
        "items": [
            _queue_item("low", "render_missing"),
            _queue_item("high", "render_missing"),
        ]
    }
    readiness = {
        "render_debt": [
            {"case_id": "high", "priority_score": 130},
            {"case_id": "low", "priority_score": 80},
        ]
    }

    targets = build_ae_manual_harnesses._select_targets(
        records,
        queue,
        {"render_missing"},
        readiness,
        limit=1,
    )

    assert [target["case_id"] for target in targets] == ["high"]


def test_manual_harness_runner_executes_chunks_with_one_confirmation(tmp_path):
    chunks = [
        tmp_path / "manual_harness_01.jsx",
        tmp_path / "manual_harness_02.jsx",
    ]
    for path in chunks:
        path.write_text("// chunk\n")

    runner = build_ae_manual_harnesses._write_runner(chunks, tmp_path)
    script = build_ae_manual_harnesses._build_script([
        _record("case", ["synthetic-v1"], 1920, 1080)
    ])

    assert runner.name == "run_all_harnesses.jsx"
    assert "$.global.AEFT_SKIP_CONFIRM = true" in runner.read_text()
    assert "$.global.AEFT_SKIP_ALERT = true" in runner.read_text()
    assert "runner_report.txt" in runner.read_text()
    assert "writeLines(completed)" in runner.read_text()
    assert "$.evalFile(new File(scripts[i]))" in runner.read_text()
    assert "!$.global.AEFT_SKIP_CONFIRM && !confirm" in script
    assert "!$.global.AEFT_SKIP_ALERT" in script


def test_train_ready_export_carries_visual_metadata_and_counts_exclusions():
    records = {
        "ready": _record("ready", ["synthetic-v1"], 1080, 1080),
        "missing": _record("missing", ["synthetic-v9"], 1920, 1080),
    }
    queue = {
        "case_count": 2,
        "decision_counts": {"promote_rendered": 1, "render_missing": 1},
        "items": [
            {
                **_queue_item("ready", "promote_rendered", train_ready=True),
                "quality_score": 0.96,
                "warnings": [],
                "notes": ["steady_motion"],
                "motion_profile": "steady",
                "active_frame_ratio": 0.8,
                "longest_stall_ratio": 0.1,
                "render_path": "/tmp/ready.mp4",
                "contact_sheet_path": "/tmp/ready.png",
            },
            _queue_item("missing", "render_missing"),
        ],
    }

    selected = export_train_ready_dataset._selected_records(records, queue)
    manifest = export_train_ready_dataset._manifest(
        queue,
        selected,
        {"train": selected, "valid": [], "test": []},
    )

    assert selected[0]["visual_review_decision"] == "promote_rendered"
    assert selected[0]["contact_sheet_path"] == "/tmp/ready.png"
    assert manifest["case_count"] == 1
    assert manifest["aspect_ratios"] == {"square_1x1": 1}
    assert manifest["synthetic_pack_counts"] == {"synthetic-v1": 1}
    assert manifest["excluded_decision_counts"] == {"render_missing": 1}


def test_train_ready_export_strict_quality_excludes_weak_promotions():
    records = {
        "strong": _record("strong", ["synthetic-v1"], 1920, 1080),
        "weak": _record("weak", ["synthetic-v1"], 1920, 1080),
    }
    queue = {
        "items": [
            _visual_item("strong", quality_priority="pass"),
            _visual_item("weak", quality_priority="review", motion_profile="sparse"),
        ]
    }

    selected = export_train_ready_dataset._selected_records(
        records,
        queue,
        strict_quality=True,
    )
    manifest = export_train_ready_dataset._manifest(
        queue,
        selected,
        {"train": selected, "valid": [], "test": []},
        strict_quality=True,
    )

    assert [case["case_id"] for case in selected] == ["strong"]
    assert manifest["strict_quality"] is True
    assert manifest["excluded_weak_train_ready_count"] == 1


def test_training_preflight_validates_chat_splits(tmp_path):
    dataset_dir = tmp_path / "dataset"
    dataset_dir.mkdir()
    good = {
        "messages": [
            {"role": "system", "content": "sys"},
            {"role": "user", "content": "prompt"},
            {"role": "assistant", "content": "code"},
        ]
    }
    for split in ["train", "valid", "test"]:
        (dataset_dir / f"{split}.jsonl").write_text("{}\n" if split == "valid" else f"{_json(good)}\n")
    config = _config(dataset_dir)

    report = preflight_train_ready_training._preflight(config, dataset_dir)

    assert report["ok"] is False
    assert report["split_counts"] == {"train": 1, "valid": 1, "test": 1}
    assert "line 1: expected three chat messages" in report["issues"]
    assert report["train_command"][-1] == "--train"


def _record(case_id, tags, width, height):
    return {
        "case_id": case_id,
        "prompt": f"Create {case_id}",
        "completion": "app.beginUndoGroup('x'); app.project.items.addComp('x', 1, 1, 1, 1, 1); app.endUndoGroup();",
        "license": "MIT",
        "expected": {"width": width, "height": height},
        "tags": tags,
        "source_repo_path": f"data/synthetic/templates/{case_id}.jsx",
    }


def _queue_item(case_id, decision, train_ready=False):
    return {
        "case_id": case_id,
        "decision": decision,
        "train_ready": train_ready,
        "reasons": ["test"],
    }


def _visual_item(case_id, quality_priority="pass", motion_profile="steady"):
    return {
        **_queue_item(case_id, "promote_rendered", train_ready=True),
        "quality_score": 1.0,
        "quality_priority": quality_priority,
        "warnings": [],
        "notes": [],
        "motion_profile": motion_profile,
        "active_frame_ratio": 0.8,
        "longest_stall_ratio": 0.1,
        "render_path": f"/tmp/{case_id}.mp4",
        "contact_sheet_path": f"/tmp/{case_id}.png",
    }


def _json(payload):
    import json

    return json.dumps(payload)


def _config(dataset_dir):
    from after_effects_pipeline.types import (
        DatasetSourceConfig,
        ExperimentConfig,
        TrainConfig,
    )

    return ExperimentConfig(
        name="test",
        base_model="model",
        source_dataset=DatasetSourceConfig(path=str(dataset_dir / "cases.jsonl")),
        dataset_dir=str(dataset_dir),
        adapter_path="adapter",
        eval_output_path="eval.json",
        train=TrainConfig(val_batches=1, iters=2),
    )
