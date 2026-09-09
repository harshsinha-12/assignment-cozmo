# Handoff

The current agent overwrites the **Current handoff** section at the end of every session. Keep older sessions as short bullets under **History**.

---

## Current handoff

**Date:** 2026-09-09
**Branch:** `main`
**Mode:** Max-score Round 2. **Agent + tools required** (Applied AI). Geometry still classical.

### What changed this session

- Completed **T6b3**, converting real Record3D plane candidates into partial FloorPlan JSON/SVG geometry.
- Added separate segment geometry, opening detection, Record3D measurement, output conversion, configuration, and focused test modules.
- Opening candidates require sparse lower/middle wall occupancy plus surviving lintel or sill evidence; solid synthetic walls produce no phantoms.
- Updated the code map, format/device/capture docs, compliance row, ADR, roadmap, README, and task queue. No commit was made.

### What is true now

- Product: local CLI. Folder in → JSON + SVG out. No Redis, no our servers.
- Plane-anchored stitch + regenerable `floorplan.ablation-off.json` work on the two-room RoomPlan fixture. Drift gate passes when that ablation is supplied.
- Video jobs with a real/synthetic MP4 are ingested (frame count in the warning) but do **not** emit centimetres yet.
- Photo jobs validate one folder per room, 2–8 decodable images per folder, and stable room/image metadata. They intentionally remain `unsupported_tier` until metric reconstruction exists.
- Raw Record3D `.r3d` ZIPs now emit schema-valid metric rooms, walls, ceiling heights, areas, and evidence-gated openings. Output stays `partial` because intervals and cross-archive registration are not yet measured.
- T19 before is pinned to `523ceea`; the shipped code is pinned to `68acdf6`. The complete bundle is under `data/fix-loop/`.
- The after run exits 0. Its eval still exits 3 because unrelated repeatability/incumbent evidence is missing, while the selected `pipeline_yield` gate passes.
- The private upload contains three room LiDAR scans, 23 photos (drawing=7, my-room=8, pooja=8), and two 720p videos. The photos have no EXIF after WhatsApp transfer; both videos carry a -90° display transform. Their manifests now match the loader contract.
- The three clouds use 61 frames each and contain 252,694 drawing-room, 224,435 my-room, and 260,653 pooja-room 2.5 cm voxel centroids. The complete private LiDAR command takes about 8 s locally.
- The private output contains 3 rooms, 12 walls, and 4 opening candidates: one in my-room and three in pooja-room. The SVG was rendered and visually inspected. These candidates are not tape-backed accuracy results.
- Separate archives preserve their exported world-pose coordinates, but no shared session/door association is invented. T9 records an empty ablation and one disconnected warning rather than claiming correction.
- All 80 tests, Ruff, touched-file formatting, compileall, synthetic reproduction, private three-scan JSON/SVG smoke, and diff checks pass. Exit 2 is intentional because the result is honestly `partial`.
- T10 is structurally drafted but remains `doing` until real LiDAR/video/photo, repeatability, incumbent, calibration, and timing evidence replaces the pending cells.

### Blockers

- Human T3 remainder: drawing-room video, connector/hallway in all tiers, repeat capture, tape/laser GT, two staged damage classes/evidence, and Polycam/magicplan output for two rooms.
- T6 calibration/repeatability/shared-opening hardening remains blocked on the human capture remainder.
- T21: full Xcode.app (this machine has Command Line Tools only).
- Metric video VO and photo SfM/adjacency/interval calibration need the actual media.

### Next agent should

1. Implement **T7b**: handle multiple room walkthroughs and their -90-degree display rotation before feature/VO work; retain per-video room identity and diagnostics.
2. Then begin metric video tracking without claiming scale from RGB alone, or start T8 SfM against the uploaded photos.
3. Keep collecting the missing T3 evidence in parallel; do not score accuracy without tape truth.

### Read next (max five)

1. `TASKS.md`
2. `docs/formats/video-job.md`
3. `src/cozmo_floorplan/io/video.py`
4. `src/cozmo_floorplan/recon/video.py`
5. `src/cozmo_floorplan/recon/video_config.py`

### Exact next command

```text
PYTHONPATH=src COZMO_AGENT_MODE=fallback python3 -m cozmo_floorplan run data/private/benchmark-video --out out/private-video
```

---

## History

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
