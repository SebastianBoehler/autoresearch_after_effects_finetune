from __future__ import annotations

import argparse
import json
from pathlib import Path

from after_effects_pipeline.render_overlap import (
    build_render_overlap_audit,
    render_overlap_markdown,
)
from after_effects_pipeline.utils import load_json, write_json

REPO_ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    args = _parse_args()
    payload = build_render_overlap_audit(
        load_json(args.render_analysis),
        split_by_case=_load_split_map(args.split_dir),
        threshold=args.threshold,
        limit=args.limit,
    )
    write_json(args.output, payload)
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.write_text(render_overlap_markdown(payload))
    print(payload["summary"])


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--render-analysis",
        type=Path,
        default=REPO_ROOT / "artifacts/visual_analysis/render-analysis.json",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=REPO_ROOT / "artifacts/visual_analysis/render-overlap.json",
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=REPO_ROOT / "artifacts/visual_analysis/render-overlap.md",
    )
    parser.add_argument("--threshold", type=float, default=0.86)
    parser.add_argument("--limit", type=int, default=30)
    parser.add_argument(
        "--split-dir",
        type=Path,
        default=REPO_ROOT / "artifacts/datasets/after-effects-train-ready",
    )
    return parser.parse_args()


def _load_split_map(split_dir: Path) -> dict[str, str]:
    split_by_case = {}
    for split in ["train", "valid", "test"]:
        path = split_dir / f"{split}.jsonl"
        if not path.exists():
            continue
        for line in path.read_text().splitlines():
            if line.strip():
                case_id = json.loads(line).get("case_id")
                if case_id:
                    split_by_case[case_id] = split
    return split_by_case


if __name__ == "__main__":
    main()
