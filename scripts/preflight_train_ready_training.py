from __future__ import annotations

import argparse
import importlib.util
import json
import shlex
from pathlib import Path
from typing import Any

from after_effects_pipeline.mlx import _base_lora_command
from after_effects_pipeline.types import ExperimentConfig
from after_effects_pipeline.utils import write_json

REPO_ROOT = Path(__file__).resolve().parents[1]
REQUIRED_SPLITS = ("train", "valid", "test")


def main() -> None:
    args = _parse_args()
    config = ExperimentConfig.load(args.config)
    dataset_dir = (REPO_ROOT / config.dataset_dir).resolve()
    report = _preflight(config, dataset_dir)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    write_json(args.output, report)
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.write_text(_markdown(report))
    print(
        {
            "ok": report["ok"],
            "dataset_dir": report["dataset_dir"],
            "counts": report["split_counts"],
            "mlx_lm_available": report["mlx_lm_available"],
        }
    )
    if not report["ok"]:
        raise SystemExit(1)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config",
        type=Path,
        default=REPO_ROOT / "configs/lfm25_8b_a1b_after_effects_train_ready.json",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=REPO_ROOT / "artifacts/datasets/lfm25-8b-a1b-after-effects-train-ready/training-preflight.json",
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=REPO_ROOT / "artifacts/datasets/lfm25-8b-a1b-after-effects-train-ready/training-preflight.md",
    )
    return parser.parse_args()


def _preflight(config: ExperimentConfig, dataset_dir: Path) -> dict[str, Any]:
    split_reports = [_split_report(dataset_dir / f"{split}.jsonl") for split in REQUIRED_SPLITS]
    command = [*_base_lora_command(config, dataset_dir), "--train"]
    issues = [
        issue
        for report in split_reports
        for issue in report["issues"]
    ]
    if not _module_available("mlx_lm"):
        issues.append("mlx_lm is not importable")
    if not _module_available("mlx"):
        issues.append("mlx is not importable")
    return {
        "ok": not issues,
        "issues": issues,
        "dataset_dir": str(dataset_dir),
        "split_counts": {
            report["split"]: report["count"]
            for report in split_reports
        },
        "split_reports": split_reports,
        "mlx_lm_available": _module_available("mlx_lm"),
        "mlx_available": _module_available("mlx"),
        "adapter_path": config.adapter_path,
        "base_model": config.base_model,
        "train_command": command,
        "train_command_shell": " ".join(shlex.quote(part) for part in command),
    }


def _split_report(path: Path) -> dict[str, Any]:
    issues = []
    records = []
    split = path.stem
    if not path.exists():
        return {"split": split, "path": str(path), "count": 0, "issues": ["missing split file"]}
    for line_number, line in enumerate(path.read_text().splitlines(), start=1):
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError as error:
            issues.append(f"line {line_number}: invalid JSON: {error.msg}")
            continue
        record_issues = _record_issues(record, line_number)
        issues.extend(record_issues)
        records.append(record)
    if not records:
        issues.append("split has no records")
    return {
        "split": split,
        "path": str(path),
        "count": len(records),
        "issues": issues,
    }


def _record_issues(record: dict[str, Any], line_number: int) -> list[str]:
    issues = []
    messages = record.get("messages")
    if not isinstance(messages, list) or len(messages) != 3:
        return [f"line {line_number}: expected three chat messages"]
    expected_roles = ["system", "user", "assistant"]
    for index, role in enumerate(expected_roles):
        message = messages[index]
        if message.get("role") != role:
            issues.append(f"line {line_number}: message {index} role is not {role}")
        if not isinstance(message.get("content"), str) or not message["content"].strip():
            issues.append(f"line {line_number}: message {index} content is empty")
    return issues


def _module_available(name: str) -> bool:
    return importlib.util.find_spec(name) is not None


def _markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Train-Ready Training Preflight",
        "",
        f"- ok: {report['ok']}",
        f"- dataset: {report['dataset_dir']}",
        f"- base model: {report['base_model']}",
        f"- adapter path: {report['adapter_path']}",
        f"- mlx_lm available: {report['mlx_lm_available']}",
        f"- mlx available: {report['mlx_available']}",
        "",
        "## Splits",
        "",
    ]
    for split, count in report["split_counts"].items():
        lines.append(f"- {split}: {count}")
    lines.extend(["", "## Command", "", "```bash", report["train_command_shell"], "```"])
    if report["issues"]:
        lines.extend(["", "## Issues", ""])
        lines.extend(f"- {issue}" for issue in report["issues"])
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    main()
