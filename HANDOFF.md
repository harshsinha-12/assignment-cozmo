# Handoff

The current agent overwrites the **Current handoff** section at the end of every session. Keep older sessions as short bullets under **History**.

---

## Current handoff

**Date:** 2026-09-08  
**Branch:** `main`
**Mode:** Max-score Round 2. **Agent + tools required** (Applied AI). Geometry still classical.

### What changed this session

- Completed **T15 whole-property SVG rendering** and paired run-artifact persistence.
- The CLI now writes both `floorplan.json` and `floorplan.svg` for successful, partial, and structured-failure runs.
- Split visual constants, coordinate layout, SVG composition, and artifact persistence into focused modules; documented every file in `docs/code-map.md`.
- Added renderer tests for rooms, openings, measured confidence intervals, determinism, XML escaping, and empty-geometry placeholders.
- Rendered the synthetic two-room artifact through macOS Quick Look and visually checked its plan geometry, labels, dimensions, opening, scale bar, and summary.

### What is true now

- Product: local CLI. Folder in → JSON + SVG out. No Redis, no our servers.
- **Recon** owns centimetres and interval-bearing measurements. **Agent** (OpenAI-compatible or Anthropic, disclosed) owns damage class, concealed **rule ids**, scope lines via tools. Fallback = same tools without an API key (walk-in must not crash).
- All three capture tiers remain pass targets. Route 2 is the guaranteed walk-in.
- Capture phone: iPhone 17 Pro.
- Schema v0.2 and its synthetic fixture validate.
- `python -m cozmo_floorplan run JOB --out OUT` writes paired JSON/SVG artifacts. Unavailable adapters honestly emit a failed JSON and explanatory SVG placeholder, then exit 2.
- `python -m cozmo_floorplan run data/fixtures/roomplan_two_room --out OUT` emits a schema-valid, dimensioned LiDAR FloorPlan and readable whole-property SVG.
- Multi-room output is intentionally `partial`: global RoomPlan transforms are used as-is and T9 must add drift correction/ablation.
- Available synthetic metric gates have zero wall/area/opening error; repeat, drift, incumbent, and pipeline yield remain red or missing as expected.
- All 30 tests pass; ruff and compileall pass.
- Raw Record3D/USDZ are not implemented or live-validated. No private sensor capture exists yet.

### Blockers

- Human T3 capture.
- Raw Record3D `.r3d`/metadata/depth fixture for the guaranteed Route 2 LiDAR path.
- API key for the live agent path (theirs at walk-in; Harsh’s locally). Never commit `.env`.
- Cozmo published schema still missing.

### Next agent should

1. **T16** agent + tools: damage classification, concealed-damage rule ids, scope, public-provider tool calling, and deterministic no-key fallback.
2. Resume T6 raw Record3D fusion as soon as T3 supplies the real export.
3. Do not skip T16 (agent). Do not let the LLM invent wall lengths.

### Read next (max five)

1. `TASKS.md`
2. `docs/agent-layer.md`
3. `docs/code-map.md`
4. `docs/schemas/floorplan.schema.json`
5. `src/cozmo_floorplan/io/artifacts.py`

### Exact next command

```text
T16: implement the disclosed public-provider tool-calling agent and deterministic fallback for damage, concealed rule ids, and scope. Geometry tools are the only source of quantities; no LLM-guessed centimetres.
```

---

## History

- **2026-09-08** — T15 JSON/SVG artifact pair complete; synthetic visual QA and 30 tests pass.
- **2026-09-08** — T6 RoomPlan JSON path works; raw Record3D/USDZ blocked on T3; 27 tests pass.
- **2026-09-08** — T14 official-gate eval CLI complete; 20 tests pass.
- **2026-09-08** — T13 modular CLI and job contract complete; 12 tests pass.
- **2026-09-08** — T12 FloorPlan IR v0.2 frozen; 8 schema tests pass.
- **2026-09-08** — Agent layer required (tool calling / public LLM API + fallback).
- **2026-09-08** — Max-score retarget. Cut list deferred to tomorrow night.
- **2026-09-08** — iPhone 17 Pro has TOF LiDAR.
- **2026-09-08** — Official prompt ingested.
- **2026-09-07** — First orchestration pass.
