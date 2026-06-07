from __future__ import annotations

import argparse
import json
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from typing import Any

from after_effects_pipeline.utils import write_json

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DECISIONS = {"render_missing", "rerender_stale", "fix_render"}


def main() -> None:
    args = _parse_args()
    status = _load_status_module()
    records = status._load_jsonl(args.dataset)
    queue = json.loads(args.queue.read_text())
    capability = json.loads(args.capability_audit.read_text())
    report = status._build_report(
        records=records,
        queue=queue,
        readiness=_readiness(_target_case_ids(capability)),
        decisions=set(args.decisions),
        harness_dir=args.harness_dir,
        dataset_path=args.dataset,
    )
    write_json(args.output, report)
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.write_text(_markdown(status, report))
    print(report["summary"])


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=Path, default=REPO_ROOT / "data/after_effects_synthetic_cases.jsonl")
    parser.add_argument("--queue", type=Path, default=REPO_ROOT / "artifacts/visual_analysis/render-review-queue.json")
    parser.add_argument("--capability-audit", type=Path, default=REPO_ROOT / "artifacts/visual_analysis/source-capability-audit.json")
    parser.add_argument("--harness-dir", type=Path, default=REPO_ROOT / "artifacts/ae_live_checks/_manual_harnesses_capability_gaps")
    parser.add_argument("--output", type=Path, default=REPO_ROOT / "artifacts/ae_live_checks/_manual_harnesses_capability_gaps/status.json")
    parser.add_argument("--markdown-output", type=Path, default=REPO_ROOT / "artifacts/ae_live_checks/_manual_harnesses_capability_gaps/status.md")
    parser.add_argument("--decisions", nargs="+", default=sorted(DEFAULT_DECISIONS))
    return parser.parse_args()


def _target_case_ids(capability: dict[str, Any]) -> list[str]:
    case_ids = []
    seen = set()
    for unlock in capability.get("train_ready_gap_unlocks", []):
        for case_id in unlock.get("case_ids", []):
            if case_id and case_id not in seen:
                seen.add(case_id)
                case_ids.append(case_id)
                break
    return case_ids


def _readiness(case_ids: list[str]) -> dict[str, list[dict[str, str]]]:
    return {"render_debt": [{"case_id": case_id} for case_id in case_ids]}


def _markdown(status_module: Any, report: dict[str, Any]) -> str:
    return status_module._markdown(report).replace(
        "# Manual AE Harness Status",
        "# Manual AE Capability-Gap Harness Status",
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
