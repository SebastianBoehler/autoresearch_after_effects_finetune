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

Render MP4s and inspect every third frame for motion, foreground density,
blank frames, contrast, color variety, and overlap-style warnings:

```bash
uv run python -m after_effects_pipeline.cli verify-source \
  --config configs/lfm25_8b_a1b_after_effects.json \
  --live --render

uv run python -m after_effects_pipeline.cli analyze-renders \
  --config configs/lfm25_8b_a1b_after_effects.json

uv run python -m after_effects_pipeline.cli audit-dataset \
  --config configs/lfm25_8b_a1b_after_effects.json

uv run python -m after_effects_pipeline.cli contact-sheets \
  --config configs/lfm25_8b_a1b_after_effects.json

uv run python -m after_effects_pipeline.cli render-review-queue \
  --config configs/lfm25_8b_a1b_after_effects.json
```

If AppleScript accepts `DoScriptFile` but AE does not execute the JSX body,
generate manual harness chunks and run them from After Effects:

```bash
uv run python scripts/build_ae_manual_harnesses.py
```

Run the generated `run_all_harnesses.jsx` from AE via
`File > Scripts > Run Script File...`.
It writes `runner_report.txt` beside the harness chunks and per-case
`report.txt` files under `artifacts/ae_live_checks/<case>/`.
Check the AE runner output before rendering:

```bash
uv run python scripts/check_ae_manual_harnesses.py
```

Then render the current project files, refresh every-third-frame analysis,
rebuild the review queue, export train-ready rows, rebuild MLX splits, and run
the training preflight:

```bash
uv run python scripts/refresh_after_manual_harnesses.py
```

For visual triage, inspect `artifacts/visual_analysis/review-dashboard.md`.
It groups every-third-frame analysis by decision, pack coverage, warning,
motion profile, and contact sheet.

For quality-focused training before the full render debt is cleared, use the
strict export under `artifacts/datasets/after-effects-high-quality/` and the
matching config:

```bash
uv run python -m after_effects_pipeline.cli train \
  --config configs/lfm25_8b_a1b_after_effects_high_quality.json
```

The refresh writes `quality-gate.json` and `quality-gate.md` under
`artifacts/datasets/after-effects-train-ready/`. Treat
`technical_trainable_subset=true` as a subset sanity check, not full completion;
`high_quality_trainable_subset=true` is the stricter signal for quality-focused
training, and `full_dataset_ready=true` is the gate for the complete diverse
rendered set.

Generate priority-ordered AE harnesses for the highest-value render debt:

```bash
uv run python scripts/build_ae_manual_harnesses.py
uv run python scripts/build_ae_manual_harnesses.py \
  --limit 8 \
  --output-dir artifacts/ae_live_checks/_manual_harnesses_priority
```

The refresh script already rebuilds MLX splits and runs the training preflight.
Before starting a LoRA run from the current promoted subset, re-run source
verification if desired, then start training:

```bash
uv run python -m after_effects_pipeline.cli verify-source \
  --config configs/lfm25_8b_a1b_after_effects_train_ready.json

uv run python -m after_effects_pipeline.cli train \
  --config configs/lfm25_8b_a1b_after_effects_train_ready.json
```

Live checks require this AE preference:

```text
After Effects > Preferences > Scripting & Expressions >
Allow Scripts to Write Files and Access Network
```

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
