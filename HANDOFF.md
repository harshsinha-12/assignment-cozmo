# Handoff

The current agent overwrites the **Current handoff** section at the end of every session. Keep older sessions as short bullets under **History**.

---

## Current handoff

**Date:** 2026-09-08  
**Branch:** `cursor/agent-orchestration-docs-4470`  
**Mode:** Max-score Round 2. **Agent + tools required** (Applied AI). Geometry still classical.

### What changed this session

- Harsh: we **will** use LLM tool calling / an AI API, not geometry-only.
- Added `docs/agent-layer.md`, ADR, architecture layer, T16 rewritten, `.env.example` keys.
- Still no reconstruction code. Next code is T12 schema.

### What is true now

- Product: local CLI. Folder in → JSON + SVG out. No Redis, no our servers.
- **Recon** owns centimetres. **Agent** (OpenAI-compatible or Anthropic, disclosed) owns damage class, concealed **rule ids**, scope lines via tools. Fallback = same tools without an API key (walk-in must not crash).
- All three capture tiers remain pass targets. Route 2 is the guaranteed walk-in.
- Capture phone: iPhone 17 Pro.

### Blockers

- Human T3 capture.
- API key for the live agent path (theirs at walk-in; Harsh’s locally). Never commit `.env`.
- Cozmo published schema still missing.

### Next agent should

1. **T12** schema (intervals, damage, concealed, scope).
2. T13 CLI, T14 red eval.
3. Do not skip T16 (agent). Do not let the LLM invent wall lengths.

### Read next (max five)

1. `docs/prompts/session-brief.md`
2. `docs/agent-layer.md`
3. `TASKS.md`
4. `docs/product.md`
5. `docs/schemas/floorplan.schema.json`

### Exact next command

```text
T12: extend floorplan.schema.json. Then T13+T14. T16 agent+tools after recon emits a plan. Human: T3 capture.
```

---

## History

- **2026-09-08** — Agent layer required (tool calling / public LLM API + fallback).
- **2026-09-08** — Max-score retarget. Cut list deferred to tomorrow night.
- **2026-09-08** — iPhone 17 Pro has TOF LiDAR.
- **2026-09-08** — Official prompt ingested.
- **2026-09-07** — First orchestration pass.
