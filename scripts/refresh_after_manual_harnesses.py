from __future__ import annotations

import argparse
import shlex
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

REPO_ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class Step:
    name: str
    command: list[str]


def main() -> None:
    args = _parse_args()
    results = _run_steps(_build_steps(args), dry_run=args.dry_run)
    failed = next((result for result in results if result["returncode"] != 0), None)
    if failed:
        raise SystemExit(failed["returncode"] or 1)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=Path("configs/lfm25_8b_a1b_after_effects.json"))
    parser.add_argument("--train-ready-config", type=Path, default=Path("configs/lfm25_8b_a1b_after_effects_train_ready.json"))
    parser.add_argument("--high-quality-config", type=Path, default=Path("configs/lfm25_8b_a1b_after_effects_high_quality.json"))
    parser.add_argument("--frame-step", type=int, default=3)
    parser.add_argument("--render-status-report", type=Path)
    parser.add_argument("--render-statuses", nargs="+", default=["project_ready", "render_stale"])
    parser.add_argument("--skip-render", action="store_true")
    parser.add_argument("--run-play-session", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def _build_steps(args: argparse.Namespace) -> list[Step]:
    python = sys.executable
    steps = [
        Step(
            "check manual AE harness status",
            [python, str(REPO_ROOT / "scripts/check_ae_manual_harnesses.py")],
        ),
        Step(
            "check motif-gap AE harness status",
            [python, str(REPO_ROOT / "scripts/check_motif_gap_harnesses.py")],
        )
    ]
    if not args.skip_render:
        command = [python, str(REPO_ROOT / "scripts/render_aep_queue.py")]
        if args.render_status_report:
            command.extend([
                "--status-report",
                str(args.render_status_report),
                "--statuses",
                *args.render_statuses,
            ])
        steps.append(
            Step(
                "render queued AE projects",
                command,
            )
        )
    steps.extend(
        [
            Step(
                "analyze rendered frames",
                [
                    python,
                    "-m",
                    "after_effects_pipeline.cli",
                    "analyze-renders",
                    "--config",
                    str(args.config),
                    "--frame-step",
                    str(args.frame_step),
                ],
            ),
            Step(
                "build contact sheets",
                [
                    python,
                    "-m",
                    "after_effects_pipeline.cli",
                    "contact-sheets",
                    "--config",
                    str(args.config),
                    "--frame-step",
                    str(args.frame_step),
                ],
            ),
            Step(
                "audit dataset coverage",
                [
                    python,
                    "-m",
                    "after_effects_pipeline.cli",
                    "audit-dataset",
                    "--config",
                    str(args.config),
                ],
            ),
            Step(
                "refresh render review queue",
                [
                    python,
                    "-m",
                    "after_effects_pipeline.cli",
                    "render-review-queue",
                    "--config",
                    str(args.config),
                ],
            ),
            Step("build manual review template", [python, str(REPO_ROOT / "scripts/build_manual_review_template.py")]),
            Step(
                "audit rendered sample progression",
                [python, str(REPO_ROOT / "scripts/build_render_progression_audit.py")],
            ),
            Step("audit animation anatomy", [python, str(REPO_ROOT / "scripts/build_animation_anatomy_audit.py")]),
            Step(
                "audit source and train-ready diversity",
                [
                    python,
                    "-m",
                    "after_effects_pipeline.cli",
                    "diversity-audit",
                    "--config",
                    str(args.config),
                ],
            ),
            Step(
                "build visual review dashboard",
                [python, str(REPO_ROOT / "scripts/build_visual_review_dashboard.py")],
            ),
            Step(
                "export train-ready dataset",
                [python, str(REPO_ROOT / "scripts/export_train_ready_dataset.py")],
            ),
            Step(
                "export high-quality dataset",
                [
                    python,
                    str(REPO_ROOT / "scripts/export_train_ready_dataset.py"),
                    "--strict-quality",
                    "--output-dir",
                    "artifacts/datasets/after-effects-high-quality",
                ],
            ),
            Step(
                "audit rendered sample overlap",
                [python, str(REPO_ROOT / "scripts/build_render_overlap_audit.py")],
            ),
            Step(
                "audit train-ready split safety",
                [python, str(REPO_ROOT / "scripts/build_split_safety_audit.py")],
            ),
            Step(
                "build training readiness report",
                [python, str(REPO_ROOT / "scripts/build_training_readiness_report.py")],
            ),
            Step(
                "audit web inspiration coverage",
                [python, str(REPO_ROOT / "scripts/build_inspiration_coverage_audit.py")],
            ),
            Step(
                "build AE play-session harnesses",
                [python, str(REPO_ROOT / "scripts/build_ae_play_session_harnesses.py")],
            ),
            *(
                [
                    Step(
                        "run AE play-session harnesses",
                        [python, str(REPO_ROOT / "scripts/run_ae_play_session_harnesses.py")],
                    )
                ]
                if args.run_play_session
                else []
            ),
            Step("audit source motion coverage", [python, str(REPO_ROOT / "scripts/build_source_motion_audit.py")]),
            Step("audit source animation quality", [python, str(REPO_ROOT / "scripts/build_source_animation_quality_audit.py")]),
            Step("audit source animation patterns", [python, str(REPO_ROOT / "scripts/build_source_pattern_audit.py")]),
            Step("audit overlap remediation", [python, str(REPO_ROOT / "scripts/build_overlap_remediation_audit.py")]),
            Step("audit render issue remediation", [python, str(REPO_ROOT / "scripts/build_render_issue_remediation_audit.py")]),
            Step("audit source capability diversity", [python, str(REPO_ROOT / "scripts/build_source_capability_audit.py")]),
            Step(
                "build capability-gap AE harnesses",
                [python, str(REPO_ROOT / "scripts/build_capability_gap_harnesses.py")],
            ),
            Step(
                "check capability-gap AE harness status",
                [python, str(REPO_ROOT / "scripts/check_capability_gap_harnesses.py")],
            ),
            Step(
                "build render unlock plan",
                [python, str(REPO_ROOT / "scripts/build_render_unlock_plan.py")],
            ),
            Step("build quality gap matrix", [python, str(REPO_ROOT / "scripts/build_quality_gap_matrix.py")]),
            Step(
                "build render-unlock AE harnesses",
                [python, str(REPO_ROOT / "scripts/build_render_unlock_harnesses.py")],
            ),
            Step(
                "check render-unlock AE harness status",
                [python, str(REPO_ROOT / "scripts/check_render_unlock_harnesses.py")],
            ),
            Step(
                "build render unlock batch status",
                [python, str(REPO_ROOT / "scripts/build_render_unlock_batch_status.py")],
            ),
            Step("build manual render briefing", [python, str(REPO_ROOT / "scripts/build_manual_render_briefing.py")]),
            Step(
                "audit render unlock completion",
                [python, str(REPO_ROOT / "scripts/build_render_unlock_completion_audit.py")],
            ),
            Step(
                "build train-ready MLX splits",
                [
                    python,
                    "-m",
                    "after_effects_pipeline.cli",
                    "build-dataset",
                    "--config",
                    str(args.train_ready_config),
                ],
            ),
            Step(
                "preflight train-ready training",
                [python, str(REPO_ROOT / "scripts/preflight_train_ready_training.py")],
            ),
            Step(
                "build high-quality MLX splits",
                [
                    python,
                    "-m",
                    "after_effects_pipeline.cli",
                    "build-dataset",
                    "--config",
                    str(args.high_quality_config),
                ],
            ),
            Step(
                "preflight high-quality training",
                [
                    python,
                    str(REPO_ROOT / "scripts/preflight_train_ready_training.py"),
                    "--config",
                    str(args.high_quality_config),
                    "--output",
                    "artifacts/datasets/lfm25-8b-a1b-after-effects-high-quality/training-preflight.json",
                    "--markdown-output",
                    "artifacts/datasets/lfm25-8b-a1b-after-effects-high-quality/training-preflight.md",
                ],
            ),
            Step(
                "build dataset quality gate",
                [python, str(REPO_ROOT / "scripts/build_dataset_quality_gate.py")],
            ),
        ]
    )
    return steps


def _run_steps(
    steps: list[Step],
    *,
    dry_run: bool,
    runner: Callable[..., Any] = subprocess.run,
) -> list[dict[str, Any]]:
    results = []
    for step in steps:
        print(f"==> {step.name}")
        print(_shell_command(step.command))
        if dry_run:
            results.append({"step": step.name, "returncode": 0, "dry_run": True})
            continue
        result = runner(step.command, cwd=REPO_ROOT, check=False)
        returncode = int(getattr(result, "returncode", 1))
        results.append({"step": step.name, "returncode": returncode, "dry_run": False})
        if returncode != 0:
            print(f"stopped after failed step: {step.name}")
            break
    return results


def _shell_command(command: list[str]) -> str:
    return " ".join(shlex.quote(part) for part in command)


if __name__ == "__main__":
    main()
