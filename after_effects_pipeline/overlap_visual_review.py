from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any, Callable

from after_effects_pipeline.utils import ensure_dir


def build_overlap_visual_review(
    *,
    render_overlap: dict[str, Any],
    contact_sheet_dir: Path,
    output_dir: Path,
    limit: int = 12,
    runner: Callable[..., subprocess.CompletedProcess[bytes]] = subprocess.run,
) -> dict[str, Any]:
    ensure_dir(output_dir)
    pairs = render_overlap.get("potential_overlaps", [])[:limit]
    items = []
    for index, pair in enumerate(pairs, start=1):
        output_path = output_dir / _pair_filename(index, pair)
        item = _build_pair_sheet(pair, contact_sheet_dir, output_path, runner)
        item["rank"] = index
        items.append(item)
    return {
        "summary": {
            "pair_count": len(items),
            "ok_count": sum(item["ok"] for item in items),
            "same_split_count": sum(bool(item["same_split"]) for item in items),
            "limit": limit,
            "output_dir": str(output_dir),
        },
        "pairs": items,
    }


def render_overlap_visual_review_markdown(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# Overlap Visual Review",
        "",
        "Side-by-side contact sheets for the highest-scoring rendered overlap pairs.",
        "",
        f"- pairs: {summary['pair_count']}",
        f"- generated: {summary['ok_count']}",
        f"- same-split pairs: {summary['same_split_count']}",
        "",
        "| rank | pair | score | splits | shared signals | sheet |",
        "| ---: | --- | ---: | --- | --- | --- |",
    ]
    base = Path(summary["output_dir"]).parent
    for pair in payload["pairs"]:
        sheet = _relative(Path(pair["output_path"]), base) if pair["ok"] else "-"
        label = f"{pair['a']} / {pair['b']}"
        splits = f"{pair['split_a'] or '-'} / {pair['split_b'] or '-'}"
        signals = ", ".join(pair["shared_signals"][:4]) or "-"
        lines.append(
            f"| {pair['rank']} | {label} | {pair['score']:.4f} | "
            f"{splits} | {signals} | [{('open' if pair['ok'] else 'missing')}]({sheet}) |"
        )
    return "\n".join(lines) + "\n"


def _build_pair_sheet(
    pair: dict[str, Any],
    contact_sheet_dir: Path,
    output_path: Path,
    runner: Callable[..., subprocess.CompletedProcess[bytes]],
) -> dict[str, Any]:
    a_path = contact_sheet_dir / f"{pair['a']}.png"
    b_path = contact_sheet_dir / f"{pair['b']}.png"
    result = _pair_payload(pair, output_path)
    if not a_path.exists() or not b_path.exists():
        result.update({"ok": False, "missing": [str(path) for path in [a_path, b_path] if not path.exists()]})
        return result
    output_path.parent.mkdir(parents=True, exist_ok=True)
    command = [
        "ffmpeg",
        "-y",
        "-v",
        "error",
        "-i",
        str(a_path),
        "-i",
        str(b_path),
        "-filter_complex",
        "[0:v]scale=-1:720[left];[1:v]scale=-1:720[right];[left][right]hstack=inputs=2",
        "-frames:v",
        "1",
        str(output_path),
    ]
    process = runner(command, capture_output=True, check=False)
    result.update({
        "ok": process.returncode == 0 and output_path.exists(),
        "missing": [],
        "returncode": process.returncode,
        "stderr": (process.stderr or b"").decode("utf-8", "replace")[-1000:],
    })
    return result


def _pair_payload(pair: dict[str, Any], output_path: Path) -> dict[str, Any]:
    return {
        "a": pair["a"],
        "b": pair["b"],
        "score": float(pair["score"]),
        "split_a": pair.get("split_a"),
        "split_b": pair.get("split_b"),
        "same_split": bool(pair.get("same_split")),
        "shared_signals": list(pair.get("shared_signals", [])),
        "output_path": str(output_path),
    }


def _pair_filename(index: int, pair: dict[str, Any]) -> str:
    return f"{index:02d}_{pair['a']}__{pair['b']}.png"


def _relative(path: Path, base: Path) -> str:
    try:
        return path.relative_to(base).as_posix()
    except ValueError:
        return path.as_posix()
