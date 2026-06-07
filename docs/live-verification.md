# Live Verification

The default verifier is static and safe. It checks JSX balance, required AE API
patterns, forbidden APIs, and dataset-specific snippets.

Live verification is opt-in:

```bash
uv run python -m after_effects_pipeline.cli verify-source \
  --config configs/lfm25_8b_a1b_after_effects.json \
  --live
```

If the verifier reports `file/network access=None` or `file/network access=False`,
it has already inspected the active After Effects preference file and skipped a
doomed live run. The JavaScript debugger preference is separate and is not
sufficient for saving reports, projects, or renders.

If the verifier says the preflight returned without writing a report, After
Effects accepted the AppleEvent but did not produce the JSX side effect. Restart
After Effects into a clean session, then confirm the scripting preference below.

Before running `--live`, enable this After Effects preference:

```text
After Effects > Preferences > Scripting & Expressions >
Allow Scripts to Write Files and Access Network
```

In German builds this is shown as:

```text
After Effects > Voreinstellungen > Skripterstellung und Expressions >
Skripte können Dateien schreiben und haben Netzwerkzugriff
```

Check the persisted local preference state with:

```bash
uv run python scripts/check_ae_scripting_access.py
```

This writes `artifacts/ae_live_checks/scripting-access.md`. If it reports
`JavaScript debugger: enabled` but `file/network access: not set`, the debugger
checkbox is enabled but the required file/network scripting checkbox still is
not persisted.

If After Effects is closed, the local helper can set the persisted preference
and keep a backup of the original file:

```bash
uv run python scripts/enable_ae_scripting_access.py --apply
```

The live path:

1. Writes a temporary harness script under `artifacts/ae_live_checks/<case>/`.
2. Executes it through AppleScript against the configured After Effects app.
3. Inspects the created composition.
4. Saves a `.aep` project for manual review.
5. Optionally runs `aerender` when `--render` is set.

After a render pass, inspect sampled visual quality with:

```bash
uv run python -m after_effects_pipeline.cli analyze-renders \
  --config configs/lfm25_8b_a1b_after_effects.json
```

The analyzer samples every third source frame and writes JSON plus Markdown
reports under `artifacts/visual_analysis/`.

Generate visual contact sheets from the same every-third-frame stream:

```bash
uv run python -m after_effects_pipeline.cli contact-sheets \
  --config configs/lfm25_8b_a1b_after_effects.json
```

Combine render warnings with manifest theme/aspect-ratio coverage:

```bash
uv run python -m after_effects_pipeline.cli audit-dataset \
  --config configs/lfm25_8b_a1b_after_effects.json
```

Build the training review queue from the render analysis, audit, and contact
sheets. If `artifacts/visual_analysis/manual-review-decisions.json` exists,
explicit visual decisions are folded into the queue:

```bash
uv run python -m after_effects_pipeline.cli render-review-queue \
  --config configs/lfm25_8b_a1b_after_effects.json
```

After the queue is refreshed, generate a safe manual-decision scaffold for
rendered cases that need visual acceptance, rejection, or watch status:

```bash
uv run python scripts/build_manual_review_template.py
```

This writes `artifacts/visual_analysis/manual-review-decisions.template.json`
and `.md`. Copy it to `manual-review-decisions.json` only after replacing
`pending` with `promote`, `fix`, or `watch` for reviewed cases.

If AppleScript returns successfully but does not execute the JSX body, build
manual harness chunks for the queue items that need project generation:

```bash
uv run python scripts/build_ae_manual_harnesses.py
```

For the prioritized render-unlock batch, build and run the guarded runner:

```bash
uv run python scripts/build_render_unlock_harnesses.py
uv run python scripts/build_render_unlock_batch_status.py
uv run python scripts/run_ae_render_unlock_harnesses.py
```

`run_ae_render_unlock_harnesses.py` refuses before touching After Effects when
the file/network scripting preference is not enabled, and writes
`artifacts/ae_live_checks/_manual_harnesses_render_unlocks/run-status.md`.
`artifacts/visual_analysis/render-unlock-batch-status.md` reports whether the
batch is in `prepare_projects`, `blocked_prepare_projects`, or has targets
ready to render. When the batch stage is `blocked_prepare_projects`, fix the
listed blocker before rerunning the guarded render-unlock harness. After it
succeeds, refresh the render-unlock status and training gate:

```bash
uv run python scripts/check_render_unlock_harnesses.py
uv run python scripts/build_render_unlock_batch_status.py
uv run python scripts/build_render_unlock_completion_audit.py
uv run python scripts/build_dataset_quality_gate.py
```

Play-session checks use the same proof-of-execution rule. If
`scripts/run_ae_play_session_harnesses.py` reports a missing probe, After
Effects accepted the AppleScript command but did not execute the JSX chunk in
the current session; restart AE or run the generated chunk manually from
`File > Scripts > Run Script File...`.

For the fastest high-value pass, generate a priority-only runner from the
readiness report:

```bash
uv run python scripts/build_ae_manual_harnesses.py \
  --limit 8 \
  --output-dir artifacts/ae_live_checks/_manual_harnesses_priority
```

To close the web-inspiration motif gate directly, generate the first-unlock
motif runner:

```bash
uv run python scripts/build_motif_gap_harnesses.py
```

Check only those motif-gap targets with:

```bash
uv run python scripts/check_motif_gap_harnesses.py
```

After a motif-only AE run, refresh and render only cases that the motif status
report marks renderable:

```bash
uv run python scripts/refresh_after_manual_harnesses.py \
  --render-status-report artifacts/ae_live_checks/_manual_harnesses_motif_gaps/status.json
```

The default generated files live under
`artifacts/ae_live_checks/_manual_harnesses/`; the priority command above
writes to `artifacts/ae_live_checks/_manual_harnesses_priority/`, and the motif
runner writes to `artifacts/ae_live_checks/_manual_harnesses_motif_gaps/`. Run
the chosen `run_all_harnesses.jsx` from After Effects via
`File > Scripts > Run Script File...` after saving or closing unrelated AE work.
The runner executes every chunk with one confirmation. The chunks stay below
the repo line-count limit and write per-case `.aep` projects plus `report.txt`
files.
The runner also writes `runner_report.txt` beside the chunks, so a partial AE
run can be diagnosed by checking the last completed chunk.

For the current render-unlock batch, open
`artifacts/visual_analysis/manual-render-briefing.md` before running AE. It
lists the first-pass archetype-gap rerenders, the second-pass missing projects,
and the exact `run_all_harnesses.jsx` path. The companion
`artifacts/visual_analysis/quality-gap-matrix.md` explains why each case is in
that order using third-frame overlap, progression, and animation-anatomy data.
`artifacts/visual_analysis/theme-motion-audit.md` checks whether source themes
from the marketplace/category research are present in the train-ready rendered
motion set; its current gaps are folded into the render-unlock plan.
`artifacts/visual_analysis/training-sample-diagnosis.md` is the compact
front-door report for deciding what to render next: it ranks every case by
motion archetype gaps, overlap watches, theme gaps, and render quality.
Use `artifacts/visual_analysis/overlap-visual-review.md` to inspect the
highest-scoring overlap pairs as side-by-side every-third-frame sheets before
changing split assignments or adding more source cases.

Check the manual AE status before rendering:

```bash
uv run python scripts/check_ae_manual_harnesses.py
```

After the manual harnesses create current project files, render only queue
targets whose project file is not stale and rebuild the downstream train-ready
artifacts:

```bash
uv run python scripts/refresh_after_manual_harnesses.py
```

Use `--dry-run` to print the exact subprocess sequence without touching AE,
renders, or dataset artifacts.
Open `artifacts/visual_analysis/review-dashboard.md` after the refresh for the
decision, pack-coverage, warning, motion-profile, and contact-sheet overview.
The refresh also writes `artifacts/datasets/after-effects-train-ready/quality-gate.md`;
use `high_quality_trainable_subset` for quality-focused subset training and
`full_dataset_ready` as the completion signal for the full rendered training
dataset.
The strict subset lives at `artifacts/datasets/after-effects-high-quality/` and
uses `configs/lfm25_8b_a1b_after_effects_high_quality.json`.

Use a clean After Effects session for live checks. This pipeline is intended for
dedicated verification runs, not while you have unrelated unsaved AE work open.
