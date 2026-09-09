# Handoff

The current agent overwrites the **Current handoff** section at the end of every session. Keep older sessions as short bullets under **History**.

---

## Current handoff

**Date:** 2026-09-10
**Branch:** `main`
**Mode:** Max-score Round 2. **Agent + tools required** (Applied AI). Geometry still classical.

### What changed this session

- **T8b3 (code, unverified on real photos):** OpenCV was reading iPhone JPEGs
  without EXIF orientation. Several stills are orientation 6 (portrait
  stored as landscape). Ingest and feature extraction now use Pillow
  `ImageOps.exif_transpose` via `load_display_oriented_bgr`. Tests exist in
  `tests/test_photos.py` and `tests/test_photo_overlap.py`. The old real-graph
  counts 2/2/5/3 are **pre-EXIF** and must be remeasured.
- **T7h (code, unverified on real MP4s):** Trajectory recovery can skip one
  failed adjacent pair by estimating a real i→i+2 pose (`maximum_edge_span=2`,
  step length = span). Adjacent-only break behaviour is locked with
  `maximum_edge_span=1`. Native Camera video with no ARKit sidecar can build an
  in-memory y-up unit sidecar, triangulate, and scale from a disclosed 1.45 m
  handheld-height prior if a floor band exists (`scale_source=imu_vo`).
  Independent native rooms are bookkeeping-placed, not registered. Wider
  intervals: `HANDHELD_VIDEO_OUTPUT`.
- **T18 (evidence densified, benchmark not re-run):** Magicplan my-room
  displayed 4.20×3.29 m is now four AABB walls. Pooja-room still has no honest
  wall lengths. Head-to-head now also scores floor area. Exact app version is
  still unrecorded.
- Tests were written (`test_video_native_scale.py`, skip-span trajectory,
  independent imu_vo FloorPlan, incumbent skip-if-missing). Focused suite:
  **53 passed** (`PYTEST_DISABLE_PLUGIN_AUTOLOAD=1`). Full `make test` and
  `make benchmark` were not run. No commit.
- Docs not yet patched: `docs/formats/photo-job.md`, `video-job.md`,
  `docs/capture-tiers.md`, `docs/decisions.md`, `docs/code-map.md`.

### What is true now

- Product: local CLI. Folder **or Cozmo Capture ZIP** in → JSON + SVG out.
- Route 1 capture on Harsh's phone works. Route 2 remains the **scored** walk-in
  route until a timed under-10-minute install is demonstrated on **their**
  (Cozmo) phone, not only ours (**T21h**).
- First Route 1 job is one room (`Room 1`), not a stitched property. Do not mix
  it with Route 2 Record3D under `data/private/benchmark-lidar/`.
- Remaining T21: T21h route decision; T21d Photos/Video modes if the on-phone
  build lacks the LiDAR/Photos/Video picker (rebuild/reinstall).
- The active benchmark has 8/8/8/5 decodable primary photos, four primary
  videos, an 8-photo `my-room` repeat, a repeat `my-room` video, three room
  Record3D scans, normalized tape measurements, and two-class damage evidence.
- Magicplan covers `my-room` and `pooja-room`. My-room now has four AABB walls
  from displayed length/width (420×329 cm). Pooja-room still has no individual
  walls. Exact app version is still unrecorded. Head-to-head now includes
  floor area as well as walls/openings/ceilings; do not quote the old 2/2
  ceiling-only win until `make benchmark` is re-run.
- Primary/repeat photos and video run but fail their current geometry gates.
  LiDAR emits a partial FloorPlan.
- LiDAR's remaining measured failures include 30 cm on both `my-room` long
  walls, 5.41 cm maximum ceiling error, unscored/unmatched opening predictions,
  and disconnected room scans. These are not hidden by the evaluator fix.
- LiDAR interval calibration passes 16/18 on the current benchmark. Two
  `my-room` long-wall truths remain outside the support-conditioned intervals;
  repeat/holdout validation is still unavailable.
- Last full `make benchmark` still reports the **pre-T8b3 / pre-T18** state:
  photo graphs 2/2/5/3 components, head-to-head 2/2 shared ceilings. Those
  numbers are stale relative to the new code/evidence.
- Native video still has no ARKit sidecars. The handheld-height path is
  implemented but has not been proven on the four private MP4s. If floor
  support is missing it must stay `unsupported_tier` / `native_scale=no-floor`.

### Blockers

- Human T3 remainder, if available: exact Magicplan version, connector LiDAR,
  and measured property placement/opening supporting walls and offsets.
- T21h: timed under-10-minute install on Cozmo's walk-in phone. Harsh's
  T21g install is evidence Route 1 runs, not an automatic scored-route switch.
  TestFlight needs a paid Developer Program enrollment (not the current
  Personal Team).
- T8c metric SfM remains blocked until the **post-EXIF** overlap graph is
  measured. Pre-EXIF isolated files were my-room `02-wall-a.JPG` and
  `08-damage-and-overlap.JPG`, plus pooja-room `03-wall-b.JPG` and
  `08-ceiling-wall.JPG`. Several of those are EXIF orientation 6. Do not
  loosen overlap gates. Do not start SfM on disconnected rooms.

### Next agent should

1. Run tests with `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1` (venv pytest if present).
   Then re-run real photo overlap and native video smoke; update photo-job /
   video-job diagnostics from those numbers, not the old 2/2/5/3 counts.
2. Patch `docs/code-map.md` (`video_native_scale.py`, EXIF loader),
   `docs/formats/photo-job.md`, `docs/formats/video-job.md`, and an ADR for
   skip-span (real i→i+2 pose, not interpolating a failed adjacent edge).
3. Re-run `make benchmark` so T18 head-to-head includes my-room AABB walls and
   areas. Still do not invent pooja-room walls or a Magicplan version.
4. T21h remains separate: Route 2 scored until timed <10 min install on
   Cozmo's phone. Do not mix Route 1 RoomPlan with Route 2 Record3D.

### Read next (max five)

1. `TASKS.md`
2. `src/cozmo_floorplan/recon/video_native_scale.py`
3. `src/cozmo_floorplan/utils/images.py`
4. `data/private/benchmark-incumbent/floorplan.json`
5. `tests/test_video_native_scale.py`

### Exact next command

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m pytest -q
```

---

## History

- **2026-09-10** — T8 EXIF orientation, T7 skip-span + handheld-height native scale, T18 my-room AABB walls + area in head-to-head. Code landed; tests/docs/benchmark not finished.
- **2026-09-10** — T21g: Harsh installed Cozmo Capture; first Route 1 job ingested (`status=partial`, open wall loop).
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
