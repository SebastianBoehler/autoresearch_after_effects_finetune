from __future__ import annotations

import argparse
import json
from pathlib import Path

from after_effects_pipeline.dataset_sources import load_source_records
from after_effects_pipeline.source_pattern_audit import (
    build_source_pattern_audit,
    render_source_pattern_markdown,
)
from after_effects_pipeline.types import ExperimentConfig
from after_effects_pipeline.utils import repo_root_from, write_json


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="configs/lfm25_8b_a1b_after_effects.json")
    parser.add_argument("--queue", default="artifacts/visual_analysis/render-review-queue.json")
    parser.add_argument("--output", default="artifacts/visual_analysis/source-pattern-audit.json")
    parser.add_argument("--markdown-output", default="artifacts/visual_analysis/source-pattern-audit.md")
    args = parser.parse_args()
    repo_root = repo_root_from(Path(args.config))
    config = ExperimentConfig.load(args.config)
    records, _source_label = load_source_records(config.source_dataset)
    queue_path = repo_root / args.queue
    queue = json.loads(queue_path.read_text()) if queue_path.exists() else {}
    payload = build_source_pattern_audit(records, render_queue=queue)
    output = repo_root / args.output
    markdown_output = repo_root / args.markdown_output
    write_json(output, payload)
    markdown_output.parent.mkdir(parents=True, exist_ok=True)
    markdown_output.write_text(render_source_pattern_markdown(payload))
    print(payload["summary"])


if __name__ == "__main__":
    main()
