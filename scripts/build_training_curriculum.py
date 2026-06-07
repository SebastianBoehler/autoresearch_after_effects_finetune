from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from after_effects_pipeline.training_curriculum import (
    build_training_curriculum,
    render_training_curriculum_markdown,
)
from after_effects_pipeline.utils import write_json

REPO_ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    args = _parse_args()
    payload = build_training_curriculum(
        diagnosis=_load_json(args.diagnosis),
        split_safety=_load_json(args.split_safety),
        quality_gate=_load_json(args.quality_gate),
    )
    write_json(args.output, payload)
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.write_text(render_training_curriculum_markdown(payload))
    print(payload["summary"])


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--diagnosis", type=Path, default=REPO_ROOT / "artifacts/visual_analysis/training-sample-diagnosis.json")
    parser.add_argument("--split-safety", type=Path, default=REPO_ROOT / "artifacts/visual_analysis/split-safety.json")
    parser.add_argument("--quality-gate", type=Path, default=REPO_ROOT / "artifacts/datasets/after-effects-train-ready/quality-gate.json")
    parser.add_argument("--output", type=Path, default=REPO_ROOT / "artifacts/visual_analysis/training-curriculum.json")
    parser.add_argument("--markdown-output", type=Path, default=REPO_ROOT / "artifacts/visual_analysis/training-curriculum.md")
    return parser.parse_args()


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text()) if path.exists() else {}


if __name__ == "__main__":
    main()
