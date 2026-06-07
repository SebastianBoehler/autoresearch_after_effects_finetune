from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from after_effects_pipeline.manual_render_briefing import (
    build_manual_render_briefing,
    render_manual_render_briefing_markdown,
)
from after_effects_pipeline.utils import write_json

REPO_ROOT = Path(__file__).resolve().parents[1]
RUNNER = REPO_ROOT / "artifacts/ae_live_checks/_manual_harnesses_render_unlocks/run_all_harnesses.jsx"


def main() -> None:
    args = _parse_args()
    payload = build_manual_render_briefing(
        quality_gap_matrix=_load_json(args.quality_gap_matrix),
        batch_status=_load_json(args.batch_status),
        runner_path=str(args.runner),
    )
    write_json(args.output, payload)
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.write_text(render_manual_render_briefing_markdown(payload))
    print(payload["summary"])


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--quality-gap-matrix", type=Path, default=REPO_ROOT / "artifacts/visual_analysis/quality-gap-matrix.json")
    parser.add_argument("--batch-status", type=Path, default=REPO_ROOT / "artifacts/visual_analysis/render-unlock-batch-status.json")
    parser.add_argument("--runner", type=Path, default=RUNNER)
    parser.add_argument("--output", type=Path, default=REPO_ROOT / "artifacts/visual_analysis/manual-render-briefing.json")
    parser.add_argument("--markdown-output", type=Path, default=REPO_ROOT / "artifacts/visual_analysis/manual-render-briefing.md")
    return parser.parse_args()


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text()) if path.exists() else {}


if __name__ == "__main__":
    main()
