from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from after_effects_pipeline.static_check import extract_code

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DECISIONS = {"render_missing", "rerender_stale", "fix_render"}


def main() -> None:
    args = _parse_args()
    records = _load_jsonl(args.dataset)
    queue = json.loads(args.queue.read_text())
    readiness = _load_optional_json(args.readiness_report)
    targets = _select_targets(records, queue, set(args.decisions), readiness, args.limit)
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    _clear_old_scripts(output_dir)
    written = _write_batches(targets, output_dir, args.max_lines)
    runner = _write_runner(written, output_dir)
    _write_index(written, runner, targets, output_dir, readiness)
    print({
        "target_count": len(targets),
        "script_count": len(written),
        "runner": str(runner),
        "output_dir": str(output_dir),
    })


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=Path, default=REPO_ROOT / "data/after_effects_synthetic_cases.jsonl")
    parser.add_argument("--queue", type=Path, default=REPO_ROOT / "artifacts/visual_analysis/render-review-queue.json")
    parser.add_argument("--readiness-report", type=Path, default=REPO_ROOT / "artifacts/datasets/after-effects-train-ready/readiness-report.json")
    parser.add_argument("--output-dir", type=Path, default=REPO_ROOT / "artifacts/ae_live_checks/_manual_harnesses")
    parser.add_argument("--decisions", nargs="+", default=sorted(DEFAULT_DECISIONS))
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--max-lines", type=int, default=280)
    return parser.parse_args()


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def _load_optional_json(path: Path) -> dict[str, Any] | None:
    return json.loads(path.read_text()) if path.exists() else None


def _select_targets(
    records: list[dict[str, Any]],
    queue: dict[str, Any],
    decisions: set[str],
    readiness: dict[str, Any] | None,
    limit: int,
) -> list[dict[str, Any]]:
    records_by_id = {record["case_id"]: record for record in records}
    decision_by_id = {
        item["case_id"]: item.get("decision")
        for item in queue.get("items", [])
    }
    case_ids = _priority_case_ids(readiness, queue)
    selected = [
        records_by_id[case_id]
        for case_id in case_ids
        if decision_by_id.get(case_id) in decisions and case_id in records_by_id
    ]
    return selected[:limit] if limit > 0 else selected


def _priority_case_ids(
    readiness: dict[str, Any] | None,
    queue: dict[str, Any],
) -> list[str]:
    if readiness:
        debt_ids = [item["case_id"] for item in readiness.get("render_debt", [])]
        if debt_ids:
            return debt_ids
    return [item["case_id"] for item in queue.get("items", [])]


def _write_batches(
    targets: list[dict[str, Any]],
    output_dir: Path,
    max_lines: int,
) -> list[Path]:
    written: list[Path] = []
    batch: list[dict[str, Any]] = []
    for target in targets:
        candidate = [*batch, target]
        if batch and _line_count(_build_script(candidate)) > max_lines:
            written.append(_write_script(batch, output_dir, len(written) + 1))
            batch = [target]
        else:
            batch = candidate
    if batch:
        written.append(_write_script(batch, output_dir, len(written) + 1))
    return written


def _write_script(batch: list[dict[str, Any]], output_dir: Path, index: int) -> Path:
    path = output_dir / f"manual_harness_{index:02d}.jsx"
    path.write_text(_build_script(batch))
    return path


def _clear_old_scripts(output_dir: Path) -> None:
    for path in output_dir.glob("manual_harness_*.jsx"):
        path.unlink()
    runner = output_dir / "run_all_harnesses.jsx"
    if runner.exists():
        runner.unlink()
    report = output_dir / "runner_report.txt"
    if report.exists():
        report.unlink()


def _build_script(batch: list[dict[str, Any]]) -> str:
    body = "\n".join(_case_block(record) for record in batch)
    return f"""
(function () {{
    var summary = [];
    if (!$.global.AEFT_SKIP_CONFIRM && !confirm("Save your current After Effects project first. This script closes the active project while creating {len(batch)} generated project file(s). Continue?")) {{
        return;
    }}

    function ensureFolder(path) {{
        var folder = new Folder(path);
        if (!folder.exists) folder.create();
    }}

    function writeReport(path, fields) {{
        var file = new File(path);
        file.encoding = "UTF-8";
        file.open("w");
        for (var key in fields) file.writeln(key + "=" + String(fields[key]));
        file.close();
    }}

    function findCompByName(name) {{
        for (var i = 1; i <= app.project.numItems; i++) {{
            var item = app.project.item(i);
            if (item instanceof CompItem && item.name === name) return item;
        }}
        return null;
    }}

    function firstComp() {{
        for (var i = 1; i <= app.project.numItems; i++) {{
            var item = app.project.item(i);
            if (item instanceof CompItem) return item;
        }}
        return null;
    }}

    function resetProject() {{
        if (app.project) app.project.close(CloseOptions.DO_NOT_SAVE_CHANGES);
        app.newProject();
    }}
{body}
    if (!$.global.AEFT_SKIP_ALERT) alert("Manual AE harness complete: " + summary.join(", "));
}})();
""".strip() + "\n"


def _write_runner(written: list[Path], output_dir: Path) -> Path:
    path = output_dir / "run_all_harnesses.jsx"
    report = output_dir / "runner_report.txt"
    scripts = ",\n".join(f"        {_js(str(script))}" for script in written)
    path.write_text(f"""
(function () {{
    var scripts = [
{scripts}
    ];
    var reportPath = {_js(str(report))};
    function writeLines(lines) {{
        var file = new File(reportPath);
        file.encoding = "UTF-8";
        file.open("w");
        for (var i = 0; i < lines.length; i++) file.writeln(lines[i]);
        file.close();
    }}
    if (!$.global.AEFT_SKIP_CONFIRM && !confirm("Save your current After Effects project first. This runs " + scripts.length + " harness chunk(s) and closes the active project repeatedly. Continue?")) {{
        return;
    }}
    $.global.AEFT_SKIP_CONFIRM = true;
    $.global.AEFT_SKIP_ALERT = true;
    var completed = [];
    for (var i = 0; i < scripts.length; i++) {{
        try {{
            $.evalFile(new File(scripts[i]));
            completed.push("ok:" + scripts[i]);
        }} catch (e) {{
            completed.push("error:" + scripts[i] + ":" + e.toString());
        }}
        writeLines(completed);
    }}
    $.global.AEFT_SKIP_CONFIRM = false;
    $.global.AEFT_SKIP_ALERT = false;
    writeLines(completed);
    if (!$.global.AEFT_SKIP_ALERT) alert("Manual AE harness runner complete. Chunks: " + completed.length);
}})();
""".strip() + "\n")
    return path


def _case_block(record: dict[str, Any]) -> str:
    case_id = record["case_id"]
    case_dir = REPO_ROOT / "artifacts/ae_live_checks" / case_id
    code = _indent(extract_code(record["completion"]), "        ")
    comp_name = record.get("expected", {}).get("comp_name", "")
    asset_root = REPO_ROOT / "data" / "synthetic" / "assets"
    return f"""
    try {{
        resetProject();
        ensureFolder({_js(str(case_dir))});
        $.global.AEFT_ASSET_ROOT = {_js(str(asset_root))};
{code}
        var comp = findCompByName({_js(comp_name)}) || firstComp();
        app.project.save(new File({_js(str(case_dir / "project.aep"))}));
        writeReport({_js(str(case_dir / "report.txt"))}, {{
            ok: comp !== null,
            compFound: comp !== null,
            compName: comp !== null ? comp.name : "",
            width: comp !== null ? comp.width : 0,
            height: comp !== null ? comp.height : 0,
            duration: comp !== null ? comp.duration : 0,
            frameRate: comp !== null ? comp.frameRate : 0,
            numLayers: comp !== null ? comp.numLayers : 0
        }});
        summary.push({_js(case_id + "=ok")});
    }} catch (e) {{
        writeReport({_js(str(case_dir / "report.txt"))}, {{ ok: false, error: e.toString(), line: e.line || "" }});
        summary.push({_js(case_id + "=error")});
    }}
"""


def _write_index(
    written: list[Path],
    runner: Path,
    targets: list[dict[str, Any]],
    output_dir: Path,
    readiness: dict[str, Any] | None,
) -> None:
    order_note = (
        "Targets are ordered by training-readiness render-debt priority."
        if readiness
        else "Targets are ordered by render-review queue order."
    )
    lines = [
        "# Manual AE Harnesses",
        "",
        "Run the all-in-one runner from After Effects via File > Scripts > Run Script File:",
        "",
        f"- {runner}",
        "",
        "The runner executes every chunk below with one confirmation.",
        "Save or close unrelated AE work first; each harness closes the active project.",
        order_note,
        "",
        "## Chunks",
        "",
    ]
    for path in written:
        lines.append(f"- {path}")
    lines.extend(["", "## Targets", ""])
    for record in targets:
        lines.append(f"- {record['case_id']}")
    (output_dir / "README.md").write_text("\n".join(lines) + "\n")


def _indent(text: str, prefix: str) -> str:
    return "\n".join(prefix + line if line else line for line in text.splitlines())


def _line_count(text: str) -> int:
    return len(text.splitlines())


def _js(value: str) -> str:
    return json.dumps(value)


if __name__ == "__main__":
    main()
