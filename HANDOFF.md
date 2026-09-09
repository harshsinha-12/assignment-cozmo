# Handoff

The current agent overwrites the **Current handoff** section at the end of every session. Keep older sessions as short bullets under **History**.

---

## Current handoff

**Date:** 2026-09-09
**Branch:** `main`
**Mode:** Max-score Round 2. **Agent + tools required** (Applied AI). Geometry still classical.

### What changed this session

- Completed **T6a**, the real Record3D archive/decode validation stage.
- Added focused archive I/O, LZFSE utility, validation config/algorithm, tests, format docs, and dependency declarations.
- Filled the three private manifests and ran all three uploaded `.r3d` files through the production LiDAR boundary.
- Inventoried the partial photos/video upload and recorded the remaining capture gaps without inventing accuracy.

### What is true now

- Product: local CLI. Folder in → JSON + SVG out. No Redis, no our servers.
- Plane-anchored stitch + regenerable `floorplan.ablation-off.json` work on the two-room RoomPlan fixture. Drift gate passes when that ablation is supplied.
- Video jobs with a real/synthetic MP4 are ingested (frame count in the warning) but do **not** emit centimetres yet.
- Photo jobs validate one folder per room, 2–8 decodable images per folder, and stable room/image metadata. They intentionally remain `unsupported_tier` until metric reconstruction exists.
- Raw Record3D `.r3d` ZIPs now validate metadata and matched frame modalities and decode sampled LZFSE depth/confidence. They still structured-fail before geometry until T6b plane extraction.
- T19 before is pinned to `523ceea`; the shipped code is pinned to `68acdf6`. The complete bundle is under `data/fix-loop/`.
- The after run exits 0. Its eval still exits 3 because unrelated repeatability/incumbent evidence is missing, while the selected `pipeline_yield` gate passes.
- The private upload contains three room LiDAR scans, 23 photos (drawing=7, my-room=8, pooja=8), and two 720p videos. The photos have no EXIF after WhatsApp transfer; both videos carry a -90° display transform. Their manifests now match the loader contract.
- The three LiDAR captures contain 4,045, 4,057, and 4,235 complete RGB-D frames; representative-frame valid-depth fractions are 87.44%, 85.38%, and 97.23%.
- All 68 tests, Ruff, compileall, synthetic reproduction, touched-file formatting, and diff checks pass. Accuracy and walk-in usability remain unmeasured. No commit was made.
- T10 is structurally drafted but remains `doing` until real LiDAR/video/photo, repeatability, incumbent, calibration, and timing evidence replaces the pending cells.

### Blockers

- Human T3 remainder: drawing-room video, connector/hallway in all tiers, repeat capture, tape/laser GT, two staged damage classes/evidence, and Polycam/magicplan output for two rooms.
- T6b raw Record3D point-cloud fusion and plane extraction.
- T21: full Xcode.app (this machine has Command Line Tools only).
- Metric video VO and photo SfM/adjacency/interval calibration need the actual media.

### Next agent should

1. Implement **T6b**: transform sampled metric depth through per-frame intrinsics/poses, fit a single-room floor and Manhattan walls, and emit diagnostic artifacts before FloorPlan conversion.
2. Then harden T7 for multiple videos and display rotation, or begin T8 SfM against the uploaded photos.
3. Keep collecting the missing T3 evidence in parallel; do not score accuracy without tape truth.

### Read next (max five)

1. `TASKS.md`
2. `docs/formats/record3d.md`
3. `src/cozmo_floorplan/io/record3d.py`
4. `src/cozmo_floorplan/recon/record3d_validation.py`
5. `docs/capture-protocol.md`

### Exact next command

```text
PYTHONPATH=src COZMO_AGENT_MODE=fallback python3 -m cozmo_floorplan run data/private/benchmark-lidar --out out/private-lidar
```

---

## History

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
