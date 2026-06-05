# autoresearch for After Effects on Apple Silicon

This repo is a config-driven autoresearch loop for **MLX LoRA fine-tuning of
small coding models on After Effects JSX project-generation tasks**.

## Objective

Train an adapter that produces runnable, compact After Effects scripts from
natural-language motion-design prompts.

Primary guardrail:

- `mean_case_score`

Secondary metrics:

- static JSX contract pass rate
- required snippet coverage
- forbidden snippet violations
- optional live After Effects execution pass rate
- optional render pass rate
- held-out `test_loss`

Lower loss alone is not enough. A candidate should not be promoted if it lowers
loss but regresses script safety or real AE execution.

## Experiment Loop

1. Build or refresh the synthetic dataset.
2. Verify source cases statically.
3. Run live verification only on reviewed candidates.
4. Build train/valid/test splits.
5. Fine-tune one LoRA adapter.
6. Evaluate against held-out cases.
7. Export HF dataset/model artifacts only after verification records are clean.

## Data Rule

Rows must be owned or explicitly licensed. The After Effects scripting guide is
useful reference material, but the repo should not copy documentation text into
training rows by default.

## Simplicity Rule

Prefer small, readable JSX scripts over maximal visual complexity. A 100-line
sample that reliably creates a comp is more useful than a clever 300-line script
that is hard to verify.

