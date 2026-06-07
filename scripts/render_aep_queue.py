from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DECISIONS = {"render_missing", "rerender_stale", "fix_render"}


def main() -> None:
    args = _parse_args()
    records = _load_records(args.dataset)
    queue = json.loads(args.queue.read_text())
    case_ids = _case_ids_from_status(args.status_report, set(args.statuses)) if args.status_report else None
    results = []
    for item in queue.get("items", []):
        if case_ids is not None and item["case_id"] not in case_ids:
            continue
        if item.get("decision") not in set(args.decisions):
            continue
        record = records.get(item["case_id"])
        if not record:
            continue
        results.append(_render_case(record, args.aerender, args.force))
    print({"attempted": len(results), "ok": sum(result["ok"] for result in results), "results": results})


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=Path, default=REPO_ROOT / "data/after_effects_synthetic_cases.jsonl")
    parser.add_argument("--queue", type=Path, default=REPO_ROOT / "artifacts/visual_analysis/render-review-queue.json")
    parser.add_argument("--aerender", default="/Applications/Adobe After Effects 2026/aerender")
    parser.add_argument("--decisions", nargs="+", default=sorted(DEFAULT_DECISIONS))
    parser.add_argument("--status-report", type=Path)
    parser.add_argument("--statuses", nargs="+", default=["project_ready", "render_stale"])
    parser.add_argument("--force", action="store_true")
    return parser.parse_args()


def _load_records(path: Path) -> dict[str, dict[str, Any]]:
    records = {}
    for line in path.read_text().splitlines():
        if line.strip():
            record = json.loads(line)
            records[record["case_id"]] = record
    return records


def _case_ids_from_status(path: Path, statuses: set[str]) -> set[str]:
    report = json.loads(path.read_text())
    return {
        case["case_id"]
        for case in report.get("cases", [])
        if case.get("status") in statuses
    }


def _render_case(record: dict[str, Any], aerender: str, force: bool) -> dict[str, Any]:
    case_id = record["case_id"]
    case_dir = REPO_ROOT / "artifacts/ae_live_checks" / case_id
    source_path = REPO_ROOT / record["source_repo_path"]
    project_path = case_dir / "project.aep"
    output_path = case_dir / "render.mp4"
    tmp_output_path = case_dir / "render.next.mp4"
    log_path = case_dir / "aerender.log"
    if not project_path.exists():
        return {"case_id": case_id, "ok": False, "reason": "missing_project"}
    if not force and project_path.stat().st_mtime < source_path.stat().st_mtime:
        return {"case_id": case_id, "ok": False, "reason": "stale_project"}
    if tmp_output_path.exists():
        tmp_output_path.unlink()
    command = [
        aerender,
        "-project",
        str(project_path),
        "-comp",
        record["expected"]["comp_name"],
        "-output",
        str(tmp_output_path),
    ]
    result = subprocess.run(command, capture_output=True, check=False, timeout=900)
    log = _decode(result.stdout) + _decode(result.stderr)
    log_path.write_text(log)
    ok = result.returncode == 0 and tmp_output_path.exists()
    if ok:
        tmp_output_path.replace(output_path)
    return {
        "case_id": case_id,
        "ok": ok,
        "returncode": result.returncode,
        "reason": "rendered" if ok else "aerender_failed",
    }


def _decode(payload: bytes | None) -> str:
    return (payload or b"").decode("utf-8", "replace")


if __name__ == "__main__":
    main()
