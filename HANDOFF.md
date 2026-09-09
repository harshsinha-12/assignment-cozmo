# Handoff

The current agent overwrites the **Current handoff** section at the end of every session. Keep older sessions as short bullets under **History**.

---

## Current handoff

**Date:** 2026-09-10
**Branch:** `main`
**Mode:** Max-score Round 2. **Agent + tools required** (Applied AI). Geometry still classical.

### What changed this session

- **T18 remainder:** Pooja-room Magicplan inspector still has no Length/Width.
  Encoded **six Manhattan inner walls** from the 2D screenshot (door-notch L)
  scaled to displayed **12.04 m²**: 299.2, 370.2, 142.3, 61.4, 156.9, 431.6 cm.
  Did not invent a rectangle from perimeter+area (negative discriminant).
- Named Magicplan **2026.35.0** from iTunes lookup id 427424432 on 2026-09-10
  (`currentVersionReleaseDate` 2026-09-02). Device Settings were not
  screenshotted. Cloud share links do not expose per-wall labels.
- Ran **`make benchmark`**: `status=complete pending=0`. LiDAR head-to-head
  **5/12 (41.7%)**, fail vs ≥70%. Same refresh: LiDAR walls **12.5 cm median /
  25 cm p95**; interval coverage **19/24 (79.2%)** still passes internally.
  Photo graphs after EXIF remain connector/drawing/my/pooja = **2/2/5/3**.
- Incumbent tests: 2 passed. No commit.

### What is true now

- Product: local CLI. Folder **or Cozmo Capture ZIP** in → JSON + SVG out.
- Route 2 remains the **scored** walk-in. Route 1 cable install is optional
  until timed on Cozmo's phone. Harsh's copy was ~18 s; that is not their phone.
- T18 evidence is denser but the gate **fails**. Quote **5/12**, not the old
  2/2 ceiling-only win and not a pre-rebuild 8/12 against a stale LiDAR JSON.
- Native video: all four clips track and scale; none produce a four-wall room.
  Handheld intervals stay ~22% relative; do not claim ±3%.
- T11 is **not done**. Holdout media is still missing.
- Photo overlap **2/2/5/3 is post-EXIF** from this benchmark run.

### Blockers

- Human T3 remainder: connector LiDAR, measured property placement/opening
  offsets. Magicplan version is recorded as App Store 2026.35.0.
- T21h remaining: time the cable install on **Cozmo's** phone.
- T11 remaining: shoot a new room into `data/private/walkin/`.
- T8c waits on a connected photo graph (still 2/2/5/3).
- T18 ≥70% needs either a better LiDAR prediction or a Magicplan inspector
  export with true per-wall lengths — do not tune incumbent walls to tape.

### Next agent should

1. Keep Route 2 scored. Do not treat Harsh's 18 s as Cozmo's walk-in install.
2. Do not loosen T8b gates; T8c still blocked on 2/2/5/3.
3. Do not claim video ±3% until reconstructed walls exist and tape eval passes.
4. T18 is measured and red: 5/12. Next T18 leverage is LiDAR accuracy / a
   Magicplan room-inspector screenshot with L×W for pooja, not invented walls.

### Read next (max five)

1. `TASKS.md`
2. `data/private/benchmark-incumbent/raw/magicplan-version-here/notes.txt`
3. `out/benchmark/lidar/eval.json`
4. `out/benchmark/benchmark-summary.md`
5. `docs/eval-and-accuracy.md`

### Exact next command

```bash
open out/benchmark/lidar/eval.json
```

---

## History

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
