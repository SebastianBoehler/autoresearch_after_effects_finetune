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

EASING_NORMALIZER = """
    function aeFtEaseProperty(prop, influence) {
        if (!prop || !prop.numKeys || prop.numKeys < 2 || !prop.setTemporalEaseAtKey) return;
        for (var k = 1; k <= prop.numKeys; k++) {
            try {
                var dims = prop.value instanceof Array ? prop.value.length : 1;
                var easeIn = [];
                var easeOut = [];
                for (var d = 0; d < dims; d++) {
                    easeIn.push(new KeyframeEase(0, influence));
                    easeOut.push(new KeyframeEase(0, influence));
                }
                prop.setTemporalEaseAtKey(k, easeIn, easeOut);
            } catch (e) {}
        }
    }
    function aeFtEaseGroup(group, influence) {
        if (!group || !group.numProperties) return;
        for (var i = 1; i <= group.numProperties; i++) {
            var prop = group.property(i);
            aeFtEaseProperty(prop, influence);
            aeFtEaseGroup(prop, influence);
        }
    }
    function aeFtEaseComp(comp, influence) {
        for (var i = 1; i <= comp.numLayers; i++) aeFtEaseGroup(comp.layer(i), influence);
    }
""".strip("\n")


def main() -> None:
    cases = _load_manifest_cases(MANIFEST_PATH)
    records = []
    for item in cases:
        template_path = MANIFEST_PATH.parent / "templates" / item["template"]
        completion = _with_easing_normalizer(template_path.read_text().strip()) + "\n"
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
                "inspiration_sources": item.get("inspiration_sources", [
                    "After Effects scripting DOM principles",
                    "After Effects shape layer match names",
                    "After Effects expression basics",
                ]),
            }
        )

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_PATH.open("w") as handle:
        for record in records:
            handle.write(json.dumps(record, sort_keys=True) + "\n")
    print(f"wrote {len(records)} cases to {OUTPUT_PATH}")


def _load_manifest_cases(path: Path) -> list[dict]:
    manifest = json.loads(path.read_text())
    if "cases" in manifest:
        return manifest["cases"]
    cases = []
    for include in manifest.get("includes", []):
        include_path = path.parent / include
        cases.extend(_load_manifest_cases(include_path))
    return cases


def _with_easing_normalizer(completion: str) -> str:
    marker = "    app.endUndoGroup();"
    if "setValueAtTime" not in completion or "setTemporalEaseAtKey" in completion:
        return completion
    if marker not in completion:
        return completion
    injection = f"{EASING_NORMALIZER}\n    aeFtEaseComp(comp, 72);\n{marker}"
    return completion.replace(marker, injection, 1)


if __name__ == "__main__":
    main()
