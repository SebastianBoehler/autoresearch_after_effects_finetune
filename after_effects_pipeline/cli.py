from __future__ import annotations

import argparse
from pathlib import Path

from after_effects_pipeline.dataset import build_dataset
from after_effects_pipeline.eval import verify_source_cases
from after_effects_pipeline.hf_dataset import export_hf_dataset
from after_effects_pipeline.mlx import train_adapter
from after_effects_pipeline.review import build_review_queue
from after_effects_pipeline.types import ExperimentConfig
from after_effects_pipeline.utils import repo_root_from, write_json


def main() -> None:
    parser = argparse.ArgumentParser(prog="after_effects_pipeline")
    subparsers = parser.add_subparsers(dest="command", required=True)

    build = subparsers.add_parser("build-dataset")
    build.add_argument("--config", required=True)

    verify = subparsers.add_parser("verify-source")
    verify.add_argument("--config", required=True)
    verify.add_argument("--output")
    verify.add_argument("--live", action="store_true")
    verify.add_argument("--render", action="store_true")

    export = subparsers.add_parser("export-hf-dataset")
    export.add_argument("--config", required=True)
    export.add_argument("--output-dir", required=True)
    export.add_argument("--repo-id", required=True)
    export.add_argument("--pretty-name", default="Autoresearch After Effects")

    review = subparsers.add_parser("build-review-queue")
    review.add_argument("--config", required=True)
    review.add_argument("--verification", required=True)
    review.add_argument("--output-dir", required=True)

    train = subparsers.add_parser("train")
    train.add_argument("--config", required=True)

    args = parser.parse_args()
    config = ExperimentConfig.load(args.config)
    repo_root = repo_root_from(Path(args.config))

    if args.command == "build-dataset":
        manifest = build_dataset(
            source=config.source_dataset,
            output_dir=repo_root / config.dataset_dir,
            split_config=config.splits,
            dataset_filter=config.dataset_filter,
        )
        write_json(repo_root / config.dataset_dir / "manifest.json", manifest)
        print(f"wrote dataset splits to {repo_root / config.dataset_dir}")
        return

    if args.command == "verify-source":
        output = Path(args.output) if args.output else repo_root / config.eval_output_path
        payload = verify_source_cases(
            config=config,
            repo_root=repo_root,
            output_path=output,
            run_live=args.live,
            run_render=args.render,
        )
        print(payload["summary"])
        return

    if args.command == "export-hf-dataset":
        payload = export_hf_dataset(
            config=config,
            dataset_dir=repo_root / config.dataset_dir,
            output_dir=Path(args.output_dir),
            repo_id=args.repo_id,
            pretty_name=args.pretty_name,
        )
        print(payload)
        return

    if args.command == "build-review-queue":
        payload = build_review_queue(
            config=config,
            verification_path=Path(args.verification),
            output_dir=Path(args.output_dir),
        )
        print(payload)
        return

    if args.command == "train":
        log_path = repo_root / "artifacts" / "logs" / f"{config.name}-train.log"
        train_adapter(config, repo_root / config.dataset_dir, log_path)
        print(f"wrote train log to {log_path}")


if __name__ == "__main__":
    main()
