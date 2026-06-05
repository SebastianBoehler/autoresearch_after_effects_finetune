from pathlib import Path

from after_effects_pipeline.dataset import build_dataset
from after_effects_pipeline.types import DatasetSourceConfig, SplitConfig
from after_effects_pipeline.utils import write_jsonl


def test_build_dataset_writes_chat_splits(tmp_path: Path):
    source = tmp_path / "cases.jsonl"
    records = []
    for index in range(5):
        records.append(
            {
                "case_id": f"case_{index}",
                "prompt": "Create an AE comp.",
                "completion": 'app.beginUndoGroup("x"); app.project.items.addComp("C", 10, 10, 1, 1, 1); app.endUndoGroup();',
                "license": "MIT",
                "expected": {"comp_name": "C"},
            }
        )
    write_jsonl(source, records)
    output = tmp_path / "dataset"
    manifest = build_dataset(
        DatasetSourceConfig(path=str(source)),
        output,
        SplitConfig(train_fraction=0.6, valid_fraction=0.2, seed=1),
    )
    assert manifest["counts"] == {"train": 3, "valid": 1, "test": 1}
    assert (output / "train.jsonl").exists()

