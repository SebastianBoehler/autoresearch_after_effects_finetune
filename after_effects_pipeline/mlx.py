from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path
from typing import Any

from after_effects_pipeline.types import ExperimentConfig
from after_effects_pipeline.utils import ensure_parent

FLOAT_PATTERN = r"([0-9]+(?:\.[0-9]+)?)"
LOSS_PATTERN = re.compile(rf"\btest loss\b[:=]?\s*{FLOAT_PATTERN}", re.IGNORECASE)
PPL_PATTERN = re.compile(rf"\bperplexity\b[:=]?\s*{FLOAT_PATTERN}", re.IGNORECASE)


def train_adapter(config: ExperimentConfig, dataset_dir: Path, log_path: Path) -> str:
    command = _base_lora_command(config, dataset_dir)
    command.append("--train")
    return _run(command, log_path)


def evaluate_loss(
    config: ExperimentConfig,
    dataset_dir: Path,
    adapter_path: Path,
    log_path: Path,
) -> dict[str, Any]:
    command = _base_lora_command(config, dataset_dir)
    command.extend(["--adapter-path", str(adapter_path), "--test"])
    output = _run(command, log_path)
    return {
        "test_loss": _parse_float(LOSS_PATTERN, output),
        "test_perplexity": _parse_float(PPL_PATTERN, output),
    }


def _base_lora_command(config: ExperimentConfig, dataset_dir: Path) -> list[str]:
    train = config.train
    command = [
        sys.executable,
        "-m",
        "mlx_lm",
        "lora",
        "--model",
        config.base_model,
        "--data",
        str(dataset_dir),
        "--adapter-path",
        config.adapter_path,
        "--fine-tune-type",
        train.fine_tune_type,
        "--optimizer",
        train.optimizer,
        "--num-layers",
        str(train.num_layers),
        "--batch-size",
        str(train.batch_size),
        "--iters",
        str(train.iters),
        "--val-batches",
        str(train.val_batches),
        "--learning-rate",
        str(train.learning_rate),
        "--steps-per-report",
        str(train.steps_per_report),
        "--steps-per-eval",
        str(train.steps_per_eval),
        "--grad-accumulation-steps",
        str(train.grad_accumulation_steps),
        "--save-every",
        str(train.save_every),
        "--test-batches",
        str(train.test_batches),
        "--max-seq-length",
        str(train.max_seq_length),
        "--seed",
        str(train.seed),
    ]
    if train.mask_prompt:
        command.append("--mask-prompt")
    if train.grad_checkpoint:
        command.append("--grad-checkpoint")
    return command


def _run(command: list[str], log_path: Path) -> str:
    ensure_parent(log_path)
    with log_path.open("w") as handle:
        result = subprocess.run(
            command,
            stdout=handle,
            stderr=subprocess.STDOUT,
            text=True,
            check=False,
        )
    output = log_path.read_text()
    if result.returncode != 0:
        raise RuntimeError(output)
    return output


def _parse_float(pattern: re.Pattern[str], text: str) -> float | None:
    match = pattern.search(text)
    return float(match.group(1)) if match else None

