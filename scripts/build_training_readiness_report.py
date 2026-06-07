from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

from after_effects_pipeline.inspiration_coverage import MOTIF_RULES
from after_effects_pipeline.utils import write_json

REPO_ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    args = _parse_args()
    records = _load_records(args.dataset)
    queue = json.loads(args.queue.read_text())
    report = _build_report(records, queue)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    write_json(args.output, report)
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.write_text(_markdown(report))
    print(
        {
            "case_count": report["case_count"],
            "train_ready_count": report["train_ready_count"],
            "render_debt_count": len(report["render_debt"]),
            "missing_train_ready_packs": report["coverage_gaps"]["synthetic_packs"],
        }
    )


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=Path, default=REPO_ROOT / "data/after_effects_synthetic_cases.jsonl")
    parser.add_argument("--queue", type=Path, default=REPO_ROOT / "artifacts/visual_analysis/render-review-queue.json")
    parser.add_argument("--output", type=Path, default=REPO_ROOT / "artifacts/datasets/after-effects-train-ready/readiness-report.json")
    parser.add_argument("--markdown-output", type=Path, default=REPO_ROOT / "artifacts/datasets/after-effects-train-ready/readiness-report.md")
    return parser.parse_args()


def _load_records(path: Path) -> dict[str, dict[str, Any]]:
    records = {}
    for line in path.read_text().splitlines():
        if line.strip():
            record = json.loads(line)
            records[record["case_id"]] = record
    return records


def _build_report(
    records: dict[str, dict[str, Any]],
    queue: dict[str, Any],
) -> dict[str, Any]:
    items = queue.get("items", [])
    ready_ids = {item["case_id"] for item in items if item.get("train_ready")}
    ready_records = [records[case_id] for case_id in ready_ids if case_id in records]
    all_records = list(records.values())
    excluded_items = [item for item in items if not item.get("train_ready")]
    coverage_gaps = _coverage_gaps(all_records, ready_records)
    motif_gap_cases = _motif_gap_cases(all_records, ready_records)
    render_debt = _render_debt(excluded_items, records, ready_records, motif_gap_cases)
    return {
        "case_count": len(all_records),
        "train_ready_count": len(ready_records),
        "train_ready_ratio": len(ready_records) / len(all_records) if all_records else 0.0,
        "queue_decision_counts": queue.get("decision_counts", {}),
        "aspect_ratios": {
            "all": _aspect_counts(all_records),
            "train_ready": _aspect_counts(ready_records),
            "excluded": _aspect_counts([records[item["case_id"]] for item in excluded_items if item["case_id"] in records]),
        },
        "synthetic_packs": {
            "all": _pack_counts(all_records),
            "train_ready": _pack_counts(ready_records),
            "excluded": _pack_counts([records[item["case_id"]] for item in excluded_items if item["case_id"] in records]),
        },
        "top_tags": {
            "all": _top_tags(all_records),
            "train_ready": _top_tags(ready_records),
            "excluded": _top_tags([records[item["case_id"]] for item in excluded_items if item["case_id"] in records]),
        },
        "coverage_gaps": coverage_gaps,
        "coverage_unlocks": _coverage_unlocks(coverage_gaps, render_debt),
        "render_debt": render_debt,
    }


def _coverage_gaps(
    all_records: list[dict[str, Any]],
    ready_records: list[dict[str, Any]],
) -> dict[str, list[str]]:
    all_packs = set(_pack_counts(all_records))
    ready_packs = set(_pack_counts(ready_records))
    all_tags = {tag for record in all_records for tag in record.get("tags", [])}
    ready_tags = {tag for record in ready_records for tag in record.get("tags", [])}
    return {
        "synthetic_packs": sorted(all_packs - ready_packs),
        "tags": sorted((all_tags - ready_tags) - all_packs),
    }


def _render_debt(
    excluded_items: list[dict[str, Any]],
    records: dict[str, dict[str, Any]],
    ready_records: list[dict[str, Any]],
    motif_gap_cases: dict[str, list[str]],
) -> list[dict[str, Any]]:
    ready_pack_counts = _pack_counts(ready_records)
    ready_tags = {tag for record in ready_records for tag in record.get("tags", [])}
    debts = []
    for item in excluded_items:
        record = records.get(item["case_id"])
        if not record:
            continue
        packs = [tag for tag in record.get("tags", []) if tag.startswith("synthetic-")]
        missing_packs = [pack for pack in packs if ready_pack_counts.get(pack, 0) == 0]
        missing_tags = [tag for tag in record.get("tags", []) if tag not in ready_tags]
        motif_gaps = motif_gap_cases.get(item["case_id"], [])
        debt = {
            "case_id": item["case_id"],
            "decision": item["decision"],
            "priority_score": _priority_score(
                item["decision"],
                missing_packs,
                missing_tags,
                motif_gaps,
            ),
            "aspect_ratio": _aspect_label(record),
            "synthetic_packs": packs,
            "coverage_reasons": _coverage_reasons(missing_packs, missing_tags, motif_gaps),
            "motif_gap_unlocks": motif_gaps,
            "queue_reasons": item.get("reasons", []),
            "source_repo_path": record.get("source_repo_path"),
        }
        debts.append(debt)
    debts.sort(key=lambda debt: (-debt["priority_score"], debt["case_id"]))
    return debts


def _priority_score(
    decision: str,
    missing_packs: list[str],
    missing_tags: list[str],
    motif_gaps: list[str],
) -> int:
    score = {"rerender_stale": 100, "render_missing": 80}.get(decision, 60)
    score += len(missing_packs) * 30
    score += min(len(missing_tags), 8) * 3
    score += len(motif_gaps) * 24
    return score


def _coverage_reasons(
    missing_packs: list[str],
    missing_tags: list[str],
    motif_gaps: list[str],
) -> list[str]:
    reasons = [f"pack absent from train-ready: {pack}" for pack in missing_packs]
    reasons.extend(f"web motif absent from train-ready: {motif}" for motif in motif_gaps)
    reasons.extend(f"tag absent from train-ready: {tag}" for tag in missing_tags[:8])
    return reasons


def _motif_gap_cases(
    all_records: list[dict[str, Any]],
    ready_records: list[dict[str, Any]],
) -> dict[str, list[str]]:
    ready_case_ids = {record["case_id"] for record in ready_records}
    case_to_motifs: dict[str, list[str]] = {}
    for motif, tags in sorted(MOTIF_RULES.items()):
        matching = [record for record in all_records if tags & set(record.get("tags", []))]
        if not matching or any(record["case_id"] in ready_case_ids for record in matching):
            continue
        for record in matching:
            case_to_motifs.setdefault(record["case_id"], []).append(motif)
    return case_to_motifs


def _coverage_unlocks(
    coverage_gaps: dict[str, list[str]],
    render_debt: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    unlocks = []
    for pack in coverage_gaps["synthetic_packs"]:
        candidate = next(
            (debt for debt in render_debt if pack in debt["synthetic_packs"]),
            None,
        )
        if candidate:
            unlocks.append(
                {
                    "synthetic_pack": pack,
                    "case_id": candidate["case_id"],
                    "decision": candidate["decision"],
                    "priority_score": candidate["priority_score"],
                    "aspect_ratio": candidate["aspect_ratio"],
                    "coverage_reasons": candidate["coverage_reasons"],
                }
            )
    return unlocks


def _aspect_counts(cases: list[dict[str, Any]]) -> dict[str, int]:
    return dict(sorted(Counter(_aspect_label(case) for case in cases).items()))


def _aspect_label(case: dict[str, Any]) -> str:
    expected = case.get("expected", {})
    width = int(expected.get("width", 0))
    height = int(expected.get("height", 0))
    if width == height:
        return "square_1x1"
    return "landscape_16x9" if width > height else "vertical_9x16"


def _pack_counts(cases: list[dict[str, Any]]) -> dict[str, int]:
    counts = Counter(
        tag
        for case in cases
        for tag in case.get("tags", [])
        if tag.startswith("synthetic-")
    )
    return dict(sorted(counts.items()))


def _top_tags(cases: list[dict[str, Any]], limit: int = 24) -> dict[str, int]:
    return dict(Counter(tag for case in cases for tag in case.get("tags", [])).most_common(limit))


def _markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Training Readiness Report",
        "",
        f"- total cases: {report['case_count']}",
        f"- train-ready cases: {report['train_ready_count']}",
        f"- train-ready ratio: {report['train_ready_ratio']:.3f}",
        f"- queue decisions: {_inline_counts(report['queue_decision_counts'])}",
        "",
        "## Coverage Gaps",
        "",
        f"- synthetic packs absent from train-ready: {', '.join(report['coverage_gaps']['synthetic_packs']) or '-'}",
        f"- tags absent from train-ready: {', '.join(report['coverage_gaps']['tags'][:30]) or '-'}",
        "",
        "## Coverage Unlocks",
        "",
        "| missing pack | first render target | decision | priority | aspect | unlock reasons |",
        "| --- | --- | --- | ---: | --- | --- |",
    ]
    for item in report["coverage_unlocks"]:
        reasons = "; ".join(item["coverage_reasons"]) or "-"
        lines.append(
            f"| {item['synthetic_pack']} | {item['case_id']} | {item['decision']} | "
            f"{item['priority_score']} | {item['aspect_ratio']} | {reasons} |"
        )
    lines.extend([
        "",
        "## Aspect Ratios",
        "",
        f"- all: {_inline_counts(report['aspect_ratios']['all'])}",
        f"- train-ready: {_inline_counts(report['aspect_ratios']['train_ready'])}",
        f"- excluded: {_inline_counts(report['aspect_ratios']['excluded'])}",
        "",
        "## Render Debt Priority",
        "",
        "| priority | case | decision | aspect | coverage reasons |",
        "| ---: | --- | --- | --- | --- |",
    ])
    for item in report["render_debt"]:
        reasons = "; ".join(item["coverage_reasons"]) or "-"
        lines.append(
            f"| {item['priority_score']} | {item['case_id']} | {item['decision']} | "
            f"{item['aspect_ratio']} | {reasons} |"
        )
    return "\n".join(lines) + "\n"


def _inline_counts(counts: dict[str, int]) -> str:
    return ", ".join(f"{key}={value}" for key, value in counts.items()) or "-"


if __name__ == "__main__":
    main()
