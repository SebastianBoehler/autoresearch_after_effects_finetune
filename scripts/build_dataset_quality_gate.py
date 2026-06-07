from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from after_effects_pipeline.utils import write_json

REPO_ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    args = _parse_args()
    gate = _build_gate(
        queue=_load_optional_json(args.queue),
        render_analysis=_load_optional_json(args.render_analysis),
        dataset_audit=_load_optional_json(args.dataset_audit),
        train_ready_manifest=_load_optional_json(args.train_ready_manifest),
        readiness_report=_load_optional_json(args.readiness_report),
        harness_status=_load_optional_json(args.harness_status),
        training_preflight=_load_optional_json(args.training_preflight),
        high_quality_manifest=_load_optional_json(args.high_quality_manifest),
        high_quality_preflight=_load_optional_json(args.high_quality_preflight),
        source_motion_audit=_load_optional_json(args.source_motion_audit),
        source_animation_quality=_load_optional_json(args.source_animation_quality),
        source_pattern_audit=_load_optional_json(args.source_pattern_audit),
        source_capability_audit=_load_optional_json(args.source_capability_audit),
        render_progression=_load_optional_json(args.render_progression),
        split_safety=_load_optional_json(args.split_safety),
        inspiration_coverage=_load_optional_json(args.inspiration_coverage),
        play_session_status=_load_optional_json(args.play_session_status),
    )
    write_json(args.output, gate)
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.write_text(_markdown(gate))
    print(gate["summary"])


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--queue", type=Path, default=REPO_ROOT / "artifacts/visual_analysis/render-review-queue.json")
    parser.add_argument("--render-analysis", type=Path, default=REPO_ROOT / "artifacts/visual_analysis/render-analysis.json")
    parser.add_argument("--dataset-audit", type=Path, default=REPO_ROOT / "artifacts/visual_analysis/dataset-audit.json")
    parser.add_argument("--train-ready-manifest", type=Path, default=REPO_ROOT / "artifacts/datasets/after-effects-train-ready/manifest.json")
    parser.add_argument("--readiness-report", type=Path, default=REPO_ROOT / "artifacts/datasets/after-effects-train-ready/readiness-report.json")
    parser.add_argument("--harness-status", type=Path, default=REPO_ROOT / "artifacts/ae_live_checks/_manual_harnesses/status.json")
    parser.add_argument("--training-preflight", type=Path, default=REPO_ROOT / "artifacts/datasets/lfm25-8b-a1b-after-effects-train-ready/training-preflight.json")
    parser.add_argument("--high-quality-manifest", type=Path, default=REPO_ROOT / "artifacts/datasets/after-effects-high-quality/manifest.json")
    parser.add_argument("--high-quality-preflight", type=Path, default=REPO_ROOT / "artifacts/datasets/lfm25-8b-a1b-after-effects-high-quality/training-preflight.json")
    parser.add_argument("--source-motion-audit", type=Path, default=REPO_ROOT / "artifacts/visual_analysis/source-motion-audit.json")
    parser.add_argument("--source-animation-quality", type=Path, default=REPO_ROOT / "artifacts/visual_analysis/source-animation-quality.json")
    parser.add_argument("--source-pattern-audit", type=Path, default=REPO_ROOT / "artifacts/visual_analysis/source-pattern-audit.json")
    parser.add_argument("--source-capability-audit", type=Path, default=REPO_ROOT / "artifacts/visual_analysis/source-capability-audit.json")
    parser.add_argument("--render-progression", type=Path, default=REPO_ROOT / "artifacts/visual_analysis/render-progression.json")
    parser.add_argument("--split-safety", type=Path, default=REPO_ROOT / "artifacts/visual_analysis/split-safety.json")
    parser.add_argument("--inspiration-coverage", type=Path, default=REPO_ROOT / "artifacts/visual_analysis/inspiration-coverage.json")
    parser.add_argument("--play-session-status", type=Path, default=REPO_ROOT / "artifacts/ae_live_checks/_play_session_harnesses/status.json")
    parser.add_argument("--output", type=Path, default=REPO_ROOT / "artifacts/datasets/after-effects-train-ready/quality-gate.json")
    parser.add_argument("--markdown-output", type=Path, default=REPO_ROOT / "artifacts/datasets/after-effects-train-ready/quality-gate.md")
    return parser.parse_args()


def _build_gate(
    *,
    queue: dict[str, Any] | None,
    render_analysis: dict[str, Any] | None,
    dataset_audit: dict[str, Any] | None,
    train_ready_manifest: dict[str, Any] | None,
    readiness_report: dict[str, Any] | None,
    harness_status: dict[str, Any] | None,
    training_preflight: dict[str, Any] | None,
    high_quality_manifest: dict[str, Any] | None = None,
    high_quality_preflight: dict[str, Any] | None = None,
    source_motion_audit: dict[str, Any] | None = None,
    source_animation_quality: dict[str, Any] | None = None,
    source_pattern_audit: dict[str, Any] | None = None,
    source_capability_audit: dict[str, Any] | None = None,
    render_progression: dict[str, Any] | None = None,
    split_safety: dict[str, Any] | None = None,
    inspiration_coverage: dict[str, Any] | None = None,
    play_session_status: dict[str, Any] | None = None,
) -> dict[str, Any]:
    checks = _checks(
        queue or {},
        render_analysis or {},
        dataset_audit or {},
        train_ready_manifest or {},
        readiness_report or {},
        harness_status or {},
        training_preflight or {},
        high_quality_manifest or {},
        high_quality_preflight or {},
        source_motion_audit or {},
        source_animation_quality or {},
        source_pattern_audit or {},
        source_capability_audit or {},
        render_progression or {},
        split_safety or {},
        inspiration_coverage or {},
        play_session_status or {},
    )
    return {"summary": {
        "technical_trainable_subset": _passed(checks, "training_preflight_ok"),
        "high_quality_trainable_subset": _passed(checks, "high_quality_subset_preflight_ok"),
        "full_dataset_ready": all(check["passed"] for check in checks),
        "failed_checks": [check["name"] for check in checks if not check["passed"]],
    }, "checks": checks, "next_actions": _next_actions(checks, readiness_report or {}, harness_status or {})}


def _checks(
    queue: dict[str, Any],
    render_analysis: dict[str, Any],
    dataset_audit: dict[str, Any],
    train_ready_manifest: dict[str, Any],
    readiness_report: dict[str, Any],
    harness_status: dict[str, Any],
    training_preflight: dict[str, Any],
    high_quality_manifest: dict[str, Any],
    high_quality_preflight: dict[str, Any],
    source_motion_audit: dict[str, Any],
    source_animation_quality: dict[str, Any],
    source_pattern_audit: dict[str, Any],
    source_capability_audit: dict[str, Any],
    render_progression: dict[str, Any],
    split_safety: dict[str, Any],
    inspiration_coverage: dict[str, Any],
    play_session_status: dict[str, Any],
) -> list[dict[str, Any]]:
    source_cases = readiness_report.get("case_count", queue.get("case_count", 0))
    train_ready = readiness_report.get("train_ready_count", train_ready_manifest.get("case_count", 0))
    render_debt = len(readiness_report.get("render_debt", []))
    missing_packs = readiness_report.get("coverage_gaps", {}).get("synthetic_packs", [])
    weak_ready = _weak_train_ready_cases(queue)
    harness_counts = harness_status.get("summary", {}).get("status_counts", {})
    harness_incomplete = sum(harness_counts.get(name, 0) for name in ["missing_project", "not_run", "script_error", "stale_project"])
    high_quality_count = int(high_quality_manifest.get("case_count", 0) or 0)
    source_motion_issues = int(source_motion_audit.get("summary", {}).get("cases_with_issues", 0) or 0)
    source_animation_issues = int(source_animation_quality.get("summary", {}).get("cases_with_issues", 0) or 0)
    pattern_gaps = int(source_pattern_audit.get("summary", {}).get("train_ready_pattern_gap_count", 0) or 0)
    capability_summary = source_capability_audit.get("summary", {})
    capability_ok = capability_summary.get("core_gap_count") == 0 and capability_summary.get("case_issue_count") == 0
    train_ready_capability_ok = capability_summary.get("train_ready_core_gap_count") == 0
    inspiration_gaps = int(inspiration_coverage.get("summary", {}).get("train_ready_gap_count", 0) or 0)
    play_summary = play_session_status.get("summary", {})
    play_script_count = int(play_summary.get("script_count", 0) or 0)
    play_completed = int(play_summary.get("completed_chunks", 0) or 0)
    play_failed = int(play_summary.get("failed_chunks", 0) or 0)
    play_ok = play_summary.get("ok") is True and play_script_count > 0 and play_completed == play_script_count and play_failed == 0
    progression_issues = int(render_progression.get("summary", {}).get("train_ready_issue_count", 0) or 0)
    split_safety_summary = split_safety.get("summary", {})
    return [
        _check("training_preflight_ok", bool(training_preflight.get("ok")), training_preflight.get("issues", [])),
        _check("high_quality_subset_preflight_ok", bool(high_quality_preflight.get("ok")) and high_quality_count > 0, {"case_count": high_quality_count, "issues": high_quality_preflight.get("issues", [])}),
        _check("no_source_motion_audit_issues", source_motion_issues == 0, {"cases_with_issues": source_motion_issues}),
        _check("no_source_animation_quality_issues", source_animation_issues == 0, {"cases_with_issues": source_animation_issues}),
        _check("train_ready_animation_patterns_ok", pattern_gaps == 0, {"train_ready_pattern_gap_count": pattern_gaps, "gaps": source_pattern_audit.get("train_ready_pattern_gaps", [])}),
        _check("source_capability_diversity_ok", capability_ok, capability_summary or {"missing": True}),
        _check("train_ready_capability_diversity_ok", train_ready_capability_ok, {
            "summary": capability_summary or {"missing": True},
            "unlocks": source_capability_audit.get("train_ready_gap_unlocks", []),
        }),
        _check("ae_play_session_harnesses_ok", play_ok, {"script_count": play_script_count, "completed_chunks": play_completed, "failed_chunks": play_failed}),
        _check("no_train_ready_render_progression_issues", progression_issues == 0, {"train_ready_issue_count": progression_issues, "cases": render_progression.get("train_ready_issue_cases", [])}),
        _check("train_ready_split_safety_ok", split_safety_summary.get("ok") is True, split_safety_summary or {"missing": True}),
        _check("no_weak_train_ready_cases", not weak_ready, {"weak_train_ready_cases": weak_ready}),
        _check("all_source_cases_train_ready", source_cases > 0 and train_ready == source_cases, {"source_cases": source_cases, "train_ready": train_ready}),
        _check("no_render_debt", render_debt == 0, {"render_debt": render_debt}),
        _check("all_synthetic_packs_train_ready", not missing_packs, {"missing_packs": missing_packs}),
        _check("web_inspiration_motifs_train_ready", inspiration_gaps == 0, {"train_ready_gap_count": inspiration_gaps}),
        _check("all_manual_harness_targets_renderable", harness_incomplete == 0, {"status_counts": harness_counts}),
        _check("no_actionable_render_warnings", dataset_audit.get("actionable_render_warning_count", 0) == 0, {"actionable_render_warning_count": dataset_audit.get("actionable_render_warning_count")}),
        _check("render_analysis_covers_train_ready_cases", render_analysis.get("summary", {}).get("case_count", 0) >= train_ready, {"rendered_cases": render_analysis.get("summary", {}).get("case_count", 0), "train_ready": train_ready}),
    ]


def _check(name: str, passed: bool, detail: Any) -> dict[str, Any]:
    return {"name": name, "passed": passed, "detail": detail}


def _passed(checks: list[dict[str, Any]], name: str) -> bool:
    return next((check["passed"] for check in checks if check["name"] == name), False)


def _next_actions(
    checks: list[dict[str, Any]],
    readiness_report: dict[str, Any],
    harness_status: dict[str, Any],
) -> list[str]:
    actions = []
    weak_check = next((check for check in checks if check["name"] == "no_weak_train_ready_cases"), None)
    weak_cases = (weak_check or {}).get("detail", {}).get("weak_train_ready_cases", [])
    if weak_cases:
        actions.append(f"Review or fix weak train-ready cases: {', '.join(weak_cases[:8])}")
    animation_check = next((check for check in checks if check["name"] == "no_source_animation_quality_issues"), None)
    if animation_check and not animation_check["passed"]:
        actions.append("Fix source-animation-quality issues, then rebuild data/after_effects_synthetic_cases.jsonl.")
    pattern_check = next((check for check in checks if check["name"] == "train_ready_animation_patterns_ok"), None)
    if pattern_check and not pattern_check["passed"]:
        gaps = pattern_check.get("detail", {}).get("gaps", [])
        targets = [f"{gap['pattern']}={gap['case_ids'][0]}" for gap in gaps if gap.get("case_ids")]
        actions.append(f"Render/promote animation-pattern targets: {', '.join(targets[:6])}")
    if not _passed(checks, "source_capability_diversity_ok"):
        actions.append("Add or revise source JSX cases to close AE capability gaps.")
    if not _passed(checks, "train_ready_capability_diversity_ok"):
        actions.append("Render/promote cases that unlock missing train-ready AE capabilities.")
        capability_check = next((check for check in checks if check["name"] == "train_ready_capability_diversity_ok"), None)
        unlocks = (capability_check or {}).get("detail", {}).get("unlocks", [])
        if unlocks:
            pairs = [f"{item['capability']}={item['case_ids'][0]}" for item in unlocks if item.get("case_ids")]
            actions.append(f"First capability-unlock render targets: {', '.join(pairs)}")
    if not _passed(checks, "ae_play_session_harnesses_ok"):
        actions.append("Run scripts/run_ae_play_session_harnesses.py to exercise playable AE review comps.")
    if not _passed(checks, "no_train_ready_render_progression_issues"):
        actions.append("Fix train-ready render progression issues or demote those renders until rerendered.")
    if not _passed(checks, "train_ready_split_safety_ok"):
        actions.append("Rebalance train-ready splits or add contrastive renders for split-safety issues.")
    if not _passed(checks, "all_manual_harness_targets_renderable"):
        actions.append("Run AE run_all_harnesses.jsx, then rerun check_ae_manual_harnesses.py.")
    if not _passed(checks, "no_render_debt"):
        top = [item["case_id"] for item in readiness_report.get("render_debt", [])[:8]]
        actions.append(f"Render/rerender priority debt cases: {', '.join(top) or '-'}")
    if not _passed(checks, "all_synthetic_packs_train_ready"):
        gaps = readiness_report.get("coverage_gaps", {}).get("synthetic_packs", [])
        actions.append(f"Promote missing train-ready packs: {', '.join(gaps) or '-'}")
        unlocks = [
            f"{item['synthetic_pack']}={item['case_id']}"
            for item in readiness_report.get("coverage_unlocks", [])
        ]
        if unlocks:
            actions.append(f"First pack-unlock render targets: {', '.join(unlocks)}")
    inspiration_check = next((check for check in checks if check["name"] == "web_inspiration_motifs_train_ready"), None)
    if inspiration_check and not inspiration_check["passed"]:
        actions.append("Run _manual_harnesses_motif_gaps/run_all_harnesses.jsx to close web inspiration motif gaps.")
    if harness_status.get("summary", {}).get("runner_report_exists") is False:
        actions.append("No runner_report.txt found; the all-in-one AE runner has not completed.")
    return actions


def _weak_train_ready_cases(queue: dict[str, Any]) -> list[str]:
    weak = []
    for item in queue.get("items", []):
        if not item.get("train_ready"):
            continue
        if _is_weak_train_ready(item):
            weak.append(item["case_id"])
    return weak


def _is_weak_train_ready(item: dict[str, Any]) -> bool:
    return (
        item.get("quality_priority") != "pass"
        or bool(item.get("warnings"))
        or item.get("motion_profile") in {"sparse", "stalled_sections"}
        or float(item.get("longest_stall_ratio") or 0.0) > 0.45
    )


def _markdown(gate: dict[str, Any]) -> str:
    lines = [
        "# Dataset Quality Gate",
        "",
        f"- technical trainable subset: {gate['summary']['technical_trainable_subset']}",
        f"- high-quality trainable subset: {gate['summary']['high_quality_trainable_subset']}",
        f"- full dataset ready: {gate['summary']['full_dataset_ready']}",
        f"- failed checks: {', '.join(gate['summary']['failed_checks']) or '-'}",
        "",
        "## Checks",
        "",
        "| passed | check | detail |",
        "| --- | --- | --- |",
    ]
    for check in gate["checks"]:
        lines.append(f"| {check['passed']} | {check['name']} | {_detail(check['detail'])} |")
    lines.extend(["", "## Next Actions", ""])
    lines.extend(f"- {action}" for action in gate["next_actions"])
    return "\n".join(lines) + "\n"


def _detail(value: Any) -> str:
    if isinstance(value, (dict, list)):
        return json.dumps(value, sort_keys=True)
    return str(value)


def _load_optional_json(path: Path) -> dict[str, Any] | None:
    return json.loads(path.read_text()) if path.exists() else None


if __name__ == "__main__":
    main()
