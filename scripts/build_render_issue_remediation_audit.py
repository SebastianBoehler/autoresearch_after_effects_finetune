from __future__ import annotations

import argparse
from pathlib import Path

from after_effects_pipeline.render_issue_remediation import (
    build_render_issue_remediation,
    render_render_issue_remediation_markdown,
)
from after_effects_pipeline.utils import load_json, write_json

REPO_ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    args = _parse_args()
    payload = build_render_issue_remediation(
        render_progression=load_json(args.render_progression),
        render_analysis=load_json(args.render_analysis),
        render_queue=load_json(args.render_queue),
        source_motion=load_json(args.source_motion),
        source_quality=load_json(args.source_quality),
    )
    write_json(args.output, payload)
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.write_text(render_render_issue_remediation_markdown(payload))
    print(payload["summary"])


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--render-progression", type=Path, default=REPO_ROOT / "artifacts/visual_analysis/render-progression.json")
    parser.add_argument("--render-analysis", type=Path, default=REPO_ROOT / "artifacts/visual_analysis/render-analysis.json")
    parser.add_argument("--render-queue", type=Path, default=REPO_ROOT / "artifacts/visual_analysis/render-review-queue.json")
    parser.add_argument("--source-motion", type=Path, default=REPO_ROOT / "artifacts/visual_analysis/source-motion-audit.json")
    parser.add_argument("--source-quality", type=Path, default=REPO_ROOT / "artifacts/visual_analysis/source-animation-quality.json")
    parser.add_argument("--output", type=Path, default=REPO_ROOT / "artifacts/visual_analysis/render-issue-remediation.json")
    parser.add_argument("--markdown-output", type=Path, default=REPO_ROOT / "artifacts/visual_analysis/render-issue-remediation.md")
    return parser.parse_args()


if __name__ == "__main__":
    main()
