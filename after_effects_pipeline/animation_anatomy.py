from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any


def build_animation_anatomy_audit(
    render_analysis: dict[str, Any],
    *,
    render_queue: dict[str, Any] | None = None,
) -> dict[str, Any]:
    queue_by_id = {item["case_id"]: item for item in (render_queue or {}).get("items", [])}
    cases = [
        _case_anatomy(case, queue_by_id.get(case["case_id"], {}))
        for case in render_analysis.get("cases", [])
    ]
    archetype_counts = Counter(case["archetype"] for case in cases)
    ready_counts = Counter(case["archetype"] for case in cases if case["train_ready"])
    phase_counts = Counter(case["dominant_phase"] for case in cases)
    ready_phase_counts = Counter(case["dominant_phase"] for case in cases if case["train_ready"])
    gaps = _train_ready_gaps(cases, archetype_counts, ready_counts)
    return {
        "summary": {
            "case_count": len(cases),
            "train_ready_count": sum(case["train_ready"] for case in cases),
            "archetype_counts": dict(sorted(archetype_counts.items())),
            "train_ready_archetype_counts": dict(sorted(ready_counts.items())),
            "train_ready_archetype_gap_count": len(gaps),
            "dominant_phase_counts": dict(sorted(phase_counts.items())),
            "train_ready_dominant_phase_counts": dict(sorted(ready_phase_counts.items())),
            "stale_recheck_count": sum(case["needs_fresh_render_review"] for case in cases),
        },
        "train_ready_archetype_gaps": gaps,
        "cases": cases,
        "recommendations": _recommendations(gaps, cases),
    }


def render_animation_anatomy_markdown(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# Animation Anatomy Audit",
        "",
        "Uses every-third-frame render analysis to summarize motion shape, phase coverage, and train-ready archetype diversity.",
        "",
        "## Summary",
        "",
        f"- rendered cases: {summary['case_count']}",
        f"- train-ready rendered cases: {summary['train_ready_count']}",
        f"- train-ready archetype gaps: {summary['train_ready_archetype_gap_count']}",
        f"- stale cases needing fresh render review: {summary['stale_recheck_count']}",
        f"- archetypes: {_counts(summary['archetype_counts'])}",
        f"- train-ready archetypes: {_counts(summary['train_ready_archetype_counts'])}",
        f"- dominant phases: {_counts(summary['dominant_phase_counts'])}",
        "",
        "## Archetype Gaps",
        "",
    ]
    if payload["train_ready_archetype_gaps"]:
        for gap in payload["train_ready_archetype_gaps"]:
            lines.append(
                f"- {gap['archetype']}: first unlock={gap['first_unlock_case']}; "
                f"cases={', '.join(gap['case_ids'][:8])}"
            )
    else:
        lines.append("- none")
    lines.extend(
        [
            "",
            "## Cases",
            "",
            "| case | decision | ready | archetype | energy | dominant | phases | profile | stall | action |",
            "| --- | --- | --- | --- | --- | --- | --- | --- | ---: | --- |",
        ]
    )
    for case in sorted(payload["cases"], key=_case_sort_key):
        lines.append(
            f"| {case['case_id']} | {case['decision']} | {case['train_ready']} | "
            f"{case['archetype']} | {case['energy']} | {case['dominant_phase']} | "
            f"{case['phase_pattern']} | {case['motion_profile']} | "
            f"{case['longest_stall_ratio']:.3f} | {case['next_action']} |"
        )
    lines.extend(["", "## Recommendations", ""])
    lines.extend(f"- {item}" for item in payload["recommendations"])
    return "\n".join(lines) + "\n"


def _case_anatomy(case: dict[str, Any], queue_item: dict[str, Any]) -> dict[str, Any]:
    analysis = case["analysis"]
    motion_timeline = analysis.get("motion_timeline", {})
    phases = analysis.get("frame_timeline", {}).get("phase_summary", [])
    phase_ratios = _phase_active_ratios(phases)
    dominant = _dominant_phase(phases)
    archetype = _archetype(analysis, motion_timeline, phase_ratios, dominant)
    decision = queue_item.get("decision", "unknown")
    needs_recheck = decision == "rerender_stale" and queue_item.get("quality_priority") in {"review", "watch"}
    return {
        "case_id": case["case_id"],
        "decision": decision,
        "train_ready": bool(queue_item.get("train_ready")),
        "archetype": archetype,
        "energy": _energy(analysis),
        "dominant_phase": dominant,
        "phase_pattern": _phase_pattern(phase_ratios),
        "phase_active_ratios": phase_ratios,
        "motion_profile": motion_timeline.get("motion_profile", "missing"),
        "longest_stall_ratio": float(motion_timeline.get("longest_stall_ratio", 0.0)),
        "quality_score": float(queue_item.get("quality_score") or 0.0),
        "needs_fresh_render_review": needs_recheck,
        "next_action": _next_action(decision, needs_recheck),
    }


def _phase_active_ratios(phases: list[dict[str, Any]]) -> dict[str, float]:
    return {
        phase["phase"]: float(phase.get("active_count", 0)) / float(phase.get("sample_count", 1) or 1)
        for phase in phases
    }


def _dominant_phase(phases: list[dict[str, Any]]) -> str:
    if not phases:
        return "missing"
    peak = max(phases, key=lambda phase: float(phase.get("mean_motion_area_ratio") or 0.0))
    return str(peak.get("phase", "missing"))


def _phase_pattern(ratios: dict[str, float]) -> str:
    return "/".join(f"{phase}:{_band(ratios.get(phase, 0.0))}" for phase in ["intro", "middle", "outro"])


def _band(value: float) -> str:
    if value >= 0.65:
        return "high"
    if value >= 0.25:
        return "mid"
    return "low"


def _energy(analysis: dict[str, Any]) -> str:
    active = float(analysis.get("active_frame_ratio", 0.0))
    motion_p95 = float(analysis.get("motion_area_ratio", {}).get("p95", 0.0))
    if active >= 0.75 and motion_p95 >= 0.055:
        return "high"
    if active >= 0.4 or motion_p95 >= 0.03:
        return "medium"
    return "low"


def _archetype(
    analysis: dict[str, Any],
    motion_timeline: dict[str, Any],
    ratios: dict[str, float],
    dominant: str,
) -> str:
    profile = motion_timeline.get("motion_profile", "")
    foreground = float(analysis.get("foreground_ratio", {}).get("p95", 0.0))
    if profile == "steady":
        return "dense_continuous" if foreground > 0.48 else "continuous_motion"
    if profile == "compressed_motion_window":
        return f"{dominant}_burst_window"
    if profile == "sparse":
        return f"{dominant}_sparse_motion"
    if profile == "stalled_sections":
        return "static_outro_sequence" if ratios.get("outro", 1.0) < 0.2 else "sectioned_motion"
    if ratios.get("outro", 0.0) >= 0.65 and ratios.get("intro", 0.0) < 0.35:
        return "late_reveal"
    return "varied_sequence"


def _train_ready_gaps(
    cases: list[dict[str, Any]],
    archetype_counts: Counter[str],
    ready_counts: Counter[str],
) -> list[dict[str, Any]]:
    by_type: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for case in cases:
        by_type[case["archetype"]].append(case)
    gaps = []
    for archetype in sorted(archetype_counts):
        if ready_counts.get(archetype, 0):
            continue
        candidates = sorted(by_type[archetype], key=lambda case: (case["decision"] != "rerender_stale", case["case_id"]))
        gaps.append({
            "archetype": archetype,
            "case_ids": [case["case_id"] for case in candidates],
            "first_unlock_case": candidates[0]["case_id"] if candidates else "",
        })
    return gaps


def _next_action(decision: str, needs_recheck: bool) -> str:
    if decision == "promote_rendered":
        return "keep_train_ready"
    if needs_recheck:
        return "rerender_then_review"
    if decision == "rerender_stale":
        return "rerender"
    if decision == "render_missing":
        return "create_project"
    return "inspect"


def _recommendations(gaps: list[dict[str, Any]], cases: list[dict[str, Any]]) -> list[str]:
    items = [f"render/promote {gap['first_unlock_case']} to cover {gap['archetype']}" for gap in gaps]
    rechecks = [case["case_id"] for case in cases if case["needs_fresh_render_review"]]
    if rechecks:
        items.append("rerender stale review/watch cases before judging anatomy: " + ", ".join(rechecks[:8]))
    return items or ["train-ready rendered subset covers all observed animation archetypes"]


def _case_sort_key(case: dict[str, Any]) -> tuple[bool, str, str]:
    return (case["train_ready"], case["next_action"], case["case_id"])


def _counts(counts: dict[str, int]) -> str:
    return ", ".join(f"{key}={value}" for key, value in sorted(counts.items())) or "-"
