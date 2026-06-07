from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

from after_effects_pipeline.case_records import case_to_chat_record, split_cases
from after_effects_pipeline.render_overlap import build_render_overlap_audit
from after_effects_pipeline.types import SplitConfig
from after_effects_pipeline.utils import write_json, write_jsonl

REPO_ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    args = _parse_args()
    records = _load_records(args.dataset)
    queue = json.loads(args.queue.read_text())
    selected = _selected_records(records, queue, strict_quality=args.strict_quality)
    splits = split_cases(selected, SplitConfig(seed=args.seed))
    overlap_report = None
    if args.render_analysis.exists():
        render_analysis = json.loads(args.render_analysis.read_text())
        splits, overlap_report = _rebalance_overlap_splits(splits, render_analysis)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    write_jsonl(args.output_dir / "cases.jsonl", selected)
    write_jsonl(args.output_dir / "chat.jsonl", [case_to_chat_record(case) for case in selected])
    for split, cases in splits.items():
        write_jsonl(args.output_dir / f"{split}.jsonl", [case_to_chat_record(case) for case in cases])
    write_json(args.output_dir / "manifest.json", _manifest(queue, selected, splits, args.strict_quality, overlap_report))
    (args.output_dir / "README.md").write_text(_readme(queue, selected, splits, args.strict_quality, overlap_report))
    print(
        {
            "output_dir": str(args.output_dir),
            "case_count": len(selected),
            "splits": {name: len(cases) for name, cases in splits.items()},
        }
    )


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=Path, default=REPO_ROOT / "data/after_effects_synthetic_cases.jsonl")
    parser.add_argument("--queue", type=Path, default=REPO_ROOT / "artifacts/visual_analysis/render-review-queue.json")
    parser.add_argument("--output-dir", type=Path, default=REPO_ROOT / "artifacts/datasets/after-effects-train-ready")
    parser.add_argument("--render-analysis", type=Path, default=REPO_ROOT / "artifacts/visual_analysis/render-analysis.json")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--strict-quality", action="store_true")
    return parser.parse_args()


def _load_records(path: Path) -> dict[str, dict[str, Any]]:
    records = {}
    for line in path.read_text().splitlines():
        if line.strip():
            record = json.loads(line)
            records[record["case_id"]] = record
    return records


def _selected_records(
    records: dict[str, dict[str, Any]],
    queue: dict[str, Any],
    *,
    strict_quality: bool = False,
) -> list[dict[str, Any]]:
    selected = []
    for item in queue.get("items", []):
        if not item.get("train_ready"):
            continue
        if strict_quality and _is_weak_train_ready(item):
            continue
        record = records[item["case_id"]]
        selected.append(
            {
                **record,
                "quality_score": item["quality_score"],
                "visual_review_decision": item["decision"],
                "visual_review_reasons": item["reasons"],
                "visual_review_warnings": item["warnings"],
                "visual_review_notes": item["notes"],
                "motion_profile": item["motion_profile"],
                "active_frame_ratio": item["active_frame_ratio"],
                "longest_stall_ratio": item["longest_stall_ratio"],
                "render_path": item["render_path"],
                "contact_sheet_path": item["contact_sheet_path"],
            }
        )
    return selected


def _manifest(
    queue: dict[str, Any],
    selected: list[dict[str, Any]],
    splits: dict[str, list[dict[str, Any]]],
    strict_quality: bool = False,
    overlap_report: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "strict_quality": strict_quality,
        "source_queue_case_count": queue.get("case_count", 0),
        "source_queue_decision_counts": queue.get("decision_counts", {}),
        "case_count": len(selected),
        "case_ids": [case["case_id"] for case in selected],
        "aspect_ratios": _aspect_counts(selected),
        "synthetic_pack_counts": _synthetic_pack_counts(selected),
        "top_tag_counts": _top_tag_counts(selected),
        "excluded_decision_counts": _excluded_decision_counts(queue),
        "excluded_weak_train_ready_count": _weak_train_ready_count(queue),
        "splits": {name: len(cases) for name, cases in splits.items()},
        "split_overlap_summary": (overlap_report or {}).get("summary", {}),
    }


def _readme(
    queue: dict[str, Any],
    selected: list[dict[str, Any]],
    splits: dict[str, list[dict[str, Any]]],
    strict_quality: bool = False,
    overlap_report: dict[str, Any] | None = None,
) -> str:
    split_text = ", ".join(f"{name}={len(cases)}" for name, cases in splits.items())
    decision_text = ", ".join(
        f"{name}={count}" for name, count in queue.get("decision_counts", {}).items()
    )
    aspect_text = ", ".join(
        f"{name}={count}" for name, count in _aspect_counts(selected).items()
    )
    pack_text = ", ".join(
        f"{name}={count}" for name, count in _synthetic_pack_counts(selected).items()
    )
    excluded_text = ", ".join(
        f"{name}={count}" for name, count in _excluded_decision_counts(queue).items()
    )
    overlap_summary = (overlap_report or {}).get("summary", {})
    return f"""# After Effects Train-Ready Dataset

This export contains only cases promoted by `render-review-queue`.
Strict quality mode: {strict_quality}.

- selected cases: {len(selected)}
- source queue cases: {queue.get("case_count", 0)}
- source queue decisions: {decision_text}
- excluded queue decisions: {excluded_text or "none"}
- splits: {split_text}
- aspect ratios: {aspect_text}
- synthetic packs: {pack_text}
- same-split visual overlaps: {overlap_summary.get("same_split_overlap_count", "not checked")}

Rows include the canonical JSX training fields plus visual-review metadata,
render paths, contact-sheet paths, and motion summary fields. Cases that still
need missing renders, stale rerenders, or visual fixes are excluded.
When strict quality mode is enabled, accepted cases with sparse/stalled motion,
non-pass visual priority, crowding warnings, or long stalls are also excluded.
"""


def _aspect_counts(cases: list[dict[str, Any]]) -> dict[str, int]:
    counts = Counter(_aspect_label(case) for case in cases)
    return dict(sorted(counts.items()))


def _aspect_label(case: dict[str, Any]) -> str:
    expected = case.get("expected", {})
    width = int(expected.get("width", 0))
    height = int(expected.get("height", 0))
    if width == height:
        return "square_1x1"
    if width > height:
        return "landscape_16x9"
    return "vertical_9x16"


def _synthetic_pack_counts(cases: list[dict[str, Any]]) -> dict[str, int]:
    counts = Counter(
        tag
        for case in cases
        for tag in case.get("tags", [])
        if tag.startswith("synthetic-")
    )
    return dict(sorted(counts.items()))


def _top_tag_counts(cases: list[dict[str, Any]], limit: int = 24) -> dict[str, int]:
    counts = Counter(tag for case in cases for tag in case.get("tags", []))
    return dict(counts.most_common(limit))


def _excluded_decision_counts(queue: dict[str, Any]) -> dict[str, int]:
    counts = Counter(
        item.get("decision", "unknown")
        for item in queue.get("items", [])
        if not item.get("train_ready")
    )
    return dict(sorted(counts.items()))


def _weak_train_ready_count(queue: dict[str, Any]) -> int:
    return sum(
        1 for item in queue.get("items", [])
        if item.get("train_ready") and _is_weak_train_ready(item)
    )


def _is_weak_train_ready(item: dict[str, Any]) -> bool:
    return (
        item.get("quality_priority") != "pass"
        or bool(item.get("warnings"))
        or item.get("motion_profile") in {"sparse", "stalled_sections"}
        or float(item.get("longest_stall_ratio") or 0.0) > 0.45
    )


def _rebalance_overlap_splits(
    splits: dict[str, list[dict[str, Any]]],
    render_analysis: dict[str, Any],
) -> tuple[dict[str, list[dict[str, Any]]], dict[str, Any]]:
    balanced = {name: list(cases) for name, cases in splits.items()}
    report = _split_overlap_report(balanced, render_analysis)
    for _ in range(12):
        pair = next((item for item in report["potential_overlaps"] if item.get("same_split")), None)
        if not pair:
            break
        candidate = _best_swap(balanced, render_analysis, pair, report)
        if not candidate:
            break
        source, target, source_index, target_index, report = candidate
        balanced[source][source_index], balanced[target][target_index] = (
            balanced[target][target_index],
            balanced[source][source_index],
        )
        report = _split_overlap_report(balanced, render_analysis)
    return balanced, report


def _best_swap(
    splits: dict[str, list[dict[str, Any]]],
    render_analysis: dict[str, Any],
    pair: dict[str, Any],
    current_report: dict[str, Any],
) -> tuple[str, str, int, int, dict[str, Any]] | None:
    source = pair["split_a"]
    if not source:
        return None
    source_index = _case_index(splits[source], pair["b"])
    if source_index is None:
        return None
    best = None
    current = current_report["summary"]["same_split_overlap_count"]
    for target, target_cases in splits.items():
        if target == source:
            continue
        for target_index, _target_case in enumerate(target_cases):
            trial = {name: list(cases) for name, cases in splits.items()}
            trial[source][source_index], trial[target][target_index] = (
                trial[target][target_index],
                trial[source][source_index],
            )
            report = _split_overlap_report(trial, render_analysis)
            score = report["summary"]["same_split_overlap_count"]
            if score < current and (best is None or score < best[-1]["summary"]["same_split_overlap_count"]):
                best = (source, target, source_index, target_index, report)
    return best


def _split_overlap_report(
    splits: dict[str, list[dict[str, Any]]],
    render_analysis: dict[str, Any],
) -> dict[str, Any]:
    return build_render_overlap_audit(
        render_analysis,
        split_by_case=_split_by_case(splits),
    )


def _split_by_case(splits: dict[str, list[dict[str, Any]]]) -> dict[str, str]:
    return {
        case["case_id"]: split
        for split, cases in splits.items()
        for case in cases
    }


def _case_index(cases: list[dict[str, Any]], case_id: str) -> int | None:
    return next((index for index, case in enumerate(cases) if case["case_id"] == case_id), None)


if __name__ == "__main__":
    main()
