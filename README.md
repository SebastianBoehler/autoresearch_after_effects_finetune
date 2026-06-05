# autoresearch_after_effects_finetune

Mac-friendly autoresearch scaffold for fine-tuning small coding models on
**After Effects ExtendScript / JSX project generation**.

The first target is narrow on purpose:

- one complete `.jsx` script per sample
- scripts create a named, renderable composition
- dataset rows carry license and provenance metadata
- static verification runs by default
- live After Effects execution is opt-in with `--live`
- Hugging Face export writes both canonical cases and train-ready chat splits
- MLX LoRA commands are wired for Apple Silicon fine-tuning

## Model Starting Point

The default train config uses:

```text
LiquidAI/LFM2.5-8B-A1B-MLX-8bit
```

This is deliberately not Qwen2.5. It is a newer LiquidAI MLX model that is
small enough to try locally before we decide whether a Qwen3.5/Qwen3-Coder
variant is worth the heavier runtime. Model trade-offs are documented in
[`docs/model-selection.md`](docs/model-selection.md).

## Setup

```bash
uv sync
```

## Quick Start

Build the owned synthetic dataset from source templates:

```bash
uv run python scripts/build_synthetic_dataset.py
```

Build MLX train/valid/test chat splits:

```bash
uv run python -m after_effects_pipeline.cli build-dataset \
  --config configs/lfm25_8b_a1b_after_effects.json
```

Run static source verification:

```bash
uv run python -m after_effects_pipeline.cli verify-source \
  --config configs/lfm25_8b_a1b_after_effects.json
```

Export a Hugging Face-ready dataset folder:

```bash
uv run python -m after_effects_pipeline.cli export-hf-dataset \
  --config configs/lfm25_8b_a1b_after_effects.json \
  --output-dir artifacts/hf_datasets/autoresearch-after-effects \
  --repo-id sebastianboehler/autoresearch-after-effects
```

Run MLX LoRA training when the dataset/eval loop is ready:

```bash
uv run python -m after_effects_pipeline.cli train \
  --config configs/lfm25_8b_a1b_after_effects.json
```

## Live After Effects Verification

Static checks are safe and run without launching Adobe apps. Live verification
is available when you want real AE execution:

```bash
uv run python -m after_effects_pipeline.cli verify-source \
  --config configs/lfm25_8b_a1b_after_effects.json \
  --live
```

Use a clean After Effects session for live checks. The verifier writes a
temporary harness under `artifacts/ae_live_checks/`, executes it through
AppleScript, inspects the created composition, and saves a `.aep` project for
manual review.

## Dataset Contract

Rows live in `data/after_effects_synthetic_cases.jsonl` and use this shape:

- `case_id`
- `system`
- `prompt`
- `completion`
- `tags`
- `must_contain`
- `must_not_contain`
- `expected`
- `license`
- `source_name`
- `source_model`
- `source_rating`
- `source_repo_path`

The default policy is provenance-first. Do not train on copied Adobe docs or
unlicensed public snippets just because they compile.

## License

MIT. See [LICENSE](LICENSE).
