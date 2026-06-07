from __future__ import annotations

import argparse
import json
from pathlib import Path

from after_effects_pipeline.split_safety import (
    build_split_safety_audit,
    split_safety_markdown,
)
from after_effects_pipeline.utils import load_json, write_json

REPO_ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    args = _parse_args()
    payload = build_split_safety_audit(
        load_json(args.render_overlap),
        split_by_case=_load_split_map(args.split_dir),
        max_animation_signature_per_split=args.max_animation_signature_per_split,
    )
    write_json(args.output, payload)
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.write_text(split_safety_markdown(payload))
    print(payload["summary"])


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--render-overlap",
        type=Path,
        default=REPO_ROOT / "artifacts/visual_analysis/render-overlap.json",
    )
    parser.add_argument(
        "--split-dir",
        type=Path,
        default=REPO_ROOT / "artifacts/datasets/after-effects-train-ready",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=REPO_ROOT / "artifacts/visual_analysis/split-safety.json",
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=REPO_ROOT / "artifacts/visual_analysis/split-safety.md",
    )
    parser.add_argument("--max-animation-signature-per-split", type=int, default=2)
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
