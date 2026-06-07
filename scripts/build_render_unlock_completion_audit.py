from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from after_effects_pipeline.render_unlock_completion import (
    build_render_unlock_completion,
    render_render_unlock_completion_markdown,
)
from after_effects_pipeline.utils import write_json

REPO_ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    args = _parse_args()
    payload = build_render_unlock_completion(
        plan=_load_json(args.plan),
        train_ready_manifest=_load_json(args.train_ready_manifest),
        capability_audit=_load_json(args.capability_audit),
        inspiration_coverage=_load_json(args.inspiration_coverage),
        source_pattern_audit=_load_json(args.source_pattern_audit),
    )
    write_json(args.output, payload)
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.write_text(render_render_unlock_completion_markdown(payload))
    print(payload["summary"])


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--plan", type=Path, default=REPO_ROOT / "artifacts/visual_analysis/render-unlock-plan.json")
    parser.add_argument("--train-ready-manifest", type=Path, default=REPO_ROOT / "artifacts/datasets/after-effects-train-ready/manifest.json")
    parser.add_argument("--capability-audit", type=Path, default=REPO_ROOT / "artifacts/visual_analysis/source-capability-audit.json")
    parser.add_argument("--inspiration-coverage", type=Path, default=REPO_ROOT / "artifacts/visual_analysis/inspiration-coverage.json")
    parser.add_argument("--source-pattern-audit", type=Path, default=REPO_ROOT / "artifacts/visual_analysis/source-pattern-audit.json")
    parser.add_argument("--output", type=Path, default=REPO_ROOT / "artifacts/visual_analysis/render-unlock-completion.json")
    parser.add_argument("--markdown-output", type=Path, default=REPO_ROOT / "artifacts/visual_analysis/render-unlock-completion.md")
    return parser.parse_args()


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text()) if path.exists() else {}


if __name__ == "__main__":
    main()
