from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from after_effects_pipeline.training_sample_diagnosis import (
    build_training_sample_diagnosis,
    render_training_sample_diagnosis_markdown,
)
from after_effects_pipeline.utils import write_json

REPO_ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    args = _parse_args()
    payload = build_training_sample_diagnosis(
        render_analysis=_load_json(args.render_analysis),
        queue=_load_json(args.queue),
        render_overlap=_load_json(args.render_overlap),
        animation_anatomy=_load_json(args.animation_anatomy),
        theme_motion_audit=_load_json(args.theme_motion_audit),
        quality_gap_matrix=_load_json(args.quality_gap_matrix),
    )
    write_json(args.output, payload)
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.write_text(render_training_sample_diagnosis_markdown(payload))
    print(payload["summary"])


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--render-analysis", type=Path, default=REPO_ROOT / "artifacts/visual_analysis/render-analysis.json")
    parser.add_argument("--queue", type=Path, default=REPO_ROOT / "artifacts/visual_analysis/render-review-queue.json")
    parser.add_argument("--render-overlap", type=Path, default=REPO_ROOT / "artifacts/visual_analysis/render-overlap.json")
    parser.add_argument("--animation-anatomy", type=Path, default=REPO_ROOT / "artifacts/visual_analysis/animation-anatomy.json")
    parser.add_argument("--theme-motion-audit", type=Path, default=REPO_ROOT / "artifacts/visual_analysis/theme-motion-audit.json")
    parser.add_argument("--quality-gap-matrix", type=Path, default=REPO_ROOT / "artifacts/visual_analysis/quality-gap-matrix.json")
    parser.add_argument("--output", type=Path, default=REPO_ROOT / "artifacts/visual_analysis/training-sample-diagnosis.json")
    parser.add_argument("--markdown-output", type=Path, default=REPO_ROOT / "artifacts/visual_analysis/training-sample-diagnosis.md")
    return parser.parse_args()


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text()) if path.exists() else {}


if __name__ == "__main__":
    main()
