# Cozmo floor-plan pipeline — technical report

**Submission status:** engineering draft; real benchmark sections are deliberately pending capture.

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

| Tier | Devices | Evidence and scale | Current implementation | Remaining proof |
| --- | --- | --- | --- | --- |
| LiDAR | iPhone 15/16/17 Pro or Pro Max; LiDAR iPad Pro | RoomPlan dimensions or depth + metric poses/intrinsics | RoomPlan JSON and raw Record3D map walls, ceilings, areas, supported openings, scale and provenance into the IR | Cross-room registration, opening truth, repeat/holdout validation, and USDZ |
| Video | Any iPhone 15+ | Walkthrough frames; metric poses when present, otherwise VO plus an auditable scale source | MP4/MOV validation and approximately 2 Hz frame sampling; pose sidecar is detected | Metric VO, scale, reconstruction and calibrated intervals on real capture |
| Photos | Any iPhone 15+ | 2–8 stills per room; overlap, doorway correspondences and declared scale evidence | Deterministic room discovery, 2–8 count enforcement, decode/dimension validation | SfM, scale, adjacency, openings/ceiling and calibrated whole-property output |

LiDAR is the build-order anchor because its metric observations make geometry errors easier to isolate; it is not permission to skip the thinner tiers. Video must target ±3% wall error and photos ±8%, with the complete opening, ceiling, stitch and interval contract. Until those reconstructions exist, the CLI refuses to print metric geometry for those tiers. The final device matrix will replace targets with measured intervals from the same spaces captured at all three tiers.

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

Calibration is evaluated as empirical interval coverage against the mean declared confidence, with a five-percentage-point tolerance. The synthetic contract fixture covers 15/15 measurements (100%) at mean declared confidence 95%; that only verifies schema/evaluator behavior. On the three-room Record3D development benchmark, conservative p95 raw-plane residual envelopes define wall/ceiling half-widths and span propagation defines area intervals. They cover 16/18 measurements (88.9%) at 80% mean declared confidence without moving any centre estimate. This passes the internal gate on development data, not independent calibration; repeat captures and a held-out property remain required.

## 5. Claims agent and operational fallback

After geometry, a disclosed OpenAI Responses API agent classifies supplied damage observations and invokes strict tools to apply damage, fire an allowed concealed-damage rule, and add a scope line. `apply_damage` rejects model-supplied quantities and copies the calibrated metric extent from the observation. Concealed rule ids are policy-validated; scope quantities copy the stored damage extent. Calls use `store: false`, and provider mutations occur on a private copy.

If a live call times out, fails, or makes an incomplete tool sequence, its partial mutations are discarded and the deterministic agent runs the same tools. Explicit deterministic mode is a supported local path and preserves a healthy status after complete execution; an automatic missing-key fallback or provider failure remains `partial`. Every path retains an `agent_fallback` warning where applicable plus provider, mode, model and successful tool-call count in provenance. This keeps the walk-in runnable without our infrastructure while making degraded operation visible.

## 6. Measured evidence and fix loop

The table below is the only current numbered geometry evidence. It is synthetic and must not be presented as device accuracy.

| Evidence | Yield | Walls | Openings | Ceilings | Drift | Intervals |
| --- | --- | --- | --- | --- | --- | --- |
| Two-room RoomPlan contract fixture | `ok` (1/1) | median 0 cm; p95 0 cm; n=8 | 1/1 matched within 2 cm; median 0 cm | 2/2 matched; max error 0 cm | plane-anchored metadata + ablation present | 15/15 covered; declared 95% |

| Required benchmark evidence | LiDAR | Video | Photos |
| --- | --- | --- | --- |
| 3+ rooms plus connector vs tape | pending T3 | pending T3 | pending T3 |
| Wall/opening/ceiling accuracy | pending | pending metric recon | pending metric recon |
| Same-room repeatability | pending | pending | pending |
| Whole-property adjacency/footprint | pending | pending | pending |
| Calibrated intervals | pending | pending | pending |
| Two-room incumbent comparison | pending | not applicable | not applicable |
| Cold runtime | pending | pending | pending |

The shipped fix loop targeted a real evaluator failure in the synthetic pipeline rather than waiting for captures. Before the fix, the deterministic claims agent completed 7 tool calls, 2 damage records, 1 concealed flag and 2 scope lines, but an audit warning unconditionally downgraded `status` from `ok` to `partial`. The prediction was `pipeline_yield` 0% → 100% for this one-job case with no geometry or calibration change. After separating warning audit from health semantics, the CLI moved exit 2 → 0 and yield moved fail → pass exactly as predicted. Parsed FloorPlans differ only in top-level status; every non-target gate is identical. Checksummed, regenerable artifacts and the readable diff are in `data/fix-loop/`.

## 7. Known failure modes and walk-in posture

- **Mirrors/glass/wet glossy surfaces:** avoid head-on capture, retain multiple viewpoints, reject unsupported planes, and widen or fail when the room loop is incomplete.
- **Low light or motion blur:** turn on room lights, avoid flash/zoom, pause at corners and doors, and report insufficient evidence instead of stretching a prior.
- **Featureless photo/video walls:** enforce overlap and doorway views; require an auditable metric scale source before emitting centimetres.
- **Occlusion and furniture:** prefer RoomPlan wall categories over objects and use cross-view agreement; incomplete surfaces remain warnings.
- **Wrong opening association:** associate to supporting walls and score missed and phantom openings, not width on detections alone.
- **Disconnected or cyclic properties:** return partial connectivity when the opening graph is insufficient; use real ablations to justify any global optimizer.
- **API/key failure:** deterministic tool fallback completes claims without affecting classical geometry; provider-triggered degradation remains visible.

The final submission cannot claim readiness until the human benchmark supplies raw photos, video, LiDAR, tape/laser truth, repeated rooms, staged damage, and a named Polycam or magicplan export, **and** a holdout room not in that set is timed through `make walkin`. Those files unlock metric video/photo work, measured intervals, the device matrix, the head-to-head table, and a timed unseen-room rehearsal. The current system is production-shaped plumbing with honest boundaries; the remaining risk is reconstruction quality on real consumer capture, not JSON presentation.
