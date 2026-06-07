from __future__ import annotations

from collections import Counter
from math import ceil
from typing import Any


def build_training_curriculum(
    *,
    diagnosis: dict[str, Any],
    split_safety: dict[str, Any],
    quality_gate: dict[str, Any],
) -> dict[str, Any]:
    cases = diagnosis.get("cases", [])
    ready = [case for case in cases if case.get("train_ready")]
    feature_counts = _feature_counts(ready)
    overrepresented = _overrepresented(feature_counts, len(ready))
    weighted = [_weighted_case(case, feature_counts, overrepresented) for case in ready]
    anchors = [case for case in weighted if case["overlap_pair_count"] == 0]
    overlap_watches = [case for case in weighted if case["overlap_pair_count"] > 0]
    promotions = _promotion_targets(cases)
    split_summary = split_safety.get("summary", split_safety)
    return {
        "summary": {
            "train_ready_count": len(ready),
            "anchor_count": len(anchors),
            "overlap_watch_count": len(overlap_watches),
            "post_render_promotion_count": len(promotions),
            "split_safe": bool(split_summary.get("ok")),
            "technical_trainable_subset": bool(quality_gate.get("summary", quality_gate).get("technical_trainable_subset")),
            "high_quality_trainable_subset": bool(quality_gate.get("summary", quality_gate).get("high_quality_trainable_subset")),
            "full_dataset_ready": bool(quality_gate.get("summary", quality_gate).get("full_dataset_ready")),
        },
        "feature_counts": feature_counts,
        "overrepresented_features": overrepresented,
        "sampling_weights": sorted(weighted, key=lambda item: (-item["weight"], item["case_id"])),
        "anchor_cases": sorted(anchors, key=lambda item: (-item["weight"], item["case_id"])),
        "overlap_watch_cases": sorted(overlap_watches, key=lambda item: (-item["overlap_pair_count"], item["case_id"])),
        "post_render_promotions": promotions,
        "recommendations": _recommendations(overrepresented, promotions, overlap_watches),
    }


def render_training_curriculum_markdown(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# Training Curriculum",
        "",
        "Turns train-ready quality reports into sampling weights and post-render promotion priorities.",
        "",
        "## Summary",
        "",
        f"- train-ready cases: {summary['train_ready_count']}",
        f"- anchor cases: {summary['anchor_count']}",
        f"- overlap-watch cases: {summary['overlap_watch_count']}",
        f"- post-render promotion targets: {summary['post_render_promotion_count']}",
        f"- split safe: {summary['split_safe']}",
        f"- technical subset trainable: {summary['technical_trainable_subset']}",
        f"- high-quality subset trainable: {summary['high_quality_trainable_subset']}",
        f"- full dataset ready: {summary['full_dataset_ready']}",
        "",
        "## Current Sampling Weights",
        "",
        "| weight | case | archetype | motion | themes | reason |",
        "| ---: | --- | --- | --- | --- | --- |",
    ]
    for item in payload["sampling_weights"]:
        lines.append(
            f"| {item['weight']:.2f} | {item['case_id']} | {item['archetype']} | "
            f"{item['motion_profile']} | {', '.join(item['themes'][:4])} | "
            f"{', '.join(item['weight_reasons']) or 'balanced'} |"
        )
    lines.extend(["", "## Anchor Cases", ""])
    lines.extend(f"- {case['case_id']}: weight={case['weight']:.2f}" for case in payload["anchor_cases"])
    lines.extend(["", "## Overlap Watches", ""])
    if payload["overlap_watch_cases"]:
        for case in payload["overlap_watch_cases"]:
            lines.append(
                f"- {case['case_id']}: overlaps={case['overlap_pair_count']}, "
                f"max={case['max_overlap_score']:.4f}, weight={case['weight']:.2f}"
            )
    else:
        lines.append("- none")
    lines.extend(["", "## Post-Render Promotion Targets", ""])
    for item in payload["post_render_promotions"]:
        lines.append(
            f"- {item['case_id']}: priority={item['priority']}, "
            f"unlocks={', '.join(item['unlock_types']) or '-'}"
        )
    lines.extend(["", "## Recommendations", ""])
    lines.extend(f"- {item}" for item in payload["recommendations"])
    return "\n".join(lines) + "\n"


def _feature_counts(cases: list[dict[str, Any]]) -> dict[str, dict[str, int]]:
    themes: Counter[str] = Counter()
    for case in cases:
        themes.update(case.get("themes", []))
    return {
        "archetypes": dict(sorted(Counter(case.get("archetype", "") for case in cases).items())),
        "motion_profiles": dict(sorted(Counter(case.get("motion_profile", "") for case in cases).items())),
        "aspects": dict(sorted(Counter(case.get("aspect", "") for case in cases).items())),
        "themes": dict(sorted(themes.items())),
    }


def _overrepresented(counts: dict[str, dict[str, int]], ready_count: int) -> dict[str, dict[str, int]]:
    result = {}
    thresholds = {
        "archetypes": max(3, ceil(ready_count * 0.35)),
        "motion_profiles": max(3, ceil(ready_count * 0.35)),
        "themes": max(4, ceil(ready_count * 0.4)),
        "aspects": max(4, ceil(ready_count * 0.55)),
    }
    for group, values in counts.items():
        result[group] = {
            key: value for key, value in values.items()
            if value > thresholds[group]
        }
    return result


def _weighted_case(
    case: dict[str, Any],
    counts: dict[str, dict[str, int]],
    overrepresented: dict[str, dict[str, int]],
) -> dict[str, Any]:
    weight = 1.0
    reasons = []
    if case.get("archetype") in overrepresented["archetypes"]:
        weight *= 0.72
        reasons.append("common_archetype")
    if case.get("motion_profile") in overrepresented["motion_profiles"]:
        weight *= 0.82
        reasons.append("common_motion")
    if case.get("aspect") in overrepresented["aspects"]:
        weight *= 0.88
        reasons.append("common_aspect")
    overlap_count = int(case.get("overlap_pair_count") or 0)
    if overlap_count:
        weight *= max(0.55, 1.0 - overlap_count * 0.12)
        reasons.append("overlap_watch")
    rare_themes = [theme for theme in case.get("themes", []) if counts["themes"].get(theme, 0) <= 2]
    if rare_themes:
        weight += min(0.35, len(rare_themes) * 0.12)
        reasons.append("rare_theme")
    return {
        "case_id": case["case_id"],
        "weight": round(max(0.4, min(weight, 1.35)), 2),
        "weight_reasons": reasons,
        "themes": list(case.get("themes", [])),
        "archetype": case.get("archetype", ""),
        "motion_profile": case.get("motion_profile", ""),
        "aspect": case.get("aspect", ""),
        "overlap_pair_count": overlap_count,
        "max_overlap_score": float(case.get("max_overlap_score") or 0.0),
    }


def _promotion_targets(cases: list[dict[str, Any]]) -> list[dict[str, Any]]:
    planned = [case for case in cases if case.get("new_unlocks") and not case.get("train_ready")]
    planned.sort(key=lambda case: (-int(case.get("priority") or 0), case["case_id"]))
    return [
        {
            "case_id": case["case_id"],
            "priority": int(case.get("priority") or 0),
            "decision": case.get("decision", ""),
            "unlock_types": sorted({str(unlock).split(":", 1)[0] for unlock in case.get("new_unlocks", [])}),
            "new_unlocks": case.get("new_unlocks", []),
        }
        for case in planned[:19]
    ]


def _recommendations(
    overrepresented: dict[str, dict[str, int]],
    promotions: list[dict[str, Any]],
    overlap_watches: list[dict[str, Any]],
) -> list[str]:
    recommendations = []
    common_archetypes = ", ".join(overrepresented["archetypes"])
    if common_archetypes:
        recommendations.append("down-weight overrepresented archetypes during current training: " + common_archetypes)
    if overlap_watches:
        recommendations.append("use overlap-watch cases with reduced sampling weight until new renders diversify motion signatures")
    if promotions:
        recommendations.append("after AE rerender, promote targets in this order: " + ", ".join(item["case_id"] for item in promotions[:8]))
    return recommendations or ["current train-ready curriculum is balanced"]
