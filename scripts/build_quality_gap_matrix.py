from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from after_effects_pipeline.quality_gap_matrix import (
    build_quality_gap_matrix,
    render_quality_gap_matrix_markdown,
)
from after_effects_pipeline.utils import write_json

REPO_ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    args = _parse_args()
    payload = build_quality_gap_matrix(
        queue=_load_json(args.queue),
        render_overlap=_load_json(args.render_overlap),
        animation_anatomy=_load_json(args.animation_anatomy),
        render_progression=_load_json(args.render_progression),
        render_unlock_plan=_load_json(args.render_unlock_plan),
    )
    write_json(args.output, payload)
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.write_text(render_quality_gap_matrix_markdown(payload))
    print(payload["summary"])


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--queue", type=Path, default=REPO_ROOT / "artifacts/visual_analysis/render-review-queue.json")
    parser.add_argument("--render-overlap", type=Path, default=REPO_ROOT / "artifacts/visual_analysis/render-overlap.json")
    parser.add_argument("--animation-anatomy", type=Path, default=REPO_ROOT / "artifacts/visual_analysis/animation-anatomy.json")
    parser.add_argument("--render-progression", type=Path, default=REPO_ROOT / "artifacts/visual_analysis/render-progression.json")
    parser.add_argument("--render-unlock-plan", type=Path, default=REPO_ROOT / "artifacts/visual_analysis/render-unlock-plan.json")
    parser.add_argument("--output", type=Path, default=REPO_ROOT / "artifacts/visual_analysis/quality-gap-matrix.json")
    parser.add_argument("--markdown-output", type=Path, default=REPO_ROOT / "artifacts/visual_analysis/quality-gap-matrix.md")
    return parser.parse_args()


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text()) if path.exists() else {}


if __name__ == "__main__":
    main()
