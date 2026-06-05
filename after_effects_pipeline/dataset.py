from __future__ import annotations

from pathlib import Path
from typing import Any

from after_effects_pipeline.case_records import (
    case_to_chat_record,
    prepare_cases,
    split_cases,
)
from after_effects_pipeline.dataset_sources import load_source_records
from after_effects_pipeline.types import (
    DatasetFilterConfig,
    DatasetSourceConfig,
    SplitConfig,
)
from after_effects_pipeline.utils import ensure_dir, write_json, write_jsonl


def build_dataset(
    source: DatasetSourceConfig | Path,
    output_dir: Path,
    split_config: SplitConfig,
    dataset_filter: DatasetFilterConfig | None = None,
) -> dict[str, Any]:
    source_config = (
        DatasetSourceConfig(path=str(source)) if isinstance(source, Path) else source
    )
    records, source_label = load_source_records(source_config)
    effective_filter = dataset_filter or DatasetFilterConfig()
    cases = prepare_cases(records, effective_filter, source_label)
    split_map = split_cases(cases, split_config)
    ensure_dir(output_dir)

    counts: dict[str, int] = {}
    for split_name, split_cases_ in split_map.items():
        write_jsonl(
            output_dir / f"{split_name}.jsonl",
            [case_to_chat_record(case) for case in split_cases_],
        )
        counts[split_name] = len(split_cases_)

    manifest = {
        "source_dataset": source_label,
        "output_dir": str(output_dir),
        "split_seed": split_config.seed,
        "dataset_filter": effective_filter.__dict__,
        "counts": counts,
    }
    write_json(output_dir / "manifest.json", manifest)
    return manifest

