from __future__ import annotations

import re
from collections import Counter
from typing import Any

from after_effects_pipeline.static_check import extract_code

TIME_PATTERN = re.compile(r"\.setValueAtTime\(\s*([0-9]+(?:\.[0-9]+)?)")


def audit_source_motion(records: list[dict[str, Any]]) -> dict[str, Any]:
    cases = [_audit_case(record) for record in records]
    issue_counts = Counter(issue for case in cases for issue in case["issues"])
    profile_counts = Counter(case["profile"] for case in cases)
    return {
        "case_count": len(cases),
        "summary": {
            "issue_counts": dict(sorted(issue_counts.items())),
            "profile_counts": dict(sorted(profile_counts.items())),
            "cases_with_issues": sum(bool(case["issues"]) for case in cases),
        },
        "cases": cases,
    }


def render_source_motion_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Source Motion Audit",
        "",
        "Static audit of owned JSX motion span. Expressions are treated as "
        "full-span motion signals; literal keyframe times are checked against "
        "each case duration.",
        "",
        "## Summary",
        "",
        f"- cases: {payload['case_count']}",
        f"- cases with issues: {payload['summary']['cases_with_issues']}",
        f"- profiles: {_counts_text(payload['summary']['profile_counts'])}",
        f"- issues: {_counts_text(payload['summary']['issue_counts'])}",
        "",
        "## Cases Needing Review",
        "",
        "| case | profile | keyframes | latest | late | expressions | issues |",
        "| --- | --- | ---: | ---: | ---: | ---: | --- |",
    ]
    rows = [case for case in payload["cases"] if case["issues"]]
    for case in sorted(rows, key=_case_sort_key):
        lines.append(
            f"| {case['case_id']} | {case['profile']} | "
            f"{case['keyframe_count']} | {case['latest_keyframe_time']:.2f} | "
            f"{case['late_keyframe_count']} | {case['expression_count']} | "
            f"{', '.join(case['issues'])} |"
        )
    if not rows:
        lines.append("| - | - | 0 | 0.00 | 0 | 0 | - |")
    return "\n".join(lines) + "\n"


def _audit_case(record: dict[str, Any]) -> dict[str, Any]:
    code = extract_code(record["completion"])
    duration = float(record.get("expected", {}).get("duration_seconds") or 0.0)
    times = sorted(_keyframe_times(code))
    expression_count = code.count(".expression")
    latest = max(times, default=0.0)
    late_threshold = duration * 0.66 if duration else 0.0
    middle_threshold = duration * 0.33 if duration else 0.0
    late_count = sum(time >= late_threshold for time in times)
    middle_count = sum(middle_threshold <= time < late_threshold for time in times)
    issues = _issues(
        duration=duration,
        keyframe_count=len(times),
        middle_count=middle_count,
        late_count=late_count,
        expression_count=expression_count,
    )
    return {
        "case_id": record["case_id"],
        "duration_seconds": duration,
        "keyframe_count": len(times),
        "distinct_keyframe_time_count": len(set(times)),
        "latest_keyframe_time": latest,
        "middle_keyframe_count": middle_count,
        "late_keyframe_count": late_count,
        "expression_count": expression_count,
        "profile": _profile(late_count, expression_count, len(times)),
        "issues": issues,
        "source_repo_path": record.get("source_repo_path", ""),
    }


def _keyframe_times(code: str) -> list[float]:
    return [round(float(match.group(1)), 3) for match in TIME_PATTERN.finditer(code)]


def _issues(
    *,
    duration: float,
    keyframe_count: int,
    middle_count: int,
    late_count: int,
    expression_count: int,
) -> list[str]:
    issues = []
    if keyframe_count + expression_count < 4:
        issues.append("low_motion_signal_count")
    if duration and late_count == 0 and expression_count < 2:
        issues.append("no_late_motion_signal")
    if duration and middle_count == 0 and expression_count == 0:
        issues.append("no_middle_motion_signal")
    return issues


def _profile(late_count: int, expression_count: int, keyframe_count: int) -> str:
    if expression_count >= 4:
        return "expression_rich"
    if expression_count > 0 and late_count > 0:
        return "mixed_full_span"
    if late_count > 0:
        return "keyframed_full_span"
    if keyframe_count > 0 or expression_count > 0:
        return "intro_weighted"
    return "static"


def _counts_text(counts: dict[str, int]) -> str:
    return ", ".join(f"{key}={value}" for key, value in counts.items()) or "-"


def _case_sort_key(case: dict[str, Any]) -> tuple[int, float, str]:
    return (-len(case["issues"]), case["latest_keyframe_time"], case["case_id"])
