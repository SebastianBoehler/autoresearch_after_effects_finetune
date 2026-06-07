from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys
from types import SimpleNamespace


REPO_ROOT = Path(__file__).resolve().parents[1]


def _load_script(name):
    path = REPO_ROOT / "scripts" / f"{name}.py"
    spec = spec_from_file_location(name, path)
    module = module_from_spec(spec)
    assert spec and spec.loader
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


refresh_after_manual_harnesses = _load_script("refresh_after_manual_harnesses")


def test_refresh_steps_cover_post_harness_training_flow():
    args = SimpleNamespace(
        config=Path("configs/source.json"),
        train_ready_config=Path("configs/train-ready.json"),
        high_quality_config=Path("configs/high-quality.json"),
        frame_step=5,
        render_status_report=None,
        render_statuses=["project_ready", "render_stale"],
        skip_render=False,
        run_play_session=False,
    )

    steps = refresh_after_manual_harnesses._build_steps(args)

    assert [step.name for step in steps] == [
        "check manual AE harness status",
        "check motif-gap AE harness status",
        "render queued AE projects",
        "analyze rendered frames",
        "build contact sheets",
        "audit dataset coverage",
        "refresh render review queue",
        "build manual review template",
        "audit rendered sample progression",
        "audit animation anatomy",
        "audit source and train-ready diversity",
        "build visual review dashboard",
        "export train-ready dataset",
        "export high-quality dataset",
        "audit rendered sample overlap",
        "audit train-ready split safety",
        "build training readiness report",
        "audit web inspiration coverage",
        "build AE play-session harnesses",
        "audit source motion coverage",
        "audit source animation quality",
        "audit source animation patterns",
        "audit overlap remediation",
        "audit render issue remediation",
        "audit source capability diversity",
        "build capability-gap AE harnesses",
        "check capability-gap AE harness status",
        "build render unlock plan",
        "build quality gap matrix",
        "build render-unlock AE harnesses",
        "check render-unlock AE harness status",
        "build render unlock batch status",
        "build manual render briefing",
        "audit render unlock completion",
        "build train-ready MLX splits",
        "preflight train-ready training",
        "build high-quality MLX splits",
        "preflight high-quality training",
        "build dataset quality gate",
    ]
    assert steps[0].command[1].endswith("scripts/check_ae_manual_harnesses.py")
    assert steps[1].command[1].endswith("scripts/check_motif_gap_harnesses.py")
    assert steps[2].command[1].endswith("scripts/render_aep_queue.py")
    assert steps[3].command[-4:] == [
        "--config",
        "configs/source.json",
        "--frame-step",
        "5",
    ]
    assert steps[4].command[-4:] == [
        "--config",
        "configs/source.json",
        "--frame-step",
        "5",
    ]
    assert steps[7].command[1].endswith("scripts/build_manual_review_template.py")
    assert steps[8].command[1].endswith("scripts/build_render_progression_audit.py")
    assert steps[9].command[1].endswith("scripts/build_animation_anatomy_audit.py")
    assert steps[10].command[1:3] == ["-m", "after_effects_pipeline.cli"]
    assert steps[10].command[3] == "diversity-audit"
    assert steps[11].command[1].endswith("scripts/build_visual_review_dashboard.py")
    assert "--strict-quality" in steps[13].command
    assert steps[14].command[1].endswith("scripts/build_render_overlap_audit.py")
    assert steps[15].command[1].endswith("scripts/build_split_safety_audit.py")
    assert steps[17].command[1].endswith("scripts/build_inspiration_coverage_audit.py")
    assert steps[18].command[1].endswith("scripts/build_ae_play_session_harnesses.py")
    assert steps[19].command[1].endswith("scripts/build_source_motion_audit.py")
    assert steps[20].command[1].endswith("scripts/build_source_animation_quality_audit.py")
    assert steps[21].command[1].endswith("scripts/build_source_pattern_audit.py")
    assert steps[22].command[1].endswith("scripts/build_overlap_remediation_audit.py")
    assert steps[23].command[1].endswith("scripts/build_render_issue_remediation_audit.py")
    assert steps[24].command[1].endswith("scripts/build_source_capability_audit.py")
    assert steps[25].command[1].endswith("scripts/build_capability_gap_harnesses.py")
    assert steps[26].command[1].endswith("scripts/check_capability_gap_harnesses.py")
    assert steps[27].command[1].endswith("scripts/build_render_unlock_plan.py")
    assert steps[28].command[1].endswith("scripts/build_quality_gap_matrix.py")
    assert steps[29].command[1].endswith("scripts/build_render_unlock_harnesses.py")
    assert steps[30].command[1].endswith("scripts/check_render_unlock_harnesses.py")
    assert steps[31].command[1].endswith("scripts/build_render_unlock_batch_status.py")
    assert steps[32].command[1].endswith("scripts/build_manual_render_briefing.py")
    assert steps[33].command[1].endswith("scripts/build_render_unlock_completion_audit.py")
    assert steps[34].command[-1] == "configs/train-ready.json"
    assert steps[36].command[-1] == "configs/high-quality.json"
    assert steps[37].command[2:4] == ["--config", "configs/high-quality.json"]
    assert steps[-1].command[1].endswith("scripts/build_dataset_quality_gate.py")


def test_refresh_steps_can_skip_render():
    args = SimpleNamespace(
        config=Path("configs/source.json"),
        train_ready_config=Path("configs/train-ready.json"),
        high_quality_config=Path("configs/high-quality.json"),
        frame_step=3,
        render_status_report=None,
        render_statuses=["project_ready", "render_stale"],
        skip_render=True,
        run_play_session=False,
    )

    steps = refresh_after_manual_harnesses._build_steps(args)

    assert [step.name for step in steps[:2]] == [
        "check manual AE harness status",
        "check motif-gap AE harness status",
    ]
    assert steps[2].name == "analyze rendered frames"


def test_refresh_can_limit_rendering_to_status_report():
    args = SimpleNamespace(
        config=Path("configs/source.json"),
        train_ready_config=Path("configs/train-ready.json"),
        high_quality_config=Path("configs/high-quality.json"),
        frame_step=3,
        render_status_report=Path("status.json"),
        render_statuses=["project_ready"],
        skip_render=False,
        run_play_session=False,
    )

    steps = refresh_after_manual_harnesses._build_steps(args)

    assert steps[2].command == [
        sys.executable,
        str(REPO_ROOT / "scripts/render_aep_queue.py"),
        "--status-report",
        "status.json",
        "--statuses",
        "project_ready",
    ]


def test_refresh_can_run_play_session_after_building_play_harnesses():
    args = SimpleNamespace(
        config=Path("configs/source.json"),
        train_ready_config=Path("configs/train-ready.json"),
        high_quality_config=Path("configs/high-quality.json"),
        frame_step=3,
        render_status_report=None,
        render_statuses=["project_ready", "render_stale"],
        skip_render=True,
        run_play_session=True,
    )

    steps = refresh_after_manual_harnesses._build_steps(args)
    names = [step.name for step in steps]

    assert names.index("run AE play-session harnesses") == (
        names.index("build AE play-session harnesses") + 1
    )
    run_step = steps[names.index("run AE play-session harnesses")]
    assert run_step.command[1].endswith("scripts/run_ae_play_session_harnesses.py")


def test_refresh_dry_run_does_not_call_runner():
    calls = []
    steps = [refresh_after_manual_harnesses.Step("first", ["python", "one.py"])]

    results = refresh_after_manual_harnesses._run_steps(
        steps,
        dry_run=True,
        runner=lambda *args, **kwargs: calls.append((args, kwargs)),
    )

    assert calls == []
    assert results == [{"step": "first", "returncode": 0, "dry_run": True}]


def test_refresh_stops_on_first_failure():
    calls = []
    steps = [
        refresh_after_manual_harnesses.Step("first", ["python", "one.py"]),
        refresh_after_manual_harnesses.Step("second", ["python", "two.py"]),
        refresh_after_manual_harnesses.Step("third", ["python", "three.py"]),
    ]

    def runner(command, cwd, check):
        calls.append((command, cwd, check))
        return SimpleNamespace(returncode=1 if len(calls) == 2 else 0)

    results = refresh_after_manual_harnesses._run_steps(
        steps,
        dry_run=False,
        runner=runner,
    )

    assert [call[0] for call in calls] == [
        ["python", "one.py"],
        ["python", "two.py"],
    ]
    assert [result["returncode"] for result in results] == [0, 1]
