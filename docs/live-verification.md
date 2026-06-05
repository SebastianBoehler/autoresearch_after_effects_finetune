# Live Verification

The default verifier is static and safe. It checks JSX balance, required AE API
patterns, forbidden APIs, and dataset-specific snippets.

Live verification is opt-in:

```bash
uv run python -m after_effects_pipeline.cli verify-source \
  --config configs/lfm25_8b_a1b_after_effects.json \
  --live
```

The live path:

1. Writes a temporary harness script under `artifacts/ae_live_checks/<case>/`.
2. Executes it through AppleScript against the configured After Effects app.
3. Inspects the created composition.
4. Saves a `.aep` project for manual review.
5. Optionally runs `aerender` when `--render` is set.

Use a clean After Effects session for live checks. This pipeline is intended for
dedicated verification runs, not while you have unrelated unsaved AE work open.
