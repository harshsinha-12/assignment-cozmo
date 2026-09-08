# Plan (aligned with official prompt)

Status: **aligned with `docs/takehome.md` (Round 2, Aug 2026).**  
Last updated: 2026-09-08.  
Product explanation: `docs/product.md`. ADR: `docs/decisions.md` (2026-09-08).

This is not a website. It is a **local one-command pipeline**: phone job folder → dimensioned stitched plan JSON + SVG + damage/scope, plus a capture route they follow at the walk-in.

**Score policy:** target **every** official row at full marks. LiDAR-first is build order, not “photos are optional.” Cuts happen only tomorrow night (`docs/cut-later.md`).

## 1. What Round 2 is asking

Round 2 inherits the full Round 1 output contract, then adds: you own capture, all three tiers, five extra gates, a live walk-in, a shipped fix loop, and a head-to-head vs Polycam/magicplan.

| Capture (submit one) | Pipeline (implement all, aim to pass) |
| --- | --- |
| Route 2 protocol always ready. Route 1 iOS app in parallel; switch scored route only if 10-min install works | Photos, video, **and** LiDAR. Same JSON. Photo folders still stitch. Every numbered gate is a **pass target**, including openings/ceiling/repeatability |

They provide **no captures**. We build the benchmark. They later capture a room we have never seen.

## 2. Design thesis (unchanged, now required)

**Three frontends, one IR, one renderer, one eval.**

```text
phone (Camera / Record3D)
        │
        ▼
job folder ─► normalizer ─► recon (L | V | P) ─► FloorPlan (metric)
                                                    │
                          stitch + drift fix ───────┤
                          agent + tools (LLM API) ──┤  damage, concealed rules, scope
                          same tools if API down ───┤
                                                    ▼
                                         JSON + SVG + eval
```

Degrade with **calibrated intervals**, not fake centimetres. The LLM does not invent wall lengths.

## 3. Output contract (IR)

Canonical schema: `docs/schemas/floorplan.schema.json` (extend in Phase 2; they did not attach a published schema).

Every capture must emit:

- Rooms: polygon, ceiling height, floor area, openings
- Walls with lengths
- Stitched adjacency (the product surface is the **whole-property** drawing)
- Per-surface damage: class + metric extent
- Concealed-damage flags with **the rule that fired**
- Scope line items keyed to surfaces
- **Confidence interval on every measurement**
- Provenance (tier, scale source, pipeline)
- Rendered plan (`floorplan.svg`)

Public command:

```text
python -m cozmo_floorplan run path/to/job --out path/to/out
```

Runs on their machine. No calls to **our** servers. **Disclosed LLM API with tool calling is in-scope** (`docs/agent-layer.md`); pretrained models/APIs allowed with disclosure. Walk-in: their API key or the local tool fallback.

## 4. Capture (human) vs pipeline (code)

**Human, tonight if possible** (`docs/capture-protocol.md` for the benchmark; `docs/capture-route.md` is what *they* follow):

- 3+ rooms plus a connector
- Same spaces at photos, video, and LiDAR
- One furnished room, two staged damage classes
- One room captured twice at the **same** tier (required: LiDAR pair). Also recapture photos and video of that room if time — repeatability is a scored gate, not LiDAR-only in the prompt.
- Laser or tape on everything
- Incumbent export (Polycam or magicplan, named version) on two rooms
- iPhone 15+ ; Pro required for LiDAR

**Code order:**

1. Schema + job layout + red eval (official gates)
2. LiDAR → IR (metric, can hit tight opening/ceiling gates)
3. Stitch + drift correction + on/off ablation
4. SVG renderer
5. Video adapter
6. Photos adapter: 2–8 stills in, stitched plan out; **target** ±8% walls **and** opening/ceiling gates; CIs calibrated (tight when evidence is strong)
7. Agent + tools: damage, concealed rules, scope (LLM API + fallback)
8. Benchmark tables + fix loop (fail → ship → before/after)
9. Compliance matrix, 6-page report, README 15 min

## 5. Reconstruction notes

**LiDAR.** Record3D and/or RoomPlan JSON. Map walls/openings to the floor plane. **Pass targets:** openings ≤2 cm on ≥85% (detection scored), ceiling ≤1.5 cm, recapture spread ≤1 cm, walls 1 cm / 0.5%, beat incumbent on ≥70% shared dims.

**Video.** Sample frames. Use poses if present; else tracking. Scale from metric poses → IMU → protocol prior. **Pass targets:** walls ±3% with calibrated intervals; same opening/ceiling/stitch contract as the other tiers.

**Photos.** 2–8 stills, no depth, no poses. Must not crash. Per-room folders → one plan, correct adjacency, no overlaps, footprint ±8%. **Pass targets:** walls ±8% with calibrated intervals; chase opening detection (miss/phantom count); metric cm (not `units: relative`). Use VP/Manhattan, COLMAP if it helps, door-in-frame scale, the full 8-photo budget. If a gate still fails, that is a **fix-loop candidate**, not a plan-time concession.

**Stitch.** Pose graph on the floor plane. **Must** correct accumulated drift (loop closure / plane-anchored snap). Ablation with correction on vs off is a named gate. “Poses used as-is” is an automatic fail.

**Damage / scope (agent).** After recon, a tool-calling LLM (disclosed OpenAI-compatible or Anthropic API) proposes damage class from crops, fires named concealed-damage rules, and emits scope lines. Quantities still come from geometry tools. If the API is down, the **same tools** run as a rule engine so the CLI never depends on our servers. Details: `docs/agent-layer.md`.

## 6. Gates — all are pass targets

| Gate | Bar | Target |
| --- | --- | --- |
| Openings | ≤ 2 cm on ≥ 85%; miss or phantom = miss | Pass on every tier we submit |
| Ceiling | ≤ 1.5 cm; recapture spread ≤ 1 cm | Pass |
| Repeatability | 1 cm or 0.5% per wall, two captures | Pass (LiDAR pair required; other tiers if captured) |
| Drift | Method + ablation | Pass (must not use poses as-is) |
| Photo stitch | Adjacency, no overlap, footprint ±8% | Pass |
| Photo walls | ±8% + calibrated intervals | Pass |
| Video walls | ±3% + calibrated intervals | Pass |
| Head-to-head | Beat/tie incumbent on ≥ 70% shared LiDAR dims | Pass |
| Walk-in | Cold run vs their laser, all three tiers | Pass |
| Fix loop | Fail → shipped fix → regenerable delta | Full marks (freeze before early) |
| Compliance | Every contract field | 100% coverage |
| Capture route | 10-min install, unambiguous | Pass |
| Process | Incremental git history | Pass |

Physics can still lose a row. That is an eval result, not a reason to skip the work. Tomorrow-night cuts: `docs/cut-later.md`.

## 7. What we will ship

- `src/cozmo_floorplan/` Python package
- CLI as above; `eval` subcommand for gates
- JSON + SVG + `eval.json`
- `docs/capture-route.md`, `docs/device-matrix.md`, `docs/compliance-matrix.md`
- Benchmark data + report + fix-loop bundle
- `docs/writeup.md` capped at ~6 pages
- Git history with incremental commits

**Out of scope (does not score):** website/SaaS, ESX, training nets, calling Harsh’s servers.

**In scope until a tomorrow-night cut:** Route 1 iOS exporter, photo opening/ceiling chase, video ±3%, mirrors/glass/low-light handling.

## 8. 48-hour implementation order

See `roadmap.md`. Do not start photos SfM before LiDAR + schema + a renderer that can show a fake-but-valid JSON. The fix loop is 25% — do not leave it for the last hour.

## 9. Decision policy

When two designs are equal, pick the one that:

1. Survives a cold walk-in (won’t crash on 2 photos, mirrors, low light)
2. Is explainable with tools closed
3. Emits intervals instead of confident garbage
4. Runs on a clean Linux/macOS laptop in 15 minutes

Record choices in `docs/decisions.md`.
