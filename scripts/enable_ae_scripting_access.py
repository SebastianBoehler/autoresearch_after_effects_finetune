from __future__ import annotations

import argparse
from pathlib import Path

from after_effects_pipeline.ae_preferences import (
    enable_scripting_access_preference,
    render_enable_scripting_access_markdown,
)
from after_effects_pipeline.utils import write_json

REPO_ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    args = _parse_args()
    report = enable_scripting_access_preference(apply=args.apply)
    write_json(args.output, report)
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.write_text(render_enable_scripting_access_markdown(report))
    print(
        {
            "ok": report["ok"],
            "applied": report["applied"],
            "would_apply": report["would_apply"],
            "after_effects_running": report["after_effects_running"],
            "active_version": report["active_version"],
            "before": report["before"],
            "after": report["after"],
        }
    )
    if args.apply and not report["ok"]:
        raise SystemExit(1)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--output", type=Path, default=REPO_ROOT / "artifacts/ae_live_checks/enable-scripting-access.json")
    parser.add_argument("--markdown-output", type=Path, default=REPO_ROOT / "artifacts/ae_live_checks/enable-scripting-access.md")
    return parser.parse_args()


if __name__ == "__main__":
    main()
