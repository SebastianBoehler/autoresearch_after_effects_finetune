from __future__ import annotations

import argparse
from pathlib import Path

from after_effects_pipeline.overlap_remediation import (
    build_overlap_remediation,
    render_overlap_remediation_markdown,
)
from after_effects_pipeline.utils import load_json, write_json

REPO_ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    args = _parse_args()
    payload = build_overlap_remediation(
        render_overlap=load_json(args.render_overlap),
        source_pattern_audit=load_json(args.source_pattern_audit),
        render_queue=load_json(args.render_queue),
    )
    write_json(args.output, payload)
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.write_text(render_overlap_remediation_markdown(payload))
    print(payload["summary"])


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--render-overlap", type=Path, default=REPO_ROOT / "artifacts/visual_analysis/render-overlap.json")
    parser.add_argument("--source-pattern-audit", type=Path, default=REPO_ROOT / "artifacts/visual_analysis/source-pattern-audit.json")
    parser.add_argument("--render-queue", type=Path, default=REPO_ROOT / "artifacts/visual_analysis/render-review-queue.json")
    parser.add_argument("--output", type=Path, default=REPO_ROOT / "artifacts/visual_analysis/overlap-remediation.json")
    parser.add_argument("--markdown-output", type=Path, default=REPO_ROOT / "artifacts/visual_analysis/overlap-remediation.md")
    return parser.parse_args()


if __name__ == "__main__":
    main()
