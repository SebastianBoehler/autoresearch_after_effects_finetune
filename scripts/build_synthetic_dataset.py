from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = REPO_ROOT / "data" / "synthetic" / "manifest.json"
OUTPUT_PATH = REPO_ROOT / "data" / "after_effects_synthetic_cases.jsonl"

SYSTEM_PROMPT = (
    "You write complete Adobe After Effects ExtendScript JSX scripts. Return "
    "only code. Create a named composition, use app.beginUndoGroup and "
    "app.endUndoGroup, avoid external assets, and keep scripts compact."
)


def main() -> None:
    manifest = json.loads(MANIFEST_PATH.read_text())
    records = []
    for item in manifest["cases"]:
        template_path = MANIFEST_PATH.parent / "templates" / item["template"]
        completion = template_path.read_text().strip() + "\n"
        records.append(
            {
                **item,
                "system": SYSTEM_PROMPT,
                "completion": completion,
                "license": "MIT",
                "source_name": "autoresearch-after-effects-synthetic-v1",
                "source_model": "codex-authored",
                "source_rating": "seed",
                "source_repo_path": str(template_path.relative_to(REPO_ROOT)),
                "synthetic_generation_method": "first-party JSX template",
                "inspiration_sources": [
                    "After Effects scripting DOM principles",
                    "After Effects shape layer match names",
                    "After Effects expression basics",
                ],
            }
        )

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_PATH.open("w") as handle:
        for record in records:
            handle.write(json.dumps(record, sort_keys=True) + "\n")
    print(f"wrote {len(records)} cases to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()

