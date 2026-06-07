from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from after_effects_pipeline.render_unlock_plan import (
    build_render_unlock_plan,
    render_render_unlock_plan_markdown,
)
from after_effects_pipeline.utils import write_json

REPO_ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    args = _parse_args()
    plan = build_render_unlock_plan(
        readiness_report=_load_json(args.readiness_report),
        capability_audit=_load_json(args.capability_audit),
        inspiration_coverage=_load_json(args.inspiration_coverage),
        render_progression=_load_json(args.render_progression),
        queue=_load_json(args.queue),
        source_pattern_audit=_load_json(args.source_pattern_audit),
        animation_anatomy=_load_json(args.animation_anatomy),
        theme_motion_audit=_load_json(args.theme_motion_audit),
    )
    write_json(args.output, plan)
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.write_text(render_render_unlock_plan_markdown(plan))
    print(plan["summary"])


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--readiness-report", type=Path, default=REPO_ROOT / "artifacts/datasets/after-effects-train-ready/readiness-report.json")
    parser.add_argument("--capability-audit", type=Path, default=REPO_ROOT / "artifacts/visual_analysis/source-capability-audit.json")
    parser.add_argument("--inspiration-coverage", type=Path, default=REPO_ROOT / "artifacts/visual_analysis/inspiration-coverage.json")
    parser.add_argument("--render-progression", type=Path, default=REPO_ROOT / "artifacts/visual_analysis/render-progression.json")
    parser.add_argument("--source-pattern-audit", type=Path, default=REPO_ROOT / "artifacts/visual_analysis/source-pattern-audit.json")
    parser.add_argument("--animation-anatomy", type=Path, default=REPO_ROOT / "artifacts/visual_analysis/animation-anatomy.json")
    parser.add_argument("--theme-motion-audit", type=Path, default=REPO_ROOT / "artifacts/visual_analysis/theme-motion-audit.json")
    parser.add_argument("--queue", type=Path, default=REPO_ROOT / "artifacts/visual_analysis/render-review-queue.json")
    parser.add_argument("--output", type=Path, default=REPO_ROOT / "artifacts/visual_analysis/render-unlock-plan.json")
    parser.add_argument("--markdown-output", type=Path, default=REPO_ROOT / "artifacts/visual_analysis/render-unlock-plan.md")
    return parser.parse_args()


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text()) if path.exists() else {}


if __name__ == "__main__":
    main()
