from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any


def build_training_sample_diagnosis(
    *,
    render_analysis: dict[str, Any],
    queue: dict[str, Any],
    render_overlap: dict[str, Any],
    animation_anatomy: dict[str, Any],
    theme_motion_audit: dict[str, Any],
    quality_gap_matrix: dict[str, Any],
) -> dict[str, Any]:
    queue_by_id = {item["case_id"]: item for item in queue.get("items", [])}
    analysis_by_id = {case["case_id"]: case for case in render_analysis.get("cases", [])}
    anatomy_by_id = {case["case_id"]: case for case in animation_anatomy.get("cases", [])}
    theme_by_id = {case["case_id"]: case for case in theme_motion_audit.get("cases", [])}
    matrix_by_id = {item["case_id"]: item for item in quality_gap_matrix.get("items", [])}
    overlaps_by_id = _overlap_index(render_overlap.get("potential_overlaps", []))
    case_ids = sorted(set(queue_by_id) | set(matrix_by_id) | set(analysis_by_id))
    cases = [
        _case_diagnosis(
            case_id,
            queue_by_id.get(case_id, {}),
            analysis_by_id.get(case_id, {}),
            anatomy_by_id.get(case_id, {}),
            theme_by_id.get(case_id, {}),
            matrix_by_id.get(case_id, {}),
            overlaps_by_id.get(case_id, []),
        )
        for case_id in case_ids
    ]
    theme_gap_cases = _theme_gap_cases(theme_motion_audit)
    archetype_gap_cases = _archetype_gap_cases(animation_anatomy)
    summary = _summary(cases, theme_gap_cases, archetype_gap_cases)
    return {
        "summary": summary,
        "train_ready_distribution": _train_ready_distribution(cases),
        "top_diagnoses": sorted(cases, key=lambda item: (-item["priority"], item["case_id"]))[:30],
        "overlap_watch_pairs": _overlap_watch_pairs(render_overlap.get("potential_overlaps", []), cases),
        "theme_gap_cases": theme_gap_cases,
        "archetype_gap_cases": archetype_gap_cases,
        "recommendations": _recommendations(summary, theme_gap_cases, archetype_gap_cases),
        "cases": cases,
    }


def render_training_sample_diagnosis_markdown(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# Training Sample Diagnosis",
        "",
        "Ranks rendered and planned samples by every-third-frame motion evidence, overlap risk, theme coverage, and quality status.",
        "",
        "## Summary",
        "",
        f"- cases: {summary['case_count']}",
        f"- rendered cases: {summary['rendered_count']}",
        f"- train-ready rendered cases: {summary['train_ready_count']}",
        f"- planned unlock targets: {summary['planned_target_count']}",
        f"- train-ready overlap watches: {summary['train_ready_overlap_watch_count']}",
        f"- train-ready theme gaps: {summary['theme_gap_count']}",
        f"- train-ready archetype gaps: {summary['archetype_gap_count']}",
        f"- warning cases: {summary['warning_case_count']}",
        "",
        "## Priority Diagnoses",
        "",
        "| priority | case | ready | decision | action | archetype | themes | issues |",
        "| ---: | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for case in payload["top_diagnoses"]:
        lines.append(
            f"| {case['priority']} | {case['case_id']} | {case['train_ready']} | "
            f"{case['decision']} | {case['action'] or '-'} | {case['archetype']} | "
            f"{', '.join(case['themes']) or '-'} | {', '.join(case['diagnoses']) or '-'} |"
        )
    lines.extend(["", "## Train-Ready Distribution", ""])
    distribution = payload["train_ready_distribution"]
    lines.append(f"- archetypes: {_counts(distribution['archetypes'])}")
    lines.append(f"- motion profiles: {_counts(distribution['motion_profiles'])}")
    lines.append(f"- themes: {_counts(distribution['themes'])}")
    lines.extend(["", "## Overlap Watch Pairs", ""])
    if payload["overlap_watch_pairs"]:
        lines.extend([
            "| score | case A | case B | shared signals |",
            "| ---: | --- | --- | --- |",
        ])
        for pair in payload["overlap_watch_pairs"][:12]:
            lines.append(
                f"| {pair['score']:.4f} | {pair['a']} | {pair['b']} | "
                f"{', '.join(pair['shared_signals']) or '-'} |"
            )
    else:
        lines.append("- none")
    lines.extend(["", "## Gap Cases", ""])
    lines.append("- theme gaps: " + _gap_summary(payload["theme_gap_cases"], "theme"))
    lines.append("- archetype gaps: " + _gap_summary(payload["archetype_gap_cases"], "archetype"))
    lines.extend(["", "## Recommendations", ""])
    lines.extend(f"- {item}" for item in payload["recommendations"])
    return "\n".join(lines) + "\n"


def _case_diagnosis(
    case_id: str,
    queue_item: dict[str, Any],
    analysis_case: dict[str, Any],
    anatomy: dict[str, Any],
    theme_case: dict[str, Any],
    matrix_item: dict[str, Any],
    overlaps: list[dict[str, Any]],
) -> dict[str, Any]:
    analysis = analysis_case.get("analysis", {})
    motion_timeline = analysis.get("motion_timeline", {})
    warnings = list(queue_item.get("warnings") or analysis_case.get("warnings", []))
    diagnoses = _diagnoses(queue_item, motion_timeline, warnings, matrix_item, overlaps)
    priority = _priority(diagnoses, matrix_item, queue_item, overlaps)
    return {
        "case_id": case_id,
        "priority": priority,
        "diagnoses": diagnoses,
        "train_ready": bool(queue_item.get("train_ready")),
        "decision": queue_item.get("decision", matrix_item.get("decision", "unknown")),
        "action": matrix_item.get("action", ""),
        "rendered": bool(analysis_case),
        "quality_score": float(queue_item.get("quality_score") or 0.0),
        "warnings": warnings,
        "themes": list(theme_case.get("themes", [])),
        "aspect": theme_case.get("aspect", ""),
        "archetype": anatomy.get("archetype") or theme_case.get("archetype", "unrendered"),
        "motion_profile": queue_item.get("motion_profile") or motion_timeline.get("motion_profile", ""),
        "active_frame_ratio": analysis.get("active_frame_ratio"),
        "longest_stall_ratio": motion_timeline.get("longest_stall_ratio"),
        "overlap_pair_count": len(overlaps),
        "max_overlap_score": max([float(item.get("score", 0.0)) for item in overlaps], default=0.0),
        "overlap_cases": [item["other"] for item in sorted(overlaps, key=lambda row: -row.get("score", 0.0))[:5]],
        "new_unlocks": list(matrix_item.get("new_unlocks", [])),
    }


def _diagnoses(
    queue_item: dict[str, Any],
    motion_timeline: dict[str, Any],
    warnings: list[str],
    matrix_item: dict[str, Any],
    overlaps: list[dict[str, Any]],
) -> list[str]:
    items = []
    action = matrix_item.get("action", "")
    if action:
        items.append(action)
    if queue_item.get("decision") in {"render_missing", "rerender_stale"}:
        items.append(queue_item["decision"])
    if warnings:
        items.extend(warnings)
    if queue_item.get("train_ready") and overlaps:
        items.append("overlap_watch")
    if motion_timeline.get("motion_profile") == "sparse":
        items.append("sparse_motion")
    if float(motion_timeline.get("longest_stall_ratio") or 0.0) >= 0.3:
        items.append("long_stall")
    return sorted(set(items))


def _priority(
    diagnoses: list[str],
    matrix_item: dict[str, Any],
    queue_item: dict[str, Any],
    overlaps: list[dict[str, Any]],
) -> int:
    score = int(matrix_item.get("priority") or 0)
    if not score:
        score = 30 if queue_item.get("train_ready") else 10
    if "overlap_watch" in diagnoses:
        score += 35 + min(len(overlaps), 4) * 5
    if "dense_foreground" in diagnoses or "center_crowding" in diagnoses:
        score += 24
    if "sparse_motion" in diagnoses or "long_stall" in diagnoses:
        score += 18
    return score


def _summary(
    cases: list[dict[str, Any]],
    theme_gap_cases: list[dict[str, Any]],
    archetype_gap_cases: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "case_count": len(cases),
        "rendered_count": sum(case["rendered"] for case in cases),
        "train_ready_count": sum(case["train_ready"] for case in cases),
        "planned_target_count": sum(bool(case["new_unlocks"]) for case in cases),
        "train_ready_overlap_watch_count": sum(case["train_ready"] and case["overlap_pair_count"] > 0 for case in cases),
        "theme_gap_count": len(theme_gap_cases),
        "archetype_gap_count": len(archetype_gap_cases),
        "warning_case_count": sum(bool(case["warnings"]) for case in cases),
    }


def _train_ready_distribution(cases: list[dict[str, Any]]) -> dict[str, dict[str, int]]:
    ready = [case for case in cases if case["train_ready"]]
    themes: Counter[str] = Counter()
    for case in ready:
        themes.update(case["themes"])
    return {
        "archetypes": dict(sorted(Counter(case["archetype"] for case in ready).items())),
        "motion_profiles": dict(sorted(Counter(case["motion_profile"] for case in ready).items())),
        "themes": dict(sorted(themes.items())),
    }


def _overlap_watch_pairs(pairs: list[dict[str, Any]], cases: list[dict[str, Any]]) -> list[dict[str, Any]]:
    ready_ids = {case["case_id"] for case in cases if case["train_ready"]}
    rows = [
        pair for pair in pairs
        if pair.get("a") in ready_ids or pair.get("b") in ready_ids
    ]
    return sorted(rows, key=lambda pair: -float(pair.get("score", 0.0)))


def _theme_gap_cases(theme_motion_audit: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {"theme": gap["theme"], "case_id": gap.get("first_planned_target") or (gap.get("candidate_cases") or [""])[0]}
        for gap in theme_motion_audit.get("train_ready_theme_gaps", [])
    ]


def _archetype_gap_cases(animation_anatomy: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {"archetype": gap["archetype"], "case_id": gap.get("first_unlock_case", "")}
        for gap in animation_anatomy.get("train_ready_archetype_gaps", [])
    ]


def _overlap_index(pairs: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    result: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for pair in pairs:
        result[pair["a"]].append({**pair, "other": pair["b"]})
        result[pair["b"]].append({**pair, "other": pair["a"]})
    return result


def _recommendations(
    summary: dict[str, Any],
    theme_gap_cases: list[dict[str, Any]],
    archetype_gap_cases: list[dict[str, Any]],
) -> list[str]:
    items = []
    if archetype_gap_cases:
        items.append("rerender archetype-gap cases first: " + ", ".join(row["case_id"] for row in archetype_gap_cases))
    if theme_gap_cases:
        items.append("create/render theme-gap cases: " + ", ".join(row["case_id"] for row in theme_gap_cases))
    if summary["train_ready_overlap_watch_count"]:
        items.append("keep split-safe overlap watches, but diversify next train-ready renders before adding more steady centered samples")
    return items or ["current rendered train-ready set has no major diagnosis gaps"]


def _counts(counts: dict[str, int]) -> str:
    return ", ".join(f"{key}={value}" for key, value in sorted(counts.items())) or "-"


def _gap_summary(rows: list[dict[str, Any]], key: str) -> str:
    return ", ".join(f"{row[key]}={row['case_id']}" for row in rows) or "none"
