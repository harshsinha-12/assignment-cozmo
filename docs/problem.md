# Problem

## Confirmed (do not water down)

From `discussion.md`, the only problem statement we have:

> Turn phone camera captures into dimensioned, stitched floor plans with cm-level accuracy across three input tiers (photos, video, LiDAR).

Implications that are already in that sentence:

1. **Input is a phone**, not a Matterport rig or a laser scanner.
2. **Output is a floor plan**, not a pretty 3D mesh (mesh may be an intermediate).
3. **Dimensioned** — numbers on walls/rooms, not just a sketch to eyeball.
4. **Stitched** — more than one room or more than one capture, aligned.
5. **cm-level accuracy** — they will ask how you know.
6. **Three tiers** — the system is a product with degradation, not a single algorithm.

## Guessed (label everything in this section as a guess)

Until `docs/takehome.md` is filled, we are guessing:

- Timebox (4 hours vs a weekend vs a week)
- Whether they ship sample data
- Output format (PNG vs SVG vs JSON vs ESX)
- Whether an iOS app is expected (unlikely for a backend/applied-AI take-home; likely ingest of exports)
- Whether Android is in scope
- Multi-floor / stairs
- Furniture
- Damage heatmaps (water line, burn) vs geometry only
- Max runtime and whether GPU is assumed

## Non-goals (until the prompt says otherwise)

- Photoreal 3D tour
- Automatic Xactimate line items (WTR, DRY, PNT codes)
- Live AR measurement UI
- Training a foundation model

## Success, in the language of the JD

A dispatcher or estimator could take the JSON/SVG and not re-walk the room for basic wall lengths. Failures are explicit. The next engineer can rerun evals.

## How this file should change

When the official prompt arrives, add a section **“Official requirements”** with bullets copied from `docs/takehome.md`, and move anything contradicted from Guessed into `docs/decisions.md`.
