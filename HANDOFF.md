# Handoff

The current agent overwrites the **Current handoff** section at the end of every session. Keep older sessions as short bullets under **History**.

---

## Current handoff

**Date:** 2026-09-08  
**Branch:** `main`
**Mode:** Max-score Round 2. **Agent + tools required** (Applied AI). Geometry still classical.

### What changed this session

- Completed **T16 claims agent + tools** with a live OpenAI Responses path and deterministic offline fallback.
- Added separate modules for config/policies, prompts, strict tool definitions, mutation tools, observations, image inputs, live agent, fallback agent, models, orchestration, and `.env` loading; all roles are in `docs/code-map.md`.
- Added `damage_observations.json` as the surface-mapped metric proposal boundary. The LLM cannot pass a quantity into `apply_damage`; tools copy extents and intervals.
- Added two explicitly synthetic staged-damage observations to the RoomPlan fixture and documented that they are contract data, not real-image evidence.
- Live `gpt-5-mini` smoke test succeeded with 7 tool calls, 2 damage records, 1 concealed-rule flag, 2 scope lines, and no fallback warning.

### What is true now

- Product: local CLI. Folder in → JSON + SVG out. No Redis, no our servers.
- **Recon** owns centimetres and interval-bearing measurements. **Agent** (OpenAI-compatible or Anthropic, disclosed) owns damage class, concealed **rule ids**, scope lines via tools. Fallback = same tools without an API key (walk-in must not crash).
- All three capture tiers remain pass targets. Route 2 is the guaranteed walk-in.
- Capture phone: iPhone 17 Pro.
- Schema v0.2 and its synthetic fixture validate.
- `python -m cozmo_floorplan run JOB --out OUT` writes paired JSON/SVG artifacts. Unavailable adapters honestly emit a failed JSON and explanatory SVG placeholder, then exit 2.
- `python -m cozmo_floorplan run data/fixtures/roomplan_two_room --out OUT` emits a schema-valid, dimensioned LiDAR FloorPlan and readable whole-property SVG.
- With observations present, the pipeline enriches claims through direct OpenAI tool calling when configured or the same validated tools offline. Live mutations roll back before fallback on any provider/tool-loop failure.
- The synthetic fixture emits 2 damage regions, 1 concealed flag with `CONCEALED_WATER_MIGRATION_001`, and 2 scope lines. Scope quantities exactly copy metric observation extents.
- Multi-room output is intentionally `partial`: global RoomPlan transforms are used as-is and T9 must add drift correction/ablation.
- Available synthetic metric gates have zero wall/area/opening error; repeat, drift, incumbent, and pipeline yield remain red or missing as expected.
- All 34 tests pass; ruff, compileall, and `git diff --check` pass.
- Raw Record3D/USDZ are not implemented or live-validated. No private sensor capture exists yet.

### Blockers

- Human T3 capture.
- Raw Record3D `.r3d`/metadata/depth fixture for the guaranteed Route 2 LiDAR path.
- Real damage images/crops and calibrated metric observation generation. The current observations are explicitly synthetic.
- Cozmo published schema still missing.

### Next agent should

1. **T21** check for Xcode, then build the thin RoomPlan/ARKit exporter only if it can preserve the 10-minute install goal.
2. Resume T6 raw Record3D fusion as soon as T3 supplies the real export.
3. Keep Route 2 as the scored capture route until Route 1 installation is proven.

### Read next (max five)

1. `TASKS.md`
2. `docs/capture-route.md`
3. `docs/capture-protocol.md`
4. `docs/code-map.md`
5. `docs/agent-layer.md`

### Exact next command

```text
T21: check whether Xcode is available. If it is, implement a minimal iOS RoomPlan/ARKit exporter whose JSON matches `docs/formats/roomplan-json.md`; keep Route 2 primary until a clean install takes under 10 minutes.
```

---

## History

- **2026-09-08** — T16 live OpenAI tool calling + offline fallback complete; live synthetic smoke and 34 tests pass.
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
