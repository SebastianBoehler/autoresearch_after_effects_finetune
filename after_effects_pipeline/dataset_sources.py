from __future__ import annotations

from pathlib import Path
from typing import Any

from datasets import load_dataset

from after_effects_pipeline.types import DatasetSourceConfig
from after_effects_pipeline.utils import load_jsonl


def load_source_records(source: DatasetSourceConfig) -> tuple[list[dict[str, Any]], str]:
    label = source.describe()
    if source.kind == "local":
        return load_jsonl(Path(source.path or "")), label
    dataset = load_dataset(
        source.repo_id,
        split=source.split,
        revision=source.revision,
    )
    return [dict(record) for record in dataset], label

