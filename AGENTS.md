# Agent operating manual

This file is the contract for every Cursor agent (Cloud or local) working in `assignment-cozmo`.

Read this first. Then follow the reading order. Do not invent a second plan.

## Mission

Build a take-home that turns **phone camera captures into dimensioned, stitched floor plans** with honest, measured accuracy across three input tiers:

1. **Photos** (hardest)
2. **Video**
3. **LiDAR** (most metric)

The work is for **Cozmo AI** (YC, property claims OS). The role is **AI Backend Engineer**. The interview process is: profile shortlist → take-home → technical discussion → culture fit → offer.

The official take-home is in `docs/takehome.md` (Round 2). Product: local CLI + capture route, not a website. **Score policy:** target every official row; cut only via `docs/cut-later.md`.

## Hard rules

1. **Do not skip a scored tier or gate** because it looks hard. LiDAR-first is build order. Photos, video, damage/scope, drift ablation, and the fix loop are in scope until `docs/cut-later.md` says otherwise. Schema/CLI/eval before photos SfM.
2. **Do not rewrite planning docs** unless the official prompt contradicts them. Patch the contradiction in `docs/decisions.md` and `update.md`. Leave history in `update.md`.
3. **Do not re-extract** `docs/briefs/ai-backend-engineer.pdf`. The cleaned brief is `docs/job-brief.md`.
4. **Do not re-research Cozmo, RoomPlan, COLMAP, or Xactimate** unless you are implementing a specific algorithm and the existing note is insufficient. Start from `docs/research.md` and `docs/claims-domain.md`.
5. **Do not claim centimetre accuracy** without a numbered eval. Target every official gate; if a tier misses, publish the number and the interval. Do not pre-concede the row in the plan.
6. **Do not run iOS RoomPlan inside a Linux Cloud Agent.** Ingest exports (`CapturedRoom` JSON, USDZ, PLY/PCD). Capture happens on a phone; processing happens here.
7. **One FloorPlan IR for all tiers.** Three capture frontends, one schema, one renderer, one eval. See `docs/schemas/floorplan.schema.json`.
8. **End every session by updating** `update.md`, `HANDOFF.md`, and `TASKS.md`. If you skip this, the next agent will waste tokens rediscovering your work.
9. **Commit and push on the working branch** as you go. Do not leave the only copy of the work in the VM.
10. **Match Cozmo’s bar:** production-shaped thinking, evals, fallbacks, structured outputs, audit/provenance. A notebook that “kind of stitches photos” will fail the technical discussion even if the pictures look nice.

## Token budget (read in this order)

Stop when you can do the task. Do not load the whole `docs/` tree by default.

| Order | File | When |
| --- | --- | --- |
| 1 | `AGENTS.md` | Always |
| 2 | `HANDOFF.md` | Always |
| 3 | `update.md` | Always (latest entries only if the file is long) |
| 4 | `TASKS.md` | Always |
| 5 | `docs/takehome.md` | Always. If it is still a stub, you are in planning/setup mode |
| 6 | `README.md` | If you need the human map |
| 7 | `plan.md` | Before any architecture or code change |
| 8 | `roadmap.md` | Before choosing what to work on next |
| 9 | Task-specific docs | Only the file that matches the task |

Task → file:

- Official prompt just arrived → `docs/prompts/ingest-takehome.md` then `docs/open-questions.md`
- Setup / Cloud Agent env → `SETUP.md`, `.cursor/environment.json`
- What we are building / how they test → `docs/product.md`
- Capture on a phone → `docs/capture-protocol.md`, walk-in protocol → `docs/capture-route.md`, holdout rehearsal → `docs/walk-in.md`
- Cuts (tomorrow night only) → `docs/cut-later.md`
- Schema / API contract → `docs/schemas/floorplan.schema.json`, `docs/architecture.md`
- Algorithm work → `docs/capture-tiers.md`, `docs/research.md`, `docs/eval-and-accuracy.md`
- Claims / Xactimate framing → `docs/claims-domain.md`
- Agent / tool calling → `docs/agent-layer.md`
- Interview → `docs/interview-prep.md`

## Session protocol

### Start

1. Read the four always-files above.
2. Check `docs/takehome.md` for a real prompt.
3. Pick the top incomplete item in `TASKS.md` that is unblocked.
4. State the chosen task in `update.md` as an in-progress line if the session will last more than a few edits.

### During

- Prefer small, reviewable commits.
- Keep the FloorPlan schema stable. If you must break it, version it and note the change in `docs/decisions.md`.
- When you learn something that future agents should not re-derive, write it down once in the matching `docs/` file. One paragraph is enough.
- If the user pastes a new prompt, email, or recruiter note, put the raw text in `docs/takehome.md` or `docs/inbox.md` **before** changing the plan.

### End (mandatory)

Fill `HANDOFF.md` using the template already in that file:

- What changed
- What is true now
- What is still blocked
- Exact next command / next task
- Files the next agent should read (max five)

Append a dated entry to `update.md`. Check off finished work in `TASKS.md`.

## Definition of done (when the take-home exists)

A submission is done only if all of these are true:

- [x] Official prompt is quoted in `docs/takehome.md`
- [ ] Three-tier ingest **all implemented**, aiming at official gates (not stubbed as unsupported)
- [ ] Output validates against `docs/schemas/floorplan.schema.json` including damage, concealed flags, scope, intervals
- [ ] Rooms stitch into a connected floor plan, not a pile of unrelated polygons
- [ ] Drift ablation on vs off
- [ ] Dimensions in real units, scale source + **confidence interval** on every measurement
- [ ] Eval table reports official gates in **cm**, by tier, plus repeatability and head-to-head
- [ ] Fix loop: before, after, regenerable, readable diff
- [ ] Capture route (protocol and/or 10-min iOS build) + device matrix
- [ ] Compliance matrix complete
- [ ] Technical report ≤ 6 pages
- [ ] README: fresh capture in 15 minutes, one command
- [ ] Walk-in rehearsal on a room not in the benchmark

## Quality bar for this company

Cozmo’s product language is: agents that do the work, structured loss data, audit trails, no rip-and-replace, minutes-not-days. The take-home should feel like a **platform primitive**, not a CV demo:

- Structured output a downstream estimate agent could consume
- **Tool-calling agent** for damage/scope (API disclosed; fallback if no key)
- Provenance (why this wall is 342 cm, which frames/points it came from)
- Evals that would survive a go-live, not just a screenshot
- Honest degradation across tiers (LiDAR tight, video medium, photos widest interval)

## Things that look productive and are not

- Re-summarizing hellocozmo.ai
- Building a pretty React viewer or website before the IR and eval exist
- Skipping photos/video because LiDAR is easier
- Pre-conceding official gates in the plan
- Calling an LLM to **guess wall lengths** instead of tool-backed geometry
- Installing COLMAP on every Cloud Agent boot “just in case”
- Reverse-engineering Xactimate `.esx` unless the official prompt requires an ESX/SKX export
