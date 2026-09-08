# Compliance matrix

Requirement → file path → artifact → status.

Status: `missing` | `partial` | `done`. Fill during implementation. This file is a scored deliverable (10%).

| ID | Requirement | File / command | Artifact | Status |
| --- | --- | --- | --- | --- |
| R1 | Choose one capture route | `docs/capture-route.md` | Route 2 one-pager | partial (draft) |
| R2 | Device matrix | `docs/device-matrix.md` | Hardware × tier × claimed interval | partial (draft) |
| R3 | Photos tier, 2–8 stills, no depth/poses, per-room folders, whole-property stitch | `src/` (not started) | JSON + SVG from photo job | missing |
| R4 | Video tier, handheld walkthrough | `src/` | JSON + SVG from video job | missing |
| R5 | LiDAR tier, depth+poses+intrinsics | `src/` | JSON + SVG from LiDAR job | missing |
| R6 | Per-room: walls, ceiling, area, openings | schema + pipeline | `floorplan.json` | missing |
| R7 | Stitched multi-room adjacency | stitch module | stitch graph + SVG | missing |
| R8 | Damage regions, class + metric extent | agent + tools (`docs/agent-layer.md`) | v0.2 `damage[]` schema ready; generation pending | partial |
| R9 | Concealed-damage flags + rule id | agent `fire_concealed_rule` | v0.2 `concealed_flags[]` requires `rule_id`; generation pending | partial |
| R10 | Scope line items keyed to surfaces | agent `add_scope_line` (qty from geometry) | v0.2 `scope[]` schema ready; generation pending | partial |
| R11 | Confidence interval on every measurement | schema | v0.2 `{value, unit, interval}` measurement objects | implemented |
| R12 | One command per capture | `src/cozmo_floorplan/cli.py` | command runs and emits structured JSON; successful adapters pending | partial |
| R13 | JSON to published schema | `docs/schemas/floorplan.schema.json` | our IR until they attach one | partial |
| R14 | Rendered plan | renderer | `floorplan.svg` | missing |
| R15 | Benchmark: 3+ rooms + connector, all tiers, damage, repeat, tape GT | `data/fixtures/` | raw + GT | missing |
| R16 | Opening width gate | eval | table | missing |
| R17 | Ceiling height + repeatability gates | eval | table | missing |
| R18 | Drift ablation | report + `eval --ablate-drift` | on/off footprints | missing |
| R19 | Photo-tier whole-property stitch ±8% | eval | table | missing |
| R20 | Head-to-head vs incumbent, 2 rooms, LiDAR | `docs/writeup.md` / benchmark report | table | missing |
| R21 | Fix loop: declaration, before, after, diff | `docs/fix-loop.md` | bundle | missing |
| R22 | README 15 min clean machine | `README.md` | — | partial |
| R23 | Reproduction bundle | `Makefile` + caches | regenerable numbers | missing |
| R24 | Technical report ≤ 6 pages | `docs/writeup.md` | PDF or md | missing |
| R25 | Mirrors / glass / wet / low light | report + fallbacks | warnings | missing |
| R26 | No calls to our infrastructure | code | local + disclosed models | not started |
| R27 | Process evidence | git history | commits as we work | doing |
