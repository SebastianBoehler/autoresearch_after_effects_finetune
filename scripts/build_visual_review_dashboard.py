from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from after_effects_pipeline.utils import write_json

REPO_ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    args = _parse_args()
    dashboard = _build_dashboard(
        queue=_load_json(args.queue),
        render_analysis=_load_optional_json(args.render_analysis),
        readiness_report=_load_optional_json(args.readiness_report),
        harness_status=_load_optional_json(args.harness_status),
        motif_harness_status=_load_optional_json(args.motif_harness_status),
    )
    write_json(args.output, dashboard)
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.write_text(_markdown(dashboard))
    print(dashboard["summary"])


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--queue", type=Path, default=REPO_ROOT / "artifacts/visual_analysis/render-review-queue.json")
    parser.add_argument("--render-analysis", type=Path, default=REPO_ROOT / "artifacts/visual_analysis/render-analysis.json")
    parser.add_argument("--readiness-report", type=Path, default=REPO_ROOT / "artifacts/datasets/after-effects-train-ready/readiness-report.json")
    parser.add_argument("--harness-status", type=Path, default=REPO_ROOT / "artifacts/ae_live_checks/_manual_harnesses/status.json")
    parser.add_argument("--motif-harness-status", type=Path, default=REPO_ROOT / "artifacts/ae_live_checks/_manual_harnesses_motif_gaps/status.json")
    parser.add_argument("--output", type=Path, default=REPO_ROOT / "artifacts/visual_analysis/review-dashboard.json")
    parser.add_argument("--markdown-output", type=Path, default=REPO_ROOT / "artifacts/visual_analysis/review-dashboard.md")
    return parser.parse_args()


def _build_dashboard(
    *,
    queue: dict[str, Any],
    render_analysis: dict[str, Any] | None,
    readiness_report: dict[str, Any] | None,
    harness_status: dict[str, Any] | None,
    motif_harness_status: dict[str, Any] | None = None,
) -> dict[str, Any]:
    items = queue.get("items", [])
    analysis_by_id = {
        case["case_id"]: case for case in (render_analysis or {}).get("cases", [])
    }
    review_items = [_dashboard_item(item, analysis_by_id.get(item["case_id"])) for item in items]
    return {
        "summary": {
            "case_count": queue.get("case_count", len(items)),
            "train_ready_count": queue.get("train_ready_count", 0),
            "rendered_case_count": len(analysis_by_id),
            "train_ready_watchlist_count": len(_train_ready_watchlist(review_items)),
            "timeline_risk_count": len(_timeline_risk_items(review_items)),
            "decision_counts": queue.get("decision_counts", {}),
            "warning_counts": _warning_counts(review_items),
            "motion_profile_counts": _motion_counts(review_items),
            "harness_status_counts": (harness_status or {}).get("summary", {}).get("status_counts", {}),
            "motif_harness_status_counts": (motif_harness_status or {}).get("summary", {}).get("status_counts", {}),
            "missing_train_ready_packs": (readiness_report or {}).get("coverage_gaps", {}).get("synthetic_packs", []),
        },
        "pack_coverage": _pack_coverage(review_items),
        "train_ready_watchlist": _train_ready_watchlist(review_items),
        "priority_review": _priority_review(review_items),
        "timeline_risks": _timeline_risk_items(review_items),
        "motif_harness_cases": (motif_harness_status or {}).get("cases", []),
        "render_debt_priority": (readiness_report or {}).get("render_debt", [])[:12],
        "items": review_items,
    }


def _dashboard_item(item: dict[str, Any], render_case: dict[str, Any] | None) -> dict[str, Any]:
    analysis = (render_case or {}).get("analysis", {})
    timeline = analysis.get("frame_timeline") or {}
    return {
        "case_id": item["case_id"],
        "decision": item.get("decision"),
        "train_ready": bool(item.get("train_ready")),
        "quality_score": item.get("quality_score", 0.0),
        "quality_priority": item.get("quality_priority"),
        "motion_profile": item.get("motion_profile"),
        "active_frame_ratio": item.get("active_frame_ratio"),
        "longest_stall_ratio": item.get("longest_stall_ratio"),
        "warnings": item.get("warnings", []),
        "notes": item.get("notes", []),
        "reasons": item.get("reasons", []),
        "tags": item.get("tags", []),
        "synthetic_packs": _synthetic_packs(item),
        "contact_sheet_path": item.get("contact_sheet_path"),
        "render_path": item.get("render_path"),
        "sampled_frames": analysis.get("sampled_frames"),
        "phase_activity": _phase_activity(timeline),
        "timeline_risks": _timeline_risk_labels(timeline),
        "motion_peaks": _motion_peak_labels(timeline),
    }


def _priority_review(items: list[dict[str, Any]], limit: int = 18) -> list[dict[str, Any]]:
    candidates = [
        item for item in items
        if item["decision"] not in {"promote_rendered", "promote_reviewed"}
        or item["warnings"]
        or item["quality_priority"] in {"fix", "review", "watch"}
    ]
    candidates.sort(key=lambda item: (_priority_score(item), item["case_id"]))
    return candidates[:limit]


def _train_ready_watchlist(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    watchlist = [item for item in items if item["train_ready"] and _is_weak_ready(item)]
    watchlist.sort(key=lambda item: (_watch_score(item), item["case_id"]))
    return watchlist


def _is_weak_ready(item: dict[str, Any]) -> bool:
    return (
        item["quality_priority"] != "pass"
        or bool(item["warnings"])
        or item["motion_profile"] in {"sparse", "stalled_sections"}
        or float(item.get("longest_stall_ratio") or 0.0) > 0.45
    )


def _watch_score(item: dict[str, Any]) -> tuple[int, float]:
    priority = {"review": 0, "watch": 1, "pass": 2}.get(str(item["quality_priority"]), 3)
    return (priority, float(item.get("quality_score") or 0.0))


def _priority_score(item: dict[str, Any]) -> tuple[int, float]:
    decision_weight = {
        "fix_render": 0,
        "rerender_stale": 1,
        "render_missing": 2,
        "manual_review_render": 3,
        "watch_quality": 4,
    }.get(item["decision"], 5)
    return (decision_weight, -float(item.get("quality_score") or 0.0))


def _pack_coverage(items: list[dict[str, Any]]) -> dict[str, dict[str, int]]:
    packs: dict[str, Counter[str]] = defaultdict(Counter)
    for item in items:
        for pack in item["synthetic_packs"]:
            packs[pack]["all"] += 1
            packs[pack][item["decision"]] += 1
            if item["train_ready"]:
                packs[pack]["train_ready"] += 1
            if item["render_path"]:
                packs[pack]["rendered"] += 1
    return {pack: dict(sorted(counts.items())) for pack, counts in sorted(packs.items())}


def _warning_counts(items: list[dict[str, Any]]) -> dict[str, int]:
    return dict(Counter(warning for item in items for warning in item["warnings"]).most_common())


def _motion_counts(items: list[dict[str, Any]]) -> dict[str, int]:
    return dict(Counter(item["motion_profile"] or "missing" for item in items).most_common())


def _timeline_risk_items(items: list[dict[str, Any]], limit: int = 18) -> list[dict[str, Any]]:
    risks = [item for item in items if item["timeline_risks"]]
    risks.sort(key=lambda item: (-len(item["timeline_risks"]), item["decision"], item["case_id"]))
    return risks[:limit]


def _phase_activity(timeline: dict[str, Any]) -> str:
    parts = []
    for phase in timeline.get("phase_summary", []):
        samples = int(phase.get("sample_count") or 0)
        active = int(phase.get("active_count") or 0)
        blanks = int(phase.get("blank_count") or 0)
        parts.append(f"{phase.get('phase')} {active}/{samples} active {blanks} blank")
    return "; ".join(parts)


def _timeline_risk_labels(timeline: dict[str, Any]) -> list[str]:
    labels: list[str] = []
    for phase in timeline.get("phase_summary", []):
        name = str(phase.get("phase"))
        samples = float(phase.get("sample_count") or 0)
        if samples <= 0:
            continue
        active_ratio = float(phase.get("active_count") or 0) / samples
        blank_ratio = float(phase.get("blank_count") or 0) / samples
        foreground = float(phase.get("mean_foreground_ratio") or 0)
        if blank_ratio > 0.2:
            labels.append(f"{name}_blank_start")
        if active_ratio < 0.2 and name != "outro":
            labels.append(f"{name}_low_motion")
        if active_ratio < 0.15 and name == "outro":
            labels.append("static_outro")
        if foreground > 0.55:
            labels.append(f"{name}_dense_layout")
    return labels


def _motion_peak_labels(timeline: dict[str, Any]) -> str:
    peaks = timeline.get("motion_peaks", [])[:3]
    return ", ".join(
        f"f{peak.get('source_frame')} {float(peak.get('motion_area_ratio') or 0):.3f} {peak.get('phase')}"
        for peak in peaks
    )


def _synthetic_packs(item: dict[str, Any]) -> list[str]:
    return [tag for tag in item.get("tags", []) if tag.startswith("synthetic-")]


def _markdown(dashboard: dict[str, Any]) -> str:
    lines = [
        "# Visual Review Dashboard",
        "",
        f"- cases: {dashboard['summary']['case_count']}",
        f"- rendered cases: {dashboard['summary']['rendered_case_count']}",
        f"- train-ready cases: {dashboard['summary']['train_ready_count']}",
        f"- train-ready watchlist: {dashboard['summary']['train_ready_watchlist_count']}",
        f"- timeline risks: {dashboard['summary']['timeline_risk_count']}",
        f"- decisions: {_inline_counts(dashboard['summary']['decision_counts'])}",
        f"- warnings: {_inline_counts(dashboard['summary']['warning_counts'])}",
        f"- motion profiles: {_inline_counts(dashboard['summary']['motion_profile_counts'])}",
        f"- motif harness status: {_inline_counts(dashboard['summary'].get('motif_harness_status_counts', {}))}",
        f"- missing train-ready packs: {', '.join(dashboard['summary']['missing_train_ready_packs']) or '-'}",
        "",
        "## Pack Coverage",
        "",
        "| pack | all | rendered | train-ready | decisions |",
        "| --- | ---: | ---: | ---: | --- |",
    ]
    for pack, counts in dashboard["pack_coverage"].items():
        decisions = {key: value for key, value in counts.items() if key not in {"all", "rendered", "train_ready"}}
        lines.append(f"| {pack} | {counts.get('all', 0)} | {counts.get('rendered', 0)} | {counts.get('train_ready', 0)} | {_inline_counts(decisions)} |")
    lines.extend(["", "## Train-Ready Watchlist", "", "| case | decision | quality | motion | stall | warnings | reasons | sheet |", "| --- | --- | ---: | --- | ---: | --- | --- | --- |"])
    for item in dashboard["train_ready_watchlist"]:
        lines.append(
            f"| {item['case_id']} | {item['decision']} | {item['quality_score']:.3f} | "
            f"{item['motion_profile'] or '-'} | {float(item.get('longest_stall_ratio') or 0.0):.3f} | "
            f"{', '.join(item['warnings']) or '-'} | {', '.join(item['reasons']) or '-'} | "
            f"{_sheet_link(item['contact_sheet_path'])} |"
        )
    lines.extend(["", "## Priority Review", "", "| decision | case | quality | motion | warnings | reasons | sheet |", "| --- | --- | ---: | --- | --- | --- | --- |"])
    for item in dashboard["priority_review"]:
        lines.append(
            f"| {item['decision']} | {item['case_id']} | {item['quality_score']:.3f} | "
            f"{item['motion_profile'] or '-'} | {', '.join(item['warnings']) or '-'} | "
            f"{', '.join(item['reasons']) or '-'} | {_sheet_link(item['contact_sheet_path'])} |"
        )
    lines.extend(["", "## Motif Harness Status", "", "| status | case | decision | AE error |", "| --- | --- | --- | --- |"])
    for case in dashboard.get("motif_harness_cases", []):
        lines.append(f"| {case['status']} | {case['case_id']} | {case['decision']} | {case.get('ae_error') or '-'} |")
    lines.extend(["", "## Timeline Risks", "", "| case | decision | risks | phase activity | motion peaks | sheet |", "| --- | --- | --- | --- | --- | --- |"])
    for item in dashboard["timeline_risks"]:
        lines.append(
            f"| {item['case_id']} | {item['decision']} | {', '.join(item['timeline_risks'])} | "
            f"{item['phase_activity'] or '-'} | {item['motion_peaks'] or '-'} | "
            f"{_sheet_link(item['contact_sheet_path'])} |"
        )
    return "\n".join(lines) + "\n"


def _sheet_link(path: str | None) -> str:
    if not path:
        return "-"
    return f"[open](contact_sheets/{Path(path).name})"


def _inline_counts(counts: dict[str, int]) -> str:
    return ", ".join(f"{key}={value}" for key, value in counts.items()) or "-"


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def _load_optional_json(path: Path) -> dict[str, Any] | None:
    return json.loads(path.read_text()) if path.exists() else None


if __name__ == "__main__":
    main()
