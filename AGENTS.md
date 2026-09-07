# Agent operating manual

This file is the contract for every Cursor agent (Cloud or local) working in `assignment-cozmo`.

Read this first. Then follow the reading order. Do not invent a second plan.

## Mission

Build a take-home that turns **phone camera captures into dimensioned, stitched floor plans** with honest, measured accuracy across three input tiers:

1. **Photos** (hardest)
2. **Video**
3. **LiDAR** (most metric)

The work is for **Cozmo AI** (YC, property claims OS). The role is **AI Backend Engineer**. The interview process is: profile shortlist → take-home → technical discussion → culture fit → offer.

The official take-home prompt is **not in this repo yet**. Until it is, this repository is an orchestration kit, not an implementation.

## Hard rules

1. **Do not implement the reconstruction pipeline** until `docs/takehome.md` contains the official assignment text (not the stub). Scaffolding, schemas, fixtures, and eval harnesses are allowed if they do not pretend to be a solution.
2. **Do not rewrite planning docs** unless the official prompt contradicts them. Patch the contradiction in `docs/decisions.md` and `update.md`. Leave history in `update.md`.
3. **Do not re-extract** `docs/briefs/ai-backend-engineer.pdf`. The cleaned brief is `docs/job-brief.md`.
4. **Do not re-research Cozmo, RoomPlan, COLMAP, or Xactimate** unless you are implementing a specific algorithm and the existing note is insufficient. Start from `docs/research.md` and `docs/claims-domain.md`.
5. **Do not claim centimetre accuracy** without a numbered eval on fixtures. Photos-only reconstructions are usually up-to-scale. Metric scale needs a prior (LiDAR, IMU/VO, ARKit/ARCore poses, or a known object).
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
- Capture data on a phone → `docs/capture-protocol.md`
- Schema / API contract → `docs/schemas/floorplan.schema.json`, `docs/architecture.md`
- Algorithm work → `docs/capture-tiers.md`, `docs/research.md`, `docs/eval-and-accuracy.md`
- Claims / Xactimate framing → `docs/claims-domain.md`
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

- [ ] Official prompt is quoted in `docs/takehome.md`
- [ ] Three-tier ingest exists or is explicitly scoped out with a reason
- [ ] Output validates against `docs/schemas/floorplan.schema.json` (or a prompt-mandated replacement)
- [ ] Rooms stitch into a connected floor plan, not a pile of unrelated polygons
- [ ] Dimensions are in real units, with scale source recorded in provenance
- [ ] Eval table reports error in **cm** on fixtures, by tier
- [ ] Failure modes and fallbacks are documented (degenerate photo sets, no LiDAR, non-Manhattan rooms)
- [ ] A short write-up explains the system the way you would to Cozmo’s CTO
- [ ] A Cloud Agent or local `make test` path reproduces the eval without a laptop GUI

## Quality bar for this company

Cozmo’s product language is: agents that do the work, structured loss data, audit trails, no rip-and-replace, minutes-not-days. The take-home should feel like a **platform primitive**, not a CV demo:

- Structured output a downstream estimate agent could consume
- Provenance (why this wall is 342 cm, which frames/points it came from)
- Evals that would survive a go-live, not just a screenshot
- Honest degradation across tiers (LiDAR tight, video medium, photos widest interval)

## Things that look productive and are not

- Re-summarizing hellocozmo.ai
- Building a pretty React viewer before the IR and eval exist
- Training a foundation model
- Calling an LLM to “guess” room dimensions from a single photo and calling it centimetre-accurate
- Installing COLMAP on every Cloud Agent boot “just in case”
- Reverse-engineering Xactimate `.esx` unless the official prompt requires an ESX/SKX export
