# Handoff

The current agent overwrites the **Current handoff** section at the end of every session. Keep older sessions as short bullets under **History**.

---

## Current handoff

**Date:** 2026-09-08  
**Branch:** `cursor/agent-orchestration-docs-4470`  
**Mode:** Max-score Round 2. **Agent + tools required** (Applied AI). Geometry still classical.

### What changed this session

- Completed **T12** and froze FloorPlan IR v0.2.
- Every scalar dimension is now `{value, unit, interval}`; intervals include low/high/coverage confidence.
- Added required `damage[]`, `concealed_flags[]`, and `scope[]` contracts plus typed surface keys and drift-correction metadata.
- Migrated the synthetic fixture and added positive/negative schema tests; 8 pass.

### What is true now

- Product: local CLI. Folder in → JSON + SVG out. No Redis, no our servers.
- **Recon** owns centimetres and interval-bearing measurements. **Agent** (OpenAI-compatible or Anthropic, disclosed) owns damage class, concealed **rule ids**, scope lines via tools. Fallback = same tools without an API key (walk-in must not crash).
- All three capture tiers remain pass targets. Route 2 is the guaranteed walk-in.
- Capture phone: iPhone 17 Pro.
- Schema v0.2 and its synthetic fixture validate. Test command: `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m pytest -q` (plain pytest has an environment plugin collision on `--output`).
- Still no reconstruction or CLI code. T13 is now the next engineering task.

### Blockers

- Human T3 capture.
- API key for the live agent path (theirs at walk-in; Harsh’s locally). Never commit `.env`.
- Cozmo published schema still missing.

### Next agent should

1. **T13** job layout + CLI stub with structured failed/partial JSON.
2. T14 red eval.
3. Do not skip T16 (agent). Do not let the LLM invent wall lengths.

### Read next (max five)

1. `TASKS.md`
2. `docs/schemas/floorplan.schema.json`
3. `docs/architecture.md`
4. `data/fixtures/synthetic_two_room/ground_truth.json`
5. `tests/test_schema.py`

### Exact next command

```text
T13: implement the job layout and `python -m cozmo_floorplan run` structured-failure CLI stub against FloorPlan v0.2. Then T14. Human: T3 capture.
```

---

## History

- **2026-09-08** — T12 FloorPlan IR v0.2 frozen; 8 schema tests pass.
- **2026-09-08** — Agent layer required (tool calling / public LLM API + fallback).
- **2026-09-08** — Max-score retarget. Cut list deferred to tomorrow night.
- **2026-09-08** — iPhone 17 Pro has TOF LiDAR.
- **2026-09-08** — Official prompt ingested.
- **2026-09-07** — First orchestration pass.
