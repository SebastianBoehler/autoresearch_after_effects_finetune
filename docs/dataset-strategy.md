# Dataset Strategy

The canonical dataset should be owned, small, and aggressively verified before
it grows.

## Sources

Use first-party generated samples first:

- source templates under `data/synthetic/templates/`
- metadata packs under `data/synthetic/manifests/`, included by
  `data/synthetic/manifest.json`
- canonical JSONL from `scripts/build_synthetic_dataset.py`
- manually reviewed model generations only after static or live verification

Avoid copying Adobe documentation into completions. The After Effects scripting
guide is useful reference material, but its own README marks the content as
Adobe-copyrighted educational material.

Marketplace and tutorial sites are reference-only unless an individual script
ships with explicit permissive training rights. Use pages such as aescripts,
Eje in Motion, Envato/Tuts+, AEJuice, Motion Array, Aeguys, Storyblocks,
Motionstyles, Gumroad, and similar
collections to identify workflow categories, UI patterns, and prompt ideas,
not to copy implementation code.

Useful reference categories include:

- shape-layer helpers, path tools, tapering, and alignment panels
- caption import, styling, timing, and subtitle animation
- one-click text, type, placeholder, and image-replacement systems
- seamless loops, motion trails, speed lines, and preset orchestration
- renderable broadcast, timeline, dashboard, and social-template builders
- trailer openers, logo stings, sports scorebugs, music visualizers,
  ecommerce story promos, science explainers, documentary title cards,
  travel stories, listing promos, split-screen launch openers, weather
  broadcast packs, finance reels, healthcare explainers, and fashion lookbooks
- pixel/voxel glitch titles, luxury product macro ads, conference agenda promos,
  vertical fitness challenges, documentary archive scans, AI/network explainers,
  trailer credits builders, object callout systems, grunge brush title reveals,
  waving flag openers, broadcast stream packs, and photo/logo placeholder
  reveals

Keep manifest packs and templates under 300 LOC. Add a new manifest pack when a
category expansion would make an existing file too large.

## Promotion Rules

A row is promotable when:

- it has explicit license/provenance metadata
- static syntax and AE contract checks pass
- required snippets are present
- forbidden snippets are absent
- live AE execution passes when available
- frame-sampled render analysis has no unexpected blank, low-motion, low-contrast,
  or severe overlap warnings
- manual review marks it as useful and visually coherent

Use `render-review-queue` to separate cases that can be promoted from cases
that need a missing render, stale re-render, or manual visual review.
When AppleScript cannot execute JSX, use `scripts/build_ae_manual_harnesses.py`
to create AE-run project-generation chunks. Run the generated
`run_all_harnesses.jsx` in After Effects, then use `scripts/render_aep_queue.py`
to render only current `.aep` files.
After those harness chunks are run in AE, use
`scripts/refresh_after_manual_harnesses.py` to render queued projects, refresh
visual analysis/contact sheets/audits, rebuild the queue, export the promoted
train-ready rows, rebuild MLX splits, and run the training preflight.

Use `scripts/export_train_ready_dataset.py` when training should consume only
cases promoted by visual review. It excludes missing renders, stale renders,
and cases marked for fixes, while preserving render/contact-sheet metadata in
the exported rows.
The export manifest records aspect-ratio counts, synthetic-pack coverage, top
tags, and excluded queue decisions so training runs cannot accidentally hide
coverage skew.
Use `scripts/build_training_readiness_report.py` after export to produce the
render-debt priority list for missing/stale cases that would improve training
coverage the most.
Use `scripts/build_source_animation_quality_audit.py` after regenerating
synthetic cases to catch source-level animation construction issues before AE
render time is spent. It checks temporal span, easing signals, dense text
layout risk, effects, 3D/camera usage, and procedural-motion strengths.
`scripts/build_ae_manual_harnesses.py` consumes that report when present, so
the generated AE scripts start with the highest-value missing renders. Use
`--limit` with a separate output directory for a short first manual pass.
Use `configs/lfm25_8b_a1b_after_effects_train_ready.json` for actual LoRA
training runs until the missing v9-v12 renders are generated and promoted.
Run `scripts/preflight_train_ready_training.py` before training to verify split
files, chat-message shape, MLX availability, and the exact `mlx_lm lora`
command without starting a long run.
Use `scripts/build_dataset_quality_gate.py` after preflight to separate a
technically trainable subset from a complete, diverse rendered dataset. The
subset can be useful for smoke tests, but do not treat the dataset objective as
complete until `full_dataset_ready` is true. For quality-focused training, also
require `high_quality_trainable_subset`; it fails when accepted cases still have
sparse/stalled motion, non-pass visual priority, or crowding warnings.
Use `scripts/build_visual_review_dashboard.py` to inspect the current render
set by decision, pack coverage, warning, motion profile, and contact sheet
before accepting or fixing visually dense samples.
Use `configs/lfm25_8b_a1b_after_effects_high_quality.json` for quality-focused
LoRA runs before the full render debt is cleared. It consumes
`artifacts/datasets/after-effects-high-quality/cases.jsonl`, which excludes
accepted-but-weak train-ready cases.

## HF Export

`export-hf-dataset` writes:

- `cases.jsonl`: canonical rows
- `chat.jsonl`: all rows as chat records
- `train.jsonl`, `valid.jsonl`, `test.jsonl`: MLX-ready splits
- `README.md`: dataset card with provenance notes
