# Handoff

The current agent overwrites the **Current handoff** section at the end of every session. Keep older sessions as short bullets under **History**.

---

## Current handoff

**Date:** 2026-09-07  
**Branch:** `cursor/agent-orchestration-docs-4470`  
**Mode:** Orchestration only. Official take-home prompt is missing.

### What changed this session

- Turned an almost-empty repo (PDF + one-line problem + URL) into an agent operating kit.
- Extracted the Brynz **AI Backend Engineer** brief into `docs/job-brief.md`.
- Wrote a provisional technical plan for photos / video / LiDAR → dimensioned stitched floor plans.
- Added Cloud Agent setup files so the next VM can `pip install` without rediscovering dependencies.
- Locked FloorPlan IR (`docs/schemas/floorplan.schema.json`) and a synthetic two-room fixture with pytest.

### What is true now

- Problem sentence (only spec we have): *turn phone camera captures into dimensioned, stitched floor plans with cm-level accuracy across three input tiers (photos, video, LiDAR).*
- Company: Cozmo AI, hellocozmo.ai, property claims OS, Xactimate/Cotality, restoration field photos → carrier-ready estimates.
- Role: AI Backend Engineer (JD also reads like a forward-deployed / applied AI seat). Interview step 2 is the take-home; we do not have that packet yet.
- Linux Cloud Agents **cannot** run Apple RoomPlan. LiDAR work is export-in, process-here.
- No reconstruction code exists on purpose.

### Blockers

- Official take-home prompt, input formats, output contract, timebox, and allowed libraries.
- Real capture fixtures (at least one room with tape-measured ground truth).

### Next agent should

1. Confirm `docs/takehome.md` is still a stub.
2. If Harsh has pasted the official prompt: follow `docs/prompts/ingest-takehome.md` and stop planning.
3. If still no prompt: do not implement the pipeline. Optional unblocked work:
   - Collect one apartment room using `docs/capture-protocol.md` (T3)
   - Fill Cloud Agent secrets only if the prompt requires paid APIs (it may not)

### Read next (max five)

1. `AGENTS.md`
2. `docs/takehome.md`
3. `TASKS.md`
4. `plan.md`
5. `roadmap.md`

### Exact next command

If the official assignment arrived:

```text
Paste the full prompt into docs/takehome.md, then follow docs/prompts/ingest-takehome.md
```

If it did not:

```text
Human capture T3 (docs/capture-protocol.md) or wait. Do not start COLMAP/RoomPlan integration.
```

---

## History

- **2026-09-07** — First orchestration pass. Repo was `README.md` stub, `discussion.md` one-liner, `url.md`, and a PDF whose filename contained a newline (`AI Backend Engineer\n.docx.pdf`). Clean copy now at `docs/briefs/ai-backend-engineer.pdf`.
