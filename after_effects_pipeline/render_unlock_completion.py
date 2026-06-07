from __future__ import annotations

from typing import Any


def build_render_unlock_completion(
    *,
    plan: dict[str, Any],
    train_ready_manifest: dict[str, Any],
    capability_audit: dict[str, Any],
    inspiration_coverage: dict[str, Any],
    source_pattern_audit: dict[str, Any] | None = None,
) -> dict[str, Any]:
    satisfied = _satisfied_requirements(
        train_ready_manifest,
        capability_audit,
        inspiration_coverage,
        source_pattern_audit or {},
    )
    requirements = plan.get("requirements", [])
    requirement_rows = [
        {"requirement": requirement, "satisfied": requirement in satisfied}
        for requirement in requirements
    ]
    target_rows = [
        _target_row(target, train_ready_manifest.get("case_ids", []), satisfied)
        for target in plan.get("greedy_unlock_sequence", [])
    ]
    satisfied_count = sum(row["satisfied"] for row in requirement_rows)
    target_ready_count = sum(row["train_ready"] for row in target_rows)
    return {
        "summary": {
            "requirement_count": len(requirement_rows),
            "satisfied_requirement_count": satisfied_count,
            "remaining_requirement_count": len(requirement_rows) - satisfied_count,
            "target_count": len(target_rows),
            "train_ready_target_count": target_ready_count,
        },
        "requirements": requirement_rows,
        "remaining_requirements": [
            row["requirement"] for row in requirement_rows if not row["satisfied"]
        ],
        "targets": target_rows,
    }


def render_render_unlock_completion_markdown(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# Render Unlock Completion Audit",
        "",
        f"- requirements: {summary['requirement_count']}",
        f"- satisfied requirements: {summary['satisfied_requirement_count']}",
        f"- remaining requirements: {summary['remaining_requirement_count']}",
        f"- train-ready unlock targets: {summary['train_ready_target_count']}/{summary['target_count']}",
        "",
        "## Remaining Requirements",
        "",
    ]
    if payload["remaining_requirements"]:
        lines.extend(f"- {requirement}" for requirement in payload["remaining_requirements"])
    else:
        lines.append("- none")
    lines.extend([
        "",
        "## Target Status",
        "",
        "| target | train-ready | satisfied unlocks | remaining unlocks |",
        "| --- | --- | --- | --- |",
    ])
    for target in payload["targets"]:
        lines.append(
            f"| {target['case_id']} | {target['train_ready']} | "
            f"{', '.join(target['satisfied_unlocks']) or '-'} | "
            f"{', '.join(target['remaining_unlocks']) or '-'} |"
        )
    return "\n".join(lines) + "\n"


def _satisfied_requirements(
    train_ready_manifest: dict[str, Any],
    capability_audit: dict[str, Any],
    inspiration_coverage: dict[str, Any],
    source_pattern_audit: dict[str, Any],
) -> set[str]:
    satisfied = {
        f"pack:{pack}"
        for pack, count in train_ready_manifest.get("synthetic_pack_counts", {}).items()
        if count
    }
    satisfied.update(
        f"capability:{capability}"
        for capability, count in capability_audit.get("train_ready_capability_counts", {}).items()
        if count
    )
    satisfied.update(
        f"motif:{motif['motif']}"
        for motif in inspiration_coverage.get("motifs", [])
        if motif.get("train_ready_count", 0) > 0
    )
    satisfied.update(
        f"pattern:{pattern}"
        for pattern, count in source_pattern_audit.get("train_ready_pattern_counts", {}).items()
        if count
    )
    return satisfied


def _target_row(
    target: dict[str, Any],
    train_ready_case_ids: list[str],
    satisfied: set[str],
) -> dict[str, Any]:
    unlocks = target.get("new_unlocks", [])
    return {
        "case_id": target["case_id"],
        "train_ready": target["case_id"] in set(train_ready_case_ids),
        "satisfied_unlocks": [key for key in unlocks if key in satisfied],
        "remaining_unlocks": [key for key in unlocks if key not in satisfied],
        "planned_unlocks": unlocks,
    }
