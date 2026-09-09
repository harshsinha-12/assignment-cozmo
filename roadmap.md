# Roadmap

Phases are gated by **dependencies**, not by “optional tiers.” Official prompt: `docs/takehome.md`. **Max-score policy:** pass every official row; cut only via `docs/cut-later.md`.

Capture: Route 2 protocol always; Route 1 (T21) in parallel. Product: `docs/product.md`.

```text
1 ingest (this session) ──► 2 schema + red eval + CLI stub
                                │
                                ▼
                         3 LiDAR mapper + SVG
                                │
                                ▼
                         4 stitch + drift ablation
                                │
                                ▼
                         5 video ──► 6 photos (folder stitch, ±8% CIs)
                                │
                                ▼
                         7 agent + tools (LLM API → damage/scope/rules)
                                │
                                ▼
                         8 human benchmark capture (parallel from now)
                                │
                                ▼
                         9 eval tables + head-to-head
                                │
                                ▼
                         10 fix loop (before / after / diff)
                                │
                                ▼
                         11 package: compliance, 6pp report, README 15 min
                                │
                                ▼
                         12 walk-in rehearsal (all three tiers)
                                │
                                ▼
                         T21 iOS exporter (parallel from Phase 2; promote only if 10-min install)
```

Human capture (Phase 8) **starts tonight** and does not wait for Phase 3.

## Phase 1 — Ingest the official take-home

**Status:** done 2026-09-08

- Prompt in `docs/takehome.md`
- Plan aligned, TASKS rewritten, ADR written

## Phase 2 — Contract, CLI stub, red evals

- Extend FloorPlan schema: required intervals, damage, concealed flags, scope
- Job directory + `manifest.yaml`
- `python -m cozmo_floorplan run` returns `status: failed` with structured JSON until adapters exist
- Eval CLI encodes official gates; `make test` fails honestly on empty preds

Done when: empty pipeline is valid JSON against schema; eval reports red on synthetic truth.

## Phase 3 — LiDAR tier

**Status:** partial — portable RoomPlan JSON works; T6a–T6b3 decode real Record3D and emit partial interval-bearing rooms, walls, ceilings, areas, and supported openings. Cross-archive registration, interval calibration, repeatability, and USDZ remain.

- Ingest Record3D / RoomPlan / USDZ as available
- Metric walls, openings, ceiling, area
- Single-room then multi-room

Done when: synthetic or real LiDAR JSON produces a dimensioned plan.

## Phase 4 — Stitch + drift

- Doorway graph, SE(2)
- Drift correction (plane-anchored / loop closure — pick one, document)
- Ablation flag: correction on vs off
- SVG whole-property render

Done when: two rooms share a door without overlap; ablation images exist.

## Phase 5 — Video tier

**Status:** partial — T7b multi-walkthrough identity/orientation, T7c
deterministic ORB/geometric track gates, and T7d segmented scale-free relative
poses work on the two current iPhone videos. T7e adds strict metric pose-sidecar
validation and per-segment similarity alignment. The current videos have no
sidecars; room geometry and FloorPlan output remain.

- ffmpeg sample + tracking or poses
- Same IR, wider intervals than LiDAR

Done when: a walkthrough clip emits a plan that eval can score.

## Phase 6 — Photos tier

- 2–8 stills per room folder, no crash
- Manhattan / VP regularizer
- Metric cm with calibrated intervals (tighten when evidence is strong)
- Multi-folder stitch, ±8% footprint **pass target**
- Opening detection scored (miss/phantom); chase ≤2 cm where the data supports it

Done when: a photos job of 3+ rooms produces one SVG with adjacency.

## Phase 7 — Agent + tools (damage / concealed / scope)

- Disclosed OpenAI-compatible (or Anthropic) tool-calling loop
- Tools: `get_plan`, `apply_damage`, `fire_concealed_rule`, `add_scope_line`, …
- Vision on damage crops; quantities from geometry tools
- Fallback: same tools, no API key

Done when: staged-damage fixture emits `damage` + `concealed_flags` (with rule ids) + `scope` via the agent path, and `run` still works with the key unset.

See `docs/agent-layer.md`.

## Phase 8 — Benchmark capture (human)

Blocked on phone + tape. Spec in `docs/capture-protocol.md`.

## Phase 9 — Benchmark report + incumbent

- Gate table all tiers
- Repeatability table
- Head-to-head vs named Polycam or magicplan version on 2 rooms
- Timing

## Phase 10 — Fix loop (25%)

- One-page `docs/fix-loop.md`
- Frozen “before” run
- Ship one fix
- Regenerable after + diff

## Phase 11 — Submission package

- Compliance matrix green/partial
- Device matrix filled
- README 15 min
- `docs/writeup.md` ≤ 6 pages
- Reproduction bundle

## Phase 12 — Walk-in rehearsal

- Follow `docs/capture-route.md` on a room not in the benchmark
- Time the command
- `docs/interview-prep.md`

## Explicitly not building (does not score)

- Website, accounts, our API
- ESX writer
- Foundation model training

## In scope until a tomorrow-night cut

- Route 1 iOS/TestFlight (T21)
- Photo opening/ceiling centimetre chase
- Repeat captures at photos and video
- Mirrors / glass / wet / low-light handling

## 48-hour time split (do the whole table; cut from the bottom of `docs/cut-later.md` only)

| Slice | Share | Notes |
| --- | --- | --- |
| Schema + CLI + red eval | 8% | Phase 2; freeze fix-loop **before** as soon as this runs |
| LiDAR + SVG | 15% | Tight gates live here first |
| Stitch + drift ablation | 10% | Named gate |
| Video | 12% | ±3% is a pass target |
| Photos stitch + opening chase | 15% | Named stitch gate + detection |
| Damage/scope | 8% | Compliance |
| Route 1 iOS exporter | 7% | Parallel; drop last among scored extras |
| Human capture / GT / incumbent | parallel | iPhone 17 Pro |
| Fix loop | 12% | 25% of score |
| Reports, README, compliance | 8% | |
| Walk-in hardening | 5% | mirrors, 2-photo, cold room |
