from __future__ import annotations

from collections import Counter
from typing import Any


FEATURE_SCALES = {
    "brightness_mean": 0.35,
    "contrast_mean": 0.35,
    "saturation_mean": 0.30,
    "motion_mean": 0.030,
    "motion_area_p95": 0.120,
    "active_frame_ratio": 0.900,
    "foreground_p95": 0.500,
    "center_p95": 0.800,
    "component_count_p95": 60.0,
    "largest_component_p95": 0.450,
    "edge_density_p95": 0.180,
    "blank_frame_ratio": 0.200,
    "longest_stall_ratio": 0.700,
}


def build_render_overlap_audit(
    render_analysis: dict[str, Any],
    *,
    split_by_case: dict[str, str] | None = None,
    threshold: float = 0.86,
    limit: int = 30,
) -> dict[str, Any]:
    split_by_case = split_by_case or {}
    cases = [_case_signature(case) for case in render_analysis.get("cases", [])]
    pairs = _pairwise_overlaps(cases, split_by_case=split_by_case, threshold=threshold, limit=limit)
    return {
        "summary": {
            "case_count": len(cases),
            "threshold": threshold,
            "potential_overlap_count": len(pairs),
            "same_split_overlap_count": sum(bool(pair.get("same_split")) for pair in pairs),
            "motion_profile_counts": dict(Counter(case["motion_profile"] for case in cases).most_common()),
            "layout_signature_count": len({case["layout_signature"] for case in cases}),
            "animation_signature_count": len({case["animation_signature"] for case in cases}),
        },
        "layout_signature_counts": dict(Counter(case["layout_signature"] for case in cases).most_common()),
        "animation_signature_counts": dict(Counter(case["animation_signature"] for case in cases).most_common()),
        "cases": cases,
        "potential_overlaps": pairs,
        "recommendations": _recommendations(cases, pairs),
    }


def render_overlap_markdown(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# Render Overlap Audit",
        "",
        "- built from third-frame render-analysis metrics",
        f"- cases: {summary['case_count']}",
        f"- threshold: {summary['threshold']:.2f}",
        f"- potential overlaps: {summary['potential_overlap_count']}",
        f"- same-split overlaps: {summary.get('same_split_overlap_count', 0)}",
        f"- layout signatures: {summary['layout_signature_count']}",
        f"- animation signatures: {summary['animation_signature_count']}",
        "",
        "## Potential Overlaps",
        "",
    ]
    if payload["potential_overlaps"]:
        lines.extend(["| score | case A | case B | split | shared signals |", "| ---: | --- | --- | --- | --- |"])
        for item in payload["potential_overlaps"]:
            split = _split_text(item)
            lines.append(
                f"| {item['score']:.3f} | {item['a']} | {item['b']} | "
                f"{split} | {', '.join(item['shared_signals']) or '-'} |"
            )
    else:
        lines.append("- none above threshold")
    lines.extend(["", "## Animation Signatures", ""])
    for signature, count in payload["animation_signature_counts"].items():
        lines.append(f"- {signature}: {count}")
    lines.extend(["", "## Recommendations", ""])
    for item in payload["recommendations"]:
        lines.append(f"- {item}")
    return "\n".join(lines) + "\n"


def _case_signature(case: dict[str, Any]) -> dict[str, Any]:
    analysis = case["analysis"]
    source = case.get("source", {})
    timeline = analysis.get("motion_timeline", {})
    features = {
        "brightness_mean": analysis["brightness"]["mean"],
        "contrast_mean": analysis["contrast"]["mean"],
        "saturation_mean": analysis["saturation"]["mean"],
        "motion_mean": analysis["motion"]["mean"],
        "motion_area_p95": analysis["motion_area_ratio"]["p95"],
        "active_frame_ratio": analysis["active_frame_ratio"],
        "foreground_p95": analysis["foreground_ratio"]["p95"],
        "center_p95": analysis["center_foreground_ratio"]["p95"],
        "component_count_p95": analysis["component_count"]["p95"],
        "largest_component_p95": analysis["largest_component_ratio"]["p95"],
        "edge_density_p95": analysis["edge_density"]["p95"],
        "blank_frame_ratio": analysis["blank_frame_ratio"],
        "longest_stall_ratio": timeline.get("longest_stall_ratio", 0.0),
    }
    aspect = _aspect_label(int(source.get("width", 0)), int(source.get("height", 0)))
    profile = timeline.get("motion_profile", "missing")
    layout = _layout_label(features)
    energy = _motion_energy(features)
    density = _density_label(features)
    color = _color_label(features)
    return {
        "case_id": case["case_id"],
        "aspect": aspect,
        "motion_profile": profile,
        "layout_signature": f"{aspect}/{layout}/{density}/{color}",
        "animation_signature": f"{aspect}/{profile}/{energy}/{layout}",
        "features": features,
        "warnings": case.get("warnings", []),
        "quality_score": case.get("render_quality", {}).get("score", 0.0),
    }


def _pairwise_overlaps(
    cases: list[dict[str, Any]],
    *,
    split_by_case: dict[str, str],
    threshold: float,
    limit: int,
) -> list[dict[str, Any]]:
    pairs = []
    for index, first in enumerate(cases):
        for second in cases[index + 1 :]:
            score = _similarity(first, second)
            if score >= threshold:
                pairs.append(
                    {
                        "a": first["case_id"],
                        "b": second["case_id"],
                        "score": round(score, 4),
                        "split_a": split_by_case.get(first["case_id"]),
                        "split_b": split_by_case.get(second["case_id"]),
                        "same_split": (
                            split_by_case.get(first["case_id"]) is not None
                            and split_by_case.get(first["case_id"]) == split_by_case.get(second["case_id"])
                        ),
                        "shared_signals": _shared_signals(first, second),
                    }
                )
    return sorted(pairs, key=lambda item: (-item["score"], item["a"], item["b"]))[:limit]


def _similarity(first: dict[str, Any], second: dict[str, Any]) -> float:
    feature_scores = []
    for key, scale in FEATURE_SCALES.items():
        delta = abs(first["features"][key] - second["features"][key])
        feature_scores.append(1.0 - min(1.0, delta / scale))
    base = sum(feature_scores) / len(feature_scores)
    if first["aspect"] != second["aspect"]:
        base -= 0.08
    if first["motion_profile"] != second["motion_profile"]:
        base -= 0.06
    if first["layout_signature"] == second["layout_signature"]:
        base += 0.04
    if first["animation_signature"] == second["animation_signature"]:
        base += 0.04
    return max(0.0, min(1.0, base))


def _shared_signals(first: dict[str, Any], second: dict[str, Any]) -> list[str]:
    signals = []
    for key in ["aspect", "motion_profile", "layout_signature", "animation_signature"]:
        if first[key] == second[key]:
            signals.append(f"{key}={first[key]}")
    return signals


def _recommendations(cases: list[dict[str, Any]], pairs: list[dict[str, Any]]) -> list[str]:
    recommendations = []
    if any(pair.get("same_split") for pair in pairs):
        recommendations.append("move same-split overlap pairs apart or add contrastive rerenders")
    if pairs:
        recommendations.append("review high-scoring overlap pairs before adding them to the same training split")
    repeated = [signature for signature, count in Counter(case["animation_signature"] for case in cases).items() if count >= 4]
    for signature in sorted(repeated)[:6]:
        recommendations.append(f"add contrastive variants for repeated animation signature: {signature}")
    return recommendations or ["no strong rendered overlap found at current threshold"]


def _aspect_label(width: int, height: int) -> str:
    if width == height:
        return "square"
    return "landscape" if width > height else "vertical"


def _layout_label(features: dict[str, float]) -> str:
    if features["component_count_p95"] > 32:
        return "fragmented"
    if features["largest_component_p95"] > 0.30:
        return "merged"
    if features["center_p95"] > 0.62:
        return "centered"
    return "distributed"


def _motion_energy(features: dict[str, float]) -> str:
    if features["motion_area_p95"] > 0.09:
        return "high_motion"
    if features["active_frame_ratio"] > 0.62:
        return "steady_motion"
    if features["motion_area_p95"] > 0.03:
        return "subtle_motion"
    return "low_motion"


def _density_label(features: dict[str, float]) -> str:
    if features["foreground_p95"] > 0.42:
        return "dense"
    if features["foreground_p95"] > 0.22:
        return "medium"
    return "open"


def _color_label(features: dict[str, float]) -> str:
    if features["saturation_mean"] > 0.18:
        return "vivid"
    if features["saturation_mean"] < 0.055:
        return "muted"
    return "balanced"


def _split_text(item: dict[str, Any]) -> str:
    split_a = item.get("split_a") or "-"
    split_b = item.get("split_b") or "-"
    marker = "same" if item.get("same_split") else "mixed"
    return f"{split_a}/{split_b} {marker}"
