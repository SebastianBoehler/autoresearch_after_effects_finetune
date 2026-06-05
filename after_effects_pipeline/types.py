from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class SplitConfig:
    train_fraction: float = 0.7
    valid_fraction: float = 0.15
    seed: int = 42


@dataclass
class DatasetFilterConfig:
    include_tags: list[str] = field(default_factory=list)
    exclude_tags: list[str] = field(default_factory=list)
    min_quality_score: float = 0.0


@dataclass
class DatasetSourceConfig:
    kind: str = "local"
    path: str | None = None
    repo_id: str | None = None
    split: str = "train"
    revision: str | None = None

    @classmethod
    def load(cls, raw: str | dict[str, Any]) -> "DatasetSourceConfig":
        if isinstance(raw, str):
            return cls(path=raw)
        return cls(**raw)

    def describe(self) -> str:
        if self.kind == "local":
            if not self.path:
                raise ValueError("local source_dataset requires path")
            return self.path
        if self.kind == "hf":
            if not self.repo_id:
                raise ValueError("hf source_dataset requires repo_id")
            revision = f"@{self.revision}" if self.revision else ""
            return f"hf://{self.repo_id}{revision}:{self.split}"
        raise ValueError(f"unsupported source_dataset kind: {self.kind}")


@dataclass
class TrainConfig:
    fine_tune_type: str = "lora"
    optimizer: str = "adamw"
    mask_prompt: bool = True
    num_layers: int = 12
    batch_size: int = 1
    iters: int = 120
    val_batches: int = 8
    learning_rate: float = 8e-5
    steps_per_report: int = 10
    steps_per_eval: int = 20
    grad_accumulation_steps: int = 8
    save_every: int = 20
    test_batches: int = -1
    max_seq_length: int = 3072
    grad_checkpoint: bool = True
    seed: int = 42


@dataclass
class GenerationConfig:
    max_tokens: int = 2400
    temperature: float = 0.35
    top_p: float = 0.9
    top_k: int = 40
    seed: int = 42


@dataclass
class MetricWeights:
    static_syntax: float = 0.25
    ae_contract: float = 0.2
    required_snippets: float = 0.2
    forbidden_snippets: float = 0.1
    live_execution: float = 0.15
    render: float = 0.1


@dataclass
class AfterEffectsRuntimeConfig:
    app_name: str = "Adobe After Effects 2026"
    aerender_path: str | None = "/Applications/Adobe After Effects 2026/aerender"
    composition_name_fallback: str = "Generated Comp"
    output_extension: str = "mov"


@dataclass
class EvaluationConfig:
    run_live_ae: bool = False
    run_render: bool = False
    max_cases: int = 0
    max_seconds: int = 180
    min_promote_score: float = 0.82
    metric_weights: MetricWeights = field(default_factory=MetricWeights)
    runtime: AfterEffectsRuntimeConfig = field(default_factory=AfterEffectsRuntimeConfig)


@dataclass
class ExperimentConfig:
    name: str
    base_model: str
    source_dataset: DatasetSourceConfig
    dataset_dir: str
    adapter_path: str
    eval_output_path: str
    results_tsv: str = "results.tsv"
    run_loss_eval: bool = True
    dataset_filter: DatasetFilterConfig = field(default_factory=DatasetFilterConfig)
    splits: SplitConfig = field(default_factory=SplitConfig)
    train: TrainConfig = field(default_factory=TrainConfig)
    generation: GenerationConfig = field(default_factory=GenerationConfig)
    evaluation: EvaluationConfig = field(default_factory=EvaluationConfig)

    @classmethod
    def load(cls, path: str | Path) -> "ExperimentConfig":
        raw = json.loads(Path(path).read_text())
        evaluation_raw = raw.get("evaluation", {})
        return cls(
            name=raw["name"],
            base_model=raw["base_model"],
            source_dataset=DatasetSourceConfig.load(raw["source_dataset"]),
            dataset_dir=raw["dataset_dir"],
            adapter_path=raw["adapter_path"],
            eval_output_path=raw["eval_output_path"],
            results_tsv=raw.get("results_tsv", "results.tsv"),
            run_loss_eval=raw.get("run_loss_eval", True),
            dataset_filter=DatasetFilterConfig(**raw.get("dataset_filter", {})),
            splits=SplitConfig(**raw.get("splits", {})),
            train=TrainConfig(**raw.get("train", {})),
            generation=GenerationConfig(**raw.get("generation", {})),
            evaluation=EvaluationConfig(
                metric_weights=MetricWeights(
                    **evaluation_raw.get("metric_weights", {})
                ),
                runtime=AfterEffectsRuntimeConfig(
                    **evaluation_raw.get("runtime", {})
                ),
                **{
                    key: value
                    for key, value in evaluation_raw.items()
                    if key not in {"metric_weights", "runtime"}
                },
            ),
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

