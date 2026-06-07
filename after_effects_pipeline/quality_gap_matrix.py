from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any


def build_quality_gap_matrix(
    *,
    queue: dict[str, Any],
    render_overlap: dict[str, Any],
    animation_anatomy: dict[str, Any],
    render_progression: dict[str, Any],
    render_unlock_plan: dict[str, Any],
) -> dict[str, Any]:
    queue_by_id = {item["case_id"]: item for item in queue.get("items", [])}
    anatomy_by_id = {item["case_id"]: item for item in animation_anatomy.get("cases", [])}
    progression_by_id = {item["case_id"]: item for item in render_progression.get("cases", [])}
    overlap_by_id = _overlap_index(render_overlap.get("potential_overlaps", []))
    plan_by_id = {
        item["case_id"]: item
        for item in render_unlock_plan.get("greedy_unlock_sequence", [])
    }
    items = [
        _case_item(case_id, queue_by_id, anatomy_by_id, progression_by_id, overlap_by_id, plan_by_id)
        for case_id in sorted(set(queue_by_id) | set(plan_by_id))
    ]
    action_counts = Counter(item["action"] for item in items)
    ranked_items = sorted(items, key=_sort_key)
    return {
        "summary": {
            "case_count": len(items),
            "train_ready_count": sum(item["train_ready"] for item in items),
            "planned_unlock_target_count": len(plan_by_id),
            "train_ready_overlap_watch_count": sum(
                item["train_ready"] and item["overlap_pair_count"] > 0 for item in items
            ),
            "archetype_unlock_target_count": sum(bool(item["archetype_unlocks"]) for item in items),
            "progression_issue_target_count": sum(bool(item["progression_issues"]) for item in items),
            "action_counts": dict(sorted(action_counts.items())),
        },
        "archetype_gaps": animation_anatomy.get("train_ready_archetype_gaps", []),
        "items": ranked_items,
        "recommendations": _recommendations(ranked_items, render_unlock_plan),
    }


def render_quality_gap_matrix_markdown(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# Quality Gap Matrix",
        "",
        "Combines third-frame render analysis, overlap pairs, animation anatomy, progression issues, and the render-unlock plan into one action list.",
        "",
        "## Summary",
        "",
        f"- cases: {summary['case_count']}",
        f"- train-ready cases: {summary['train_ready_count']}",
        f"- planned render-unlock targets: {summary['planned_unlock_target_count']}",
        f"- archetype unlock targets: {summary['archetype_unlock_target_count']}",
        f"- progression issue targets: {summary['progression_issue_target_count']}",
        f"- train-ready overlap watches: {summary['train_ready_overlap_watch_count']}",
        f"- actions: {_counts(summary['action_counts'])}",
        "",
        "## Priority Actions",
        "",
        "| priority | case | action | ready | decision | archetype | overlaps | unlocks | issues |",
        "| ---: | --- | --- | --- | --- | --- | ---: | --- | --- |",
    ]
    for item in payload["items"][:40]:
        lines.append(
            f"| {item['priority']} | {item['case_id']} | {item['action']} | "
            f"{item['train_ready']} | {item['decision']} | {item['archetype'] or '-'} | "
            f"{item['overlap_pair_count']} | {', '.join(item['new_unlocks']) or '-'} | "
            f"{', '.join(item['progression_issues'] + item['warnings']) or '-'} |"
        )
    lines.extend(["", "## Archetype Gaps", ""])
    if payload["archetype_gaps"]:
        for gap in payload["archetype_gaps"]:
            lines.append(
                f"- {gap['archetype']}: first unlock={gap['first_unlock_case']}; "
                f"cases={', '.join(gap['case_ids'])}"
            )
    else:
        lines.append("- none")
    lines.extend(["", "## Recommendations", ""])
    lines.extend(f"- {item}" for item in payload["recommendations"])
    return "\n".join(lines) + "\n"


def _case_item(
    case_id: str,
    queue_by_id: dict[str, dict[str, Any]],
    anatomy_by_id: dict[str, dict[str, Any]],
    progression_by_id: dict[str, dict[str, Any]],
    overlap_by_id: dict[str, list[dict[str, Any]]],
    plan_by_id: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    queue_item = queue_by_id.get(case_id, {})
    anatomy = anatomy_by_id.get(case_id, {})
    progression = progression_by_id.get(case_id, {})
    plan = plan_by_id.get(case_id, {})
    overlaps = overlap_by_id.get(case_id, [])
    train_ready = bool(queue_item.get("train_ready"))
    progression_issues = list(progression.get("issues", []))
    warnings = list(queue_item.get("warnings", []))
    new_unlocks = list(plan.get("new_unlocks", []))
    archetype_unlocks = list(plan.get("archetype_unlocks", []))
    action = _action(train_ready, queue_item, plan, progression_issues, overlaps)
    priority = _priority(action, new_unlocks, archetype_unlocks, progression_issues, overlaps, warnings)
    return {
        "case_id": case_id,
        "action": action,
        "priority": priority,
        "train_ready": train_ready,
        "decision": queue_item.get("decision", plan.get("decision", "unknown")),
        "quality_score": float(queue_item.get("quality_score") or 0.0),
        "archetype": anatomy.get("archetype", ""),
        "dominant_phase": anatomy.get("dominant_phase", ""),
        "motion_profile": queue_item.get("motion_profile", anatomy.get("motion_profile", "")),
        "progression_issues": progression_issues,
        "warnings": warnings,
        "overlap_pair_count": len(overlaps),
        "max_overlap_score": max([float(item["score"]) for item in overlaps], default=0.0),
        "same_split_overlap_count": sum(bool(item.get("same_split")) for item in overlaps),
        "overlap_cases": [item["other"] for item in sorted(overlaps, key=lambda row: -row["score"])[:5]],
        "new_unlocks": new_unlocks,
        "archetype_unlocks": archetype_unlocks,
        "source_repo_path": queue_item.get("source_repo_path", plan.get("source_repo_path", "")),
    }


def _overlap_index(pairs: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    result: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for pair in pairs:
        result[pair["a"]].append({**pair, "other": pair["b"]})
        result[pair["b"]].append({**pair, "other": pair["a"]})
    return result


def _action(
    train_ready: bool,
    queue_item: dict[str, Any],
    plan: dict[str, Any],
    progression_issues: list[str],
    overlaps: list[dict[str, Any]],
) -> str:
    if plan:
        if plan.get("archetype_unlocks"):
            return "render_unlock_archetype_gap"
        if progression_issues:
            return "rerender_progression_gap"
        return "render_unlock_requirement"
    if train_ready and any(pair.get("same_split") for pair in overlaps):
        return "fix_split_overlap"
    if train_ready and overlaps:
        return "watch_train_ready_overlap"
    if train_ready:
        return "keep_train_ready"
    if queue_item.get("decision") == "rerender_stale":
        return "rerender_stale_backlog"
    if queue_item.get("decision") == "render_missing":
        return "render_missing_backlog"
    return "inspect"


def _priority(
    action: str,
    new_unlocks: list[str],
    archetype_unlocks: list[str],
    progression_issues: list[str],
    overlaps: list[dict[str, Any]],
    warnings: list[str],
) -> int:
    base = {
        "fix_split_overlap": 220,
        "render_unlock_archetype_gap": 190,
        "rerender_progression_gap": 170,
        "render_unlock_requirement": 150,
        "watch_train_ready_overlap": 90,
        "rerender_stale_backlog": 70,
        "render_missing_backlog": 50,
        "keep_train_ready": 20,
    }.get(action, 10)
    return (
        base
        + len(new_unlocks) * 5
        + len(archetype_unlocks) * 12
        + len(progression_issues) * 8
        + min(len(overlaps), 4) * 4
        + len(warnings) * 3
    )


def _recommendations(items: list[dict[str, Any]], plan: dict[str, Any]) -> list[str]:
    archetype_targets = [item["case_id"] for item in items if item["action"] == "render_unlock_archetype_gap"]
    requirement_targets = [item["case_id"] for item in items if item["action"] == "render_unlock_requirement"]
    overlap_watches = [item["case_id"] for item in items if item["action"] == "watch_train_ready_overlap"]
    recommendations = []
    if archetype_targets:
        recommendations.append("render/rerender archetype-gap targets first: " + ", ".join(archetype_targets[:8]))
    if requirement_targets:
        recommendations.append("then render remaining requirement targets: " + ", ".join(requirement_targets[:8]))
    if overlap_watches:
        recommendations.append("keep current split assignments, but visually review overlap watches: " + ", ".join(overlap_watches[:8]))
    if plan.get("summary", {}).get("covered_requirement_count") == plan.get("summary", {}).get("requirement_count"):
        recommendations.append("current render-unlock plan covers all known requirement gaps; prefer rendering over adding new source cases")
    return recommendations or ["no quality actions found"]


def _sort_key(item: dict[str, Any]) -> tuple[int, str]:
    return (-item["priority"], item["case_id"])


def _counts(counts: dict[str, int]) -> str:
    return ", ".join(f"{key}={value}" for key, value in sorted(counts.items())) or "-"
