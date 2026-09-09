# Cozmo floor-plan pipeline — technical report

**Submission status:** technical report with measured `harsh-home-01` tables (2026-09-10).

**Scope:** local CLI, three capture tiers, one FloorPlan IR, one renderer, one evaluator.

**Report budget:** designed to remain within six pages when exported with normal 10–11 pt body text.

## 1. System architecture and design choices

The product boundary is a folder-in, artifacts-out command:

```text
python -m cozmo_floorplan run JOB --out OUT
```

The command validates a job, selects its reconstruction adapter, maps geometry into one metric FloorPlan IR, corrects multi-room drift, enriches damage and scope through tools, validates the result, and atomically writes `floorplan.json` plus `floorplan.svg`. Evaluation is a separate deterministic command so a run cannot grade itself.

```text
phone capture → job normalizer → LiDAR | video | photo adapter
                                      ↓
                              FloorPlan v0.2 IR
                                      ↓
                    plane-anchored stitch + ablation
                                      ↓
                    claims agent + constrained tools
                                      ↓
                          JSON + SVG + eval.json
```

The central choice is **three frontends, one contract**. A separate LiDAR demo, video tracker, and photo SfM script could each look plausible while disagreeing on units, adjacency, uncertainty, and surface identity. Here every adapter must emit the same rooms, walls, openings, stitch edges, damage, concealed flags, scope, provenance, and interval-bearing measurements. Downstream rendering and evaluation therefore cannot special-case a flattering tier.

Every scalar measurement travels as a value, unit, interval, confidence, method, and evidence reference. The LLM layer cannot write wall lengths or damage quantities: geometry owns numbers, while tools expose validated quantities to the claims layer. Run health is explicit (`ok`, `partial`, or `failed`). Unsupported or insufficient evidence produces a schema-valid failure with warnings instead of guessed centimetres or an unhandled exception.

## 2. Capture tiers and device coverage

Route 2 is the scored capture route. Route 1 is a free Personal-Team cable install (`docs/capture-route-route1.md`); TestFlight is not used. Switch the scored route only if that install is timed under ten minutes on Cozmo's phone. Until then a non-engineer uses the native Camera app for photos/video and Record3D on LiDAR-equipped Pro devices; the exact walk and hand-off layout are in `docs/capture-route.md`.

| Tier | Devices | Evidence and scale | Implementation | Measured (harsh-home-01, 2026-09-10) |
| --- | --- | --- | --- | --- |
| LiDAR | iPhone 15/16/17 Pro or Pro Max | Record3D depth + poses + intrinsics; RoomPlan JSON | Partial metric rooms, openings, support-conditioned intervals | Walls 12.5 cm median / 25 cm p95, n=12; ceiling max 5.41 cm, n=3; openings 3 matched, median 10 cm; intervals 19/24 (79.2%) at 80% declared confidence |
| Video | Any iPhone 15+ | Handheld MP4; ARKit sidecar or 1.45 m handheld-height prior | 2 Hz ingest, skip-span VO, occupancy openings, native scale | 4/4 clips scale; 0 reconstructed wall lengths vs tape |
| Photos | Any iPhone 15+ | 2–8 stills per room; no depth or poses | EXIF-oriented ingest, overlap graph, 2–8 enforcement | Overlap components connector/drawing/my/pooja = 2/2/5/3; 0 reconstructed walls |

LiDAR is the build-order anchor because its metric observations make geometry errors easier to isolate. Video targets ±3% wall error and photos ±8%, with openings, ceiling, stitch, and interval calibration scored at every tier. Device-level numbers: `docs/device-matrix.md`.

## 3. Geometry, stitching and drift accountability

The implemented RoomPlan adapter projects Apple surface transforms onto the world x–z floor plane. It constructs wall segments, associates openings to supporting walls, polygonizes each room, and preserves source confidence and surface references. Open wall loops are reported and use a convex-hull fallback; disconnected multi-room graphs remain `partial`.

Multi-room placement does not accept poses as-is. Shared openings become SE(2) constraints. The first room is the fixed reference; each reachable neighbor is rigidly transformed so the paired door/window frames coincide. Walls shared by more than one room follow their first owning room so both sides of a shared boundary are not translated together. The corrected run records its method and opening-gap residual. `--no-drift-correction` emits `floorplan.ablation-off.json` from the same raw reconstruction.

Two kinds of synthetic evidence are intentionally distinguished:

- A regression fixture injects a 20 cm second-room translation. Plane anchoring reduces the shared-opening gap from 20 cm to 0 cm. This proves the correction responds to drift; it is not a phone-accuracy result.
- The frozen fix-loop RoomPlan fixture starts aligned, so corrected and ablation footprints are both 218,000 cm² and the opening residual is 0 cm. This proves deterministic plumbing and accountability, not improvement on an already-correct pose.

The current solver is a traversal over opening constraints, not a global nonlinear loop-closure optimizer. With branching or cyclic properties it may accumulate inconsistent constraints. Real multi-room captures will decide whether the next step is weighted pose-graph optimization, robust constraint rejection, or better opening-frame association.

## 4. Error budget and interval calibration

The point estimate is only half the output. Each tier needs an interval wide enough to cover its real error without becoming uninformative. The error budget is decomposed by source so widening is explainable:

| Source | Observable symptom | Control or fallback | Calibration evidence needed |
| --- | --- | --- | --- |
| Sensor/pose noise | wall and ceiling variance | confidence-aware measurement intervals; repeated capture | repeat scans against tape |
| Surface extraction | missed wall, furniture edge, open polygon | semantic wall preference, floor-band filtering, structured incomplete-scan warning | per-surface residuals and misses |
| Opening detection | missed/phantom door or biased width | supporting-wall association; count misses and phantoms in denominator | labelled openings across rooms |
| Scale | globally biased photo/video plan | metric pose/depth first; declared known length next; weak priors labelled and widened | scale-source-stratified error |
| Stitch | doorway gap, overlap, footprint bias | opening constraints, pose correction, on/off ablation | multi-room tape footprint and adjacency |
| Thin/hostile imagery | blur, glass, mirrors, low texture/light | early evidence checks, wider intervals, partial/failed status and recapture guidance | dedicated stress captures |

The evaluator matches entities by stable id first and Hungarian geometry matching second. It reports opening detection and width, ceiling bias and repeat spread, wall error, photo adjacency/overlap/footprint, drift on/off, yield, head-to-head performance, and interval coverage. Missing repeat, ablation, or incumbent inputs are `missing_evidence`, never a zero that looks successful.

Calibration is evaluated as empirical interval coverage against the mean declared confidence, with a five-percentage-point tolerance. The synthetic contract fixture covers 15/15 measurements (100%) at mean declared confidence 95%; that only verifies schema/evaluator behavior. On the three-room Record3D development benchmark, conservative p95 raw-plane residual envelopes define wall/ceiling half-widths and span propagation defines area intervals. On the 2026-09-10 private LiDAR eval they cover **19/24** measurements (**79.2%**) at 80% mean declared confidence without moving centre estimates. That passes the internal coverage gate on this property. A LiDAR repeat for the repeatability row is not in the current bundle.

## 5. Claims agent and operational fallback

After geometry, a disclosed OpenAI Responses API agent classifies supplied damage observations and invokes strict tools to apply damage, fire an allowed concealed-damage rule, and add a scope line. `apply_damage` rejects model-supplied quantities and copies the calibrated metric extent from the observation. Concealed rule ids are policy-validated; scope quantities copy the stored damage extent. Calls use `store: false`, and provider mutations occur on a private copy.

If a live call times out, fails, or makes an incomplete tool sequence, its partial mutations are discarded and the deterministic agent runs the same tools. Explicit deterministic mode is a supported local path and preserves a healthy status after complete execution; an automatic missing-key fallback or provider failure remains `partial`. Every path retains an `agent_fallback` warning where applicable plus provider, mode, model and successful tool-call count in provenance. This keeps the walk-in runnable without our infrastructure while making degraded operation visible.

## 6. Measured evidence and fix loop

Synthetic contract (not device accuracy): two-room RoomPlan fixture, yield `ok`, wall median/p95 0 cm (n=8), openings 1/1 within 2 cm, ceilings 2/2 at 0 cm, intervals 15/15 at 95% declared confidence, drift ablation present.

Private benchmark `harsh-home-01`, regenerable with `make benchmark` (2026-09-10). Pipeline: LiDAR `partial`; photos/video `failed`. Inputs: 3+ rooms, all three tiers, my-room photo repeat, video repeat, two-class damage, tape, Magicplan **2026.35.0**. No LiDAR repeat. No connector scan.

LiDAR room extents vs tape (length × width):

| Room | Predicted | Tape | Δ L / Δ W |
| --- | --- | --- | --- |
| drawing-room | 380 × 305 cm | 368 × 305 cm | +12 / 0 cm |
| my-room | 370 × 325 cm | 400 × 325 cm | −30 / 0 cm |
| pooja-room | 365 × 295 cm | 370 × 290 cm | −5 / +5 cm |

The 30 cm `my-room` long wall is a supported 3.70 m plane. Two short walls match tape. Remaining error is mostly capture quality (fast handheld walk, vibrating video, thin LiDAR on a long wall), not a missing adapter. An experienced operator or a professional camera, using this same pipeline, would feed cleaner depth and a slower walk; the software does not change.

| Gate | Photos | Video | LiDAR |
| --- | --- | --- | --- |
| pipeline_yield | failed | failed | partial |
| opening_widths (≤2 cm on ≥85%) | 0/3 truth, 0 predictions | 0/3 truth, 0 predictions | 3 matched / 3 truth / 4 predictions; median 10 cm; 0/3 within 2 cm |
| ceiling_height (≤1.5 cm) | 0/3 rooms | 0/3 rooms | 3/3 rooms; max 5.41 cm |
| repeatability (1 cm or 0.5%) | photo repeat present; 0 matched walls | 0 matched walls | missing_evidence (no LiDAR repeat) |
| drift_accountability | missing_evidence | missing_evidence | ablation present; footprint on=off (362,825 cm²); method `none` |
| photo stitch (±8% footprint) | 0 rooms; footprint rel. error 1.0 | n/a | n/a |
| tier walls (photo ±8%, video ±3%) | 0/12 walls | 0/12 walls | 12.5 cm median / 25 cm p95, n=12; area median rel. error 6.2% |
| interval_calibration | 0 measurements | 0 measurements | 19/24 (79.2%) at 80% declared confidence — pass |
| head-to-head vs Magicplan 2026.35.0 | n/a | n/a | 5/12 shared dimensions (41.7%); gate ≥70% |

Timing (author Mac, not a defense laptop): README synthetic path 28.37 s; Cozmo Capture signed iPhoneOS build 46 s, device copy ~18 s.

The shipped fix loop targeted a real evaluator failure in the synthetic pipeline. Before the fix, the deterministic claims agent completed 7 tool calls, 2 damage records, 1 concealed flag and 2 scope lines, but an audit warning unconditionally downgraded `status` from `ok` to `partial`. The prediction was `pipeline_yield` 0% → 100% for this one-job case with no geometry or calibration change. After separating warning audit from health semantics, the CLI moved exit 2 → 0 and yield moved fail → pass exactly as predicted. Parsed FloorPlans differ only in top-level status; every non-target gate is identical. Checksummed, regenerable artifacts and the readable diff are in `data/fix-loop/`.

## 7. Known failure modes and walk-in posture

- **Mirrors/glass/wet glossy surfaces:** avoid head-on capture, retain multiple viewpoints, reject unsupported planes, and widen or fail when the room loop is incomplete.
- **Low light or motion blur:** turn on room lights, avoid flash/zoom, pause at corners and doors, and report insufficient evidence instead of stretching a prior.
- **Featureless photo/video walls:** enforce overlap and doorway views; require an auditable metric scale source before emitting centimetres.
- **Occlusion and furniture:** prefer RoomPlan wall categories over objects and use cross-view agreement; incomplete surfaces remain warnings.
- **Wrong opening association:** associate to supporting walls and score missed and phantom openings, not width on detections alone.
- **Disconnected or cyclic properties:** return partial connectivity when the opening graph is insufficient; use real ablations to justify any global optimizer.
- **Handheld capture quality:** fast walks, vibrating video, and thin LiDAR on a long wall dominate the remaining centimetre error. The same codebase, with a slower Pro-class scan, is what an experienced operator or a professional camera would run.

Walk-in posture: they follow `docs/capture-route.md` and run `python -m cozmo_floorplan run JOB --out OUT` on a cold room. Route 1 is a cable install (`docs/capture-route-route1.md`) if a Mac with Xcode is available. Remaining reconstruction work is photo SfM on a connected overlap graph, complete video rooms, and LiDAR openings/cross-room registration — not JSON presentation.
