from __future__ import annotations

import argparse
from pathlib import Path

from after_effects_pipeline.ae_preferences import (
    inspect_scripting_access,
    render_scripting_access_markdown,
)
from after_effects_pipeline.utils import write_json

REPO_ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    args = _parse_args()
    report = inspect_scripting_access()
    write_json(args.output, report)
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.write_text(render_scripting_access_markdown(report))
    print(
        {
            "ok": report["ok"],
            "active_version": report["active_version"],
            "javascript_debugger": report["javascript_debugger"],
            "script_file_network_access": report["script_file_network_access"],
        }
    )


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=REPO_ROOT / "artifacts/ae_live_checks/scripting-access.json")
    parser.add_argument("--markdown-output", type=Path, default=REPO_ROOT / "artifacts/ae_live_checks/scripting-access.md")
    return parser.parse_args()


if __name__ == "__main__":
    main()
