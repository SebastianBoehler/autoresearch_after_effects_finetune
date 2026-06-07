from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from after_effects_pipeline.overlap_visual_review import (
    build_overlap_visual_review,
    render_overlap_visual_review_markdown,
)
from after_effects_pipeline.utils import write_json

REPO_ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    args = _parse_args()
    payload = build_overlap_visual_review(
        render_overlap=_load_json(args.render_overlap),
        contact_sheet_dir=args.contact_sheet_dir,
        output_dir=args.output_dir,
        limit=args.limit,
    )
    write_json(args.output, payload)
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.write_text(render_overlap_visual_review_markdown(payload))
    print(payload["summary"])


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--render-overlap", type=Path, default=REPO_ROOT / "artifacts/visual_analysis/render-overlap.json")
    parser.add_argument("--contact-sheet-dir", type=Path, default=REPO_ROOT / "artifacts/visual_analysis/contact_sheets")
    parser.add_argument("--output-dir", type=Path, default=REPO_ROOT / "artifacts/visual_analysis/overlap_review")
    parser.add_argument("--output", type=Path, default=REPO_ROOT / "artifacts/visual_analysis/overlap-visual-review.json")
    parser.add_argument("--markdown-output", type=Path, default=REPO_ROOT / "artifacts/visual_analysis/overlap-visual-review.md")
    parser.add_argument("--limit", type=int, default=12)
    return parser.parse_args()


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text()) if path.exists() else {}


if __name__ == "__main__":
    main()
