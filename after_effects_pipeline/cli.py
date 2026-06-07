from __future__ import annotations

import argparse
from pathlib import Path

from after_effects_pipeline.dataset import build_dataset
from after_effects_pipeline.dataset_audit import audit_dataset, render_audit_markdown
from after_effects_pipeline.dataset_sources import load_source_records
from after_effects_pipeline.diversity_audit import (
    build_diversity_audit,
    render_diversity_markdown,
)
from after_effects_pipeline.eval import verify_source_cases
from after_effects_pipeline.hf_dataset import export_hf_dataset
from after_effects_pipeline.mlx import train_adapter
from after_effects_pipeline.review import build_review_queue
from after_effects_pipeline.render_review_queue import (
    build_render_review_queue,
    render_review_queue_markdown,
)
from after_effects_pipeline.types import ExperimentConfig
from after_effects_pipeline.utils import load_json, repo_root_from, write_json
from after_effects_pipeline.video_analysis import (
    analyze_render_tree,
    render_markdown_report,
)
from after_effects_pipeline.video_contact_sheet import (
    build_contact_sheet_tree,
    render_contact_sheet_markdown,
)


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

    analyze = subparsers.add_parser("analyze-renders")
    analyze.add_argument("--config", required=True)
    analyze.add_argument("--render-root", default="artifacts/ae_live_checks")
    analyze.add_argument("--output", default="artifacts/visual_analysis/render-analysis.json")
    analyze.add_argument("--markdown-output", default="artifacts/visual_analysis/render-analysis.md")
    analyze.add_argument("--frame-step", type=int, default=3)
    analyze.add_argument("--sample-width", type=int, default=320)

    audit = subparsers.add_parser("audit-dataset")
    audit.add_argument("--config", required=True)
    audit.add_argument("--render-analysis", default="artifacts/visual_analysis/render-analysis.json")
    audit.add_argument("--output", default="artifacts/visual_analysis/dataset-audit.json")
    audit.add_argument("--markdown-output", default="artifacts/visual_analysis/dataset-audit.md")

    sheets = subparsers.add_parser("contact-sheets")
    sheets.add_argument("--config", required=True)
    sheets.add_argument("--render-root", default="artifacts/ae_live_checks")
    sheets.add_argument("--output-dir", default="artifacts/visual_analysis/contact_sheets")
    sheets.add_argument("--output", default="artifacts/visual_analysis/contact-sheets.json")
    sheets.add_argument("--markdown-output", default="artifacts/visual_analysis/contact-sheets.md")
    sheets.add_argument("--render-analysis", default="artifacts/visual_analysis/render-analysis.json")
    sheets.add_argument("--frame-step", type=int, default=3)
    sheets.add_argument("--thumb-width", type=int, default=120)
    sheets.add_argument("--columns", type=int, default=12)
    sheets.add_argument("--max-frames", type=int, default=96)

    render_queue = subparsers.add_parser("render-review-queue")
    render_queue.add_argument("--config", required=True)
    render_queue.add_argument(
        "--render-analysis",
        default="artifacts/visual_analysis/render-analysis.json",
    )
    render_queue.add_argument(
        "--dataset-audit",
        default="artifacts/visual_analysis/dataset-audit.json",
    )
    render_queue.add_argument(
        "--contact-sheets",
        default="artifacts/visual_analysis/contact-sheets.json",
    )
    render_queue.add_argument(
        "--manual-decisions",
        default="artifacts/visual_analysis/manual-review-decisions.json",
    )
    render_queue.add_argument(
        "--output",
        default="artifacts/visual_analysis/render-review-queue.json",
    )
    render_queue.add_argument(
        "--markdown-output",
        default="artifacts/visual_analysis/render-review-queue.md",
    )

    diversity = subparsers.add_parser("diversity-audit")
    diversity.add_argument("--config", required=True)
    diversity.add_argument(
        "--render-review-queue",
        default="artifacts/visual_analysis/render-review-queue.json",
    )
    diversity.add_argument(
        "--output",
        default="artifacts/visual_analysis/diversity-audit.json",
    )
    diversity.add_argument(
        "--markdown-output",
        default="artifacts/visual_analysis/diversity-audit.md",
    )

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
        try:
            payload = verify_source_cases(
                config=config,
                repo_root=repo_root,
                output_path=output,
                run_live=args.live,
                run_render=args.render,
            )
        except RuntimeError as exc:
            raise SystemExit(str(exc)) from exc
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
        return

    if args.command == "analyze-renders":
        payload = analyze_render_tree(
            repo_root / args.render_root,
            frame_step=args.frame_step,
            sample_width=args.sample_width,
        )
        output = repo_root / args.output
        markdown_output = repo_root / args.markdown_output
        write_json(output, payload)
        markdown_output.parent.mkdir(parents=True, exist_ok=True)
        markdown_output.write_text(render_markdown_report(payload))
        print(payload["summary"])
        return

    if args.command == "audit-dataset":
        records, _source_label = load_source_records(config.source_dataset)
        render_path = repo_root / args.render_analysis
        render_analysis = load_json(render_path) if render_path.exists() else None
        payload = audit_dataset(records, render_analysis, repo_root=repo_root)
        output = repo_root / args.output
        markdown_output = repo_root / args.markdown_output
        write_json(output, payload)
        markdown_output.parent.mkdir(parents=True, exist_ok=True)
        markdown_output.write_text(render_audit_markdown(payload))
        print(
            {
                "case_count": payload["case_count"],
                "undercovered_categories": payload["undercovered_categories"],
                "missing_render_count": payload["missing_render_count"],
                "stale_render_count": payload["stale_render_count"],
                "render_warning_count": payload["render_warning_count"],
                "actionable_render_warning_count": payload[
                    "actionable_render_warning_count"
                ],
            }
        )
        return

    if args.command == "contact-sheets":
        payload = build_contact_sheet_tree(
            repo_root / args.render_root,
            repo_root / args.output_dir,
            frame_step=args.frame_step,
            thumb_width=args.thumb_width,
            columns=args.columns,
            max_frames=args.max_frames,
        )
        render_path = repo_root / args.render_analysis
        render_analysis = load_json(render_path) if render_path.exists() else None
        output = repo_root / args.output
        markdown_output = repo_root / args.markdown_output
        write_json(output, payload)
        markdown_output.parent.mkdir(parents=True, exist_ok=True)
        markdown_output.write_text(
            render_contact_sheet_markdown(payload, render_analysis)
        )
        print(
            {
                "case_count": payload["case_count"],
                "ok_count": sum(bool(case["ok"]) for case in payload["cases"]),
                "output_dir": str(repo_root / args.output_dir),
            }
        )
        return

    if args.command == "render-review-queue":
        records, _source_label = load_source_records(config.source_dataset)
        render_path = repo_root / args.render_analysis
        audit_path = repo_root / args.dataset_audit
        sheets_path = repo_root / args.contact_sheets
        decisions_path = repo_root / args.manual_decisions
        payload = build_render_review_queue(
            records,
            render_analysis=load_json(render_path) if render_path.exists() else None,
            dataset_audit=load_json(audit_path) if audit_path.exists() else None,
            contact_sheets=load_json(sheets_path) if sheets_path.exists() else None,
            manual_decisions=load_json(decisions_path) if decisions_path.exists() else None,
        )
        output = repo_root / args.output
        markdown_output = repo_root / args.markdown_output
        write_json(output, payload)
        markdown_output.parent.mkdir(parents=True, exist_ok=True)
        markdown_output.write_text(render_review_queue_markdown(payload))
        print(
            {
                "case_count": payload["case_count"],
                "train_ready_count": payload["train_ready_count"],
                "decision_counts": payload["decision_counts"],
            }
        )
        return

    if args.command == "diversity-audit":
        records, _source_label = load_source_records(config.source_dataset)
        queue_path = repo_root / args.render_review_queue
        payload = build_diversity_audit(
            records,
            render_queue=load_json(queue_path) if queue_path.exists() else None,
        )
        output = repo_root / args.output
        markdown_output = repo_root / args.markdown_output
        write_json(output, payload)
        markdown_output.parent.mkdir(parents=True, exist_ok=True)
        markdown_output.write_text(render_diversity_markdown(payload))
        print(payload["summary"])


if __name__ == "__main__":
    main()
