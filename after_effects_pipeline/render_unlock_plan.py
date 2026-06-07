from __future__ import annotations

from typing import Any


def build_render_unlock_plan(
    *,
    readiness_report: dict[str, Any],
    capability_audit: dict[str, Any],
    inspiration_coverage: dict[str, Any],
    render_progression: dict[str, Any],
    queue: dict[str, Any],
    source_pattern_audit: dict[str, Any] | None = None,
    animation_anatomy: dict[str, Any] | None = None,
    theme_motion_audit: dict[str, Any] | None = None,
) -> dict[str, Any]:
    queue_by_id = {item["case_id"]: item for item in queue.get("items", [])}
    candidates = _candidates(readiness_report, queue_by_id)
    requirements = set()
    _add_capability_unlocks(candidates, requirements, capability_audit)
    _add_motif_unlocks(candidates, requirements, inspiration_coverage)
    _add_pattern_unlocks(candidates, requirements, source_pattern_audit or {})
    _add_archetype_unlocks(candidates, requirements, animation_anatomy or {})
    _add_theme_unlocks(candidates, requirements, theme_motion_audit or {})
    _add_pack_unlocks(candidates, requirements, readiness_report)
    _add_progression_rerenders(candidates, render_progression)
    targets = sorted(candidates.values(), key=_sort_key)
    sequence = _greedy_sequence(targets, requirements)
    return {
        "summary": {
            "candidate_count": len(targets),
            "requirement_count": len(requirements),
            "greedy_target_count": len(sequence),
            "covered_requirement_count": _covered_count(sequence),
            "progression_issue_target_count": sum(
                1 for target in targets if target["progression_issues"]
            ),
        },
        "requirements": sorted(requirements),
        "greedy_unlock_sequence": sequence,
        "targets": targets,
    }


def render_render_unlock_plan_markdown(plan: dict[str, Any]) -> str:
    summary = plan["summary"]
    lines = [
        "# Render Unlock Plan",
        "",
        f"- candidates: {summary['candidate_count']}",
        f"- requirements: {summary['requirement_count']}",
        f"- greedy targets: {summary['greedy_target_count']}",
        f"- covered requirements: {summary['covered_requirement_count']}",
        f"- progression issue targets: {summary['progression_issue_target_count']}",
        "",
        "## Greedy Unlock Sequence",
        "",
        "| rank | case | decision | score | new unlocks | reasons |",
        "| ---: | --- | --- | ---: | --- | --- |",
    ]
    for index, target in enumerate(plan["greedy_unlock_sequence"], start=1):
        lines.append(_target_row(index, target, include_new=True))
    lines.extend(["", "## Top Scored Targets", "", "| rank | case | decision | score | unlocks | reasons |", "| ---: | --- | --- | ---: | --- | --- |"])
    for index, target in enumerate(plan["targets"][:20], start=1):
        lines.append(_target_row(index, target, include_new=False))
    return "\n".join(lines) + "\n"


def _candidates(
    readiness_report: dict[str, Any],
    queue_by_id: dict[str, dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    candidates = {}
    for debt in readiness_report.get("render_debt", []):
        case_id = debt["case_id"]
        queue_item = queue_by_id.get(case_id, {})
        candidates[case_id] = {
            "case_id": case_id,
            "decision": debt.get("decision", queue_item.get("decision", "")),
            "score": _base_score(debt, queue_item),
            "coverage_keys": [],
            "capability_unlocks": [],
            "motif_unlocks": list(debt.get("motif_gap_unlocks", [])),
            "archetype_unlocks": [],
            "theme_unlocks": [],
            "synthetic_pack_unlocks": [],
            "progression_issues": [],
            "reasons": list(debt.get("coverage_reasons", [])),
            "source_repo_path": debt.get("source_repo_path", queue_item.get("source_repo_path", "")),
        }
        for motif in debt.get("motif_gap_unlocks", []):
            _add_unlock(candidates[case_id], f"motif:{motif}", 18)
    return candidates


def _add_capability_unlocks(
    candidates: dict[str, dict[str, Any]],
    requirements: set[str],
    capability_audit: dict[str, Any],
) -> None:
    for unlock in capability_audit.get("train_ready_gap_unlocks", []):
        capability = unlock["capability"]
        key = f"capability:{capability}"
        requirements.add(key)
        for index, case_id in enumerate(unlock.get("case_ids", [])):
            if case_id not in candidates:
                continue
            target = candidates[case_id]
            if capability not in target["capability_unlocks"]:
                target["capability_unlocks"].append(capability)
            target["reasons"].append(f"unlocks train-ready capability: {capability}")
            _add_unlock(target, key, 70 if index == 0 else 42)


def _add_motif_unlocks(
    candidates: dict[str, dict[str, Any]],
    requirements: set[str],
    inspiration_coverage: dict[str, Any],
) -> None:
    for gap in inspiration_coverage.get("train_ready_gaps", []):
        motif = gap["motif"]
        key = f"motif:{motif}"
        requirements.add(key)
        case_ids = [gap.get("first_unlock_case")]
        case_ids.extend(gap.get("render_missing_cases", []))
        case_ids.extend(gap.get("rerender_stale_cases", []))
        for index, case_id in enumerate(_unique(case_ids)):
            if not case_id or case_id not in candidates:
                continue
            target = candidates[case_id]
            if motif not in target["motif_unlocks"]:
                target["motif_unlocks"].append(motif)
            target["reasons"].append(f"unlocks web inspiration motif: {motif}")
            _add_unlock(target, key, 36 if index == 0 else 14)


def _add_pattern_unlocks(
    candidates: dict[str, dict[str, Any]],
    requirements: set[str],
    source_pattern_audit: dict[str, Any],
) -> None:
    for gap in source_pattern_audit.get("train_ready_pattern_gaps", []):
        pattern = gap["pattern"]
        key = f"pattern:{pattern}"
        requirements.add(key)
        for index, case_id in enumerate(gap.get("case_ids", [])):
            if case_id not in candidates:
                continue
            target = candidates[case_id]
            target["reasons"].append(f"unlocks train-ready animation pattern: {pattern}")
            _add_unlock(target, key, 32 if index == 0 else 12)


def _add_archetype_unlocks(
    candidates: dict[str, dict[str, Any]],
    requirements: set[str],
    animation_anatomy: dict[str, Any],
) -> None:
    for gap in animation_anatomy.get("train_ready_archetype_gaps", []):
        archetype = gap["archetype"]
        key = f"archetype:{archetype}"
        requirements.add(key)
        case_ids = [gap.get("first_unlock_case")]
        case_ids.extend(gap.get("case_ids", []))
        for index, case_id in enumerate(_unique(case_ids)):
            if not case_id or case_id not in candidates:
                continue
            target = candidates[case_id]
            if archetype not in target["archetype_unlocks"]:
                target["archetype_unlocks"].append(archetype)
            target["reasons"].append(f"unlocks train-ready animation archetype: {archetype}")
            _add_unlock(target, key, 44 if index == 0 else 16)


def _add_theme_unlocks(
    candidates: dict[str, dict[str, Any]],
    requirements: set[str],
    theme_motion_audit: dict[str, Any],
) -> None:
    for gap in theme_motion_audit.get("train_ready_theme_gaps", []):
        theme = gap["theme"]
        key = f"theme:{theme}"
        requirements.add(key)
        case_ids = [gap.get("first_planned_target")]
        case_ids.extend(gap.get("candidate_cases", []))
        for index, case_id in enumerate(_unique(case_ids)):
            if not case_id or case_id not in candidates:
                continue
            target = candidates[case_id]
            if theme not in target["theme_unlocks"]:
                target["theme_unlocks"].append(theme)
            target["reasons"].append(f"unlocks train-ready theme: {theme}")
            _add_unlock(target, key, 34 if index == 0 else 12)


def _add_pack_unlocks(
    candidates: dict[str, dict[str, Any]],
    requirements: set[str],
    readiness_report: dict[str, Any],
) -> None:
    for pack in readiness_report.get("coverage_gaps", {}).get("synthetic_packs", []):
        requirements.add(f"pack:{pack}")
    for unlock in readiness_report.get("coverage_unlocks", []):
        case_id = unlock["case_id"]
        if case_id not in candidates:
            continue
        pack = unlock["synthetic_pack"]
        target = candidates[case_id]
        target["synthetic_pack_unlocks"].append(pack)
        target["reasons"].append(f"unlocks synthetic pack: {pack}")
        _add_unlock(target, f"pack:{pack}", 45)


def _add_progression_rerenders(
    candidates: dict[str, dict[str, Any]],
    render_progression: dict[str, Any],
) -> None:
    for case in render_progression.get("cases", []):
        issues = case.get("issues", [])
        case_id = case.get("case_id")
        if not issues or case_id not in candidates:
            continue
        target = candidates[case_id]
        target["progression_issues"] = issues
        target["score"] += 12 + len(issues) * 8
        target["reasons"].append("rerender stale progression issue: " + ", ".join(issues))


def _greedy_sequence(
    targets: list[dict[str, Any]],
    requirements: set[str],
) -> list[dict[str, Any]]:
    uncovered = set(requirements)
    selected = []
    remaining = list(targets)
    while uncovered:
        best = max(
            remaining,
            key=lambda target: (len(set(target["coverage_keys"]) & uncovered), target["score"]),
            default=None,
        )
        if not best:
            break
        new_unlocks = sorted(set(best["coverage_keys"]) & uncovered)
        if not new_unlocks:
            break
        item = dict(best)
        item["new_unlocks"] = new_unlocks
        selected.append(item)
        uncovered -= set(new_unlocks)
        remaining.remove(best)
    return selected


def _covered_count(sequence: list[dict[str, Any]]) -> int:
    return len({key for target in sequence for key in target.get("new_unlocks", [])})


def _add_unlock(target: dict[str, Any], key: str, score: int) -> None:
    if key not in target["coverage_keys"]:
        target["coverage_keys"].append(key)
        target["score"] += score


def _base_score(debt: dict[str, Any], queue_item: dict[str, Any]) -> int:
    decision = debt.get("decision", queue_item.get("decision", ""))
    score = {"render_missing": 20, "rerender_stale": 18, "fix_render": 16}.get(decision, 8)
    score += min(int(debt.get("priority_score", 0) or 0), 220) // 12
    score += {"pass": 8, "watch": 4, "review": 2}.get(queue_item.get("quality_priority"), 0)
    return score


def _sort_key(target: dict[str, Any]) -> tuple[int, int, str]:
    return (-target["score"], -len(target["coverage_keys"]), target["case_id"])


def _target_row(index: int, target: dict[str, Any], *, include_new: bool) -> str:
    unlocks = target.get("new_unlocks", []) if include_new else target.get("coverage_keys", [])
    reasons = "; ".join(_unique(target["reasons"])[:5]) or "-"
    return (
        f"| {index} | {target['case_id']} | {target['decision']} | {target['score']} | "
        f"{', '.join(unlocks) or '-'} | {reasons} |"
    )


def _unique(values: list[Any]) -> list[Any]:
    seen = set()
    result = []
    for value in values:
        if value and value not in seen:
            seen.add(value)
            result.append(value)
    return result
