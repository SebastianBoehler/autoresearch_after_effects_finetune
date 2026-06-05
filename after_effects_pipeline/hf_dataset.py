from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

from after_effects_pipeline.case_records import case_to_chat_record, prepare_cases
from after_effects_pipeline.dataset_sources import load_source_records
from after_effects_pipeline.types import ExperimentConfig
from after_effects_pipeline.utils import ensure_dir, write_jsonl


def export_hf_dataset(
    *,
    config: ExperimentConfig,
    dataset_dir: Path,
    output_dir: Path,
    repo_id: str,
    pretty_name: str,
) -> dict[str, Any]:
    records, source_label = load_source_records(config.source_dataset)
    cases = prepare_cases(records, config.dataset_filter, source_label)
    ensure_dir(output_dir)
    write_jsonl(output_dir / "cases.jsonl", cases)
    write_jsonl(output_dir / "chat.jsonl", [case_to_chat_record(case) for case in cases])

    copied_splits: list[str] = []
    for split in ["train", "valid", "test"]:
        source_path = dataset_dir / f"{split}.jsonl"
        if source_path.exists():
            shutil.copy2(source_path, output_dir / f"{split}.jsonl")
            copied_splits.append(split)

    (output_dir / "README.md").write_text(
        _dataset_card(
            repo_id=repo_id,
            pretty_name=pretty_name,
            source_label=source_label,
            num_cases=len(cases),
            copied_splits=copied_splits,
        )
    )
    return {
        "repo_id": repo_id,
        "output_dir": str(output_dir),
        "num_cases": len(cases),
        "splits": copied_splits,
    }


def _dataset_card(
    *,
    repo_id: str,
    pretty_name: str,
    source_label: str,
    num_cases: int,
    copied_splits: list[str],
) -> str:
    split_text = ", ".join(copied_splits) if copied_splits else "not exported"
    return f"""---
license: mit
language:
- en
task_categories:
- text-generation
tags:
- after-effects
- extendscript
- jsx
- code-generation
- synthetic
pretty_name: {pretty_name}
size_categories:
- n<1K
---

# {pretty_name}

HF repo id: `{repo_id}`

This is a provenance-first synthetic dataset for generating Adobe After Effects
ExtendScript / JSX scripts. Each row contains a natural-language motion-design
prompt, a complete script completion, expected composition metadata, required
and forbidden snippets, and source/license metadata.

## Files

- `cases.jsonl`: canonical case records.
- `chat.jsonl`: all cases converted to chat messages.
- `train.jsonl`, `valid.jsonl`, `test.jsonl`: MLX-ready chat splits when present.

Exported cases: `{num_cases}`

Split files: `{split_text}`

Source dataset: `{source_label}`

## License And Provenance

Rows are generated from first-party templates in this repository and are marked
MIT. Do not add copied Adobe documentation or unlicensed public snippets without
preserving their original license and provenance metadata.
"""

