# Handoff

The current agent overwrites the **Current handoff** section at the end of every session. Keep older sessions as short bullets under **History**.

---

## Current handoff

**Date:** 2026-09-10
**Branch:** `main`
**Mode:** Max-score Round 2. **Agent + tools required** (Applied AI). Geometry still classical.

### What changed this session

- **T21h timing + Xcode open:** Harsh timed the cable install copy onto his
  iPhone at **~18 s**. The walk-in card and installer now also document
  `open -a Xcode ios/CozmoCapture/CozmoCapture.xcodeproj` (repo-relative;
  Cursor will not open it). `--open-xcode` / `make open-capture-app` open
  the project only. Route 2 stays scored until Cozmo's phone is timed.
- T11a walk-in harness from earlier today is unchanged: templates exist,
  holdout media is still missing.

### What is true now

- Product: local CLI. Folder **or Cozmo Capture ZIP** in → JSON + SVG out.
- Route 2 remains the **scored** walk-in. Route 1 cable install is optional
  (`docs/capture-route-route1.md`) until timed on Cozmo's phone.
- Harsh's T21h numbers: signed iPhoneOS build 46 s, device copy ~18 s.
  Developer Mode was already on.
- T11 is **not done**. The rehearsal folder exists; there is no holdout capture
  yet. Do not drop benchmark rooms into `data/private/walkin/`.
- First Route 1 job is still one room (`Room 1`). Do not mix it with Route 2
  Record3D or the walk-in folder.

### Blockers

- Human T3 remainder, if available: exact Magicplan version, connector LiDAR,
  and measured property placement/opening supporting walls and offsets.
- T21h remaining: time `./scripts/install-cozmo-capture.sh` on **Cozmo's**
  phone. Harsh's ~18 s is not that switch.
- T11 remaining: shoot a new room into `data/private/walkin/`, then
  `make walkin`.
- T8c metric SfM remains blocked until the **post-EXIF** overlap graph is
  measured. Do not loosen overlap gates.

### Next agent should

1. Keep Route 2 scored. Do not treat Harsh's 18 s as Cozmo's walk-in install.
2. If holdout media arrives: `make walkin` and record elapsed_s.
3. Run tests with `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1`. Then remasure photo
   overlap / native video and `make benchmark` for T18.

### Read next (max five)

1. `TASKS.md`
2. `docs/capture-route-route1.md`
3. `docs/t21h-install-rehearsal.md`
4. `docs/capture-route.md`
5. `docs/walk-in.md`

### Exact next command

```bash
./scripts/install-cozmo-capture.sh --dry-run
```

---

## History

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
