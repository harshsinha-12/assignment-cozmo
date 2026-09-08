# Handoff

The current agent overwrites the **Current handoff** section at the end of every session. Keep older sessions as short bullets under **History**.

---

## Current handoff

**Date:** 2026-09-08  
**Branch:** `cursor/agent-orchestration-docs-4470`  
**Mode:** Official prompt is in `docs/takehome.md`. This session explained Round 2 scoring vs app vs Round 1 reuse. Ingest still pending.

### What changed this session

- Clarified: this packet is Round 2. Round 1 contract is inherited, not a separate optional track.
- An iOS app is not required. Max score is not guaranteed by implementing every feature.
- Round 1 output pipeline should be the Round 2 core now; a Round 1 capture app can be skipped.

### What is true now

- Official assignment exists. They provide no captures. Walk-in test (30%) + fix loop (25%) dominate scoring.
- Route 1 = own iOS/TestFlight app. Route 2 = named App Store tool + one-page protocol. XOR.
- Photos / video / LiDAR are all mandatory. Photo folders must still stitch a whole-property plan.
- Output is bigger than our FloorPlan IR: damage regions, concealed-damage flags, scope line items, CIs, rendered plan, one command per capture.
- No published schema was attached. Our `docs/schemas/floorplan.schema.json` is a starting IR, not the graded contract yet.
- No reconstruction code exists.

### Blockers

- Full ingest not run (`docs/prompts/ingest-takehome.md`).
- Human hardware + captures: iPhone 15+ for photos/video; Pro-class for LiDAR; 3+ rooms + connector; staged damage; tape GT; Polycam/magicplan export for Part 3.
- Published JSON schema still missing from the packet.

### Next agent should

1. Follow `docs/prompts/ingest-takehome.md`: ADR in `docs/decisions.md`, rescope `TASKS.md`/`plan.md`, extend schema for damage/scope/intervals.
2. Do not start a custom iOS app unless Harsh explicitly chooses Route 1.
3. After ingest: freeze schema + red eval, then LiDAR ingest first.

### Read next (max five)

1. `docs/takehome.md`
2. `docs/prompts/ingest-takehome.md`
3. `plan.md`
4. `docs/schemas/floorplan.schema.json`
5. `TASKS.md`

### Exact next command

```text
Follow docs/prompts/ingest-takehome.md. Then freeze schema + red eval. Do not start an iOS capture app.
```

---

## History

- **2026-09-08** — Second Q&A: Round 2 cannot be certainly maxed; app optional; Round 1 pipeline integrates now, app later is optional.
- **2026-09-08** — Official prompt present. Session was Q&A on routes vs tiers; ingest still pending.
- **2026-09-07** — First orchestration pass. Repo was `README.md` stub, `discussion.md` one-liner, `url.md`, and a PDF whose filename contained a newline (`AI Backend Engineer\n.docx.pdf`). Clean copy now at `docs/briefs/ai-backend-engineer.pdf`.
