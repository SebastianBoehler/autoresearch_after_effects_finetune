from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any


def build_split_safety_audit(
    render_overlap: dict[str, Any],
    *,
    split_by_case: dict[str, str],
    max_animation_signature_per_split: int = 2,
) -> dict[str, Any]:
    assigned_cases = _assigned_cases(render_overlap.get("cases", []), split_by_case)
    pair_issues = _same_split_overlap_issues(render_overlap.get("potential_overlaps", []))
    signature_counts = _signature_counts(assigned_cases, max_animation_signature_per_split)
    issues = [*pair_issues, *signature_counts["issues"]]
    return {
        "summary": {
            "case_count": len(assigned_cases),
            "split_count": len({case["split"] for case in assigned_cases}),
            "same_split_overlap_count": len(pair_issues),
            "repeated_signature_issue_count": len(signature_counts["issues"]),
            "max_animation_signature_per_split": max_animation_signature_per_split,
            "issue_count": len(issues),
            "ok": not issues,
        },
        "split_case_counts": dict(Counter(case["split"] for case in assigned_cases).most_common()),
        "animation_signature_counts_by_split": signature_counts["counts"],
        "issues": issues,
    }


def split_safety_markdown(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# Train-Ready Split Safety Audit",
        "",
        "- built from render-overlap signatures and train-ready split files",
        f"- assigned cases: {summary['case_count']}",
        f"- splits: {summary['split_count']}",
        f"- same-split overlaps: {summary['same_split_overlap_count']}",
        f"- repeated signature issues: {summary['repeated_signature_issue_count']}",
        f"- max animation signature per split: {summary['max_animation_signature_per_split']}",
        f"- ok: {summary['ok']}",
        "",
        "## Issues",
        "",
    ]
    if payload["issues"]:
        lines.extend(["| type | split | cases | detail |", "| --- | --- | --- | --- |"])
        for item in payload["issues"]:
            lines.append(
                f"| {item['type']} | {item.get('split', '-')} | "
                f"{', '.join(item.get('case_ids', []))} | {_issue_detail(item)} |"
            )
    else:
        lines.append("- none")
    lines.extend(["", "## Animation Signature Counts", ""])
    for split, counts in payload["animation_signature_counts_by_split"].items():
        lines.append(f"### {split}")
        for signature, count in counts.items():
            lines.append(f"- {signature}: {count}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def _assigned_cases(cases: list[dict[str, Any]], split_by_case: dict[str, str]) -> list[dict[str, Any]]:
    assigned = []
    for case in cases:
        case_id = case.get("case_id")
        split = split_by_case.get(case_id)
        if split:
            assigned.append({**case, "split": split})
    return sorted(assigned, key=lambda item: (item["split"], item["case_id"]))


def _same_split_overlap_issues(pairs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    issues = []
    for pair in pairs:
        if not pair.get("same_split"):
            continue
        issues.append(
            {
                "type": "same_split_overlap",
                "split": pair.get("split_a"),
                "case_ids": [pair["a"], pair["b"]],
                "score": pair.get("score"),
                "shared_signals": pair.get("shared_signals", []),
            }
        )
    return issues


def _signature_counts(
    cases: list[dict[str, Any]],
    max_animation_signature_per_split: int,
) -> dict[str, Any]:
    buckets: dict[str, dict[str, list[str]]] = defaultdict(lambda: defaultdict(list))
    for case in cases:
        buckets[case["split"]][case["animation_signature"]].append(case["case_id"])
    counts = {}
    issues = []
    for split in sorted(buckets):
        counts[split] = {}
        for signature, case_ids in sorted(buckets[split].items()):
            counts[split][signature] = len(case_ids)
            if len(case_ids) > max_animation_signature_per_split:
                issues.append(
                    {
                        "type": "repeated_animation_signature",
                        "split": split,
                        "animation_signature": signature,
                        "count": len(case_ids),
                        "case_ids": sorted(case_ids),
                    }
                )
    return {"counts": counts, "issues": issues}


def _issue_detail(item: dict[str, Any]) -> str:
    if item["type"] == "same_split_overlap":
        signals = ", ".join(item.get("shared_signals", [])) or "-"
        return f"score={item.get('score')}; shared={signals}"
    return f"{item.get('animation_signature')} count={item.get('count')}"
