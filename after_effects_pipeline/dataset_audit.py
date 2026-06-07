from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any


CATEGORY_RULES = {
    "app_promo_mockup": {"app-promo", "mockup", "ecommerce", "product"},
    "abstract_effects": {"abstract-effects", "fluid-map", "noise", "particle"},
    "broadcast_package": {"broadcast", "lower-third", "scorebug", "sports"},
    "data_infographic": {"dashboard", "data-visualization", "infographic", "chart"},
    "education_explainer": {"education", "explainer", "science", "code"},
    "filmic_teaser": {"trailer", "teaser", "cinematic", "action"},
    "fashion_promo": {"fashion", "lookbook", "streetwear", "runway"},
    "finance_market": {"finance", "stock-market", "trading", "investing"},
    "healthcare_explainer": {"healthcare", "medical", "device", "patient"},
    "hud_interface": {"hud", "interface", "sci-fi"},
    "logo_branding": {"logo-sting", "branding", "glitch"},
    "music_visualizer": {"music", "visualizer"},
    "photo_slideshow": {"slideshow", "photo-grid", "photo-collage"},
    "page_turn_3d": {"flipbook", "page-turn", "3d"},
    "retro_lights": {"neon", "retro", "lights"},
    "social_vertical": {"social", "vertical", "story"},
    "text_titles": {"typography", "title-sequence", "intro", "opener"},
    "timeline_map": {"timeline", "map", "route-reveal"},
    "transitions": {"transition", "transitions", "shape-morph", "geometric"},
    "weather_broadcast": {"weather", "forecast", "climate", "temperature"},
}

MIN_CATEGORY_COVERAGE = {
    "abstract_effects": 1,
    "app_promo_mockup": 2,
    "broadcast_package": 2,
    "data_infographic": 2,
    "education_explainer": 2,
    "filmic_teaser": 1,
    "fashion_promo": 1,
    "finance_market": 1,
    "healthcare_explainer": 1,
    "hud_interface": 2,
    "logo_branding": 2,
    "music_visualizer": 2,
    "page_turn_3d": 1,
    "photo_slideshow": 2,
    "retro_lights": 1,
    "social_vertical": 3,
    "text_titles": 3,
    "timeline_map": 2,
    "transitions": 2,
    "weather_broadcast": 1,
}


def audit_dataset(
    records: list[dict[str, Any]],
    render_analysis: dict[str, Any] | None = None,
    repo_root: Path | None = None,
) -> dict[str, Any]:
    tag_counts = Counter(tag for record in records for tag in record.get("tags", []))
    aspect_counts = Counter(_aspect_label(record) for record in records)
    category_cases = _category_cases(records)
    warning_cases = _warning_cases(render_analysis)
    missing_render_cases = _missing_render_cases(records, render_analysis)
    stale_render_cases = _stale_render_cases(records, render_analysis, repo_root)
    intentional, actionable = _split_warning_cases(records, warning_cases)
    return {
        "case_count": len(records),
        "aspect_ratios": dict(sorted(aspect_counts.items())),
        "top_tags": dict(tag_counts.most_common(24)),
        "category_counts": {
            category: len(case_ids)
            for category, case_ids in sorted(category_cases.items())
        },
        "category_cases": {
            category: case_ids
            for category, case_ids in sorted(category_cases.items())
        },
        "undercovered_categories": _undercovered_categories(category_cases),
        "render_warning_cases": warning_cases,
        "intentional_render_warning_cases": intentional,
        "actionable_render_warning_cases": actionable,
        "render_warning_count": len(warning_cases),
        "missing_render_cases": missing_render_cases,
        "missing_render_count": len(missing_render_cases),
        "stale_render_cases": stale_render_cases,
        "stale_render_count": len(stale_render_cases),
        "actionable_render_warning_count": len(actionable),
        "recommendations": _recommendations(
            category_cases=category_cases,
            aspect_counts=aspect_counts,
            actionable_warning_cases=actionable,
            intentional_warning_cases=intentional,
            missing_render_cases=missing_render_cases,
            stale_render_cases=stale_render_cases,
        ),
    }


def render_audit_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Dataset Coverage Audit",
        "",
        f"- cases: {payload['case_count']}",
        f"- missing render cases: {payload['missing_render_count']}",
        f"- stale render cases: {payload.get('stale_render_count', 0)}",
        f"- render warning cases: {payload['render_warning_count']}",
        f"- actionable render warning cases: {payload['actionable_render_warning_count']}",
        "",
        "## Aspect Ratios",
        "",
    ]
    for label, count in payload["aspect_ratios"].items():
        lines.append(f"- {label}: {count}")
    lines.extend(["", "## Category Coverage", ""])
    for category, count in payload["category_counts"].items():
        case_ids = ", ".join(payload["category_cases"][category])
        lines.append(f"- {category}: {count} ({case_ids})")
    lines.extend(["", "## Undercovered Categories", ""])
    undercovered = payload["undercovered_categories"]
    if undercovered:
        for category in undercovered:
            lines.append(f"- {category}")
    else:
        lines.append("- none")
    lines.extend(["", "## Missing Render Cases", ""])
    if payload["missing_render_cases"]:
        for case_id in payload["missing_render_cases"]:
            lines.append(f"- {case_id}")
    else:
        lines.append("- none")
    lines.extend(["", "## Stale Render Cases", ""])
    if payload.get("stale_render_cases"):
        for case_id in payload["stale_render_cases"]:
            lines.append(f"- {case_id}")
    else:
        lines.append("- none")
    lines.extend(["", "## Actionable Render Warning Cases", ""])
    if payload["actionable_render_warning_cases"]:
        for item in payload["actionable_render_warning_cases"]:
            warnings = ", ".join(item["warnings"])
            notes = ", ".join(item["notes"])
            lines.append(f"- {item['case_id']}: {warnings} ({notes})")
    else:
        lines.append("- none")
    lines.extend(["", "## Intentional Full-Frame Warning Cases", ""])
    if payload["intentional_render_warning_cases"]:
        for item in payload["intentional_render_warning_cases"]:
            warnings = ", ".join(item["warnings"])
            notes = ", ".join(item["notes"])
            lines.append(f"- {item['case_id']}: {warnings} ({notes})")
    else:
        lines.append("- none")
    lines.extend(["", "## Recommendations", ""])
    for item in payload["recommendations"]:
        lines.append(f"- {item}")
    return "\n".join(lines) + "\n"


def _category_cases(records: list[dict[str, Any]]) -> dict[str, list[str]]:
    coverage = {category: [] for category in CATEGORY_RULES}
    for record in records:
        tags = set(record.get("tags", []))
        for category, markers in CATEGORY_RULES.items():
            if tags & markers:
                coverage[category].append(record["case_id"])
    return coverage


def _undercovered_categories(category_cases: dict[str, list[str]]) -> list[str]:
    undercovered = []
    for category, minimum in MIN_CATEGORY_COVERAGE.items():
        if len(category_cases.get(category, [])) < minimum:
            undercovered.append(category)
    return undercovered


def _warning_cases(render_analysis: dict[str, Any] | None) -> list[dict[str, Any]]:
    if not render_analysis:
        return []
    cases = []
    for case in render_analysis.get("cases", []):
        warnings = case.get("warnings", [])
        if warnings:
            cases.append(
                {
                    "case_id": case["case_id"],
                    "warnings": warnings,
                    "notes": case.get("notes", []),
                }
            )
    return cases


def _missing_render_cases(
    records: list[dict[str, Any]],
    render_analysis: dict[str, Any] | None,
) -> list[str]:
    if not render_analysis:
        return []
    rendered = {case["case_id"] for case in render_analysis.get("cases", [])}
    return [record["case_id"] for record in records if record["case_id"] not in rendered]


def _stale_render_cases(
    records: list[dict[str, Any]],
    render_analysis: dict[str, Any] | None,
    repo_root: Path | None,
) -> list[str]:
    if not render_analysis:
        return []
    rendered = {case["case_id"]: case for case in render_analysis.get("cases", [])}
    stale = []
    for record in records:
        case = rendered.get(record["case_id"])
        source = record.get("source_repo_path")
        if not case or not source or not case.get("video_path"):
            continue
        source_path = Path(source)
        if repo_root and not source_path.is_absolute():
            source_path = repo_root / source_path
        video_path = Path(case["video_path"])
        if source_path.exists() and video_path.exists() and video_path.stat().st_mtime < source_path.stat().st_mtime:
            stale.append(record["case_id"])
    return stale


def _split_warning_cases(
    records: list[dict[str, Any]],
    warning_cases: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    tags_by_case = {record["case_id"]: set(record.get("tags", [])) for record in records}
    intentional = []
    actionable = []
    for warning_case in warning_cases:
        tags = tags_by_case.get(warning_case["case_id"], set())
        if _is_intentional_full_frame_warning(warning_case, tags):
            intentional.append(warning_case)
        else:
            actionable.append(warning_case)
    return intentional, actionable


def _is_intentional_full_frame_warning(
    warning_case: dict[str, Any],
    tags: set[str],
) -> bool:
    warnings = set(warning_case.get("warnings", []))
    notes = set(warning_case.get("notes", []))
    full_frame_tags = {"transition", "transitions", "geometric", "shape-morph", "product", "visualizer", "lyrics"}
    return (
        warnings <= {"dense_foreground", "center_crowding"}
        and "full_frame_coverage" in notes
        and bool(tags & full_frame_tags)
    )


def _recommendations(
    *,
    category_cases: dict[str, list[str]],
    aspect_counts: Counter,
    actionable_warning_cases: list[dict[str, Any]],
    intentional_warning_cases: list[dict[str, Any]],
    missing_render_cases: list[str],
    stale_render_cases: list[str],
) -> list[str]:
    recommendations = []
    for category in _undercovered_categories(category_cases):
        recommendations.append(f"add more {category.replace('_', ' ')} samples")
    if aspect_counts.get("vertical_9x16", 0) < 4:
        recommendations.append("add another vertical social/mobile sample")
    if aspect_counts.get("square_1x1", 0) < 3:
        recommendations.append("add another square visualizer/social sample")
    if actionable_warning_cases:
        recommendations.append("fix actionable render warning cases")
    if missing_render_cases:
        recommendations.append("rerender missing render cases")
    if stale_render_cases:
        recommendations.append("rerender stale render cases")
    if intentional_warning_cases:
        recommendations.append("manual-review intentional full-frame warning cases")
    return recommendations or ["coverage is balanced for this seed set"]


def _aspect_label(record: dict[str, Any]) -> str:
    expected = record.get("expected", {})
    width = int(expected.get("width", 0))
    height = int(expected.get("height", 0))
    if width == height:
        return "square_1x1"
    if width > height:
        return "landscape_16x9"
    return "vertical_9x16"
