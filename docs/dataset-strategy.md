# Dataset Strategy

The canonical dataset should be owned, small, and aggressively verified before
it grows.

## Sources

Use first-party generated samples first:

- source templates under `data/synthetic/templates/`
- metadata in `data/synthetic/manifest.json`
- canonical JSONL from `scripts/build_synthetic_dataset.py`
- manually reviewed model generations only after static or live verification

Avoid copying Adobe documentation into completions. The After Effects scripting
guide is useful reference material, but its own README marks the content as
Adobe-copyrighted educational material.

## Promotion Rules

A row is promotable when:

- it has explicit license/provenance metadata
- static syntax and AE contract checks pass
- required snippets are present
- forbidden snippets are absent
- live AE execution passes when available
- manual review marks it as useful and visually coherent

## HF Export

`export-hf-dataset` writes:

- `cases.jsonl`: canonical rows
- `chat.jsonl`: all rows as chat records
- `train.jsonl`, `valid.jsonl`, `test.jsonl`: MLX-ready splits
- `README.md`: dataset card with provenance notes

