from __future__ import annotations

from collections import Counter
from typing import Any


def build_render_issue_remediation(
    *,
    render_progression: dict[str, Any],
    render_analysis: dict[str, Any],
    render_queue: dict[str, Any],
    source_motion: dict[str, Any],
    source_quality: dict[str, Any],
) -> dict[str, Any]:
    progression_cases = {
        case["case_id"]: case
        for case in render_progression.get("cases", [])
        if case.get("issues")
    }
    warning_cases = {
        case["case_id"]: case
        for case in render_analysis.get("cases", [])
        if case.get("warnings")
    }
    queue_by_case = {item["case_id"]: item for item in render_queue.get("items", [])}
    motion_by_case = {case["case_id"]: case for case in source_motion.get("cases", [])}
    quality_by_case = {case["case_id"]: case for case in source_quality.get("cases", [])}
    case_ids = sorted(set(progression_cases) | set(warning_cases))
    cases = [
        _remediation_case(
            case_id,
            progression_cases.get(case_id, {}),
            warning_cases.get(case_id, {}),
            queue_by_case.get(case_id),
            motion_by_case.get(case_id, {}),
            quality_by_case.get(case_id, {}),
        )
        for case_id in case_ids
    ]
    status_counts = Counter(case["status"] for case in cases)
    return {
        "summary": {
            "issue_case_count": len(cases),
            "progression_issue_case_count": len(progression_cases),
            "warning_case_count": len(warning_cases),
            "source_remediated_count": sum(case["source_remediated"] for case in cases),
            "needs_fresh_render_count": sum(case["needs_fresh_render"] for case in cases),
            "source_issue_count": sum(
                bool(case["source_motion_issues"] or case["source_quality_issues"])
                for case in cases
            ),
            "status_counts": dict(sorted(status_counts.items())),
        },
        "cases": cases,
    }


def render_render_issue_remediation_markdown(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# Render Issue Remediation Audit",
        "",
        "Joins stale render progression issues and visual warnings to the current source audits.",
        "",
        "## Summary",
        "",
        f"- issue or warning cases: {summary['issue_case_count']}",
        f"- progression issue cases: {summary['progression_issue_case_count']}",
        f"- visual warning cases: {summary['warning_case_count']}",
        f"- source-remediated cases: {summary['source_remediated_count']}",
        f"- cases needing fresh render: {summary['needs_fresh_render_count']}",
        f"- cases with source issues: {summary['source_issue_count']}",
        f"- statuses: {_counts_text(summary['status_counts'])}",
        "",
        "## Cases",
        "",
        "| status | case | decision | train-ready | progression issues | render warnings | source issues |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for case in payload["cases"]:
        source_issues = [*case["source_motion_issues"], *case["source_quality_issues"]]
        lines.append(
            f"| {case['status']} | {case['case_id']} | {case['decision']} | "
            f"{case['train_ready']} | {_list_text(case['progression_issues'])} | "
            f"{_list_text(case['render_warnings'])} | {_list_text(source_issues)} |"
        )
    if not payload["cases"]:
        lines.append("| - | - | - | False | - | - | - |")
    return "\n".join(lines) + "\n"


def _remediation_case(
    case_id: str,
    progression: dict[str, Any],
    warning: dict[str, Any],
    queue_item: dict[str, Any] | None,
    source_motion: dict[str, Any],
    source_quality: dict[str, Any],
) -> dict[str, Any]:
    reasons = list((queue_item or {}).get("reasons", []))
    source_motion_issues = list(source_motion.get("issues", []))
    source_quality_issues = list(source_quality.get("issues", []))
    needs_fresh_render = (queue_item or {}).get("decision") == "rerender_stale" or any(
        "source changed after render" in reason for reason in reasons
    )
    source_remediated = (
        queue_item is not None
        and needs_fresh_render
        and not source_motion_issues
        and not source_quality_issues
    )
    return {
        "case_id": case_id,
        "progression_issues": list(progression.get("issues", [])),
        "render_warnings": list(warning.get("warnings", [])),
        "decision": (queue_item or {}).get("decision", "missing_queue_status"),
        "reasons": reasons,
        "source_repo_path": _source_repo_path(queue_item, source_motion, source_quality),
        "source_motion_profile": source_motion.get("profile", "missing"),
        "source_motion_issues": source_motion_issues,
        "source_quality_issues": source_quality_issues,
        "source_remediated": source_remediated,
        "needs_fresh_render": needs_fresh_render,
        "train_ready": bool((queue_item or {}).get("train_ready")),
        "status": _status(queue_item, source_motion_issues, source_quality_issues, source_remediated),
    }


def _status(
    queue_item: dict[str, Any] | None,
    source_motion_issues: list[str],
    source_quality_issues: list[str],
    source_remediated: bool,
) -> str:
    if queue_item is None:
        return "missing_queue_status"
    if source_motion_issues or source_quality_issues:
        return "source_needs_attention"
    if source_remediated:
        return "source_remediated_needs_rerender"
    return "render_proven_or_train_ready"


def _source_repo_path(
    queue_item: dict[str, Any] | None,
    source_motion: dict[str, Any],
    source_quality: dict[str, Any],
) -> str:
    return (
        (queue_item or {}).get("source_repo_path")
        or source_motion.get("source_repo_path")
        or source_quality.get("source_repo_path")
        or ""
    )


def _counts_text(counts: dict[str, int]) -> str:
    return ", ".join(f"{key}={value}" for key, value in counts.items()) or "-"


def _list_text(items: list[str]) -> str:
    return ", ".join(items) or "-"
