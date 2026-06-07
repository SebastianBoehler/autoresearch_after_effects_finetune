from __future__ import annotations

from collections import Counter
from typing import Any


def build_render_progression_audit(
    render_analysis: dict[str, Any],
    *,
    render_queue: dict[str, Any] | None = None,
) -> dict[str, Any]:
    queue_by_case = {
        item["case_id"]: item
        for item in (render_queue or {}).get("items", [])
    }
    cases = [
        _case_progression(case, queue_by_case.get(case["case_id"], {}))
        for case in render_analysis.get("cases", [])
    ]
    issue_counts = Counter(issue for case in cases for issue in case["issues"])
    train_ready_issues = [
        case["case_id"]
        for case in cases
        if case["train_ready"] and case["issues"]
    ]
    return {
        "summary": {
            "case_count": len(cases),
            "cases_with_issues": sum(bool(case["issues"]) for case in cases),
            "train_ready_issue_count": len(train_ready_issues),
            "issue_counts": dict(sorted(issue_counts.items())),
        },
        "train_ready_issue_cases": train_ready_issues,
        "cases": cases,
        "recommendations": _recommendations(cases),
    }


def render_progression_markdown(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# Render Progression Audit",
        "",
        "Third-frame temporal audit of visual progression across intro, middle, and outro.",
        "",
        "## Summary",
        "",
        f"- cases: {summary['case_count']}",
        f"- cases with issues: {summary['cases_with_issues']}",
        f"- train-ready issue cases: {summary['train_ready_issue_count']}",
        f"- issues: {_counts_text(summary['issue_counts'])}",
        "",
        "## Cases Needing Review",
        "",
        "| case | decision | ready | score | active | stall | intro | middle | outro | issues |",
        "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    issue_cases = [case for case in payload["cases"] if case["issues"]]
    for case in sorted(issue_cases, key=_case_sort_key):
        lines.append(
            f"| {case['case_id']} | {case['decision']} | {case['train_ready']} | "
            f"{case['progression_score']:.3f} | {case['active_frame_ratio']:.3f} | "
            f"{case['longest_stall_ratio']:.3f} | "
            f"{case['phase_active_ratios'].get('intro', 0.0):.2f} | "
            f"{case['phase_active_ratios'].get('middle', 0.0):.2f} | "
            f"{case['phase_active_ratios'].get('outro', 0.0):.2f} | "
            f"{', '.join(case['issues'])} |"
        )
    if not issue_cases:
        lines.append("| - | - | False | 0.000 | 0.000 | 0.000 | 0.00 | 0.00 | 0.00 | - |")
    lines.extend(["", "## Recommendations", ""])
    lines.extend(f"- {item}" for item in payload["recommendations"])
    return "\n".join(lines) + "\n"


def _case_progression(case: dict[str, Any], queue_item: dict[str, Any]) -> dict[str, Any]:
    analysis = case["analysis"]
    timeline = analysis.get("motion_timeline", {})
    frame_timeline = analysis.get("frame_timeline", {})
    samples = frame_timeline.get("samples", [])
    phases = frame_timeline.get("phase_summary", [])
    phase_active = _phase_active_ratios(phases)
    metrics = {
        "case_id": case["case_id"],
        "decision": queue_item.get("decision", "unknown"),
        "train_ready": bool(queue_item.get("train_ready")),
        "motion_profile": timeline.get("motion_profile", "missing"),
        "active_frame_ratio": float(analysis.get("active_frame_ratio", 0.0)),
        "longest_stall_ratio": float(timeline.get("longest_stall_ratio", 0.0)),
        "foreground_p95": float(analysis.get("foreground_ratio", {}).get("p95", 0.0)),
        "center_p95": float(analysis.get("center_foreground_ratio", {}).get("p95", 0.0)),
        "progression_score": _progression_score(samples),
        "phase_active_ratios": phase_active,
    }
    return {**metrics, "issues": _issues(metrics)}


def _progression_score(samples: list[dict[str, Any]]) -> float:
    return round(
        0.35 * _range(samples, "foreground_ratio")
        + 0.25 * _range(samples, "center_foreground_ratio")
        + 0.25 * min(1.0, _range(samples, "component_count") / 80)
        + 0.15 * _range(samples, "saturation"),
        6,
    )


def _phase_active_ratios(phases: list[dict[str, Any]]) -> dict[str, float]:
    return {
        phase["phase"]: (
            float(phase.get("active_count", 0)) / float(phase.get("sample_count", 1) or 1)
        )
        for phase in phases
    }


def _issues(metrics: dict[str, Any]) -> list[str]:
    issues = []
    if (
        metrics["foreground_p95"] > 0.45
        and metrics["progression_score"] < 0.04
        and metrics["motion_profile"] != "steady"
    ):
        issues.append("full_frame_low_progression")
    if (
        metrics["phase_active_ratios"].get("outro", 1.0) <= 0.10
        and metrics["longest_stall_ratio"] >= 0.40
    ):
        issues.append("inactive_outro_stall")
    if metrics["active_frame_ratio"] < 0.25:
        issues.append("sparse_progression")
    return issues


def _range(samples: list[dict[str, Any]], field: str) -> float:
    values = [float(sample.get(field, 0.0)) for sample in samples]
    return max(values) - min(values) if values else 0.0


def _recommendations(cases: list[dict[str, Any]]) -> list[str]:
    issue_cases = [case for case in cases if case["issues"]]
    if not issue_cases:
        return ["rendered samples show adequate temporal progression"]
    return [
        f"add late/mid timeline motion or layout changes for {case['case_id']}"
        for case in sorted(issue_cases, key=_case_sort_key)[:8]
    ]


def _case_sort_key(case: dict[str, Any]) -> tuple[bool, int, float, str]:
    return (
        not case["train_ready"],
        -len(case["issues"]),
        case["progression_score"],
        case["case_id"],
    )


def _counts_text(counts: dict[str, int]) -> str:
    return ", ".join(f"{key}={value}" for key, value in counts.items()) or "-"
