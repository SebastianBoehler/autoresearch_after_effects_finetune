from __future__ import annotations

from typing import Any

ACTIVE_MOTION_AREA_THRESHOLD = 0.015


def build_motion_timeline(
    reports: list[dict[str, float]],
    *,
    frame_step: int,
) -> dict[str, Any]:
    entries = [
        (index, report["motion_area_ratio"] > ACTIVE_MOTION_AREA_THRESHOLD)
        for index, report in enumerate(reports)
    ][1:]
    if not entries:
        return _empty_timeline()
    active_indices = [index for index, active in entries if active]
    longest_stall = _longest_run(entries, active=False)
    active_ratio = len(active_indices) / len(entries)
    active_span_ratio = (
        ((active_indices[-1] - active_indices[0] + 1) / len(entries))
        if active_indices
        else 0.0
    )
    longest_stall_ratio = longest_stall["length"] / len(entries)
    return {
        "active_threshold": ACTIVE_MOTION_AREA_THRESHOLD,
        "active_span_ratio": active_span_ratio,
        "first_active_source_frame": active_indices[0] * frame_step if active_indices else None,
        "last_active_source_frame": active_indices[-1] * frame_step if active_indices else None,
        "longest_stall": _source_run(longest_stall, frame_step),
        "longest_stall_ratio": longest_stall_ratio,
        "motion_profile": _motion_profile(active_ratio, active_span_ratio, longest_stall_ratio),
    }


def build_frame_timeline(
    reports: list[dict[str, float]],
    *,
    frame_step: int,
    peak_count: int = 5,
) -> dict[str, Any]:
    samples = [
        _frame_sample(index, report, frame_step, len(reports))
        for index, report in enumerate(reports)
    ]
    return {
        "frame_step": frame_step,
        "sample_count": len(samples),
        "samples": samples,
        "phase_summary": _phase_summary(samples),
        "motion_peaks": _peaks(samples, "motion_area_ratio", peak_count),
        "foreground_peaks": _peaks(samples, "foreground_ratio", peak_count),
    }


def _empty_timeline() -> dict[str, Any]:
    return {
        "active_threshold": ACTIVE_MOTION_AREA_THRESHOLD,
        "active_span_ratio": 0.0,
        "first_active_source_frame": None,
        "last_active_source_frame": None,
        "longest_stall": {"sample_start": 0, "sample_end": 0, "source_start_frame": 0, "source_end_frame": 0, "length": 0},
        "longest_stall_ratio": 1.0,
        "motion_profile": "single_frame",
    }


def _frame_sample(
    index: int,
    report: dict[str, float],
    frame_step: int,
    total: int,
) -> dict[str, Any]:
    foreground = report.get("foreground_ratio", 0.0)
    contrast = report.get("contrast", 0.0)
    motion_area = report.get("motion_area_ratio", 0.0)
    return {
        "sample_index": index,
        "source_frame": index * frame_step,
        "phase": _phase(index, total),
        "active": index > 0 and motion_area > ACTIVE_MOTION_AREA_THRESHOLD,
        "blank": contrast < 0.03 and foreground < 0.02,
        "motion_area_ratio": _round(motion_area),
        "motion": _round(report.get("motion", 0.0)),
        "foreground_ratio": _round(foreground),
        "center_foreground_ratio": _round(report.get("center_foreground_ratio", 0.0)),
        "component_count": _round(report.get("component_count", 0.0)),
        "largest_component_ratio": _round(report.get("largest_component_ratio", 0.0)),
        "brightness": _round(report.get("brightness", 0.0)),
        "contrast": _round(contrast),
        "saturation": _round(report.get("saturation", 0.0)),
    }


def _phase(index: int, total: int) -> str:
    if total <= 1:
        return "single"
    ratio = index / max(1, total - 1)
    if ratio < 1 / 3:
        return "intro"
    if ratio < 2 / 3:
        return "middle"
    return "outro"


def _phase_summary(samples: list[dict[str, Any]]) -> list[dict[str, Any]]:
    summary = []
    for phase in ["intro", "middle", "outro", "single"]:
        phase_samples = [sample for sample in samples if sample["phase"] == phase]
        if not phase_samples:
            continue
        peak = max(phase_samples, key=lambda sample: sample["motion_area_ratio"])
        summary.append(
            {
                "phase": phase,
                "sample_count": len(phase_samples),
                "active_count": sum(bool(sample["active"]) for sample in phase_samples),
                "blank_count": sum(bool(sample["blank"]) for sample in phase_samples),
                "mean_motion_area_ratio": _round(_mean(phase_samples, "motion_area_ratio")),
                "mean_foreground_ratio": _round(_mean(phase_samples, "foreground_ratio")),
                "peak_motion_source_frame": peak["source_frame"],
            }
        )
    return summary


def _peaks(samples: list[dict[str, Any]], field: str, limit: int) -> list[dict[str, Any]]:
    ordered = sorted(samples, key=lambda sample: sample[field], reverse=True)
    return [
        {
            "source_frame": sample["source_frame"],
            field: sample[field],
            "phase": sample["phase"],
        }
        for sample in ordered[:limit]
    ]


def _longest_run(entries: list[tuple[int, bool]], *, active: bool) -> dict[str, int]:
    best = {"sample_start": 0, "sample_end": 0, "length": 0}
    start = None
    previous = None
    for index, is_active in entries:
        if is_active == active and start is None:
            start = index
        if is_active != active and start is not None:
            best = _better_run(best, start, previous)
            start = None
        previous = index
    if start is not None:
        best = _better_run(best, start, previous)
    return best


def _mean(samples: list[dict[str, Any]], field: str) -> float:
    return sum(float(sample[field]) for sample in samples) / len(samples) if samples else 0.0


def _round(value: float) -> float:
    return round(float(value), 6)


def _better_run(best: dict[str, int], start: int, end: int | None) -> dict[str, int]:
    end = start if end is None else end
    length = end - start + 1
    if length > best["length"]:
        return {"sample_start": start, "sample_end": end, "length": length}
    return best


def _source_run(run: dict[str, int], frame_step: int) -> dict[str, int]:
    return {
        **run,
        "source_start_frame": run["sample_start"] * frame_step,
        "source_end_frame": run["sample_end"] * frame_step,
    }


def _motion_profile(
    active_ratio: float,
    active_span_ratio: float,
    longest_stall_ratio: float,
) -> str:
    if active_ratio > 0.65 and longest_stall_ratio < 0.25:
        return "steady"
    if active_ratio < 0.25:
        return "sparse"
    if longest_stall_ratio > 0.45:
        return "stalled_sections"
    if active_span_ratio < 0.55:
        return "compressed_motion_window"
    return "varied"
