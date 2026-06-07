from __future__ import annotations

import argparse
from pathlib import Path

from after_effects_pipeline.animation_anatomy import (
    build_animation_anatomy_audit,
    render_animation_anatomy_markdown,
)
from after_effects_pipeline.utils import load_json, write_json

REPO_ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    args = _parse_args()
    payload = build_animation_anatomy_audit(
        load_json(args.render_analysis),
        render_queue=load_json(args.render_queue) if args.render_queue.exists() else None,
    )
    write_json(args.output, payload)
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.write_text(render_animation_anatomy_markdown(payload))
    print(payload["summary"])


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--render-analysis",
        type=Path,
        default=REPO_ROOT / "artifacts/visual_analysis/render-analysis.json",
    )
    parser.add_argument(
        "--render-queue",
        type=Path,
        default=REPO_ROOT / "artifacts/visual_analysis/render-review-queue.json",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=REPO_ROOT / "artifacts/visual_analysis/animation-anatomy.json",
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=REPO_ROOT / "artifacts/visual_analysis/animation-anatomy.md",
    )
    return parser.parse_args()


if __name__ == "__main__":
    main()
