# Rating Workflow

Build source verification first:

```bash
uv run python -m after_effects_pipeline.cli verify-source \
  --config configs/lfm25_8b_a1b_after_effects.json
```

Create a human review queue:

```bash
uv run python -m after_effects_pipeline.cli build-review-queue \
  --config configs/lfm25_8b_a1b_after_effects.json \
  --verification artifacts/evals/lfm25-8b-a1b-after-effects-source.json \
  --output-dir artifacts/reviews/source-v1
```

Review `artifacts/reviews/source-v1/review_queue.jsonl` and edit:

- `review_status`: `accepted`, `rejected`, or `needs_fix`
- `review_notes`: short reason
- `promote`: final boolean

Only promoted rows should be merged into a higher-quality training source.
