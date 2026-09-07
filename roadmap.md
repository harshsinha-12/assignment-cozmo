# Roadmap

Phases are gated. Do not start a later phase just because it is more fun.

Official prompt missing = you may only work **Phase 0** and the unblocked parts of **Phase 0.5**.

```text
0 orchestration ──► 0.5 capture/fixtures ──► 1 ingest prompt
                                              │
                                              ▼
                         2 contract + eval harness (red)
                                              │
                                              ▼
                         3 LiDAR mapper (first green)
                                              │
                                              ▼
                         4 video  ──► 5 photos (scale-honest)
                                              │
                                              ▼
                         6 stitch + dimensions
                                              │
                                              ▼
                         7 eval table + write-up + demo
                                              │
                                              ▼
                         8 technical-discussion prep
```

## Phase 0 — Orchestration kit

**Status:** done (2026-09-07)

- Agent contract, handoff, plan, setup, schema stub, prompts
- Job brief extracted from the Brynz PDF
- Cloud Agent `install` via `.cursor/environment.json`

Done when: a new agent can start from `AGENTS.md` and not re-read hellocozmo.ai.

## Phase 0.5 — Fixtures and capture (unblocked without the prompt)

**Status:** synthetic fixture done (2026-09-07). Real-room capture still open.

Safe to do tomorrow morning even if the email has not arrived.

- [x] One synthetic axis-aligned apartment (two rooms + door) as JSON ground truth
- [ ] Optional: one real room captured per `docs/capture-protocol.md` (photos, a 30–60s video, LiDAR if an iPhone Pro is available)
- [ ] Tape-measure a few walls and write them in `manifest.yaml`

Synthetic fixture: `data/fixtures/synthetic_two_room/`. Eval *scoring* function still waits for Phase 2.

## Phase 1 — Ingest the official take-home

**Status:** blocked on recruiter / Cozmo packet

Follow `docs/prompts/ingest-takehome.md`.

- Paste the prompt into `docs/takehome.md`
- Diff it against this roadmap and `plan.md`
- Update `docs/open-questions.md` with anything still missing
- Freeze scope: what we will not build

Done when: `plan.md` is marked **aligned with official prompt** and `TASKS.md` is rewritten around that scope.

## Phase 2 — Contract and red evals

- Freeze `docs/schemas/floorplan.schema.json` (or replace it if the prompt dictates a schema)
- Job directory layout + `manifest.yaml` schema
- Eval CLI that scores an empty/wrong plan and fails
- Pytest on schema validation

Done when: `make test` fails for the right reason (no implementation), not because imports crash.

## Phase 3 — LiDAR tier

Highest accuracy, lowest risk, best story.

- Parser for `CapturedRoom` JSON
- Floor-plane projection of walls / doors / windows
- Single-room FloorPlan emit
- Multi-room stitch if a structure export is provided
- Green eval on a LiDAR fixture (synthetic JSON is enough if no iPhone)

Done when: LiDAR fixture wall errors are in the centimetre range **or** we document the export’s own error.

## Phase 4 — Video tier

- Frame sample via ffmpeg
- Pose path: use sidecar poses if present
- Fallback: sequential feature tracking
- Floor slice → walls
- Scale policy documented and encoded in provenance

Done when: video fixture produces a closed room loop and eval numbers we would say out loud in an interview.

## Phase 5 — Photos tier

- Overlap checks; fail early if SfM cannot start
- Vanishing-point / Manhattan regularization
- Scale: require prior or output unitless + `missing_scale` warning
- Do not hide this behind a fake 1.00 scale factor

Done when: photos either metric-with-prior or explicitly non-metric, and eval reflects that.

## Phase 6 — Stitch and dimension polish

- Doorway graph, SE(2) snap
- Opening widths
- SVG renderer that a human can sanity-check
- Provenance completeness

## Phase 7 — Package for humans

- `docs/writeup.md` (problem, method, results table, failure cases, what you’d do in week two at Cozmo)
- README quickstart that a founder could run
- Optional: 60-second demo script / recording
- Re-run evals on a clean Cloud Agent

## Phase 8 — Technical discussion

Use `docs/interview-prep.md`.

- Whiteboard the IR
- Defend scale physics
- Talk fallbacks and evals like a production FDE
- Connect the primitive to Xactimate sketch / estimate agents

## Explicitly later or never (unless the prompt says so)

- Training a wall-segmentation network
- Full ESX writer
- iOS capture app
- Real-time streaming reconstruction
- Multi-floor buildings with stairs as first-class geometry
- Web app with accounts

## Suggested time split once the clock starts

If the packet looks like a 48-hour take-home:

| Slice | Share |
| --- | --- |
| Prompt ingest + contract + fixtures | 15% |
| LiDAR path green | 25% |
| Video path usable | 20% |
| Photos path honest | 15% |
| Stitch + SVG + eval table | 15% |
| Write-up | 10% |

If it looks like a 4-hour take-home: **LiDAR + schema + eval + write-up**. Mention video/photos as designed, implement only a stub that returns `unsupported_tier` rather than a fake plan.
