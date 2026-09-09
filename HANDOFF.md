# Handoff

The current agent overwrites the **Current handoff** section at the end of every session. Keep older sessions as short bullets under **History**.

---

## Current handoff

**Date:** 2026-09-09
**Branch:** `main`
**Mode:** Max-score Round 2. **Agent + tools required** (Applied AI). Geometry still classical.

### What changed this session

- Implemented **T21b** multi-room Cozmo Capture: name rooms, keep each
  `CapturedRoom`, merge two or more with Apple `StructureBuilder`, and share one
  portable `roomplan.json` `rooms[]` file.
- Shared wall identifiers get `roomIds`; openings on those walls get
  `connectsRoomIds`. Merge failure can export unmerged rooms instead of
  discarding the session.
- Downloaded the iOS 26.5 simulator runtime. Simulator and unsigned generic
  iPhoneOS builds succeed. XCTest compiled; launching tests on the first-boot
  simulator hung, so on-device RoomPlan is still unproven.
- No commit was made.

### What is true now

- Product: local CLI. Folder in → JSON + SVG out. No Redis, no our servers.
- Route 2 remains the default/scored capture route. T21 Route 1 is parallel and
  must not replace it until a signed device install completes in under 10
  minutes.
- The T21b app names rooms, accumulates sessions, merges with
  `StructureBuilder`, and writes portable `rooms[]` JSON. Simulator and unsigned
  generic iPhoneOS builds succeed. RoomPlan sensing and sharing have not yet
  been exercised on the iPhone.
- Plane-anchored stitch + regenerable `floorplan.ablation-off.json` work on the two-room RoomPlan fixture. Drift gate passes when that ablation is supplied.
- Video jobs ingest every MP4/MOV in stable order, retain source-frame/time identity, qualify relative-VO evidence, recover disconnected unitless pose segments, and strictly validate/align optional metric camera poses. Calibrated v1.2 sidecars can now emit conservative partial rooms/walls after complete surface qualification.
- Photo jobs validate one folder per room, 2–8 decodable images, stable identity, and all-pairs geometric overlap. Disconnected evidence now returns actionable `insufficient_overlap` before SfM.
- Raw Record3D `.r3d` ZIPs now emit schema-valid metric rooms, walls, ceiling heights, areas, and evidence-gated openings. Output stays `partial` because intervals and cross-archive registration are not yet measured.
- T19 before is pinned to `523ceea`; the shipped code is pinned to `68acdf6`. The complete bundle is under `data/fix-loop/`.
- The after run exits 0. Its eval still exits 3 because unrelated repeatability/incumbent evidence is missing, while the selected `pipeline_yield` gate passes.
- The active private upload contains only the three earlier room LiDAR scans.
  Photo/video job folders are intentionally empty for original-quality reshoots.
  Repeat template manifests are not active until their media is copied.
- OpenCV reports both video transforms as 90° clockwise. Explicit normalization yields 720×1280 RGB: my-room 138 samples / 68.56 s, pooja-room 148 samples / 73.91 s at about 2 Hz. The second video is no longer ignored.
- Both archived videos passed the internal 35% eligible-pair threshold: my-room 23/60 with median 1,166 keypoints, 262 matches, 178 F-inliers, 1.15 px parallax, 23.5% coverage; pooja-room 27/60 with 1,188, 257, 190, 1.23 px, 20.6%. These are historical trackability diagnostics, not metric accuracy.
- With at most 90 selected frames, my-room recovers 21/89 relative-pose edges in 10 local segments and pooja-room recovers 17/89 in 9. The 576 px focal length is an unvalidated image-size prior; unit steps and separate identity anchors are not metric or globally aligned.
- Metric pose sidecar v1 requires metres, camera-to-world, right-handed y-up, video-start timestamps, increasing source-frame/time keys, finite positions, and unit XYZW quaternions. Segment alignment requires ≥3 exact frame/time matches, trajectory rank ≥2, and ≤0.15 m RMSE.
- Metric pose sidecar v1.1 adds display-oriented calibrated pinhole intrinsics
  and `x_right_y_down_z_forward` axes. v1.2 adds an ARKit/ARCore scale source and
  shared `world_frame_id`. Accepted aligned segments can yield filtered sparse
  points; complete camera-bracketing room surfaces can then enter the shared
  IR. v1.0 cannot authorize triangulation.
- The archived MP4s contained no sidecars, so both reported `metric_alignment=not-available`; no scale was inferred.
- The archived photo graphs failed connectivity: drawing-room had 3/21 eligible edges and 4 components, my-room 2/28 and 6, and pooja-room 2/28 and 6. No cross-room connector candidate passed. The new active folders are empty.
- The three clouds use 61 frames each and contain 252,694 drawing-room, 224,435 my-room, and 260,653 pooja-room 2.5 cm voxel centroids. The complete private LiDAR command takes about 8 s locally.
- The private output contains 3 rooms, 12 walls, and 4 opening candidates: one in my-room and three in pooja-room. The SVG was rendered and visually inspected. These candidates are not tape-backed accuracy results.
- Separate archives preserve their exported world-pose coordinates, but no shared session/door association is invented. T9 records an empty ablation and one disconnected warning rather than claiming correction.
- All 117 tests, Ruff, touched-file formatting, compileall, synthetic reproduction, real partial benchmark, private photo/video smokes, and diff checks pass. Photo refusal is intentional and classified `insufficient_overlap`; current uncalibrated video refusal is intentional and classified `unsupported_tier`.
- T10 is structurally drafted but remains `doing` until real LiDAR/video/photo, repeatability, incumbent, calibration, and timing evidence replaces the pending cells.
- `make benchmark` now writes per-tier artifacts plus a single JSON/Markdown
  status. The current report is `pending_inputs`: ground truth, repeat LiDAR,
  incumbent, and staged damage observations are missing; LiDAR is `partial`
  while photos/video are structured `failed` on current evidence.

### Blockers

- Human T3 remainder: drawing-room video, connector/hallway in all tiers, repeat capture, tape/laser GT, two staged damage classes/evidence, and Polycam/magicplan output for two rooms.
- T6 calibration/repeatability/shared-opening hardening remains blocked on the human capture remainder.
- T7 room/FloorPlan conversion is implemented synthetically; current captures lack calibrated v1.2 pose sidecars. Video openings, shared-room constraints, interval calibration, and the official ±3% evaluation remain media-dependent.
- T8c metric SfM is blocked on a photo reshoot with overlapping intermediate views and doorway/connector evidence. Do not loosen the evidence thresholds to force the current capture through.
- T21c raw ARKit RGB-D logging, T21g Apple-team signing/device install, a real
  RoomPlan export round-trip through the Python CLI, and the timed under-10-minute
  installation remain.
- Metric video VO and photo SfM/adjacency/interval calibration need the actual media.

### Next agent should

1. Review T21b, then start T21c raw ARKit RGB/depth/confidence/pose logging in
   the iOS project. Do not overlap another agent on the same Xcode files.
2. Harsh: T21g — select an Apple team in Signing & Capabilities, install on the
   iPhone 17 Pro, capture several rooms, and save `roomplan.json` under
   `data/private/route1-roomplan/lidar/`.
3. Follow `mytask.md` for the T3 reshoot; do not start T8c until photo graphs
   connect.

### Read next (max five)

1. `ios/CozmoCapture/README.md`
2. `TASKS.md`
3. `docs/formats/roomplan-json.md`
4. `ios/CozmoCapture/CozmoCapture/Capture/RoomCaptureStore.swift`
5. `mytask.md`

### Exact next command

```bash
xcodebuild \
  -project ios/CozmoCapture/CozmoCapture.xcodeproj \
  -scheme CozmoCapture \
  -destination 'generic/platform=iOS Simulator' \
  CODE_SIGNING_ALLOWED=NO build
```

---

## History

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
