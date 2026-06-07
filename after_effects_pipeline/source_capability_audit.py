from __future__ import annotations

from collections import Counter
from typing import Any

from after_effects_pipeline.static_check import extract_code

CORE_CAPABILITIES = {
    "camera_3d",
    "eased_keyframes",
    "expressions",
    "keyframes",
    "markers",
    "nested_comps",
    "null_controls",
    "path_motion",
    "shape_layers",
    "text_layers",
    "time_remap",
}

MARKERS = {
    "camera_3d": ("layers.addCamera", "threeDLayer = true"),
    "eased_keyframes": ("KeyframeEase", "setTemporalEaseAtKey"),
    "effects": ('.property("Effects").addProperty', ".property('Effects').addProperty"),
    "expressions": (".expression",),
    "keyframes": ("setValueAtTime",),
    "markers": ("MarkerValue", '.property("Marker")', ".property('Marker')"),
    "null_controls": ("layers.addNull",),
    "path_motion": ("ADBE Vector Filter - Trim", "createPath"),
    "shape_layers": ("layers.addShape", "ADBE Vector Shape"),
    "solid_layers": ("layers.addSolid",),
    "text_layers": ("layers.addText",),
    "time_remap": ("timeRemapEnabled", "ADBE Time Remapping"),
}


def audit_source_capabilities(
    records: list[dict[str, Any]],
    *,
    train_ready_case_ids: set[str] | None = None,
) -> dict[str, Any]:
    cases = [_audit_case(record) for record in records]
    capability_counts = Counter(
        capability for case in cases for capability in case["capabilities"]
    )
    train_ready_cases = [
        case for case in cases if train_ready_case_ids and case["case_id"] in train_ready_case_ids
    ]
    train_ready_counts = Counter(
        capability for case in train_ready_cases for capability in case["capabilities"]
    )
    core_gaps = sorted(CORE_CAPABILITIES - set(capability_counts))
    train_ready_core_gaps = sorted(CORE_CAPABILITIES - set(train_ready_counts))
    train_ready_gap_unlocks = _train_ready_gap_unlocks(
        train_ready_core_gaps,
        cases,
        train_ready_case_ids or set(),
    )
    return {
        "case_count": len(cases),
        "summary": {
            "capability_count": len(capability_counts),
            "core_gap_count": len(core_gaps),
            "case_issue_count": sum(bool(case["issues"]) for case in cases),
            "train_ready_case_count": len(train_ready_cases),
            "train_ready_capability_count": len(train_ready_counts),
            "train_ready_core_gap_count": len(train_ready_core_gaps),
        },
        "capability_counts": dict(sorted(capability_counts.items())),
        "train_ready_capability_counts": dict(sorted(train_ready_counts.items())),
        "core_gaps": core_gaps,
        "train_ready_core_gaps": train_ready_core_gaps,
        "train_ready_gap_unlocks": train_ready_gap_unlocks,
        "cases": cases,
    }


def render_source_capability_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Source Capability Audit",
        "",
        "Static audit of distinct AE construction techniques represented in source JSX.",
        "",
        "## Summary",
        "",
        f"- cases: {payload['case_count']}",
        f"- represented capabilities: {payload['summary']['capability_count']}",
        f"- core capability gaps: {payload['summary']['core_gap_count']}",
        f"- cases with issues: {payload['summary']['case_issue_count']}",
        f"- train-ready capabilities: {payload['summary']['train_ready_capability_count']}",
        f"- train-ready core capability gaps: {payload['summary']['train_ready_core_gap_count']}",
        "",
        "## Capability Counts",
        "",
    ]
    for capability, count in payload["capability_counts"].items():
        lines.append(f"- {capability}: {count}")
    lines.extend(["", "## Train-Ready Capability Counts", ""])
    for capability, count in payload["train_ready_capability_counts"].items():
        lines.append(f"- {capability}: {count}")
    if not payload["train_ready_capability_counts"]:
        lines.append("- none")
    if payload["core_gaps"]:
        lines.extend(["", "## Core Gaps", ""])
        lines.extend(f"- {gap}" for gap in payload["core_gaps"])
    if payload["train_ready_core_gaps"]:
        lines.extend(["", "## Train-Ready Core Gaps", ""])
        lines.extend(f"- {gap}" for gap in payload["train_ready_core_gaps"])
    if payload["train_ready_gap_unlocks"]:
        lines.extend(["", "## Train-Ready Gap Unlocks", ""])
        for item in payload["train_ready_gap_unlocks"]:
            lines.append(f"- {item['capability']}: {', '.join(item['case_ids'][:6])}")
    lines.extend(["", "## Cases Needing Review", ""])
    review_cases = [case for case in payload["cases"] if case["issues"]]
    if review_cases:
        lines.extend(["| case | capabilities | issues |", "| --- | --- | --- |"])
        for case in sorted(review_cases, key=lambda item: item["case_id"]):
            caps = ", ".join(case["capabilities"]) or "-"
            lines.append(f"| {case['case_id']} | {caps} | {', '.join(case['issues'])} |")
    else:
        lines.append("- none")
    return "\n".join(lines) + "\n"


def _audit_case(record: dict[str, Any]) -> dict[str, Any]:
    code = extract_code(record["completion"])
    capabilities = sorted(_capabilities(code))
    return {
        "case_id": record["case_id"],
        "source_repo_path": record.get("source_repo_path", ""),
        "capabilities": capabilities,
        "capability_count": len(capabilities),
        "issues": _issues(capabilities),
    }


def _capabilities(code: str) -> set[str]:
    capabilities = {
        name
        for name, markers in MARKERS.items()
        if any(marker in code for marker in markers)
    }
    if code.count("app.project.items.addComp") > 1 or ".layers.add(" in code:
        capabilities.add("nested_comps")
    return capabilities


def _train_ready_gap_unlocks(
    gaps: list[str],
    cases: list[dict[str, Any]],
    train_ready_case_ids: set[str],
) -> list[dict[str, Any]]:
    unlocks = []
    for gap in gaps:
        case_ids = [
            case["case_id"]
            for case in cases
            if gap in case["capabilities"] and case["case_id"] not in train_ready_case_ids
        ]
        unlocks.append({"capability": gap, "case_ids": case_ids})
    return unlocks


def _issues(capabilities: list[str]) -> list[str]:
    if len(capabilities) < 3:
        return ["low_capability_variety"]
    return []
