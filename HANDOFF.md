# Handoff

The current agent overwrites the **Current handoff** section at the end of every session. Keep older sessions as short bullets under **History**.

---

## Current handoff

**Date:** 2026-09-08  
**Branch:** `main`
**Mode:** Max-score Round 2. **Agent + tools required** (Applied AI). Geometry still classical.

### What changed this session

- Implemented the **T6 RoomPlan JSON path** using a documented portable v1 format.
- Added separate typed RoomPlan parsing, surface-transform projection, wall polygonization, LiDAR uncertainty config, measurement construction, and FloorPlan assembly; documented every file in `docs/code-map.md`.
- Added `data/fixtures/roomplan_two_room`: 2 rooms, 8 walls, one shared 80×210 cm door, metric transforms, and high confidence.
- Added structured detection for unsupported raw Record3D/metadata and USDZ rather than guessing their bytes.

### What is true now

- Product: local CLI. Folder in → JSON + SVG out. No Redis, no our servers.
- **Recon** owns centimetres and interval-bearing measurements. **Agent** (OpenAI-compatible or Anthropic, disclosed) owns damage class, concealed **rule ids**, scope lines via tools. Fallback = same tools without an API key (walk-in must not crash).
- All three capture tiers remain pass targets. Route 2 is the guaranteed walk-in.
- Capture phone: iPhone 17 Pro.
- Schema v0.2 and its synthetic fixture validate.
- `python -m cozmo_floorplan run JOB --out OUT` exists. Until adapters land, it honestly writes `status: failed`, a typed warning, empty geometry/claims arrays, and provenance, then exits 2.
- `python -m cozmo_floorplan run data/fixtures/roomplan_two_room --out OUT` emits a schema-valid, dimensioned LiDAR FloorPlan.
- Multi-room output is intentionally `partial`: global RoomPlan transforms are used as-is and T9 must add drift correction/ablation.
- Available synthetic metric gates have zero wall/area/opening error; repeat, drift, incumbent, and pipeline yield remain red or missing as expected.
- `make test` passes 27 tests; ruff and compileall pass.
- Raw Record3D/USDZ are not implemented or live-validated. No private sensor capture exists yet.

### Blockers

- Human T3 capture.
- Raw Record3D `.r3d`/metadata/depth fixture for the guaranteed Route 2 LiDAR path.
- API key for the live agent path (theirs at walk-in; Harsh’s locally). Never commit `.env`.
- Cozmo published schema still missing.

### Next agent should

1. **T15** whole-property SVG renderer using the RoomPlan fixture output.
2. Resume T6 raw Record3D fusion as soon as T3 supplies the real export.
3. Do not skip T16 (agent). Do not let the LLM invent wall lengths.

### Read next (max five)

1. `TASKS.md`
2. `docs/code-map.md`
3. `docs/schemas/floorplan.schema.json`
4. `data/fixtures/roomplan_two_room/README.md`
5. `docs/formats/roomplan-json.md`

### Exact next command

```text
T15: render a readable whole-property SVG from FloorPlan v0.2 and the RoomPlan fixture. Keep raw Record3D T6 blocked until T3 supplies a real export; do not claim Route 2 LiDAR readiness.
```

---

## History

- **2026-09-08** — T6 RoomPlan JSON path works; raw Record3D/USDZ blocked on T3; 27 tests pass.
- **2026-09-08** — T14 official-gate eval CLI complete; 20 tests pass.
- **2026-09-08** — T13 modular CLI and job contract complete; 12 tests pass.
- **2026-09-08** — T12 FloorPlan IR v0.2 frozen; 8 schema tests pass.
- **2026-09-08** — Agent layer required (tool calling / public LLM API + fallback).
- **2026-09-08** — Max-score retarget. Cut list deferred to tomorrow night.
- **2026-09-08** — iPhone 17 Pro has TOF LiDAR.
- **2026-09-08** — Official prompt ingested.
- **2026-09-07** — First orchestration pass.
