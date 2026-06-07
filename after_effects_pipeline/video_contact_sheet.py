from __future__ import annotations

import math
import subprocess
from pathlib import Path
from typing import Any

from after_effects_pipeline.utils import ensure_dir


def build_contact_sheet_tree(
    render_root: Path,
    output_dir: Path,
    *,
    frame_step: int = 3,
    thumb_width: int = 120,
    columns: int = 12,
    max_frames: int = 96,
) -> dict[str, Any]:
    videos = sorted(render_root.glob("*/render.mp4"))
    ensure_dir(output_dir)
    _remove_stale_case_sheets(output_dir, {f"{path.parent.name}.png" for path in videos})
    cases = [
        build_contact_sheet(
            path,
            output_dir / f"{path.parent.name}.png",
            frame_step=frame_step,
            thumb_width=thumb_width,
            columns=columns,
            max_frames=max_frames,
        )
        for path in videos
    ]
    return {
        "render_root": str(render_root),
        "output_dir": str(output_dir),
        "frame_step": frame_step,
        "thumb_width": thumb_width,
        "columns": columns,
        "max_frames": max_frames,
        "case_count": len(cases),
        "cases": cases,
    }


def build_contact_sheet(
    video_path: Path,
    output_path: Path,
    *,
    frame_step: int,
    thumb_width: int,
    columns: int,
    max_frames: int,
) -> dict[str, Any]:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    rows = sheet_rows(columns=columns, max_frames=max_frames)
    command = [
        "ffmpeg",
        "-y",
        "-v",
        "error",
        "-i",
        str(video_path),
        "-vf",
        sheet_filter(
            frame_step=frame_step,
            thumb_width=thumb_width,
            columns=columns,
            rows=rows,
        ),
        "-frames:v",
        "1",
        str(output_path),
    ]
    result = subprocess.run(command, capture_output=True, check=False)
    return {
        "case_id": video_path.parent.name,
        "video_path": str(video_path),
        "output_path": str(output_path),
        "ok": result.returncode == 0 and output_path.exists(),
        "returncode": result.returncode,
        "stderr": result.stderr.decode("utf-8", errors="replace")[-2000:],
    }


def render_contact_sheet_markdown(
    payload: dict[str, Any],
    render_analysis: dict[str, Any] | None = None,
) -> str:
    analysis_by_case = {
        case["case_id"]: case
        for case in (render_analysis or {}).get("cases", [])
    }
    output_dir = Path(payload["output_dir"])
    lines = [
        "# Render Contact Sheets",
        "",
        f"- cases: {payload['case_count']}",
        f"- sampled every {payload['frame_step']}rd source frame",
        f"- thumbnail width: {payload['thumb_width']} px",
        f"- max sampled frames per sheet: {payload['max_frames']}",
        "",
        "| case | sheet | notes | warnings |",
        "| --- | --- | --- | --- |",
    ]
    for case in payload["cases"]:
        analysis = analysis_by_case.get(case["case_id"], {})
        notes = ", ".join(analysis.get("notes", [])) or "-"
        warnings = ", ".join(analysis.get("warnings", [])) or "-"
        sheet = _relative_markdown_path(Path(case["output_path"]), output_dir.parent)
        label = "open" if case["ok"] else "failed"
        lines.append(f"| {case['case_id']} | [{label}]({sheet}) | {notes} | {warnings} |")
    return "\n".join(lines) + "\n"


def sheet_filter(
    *,
    frame_step: int,
    thumb_width: int,
    columns: int,
    rows: int,
) -> str:
    return (
        f"select='not(mod(n\\,{frame_step}))',"
        f"scale={thumb_width}:-1,"
        f"tile={columns}x{rows}:padding=4:margin=4:color=black"
    )


def sheet_rows(*, columns: int, max_frames: int) -> int:
    return max(1, math.ceil(max_frames / columns))


def _relative_markdown_path(path: Path, base: Path) -> str:
    try:
        return path.relative_to(base).as_posix()
    except ValueError:
        return path.as_posix()


def _remove_stale_case_sheets(output_dir: Path, expected_names: set[str]) -> None:
    preserved = {"all_samples.png", "changed_cases.png"}
    for path in output_dir.glob("*.png"):
        if path.name not in expected_names and path.name not in preserved:
            path.unlink()
