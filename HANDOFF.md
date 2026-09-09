# Handoff

The current agent overwrites the **Current handoff** section at the end of every session. Keep older sessions as short bullets under **History**.

---

## Current handoff

**Date:** 2026-09-10
**Branch:** `main`
**Mode:** Max-score Round 2. **Agent + tools required** (Applied AI). Geometry still classical.

### What changed this session

- Completed **T6d support-conditioned Record3D intervals**. A separate
  uncertainty algorithm converts conservative p95 residuals around each raw
  floor, ceiling, and wall plane into wall-span/ceiling half-widths and
  propagated area bounds.
- Point estimates did not move. Private aggregate interval coverage moved from
  11/18 (61.1%) to 16/18 (88.9%) at 80% mean declared confidence, so the
  internal calibration gate now passes. This is development-benchmark
  calibration, not independent holdout proof.
- Raw support strongly backs the visible 3.70 m `my-room` plane separation;
  the pipeline does not manufacture the missing 30 cm needed to match tape.
- Completed **T6c frame-invariant wall evaluation**. Generated Record3D wall
  numbers are no longer trusted as cross-document identities; walls match by
  room-local cyclic topology and side lengths across translation, rotation,
  reflection, and array reordering.
- The private LiDAR wall result is now an honest 2.5 cm median / 30 cm p95 over
  12 walls instead of the invalid 75 cm median caused by long-to-short ID
  matches. No reconstruction centre used truth.
- Completed **T8b2 robust photo overlap**. Added a bounded CLAHE-assisted SIFT
  fallback alongside ORB, with unchanged normalized match/inlier/coverage
  acceptance gates.
- Added explicit component membership and isolated-image names to diagnostics.
  The real primary set improved connector/drawing/my/pooja from 5/6/7/7 to
  2/2/5/3 components and now has conservative connector↔my-room and
  connector↔pooja-room candidates.
- Metric SfM remains blocked because every room graph is still disconnected;
  the CLI continues to refuse centimetres.
- Completed **T20d benchmark evidence activation**. Photo/video repeat manifests
  now link to their primary jobs and declare `my-room`; readiness no longer
  incorrectly requires a LiDAR repeat.
- Added separate repeat/evidence validators. Readiness validates FloorPlan JSON,
  requires two incumbent rooms, verifies two damage classes and local image
  refs, and rejects unlinked or mismatched repeat manifests.
- Normalized supplied tape measurements, three measured damage records, and two
  Magicplan room summaries without inventing individual wall dimensions.
- Python verification passes: 138 tests, Ruff, compileall, full private
  benchmark, and diff check.
- Implemented **T21f** CLI ZIP ingest: `python -m cozmo_floorplan run` accepts a
  Cozmo Capture `.zip`, unpacks it, reconstructs RoomPlan JSON, and writes a
  structured failure for incomplete archives. First-flight install steps are in
  `ios/CozmoCapture/README.md`.
- CLI/lidar/capture-package tests for this change pass. The iOS app still cannot
  run RoomPlan on the Mac or Simulator.
- No commit was made.

### What is true now

- Product: local CLI. Folder **or Cozmo Capture ZIP** in → JSON + SVG out.
- Route 2 remains the default/scored capture route. T21 Route 1 is parallel and
  must not replace it until a signed device install completes in under 10
  minutes.
- The T21 app names rooms, merges with `StructureBuilder`, logs per-room ARKit
  `.r3d` archives, and shares one job ZIP. The CLI reconstructs that ZIP. On-
  device RoomPlan/LiDAR sensing has not been exercised yet.
- Remaining T21 work is T21g (signed iPhone install) and optional T21d
  (in-app photo/video modes).
- The active benchmark has 8/8/8/5 decodable primary photos, four primary
  videos, an 8-photo `my-room` repeat, a repeat `my-room` video, three room
  Record3D scans, normalized tape measurements, and two-class damage evidence.
- Magicplan now covers `my-room` and `pooja-room`. Its screenshots expose room
  summary dimensions but not individual wall lengths; the exact app version is
  still unrecorded.
- Primary/repeat photos and video run but fail their current geometry gates.
  LiDAR emits a partial FloorPlan.
- LiDAR's remaining measured failures include 30 cm on both `my-room` long
  walls, 5.41 cm maximum ceiling error, unscored/unmatched opening predictions,
  and disconnected room scans. These are not hidden by the evaluator fix.
- LiDAR interval calibration passes 16/18 on the current benchmark. Two
  `my-room` long-wall truths remain outside the support-conditioned intervals;
  repeat/holdout validation is still unavailable.
- Final `make benchmark` reports `status=complete` with zero pending input
  classes. The LiDAR head-to-head gate passes 2/2 shared ceiling dimensions,
  but this is sparse evidence and must not be described as a wall comparison.
- The post-T8b2 full benchmark also completes with zero pending inputs; its
  photo warning records the improved 2/2/5/3 component counts and two connector
  candidates while preserving `status=failed` for incomplete photo geometry.

### Blockers

- Human T3 remainder, if available: exact Magicplan version, connector LiDAR,
  and measured property placement/opening supporting walls and offsets.
- T21g Apple-team signing and timed under-10-minute iPhone install.
- T8c metric SfM remains blocked by disconnected photo overlap. The current
  isolated files include my-room `02-wall-a.JPG` and
  `08-damage-and-overlap.JPG`, plus pooja-room `03-wall-b.JPG` and
  `08-ceiling-wall.JPG`. Corner-transition replacements would help; keep at
  most eight photos per room.

### Next agent should

1. Review/commit the existing T21, T20d, and T8b2 changes before another
   overlapping implementation stage.
2. Review T6d. Next choose T7 native-video fallback/scale evidence or T8 photo
   SfM recovery; do not add a Record3D centre correction unsupported by raw
   planes.
3. T21g remains the separate signed iPhone installation rehearsal.

### Read next (max five)

1. `TASKS.md`
2. `out/benchmark/benchmark-summary.md`
3. `src/cozmo_floorplan/recon/record3d_uncertainty.py`
4. `out/benchmark/lidar/eval.json`
5. `docs/eval-and-accuracy.md`

### Exact next command

```bash
make benchmark
```

---

## History

- **2026-09-10** — T6d support-conditioned Record3D intervals moved private coverage 61.1%→88.9% without changing centre estimates.
- **2026-09-10** — T6c fixed cross-frame wall identity scoring; private LiDAR now reports 2.5 cm median / 30 cm p95 without truth-driven reconstruction tuning.
- **2026-09-10** — T8b2 added CLAHE+SIFT fallback and improved every real photo graph without weakening acceptance gates.
- **2026-09-09** — T20d activated truth/damage/repeats and corrected any-tier repeat readiness; two-room Magicplan summaries normalized.
- **2026-09-09** — T20d activated truth/damage/repeats and corrected any-tier repeat readiness; only second-room incumbent evidence remains pending.
- **2026-09-09** — T21f CLI accepts a Cozmo Capture ZIP and reconstructs RoomPlan JSON.
- **2026-09-09** — T21e shareable job ZIP (`manifest.yaml` + `lidar/`) with Python unpack/reject.
- **2026-09-09** — T21c ARKit RGB-D logging writes Record3D-compatible `.r3d` beside roomplan.json.
- **2026-09-09** — Damage evidence classified as crack/impact damage; measurements intentionally left for Harsh.
- **2026-09-09** — T21b named multi-room RoomPlan capture/`rooms[]` export; simulator and unsigned iPhoneOS builds succeed.
- **2026-09-09** — T3 clean-reshoot folders/templates prepared; old photo/video media archived outside active jobs.
- **2026-09-09** — T21a single-room iOS RoomPlan exporter foundation complete; device/multi-room T21b remains.
- **2026-09-09** — T20c final benchmark runner complete; real partial audit reports exactly four missing evidence classes.
- **2026-09-09** — T7g conservative calibrated-video room/FloorPlan path complete; current native MP4s remain sidecar-blocked.
- **2026-09-09** — T7f calibrated sidecar-backed sparse metric triangulation and diagnostic floor/wall candidates complete; current Camera MP4s remain uncalibrated.
- **2026-09-09** — T8b photo overlap graph complete; all three current rooms are disconnected and have no cross-room connector candidate, so reshoot precedes SfM.
- **2026-09-09** — T7e strict metric pose-sidecar validation and exact frame/time segment alignment complete; current native MP4s remain unitless.
- **2026-09-09** — T7d scale-free relative video poses and explicit local segment breaks/restarts complete; T7e metric sidecar validation next.
- **2026-09-09** — T7c ORB/geometric trackability gate complete on both real videos; T7d relative trajectory next.
- **2026-09-09** — T7b multi-video identity and explicit display rotation complete; T7c feature diagnostics next.
- **2026-09-09** — T6b3 raw Record3D partial FloorPlan JSON/SVG complete; T6 evidence hardening waits on capture, T7b next.
- **2026-09-09** — T6b2 Record3D horizontal and Manhattan wall candidates complete; T6b3 openings/IR conversion next.
- **2026-09-09** — T6b1 real Record3D metric world clouds complete; T6b2 plane extraction next.
- **2026-09-09** — T6a real Record3D archive/LZFSE decode and integrity validation complete; T6b plane extraction next.
- **2026-09-09** — T20b compliance matrix structure locked; remaining evidence is capture-dependent.
- **2026-09-09** — T17a Route 2 operator card and loader-checked per-tier handoff templates complete; walk-in measurements remain T3-blocked.
- **2026-09-09** — T20a clean-environment README path and one-command synthetic reproduction verified; real bundle remains T3-blocked.
- **2026-09-09** — T10 engineering report draft complete; real benchmark tables remain capture-blocked.
- **2026-09-09** — T19 completed: predicted fallback-yield fail→pass fix shipped with pinned before/after artifacts and readable diff.
- **2026-09-09** — T19a declaration and checksum-locked before bundle frozen at commit `523ceea`; fix deliberately pending.
- **2026-09-09** — T8a per-room photo ingest and honest metric boundary complete.
- **2026-09-08** — T9 shared-wall owner-pose fix (20 cm gap actually closes) + T7 video ingest; 45 tests pass.
- **2026-09-09** — T9 plane-anchored drift correction first land; 42 tests; full Xcode unavailable.
- **2026-09-08** — T16 live OpenAI tool calling + offline fallback complete; live synthetic smoke and 34 tests pass.
- **2026-09-08** — T15 JSON/SVG artifact pair complete; synthetic visual QA and 30 tests pass.
- **2026-09-08** — T6 RoomPlan JSON path works; raw Record3D/USDZ blocked on T3; 27 tests pass.
- **2026-09-08** — T14 official-gate eval CLI complete; 20 tests pass.
- **2026-09-08** — T13 modular CLI and job contract complete; 12 tests pass.
- **2026-09-08** — T12 FloorPlan IR v0.2 frozen; 8 schema tests pass.
- **2026-09-08** — Agent layer required (tool calling / public LLM API + fallback).
- **2026-09-08** — Max-score retarget. Cut list deferred to tomorrow night.
- **2026-09-08** — iPhone 17 Pro has TOF LiDAR.
- **2026-09-08** — Official prompt ingested.
- **2026-09-07** — First orchestration pass.
