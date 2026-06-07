from __future__ import annotations

import re
from collections import Counter
from typing import Any

from after_effects_pipeline.static_check import extract_code

TIME_PATTERN = re.compile(r"\.setValueAtTime\(\s*([0-9]+(?:\.[0-9]+)?)")
EFFECT_PATTERN = re.compile(r'\.property\(["\']Effects["\']\)\.addProperty')


def audit_source_animation_quality(records: list[dict[str, Any]]) -> dict[str, Any]:
    cases = [_audit_case(record) for record in records]
    issue_counts = Counter(issue for case in cases for issue in case["issues"])
    strength_counts = Counter(strength for case in cases for strength in case["strengths"])
    return {
        "case_count": len(cases),
        "summary": {
            "cases_with_issues": sum(bool(case["issues"]) for case in cases),
            "issue_counts": dict(sorted(issue_counts.items())),
            "strength_counts": dict(sorted(strength_counts.items())),
        },
        "cases": cases,
    }


def render_source_animation_quality_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Source Animation Quality Audit",
        "",
        "Static audit for animation construction quality before AE render time is spent.",
        "",
        "## Summary",
        "",
        f"- cases: {payload['case_count']}",
        f"- cases with issues: {payload['summary']['cases_with_issues']}",
        f"- strengths: {_counts_text(payload['summary']['strength_counts'])}",
        f"- issues: {_counts_text(payload['summary']['issue_counts'])}",
        "",
        "## Cases Needing Review",
        "",
        "| case | layers | keyframes | times | span | ease | effects | text | bounds | strengths | issues |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |",
    ]
    review_cases = [case for case in payload["cases"] if case["issues"]]
    for case in sorted(review_cases, key=_case_sort_key):
        lines.append(
            f"| {case['case_id']} | {case['layer_signal_count']} | {case['keyframe_count']} | "
            f"{case['distinct_keyframe_time_count']} | {case['temporal_span_ratio']:.2f} | "
            f"{case['easing_signal_count']} | {case['effect_count']} | {case['text_layer_count']} | "
            f"{case['layout_bound_signal_count']} | {', '.join(case['strengths']) or '-'} | "
            f"{', '.join(case['issues'])} |"
        )
    if not review_cases:
        lines.append("| - | 0 | 0 | 0 | 0.00 | 0 | 0 | 0 | 0 | - | - |")
    return "\n".join(lines) + "\n"


def _audit_case(record: dict[str, Any]) -> dict[str, Any]:
    code = extract_code(record["completion"])
    duration = float(record.get("expected", {}).get("duration_seconds") or 0.0)
    times = _keyframe_times(code)
    metrics = _metrics(code, times, duration)
    strengths = _strengths(metrics)
    issues = _issues(metrics)
    return {
        "case_id": record["case_id"],
        "source_repo_path": record.get("source_repo_path", ""),
        "strengths": strengths,
        "issues": issues,
        **metrics,
    }


def _metrics(code: str, times: list[float], duration: float) -> dict[str, Any]:
    latest = max(times, default=0.0)
    text_layers = code.count(".layers.addText")
    shape_layers = code.count(".layers.addShape")
    solid_layers = code.count(".layers.addSolid")
    null_layers = code.count(".layers.addNull")
    camera_layers = code.count(".layers.addCamera")
    expression_count = code.count(".expression")
    effect_count = len(EFFECT_PATTERN.findall(code))
    layout_bounds = code.count("sourceRectAtTime")
    layer_count = text_layers + shape_layers + solid_layers + null_layers + camera_layers
    return {
        "duration_seconds": duration,
        "keyframe_count": len(times),
        "distinct_keyframe_time_count": len(set(times)),
        "latest_keyframe_time": latest,
        "temporal_span_ratio": latest / duration if duration else 0.0,
        "expression_count": expression_count,
        "easing_signal_count": code.count("setTemporalEaseAtKey") + code.count("KeyframeEase"),
        "effect_count": effect_count,
        "text_layer_count": text_layers,
        "shape_layer_count": shape_layers,
        "solid_layer_count": solid_layers,
        "camera_layer_count": camera_layers,
        "three_d_signal_count": code.count("threeDLayer = true"),
        "layer_signal_count": layer_count,
        "layout_bound_signal_count": layout_bounds,
        "path_motion_signal_count": code.count("Trim Paths") + code.count("createPath"),
    }


def _keyframe_times(code: str) -> list[float]:
    return [round(float(match.group(1)), 3) for match in TIME_PATTERN.finditer(code)]


def _strengths(metrics: dict[str, Any]) -> list[str]:
    strengths = []
    if metrics["temporal_span_ratio"] >= 0.66 or metrics["expression_count"] >= 2:
        strengths.append("full_span_motion")
    if metrics["easing_signal_count"]:
        strengths.append("eased_keyframes")
    if metrics["layer_signal_count"] >= 6:
        strengths.append("layered_composition")
    if metrics["effect_count"] >= 2:
        strengths.append("effects_driven")
    if metrics["expression_count"] >= 3:
        strengths.append("procedural_motion")
    if metrics["camera_layer_count"] or metrics["three_d_signal_count"] >= 2:
        strengths.append("camera_or_3d")
    if metrics["path_motion_signal_count"]:
        strengths.append("path_motion")
    if metrics["text_layer_count"] and metrics["layout_bound_signal_count"]:
        strengths.append("text_layout_bounds")
    return strengths


def _issues(metrics: dict[str, Any]) -> list[str]:
    issues = []
    if metrics["keyframe_count"] + metrics["expression_count"] + metrics["effect_count"] < 4:
        issues.append("low_animation_signal_count")
    if metrics["duration_seconds"] and metrics["temporal_span_ratio"] < 0.5 and metrics["expression_count"] < 2:
        issues.append("short_temporal_span")
    if metrics["keyframe_count"] >= 8 and metrics["easing_signal_count"] == 0:
        issues.append("keyframes_without_easing")
    if metrics["text_layer_count"] >= 4 and metrics["layout_bound_signal_count"] == 0:
        issues.append("dense_text_without_bounds")
    if metrics["layer_signal_count"] >= 8 and metrics["distinct_keyframe_time_count"] < 4 and metrics["expression_count"] < 2:
        issues.append("dense_layers_low_stagger")
    return issues


def _counts_text(counts: dict[str, int]) -> str:
    return ", ".join(f"{key}={value}" for key, value in counts.items()) or "-"


def _case_sort_key(case: dict[str, Any]) -> tuple[int, int, float, str]:
    return (
        -len(case["issues"]),
        -case["text_layer_count"],
        case["temporal_span_ratio"],
        case["case_id"],
    )
