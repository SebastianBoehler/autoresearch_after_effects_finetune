from __future__ import annotations

from typing import Any

ACTIONABLE_WARNINGS = {
    "blank_frames",
    "low_motion",
    "limited_motion_range",
    "edge_clutter",
    "low_contrast",
    "low_color_variety",
}


def score_render_quality(
    analysis: dict[str, Any],
    warnings: list[str],
) -> dict[str, Any]:
    timeline = analysis.get("motion_timeline", {})
    reasons = _quality_reasons(analysis, warnings, timeline)
    score = 1.0
    for reason, penalty in reasons:
        score -= penalty
    score = max(0.0, min(1.0, score))
    return {
        "score": round(score, 3),
        "priority": _priority(score, warnings, timeline),
        "reasons": [reason for reason, _penalty in reasons],
    }


def _quality_reasons(
    analysis: dict[str, Any],
    warnings: list[str],
    timeline: dict[str, Any],
) -> list[tuple[str, float]]:
    reasons = []
    profile = timeline.get("motion_profile", "")
    stall_ratio = float(timeline.get("longest_stall_ratio", 0.0))
    if profile == "sparse":
        reasons.append(("sparse motion profile", 0.22))
    elif profile == "stalled_sections":
        reasons.append(("long still section", 0.16))
    elif profile == "compressed_motion_window":
        reasons.append(("motion compressed into short window", 0.1))
    if stall_ratio > 0.45:
        reasons.append(("longest stall exceeds 45% of sampled frames", 0.12))
    if analysis["blank_frame_ratio"] > 0.08:
        reasons.append(("intro or blank frames exceed 8%", 0.1))
    for warning in warnings:
        reasons.append((f"warning: {warning}", _warning_penalty(warning)))
    if _has_merged_full_frame_subject(analysis):
        reasons.append(("large merged foreground may hide layout overlaps", 0.08))
    return reasons


def _warning_penalty(warning: str) -> float:
    if warning in ACTIONABLE_WARNINGS:
        return 0.18
    if warning in {"dense_foreground", "center_crowding"}:
        return 0.06
    return 0.08


def _has_merged_full_frame_subject(analysis: dict[str, Any]) -> bool:
    return (
        analysis["foreground_ratio"]["p95"] > 0.6
        and analysis["largest_component_ratio"]["p95"] > 0.55
    )


def _priority(
    score: float,
    warnings: list[str],
    timeline: dict[str, Any],
) -> str:
    if set(warnings) & ACTIONABLE_WARNINGS:
        return "fix"
    if score < 0.7 or timeline.get("motion_profile") == "sparse":
        return "review"
    if score < 0.84:
        return "watch"
    return "pass"
