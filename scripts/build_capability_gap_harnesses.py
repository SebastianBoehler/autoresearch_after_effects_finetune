from __future__ import annotations

import argparse
import json
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
harnesses = None


def main() -> None:
    global harnesses
    harnesses = harnesses or _load_harnesses()
    args = _parse_args()
    records = harnesses._load_jsonl(args.dataset)
    capability = json.loads(args.capability_audit.read_text())
    queue = json.loads(args.queue.read_text())
    targets = _select_targets(records, capability, queue, set(args.decisions))
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    harnesses._clear_old_scripts(output_dir)
    written = harnesses._write_batches(targets, output_dir, args.max_lines)
    runner = harnesses._write_runner(written, output_dir)
    _write_index(written, runner, targets, capability, output_dir)
    print({
        "target_count": len(targets),
        "script_count": len(written),
        "runner": str(runner),
        "output_dir": str(output_dir),
    })


def _parse_args() -> argparse.Namespace:
    global harnesses
    harnesses = harnesses or _load_harnesses()
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=Path, default=REPO_ROOT / "data/after_effects_synthetic_cases.jsonl")
    parser.add_argument("--queue", type=Path, default=REPO_ROOT / "artifacts/visual_analysis/render-review-queue.json")
    parser.add_argument("--capability-audit", type=Path, default=REPO_ROOT / "artifacts/visual_analysis/source-capability-audit.json")
    parser.add_argument("--output-dir", type=Path, default=REPO_ROOT / "artifacts/ae_live_checks/_manual_harnesses_capability_gaps")
    parser.add_argument("--decisions", nargs="+", default=sorted(harnesses.DEFAULT_DECISIONS))
    parser.add_argument("--max-lines", type=int, default=280)
    return parser.parse_args()


def _load_harnesses():
    path = REPO_ROOT / "scripts/build_ae_manual_harnesses.py"
    spec = spec_from_file_location("build_ae_manual_harnesses", path)
    module = module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def _select_targets(
    records: list[dict[str, Any]],
    capability: dict[str, Any],
    queue: dict[str, Any],
    decisions: set[str],
) -> list[dict[str, Any]]:
    records_by_id = {record["case_id"]: record for record in records}
    queue_by_id = {item["case_id"]: item for item in queue.get("items", [])}
    selected = []
    seen = set()
    for unlock in capability.get("train_ready_gap_unlocks", []):
        for case_id in unlock.get("case_ids", []):
            decision = queue_by_id.get(case_id, {}).get("decision")
            if case_id not in seen and case_id in records_by_id and decision in decisions:
                seen.add(case_id)
                selected.append(records_by_id[case_id])
                break
    return selected


def _write_index(
    written: list[Path],
    runner: Path,
    targets: list[dict[str, Any]],
    capability: dict[str, Any],
    output_dir: Path,
) -> None:
    gap_count = capability.get("summary", {}).get("train_ready_core_gap_count", 0)
    lines = [
        "# Manual AE Capability-Gap Harnesses",
        "",
        "Run this runner from After Effects via File > Scripts > Run Script File:",
        "",
        f"- {runner}",
        "",
        f"Targets are first-unlock cases for {gap_count} missing train-ready AE capability gap(s).",
        "Save or close unrelated AE work first; each harness closes the active project.",
        "",
        "## Chunks",
        "",
    ]
    lines.extend(f"- {path}" for path in written)
    lines.extend(["", "## Targets", ""])
    lines.extend(f"- {record['case_id']}" for record in targets)
    (output_dir / "README.md").write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
