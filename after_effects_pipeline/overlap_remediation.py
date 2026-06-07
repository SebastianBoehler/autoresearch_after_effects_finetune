from __future__ import annotations

from collections import Counter
from typing import Any

GENERIC_TAGS = {
    "keyframes",
    "expression",
    "expressions",
    "motion-graphics",
    "social",
    "typography",
}
ASPECT_TAGS = {"landscape", "square", "vertical"}


def build_overlap_remediation(
    *,
    render_overlap: dict[str, Any],
    source_pattern_audit: dict[str, Any],
    render_queue: dict[str, Any],
) -> dict[str, Any]:
    queue_by_case = {item["case_id"]: item for item in render_queue.get("items", [])}
    source_by_case = {item["case_id"]: item for item in source_pattern_audit.get("cases", [])}
    render_pairs = {_pair_key(item["a"], item["b"]): item for item in render_overlap.get("potential_overlaps", [])}
    source_pairs = {
        _pair_key(item["a"], item["b"]): item
        for item in source_pattern_audit.get("pattern_overlap_pairs", [])
    }
    pairs = [
        _pair_payload(key, render_pairs.get(key), source_pairs.get(key), queue_by_case, source_by_case)
        for key in sorted(set(render_pairs) | set(source_pairs))
    ]
    status_counts = Counter(pair["status"] for pair in pairs)
    return {
        "summary": {
            "pair_count": len(pairs),
            "render_overlap_pair_count": len(render_pairs),
            "source_pattern_overlap_pair_count": len(source_pairs),
            "dual_overlap_pair_count": sum(pair["has_render_overlap"] and pair["has_source_pattern_overlap"] for pair in pairs),
            "same_split_pair_count": sum(pair["same_split"] for pair in pairs),
            "high_risk_pair_count": sum(pair["priority"] == "high" for pair in pairs),
            "train_ready_pair_count": sum(pair["both_train_ready"] for pair in pairs),
            "source_pattern_contrast_pair_count": sum(
                pair["has_source_pattern_overlap"] and bool(pair["contrast_signals"]) for pair in pairs
            ),
            "thin_source_pattern_pair_count": sum(_is_thin_source_pair(pair) for pair in pairs),
            "status_counts": dict(sorted(status_counts.items())),
        },
        "pairs": sorted(pairs, key=_sort_key),
        "recommendations": _recommendations(pairs),
    }


def render_overlap_remediation_markdown(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# Overlap Remediation Audit",
        "",
        "Combines third-frame render overlap with static source animation-pattern overlap.",
        "",
        "## Summary",
        "",
        f"- pairs: {summary['pair_count']}",
        f"- render overlap pairs: {summary['render_overlap_pair_count']}",
        f"- source-pattern overlap pairs: {summary['source_pattern_overlap_pair_count']}",
        f"- dual overlap pairs: {summary['dual_overlap_pair_count']}",
        f"- same-split pairs: {summary['same_split_pair_count']}",
        f"- high-risk pairs: {summary['high_risk_pair_count']}",
        f"- train-ready pairs: {summary['train_ready_pair_count']}",
        f"- source-pattern pairs with contrast: {summary['source_pattern_contrast_pair_count']}",
        f"- thin source-pattern pairs: {summary['thin_source_pattern_pair_count']}",
        f"- statuses: {_counts_text(summary['status_counts'])}",
        "",
        "## Pairs",
        "",
        "| priority | status | case A | case B | render | source | train-ready | shared signals | contrast signals |",
        "| --- | --- | --- | --- | ---: | ---: | --- | --- | --- |",
    ]
    for pair in payload["pairs"][:40]:
        lines.append(
            f"| {pair['priority']} | {pair['status']} | {pair['a']} | {pair['b']} | "
            f"{_score(pair['render_score'])} | {_score(pair['source_pattern_score'])} | "
            f"{pair['both_train_ready']} | {_signals(pair)} | {_contrast(pair)} |"
        )
    if not payload["pairs"]:
        lines.append("| - | - | - | - | - | - | False | - | - |")
    lines.extend(["", "## Recommendations", ""])
    lines.extend(f"- {item}" for item in payload["recommendations"])
    return "\n".join(lines) + "\n"


def _pair_payload(
    key: tuple[str, str],
    render_pair: dict[str, Any] | None,
    source_pair: dict[str, Any] | None,
    queue_by_case: dict[str, dict[str, Any]],
    source_by_case: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    a, b = key
    both_ready = bool(queue_by_case.get(a, {}).get("train_ready") and queue_by_case.get(b, {}).get("train_ready"))
    same_split = bool((render_pair or {}).get("same_split"))
    status = _status(render_pair, source_pair, same_split, both_ready)
    return {
        "a": a,
        "b": b,
        "status": status,
        "priority": _priority(status),
        "has_render_overlap": render_pair is not None,
        "has_source_pattern_overlap": source_pair is not None,
        "same_split": same_split,
        "both_train_ready": both_ready,
        "render_score": (render_pair or {}).get("score"),
        "source_pattern_score": (source_pair or {}).get("score"),
        "shared_render_signals": (render_pair or {}).get("shared_signals", []),
        "shared_source_patterns": (source_pair or {}).get("shared_patterns", []),
        "contrast_signals": _contrast_signals(a, b, queue_by_case, source_by_case),
        "decisions": {
            a: queue_by_case.get(a, {}).get("decision", "unknown"),
            b: queue_by_case.get(b, {}).get("decision", "unknown"),
        },
    }


def _status(
    render_pair: dict[str, Any] | None,
    source_pair: dict[str, Any] | None,
    same_split: bool,
    both_ready: bool,
) -> str:
    if same_split:
        return "same_split_overlap"
    if render_pair and source_pair:
        return "dual_render_source_overlap"
    if render_pair and both_ready:
        return "train_ready_render_watch"
    if render_pair:
        return "render_metric_watch"
    return "source_pattern_watch"


def _priority(status: str) -> str:
    if status in {"same_split_overlap", "dual_render_source_overlap"}:
        return "high"
    if status == "train_ready_render_watch":
        return "medium"
    return "low"


def _recommendations(pairs: list[dict[str, Any]]) -> list[str]:
    if any(pair["status"] == "same_split_overlap" for pair in pairs):
        return ["move same-split overlap pairs apart before training export"]
    actions = []
    if any(pair["status"] == "dual_render_source_overlap" for pair in pairs):
        actions.append("diversify or manually review dual render/source overlap pairs")
    if any(pair["status"] == "train_ready_render_watch" for pair in pairs):
        actions.append("keep train-ready render-overlap pairs split apart and review contact sheets before promotion")
    if any(pair["status"] == "source_pattern_watch" for pair in pairs):
        actions.append("when promoting source-pattern overlap pairs, prefer different splits or add contrastive animation details")
    if any(_is_thin_source_pair(pair) for pair in pairs):
        actions.append("prioritize source edits for thin source-pattern pairs with fewer than two contrast signals")
    return actions or ["no overlap remediation needed at current thresholds"]


def _is_thin_source_pair(pair: dict[str, Any]) -> bool:
    return (
        pair["has_source_pattern_overlap"]
        and not pair["has_render_overlap"]
        and len(pair["contrast_signals"]) < 2
    )


def _sort_key(pair: dict[str, Any]) -> tuple[int, float, str, str]:
    priority = {"high": 0, "medium": 1, "low": 2}[pair["priority"]]
    score = max(float(pair["render_score"] or 0), float(pair["source_pattern_score"] or 0))
    return (priority, -score, pair["a"], pair["b"])


def _pair_key(a: str, b: str) -> tuple[str, str]:
    return tuple(sorted((a, b)))


def _score(value: float | None) -> str:
    return "-" if value is None else f"{value:.3f}"


def _signals(pair: dict[str, Any]) -> str:
    signals = [*pair["shared_render_signals"], *pair["shared_source_patterns"]]
    return ", ".join(signals[:8]) or "-"


def _contrast(pair: dict[str, Any]) -> str:
    return ", ".join(pair["contrast_signals"][:8]) or "-"


def _contrast_signals(
    a: str,
    b: str,
    queue_by_case: dict[str, dict[str, Any]],
    source_by_case: dict[str, dict[str, Any]],
) -> list[str]:
    signals = []
    source_a = source_by_case.get(a, {})
    source_b = source_by_case.get(b, {})
    for key in ("layer_mix", "motion_driver", "temporal_stage"):
        left = source_a.get(key)
        right = source_b.get(key)
        if left and right and left != right:
            signals.append(f"{key}:{_short(left)} vs {_short(right)}")
    aspect_a = _aspect(queue_by_case.get(a, {}))
    aspect_b = _aspect(queue_by_case.get(b, {}))
    if aspect_a and aspect_b and aspect_a != aspect_b:
        signals.append(f"aspect:{aspect_a} vs {aspect_b}")
    tag_a = _specific_tags(queue_by_case.get(a, {}))
    tag_b = _specific_tags(queue_by_case.get(b, {}))
    unique_a = sorted(tag_a - tag_b)
    unique_b = sorted(tag_b - tag_a)
    if unique_a:
        signals.append(f"{a}:tags={','.join(unique_a[:3])}")
    if unique_b:
        signals.append(f"{b}:tags={','.join(unique_b[:3])}")
    return signals


def _aspect(item: dict[str, Any]) -> str:
    tags = set(item.get("tags", []))
    found = sorted(tags & ASPECT_TAGS)
    return found[0] if found else ""


def _specific_tags(item: dict[str, Any]) -> set[str]:
    tags = set(item.get("tags", []))
    return {
        tag
        for tag in tags
        if tag not in GENERIC_TAGS and tag not in ASPECT_TAGS and not tag.startswith("synthetic-v")
    }


def _short(value: str) -> str:
    return value.split(":", 1)[-1]


def _counts_text(counts: dict[str, int]) -> str:
    return ", ".join(f"{key}={value}" for key, value in counts.items()) or "-"
