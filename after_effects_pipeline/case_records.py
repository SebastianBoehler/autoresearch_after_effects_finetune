from __future__ import annotations

import random
from typing import Any

from after_effects_pipeline.types import DatasetFilterConfig, SplitConfig

DEFAULT_SYSTEM = (
    "You write complete Adobe After Effects ExtendScript JSX scripts. "
    "Return only code. Create a named composition, use app.beginUndoGroup and "
    "app.endUndoGroup, and avoid external assets unless the prompt asks for them."
)

REQUIRED_FIELDS = {"case_id", "prompt", "completion", "license", "expected"}


def prepare_cases(
    records: list[dict[str, Any]],
    dataset_filter: DatasetFilterConfig,
    source_label: str,
) -> list[dict[str, Any]]:
    prepared: list[dict[str, Any]] = []
    seen: set[str] = set()
    for record in records:
        missing = REQUIRED_FIELDS - set(record)
        if missing:
            raise ValueError(f"case missing required fields: {sorted(missing)}")
        if record["case_id"] in seen:
            raise ValueError(f"duplicate case_id: {record['case_id']}")
        seen.add(record["case_id"])
        tags = set(record.get("tags", []))
        if dataset_filter.include_tags and not tags.intersection(
            dataset_filter.include_tags
        ):
            continue
        if tags.intersection(dataset_filter.exclude_tags):
            continue
        quality = float(record.get("quality_score", 0.0))
        if quality < dataset_filter.min_quality_score:
            continue
        prepared.append({**record, "source_dataset": source_label})
    return prepared


def split_cases(
    cases: list[dict[str, Any]],
    split_config: SplitConfig,
) -> dict[str, list[dict[str, Any]]]:
    shuffled = list(cases)
    random.Random(split_config.seed).shuffle(shuffled)
    total = len(shuffled)
    train_end = int(total * split_config.train_fraction)
    valid_end = train_end + int(total * split_config.valid_fraction)
    if total >= 3:
        train_end = max(1, min(train_end, total - 2))
        valid_end = max(train_end + 1, min(valid_end, total - 1))
    return {
        "train": shuffled[:train_end],
        "valid": shuffled[train_end:valid_end],
        "test": shuffled[valid_end:],
    }


def case_to_chat_record(case: dict[str, Any]) -> dict[str, Any]:
    return {
        **case,
        "messages": [
            {"role": "system", "content": case.get("system", DEFAULT_SYSTEM)},
            {"role": "user", "content": case["prompt"]},
            {"role": "assistant", "content": case["completion"]},
        ],
    }

