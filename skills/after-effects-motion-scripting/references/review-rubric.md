# Review Rubric

## Static Gate

A sample can enter manual review only if:

- JSX syntax passes.
- It creates the expected comp.
- Required API snippets are present.
- Forbidden APIs are absent: `app.quit`, `system.callSystem`, `fetch`, `XMLHttpRequest`.
- It stays under the repo line limit.

## Visual Gate

Reject or mark for rework when:

- the result looks like simple shapes placed on screen
- text overlaps or is hard to read
- scene changes are too slow, flat, or repetitive
- assets are low quality or do not justify being imported
- API coverage is visible but the trailer would not be useful as training taste data

## Benchmarking Models

Compare models on:

- execution validity in AE
- script compactness and ES3 compatibility
- API breadth used correctly
- motion grammar diversity
- text readability
- transitions and pacing
- final lockup quality
- amount of manual repair needed

## Current Repo Notes

- `pro_motion_trailer_intro.jsx` is a strong benchmark for fast editorial pacing and readable copy.
- `celestial_clockwork_luxury_trailer.jsx` is a broad API-coverage benchmark for cameras, lights, null rigs, 3D layers, Trim Paths, Repeaters, and text.
- `product_sequence_launch_trailer.jsx` is useful for import/sequence/replaceSource coverage, but it is not visually accepted yet. Replace its PNG fixtures with high-quality product graphics and redesign the full motion language before promoting it.
