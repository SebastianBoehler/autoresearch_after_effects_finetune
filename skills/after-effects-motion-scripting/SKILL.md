---
name: after-effects-motion-scripting
description: Create, review, and iterate Adobe After Effects ExtendScript JSX animation scripts and curated dataset samples. Use when writing AE scripts, improving motion-graphics trailer samples, using AE scripting APIs such as comps/layers/shapes/text/cameras/lights/effects/imports/markers/expressions, debugging AE JSX runtime errors, or benchmarking model outputs for professional motion design quality.
---

# After Effects Motion Scripting

## Workflow

1. Decide whether the script is self-contained or asset-backed.
   - Self-contained scripts must create all visuals procedurally.
   - Asset-backed scripts must use tiny local fixtures, not live URLs or absolute machine paths.
2. Storyboard before coding: 3-6 distinct beats, one visual system, fast deliberate transitions, readable title/subtitle/final lockup.
3. Write ES3-safe ExtendScript: `var` only, no `let`, `const`, classes, arrow functions, template strings, destructuring, `forEach`, or `map`.
4. Use stable AE handles: reacquire properties after adding shape operators if needed, and add Trim Paths/Repeaters before Stroke/Fill when AE reports invalid object handles.
5. Verify narrow first, then visually:
   - `node --check --input-type=commonjs < script.jsx`
   - repo dataset rebuild and source verifier when working in this repo
   - live AE execution/manual preview when judging visual quality

## Quality Bar

Do not accept a sample because it demonstrates APIs. A useful AE sample must also look intentional.

- Prefer one strong visual grammar over many unrelated elements.
- Use hairlines, masks, trim-path reveals, offset timing, camera/null drift, and fast cuts deliberately.
- Keep secondary text readable; avoid tiny gray microcopy.
- Avoid generic centered cards, random grids, arbitrary squares, and palette-only variations.
- Avoid overlap: reserve clear text zones and keep decorative systems behind or beside copy.
- Use asset-backed samples only when the referenced assets are visibly meaningful and good enough.

## API Coverage Targets

Use the smallest set that improves coverage for the sample:

- Project/comps: `app.project.items.addComp`, nested comps, precomps, save paths.
- Layers: solids, shape layers, text/box text, footage layers, nulls, cameras, lights.
- Shapes: paths, rectangles, ellipses, groups, Trim Paths, Repeaters, strokes/fills.
- Animation: `setValueAtTime`, `KeyframeEase`, markers, expressions, time remap when useful.
- Assets: `File`, `Folder`, `ImportOptions`, `app.project.importFile`, image sequences, audio, JSON/GeoJSON/CSV fixtures, `replaceSource`.
- Effects/materials: built-in effects by match name, blend modes, 3D material options, lights/camera depth.

## Runtime Rules

Read [references/extendscript-api-patterns.md](references/extendscript-api-patterns.md) when implementing or debugging JSX.

Read [references/motion-design-patterns.md](references/motion-design-patterns.md) when improving visual taste, pacing, transitions, or sample diversity.

Read [references/review-rubric.md](references/review-rubric.md) when comparing model outputs, deciding whether a sample is curated, or writing benchmark notes.

## Repo Integration

When adding samples in this repo:

- Put JSX in `data/synthetic/templates/`.
- Keep each file under 300 LOC.
- Put small owned fixtures in `data/synthetic/assets/`.
- Add one manifest row in `data/synthetic/manifest.json`.
- Rebuild `data/after_effects_synthetic_cases.jsonl` with `uv run python scripts/build_synthetic_dataset.py`.
- Verify with `uv run python -m after_effects_pipeline.cli verify-source --config configs/lfm25_8b_a1b_after_effects.json`.
