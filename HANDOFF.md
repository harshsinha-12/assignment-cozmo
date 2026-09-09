# Handoff

The current agent overwrites the **Current handoff** section at the end of every session. Keep older sessions as short bullets under **History**.

---

## Current handoff

**Date:** 2026-09-09
**Branch:** `main`
**Mode:** Max-score Round 2. **Agent + tools required** (Applied AI). Geometry still classical.

### What changed this session

- Completed the media-independent **T17a Route 2 protocol handoff**.
- Added copyable photos/video/LiDAR job templates under `data/templates/`; a new contract test loads them through the production job loader and checks tier separation.
- Reworked `docs/capture-route.md` into a 469-word operator card and aligned `data/README.md`, the compliance matrix, and device matrix.
- Made the runtime boundary explicit: RoomPlan JSON reconstructs today; raw Record3D/USDZ must be preserved but is not yet runnable.

### What is true now

- Product: local CLI. Folder in → JSON + SVG out. No Redis, no our servers.
- Plane-anchored stitch + regenerable `floorplan.ablation-off.json` work on the two-room RoomPlan fixture. Drift gate passes when that ablation is supplied.
- Video jobs with a real/synthetic MP4 are ingested (frame count in the warning) but do **not** emit centimetres yet.
- Photo jobs validate one folder per room, 2–8 decodable images per folder, and stable room/image metadata. They intentionally remain `unsupported_tier` until metric reconstruction exists.
- Raw Record3D/USDZ still structured-fail.
- T19 before is pinned to `523ceea`; the shipped code is pinned to `68acdf6`. The complete bundle is under `data/fix-loop/`.
- The after run exits 0. Its eval still exits 3 because unrelated repeatability/incumbent evidence is missing, while the selected `pipeline_yield` gate passes.
- The Route 2 manifests now exist and match the loader contract. Accuracy and walk-in usability remain unmeasured until T3.
- `make reproduce-synthetic`, all 63 tests, `ruff check .`, compileall, fix-loop verification, and diff checks pass.
- T10 is structurally drafted but remains `doing` until real LiDAR/video/photo, repeatability, incumbent, calibration, and timing evidence replaces the pending cells.

### Blockers

- Human T3 capture (photos, video, LiDAR, tape GT, Polycam/magicplan). Drop files under gitignored `data/private/` using `data/README.md`.
- Raw Record3D `.r3d`/metadata/depth for Route 2 LiDAR.
- T21: full Xcode.app (this machine has Command Line Tools only).
- Metric video VO and photo SfM/adjacency/interval calibration need the actual media.

### Next agent should

1. Capture **T3** and inventory the resulting photos/video/LiDAR/tape/incumbent files before changing adapters.
2. With captures present, implement metric **T7 VO** and/or **T8 photo** reconstruction against them; extend `make reproduce-synthetic` into the real bundle only after raw inputs exist.
3. Without captures, no metric or remaining T17 stage is unblocked. Do not run T21 without Xcode.app.

### Read next (max five)

1. `TASKS.md`
2. `docs/capture-route.md`
3. `data/templates/README.md`
4. `data/README.md`
5. `docs/capture-protocol.md`

### Exact next command

```text
cp -R data/templates/photos data/private/benchmark-photos  # repeat for video/lidar, replace manifest placeholders, then capture T3
```

---

## History

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
