from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from after_effects_pipeline.utils import write_json

REPO_ROOT = Path(__file__).resolve().parents[1]
REVIEW_DECISIONS = {"fix_render", "manual_review_render", "watch_quality"}
DECISION_ORDER = {"fix_render": 0, "manual_review_render": 1, "watch_quality": 2}


def main() -> None:
    args = _parse_args()
    template = _build_template(_load_json(args.queue))
    write_json(args.output, template)
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.write_text(_markdown(template))
    print(template["summary"])


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--queue", type=Path, default=REPO_ROOT / "artifacts/visual_analysis/render-review-queue.json")
    parser.add_argument("--output", type=Path, default=REPO_ROOT / "artifacts/visual_analysis/manual-review-decisions.template.json")
    parser.add_argument("--markdown-output", type=Path, default=REPO_ROOT / "artifacts/visual_analysis/manual-review-decisions.template.md")
    return parser.parse_args()


def _build_template(queue: dict[str, Any]) -> dict[str, Any]:
    cases = [_template_case(item) for item in queue.get("items", []) if _needs_manual_decision(item)]
    cases.sort(key=lambda item: (DECISION_ORDER[item["current_decision"]], item["quality_score"], item["case_id"]))
    return {
        "summary": {
            "case_count": len(cases),
            "allowed_decisions": ["promote", "fix", "watch"],
        },
        "instructions": (
            "Copy this file to manual-review-decisions.json and replace pending "
            "with promote, fix, or watch after inspecting the contact sheet/render."
        ),
        "cases": cases,
    }


def _needs_manual_decision(item: dict[str, Any]) -> bool:
    return (
        item.get("decision") in REVIEW_DECISIONS
        and bool(item.get("render_path"))
        and bool(item.get("contact_sheet_path"))
    )


def _template_case(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "case_id": item["case_id"],
        "decision": "pending",
        "suggested_decision": _suggestion(item),
        "note": "",
        "current_decision": item.get("decision", ""),
        "quality_score": round(float(item.get("quality_score") or 0.0), 3),
        "warnings": item.get("warnings", []),
        "reasons": item.get("reasons", []),
        "contact_sheet_path": item.get("contact_sheet_path", ""),
        "render_path": item.get("render_path", ""),
    }


def _suggestion(item: dict[str, Any]) -> str:
    if item.get("decision") == "fix_render":
        return "fix"
    if item.get("decision") == "watch_quality":
        return "watch"
    return "promote_if_visual_intentional_else_fix"


def _markdown(template: dict[str, Any]) -> str:
    lines = [
        "# Manual Review Decisions Template",
        "",
        template["instructions"],
        "",
        f"- cases: {template['summary']['case_count']}",
        f"- allowed decisions: {', '.join(template['summary']['allowed_decisions'])}",
        "",
        "| case | current | suggested | quality | warnings | reasons | sheet |",
        "| --- | --- | --- | ---: | --- | --- | --- |",
    ]
    for item in template["cases"]:
        lines.append(
            f"| {item['case_id']} | {item['current_decision']} | {item['suggested_decision']} | "
            f"{item['quality_score']:.3f} | {', '.join(item['warnings']) or '-'} | "
            f"{', '.join(item['reasons']) or '-'} | {_sheet_link(item['contact_sheet_path'])} |"
        )
    if not template["cases"]:
        lines.append("| - | - | - | - | - | - | - |")
    return "\n".join(lines) + "\n"


def _sheet_link(path: str) -> str:
    return "-" if not path else f"[open](contact_sheets/{Path(path).name})"


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text()) if path.exists() else {}


if __name__ == "__main__":
    main()
