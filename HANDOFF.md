# Handoff

The current agent overwrites the **Current handoff** section at the end of every session. Keep older sessions as short bullets under **History**.

---

## Current handoff

**Date:** 2026-09-09
**Branch:** `main`
**Mode:** Max-score Round 2. **Agent + tools required** (Applied AI). Geometry still classical.

### What changed this session

- Completed **T19a**: froze the fix-loop before bundle without shipping the fix.
- The target is `pipeline_yield=fail`: explicit deterministic fallback completes claims but downgrades the prediction to `partial`.
- Added the one-page declaration, exact prediction, pinned source commit, baseline FloorPlan/SVG/ablation/eval, SHA-256 manifest, isolated-worktree reproduction instructions, verifier, and tamper tests.
- Recorded every new file’s responsibility in `docs/code-map.md`.

### What is true now

- Product: local CLI. Folder in → JSON + SVG out. No Redis, no our servers.
- Plane-anchored stitch + regenerable `floorplan.ablation-off.json` work on the two-room RoomPlan fixture. Drift gate passes when that ablation is supplied.
- Video jobs with a real/synthetic MP4 are ingested (frame count in the warning) but do **not** emit centimetres yet.
- Photo jobs validate one folder per room, 2–8 decodable images per folder, and stable room/image metadata. They intentionally remain `unsupported_tier` until metric reconstruction exists.
- Raw Record3D/USDZ still structured-fail.
- T19a before is immutable evidence from commit `523ceea`; its run exits 2 and eval exits 3 by design. The fix is not yet implemented.
- Bundle verification, all 52 tests, `ruff check .`, compileall, and diff checks pass. No commit was made.

### Blockers

- Human T3 capture (photos, video, LiDAR, tape GT, Polycam/magicplan). Drop files under gitignored `data/private/` using `data/README.md`.
- Raw Record3D `.r3d`/metadata/depth for Route 2 LiDAR.
- T21: full Xcode.app (this machine has Command Line Tools only).
- Metric video VO and photo SfM/adjacency/interval calibration need the actual media.

### Next agent should

1. Execute **T19b**: implement only the declared fallback-status fix, then generate `after/` and a readable diff.
2. If T3 files are present: implement metric **T7 VO** and/or **T8 photo** reconstruction against them.
3. Do not run T21 without Xcode.app.

### Read next (max five)

1. `TASKS.md`
2. `docs/fix-loop.md`
3. `data/fix-loop/manifest.json`
4. `src/cozmo_floorplan/agent/orchestrator.py`
5. `docs/code-map.md`

### Exact next command

```text
Execute exactly T19b: preserve data/fix-loop/before, implement the declared explicit-fallback status fix, generate data/fix-loop/after, update the manifest, and add a readable diff.
```

---

## History

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
