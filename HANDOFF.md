# Handoff

The current agent overwrites the **Current handoff** section at the end of every session. Keep older sessions as short bullets under **History**.

---

## Current handoff

**Date:** 2026-09-08  
**Branch:** `main`
**Mode:** Max-score Round 2. **Agent + tools required** (Applied AI). Geometry still classical.

### What changed this session

- Completed **T14**: a modular official-gate evaluation package and `eval` CLI.
- Added separate threshold config, report models, entity matching, measurement metrics, property geometry, evaluator, and eval I/O modules; all are documented in `docs/code-map.md`.
- Encoded yield, openings, ceilings, repeatability, drift ablation, photo stitch, photo/video walls, interval calibration, and LiDAR incumbent comparison.
- Added tests for red empty output, missing evidence, misses/phantoms, geometry-based adjacency matching, a perfect synthetic pass, head-to-head, and CLI output.

### What is true now

- Product: local CLI. Folder in → JSON + SVG out. No Redis, no our servers.
- **Recon** owns centimetres and interval-bearing measurements. **Agent** (OpenAI-compatible or Anthropic, disclosed) owns damage class, concealed **rule ids**, scope lines via tools. Fallback = same tools without an API key (walk-in must not crash).
- All three capture tiers remain pass targets. Route 2 is the guaranteed walk-in.
- Capture phone: iPhone 17 Pro.
- Schema v0.2 and its synthetic fixture validate.
- `python -m cozmo_floorplan run JOB --out OUT` exists. Until adapters land, it honestly writes `status: failed`, a typed warning, empty geometry/claims arrays, and provenance, then exits 2.
- `python -m cozmo_floorplan eval --pred PRED --truth TRUTH --out OUT` writes deterministic `eval.json`; repeat, ablation-off, and incumbent evidence are optional CLI inputs but missing evidence remains red where applicable.
- `make test` disables unrelated global pytest plugins and passes all 20 tests.
- Still no reconstruction code. T6 LiDAR is now the next engineering task.

### Blockers

- Human T3 capture.
- API key for the live agent path (theirs at walk-in; Harsh’s locally). Never commit `.env`.
- Cozmo published schema still missing.

### Next agent should

1. **T6** LiDAR export → FloorPlan adapter.
2. Keep capture-format parsing separate from geometry extraction and shared FloorPlan construction.
3. Do not skip T16 (agent). Do not let the LLM invent wall lengths.

### Read next (max five)

1. `TASKS.md`
2. `docs/capture-tiers.md`
3. `docs/research.md`
4. `docs/schemas/floorplan.schema.json`
5. `docs/code-map.md`

### Exact next command

```text
T6: implement LiDAR export → FloorPlan v0.2 against a documented Record3D/RoomPlan fixture. No real sensor capture exists in `data/private/` yet, so do not claim live validation. Human: T3 capture remains urgent.
```

---

## History

- **2026-09-08** — T14 official-gate eval CLI complete; 20 tests pass.
- **2026-09-08** — T13 modular CLI and job contract complete; 12 tests pass.
- **2026-09-08** — T12 FloorPlan IR v0.2 frozen; 8 schema tests pass.
- **2026-09-08** — Agent layer required (tool calling / public LLM API + fallback).
- **2026-09-08** — Max-score retarget. Cut list deferred to tomorrow night.
- **2026-09-08** — iPhone 17 Pro has TOF LiDAR.
- **2026-09-08** — Official prompt ingested.
- **2026-09-07** — First orchestration pass.
