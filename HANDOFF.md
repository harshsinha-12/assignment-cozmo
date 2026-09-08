# Handoff

The current agent overwrites the **Current handoff** section at the end of every session. Keep older sessions as short bullets under **History**.

---

## Current handoff

**Date:** 2026-09-08  
**Branch:** `main`
**Mode:** Max-score Round 2. **Agent + tools required** (Applied AI). Geometry still classical.

### What changed this session

- Completed **T13**: an installable, modular `cozmo_floorplan` CLI package.
- Separated config, domain errors, job loading, schema validation, atomic output, FloorPlan factories, pipeline orchestration, path utilities, and CLI parsing.
- Added `docs/code-map.md`, which explains what every implementation file owns and must stay current as code is added.
- Added CLI tests for valid layouts, missing manifests/directories, structured output, and the exact module command.

### What is true now

- Product: local CLI. Folder in → JSON + SVG out. No Redis, no our servers.
- **Recon** owns centimetres and interval-bearing measurements. **Agent** (OpenAI-compatible or Anthropic, disclosed) owns damage class, concealed **rule ids**, scope lines via tools. Fallback = same tools without an API key (walk-in must not crash).
- All three capture tiers remain pass targets. Route 2 is the guaranteed walk-in.
- Capture phone: iPhone 17 Pro.
- Schema v0.2 and its synthetic fixture validate.
- `python -m cozmo_floorplan run JOB --out OUT` exists. Until adapters land, it honestly writes `status: failed`, a typed warning, empty geometry/claims arrays, and provenance, then exits 2.
- `make test` disables unrelated global pytest plugins and passes all 12 tests.
- Still no reconstruction code. T14 is now the next engineering task.

### Blockers

- Human T3 capture.
- API key for the live agent path (theirs at walk-in; Harsh’s locally). Never commit `.env`.
- Cozmo published schema still missing.

### Next agent should

1. **T14** red eval harness for the official gates.
2. Keep eval separate from reconstruction; empty predictions must fail honestly.
3. Do not skip T16 (agent). Do not let the LLM invent wall lengths.

### Read next (max five)

1. `TASKS.md`
2. `docs/code-map.md`
3. `docs/eval-and-accuracy.md`
4. `docs/schemas/floorplan.schema.json`
5. `tests/test_cli.py`

### Exact next command

```text
T14: implement a red eval harness for the official gates against FloorPlan v0.2. Empty predictions must report failures. Human: T3 capture.
```

---

## History

- **2026-09-08** — T13 modular CLI and job contract complete; 12 tests pass.
- **2026-09-08** — T12 FloorPlan IR v0.2 frozen; 8 schema tests pass.
- **2026-09-08** — Agent layer required (tool calling / public LLM API + fallback).
- **2026-09-08** — Max-score retarget. Cut list deferred to tomorrow night.
- **2026-09-08** — iPhone 17 Pro has TOF LiDAR.
- **2026-09-08** — Official prompt ingested.
- **2026-09-07** — First orchestration pass.
