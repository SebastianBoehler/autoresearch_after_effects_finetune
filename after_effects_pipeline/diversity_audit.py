from __future__ import annotations

import re
from collections import Counter
from typing import Any

from after_effects_pipeline.dataset_audit import CATEGORY_RULES


ANIMATION_RULES = {
    "broadcast_ticker": {"broadcast", "ticker", "lower third", "scorebug", "stream"},
    "callout_scan": {"callout", "target", "scan", "magnified", "connector"},
    "ascii_glitch": {"ascii", "glyph", "terminal", "pixel sort", "signal glitch"},
    "audio_sync": {"audio", "beat", "marker", "sound sync", "waveform", "whoosh"},
    "data_dashboard": {"dashboard", "data", "chart", "meter", "infographic"},
    "geo_map_flyover": {"geo map", "terrain", "altitude", "satellite", "route flyover"},
    "glitch_datamosh": {"glitch", "datamosh", "crt", "rgb", "pixel", "voxel"},
    "grid_layout": {"grid", "layout builder", "placeholder card", "tile grid", "product wall"},
    "grunge_brush": {"grunge", "brush", "paint", "ink", "texture"},
    "hud_interface": {"hud", "interface", "terminal", "command palette", "network"},
    "liquid_glass": {
        "liquid glass",
        "liquid logo",
        "refraction",
        "ripple",
        "specular",
        "glass card",
        "glass edge",
    },
    "logo_reveal": {"logo", "brand", "lockup", "sting", "aperture"},
    "motion_trails": {"trail", "speed line", "motion line", "streak", "whoosh"},
    "parallax_ui": {"parallax ui", "mouse cursor", "screen recording", "click states"},
    "particle_smoke": {"particle", "smoke", "puff", "spark", "dust"},
    "photo_slideshow": {"photo", "slideshow", "collage", "placeholder", "image tile"},
    "product_promo": {"product", "promo", "cta", "swatch", "preorder"},
    "split_screen": {"split", "feed", "panel", "screen", "media wall"},
    "speed_time_remap": {"speed ramp", "time remap", "timewarp", "velocity graph"},
    "spiral_grid": {"spiral grid", "circular grid", "layout camera", "guide ring"},
    "tapered_paths": {"path", "stroke", "taper", "snake", "route"},
    "text_reveal": {"typography", "title", "caption", "credits", "word"},
    "typewriter_text": {"typewriter", "cursor", "monospaced", "underline", "typed"},
    "transition_wipe": {"transition", "wipe", "morph", "reveal", "flash"},
}

STOPWORDS = {
    "after",
    "animated",
    "animation",
    "effects",
    "create",
    "with",
    "and",
    "the",
    "for",
    "style",
    "second",
    "seconds",
    "aeft",
    "synthetic",
    "keyframes",
    "expressions",
    "template",
}


def build_diversity_audit(
    records: list[dict[str, Any]],
    *,
    render_queue: dict[str, Any] | None = None,
) -> dict[str, Any]:
    queue_items = {
        item["case_id"]: item
        for item in (render_queue or {}).get("items", [])
    }
    rendered_ready = {
        case_id
        for case_id, item in queue_items.items()
        if item.get("train_ready")
    }
    source_buckets = _bucket_cases(records, ANIMATION_RULES)
    category_buckets = _bucket_cases(records, CATEGORY_RULES)
    train_buckets = _filter_bucket_cases(source_buckets, rendered_ready)
    train_categories = _filter_bucket_cases(category_buckets, rendered_ready)
    return {
        "summary": {
            "case_count": len(records),
            "train_ready_count": len(rendered_ready),
            "source_animation_bucket_count": _nonzero_count(source_buckets),
            "train_ready_animation_bucket_count": _nonzero_count(train_buckets),
            "train_ready_gap_count": len(_train_ready_gaps(source_buckets, train_buckets)),
            "overlap_pair_count": len(_overlap_pairs(records)),
        },
        "source_pack_counts": _pack_counts(records),
        "train_ready_pack_counts": _pack_counts(
            [record for record in records if record["case_id"] in rendered_ready]
        ),
        "source_animation_buckets": _counts(source_buckets),
        "train_ready_animation_buckets": _counts(train_buckets),
        "source_category_buckets": _counts(category_buckets),
        "train_ready_category_buckets": _counts(train_categories),
        "train_ready_animation_gaps": _train_ready_gaps(source_buckets, train_buckets),
        "train_ready_category_gaps": _train_ready_gaps(category_buckets, train_categories),
        "render_debt_by_animation": _render_debt_by_bucket(source_buckets, queue_items),
        "overlap_pairs": _overlap_pairs(records),
        "recommendations": _recommendations(
            source_buckets,
            train_buckets,
            category_buckets,
            train_categories,
            queue_items,
        ),
    }


def render_diversity_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Dataset Diversity Audit",
        "",
        f"- cases: {payload['summary']['case_count']}",
        f"- train-ready cases: {payload['summary']['train_ready_count']}",
        f"- source animation buckets: {payload['summary']['source_animation_bucket_count']}",
        f"- train-ready animation buckets: {payload['summary']['train_ready_animation_bucket_count']}",
        f"- train-ready animation gaps: {payload['summary']['train_ready_gap_count']}",
        "",
        "## Train-Ready Animation Gaps",
        "",
    ]
    _append_gap_lines(lines, payload["train_ready_animation_gaps"])
    lines.extend(["", "## Render Debt By Animation", ""])
    for bucket, debt in payload["render_debt_by_animation"].items():
        missing = ", ".join(debt["render_missing"][:8]) or "-"
        stale = ", ".join(debt["rerender_stale"][:8]) or "-"
        lines.append(f"- {bucket}: missing={missing}; stale={stale}")
    lines.extend(["", "## Potential Overlaps", ""])
    if payload["overlap_pairs"]:
        for pair in payload["overlap_pairs"]:
            shared = ", ".join(pair["shared_terms"][:8])
            lines.append(
                f"- {pair['a']} / {pair['b']}: {pair['score']:.2f} ({shared})"
            )
    else:
        lines.append("- none above threshold")
    lines.extend(["", "## Recommendations", ""])
    for item in payload["recommendations"]:
        lines.append(f"- {item}")
    return "\n".join(lines) + "\n"


def _bucket_cases(
    records: list[dict[str, Any]],
    rules: dict[str, set[str]],
) -> dict[str, list[str]]:
    buckets = {name: [] for name in rules}
    for record in records:
        text = _record_text(record)
        for name, markers in rules.items():
            if any(_marker_match(marker, text) for marker in markers):
                buckets[name].append(record["case_id"])
    return buckets


def _record_text(record: dict[str, Any]) -> str:
    parts = [
        record.get("case_id", ""),
        record.get("prompt", ""),
        " ".join(record.get("tags", [])),
        record.get("completion", ""),
    ]
    return " ".join(parts).lower().replace("_", " ").replace("-", " ")


def _marker_match(marker: str, text: str) -> bool:
    return marker.lower().replace("_", " ").replace("-", " ") in text


def _filter_bucket_cases(
    buckets: dict[str, list[str]],
    allowed: set[str],
) -> dict[str, list[str]]:
    return {
        bucket: [case_id for case_id in case_ids if case_id in allowed]
        for bucket, case_ids in buckets.items()
    }


def _counts(buckets: dict[str, list[str]]) -> dict[str, int]:
    return {
        bucket: len(case_ids)
        for bucket, case_ids in sorted(buckets.items())
        if case_ids
    }


def _nonzero_count(buckets: dict[str, list[str]]) -> int:
    return sum(1 for case_ids in buckets.values() if case_ids)


def _pack_counts(records: list[dict[str, Any]]) -> dict[str, int]:
    counts = Counter()
    for record in records:
        pack = next((tag for tag in record.get("tags", []) if tag.startswith("synthetic-v")), "unknown")
        counts[pack] += 1
    return dict(sorted(counts.items()))


def _train_ready_gaps(
    source_buckets: dict[str, list[str]],
    train_buckets: dict[str, list[str]],
) -> list[dict[str, Any]]:
    gaps = []
    for bucket, case_ids in sorted(source_buckets.items()):
        if case_ids and not train_buckets.get(bucket):
            gaps.append({"bucket": bucket, "source_count": len(case_ids), "case_ids": case_ids})
    return gaps


def _render_debt_by_bucket(
    buckets: dict[str, list[str]],
    queue_items: dict[str, dict[str, Any]],
) -> dict[str, dict[str, list[str]]]:
    debt = {}
    for bucket, case_ids in sorted(buckets.items()):
        missing = [cid for cid in case_ids if _decision(queue_items, cid) == "render_missing"]
        stale = [cid for cid in case_ids if _decision(queue_items, cid) == "rerender_stale"]
        if missing or stale:
            debt[bucket] = {"render_missing": missing, "rerender_stale": stale}
    return debt


def _decision(queue_items: dict[str, dict[str, Any]], case_id: str) -> str:
    return queue_items.get(case_id, {}).get("decision", "render_missing")


def _overlap_pairs(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    vectors = {record["case_id"]: _overlap_terms(record) for record in records}
    pairs = []
    ids = list(vectors)
    for i, first in enumerate(ids):
        for second in ids[i + 1 :]:
            a, b = vectors[first], vectors[second]
            if not a or not b:
                continue
            shared = sorted(a & b)
            score = len(shared) / len(a | b)
            if score >= 0.34 and len(shared) >= 4:
                pairs.append({"a": first, "b": second, "score": round(score, 4), "shared_terms": shared})
    return sorted(pairs, key=lambda item: (-item["score"], item["a"], item["b"]))[:20]


def _overlap_terms(record: dict[str, Any]) -> set[str]:
    text = f"{record.get('case_id', '')} {record.get('prompt', '')} {' '.join(record.get('tags', []))}"
    tokens = re.findall(r"[a-z0-9]{3,}", text.lower().replace("_", " ").replace("-", " "))
    return {token for token in tokens if token not in STOPWORDS}


def _recommendations(
    source_buckets: dict[str, list[str]],
    train_buckets: dict[str, list[str]],
    source_categories: dict[str, list[str]],
    train_categories: dict[str, list[str]],
    queue_items: dict[str, dict[str, Any]],
) -> list[str]:
    recs = []
    for gap in _train_ready_gaps(source_buckets, train_buckets)[:8]:
        recs.append(f"render/promote animation bucket: {gap['bucket']}")
    for gap in _train_ready_gaps(source_categories, train_categories)[:6]:
        recs.append(f"render/promote category bucket: {gap['bucket']}")
    if any(item.get("decision") == "rerender_stale" for item in queue_items.values()):
        recs.append("run AE manual harnesses to clear stale high-potential renders")
    if any(item.get("decision") == "render_missing" for item in queue_items.values()):
        recs.append("generate missing AE projects before judging newer packs")
    return recs or ["source and train-ready diversity are aligned"]


def _append_gap_lines(lines: list[str], gaps: list[dict[str, Any]]) -> None:
    if not gaps:
        lines.append("- none")
        return
    for gap in gaps:
        cases = ", ".join(gap["case_ids"][:10])
        lines.append(f"- {gap['bucket']}: {gap['source_count']} source cases ({cases})")
