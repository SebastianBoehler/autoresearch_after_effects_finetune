from __future__ import annotations

from typing import Any

from after_effects_pipeline.video_components import foreground_component_metrics


def measure_frame(
    frame: bytes,
    previous: bytes | None,
    width: int,
    height: int,
) -> dict[str, float]:
    pixel_count = width * height
    lumas: list[int] = []
    luma_sum = 0.0
    luma_sq_sum = 0.0
    chroma_sum = 0.0
    motion_sum = 0.0
    motion_pixels = 0
    for index in range(0, len(frame), 3):
        r, g, b = frame[index], frame[index + 1], frame[index + 2]
        luma = (299 * r + 587 * g + 114 * b) // 1000
        lumas.append(luma)
        luma_sum += luma
        luma_sq_sum += luma * luma
        chroma_sum += max(r, g, b) - min(r, g, b)
        if previous is not None:
            delta = (
                abs(r - previous[index])
                + abs(g - previous[index + 1])
                + abs(b - previous[index + 2])
            ) / 3
            motion_sum += delta
            if delta > 8:
                motion_pixels += 1

    mean_luma = luma_sum / pixel_count
    variance = max(0.0, (luma_sq_sum / pixel_count) - mean_luma * mean_luma)
    bg_r, bg_g, bg_b = _border_average(frame, width, height)
    foreground, center_foreground = _foreground_counts(frame, width, height, bg_r, bg_g, bg_b)
    components = foreground_component_metrics(frame, width, height, bg_r, bg_g, bg_b)
    return {
        "brightness": mean_luma / 255,
        "contrast": (variance**0.5) / 255,
        "saturation": (chroma_sum / pixel_count) / 255,
        "motion": (motion_sum / pixel_count) / 255 if previous is not None else 0.0,
        "motion_area_ratio": motion_pixels / pixel_count if previous is not None else 0.0,
        "foreground_ratio": foreground / pixel_count,
        "center_foreground_ratio": center_foreground / _center_pixel_count(width, height),
        "edge_density": _edge_density(lumas, width, height),
        **components,
    }


def aggregate_frame_reports(reports: list[dict[str, float]]) -> dict[str, Any]:
    fields = [
        "brightness",
        "contrast",
        "saturation",
        "motion",
        "motion_area_ratio",
        "foreground_ratio",
        "center_foreground_ratio",
        "edge_density",
        "component_count",
        "largest_component_ratio",
        "largest_component_share",
        "edge_touch_component_ratio",
    ]
    analysis: dict[str, Any] = {"sampled_frames": len(reports)}
    for field in fields:
        analysis[field] = stats([item[field] for item in reports])
    blank_frames = [
        item
        for item in reports
        if item["contrast"] < 0.03 and item["foreground_ratio"] < 0.02
    ]
    motion_reports = reports[1:]
    active_frames = [
        item for item in motion_reports if item["motion_area_ratio"] > 0.015
    ]
    analysis["blank_frame_ratio"] = len(blank_frames) / len(reports) if reports else 1.0
    analysis["active_frame_ratio"] = (
        len(active_frames) / len(motion_reports) if motion_reports else 0.0
    )
    return analysis


def warnings_for_analysis(analysis: dict[str, Any]) -> list[str]:
    warnings = []
    if analysis["blank_frame_ratio"] > 0.15:
        warnings.append("blank_frames")
    active_motion = analysis["motion_area_ratio"]["p95"]
    if analysis["motion"]["mean"] < 0.001 and active_motion < 0.01:
        warnings.append("low_motion")
    if analysis["motion"]["p95"] < 0.003 and active_motion < 0.025:
        warnings.append("limited_motion_range")
    foreground_p95 = analysis["foreground_ratio"]["p95"]
    center_p95 = analysis["center_foreground_ratio"]["p95"]
    if foreground_p95 > 0.45:
        warnings.append("dense_foreground")
    if center_p95 > 0.75 and foreground_p95 > 0.25:
        warnings.append("center_crowding")
    if analysis["edge_density"]["p95"] > 0.22:
        warnings.append("edge_clutter")
    if analysis["contrast"]["mean"] < 0.08:
        warnings.append("low_contrast")
    if analysis["saturation"]["mean"] < 0.05:
        warnings.append("low_color_variety")
    return warnings


def quality_notes_for_analysis(analysis: dict[str, Any]) -> list[str]:
    notes = []
    active_p95 = analysis["motion_area_ratio"]["p95"]
    active_frame_ratio = analysis["active_frame_ratio"]
    foreground_p95 = analysis["foreground_ratio"]["p95"]
    center_p95 = analysis["center_foreground_ratio"]["p95"]
    largest_component_p95 = analysis.get("largest_component_ratio", {}).get("p95", 0.0)
    component_count_p95 = analysis.get("component_count", {}).get("p95", 0.0)
    edge_touch_p95 = analysis.get("edge_touch_component_ratio", {}).get("p95", 0.0)
    if active_frame_ratio > 0.65:
        notes.append("steady_motion")
    elif active_p95 > 0.07:
        notes.append("burst_motion")
    elif active_p95 > 0.025:
        notes.append("subtle_motion")
    else:
        notes.append("localized_motion")
    if foreground_p95 > 0.45:
        notes.append("full_frame_coverage")
    elif center_p95 > 0.6:
        notes.append("center_weighted_layout")
    if largest_component_p95 > 0.35:
        notes.append("merged_foreground_regions")
    elif component_count_p95 > 24:
        notes.append("fragmented_foreground_detail")
    if edge_touch_p95 > 0.5:
        notes.append("edge_touching_foreground")
    if analysis["blank_frame_ratio"] > 0.04:
        notes.append("intentional_intro_blanks")
    timeline = analysis.get("motion_timeline", {})
    if timeline.get("longest_stall_ratio", 0.0) > 0.45:
        notes.append("long_stall_window")
    if timeline.get("motion_profile") == "compressed_motion_window":
        notes.append("compressed_motion_window")
    return notes


def summarize_cases(cases: list[dict[str, Any]]) -> dict[str, Any]:
    warning_counts: dict[str, int] = {}
    for case in cases:
        for warning in case["warnings"]:
            warning_counts[warning] = warning_counts.get(warning, 0) + 1
    return {
        "case_count": len(cases),
        "cases_with_warnings": sum(bool(case["warnings"]) for case in cases),
        "warning_counts": warning_counts,
        "mean_motion": mean([case["analysis"]["motion"]["mean"] for case in cases]),
        "mean_active_motion_p95": mean(
            [case["analysis"]["motion_area_ratio"]["p95"] for case in cases]
        ),
        "mean_active_frame_ratio": mean(
            [case["analysis"]["active_frame_ratio"] for case in cases]
        ),
        "mean_foreground_p95": mean(
            [case["analysis"]["foreground_ratio"]["p95"] for case in cases]
        ),
        "mean_largest_component_p95": mean(
            [case["analysis"]["largest_component_ratio"]["p95"] for case in cases]
        ),
        "mean_component_count_p95": mean(
            [case["analysis"]["component_count"]["p95"] for case in cases]
        ),
    }


def stats(values: list[float]) -> dict[str, float]:
    return {
        "mean": mean(values),
        "min": min(values) if values else 0.0,
        "max": max(values) if values else 0.0,
        "p95": percentile(values, 0.95),
    }


def percentile(values: list[float], quantile: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = min(len(ordered) - 1, max(0, round((len(ordered) - 1) * quantile)))
    return ordered[index]


def mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def _border_average(frame: bytes, width: int, height: int) -> tuple[float, float, float]:
    coords = []
    stride = max(1, width // 48)
    for x in range(0, width, stride):
        coords.append((x, 0))
        coords.append((x, height - 1))
    for y in range(0, height, stride):
        coords.append((0, y))
        coords.append((width - 1, y))
    sums = [0.0, 0.0, 0.0]
    for x, y in coords:
        index = (y * width + x) * 3
        sums[0] += frame[index]
        sums[1] += frame[index + 1]
        sums[2] += frame[index + 2]
    count = len(coords) or 1
    return sums[0] / count, sums[1] / count, sums[2] / count


def _foreground_counts(
    frame: bytes,
    width: int,
    height: int,
    bg_r: float,
    bg_g: float,
    bg_b: float,
) -> tuple[int, int]:
    foreground = 0
    center_foreground = 0
    x0, x1 = width // 3, (2 * width) // 3
    y0, y1 = height // 4, (3 * height) // 4
    for y in range(height):
        for x in range(width):
            index = (y * width + x) * 3
            delta = (
                abs(frame[index] - bg_r)
                + abs(frame[index + 1] - bg_g)
                + abs(frame[index + 2] - bg_b)
            )
            if delta > 90:
                foreground += 1
                if x0 <= x < x1 and y0 <= y < y1:
                    center_foreground += 1
    return foreground, center_foreground


def _edge_density(lumas: list[int], width: int, height: int) -> float:
    edges = 0
    samples = 0
    for y in range(1, height, 2):
        row = y * width
        previous_row = (y - 1) * width
        for x in range(1, width, 2):
            value = lumas[row + x]
            horizontal = abs(value - lumas[row + x - 1])
            vertical = abs(value - lumas[previous_row + x])
            if horizontal > 35 or vertical > 35:
                edges += 1
            samples += 1
    return edges / samples if samples else 0.0


def _center_pixel_count(width: int, height: int) -> int:
    return ((2 * width) // 3 - width // 3) * ((3 * height) // 4 - height // 4)
