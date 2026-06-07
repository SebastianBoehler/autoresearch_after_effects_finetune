from __future__ import annotations

import argparse
from pathlib import Path

from after_effects_pipeline.dataset_sources import load_source_records
from after_effects_pipeline.source_motion_audit import (
    audit_source_motion,
    render_source_motion_markdown,
)
from after_effects_pipeline.types import ExperimentConfig
from after_effects_pipeline.utils import repo_root_from, write_json


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="configs/lfm25_8b_a1b_after_effects.json")
    parser.add_argument(
        "--output",
        default="artifacts/visual_analysis/source-motion-audit.json",
    )
    parser.add_argument(
        "--markdown-output",
        default="artifacts/visual_analysis/source-motion-audit.md",
    )
    args = parser.parse_args()
    config = ExperimentConfig.load(args.config)
    repo_root = repo_root_from(Path(args.config))
    records, _source_label = load_source_records(config.source_dataset)
    payload = audit_source_motion(records)
    output = repo_root / args.output
    markdown_output = repo_root / args.markdown_output
    write_json(output, payload)
    markdown_output.parent.mkdir(parents=True, exist_ok=True)
    markdown_output.write_text(render_source_motion_markdown(payload))
    print(payload["summary"])


if __name__ == "__main__":
    main()
