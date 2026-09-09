# Handoff

The current agent overwrites the **Current handoff** section at the end of every session. Keep older sessions as short bullets under **History**.

---

## Current handoff

**Date:** 2026-09-08  
**Branch:** `main`  
**Mode:** Max-score Round 2. **Agent + tools required** (Applied AI). Geometry still classical.

### What changed this session

- Finished **T9** for real: shared walls were inheriting the neighbor room’s SE(2), so an injected 20 cm door gap stayed 20 cm. Walls now move with their **first listed owner**; `a_east` stays put, `b_west` snaps, gap → 0.
- Pytest/CLI on the RoomPlan fixture stay `partial` when `COZMO_AGENT_MODE=fallback` (`agent_fallback`). Geometry-only stitch documents are `ok`. Tests no longer require `status==ok` / exit 0 on the enriched path.
- Started **T7 ingest** without private captures: OpenCV samples generated MP4s at ~2 Hz, detects `poses.json`, and refuses uncalibrated centimetres (`unsupported_tier` after a successful sample). Layout: `docs/formats/video-job.md`.

### What is true now

- Product: local CLI. Folder in → JSON + SVG out. No Redis, no our servers.
- Plane-anchored stitch + regenerable `floorplan.ablation-off.json` work on the two-room RoomPlan fixture. Drift gate passes when that ablation is supplied.
- Video jobs with a real/synthetic MP4 are ingested (frame count in the warning) but do **not** emit centimetres yet.
- Photos still `unsupported_tier`. Raw Record3D/USDZ still structured-fail.
- 45 tests pass. `ruff check src tests`, compileall, `git diff --check` pass. No commit (user did not ask).

### Blockers

- Human T3 capture (photos, video, LiDAR, tape GT, Polycam/magicplan). Drop files under gitignored `data/private/` using `data/README.md`.
- Raw Record3D `.r3d`/metadata/depth for Route 2 LiDAR.
- T21: full Xcode.app (this machine has Command Line Tools only).
- Metric video VO and photo SfM need the actual media.

### Next agent should

1. If T3 files are present: implement metric **T7 VO** and/or **T8 photo** reconstruction against them.
2. If T3 is still empty: **T8 photo ingest** (mirror video: per-room JPEGs, overlap/count checks, no invented cm) **or** freeze **T19** fix-loop before.
3. Do not run T21 without Xcode.app.

### Read next (max five)

1. `TASKS.md`
2. `docs/formats/video-job.md`
3. `docs/capture-protocol.md`
4. `data/README.md`
5. `docs/code-map.md`

### Exact next command

```text
If data/private/ still empty: implement T8 photo-folder ingest with generated JPEGs in tests (no invented centimetres), same honesty bar as T7 video ingest.
If a walkthrough exists: start metric T7 VO from sampled frames + optional poses.json.
```

---

## History

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
