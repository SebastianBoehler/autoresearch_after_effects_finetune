from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

from after_effects_pipeline.video_metrics import (
    aggregate_frame_reports,
    measure_frame,
    quality_notes_for_analysis,
    summarize_cases,
    warnings_for_analysis,
)
from after_effects_pipeline.video_quality import score_render_quality
from after_effects_pipeline.video_timeline import build_frame_timeline, build_motion_timeline


def analyze_render_tree(
    render_root: Path,
    *,
    frame_step: int = 3,
    sample_width: int = 320,
) -> dict[str, Any]:
    videos = sorted(render_root.glob("*/render.mp4"))
    cases = [
        analyze_video(path, frame_step=frame_step, sample_width=sample_width)
        for path in videos
    ]
    return {
        "render_root": str(render_root),
        "frame_step": frame_step,
        "sample_width": sample_width,
        "summary": summarize_cases(cases),
        "cases": cases,
    }


def render_markdown_report(payload: dict[str, Any]) -> str:
    lines = [
        "# Visual Render Analysis",
        "",
        f"Sampled every {payload['frame_step']}rd source frame at "
        f"{payload['sample_width']} px width.",
        "",
        "## Summary",
        "",
    ]
    summary = payload["summary"]
    lines.extend(
        [
            f"- cases: {summary['case_count']}",
            f"- mean motion: {summary['mean_motion']:.3f}",
            f"- mean active motion p95: {summary['mean_active_motion_p95']:.3f}",
            f"- mean active frame ratio: {summary['mean_active_frame_ratio']:.3f}",
            f"- mean foreground p95: {summary['mean_foreground_p95']:.3f}",
            f"- mean largest component p95: {summary['mean_largest_component_p95']:.3f}",
            f"- mean component count p95: {summary['mean_component_count_p95']:.1f}",
            f"- cases with warnings: {summary['cases_with_warnings']}",
            "",
            "## Cases",
            "",
            "| case | quality | priority | frames | motion | active p95 | active frames | profile | stall | foreground p95 | center p95 | largest comp | comp count | blank | notes | warnings |",
            "| --- | ---: | --- | ---: | ---: | ---: | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |",
        ]
    )
    for case in payload["cases"]:
        analysis = case["analysis"]
        timeline = analysis.get("motion_timeline", {})
        quality = case.get("render_quality", {})
        notes = ", ".join(case["notes"]) or "-"
        warnings = ", ".join(case["warnings"]) or "-"
        lines.append(
            f"| {case['case_id']} | {quality.get('score', 0.0):.3f} | "
            f"{quality.get('priority', '-')} | {analysis['sampled_frames']} | "
            f"{analysis['motion']['mean']:.3f} | "
            f"{analysis['motion_area_ratio']['p95']:.3f} | "
            f"{analysis['active_frame_ratio']:.3f} | "
            f"{timeline.get('motion_profile', '-')} | "
            f"{timeline.get('longest_stall_ratio', 0.0):.3f} | "
            f"{analysis['foreground_ratio']['p95']:.3f} | "
            f"{analysis['center_foreground_ratio']['p95']:.3f} | "
            f"{analysis['largest_component_ratio']['p95']:.3f} | "
            f"{analysis['component_count']['p95']:.0f} | "
            f"{analysis['blank_frame_ratio']:.3f} | {notes} | {warnings} |"
        )
    _append_timeline_highlights(lines, payload["cases"])
    return "\n".join(lines) + "\n"


def analyze_video(
    path: Path,
    *,
    frame_step: int = 3,
    sample_width: int = 320,
) -> dict[str, Any]:
    meta = _probe_video(path)
    width = min(sample_width, int(meta["width"]))
    height = _even_height(int(meta["width"]), int(meta["height"]), width)
    frames = _read_sampled_frames(path, frame_step=frame_step, width=width, height=height)
    frame_size = width * height * 3
    reports: list[dict[str, float]] = []
    previous: bytes | None = None
    for start in range(0, len(frames), frame_size):
        frame = frames[start : start + frame_size]
        if len(frame) != frame_size:
            continue
        reports.append(measure_frame(frame, previous, width, height))
        previous = frame

    analysis = aggregate_frame_reports(reports)
    analysis["motion_timeline"] = build_motion_timeline(
        reports,
        frame_step=frame_step,
    )
    analysis["frame_timeline"] = build_frame_timeline(
        reports,
        frame_step=frame_step,
    )
    warnings = warnings_for_analysis(analysis)
    return {
        "case_id": path.parent.name,
        "video_path": str(path),
        "source": meta,
        "sampled_size": {"width": width, "height": height},
        "analysis": analysis,
        "notes": quality_notes_for_analysis(analysis),
        "warnings": warnings,
        "render_quality": score_render_quality(analysis, warnings),
    }


def _probe_video(path: Path) -> dict[str, Any]:
    command = [
        "ffprobe",
        "-v",
        "error",
        "-select_streams",
        "v:0",
        "-show_entries",
        "stream=width,height,r_frame_rate,nb_frames,duration",
        "-show_entries",
        "format=duration",
        "-of",
        "json",
        str(path),
    ]
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or f"ffprobe failed for {path}")
    payload = json.loads(result.stdout)
    stream = payload["streams"][0]
    stream["fps"] = _parse_rate(stream.get("r_frame_rate", "0/1"))
    stream["duration"] = float(stream.get("duration") or payload["format"]["duration"])
    return stream


def _read_sampled_frames(path: Path, *, frame_step: int, width: int, height: int) -> bytes:
    vf = f"select='not(mod(n\\,{frame_step}))',scale={width}:{height},format=rgb24"
    command = [
        "ffmpeg",
        "-v",
        "error",
        "-i",
        str(path),
        "-vf",
        vf,
        "-vsync",
        "0",
        "-f",
        "rawvideo",
        "-",
    ]
    result = subprocess.run(command, capture_output=True, check=False)
    if result.returncode != 0:
        stderr = result.stderr.decode("utf-8", errors="replace")
        raise RuntimeError(stderr.strip() or f"ffmpeg failed for {path}")
    return result.stdout


def _parse_rate(rate: str) -> float:
    numerator, denominator = rate.split("/")
    return float(numerator) / float(denominator)


def _even_height(source_width: int, source_height: int, width: int) -> int:
    height = round(source_height * width / source_width)
    return height if height % 2 == 0 else height + 1


def _append_timeline_highlights(lines: list[str], cases: list[dict[str, Any]]) -> None:
    rows = []
    for case in cases:
        timeline = case["analysis"].get("frame_timeline", {})
        phases = timeline.get("phase_summary", [])
        if not phases:
            continue
        rows.append(
            "| "
            f"{case['case_id']} | "
            f"{_phase_text(phases)} | "
            f"{_peak_text(timeline.get('motion_peaks', []), 'motion_area_ratio')} | "
            f"{_peak_text(timeline.get('foreground_peaks', []), 'foreground_ratio')} |"
        )
    if not rows:
        return
    lines.extend(
        [
            "",
            "## Timeline Highlights",
            "",
            "| case | phases | motion peaks | foreground peaks |",
            "| --- | --- | --- | --- |",
            *rows,
        ]
    )


def _phase_text(phases: list[dict[str, Any]]) -> str:
    return "; ".join(
        f"{phase['phase']} m={phase['mean_motion_area_ratio']:.3f} "
        f"fg={phase['mean_foreground_ratio']:.3f} "
        f"a={phase['active_count']}/{phase['sample_count']} "
        f"b={phase['blank_count']}"
        for phase in phases
    )


def _peak_text(peaks: list[dict[str, Any]], field: str) -> str:
    if not peaks:
        return "-"
    return ", ".join(
        f"f{peak['source_frame']} {peak[field]:.3f} {peak['phase']}"
        for peak in peaks[:3]
    )
