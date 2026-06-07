from __future__ import annotations

import argparse
import json
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from typing import Any

from after_effects_pipeline.static_check import extract_code

REPO_ROOT = Path(__file__).resolve().parents[1]
harnesses = None


def main() -> None:
    global harnesses
    harnesses = harnesses or _load_harnesses()
    args = _parse_args()
    records = harnesses._load_jsonl(args.dataset)
    inspiration = json.loads(args.inspiration_coverage.read_text())
    targets = _select_targets(records, inspiration, args.limit)
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    _clear_old_scripts(output_dir)
    written = _write_batches(targets, output_dir, args.max_lines)
    _write_index(written, targets, inspiration, output_dir)
    print({
        "target_count": len(targets),
        "script_count": len(written),
        "output_dir": str(output_dir),
    })


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=Path, default=REPO_ROOT / "data/after_effects_synthetic_cases.jsonl")
    parser.add_argument("--inspiration-coverage", type=Path, default=REPO_ROOT / "artifacts/visual_analysis/inspiration-coverage.json")
    parser.add_argument("--output-dir", type=Path, default=REPO_ROOT / "artifacts/ae_live_checks/_play_session_harnesses")
    parser.add_argument("--limit", type=int, default=0)
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
    inspiration: dict[str, Any],
    limit: int,
) -> list[dict[str, Any]]:
    records_by_id = {record["case_id"]: record for record in records}
    selected = []
    seen = set()
    for gap in inspiration.get("train_ready_gaps", []):
        case_id = gap.get("first_unlock_case")
        if case_id and case_id not in seen and case_id in records_by_id:
            seen.add(case_id)
            selected.append(records_by_id[case_id])
    return selected[:limit] if limit > 0 else selected


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
    path = output_dir / f"play_review_{index:02d}.jsx"
    path.write_text(_build_script(batch))
    return path


def _clear_old_scripts(output_dir: Path) -> None:
    for path in output_dir.glob("play_review_*.jsx"):
        path.unlink()
    for name in ["status.json", "status.md"]:
        path = output_dir / name
        if path.exists():
            path.unlink()


def _build_script(batch: list[dict[str, Any]]) -> str:
    body = "\n".join(_case_block(record) for record in batch)
    return f"""
(function () {{
    var created = [];
    var errors = [];
    if (!$.global.AEFT_SKIP_CONFIRM && !confirm("This creates {len(batch)} AEFT review comp(s) in the current project without saving files. Continue?")) {{
        return;
    }}

    function findNewestCompByName(name) {{
        for (var i = app.project.numItems; i >= 1; i--) {{
            var item = app.project.item(i);
            if (item instanceof CompItem && item.name === name) return item;
        }}
        return null;
    }}

    function removeCompsByName(name) {{
        if (!name) return;
        for (var i = app.project.numItems; i >= 1; i--) {{
            var item = app.project.item(i);
            if (item instanceof CompItem && item.name === name) item.remove();
        }}
    }}

    function addIndexComp() {{
        var index = app.project.items.addComp("AEFT Play Review Index", 1920, 1080, 1, 8, 30);
        index.bgColor = [0.02, 0.022, 0.028];
        var title = index.layers.addText("PLAY REVIEW");
        title.property("Transform").property("Position").setValue([120, 130]);
        var doc = title.property("Source Text").value;
        doc.fontSize = 54;
        doc.fillColor = [0.92, 0.96, 1];
        title.property("Source Text").setValue(doc);
        for (var j = 0; j < created.length; j++) {{
            var line = index.layers.addText((j + 1) + ". " + created[j]);
            line.property("Transform").property("Position").setValue([130, 230 + j * 54]);
            var lineDoc = line.property("Source Text").value;
            lineDoc.fontSize = 28;
            lineDoc.fillColor = [0.62, 0.85, 1];
            line.property("Source Text").setValue(lineDoc);
        }}
    }}
{body}
    addIndexComp();
    if (errors.length > 0 && $.global.AEFT_THROW_ON_ERRORS) {{
        throw new Error(errors.join(" | "));
    }}
    if (!$.global.AEFT_SKIP_ALERT) alert("Play review created " + created.length + " comp(s). Errors: " + errors.length);
}})();
""".strip() + "\n"


def _case_block(record: dict[str, Any]) -> str:
    case_id = record["case_id"]
    code = _indent(extract_code(record["completion"]), "        ")
    comp_name = record.get("expected", {}).get("comp_name", "")
    return f"""
    try {{
        removeCompsByName({_js(comp_name)});
{code}
        var comp = findNewestCompByName({_js(comp_name)});
        if (comp !== null) {{
            comp.openInViewer();
            created.push({_js(case_id)} + " / " + comp.name + " / " + comp.numLayers + " layers");
        }} else {{
            errors.push({_js(case_id)} + ": comp not found");
        }}
    }} catch (e) {{
        errors.push({_js(case_id)} + ": " + e.toString() + " line " + (e.line || ""));
    }}
"""


def _write_index(
    written: list[Path],
    targets: list[dict[str, Any]],
    inspiration: dict[str, Any],
    output_dir: Path,
) -> None:
    gap_count = inspiration.get("summary", {}).get("train_ready_gap_count", 0)
    lines = [
        "# AE Play Session Harnesses",
        "",
        "Run these from After Effects via File > Scripts > Run Script File.",
        "They create playable review comps in the current project only.",
        "They do not save project files, write reports, or render movies.",
        "",
        f"Targets are first-unlock cases for {gap_count} web-inspired train-ready motif gap(s).",
        "",
        "## Chunks",
        "",
    ]
    lines.extend(f"- {path}" for path in written)
    lines.extend(["", "## Targets", ""])
    lines.extend(f"- {record['case_id']}" for record in targets)
    (output_dir / "README.md").write_text("\n".join(lines) + "\n")


def _indent(text: str, prefix: str) -> str:
    return "\n".join(prefix + line if line else line for line in text.splitlines())


def _line_count(text: str) -> int:
    return len(text.splitlines())


def _js(value: str) -> str:
    return json.dumps(value)


if __name__ == "__main__":
    main()
