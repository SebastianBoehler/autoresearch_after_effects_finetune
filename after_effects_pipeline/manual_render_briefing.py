from __future__ import annotations

from typing import Any


def build_manual_render_briefing(
    *,
    quality_gap_matrix: dict[str, Any],
    batch_status: dict[str, Any],
    runner_path: str,
) -> dict[str, Any]:
    status_by_id = {item["case_id"]: item for item in batch_status.get("cases", [])}
    priority_items = [
        _target(item, status_by_id[item["case_id"]])
        for item in quality_gap_matrix.get("items", [])
        if item["case_id"] in status_by_id
    ]
    first_pass = [item for item in priority_items if item["action"] == "render_unlock_archetype_gap"]
    second_pass = [item for item in priority_items if item["action"] != "render_unlock_archetype_gap"]
    summary = batch_status.get("summary", {})
    return {
        "summary": {
            "target_count": len(priority_items),
            "first_pass_count": len(first_pass),
            "second_pass_count": len(second_pass),
            "create_project_count": sum(item["next_action"] == "create_project" for item in priority_items),
            "refresh_project_count": sum(item["next_action"] == "refresh_project" for item in priority_items),
            "renderable_count": int(summary.get("renderable_count", 0)),
            "batch_stage": summary.get("batch_stage", ""),
            "blocker": summary.get("blocker", {}),
        },
        "runner_path": runner_path,
        "first_pass_targets": first_pass,
        "second_pass_targets": second_pass,
        "post_run_commands": [
            "uv run python scripts/check_render_unlock_harnesses.py",
            "uv run python scripts/build_render_unlock_batch_status.py",
            "uv run python scripts/refresh_after_manual_harnesses.py --render-status-report artifacts/visual_analysis/render-unlock-batch-status.json --render-statuses project_ready render_stale",
        ],
    }


def render_manual_render_briefing_markdown(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# Manual AE Render Briefing",
        "",
        "Use this when AE can play compositions but AppleScript/DoScriptFile does not write runner reports.",
        "",
        "## Summary",
        "",
        f"- targets: {summary['target_count']}",
        f"- first-pass archetype targets: {summary['first_pass_count']}",
        f"- second-pass requirement targets: {summary['second_pass_count']}",
        f"- create projects: {summary['create_project_count']}",
        f"- refresh projects: {summary['refresh_project_count']}",
        f"- renderable now: {summary['renderable_count']}",
        f"- batch stage: {summary['batch_stage'] or '-'}",
        f"- blocker: {summary.get('blocker', {}).get('reason', '-')}",
        "",
        "## Run In After Effects",
        "",
        "File > Scripts > Run Script File:",
        "",
        f"`{payload['runner_path']}`",
        "",
        "## First Pass",
        "",
    ]
    lines.extend(_table(payload["first_pass_targets"]))
    lines.extend(["", "## Second Pass", ""])
    lines.extend(_table(payload["second_pass_targets"]))
    lines.extend(["", "## After Runner Succeeds", ""])
    lines.extend(f"```bash\n{command}\n```" for command in payload["post_run_commands"])
    return "\n".join(lines) + "\n"


def _target(item: dict[str, Any], status: dict[str, Any]) -> dict[str, Any]:
    return {
        "case_id": item["case_id"],
        "priority": item["priority"],
        "action": item["action"],
        "next_action": status.get("next_action", ""),
        "status": status.get("status", ""),
        "decision": item["decision"],
        "archetype": item.get("archetype", ""),
        "new_unlocks": item.get("new_unlocks", []),
        "progression_issues": item.get("progression_issues", []),
        "warnings": item.get("warnings", []),
        "source_repo_path": status.get("source_repo_path", item.get("source_repo_path", "")),
        "project_path": status.get("project_path", ""),
        "render_path": status.get("render_path", ""),
    }


def _table(targets: list[dict[str, Any]]) -> list[str]:
    if not targets:
        return ["- none"]
    lines = [
        "| priority | case | next | status | archetype | unlocks | issues |",
        "| ---: | --- | --- | --- | --- | --- | --- |",
    ]
    for item in targets:
        lines.append(
            f"| {item['priority']} | {item['case_id']} | {item['next_action']} | "
            f"{item['status']} | {item['archetype'] or '-'} | "
            f"{', '.join(item['new_unlocks']) or '-'} | "
            f"{', '.join(item['progression_issues'] + item['warnings']) or '-'} |"
        )
    return lines
