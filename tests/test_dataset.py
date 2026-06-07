from pathlib import Path

from after_effects_pipeline.dataset import build_dataset
from after_effects_pipeline.types import DatasetSourceConfig, SplitConfig
from after_effects_pipeline.utils import write_jsonl


def test_build_dataset_writes_chat_splits(tmp_path: Path):
    source = tmp_path / "cases.jsonl"
    records = [_record(f"case_{index}") for index in range(5)]
    write_jsonl(source, records)
    output = tmp_path / "dataset"
    manifest = build_dataset(
        DatasetSourceConfig(path=str(source)),
        output,
        SplitConfig(train_fraction=0.6, valid_fraction=0.2, seed=1),
    )
    assert manifest["counts"] == {"train": 3, "valid": 1, "test": 1}
    assert (output / "train.jsonl").exists()


def test_build_dataset_preserves_curated_sibling_splits(tmp_path: Path):
    source = tmp_path / "cases.jsonl"
    records = [_record(f"case_{index}") for index in range(6)]
    write_jsonl(source, records)
    write_jsonl(tmp_path / "train.jsonl", [records[0], records[1]])
    write_jsonl(tmp_path / "valid.jsonl", [records[2]])
    write_jsonl(tmp_path / "test.jsonl", [records[3], records[4], records[5]])

    manifest = build_dataset(
        DatasetSourceConfig(path=str(source)),
        tmp_path / "dataset",
        SplitConfig(train_fraction=0.6, valid_fraction=0.2, seed=1),
    )

    assert manifest["split_source"] == "curated"
    assert manifest["counts"] == {"train": 2, "valid": 1, "test": 3}


def _record(case_id):
    return {
        "case_id": case_id,
        "prompt": "Create an AE comp.",
        "completion": 'app.beginUndoGroup("x"); app.project.items.addComp("C", 10, 10, 1, 1, 1); app.endUndoGroup();',
        "license": "MIT",
        "expected": {"comp_name": "C"},
    }
