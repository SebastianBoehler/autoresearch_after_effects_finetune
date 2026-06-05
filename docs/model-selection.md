# Model Selection

Checked on 2026-06-05.

## Default Baseline

Use `LiquidAI/LFM2.5-8B-A1B-MLX-8bit` first.

Reasons:

- It is newer than the Qwen2.5 family and has an official LiquidAI MLX card.
- The MLX quantization is about 9 GB, so it is realistic for local iteration.
- It supports the `mlx-lm` load path directly.
- It is not a dubious third-party "Claude/uncensored" merge.

Open issue: confirm `mlx_lm lora` support for this exact LFM2.5 MoE
architecture before a long run. The repo is scaffolded so that this can be a
short smoke command before committing overnight training time.

## Candidate Models

- `LiquidAI/LFM2.5-8B-A1B-MLX-8bit`: default candidate. The card says it was
  converted from `LiquidAI/LFM2.5-8B-A1B` with `mlx-lm` 0.31.3, uses 8-bit MLX,
  and is about 9 GB.
- `Qwen/Qwen3.5-2B` or `mlx-community/Qwen3.5-2B-*`: small Qwen option if LFM
  LoRA support blocks. This is not a coder-specific model, but it is much
  newer than Qwen2.5.
- `Qwen/Qwen3-Coder-Next` / MLX quantizations: strong coding direction, but the
  visible MLX 4-bit card is an 80B model around 44.8 GB. Better as teacher or
  benchmark target than first LoRA baseline.
- `mlx-community/Qwen3.6-40B-Claude-4.6-Opus-Deckard-Heretic-Uncensored-Thinking-8bit`:
  do not use as the default. It is an unofficial derivative/merge, 39B params,
  around 41.5 GB, trained on a Claude-named dataset, and tagged uncensored. That
  makes provenance and reproducibility weaker for this repo.

## Decision

Start with LFM2.5 as the default config. Keep Qwen3.5/Qwen3-Coder-Next in the
model-selection doc as candidates, not as the initial hard-coded training path.

Primary sources checked:

- https://huggingface.co/Qwen/models
- https://huggingface.co/LiquidAI/LFM2.5-8B-A1B-MLX-8bit
- https://huggingface.co/mlx-community/Qwen3.6-40B-Claude-4.6-Opus-Deckard-Heretic-Uncensored-Thinking-8bit
- https://huggingface.co/lmstudio-community/Qwen3-Coder-Next-MLX-4bit
