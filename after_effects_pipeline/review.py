from __future__ import annotations

from pathlib import Path
from typing import Any

from after_effects_pipeline.dataset_sources import load_source_records
from after_effects_pipeline.types import ExperimentConfig
from after_effects_pipeline.utils import ensure_dir, load_json, write_jsonl


def build_review_queue(
    *,
    config: ExperimentConfig,
    verification_path: Path,
    output_dir: Path,
) -> dict[str, Any]:
    verification = load_json(verification_path)
    records, _ = load_source_records(config.source_dataset)
    cases_by_id = {record["case_id"]: record for record in records}
    ensure_dir(output_dir)
    queue = []
    for result in verification.get("cases", []):
        case = cases_by_id[result["case_id"]]
        queue.append(
            {
                "case_id": result["case_id"],
                "prompt": case["prompt"],
                "quality_score": result["quality_score"],
                "issues": result["issues"],
                "review_status": "pending",
                "review_notes": "",
                "promote": result["quality_score"]
                >= config.evaluation.min_promote_score
                and not result["issues"],
                "completion": case["completion"],
                "expected": case.get("expected", {}),
                "tags": case.get("tags", []),
            }
        )
    queue_path = output_dir / "review_queue.jsonl"
    write_jsonl(queue_path, queue)
    return {"queue_path": str(queue_path), "num_items": len(queue)}

