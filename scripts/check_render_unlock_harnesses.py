from __future__ import annotations

import argparse
import json
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DECISIONS = {"render_missing", "rerender_stale", "fix_render"}


def main() -> None:
    args = _parse_args()
    status = _load_status_module()
    records = status._load_jsonl(args.dataset)
    queue = json.loads(args.queue.read_text())
    plan = json.loads(args.plan.read_text())
    report = status._build_report(
        records=records,
        queue=queue,
        readiness=_readiness(_target_case_ids(plan)),
        decisions=set(args.decisions),
        harness_dir=args.harness_dir,
        dataset_path=args.dataset,
    )
    _write_compact_json(args.output, report)
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.write_text(_markdown(status, report))
    print(report["summary"])


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=Path, default=REPO_ROOT / "data/after_effects_synthetic_cases.jsonl")
    parser.add_argument("--queue", type=Path, default=REPO_ROOT / "artifacts/visual_analysis/render-review-queue.json")
    parser.add_argument("--plan", type=Path, default=REPO_ROOT / "artifacts/visual_analysis/render-unlock-plan.json")
    parser.add_argument("--harness-dir", type=Path, default=REPO_ROOT / "artifacts/ae_live_checks/_manual_harnesses_render_unlocks")
    parser.add_argument("--output", type=Path, default=REPO_ROOT / "artifacts/ae_live_checks/_manual_harnesses_render_unlocks/status.json")
    parser.add_argument("--markdown-output", type=Path, default=REPO_ROOT / "artifacts/ae_live_checks/_manual_harnesses_render_unlocks/status.md")
    parser.add_argument("--decisions", nargs="+", default=sorted(DEFAULT_DECISIONS))
    return parser.parse_args()


def _target_case_ids(plan: dict[str, Any]) -> list[str]:
    case_ids = []
    seen = set()
    for target in plan.get("greedy_unlock_sequence", []):
        case_id = target.get("case_id")
        if case_id and case_id not in seen:
            seen.add(case_id)
            case_ids.append(case_id)
    return case_ids


def _write_compact_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, sort_keys=True) + "\n")


def _readiness(case_ids: list[str]) -> dict[str, list[dict[str, str]]]:
    return {"render_debt": [{"case_id": case_id} for case_id in case_ids]}


def _markdown(status_module: Any, report: dict[str, Any]) -> str:
    return status_module._markdown(report).replace(
        "# Manual AE Harness Status",
        "# Manual AE Render-Unlock Harness Status",
        1,
    )


def _load_status_module() -> Any:
    path = REPO_ROOT / "scripts/check_ae_manual_harnesses.py"
    spec = spec_from_file_location("check_ae_manual_harnesses", path)
    module = module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


if __name__ == "__main__":
    main()
