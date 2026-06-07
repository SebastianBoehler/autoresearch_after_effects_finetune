from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any


DECISION_ORDER = {
    "fix_render": 0,
    "rerender_stale": 1,
    "render_missing": 2,
    "manual_review_render": 3,
    "watch_quality": 4,
    "promote_rendered": 5,
    "promote_reviewed": 6,
}


def build_render_review_queue(
    records: list[dict[str, Any]],
    *,
    render_analysis: dict[str, Any] | None = None,
    dataset_audit: dict[str, Any] | None = None,
    contact_sheets: dict[str, Any] | None = None,
    manual_decisions: dict[str, Any] | None = None,
) -> dict[str, Any]:
    cases_by_id = _cases_by_id(render_analysis)
    sheet_paths = _sheet_paths(contact_sheets)
    audit_index = _audit_index(dataset_audit)
    decisions = _manual_decisions(manual_decisions)
    items = [
        _queue_item(
            record,
            cases_by_id.get(record["case_id"]),
            sheet_paths,
            audit_index,
            decisions,
        )
        for record in records
    ]
    items.sort(key=lambda item: (DECISION_ORDER[item["decision"]], item["case_id"]))
    decision_counts = Counter(item["decision"] for item in items)
    return {
        "case_count": len(items),
        "train_ready_count": sum(bool(item["train_ready"]) for item in items),
        "decision_counts": dict(sorted(decision_counts.items())),
        "items": items,
    }


def render_review_queue_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Render Review Queue",
        "",
        f"- cases: {payload['case_count']}",
        f"- train-ready rendered cases: {payload['train_ready_count']}",
        "",
        "## Decision Counts",
        "",
    ]
    for decision, count in payload["decision_counts"].items():
        lines.append(f"- {decision}: {count}")
    lines.extend(
        [
            "",
            "## Cases",
            "",
            "| decision | case | quality | priority | warnings | reasons | contact sheet |",
            "| --- | --- | ---: | --- | --- | --- | --- |",
        ]
    )
    for item in payload["items"]:
        warnings = ", ".join(item["warnings"]) or "-"
        reasons = ", ".join(item["reasons"]) or "-"
        sheet = _sheet_link(item["contact_sheet_path"])
        lines.append(
            f"| {item['decision']} | {item['case_id']} | "
            f"{item['quality_score']:.3f} | {item['quality_priority']} | "
            f"{warnings} | {reasons} | {sheet} |"
        )
    return "\n".join(lines) + "\n"


def _queue_item(
    record: dict[str, Any],
    render_case: dict[str, Any] | None,
    sheet_paths: dict[str, str],
    audit_index: dict[str, set[str]],
    manual_decisions: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    case_id = record["case_id"]
    quality = (render_case or {}).get("render_quality", {})
    analysis = (render_case or {}).get("analysis", {})
    timeline = analysis.get("motion_timeline", {})
    warnings = (render_case or {}).get("warnings", [])
    notes = (render_case or {}).get("notes", [])
    decision, reasons = _decision(
        case_id=case_id,
        has_render=render_case is not None,
        quality=quality,
        warnings=warnings,
        audit_index=audit_index,
    )
    decision, reasons = _apply_manual_decision(
        case_id,
        decision,
        reasons,
        render_case is not None,
        manual_decisions,
    )
    return {
        "case_id": case_id,
        "decision": decision,
        "train_ready": decision in {"promote_rendered", "promote_reviewed"},
        "quality_score": float(quality.get("score", 0.0)),
        "quality_priority": quality.get("priority", "missing"),
        "reasons": [*reasons, *quality.get("reasons", [])],
        "warnings": warnings,
        "notes": notes,
        "motion_profile": timeline.get("motion_profile"),
        "active_frame_ratio": analysis.get("active_frame_ratio"),
        "longest_stall_ratio": timeline.get("longest_stall_ratio"),
        "prompt": record.get("prompt", ""),
        "tags": record.get("tags", []),
        "source_repo_path": record.get("source_repo_path"),
        "render_path": (render_case or {}).get("video_path"),
        "contact_sheet_path": sheet_paths.get(case_id),
    }


def _decision(
    *,
    case_id: str,
    has_render: bool,
    quality: dict[str, Any],
    warnings: list[str],
    audit_index: dict[str, set[str]],
) -> tuple[str, list[str]]:
    if case_id in audit_index["stale"]:
        return "rerender_stale", ["source changed after render"]
    if case_id in audit_index["missing"] or not has_render:
        return "render_missing", ["no current render artifact"]
    if case_id in audit_index["actionable"] or quality.get("priority") == "fix":
        return "fix_render", ["actionable visual warning"]
    if quality.get("priority") == "review" or case_id in audit_index["intentional"]:
        return "manual_review_render", ["needs visual review before training"]
    if warnings:
        return "manual_review_render", ["render warning present"]
    if quality.get("priority") == "watch":
        return "watch_quality", ["acceptable but below promotion threshold"]
    return "promote_rendered", []


def _apply_manual_decision(
    case_id: str,
    decision: str,
    reasons: list[str],
    has_render: bool,
    manual_decisions: dict[str, dict[str, Any]],
) -> tuple[str, list[str]]:
    manual = manual_decisions.get(case_id)
    if not manual or not has_render or decision in {"render_missing", "rerender_stale"}:
        return decision, reasons
    note = manual.get("note", "manual visual review")
    if manual.get("decision") == "promote":
        return "promote_reviewed", [f"manual visual review accepted: {note}"]
    if manual.get("decision") == "fix":
        return "fix_render", [f"manual visual review rejected: {note}"]
    if manual.get("decision") == "watch":
        return "watch_quality", [f"manual visual review watch: {note}", *reasons]
    return decision, reasons


def _audit_index(dataset_audit: dict[str, Any] | None) -> dict[str, set[str]]:
    if not dataset_audit:
        return {"missing": set(), "stale": set(), "actionable": set(), "intentional": set()}
    return {
        "missing": set(dataset_audit.get("missing_render_cases", [])),
        "stale": set(dataset_audit.get("stale_render_cases", [])),
        "actionable": {
            item["case_id"]
            for item in dataset_audit.get("actionable_render_warning_cases", [])
        },
        "intentional": {
            item["case_id"]
            for item in dataset_audit.get("intentional_render_warning_cases", [])
        },
    }


def _cases_by_id(render_analysis: dict[str, Any] | None) -> dict[str, dict[str, Any]]:
    return {
        case["case_id"]: case
        for case in (render_analysis or {}).get("cases", [])
    }


def _sheet_paths(contact_sheets: dict[str, Any] | None) -> dict[str, str]:
    return {
        case["case_id"]: case["output_path"]
        for case in (contact_sheets or {}).get("cases", [])
        if case.get("ok") and case.get("output_path")
    }


def _manual_decisions(payload: dict[str, Any] | None) -> dict[str, dict[str, Any]]:
    return {
        item["case_id"]: item
        for item in (payload or {}).get("cases", [])
    }


def _sheet_link(path: str | None) -> str:
    if not path:
        return "-"
    name = Path(path).name
    return f"[open](contact_sheets/{name})"
