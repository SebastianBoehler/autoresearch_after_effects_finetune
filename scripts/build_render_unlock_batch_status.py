from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

from after_effects_pipeline.utils import write_json

REPO_ROOT = Path(__file__).resolve().parents[1]
RENDERABLE_STATUSES = {"project_ready", "render_stale"}


def main() -> None:
    args = _parse_args()
    report = _build_report(
        plan=_load_json(args.plan),
        harness_status=_load_json(args.harness_status),
        runner_status=_load_json(args.runner_status),
    )
    write_json(args.output, report)
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.write_text(_markdown(report, args.output))
    print(report["summary"])


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--plan", type=Path, default=REPO_ROOT / "artifacts/visual_analysis/render-unlock-plan.json")
    parser.add_argument("--harness-status", type=Path, default=REPO_ROOT / "artifacts/ae_live_checks/_manual_harnesses_render_unlocks/status.json")
    parser.add_argument("--runner-status", type=Path, default=REPO_ROOT / "artifacts/ae_live_checks/_manual_harnesses_render_unlocks/run-status.json")
    parser.add_argument("--output", type=Path, default=REPO_ROOT / "artifacts/visual_analysis/render-unlock-batch-status.json")
    parser.add_argument("--markdown-output", type=Path, default=REPO_ROOT / "artifacts/visual_analysis/render-unlock-batch-status.md")
    return parser.parse_args()


def _build_report(
    *,
    plan: dict[str, Any],
    harness_status: dict[str, Any],
    runner_status: dict[str, Any] | None = None,
) -> dict[str, Any]:
    status_by_id = {case["case_id"]: case for case in harness_status.get("cases", [])}
    cases = []
    for rank, target in enumerate(plan.get("greedy_unlock_sequence", []), start=1):
        status = status_by_id.get(target["case_id"], {})
        cases.append(
            {
                **status,
                "case_id": target["case_id"],
                "status": status.get("status", "missing_status"),
                "next_action": _next_action(status.get("status", "missing_status")),
                "decision": target.get("decision", status.get("decision", "")),
                "unlock_rank": rank,
                "unlock_score": target.get("score", 0),
                "new_unlocks": target.get("new_unlocks", []),
                "coverage_keys": target.get("coverage_keys", []),
                "source_repo_path": target.get("source_repo_path", ""),
            }
        )
    status_counts = Counter(case["status"] for case in cases)
    action_counts = Counter(case["next_action"] for case in cases)
    renderable = [case for case in cases if case["status"] in RENDERABLE_STATUSES]
    summary = {
        "target_count": len(cases),
        "renderable_count": len(renderable),
        "status_counts": dict(sorted(status_counts.items())),
        "action_counts": dict(sorted(action_counts.items())),
        "batch_stage": _batch_stage(action_counts, runner_status or {}),
        "covered_requirement_count": plan.get("summary", {}).get("covered_requirement_count", 0),
        "requirement_count": plan.get("summary", {}).get("requirement_count", 0),
    }
    blocker = _blocker(runner_status or {})
    if blocker:
        summary["blocker"] = blocker
    return {
        "summary": summary,
        "cases": cases,
    }


def _markdown(report: dict[str, Any], output: Path) -> str:
    summary = report["summary"]
    prepare_command = "uv run python scripts/run_ae_render_unlock_harnesses.py"
    render_command = (
        "uv run python scripts/refresh_after_manual_harnesses.py "
        f"--render-status-report {output} --render-statuses project_ready render_stale"
    )
    lines = [
        "# Render Unlock Batch Status",
        "",
        f"- targets: {summary['target_count']}",
        f"- renderable now: {summary['renderable_count']}",
        f"- requirements covered by plan: {summary['covered_requirement_count']}/{summary['requirement_count']}",
        f"- batch stage: {summary['batch_stage']}",
        f"- status counts: {_inline_counts(summary['status_counts'])}",
        f"- action counts: {_inline_counts(summary['action_counts'])}",
    ]
    if summary.get("blocker"):
        lines.extend([
            f"- blocker: {summary['blocker']['reason']}",
            f"- blocker detail: {summary['blocker']['detail']}",
        ])
    lines.extend([
        "",
        "## Next Commands",
        "",
        "```bash",
        prepare_command,
        render_command,
        "```",
        "",
        "## Targets",
        "",
        "| rank | status | next action | case | decision | score | new unlocks |",
        "| ---: | --- | --- | --- | --- | ---: | --- |",
    ])
    for case in report["cases"]:
        lines.append(
            f"| {case['unlock_rank']} | {case['status']} | {case['next_action']} | {case['case_id']} | "
            f"{case['decision']} | {case['unlock_score']} | "
            f"{', '.join(case['new_unlocks']) or '-'} |"
        )
    return "\n".join(lines) + "\n"


def _next_action(status: str) -> str:
    if status in RENDERABLE_STATUSES:
        return "render"
    if status in {"not_run", "missing_project", "missing_status"}:
        return "create_project"
    if status == "stale_project":
        return "refresh_project"
    if status in {"rendered", "train_ready"}:
        return "review"
    return "inspect"


def _batch_stage(action_counts: Counter[str], runner_status: dict[str, Any]) -> str:
    if _blocker(runner_status) and (action_counts.get("create_project") or action_counts.get("refresh_project")):
        return "blocked_prepare_projects"
    if action_counts.get("render"):
        return "render_ready"
    if action_counts.get("create_project") or action_counts.get("refresh_project"):
        return "prepare_projects"
    if action_counts.get("inspect"):
        return "inspect_status"
    return "review_outputs"


def _blocker(runner_status: dict[str, Any]) -> dict[str, str]:
    summary = runner_status.get("summary", runner_status)
    if not summary or summary.get("ok") is not False:
        return {}
    reason = str(summary.get("reason") or "runner_failed")
    return {"reason": reason, "detail": _blocker_detail(reason, summary)}


def _blocker_detail(reason: str, runner_status: dict[str, Any]) -> str:
    if reason == "scripting_access_disabled":
        return (
            "After Effects file/network scripting is not enabled "
            f"(debugger={runner_status.get('javascript_debugger')}, "
            f"file_network={runner_status.get('script_file_network_access')})."
        )
    if reason == "missing_runner_report":
        return "After Effects accepted the runner command but did not write runner_report.txt; DoScriptFile may not have executed."
    if reason == "runner_chunk_errors":
        return f"Render-unlock runner reported {runner_status.get('error_chunks', 'unknown')} chunk error(s)."
    if reason == "incomplete_runner_report":
        return (
            "After Effects wrote an incomplete runner_report.txt "
            f"({runner_status.get('completed_chunks', 0)} completed chunk(s))."
        )
    return f"Render-unlock runner failed with return code {runner_status.get('returncode', 'unknown')}."


def _inline_counts(counts: dict[str, int]) -> str:
    return ", ".join(f"{key}={value}" for key, value in sorted(counts.items())) or "-"


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text()) if path.exists() else {}


if __name__ == "__main__":
    main()
