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


build_dataset_quality_gate = _load_script("build_dataset_quality_gate")


def _play_ok(script_count=1):
    return {
        "summary": {
            "ok": True,
            "script_count": script_count,
            "completed_chunks": script_count,
            "failed_chunks": 0,
        }
    }


def _complete_gate(**overrides):
    kwargs = {
        "queue": {"case_count": 1, "items": []},
        "render_analysis": {"summary": {"case_count": 1}},
        "dataset_audit": {"actionable_render_warning_count": 0},
        "train_ready_manifest": {"case_count": 1},
        "readiness_report": {
            "case_count": 1,
            "train_ready_count": 1,
            "coverage_gaps": {"synthetic_packs": []},
            "render_debt": [],
        },
        "harness_status": {
            "summary": {
                "runner_report_exists": True,
                "status_counts": {"render_ready": 1},
            }
        },
        "training_preflight": {"ok": True, "issues": []},
        "high_quality_manifest": {"case_count": 1},
        "high_quality_preflight": {"ok": True, "issues": []},
        "source_motion_audit": {"summary": {"cases_with_issues": 0}},
        "source_animation_quality": {"summary": {"cases_with_issues": 0}},
        "source_capability_audit": {
            "summary": {
                "core_gap_count": 0,
                "case_issue_count": 0,
                "train_ready_core_gap_count": 0,
            }
        },
        "render_progression": {"summary": {"train_ready_issue_count": 0}},
        "split_safety": {"summary": {"ok": True}},
        "play_session_status": _play_ok(),
    }
    kwargs.update(overrides)
    return build_dataset_quality_gate._build_gate(**kwargs)


def test_quality_gate_distinguishes_trainable_subset_from_full_ready():
    gate = build_dataset_quality_gate._build_gate(
        queue={
            "case_count": 3,
            "items": [
                {
                    "case_id": "weak_ready",
                    "train_ready": True,
                    "quality_priority": "review",
                    "warnings": [],
                    "motion_profile": "sparse",
                    "longest_stall_ratio": 0.2,
                }
            ],
        },
        render_analysis={"summary": {"case_count": 2}},
        dataset_audit={"actionable_render_warning_count": 0},
        train_ready_manifest={"case_count": 2},
        readiness_report={
            "case_count": 3,
            "train_ready_count": 2,
            "coverage_gaps": {"synthetic_packs": ["synthetic-v9"]},
            "coverage_unlocks": [
                {"synthetic_pack": "synthetic-v9", "case_id": "missing"}
            ],
            "render_debt": [{"case_id": "missing"}],
        },
        harness_status={
            "summary": {
                "runner_report_exists": False,
                "status_counts": {"not_run": 1},
            }
        },
        training_preflight={"ok": True, "issues": []},
        high_quality_manifest={"case_count": 1},
        high_quality_preflight={"ok": True, "issues": []},
        source_motion_audit={"summary": {"cases_with_issues": 0}},
        source_capability_audit={
            "summary": {"core_gap_count": 0, "case_issue_count": 0, "train_ready_core_gap_count": 0}
        },
        render_progression={"summary": {"train_ready_issue_count": 0}},
        split_safety={"summary": {"ok": True}},
        inspiration_coverage={"summary": {"train_ready_gap_count": 2}},
        play_session_status=_play_ok(),
    )

    assert gate["summary"]["technical_trainable_subset"] is True
    assert gate["summary"]["high_quality_trainable_subset"] is True
    assert gate["summary"]["full_dataset_ready"] is False
    assert gate["summary"]["failed_checks"] == [
        "no_weak_train_ready_cases",
        "all_source_cases_train_ready",
        "no_render_debt",
        "all_synthetic_packs_train_ready",
        "web_inspiration_motifs_train_ready",
        "all_manual_harness_targets_renderable",
    ]
    assert "First pack-unlock render targets: synthetic-v9=missing" in gate["next_actions"]
    assert "_manual_harnesses_motif_gaps/run_all_harnesses.jsx" in " ".join(gate["next_actions"])
    assert "No runner_report.txt found" in gate["next_actions"][-1]


def test_quality_gate_passes_when_all_artifacts_are_complete():
    gate = build_dataset_quality_gate._build_gate(
        queue={
            "case_count": 2,
            "items": [
                {
                    "case_id": "ready",
                    "train_ready": True,
                    "quality_priority": "pass",
                    "warnings": [],
                    "motion_profile": "steady",
                    "longest_stall_ratio": 0.1,
                }
            ],
        },
        render_analysis={"summary": {"case_count": 2}},
        dataset_audit={"actionable_render_warning_count": 0},
        train_ready_manifest={"case_count": 2},
        readiness_report={
            "case_count": 2,
            "train_ready_count": 2,
            "coverage_gaps": {"synthetic_packs": []},
            "render_debt": [],
        },
        harness_status={
            "summary": {
                "runner_report_exists": True,
                "status_counts": {"render_ready": 2},
            }
        },
        training_preflight={"ok": True, "issues": []},
        high_quality_manifest={"case_count": 2},
        high_quality_preflight={"ok": True, "issues": []},
        source_motion_audit={"summary": {"cases_with_issues": 0}},
        source_capability_audit={
            "summary": {"core_gap_count": 0, "case_issue_count": 0, "train_ready_core_gap_count": 0}
        },
        render_progression={"summary": {"train_ready_issue_count": 0}},
        split_safety={"summary": {"ok": True}},
        play_session_status=_play_ok(script_count=2),
    )

    assert gate["summary"] == {
            "technical_trainable_subset": True,
            "high_quality_trainable_subset": True,
        "full_dataset_ready": True,
        "failed_checks": [],
    }
    assert gate["next_actions"] == []


def test_quality_gate_fails_when_source_motion_audit_has_issues():
    gate = _complete_gate(
        source_motion_audit={"summary": {"cases_with_issues": 2}},
    )

    assert "no_source_motion_audit_issues" in gate["summary"]["failed_checks"]


def test_quality_gate_fails_when_play_session_harnesses_have_not_run():
    gate = _complete_gate(
        play_session_status={
            "summary": {
                "ok": False,
                "script_count": 2,
                "completed_chunks": 1,
                "failed_chunks": 1,
            }
        },
    )

    assert "ae_play_session_harnesses_ok" in gate["summary"]["failed_checks"]
    assert "run_ae_play_session_harnesses.py" in " ".join(gate["next_actions"])


def test_quality_gate_fails_when_source_capability_audit_has_gaps():
    gate = _complete_gate(
        source_capability_audit={
            "summary": {"core_gap_count": 1, "case_issue_count": 0, "train_ready_core_gap_count": 0}
        }
    )

    assert "source_capability_diversity_ok" in gate["summary"]["failed_checks"]
    assert "AE capability gaps" in " ".join(gate["next_actions"])
    gate = _complete_gate(
        source_capability_audit={
            "summary": {"core_gap_count": 0, "case_issue_count": 0, "train_ready_core_gap_count": 1},
            "train_ready_gap_unlocks": [{"capability": "camera_3d", "case_ids": ["geo"]}],
        }
    )
    assert "train_ready_capability_diversity_ok" in gate["summary"]["failed_checks"]
    assert "camera_3d=geo" in " ".join(gate["next_actions"])


def test_quality_gate_fails_when_source_animation_quality_has_issues():
    gate = _complete_gate(
        source_animation_quality={"summary": {"cases_with_issues": 1}},
    )

    assert "no_source_animation_quality_issues" in gate["summary"]["failed_checks"]
    assert "Fix source-animation-quality issues" in " ".join(gate["next_actions"])


def test_quality_gate_fails_when_train_ready_animation_patterns_have_gaps():
    gate = _complete_gate(
        source_pattern_audit={
            "summary": {"train_ready_pattern_gap_count": 1},
            "train_ready_pattern_gaps": [{"pattern": "feature:markers", "case_ids": ["sound"]}],
        },
    )

    assert "train_ready_animation_patterns_ok" in gate["summary"]["failed_checks"]
    assert "feature:markers=sound" in " ".join(gate["next_actions"])


def test_quality_gate_fails_when_split_safety_has_issues():
    gate = _complete_gate(
        split_safety={"summary": {"ok": False, "issue_count": 1}},
    )

    assert "train_ready_split_safety_ok" in gate["summary"]["failed_checks"]
    assert "split-safety issues" in " ".join(gate["next_actions"])


def test_quality_gate_fails_when_train_ready_progression_has_issues():
    gate = _complete_gate(
        render_progression={
            "summary": {"train_ready_issue_count": 1},
            "train_ready_issue_cases": ["weak_render"],
        },
    )

    assert "no_train_ready_render_progression_issues" in gate["summary"]["failed_checks"]
    assert "train-ready render progression" in " ".join(gate["next_actions"])


def test_quality_gate_markdown_lists_failed_checks():
    gate = {
        "summary": {
            "technical_trainable_subset": True,
            "high_quality_trainable_subset": True,
            "full_dataset_ready": False,
            "failed_checks": ["no_render_debt"],
        },
        "checks": [
            {
                "name": "no_render_debt",
                "passed": False,
                "detail": {"render_debt": 1},
            }
        ],
        "next_actions": ["Render missing case"],
    }

    markdown = build_dataset_quality_gate._markdown(gate)

    assert "# Dataset Quality Gate" in markdown
    assert "| False | no_render_debt | {\"render_debt\": 1} |" in markdown
    assert "- Render missing case" in markdown
