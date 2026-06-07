from __future__ import annotations

from typing import Any


MOTIF_RULES = {
    "abstract_effects": {"abstract-effects", "fluid-map", "noise", "particle", "smoke", "voxel"},
    "ascii_glitch": {"ascii", "pixel-sorter", "terminal", "glyph", "glitch"},
    "audio_visualizer": {"audio", "music", "visualizer", "waveform"},
    "broadcast_news": {"broadcast", "news", "lower-third", "ticker", "scorebug"},
    "callouts": {"callout", "object-highlight", "focus", "target"},
    "cinematic_trailer": {"trailer", "cinematic", "credits", "teaser"},
    "crt_glitch": {"crt", "glitch", "datamosh", "rgb-shift", "pixel-sorter"},
    "grunge_brush": {"grunge", "brush", "texture", "watercolor", "handwriting"},
    "geo_map_flyover": {"geo-map", "terrain", "earth-zoom", "location", "satellite"},
    "grid_layout_builder": {"grid", "layout-builder", "media-wall", "placeholder"},
    "hud_interface": {"hud", "interface", "terminal", "command-palette", "workflow-ui"},
    "kinetic_typography": {"typography", "title-sequence", "caption", "subtitles", "lyrics"},
    "liquid_glass": {"liquid-glass", "glass", "chromatic"},
    "logo_reveal": {"logo-sting", "logo-reveal", "branding", "photo-logo"},
    "motion_lines": {"motion-trails", "speed-lines", "action", "elements"},
    "multiscreen_media": {"split-screen", "multiscreen", "media-wall", "photo-collage"},
    "parallax_ui": {"parallax-ui", "mouse-cursor", "screen-recording", "mockup"},
    "product_promo": {"product", "promo", "mockup", "app-promo", "ecommerce"},
    "social_vertical": {"social", "vertical", "story", "reels", "instagram"},
    "sports_fitness": {"sports", "fitness", "replay", "scorebug"},
    "sound_marker_sync": {"sound-sync", "markers", "audio", "waveform"},
    "speed_time_tools": {"speed-ramp", "time-remap", "audio-sync"},
    "spiral_grid": {"spiral-grid", "circular-grid", "grid", "layout-builder"},
    "tapered_paths": {"path", "taper", "stroke", "route-reveal", "map"},
    "transitions": {"transition", "transitions", "shape-morph", "geometric", "wipe"},
    "typewriter_text": {"typewriter", "text-highlight", "cursor", "monospaced"},
    "workflow_panels": {"automation", "workflow-ui", "command-palette", "icons"},
}


def build_inspiration_coverage(
    records: list[dict[str, Any]],
    *,
    render_queue: dict[str, Any] | None = None,
    readiness_report: dict[str, Any] | None = None,
) -> dict[str, Any]:
    queue_items = {item["case_id"]: item for item in (render_queue or {}).get("items", [])}
    priority = {
        item["case_id"]: index
        for index, item in enumerate((readiness_report or {}).get("render_debt", []))
    }
    motifs = [
        _motif_payload(name, tags, records, queue_items, priority)
        for name, tags in sorted(MOTIF_RULES.items())
    ]
    gaps = [motif for motif in motifs if motif["source_count"] and not motif["train_ready_count"]]
    return {
        "summary": {
            "motif_count": len(motifs),
            "source_covered_motifs": sum(1 for motif in motifs if motif["source_count"]),
            "train_ready_motifs": sum(1 for motif in motifs if motif["train_ready_count"]),
            "train_ready_gap_count": len(gaps),
        },
        "motifs": motifs,
        "train_ready_gaps": gaps,
        "recommendations": _recommendations(gaps),
    }


def render_inspiration_coverage_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Web Inspiration Coverage Audit",
        "",
        f"- motifs: {payload['summary']['motif_count']}",
        f"- source-covered motifs: {payload['summary']['source_covered_motifs']}",
        f"- train-ready motifs: {payload['summary']['train_ready_motifs']}",
        f"- train-ready motif gaps: {payload['summary']['train_ready_gap_count']}",
        "",
        "## Motif Coverage",
        "",
        "| motif | source | train-ready | missing | stale | first unlock |",
        "| --- | ---: | ---: | ---: | ---: | --- |",
    ]
    for motif in payload["motifs"]:
        lines.append(
            f"| {motif['motif']} | {motif['source_count']} | {motif['train_ready_count']} | "
            f"{motif['render_missing_count']} | {motif['rerender_stale_count']} | "
            f"{motif['first_unlock_case'] or '-'} |"
        )
    lines.extend(["", "## Train-Ready Motif Gaps", ""])
    if payload["train_ready_gaps"]:
        for motif in payload["train_ready_gaps"]:
            cases = ", ".join(motif["source_cases"][:8])
            lines.append(
                f"- {motif['motif']}: first unlock={motif['first_unlock_case'] or '-'}; "
                f"source={cases}"
            )
    else:
        lines.append("- none")
    lines.extend(["", "## Recommendations", ""])
    for item in payload["recommendations"]:
        lines.append(f"- {item}")
    return "\n".join(lines) + "\n"


def _motif_payload(
    name: str,
    tags: set[str],
    records: list[dict[str, Any]],
    queue_items: dict[str, dict[str, Any]],
    priority: dict[str, int],
) -> dict[str, Any]:
    source_cases = [record["case_id"] for record in records if tags & set(record.get("tags", []))]
    train_ready = [case_id for case_id in source_cases if queue_items.get(case_id, {}).get("train_ready")]
    missing = [case_id for case_id in source_cases if _decision(queue_items, case_id) == "render_missing"]
    stale = [case_id for case_id in source_cases if _decision(queue_items, case_id) == "rerender_stale"]
    return {
        "motif": name,
        "tags": sorted(tags),
        "source_count": len(source_cases),
        "train_ready_count": len(train_ready),
        "render_missing_count": len(missing),
        "rerender_stale_count": len(stale),
        "source_cases": source_cases,
        "train_ready_cases": train_ready,
        "render_missing_cases": missing,
        "rerender_stale_cases": stale,
        "first_unlock_case": _first_unlock(source_cases, queue_items, priority),
    }


def _first_unlock(
    source_cases: list[str],
    queue_items: dict[str, dict[str, Any]],
    priority: dict[str, int],
) -> str | None:
    debt_cases = [
        case_id
        for case_id in source_cases
        if _decision(queue_items, case_id) in {"render_missing", "rerender_stale"}
    ]
    if not debt_cases:
        return None
    return sorted(debt_cases, key=lambda case_id: (priority.get(case_id, 9999), case_id))[0]


def _decision(queue_items: dict[str, dict[str, Any]], case_id: str) -> str:
    return queue_items.get(case_id, {}).get("decision", "render_missing")


def _recommendations(gaps: list[dict[str, Any]]) -> list[str]:
    if not gaps:
        return ["web-inspired motif coverage is present in the train-ready subset"]
    return [
        f"render/promote {gap['first_unlock_case'] or gap['source_cases'][0]} for {gap['motif']}"
        for gap in gaps
    ]
