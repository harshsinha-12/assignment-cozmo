# Handoff

The current agent overwrites the **Current handoff** section at the end of every session. Keep older sessions as short bullets under **History**.

---

## Current handoff

**Date:** 2026-09-10
**Branch:** `main`
**Mode:** Max-score Round 2. **Agent + tools required** (Applied AI). Geometry still classical.

### What changed this session

- Added general semantic `.usd`, `.usda`, and `.usdz` LiDAR input. Binary
  crates/packages decode through `usdcat`; named wall/door/window metric meshes
  share the RoomPlan surface-to-IR path. Furniture meshes are ignored.
- Converted the separately supplied `mummy-room` measurements into schema-valid
  holdout truth without exposing them to reconstruction.
- Selected LiDAR walk-in completes with `pending=0`, geometry ready in 0.106 s.
  It remains `partial` and its accuracy gates fail.
- Verification: focused USD/LiDAR/walk-in 21/21; full suite 185/185; Ruff,
  compileall, schema validation, synthetic reproduction, final benchmark, and
  final selected LiDAR walk-in all pass as commands.
- Reviewer-facing README/report now distinguish capture-sensitive photo/video
  failures from execution success and describe the professional recapture path;
  expected gains remain explicitly unmeasured.

### What is true now

- Product: local CLI. Folder or Cozmo Capture ZIP in → JSON + SVG out.
- Scored walk-in is Route 2. Semantic USD/USDZ is now accepted in addition to
  Record3D and RoomPlan JSON.
- Latest benchmark: photos `failed` (disconnected). Video `partial` (drawing
  + pooja rooms, 8 walls, median error 356 cm — ±3% not claimed). LiDAR
  `partial`, walls 7.5/30 cm, openings median 5 cm, head-to-head 9/12 (75%).
- Independent `mummy-room` USD holdout: 16.1 cm one matched wall, 4.17 cm
  closest door, 7 cm ceiling, 48.2% area error. Do not call these passing.

### Blockers

- Connector LiDAR before any cross-room snap.
- Author photo graphs remain disconnected (2/2/5/3). Do not loosen T8b gates.
- LiDAR repeat, photo holdout, and video holdout remain unavailable.

### Next agent should

1. Do not claim the semantic USD holdout passes accuracy; it only proves cold
   format ingest, geometry output, evaluation, and timing.
2. Do not claim photo ±8% or video ±3% from harsh-home-01.
3. Preserve the separation between USD reconstruction and tape truth.

### Read next (max five)

1. `docs/formats/usd-mesh.md`
2. `docs/walk-in.md`
3. `docs/writeup.md`
4. `TASKS.md`
5. `README.md`

### Exact next command

```bash
git status --short --branch && git log -3 --oneline
```

---

## History

- **2026-09-10** — Clarified photo overlap/video stability limitations and professional recapture path without changing measured gate statuses.
- **2026-09-10** — T6g/T11c semantic USD/USDZ ingest + measured mummy-room LiDAR holdout; commands pass, accuracy gates do not.
- **2026-09-10** — T8c photo SfM + video occupancy envelopes; benchmark video failed→partial (8 walls); photos still disconnected; 182 tests.
- **2026-09-10** — Finish-line closeout: cleanup committed, installer dry-run fixed (178/178 tests), final benchmark complete with pending=0; head-to-head 75% pass.
- **2026-09-10** — T20e submission README refresh + local-only capture/IDE/temporary-file cleanup.
- **2026-09-10** — README Route 1 gallery: app screenshots (room mesh IMG_0151) + CLI SVG/JSON.
- **2026-09-10** — T6e: openings 5/10/15 cm vs tape; shared-world pairing empty (nearest 5.08 m); walls/ceiling bias left honest.
- **2026-09-10** — T10/T17/T20: measured writeup/device-matrix/compliance + submission README (deliverables, run, app install, defense test).
- **2026-09-10** — T18 remainder: pooja traced Manhattan walls + Magicplan 2026.35.0; earlier result superseded by the 10:06 final benchmark.
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
