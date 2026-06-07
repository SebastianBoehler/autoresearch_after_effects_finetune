from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

from after_effects_pipeline.utils import write_json

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DECISIONS = {"render_missing", "rerender_stale", "fix_render"}


def main() -> None:
    args = _parse_args()
    records = _load_jsonl(args.dataset)
    queue = json.loads(args.queue.read_text())
    readiness = _load_optional_json(args.readiness_report)
    report = _build_report(
        records=records,
        queue=queue,
        readiness=readiness,
        decisions=set(args.decisions),
        harness_dir=args.harness_dir,
        dataset_path=args.dataset,
    )
    write_json(args.output, report)
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.write_text(_markdown(report))
    print(report["summary"])


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=Path, default=REPO_ROOT / "data/after_effects_synthetic_cases.jsonl")
    parser.add_argument("--queue", type=Path, default=REPO_ROOT / "artifacts/visual_analysis/render-review-queue.json")
    parser.add_argument("--readiness-report", type=Path, default=REPO_ROOT / "artifacts/datasets/after-effects-train-ready/readiness-report.json")
    parser.add_argument("--harness-dir", type=Path, default=REPO_ROOT / "artifacts/ae_live_checks/_manual_harnesses")
    parser.add_argument("--output", type=Path, default=REPO_ROOT / "artifacts/ae_live_checks/_manual_harnesses/status.json")
    parser.add_argument("--markdown-output", type=Path, default=REPO_ROOT / "artifacts/ae_live_checks/_manual_harnesses/status.md")
    parser.add_argument("--decisions", nargs="+", default=sorted(DEFAULT_DECISIONS))
    return parser.parse_args()


def _build_report(
    *,
    records: list[dict[str, Any]],
    queue: dict[str, Any],
    readiness: dict[str, Any] | None,
    decisions: set[str],
    harness_dir: Path,
    dataset_path: Path | None = None,
) -> dict[str, Any]:
    records_by_id = {record["case_id"]: record for record in records}
    queue_by_id = {item["case_id"]: item for item in queue.get("items", [])}
    case_ids = _target_case_ids(readiness, queue)
    cases = [
        _case_status(records_by_id[case_id], queue_by_id[case_id], dataset_path)
        for case_id in case_ids
        if case_id in records_by_id
        and queue_by_id.get(case_id, {}).get("decision") in decisions
    ]
    status_counts = Counter(case["status"] for case in cases)
    runner = _runner_status(harness_dir)
    return {
        "summary": {
            "target_count": len(cases),
            "status_counts": dict(sorted(status_counts.items())),
            "runner_report_exists": runner["exists"],
            "runner_completed_chunks": runner["completed_chunks"],
            "runner_error_chunks": runner["error_chunks"],
        },
        "runner": runner,
        "cases": cases,
    }


def _target_case_ids(readiness: dict[str, Any] | None, queue: dict[str, Any]) -> list[str]:
    if readiness and readiness.get("render_debt"):
        return [item["case_id"] for item in readiness["render_debt"]]
    return [item["case_id"] for item in queue.get("items", [])]


def _case_status(record: dict[str, Any], queue_item: dict[str, Any], dataset_path: Path | None = None) -> dict[str, Any]:
    case_id = record["case_id"]
    case_dir = REPO_ROOT / "artifacts/ae_live_checks" / case_id
    source_path = REPO_ROOT / record["source_repo_path"]
    report_path = case_dir / "report.txt"
    project_path = case_dir / "project.aep"
    render_path = case_dir / "render.mp4"
    ae_report = _parse_report(report_path)
    source_paths = [source_path, *( [dataset_path] if dataset_path else [] )]
    status = _status(source_paths, report_path, project_path, render_path, ae_report)
    return {
        "case_id": case_id,
        "decision": queue_item.get("decision"),
        "status": status,
        "project_path": str(project_path),
        "render_path": str(render_path),
        "report_path": str(report_path),
        "project_exists": project_path.exists(),
        "render_exists": render_path.exists(),
        "report_exists": report_path.exists(),
        "project_stale": _is_stale_against_any(project_path, source_paths),
        "render_stale": _is_stale(render_path, project_path),
        "ae_ok": ae_report.get("ok"),
        "ae_error": ae_report.get("error", ""),
    }


def _status(
    source_paths: list[Path],
    report_path: Path,
    project_path: Path,
    render_path: Path,
    ae_report: dict[str, str],
) -> str:
    if report_path.exists() and ae_report.get("ok") == "false":
        return "script_error"
    if not project_path.exists():
        return "not_run" if not report_path.exists() else "missing_project"
    if _is_stale_against_any(project_path, source_paths):
        return "stale_project"
    if not render_path.exists():
        return "project_ready"
    if _is_stale(render_path, project_path):
        return "render_stale"
    return "render_ready"


def _runner_status(harness_dir: Path) -> dict[str, Any]:
    path = harness_dir / "runner_report.txt"
    lines = path.read_text().splitlines() if path.exists() else []
    return {
        "path": str(path),
        "exists": path.exists(),
        "completed_chunks": sum(line.startswith("ok:") for line in lines),
        "error_chunks": sum(line.startswith("error:") for line in lines),
        "lines": lines,
    }


def _parse_report(path: Path) -> dict[str, str]:
    values = {}
    if not path.exists():
        return values
    for line in path.read_text(errors="replace").splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            values[key] = value
    return values


def _is_stale(path: Path, source_path: Path) -> bool:
    return path.exists() and source_path.exists() and path.stat().st_mtime < source_path.stat().st_mtime


def _is_stale_against_any(path: Path, source_paths: list[Path]) -> bool:
    return any(_is_stale(path, source_path) for source_path in source_paths)


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def _load_optional_json(path: Path) -> dict[str, Any] | None:
    return json.loads(path.read_text()) if path.exists() else None


def _markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Manual AE Harness Status",
        "",
        f"- targets: {report['summary']['target_count']}",
        f"- status counts: {_inline_counts(report['summary']['status_counts'])}",
        f"- runner report exists: {report['summary']['runner_report_exists']}",
        f"- completed chunks: {report['summary']['runner_completed_chunks']}",
        f"- error chunks: {report['summary']['runner_error_chunks']}",
        "",
        "| status | case | decision | AE error |",
        "| --- | --- | --- | --- |",
    ]
    for case in report["cases"]:
        lines.append(
            f"| {case['status']} | {case['case_id']} | {case['decision']} | "
            f"{case['ae_error'] or '-'} |"
        )
    return "\n".join(lines) + "\n"


def _inline_counts(counts: dict[str, int]) -> str:
    return ", ".join(f"{key}={value}" for key, value in counts.items()) or "-"


if __name__ == "__main__":
    main()
