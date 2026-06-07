from __future__ import annotations

from collections import Counter
from typing import Any


THEME_RULES: dict[str, tuple[str, ...]] = {
    "abstract_glitch": ("abstract", "ascii", "crt", "datamosh", "fluid", "glitch", "grunge", "noise", "pixel"),
    "audio_music": ("audio", "equalizer", "lyric", "music", "podcast", "sound", "sound-sync", "waveform"),
    "broadcast_news": ("broadcast", "forecast", "live-stream", "news", "scorebug", "weather"),
    "dashboard_data": ("bar-race", "chart", "dashboard", "data", "data-visualization", "infographic", "metric", "timeline"),
    "fashion_food_fitness": ("fashion", "fitness", "food", "lookbook", "recipe"),
    "finance_market": ("finance", "market"),
    "geo_map": ("earth", "geo", "location", "map", "route", "terrain"),
    "hud_tech": ("ai", "code", "console", "hud", "network", "scan", "security", "terminal", "target-lock"),
    "logo_brand": ("badge", "brand", "logo", "sting"),
    "lower_third_caption": ("caption", "lower-third", "quote", "subtitle", "subtitles"),
    "path_shape_system": ("line", "motion-trails", "multicolor", "path", "shape", "speed-line", "stroke", "taper"),
    "photo_slideshow": ("archive", "collage", "photo", "placeholder", "slideshow", "video-wall"),
    "product_promo": ("app-promo", "ecommerce", "launch", "perfume", "product", "promo", "sale"),
    "real_estate": ("listing", "real-estate"),
    "science_medical": ("device", "medical", "molecule", "science"),
    "social_vertical": ("reel", "social", "story", "vertical"),
    "sports_replay": ("replay", "scorebug", "sports"),
    "transition_effects": ("split-screen", "speed-ramp", "timewarp", "transition", "wipe"),
    "travel_postcard": ("postcard", "travel"),
    "typography_title": ("handwriting", "headline", "kinetic", "text", "title", "type", "typewriter", "typography"),
    "workflow_tools": ("builder", "command", "controls", "generator", "layout-builder", "marker", "toolkit", "workflow"),
}


def build_theme_motion_audit(
    records: list[dict[str, Any]],
    *,
    queue: dict[str, Any],
    animation_anatomy: dict[str, Any],
    quality_gap_matrix: dict[str, Any],
) -> dict[str, Any]:
    queue_by_id = {item["case_id"]: item for item in queue.get("items", [])}
    anatomy_by_id = {item["case_id"]: item for item in animation_anatomy.get("cases", [])}
    matrix_by_id = {item["case_id"]: item for item in quality_gap_matrix.get("items", [])}
    cases = [
        _case_item(record, queue_by_id, anatomy_by_id, matrix_by_id)
        for record in records
    ]
    source_counts = _theme_counts(cases)
    ready_counts = _theme_counts([case for case in cases if case["train_ready"]])
    gaps = _theme_gaps(cases, source_counts, ready_counts)
    combos = _theme_motion_combos(cases)
    planned_unlocks = _planned_theme_unlocks(cases, gaps)
    return {
        "summary": {
            "case_count": len(cases),
            "train_ready_count": sum(case["train_ready"] for case in cases),
            "source_theme_count": len(source_counts),
            "train_ready_theme_count": len(ready_counts),
            "train_ready_theme_gap_count": len(gaps),
            "train_ready_theme_motion_combo_count": len(combos),
            "planned_gap_target_count": len({item["case_id"] for item in planned_unlocks}),
        },
        "theme_counts": dict(sorted(source_counts.items())),
        "train_ready_theme_counts": dict(sorted(ready_counts.items())),
        "train_ready_theme_gaps": gaps,
        "train_ready_theme_motion_combos": combos,
        "planned_theme_unlock_targets": planned_unlocks,
        "cases": sorted(cases, key=lambda item: item["case_id"]),
        "recommendations": _recommendations(gaps, planned_unlocks),
    }


def render_theme_motion_markdown(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# Theme Motion Audit",
        "",
        "Pairs source themes with train-ready render state and every-third-frame motion archetypes.",
        "",
        "## Summary",
        "",
        f"- cases: {summary['case_count']}",
        f"- train-ready cases: {summary['train_ready_count']}",
        f"- source themes: {summary['source_theme_count']}",
        f"- train-ready themes: {summary['train_ready_theme_count']}",
        f"- train-ready theme gaps: {summary['train_ready_theme_gap_count']}",
        f"- train-ready theme-motion combos: {summary['train_ready_theme_motion_combo_count']}",
        f"- planned gap targets: {summary['planned_gap_target_count']}",
        "",
        "## Train-Ready Theme Gaps",
        "",
        "| theme | source cases | first planned target | candidate cases |",
        "| --- | ---: | --- | --- |",
    ]
    if payload["train_ready_theme_gaps"]:
        for gap in payload["train_ready_theme_gaps"]:
            lines.append(
                f"| {gap['theme']} | {gap['source_count']} | {gap['first_planned_target'] or '-'} | "
                f"{', '.join(gap['candidate_cases'][:6]) or '-'} |"
            )
    else:
        lines.append("| none | 0 | - | - |")
    lines.extend(["", "## Planned Theme Unlock Targets", ""])
    if payload["planned_theme_unlock_targets"]:
        lines.extend([
            "| case | decision | action | missing themes | archetype | unlocks |",
            "| --- | --- | --- | --- | --- | --- |",
        ])
        for item in payload["planned_theme_unlock_targets"]:
            lines.append(
                f"| {item['case_id']} | {item['decision']} | {item['action']} | "
                f"{', '.join(item['missing_themes'])} | {item['archetype']} | "
                f"{', '.join(item['new_unlocks']) or '-'} |"
            )
    else:
        lines.append("- none")
    lines.extend(["", "## Train-Ready Theme-Motion Combos", ""])
    lines.extend([
        "| theme | aspect | archetype | count | cases |",
        "| --- | --- | --- | ---: | --- |",
    ])
    for combo in payload["train_ready_theme_motion_combos"][:60]:
        lines.append(
            f"| {combo['theme']} | {combo['aspect']} | {combo['archetype']} | "
            f"{combo['count']} | {', '.join(combo['case_ids'][:6])} |"
        )
    lines.extend(["", "## Recommendations", ""])
    lines.extend(f"- {item}" for item in payload["recommendations"])
    return "\n".join(lines) + "\n"


def infer_themes(record: dict[str, Any]) -> list[str]:
    haystack = _record_haystack(record)
    themes = [
        theme
        for theme, keywords in THEME_RULES.items()
        if any(keyword in haystack for keyword in keywords)
    ]
    return sorted(themes) or ["uncategorized"]


def _case_item(
    record: dict[str, Any],
    queue_by_id: dict[str, dict[str, Any]],
    anatomy_by_id: dict[str, dict[str, Any]],
    matrix_by_id: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    case_id = record["case_id"]
    queue_item = queue_by_id.get(case_id, {})
    anatomy = anatomy_by_id.get(case_id, {})
    matrix_item = matrix_by_id.get(case_id, {})
    decision = queue_item.get("decision", matrix_item.get("decision", "unknown"))
    archetype = anatomy.get("archetype") or ("unrendered" if decision == "render_missing" else "unknown")
    return {
        "case_id": case_id,
        "themes": infer_themes(record),
        "aspect": _aspect(record.get("expected", {})),
        "train_ready": bool(queue_item.get("train_ready")),
        "decision": decision,
        "archetype": archetype,
        "motion_profile": queue_item.get("motion_profile") or anatomy.get("motion_profile", ""),
        "action": matrix_item.get("action", ""),
        "new_unlocks": list(matrix_item.get("new_unlocks", [])),
        "planned": bool(matrix_item.get("new_unlocks")),
        "source_repo_path": record.get("source_repo_path", ""),
    }


def _theme_counts(cases: list[dict[str, Any]]) -> Counter[str]:
    counts: Counter[str] = Counter()
    for case in cases:
        counts.update(case["themes"])
    return counts


def _theme_gaps(
    cases: list[dict[str, Any]],
    source_counts: Counter[str],
    ready_counts: Counter[str],
) -> list[dict[str, Any]]:
    gaps = []
    for theme in sorted(source_counts):
        if ready_counts.get(theme):
            continue
        candidates = [case for case in cases if theme in case["themes"] and not case["train_ready"]]
        candidates.sort(key=lambda item: (not item["planned"], item["case_id"]))
        planned = [case["case_id"] for case in candidates if case["planned"]]
        gaps.append({
            "theme": theme,
            "source_count": source_counts[theme],
            "first_planned_target": planned[0] if planned else "",
            "candidate_cases": [case["case_id"] for case in candidates],
        })
    return gaps


def _theme_motion_combos(cases: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[tuple[str, str, str], list[str]] = {}
    for case in cases:
        if not case["train_ready"]:
            continue
        for theme in case["themes"]:
            key = (theme, case["aspect"], case["archetype"])
            groups.setdefault(key, []).append(case["case_id"])
    rows = [
        {"theme": theme, "aspect": aspect, "archetype": archetype, "count": len(case_ids), "case_ids": sorted(case_ids)}
        for (theme, aspect, archetype), case_ids in groups.items()
    ]
    return sorted(rows, key=lambda item: (item["theme"], item["aspect"], item["archetype"]))


def _planned_theme_unlocks(cases: list[dict[str, Any]], gaps: list[dict[str, Any]]) -> list[dict[str, Any]]:
    missing_themes = {gap["theme"] for gap in gaps}
    rows = []
    for case in cases:
        themes = [theme for theme in case["themes"] if theme in missing_themes]
        if not themes or not case["planned"]:
            continue
        rows.append({
            "case_id": case["case_id"],
            "decision": case["decision"],
            "action": case["action"],
            "missing_themes": themes,
            "archetype": case["archetype"],
            "new_unlocks": case["new_unlocks"],
        })
    return sorted(rows, key=lambda item: (item["case_id"]))


def _recommendations(gaps: list[dict[str, Any]], planned_unlocks: list[dict[str, Any]]) -> list[str]:
    if not gaps:
        return ["train-ready subset already covers all source themes"]
    covered = {theme for item in planned_unlocks for theme in item["missing_themes"]}
    missing = [gap["theme"] for gap in gaps if gap["theme"] not in covered]
    recommendations = []
    if covered:
        targets = ", ".join(sorted({item["case_id"] for item in planned_unlocks})[:10])
        recommendations.append("render/rerender planned targets before adding more source scripts: " + targets)
    if missing:
        candidates = [
            f"{gap['theme']}={gap['candidate_cases'][0]}"
            for gap in gaps
            if gap["theme"] in missing and gap["candidate_cases"]
        ]
        recommendations.append("add existing candidates to the render-unlock plan: " + ", ".join(candidates or missing))
    if not missing:
        recommendations.append("current render-unlock batch covers the train-ready theme gaps")
    return recommendations


def _aspect(expected: dict[str, Any]) -> str:
    width = int(expected.get("width") or 0)
    height = int(expected.get("height") or 0)
    if height > width:
        return "vertical"
    if width and width == height:
        return "square"
    return "landscape"


def _record_haystack(record: dict[str, Any]) -> str:
    parts = [
        record.get("case_id", ""),
        record.get("template", ""),
        record.get("prompt", ""),
        record.get("source_repo_path", ""),
        " ".join(record.get("tags", [])),
    ]
    return " ".join(parts).replace("_", "-").lower()
