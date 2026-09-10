# Handoff

The current agent overwrites the **Current handoff** section at the end of every session. Keep older sessions as short bullets under **History**.

---

## Current handoff

**Date:** 2026-09-10
**Branch:** `main`
**Mode:** Max-score Round 2. **Agent + tools required** (Applied AI). Geometry still classical.

### What changed this session

- Confirmed the repository cleanup is already committed in `a67f861` and
  `7c7884a`.
- Fixed `scripts/install-cozmo-capture.sh --dry-run` so it prints the build and
  install plan without querying `xcrun devicectl` or waiting for an iPhone.
- Updated the submission writing to distinguish successful delivery checks from
  measured accuracy. Better results require higher-overlap stills, a slower and
  steadier handheld video sweep, and a stable LiDAR perimeter scan with strong
  surface coverage.
- Improved the generic Record3D outer-wall selector from exact-peak-only to a
  conservative 95%-of-peak support band. This uses capture support only and
  contains no truth, room, or incumbent special case.
- Final Magicplan head-to-head is 9/12 shared dimensions (75%), passing the
  official 70% gate.
- Verification: focused closeout tests pass 9/9; the full suite passes 178/178;
  `make benchmark` exits successfully with `status=complete pending=0`.

### What is true now

- Product: local CLI. Folder or Cozmo Capture ZIP in → JSON + SVG out.
- Scored walk-in is Route 2. Route 1 cable install is documented (~18 s on
  Harsh's phone).
- README covers every official scoring row. The cleanup, automated test suite,
  and final benchmark execution all pass without runner/test failures.
- LiDAR openings exist but **miss the ≤2 cm gate**. Ceiling **misses ≤1.5 cm**.
  Do not add unobserved wall centimetres (my-room 3.70 m plane is supported).
- The 10:21 benchmark reports photo/video pipeline outputs as `failed` and LiDAR
  as `partial`; those are measured capture/accuracy outcomes, not execution
  failures. LiDAR wall median/p95 is 7.5/30 cm, opening median/p95 is 5/10 cm,
  interval calibration passes 19/24, and Magicplan head-to-head passes at 9/12
  (75%).
- T8c still waits on a connected photo graph (2/2/5/3).
- Harsh is not shooting T11 or connector LiDAR.

### Blockers

- Connector LiDAR before any cross-room snap. Do not pair 80 cm bedroom doors
  across 5+ m.
- T8c waits on a connected photo graph (2/2/5/3). Do not loosen gates.

### Next agent should

1. Do not claim opening ≤2 cm, ceiling ≤1.5 cm, photo ±8%, or video ±3% from
   the current benchmark. Head-to-head ≥70% is now supported at 75%.
2. T8c incremental SfM only if a higher-overlap photo graph connects.
3. Improve input quality with slower, steadier handheld capture and more
   overlap; do not loosen evidence gates to force a result.

### Read next (max five)

1. `README.md`
2. `TASKS.md`
3. `docs/compliance-matrix.md`
4. `docs/writeup.md`
5. `.gitignore`

### Exact next command

```bash
git status --short --branch && git log -3 --oneline
```

---

## History

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
