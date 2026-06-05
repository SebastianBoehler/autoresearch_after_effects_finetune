from __future__ import annotations

from pathlib import Path
from typing import Any

from after_effects_pipeline.ae_runtime import run_live_check
from after_effects_pipeline.dataset_sources import load_source_records
from after_effects_pipeline.quality import score_case, summarize_scores
from after_effects_pipeline.static_check import extract_code
from after_effects_pipeline.types import ExperimentConfig
from after_effects_pipeline.utils import write_json


def verify_source_cases(
    *,
    config: ExperimentConfig,
    repo_root: Path,
    output_path: Path,
    run_live: bool | None = None,
    run_render: bool | None = None,
) -> dict[str, Any]:
    records, source_label = load_source_records(config.source_dataset)
    max_cases = config.evaluation.max_cases or len(records)
    selected = records[:max_cases]
    live_enabled = config.evaluation.run_live_ae if run_live is None else run_live
    render_enabled = config.evaluation.run_render if run_render is None else run_render
    live_dir = repo_root / "artifacts" / "ae_live_checks"
    results: list[dict[str, Any]] = []

    for case in selected:
        code = extract_code(case["completion"])
        live_result = None
        if live_enabled:
            live_result = run_live_check(
                case=case,
                code=code,
                runtime=config.evaluation.runtime,
                output_dir=live_dir,
                timeout_seconds=config.evaluation.max_seconds,
                render=render_enabled,
            )
        results.append(
            score_case(
                case,
                code=code,
                weights=config.evaluation.metric_weights,
                live_result=live_result,
            )
        )

    payload = {
        "run_name": config.name,
        "source_dataset": source_label,
        "summary": summarize_scores(results),
        "cases": results,
    }
    write_json(output_path, payload)
    return payload

