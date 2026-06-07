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
    curated_split_map = _curated_split_map(source_config, effective_filter, source_label)
    split_map = curated_split_map or split_cases(
        prepare_cases(records, effective_filter, source_label),
        split_config,
    )
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
        "split_source": "curated" if curated_split_map else "generated",
        "dataset_filter": effective_filter.__dict__,
        "counts": counts,
    }
    write_json(output_dir / "manifest.json", manifest)
    return manifest


def _curated_split_map(
    source_config: DatasetSourceConfig,
    dataset_filter: DatasetFilterConfig,
    source_label: str,
) -> dict[str, list[dict[str, Any]]] | None:
    if source_config.kind != "local" or not source_config.path:
        return None
    source_path = Path(source_config.path)
    if source_path.name != "cases.jsonl":
        return None
    split_paths = {name: source_path.with_name(f"{name}.jsonl") for name in ["train", "valid", "test"]}
    if not all(path.exists() for path in split_paths.values()):
        return None
    split_map = {
        name: prepare_cases(load_source_records(DatasetSourceConfig(path=str(path)))[0], dataset_filter, source_label)
        for name, path in split_paths.items()
    }
    _validate_disjoint_splits(split_map)
    return split_map


def _validate_disjoint_splits(split_map: dict[str, list[dict[str, Any]]]) -> None:
    seen = {}
    for split, cases in split_map.items():
        for case in cases:
            case_id = case["case_id"]
            if case_id in seen:
                raise ValueError(f"case_id {case_id} appears in both {seen[case_id]} and {split}")
            seen[case_id] = split
