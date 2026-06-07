from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from after_effects_pipeline.theme_motion_audit import (
    build_theme_motion_audit,
    render_theme_motion_markdown,
)
from after_effects_pipeline.utils import load_jsonl, write_json

REPO_ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    args = _parse_args()
    payload = build_theme_motion_audit(
        load_jsonl(args.source),
        queue=_load_json(args.queue),
        animation_anatomy=_load_json(args.animation_anatomy),
        quality_gap_matrix=_load_json(args.quality_gap_matrix),
    )
    write_json(args.output, payload)
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.write_text(render_theme_motion_markdown(payload))
    print(payload["summary"])


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=REPO_ROOT / "data/after_effects_synthetic_cases.jsonl")
    parser.add_argument("--queue", type=Path, default=REPO_ROOT / "artifacts/visual_analysis/render-review-queue.json")
    parser.add_argument("--animation-anatomy", type=Path, default=REPO_ROOT / "artifacts/visual_analysis/animation-anatomy.json")
    parser.add_argument("--quality-gap-matrix", type=Path, default=REPO_ROOT / "artifacts/visual_analysis/quality-gap-matrix.json")
    parser.add_argument("--output", type=Path, default=REPO_ROOT / "artifacts/visual_analysis/theme-motion-audit.json")
    parser.add_argument("--markdown-output", type=Path, default=REPO_ROOT / "artifacts/visual_analysis/theme-motion-audit.md")
    return parser.parse_args()


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text()) if path.exists() else {}


if __name__ == "__main__":
    main()
