# Handoff

The current agent overwrites the **Current handoff** section at the end of every session. Keep older sessions as short bullets under **History**.

---

## Current handoff

**Date:** 2026-09-10
**Branch:** `main`
**Mode:** Max-score Round 2. **Agent + tools required** (Applied AI). Geometry still classical.

### What changed this session

- Wired Harsh's Cozmo Capture screenshots into README **These paths ran**.
  Hero room mesh is `docs/evidence/app-lidar-room.jpg` (IMG_0151). Gallery
  also has scanning, Photos, Video, and Share ZIP next to the CLI SVG.
- Full-res `IMG_*.PNG` and `docs/evidence/lidar/*.r3d` are gitignored.

### What is true now

- Product: local CLI. Folder or Cozmo Capture ZIP in → JSON + SVG out.
- Scored walk-in is Route 2. Route 1 cable install is documented (~18 s on
  Harsh's phone).
- LiDAR openings exist but **miss the ≤2 cm gate**. Ceiling **misses ≤1.5 cm**.
  Do not add unobserved wall centimetres (my-room 3.70 m plane is supported).
- T10/T17/T20 docs were filled earlier this day from `make benchmark`
  (walls 12.5/25 cm, head-to-head 5/12). That run predates this detector
  change; wall centres were not retuned. Opening-width median 10 cm still
  matches 5/10/15.
- T8c still waits on a connected photo graph (2/2/5/3).
- Harsh is not shooting T11 or connector LiDAR.

### Blockers

- Connector LiDAR before any cross-room snap. Do not pair 80 cm bedroom doors
  across 5+ m.
- T8c waits on a connected photo graph (2/2/5/3). Do not loosen gates.
- T18 5/12 stays unless LiDAR geometry improves; do not retune Magicplan walls.

### Next agent should

1. Do not enable clutter-band outer walls on this capture.
2. Do not claim opening ≤2 cm or ceiling ≤1.5 cm from these numbers.
3. Re-run `make benchmark` before quoting a new official wall median.
4. T8c incremental SfM only if a room graph connects; otherwise stop.

### Read next (max five)

1. `TASKS.md`
2. `docs/formats/record3d.md`
3. `src/cozmo_floorplan/recon/record3d_openings.py`
4. `src/cozmo_floorplan/recon/record3d_register.py`
5. `src/cozmo_floorplan/recon/record3d_planes.py`

### Exact next command

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONPATH=src python3 -m pytest -q tests/test_record3d_openings.py tests/test_record3d_register.py tests/test_record3d_floorplan.py tests/test_record3d_planes.py
```

---

## History

- **2026-09-10** — README Route 1 gallery: app screenshots (room mesh IMG_0151) + CLI SVG/JSON.
- **2026-09-10** — T6e: openings 5/10/15 cm vs tape; shared-world pairing empty (nearest 5.08 m); walls/ceiling bias left honest.
- **2026-09-10** — T10/T17/T20: measured writeup/device-matrix/compliance + submission README (deliverables, run, app install, defense test).
- **2026-09-10** — T18 remainder: pooja traced Manhattan walls + Magicplan 2026.35.0; `make benchmark` LiDAR head-to-head 5/12 (41.7%).
- **2026-09-10** — T7 remainder: native MP4 smoke 4/4 scaled 0/4 rooms; display-K fix; openings/stitch coded; ±3% not claimed.
- **2026-09-10** — T21h: Harsh device copy ~18 s; added `open -a Xcode ios/CozmoCapture/CozmoCapture.xcodeproj`.
- **2026-09-10** — T11a: walk-in harness (`make walkin`) for a holdout room; refuses benchmark-room reuse; 2-still crash test; media still pending.
- **2026-09-10** — T21h: cable Personal-Team install card + script; signed iPhoneOS build 46 s; TestFlight declined; Route 2 still scored.
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
