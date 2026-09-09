# Update log

Append-only. Newest entry at the top. This is the cache that stops agents from repeating web research and PDF extraction.

Format:

```text
## YYYY-MM-DD — short title

- Context
- Done
- Learned (facts the next agent should trust)
- Next
```

## 2026-09-10 — T18 remainder: pooja walls, Magicplan 2026.35.0, benchmark

- Context: T18 still lacked pooja-room walls and an exact app version; the last
  quoted 2/2 ceiling win was stale.
- Done: Traced pooja-room.png inner floor, reconstructed the door-notch as a
  Manhattan L (not a convex-hull diagonal), scaled the polygon to displayed
  12.04 m², and wrote six incumbent walls. Recorded Magicplan **2026.35.0**
  from iTunes lookup 427424432 (released 2026-09-02). Ran `make benchmark`
  (`status=complete pending=0`). Incumbent tests: 2 passed.
- Learned: Pooja inspector has no L×W because the room is not a rectangle;
  perimeter+area has a negative discriminant. Cloud share pages do not expose
  dimensions. Head-to-head on the refreshed LiDAR prediction is **5/12
  (41.7%)**, fail vs ≥70%. Same run: walls 12.5 cm median / 25 cm p95;
  calibration 19/24 (79.2%) still passes; photo graphs stay 2/2/5/3 after EXIF.
  App Store version is not a Settings screenshot.
- Next: Do not retune incumbent walls to tape. T18 leverage is LiDAR accuracy
  or a Magicplan room-inspector export. T8c still blocked on 2/2/5/3.

## 2026-09-10 — T7 remainder: native MP4 smoke, openings/stitch, no ±3%

- Context: User asked to smoke the four native MP4s, add openings/stitch, and
  claim ±3% only if geometry holds.
- Done: Ran all four Camera clips. Fixed native sidecar intrinsics to display
  space so triangulation K matches `_scaled_intrinsics`. After that, 4/4
  clips get a floor-supported handheld-height scale; 0/4 pass complete
  floor/ceiling/wall room conversion. Added occupancy openings (Record3D
  profile, no phantoms), shared-world opening pairing for stitch, partial
  FloorPlan emission, and median-path wall bracketing. 25 focused tests pass.
  ±3% not claimed; handheld intervals stay ~22% relative.
- Learned: Feature-space 576 px focal inside a 1080p sidecar was a ~3× K
  error (`native_scale=no-floor` on drawing-room and pooja-room). Only the
  longest VO segment becomes a native sidecar, so most segments are
  `insufficient_exact_frame_time_matches`. Connector 596 vx / drawing 175 /
  my-room 493 / pooja 278. Failures: x-high wall, ceiling, floor, x-high
  wall. Do not loosen those gates. `scale_source` is `known_length` (schema),
  not `imu_vo`.
- Next: Remeasure post-EXIF photo overlap, then `make benchmark` for T18.
  Video rooms need denser segments or a recapture, not invented walls.

## 2026-09-10 — T21h device copy ~18 s + open Xcode

- Context: Harsh timed the cable install on his already-working iPhone and
  asked to add the Xcode open command.
- Done: Recorded ~18 s device copy. Walk-in card, iOS README, installer, and
  `make open-capture-app` now use `open -a Xcode ios/CozmoCapture/CozmoCapture.xcodeproj`
  (repo-relative; Cursor will not). `--open-xcode` opens the project only.
- Learned: Incremental reinstall on a phone with Developer Mode already on is
  far under 10 minutes. That is still not a timed install on Cozmo's phone.
- Next: Keep Route 2 scored until they time the same commands. Do not pay for
  TestFlight.

## 2026-09-10 — T11a walk-in harness for a holdout room

- Context: User asked to work T11 (walk-in rehearsal on a new room, all three
  tiers). T20a–c already shipped, so the blocker was the missing rehearsal
  itself, not packaging. No holdout capture existed; the first Route 1 job is
  still unlabeled `Room 1` and must not be used as the cold room.
- Done: Added `walkin` CLI / `make walkin`, holdout templates, automatic 2-still
  photo subset, forbidden-room collision check, operator card in
  `docs/walk-in.md`, and a Route 2 handoff that runs
  `python -m cozmo_floorplan run` instead of `make benchmark`. Seeded
  `data/private/walkin/`. 10 walk-in tests passed. Current audit:
  `pending_inputs` ×4 (photos, video, LiDAR, tape).
- Learned: The previous operator card would have dumped a defense capture into
  the author's benchmark. Walk-in jobs are ready only when original media
  exists, not when empty templates are copied. Recapturing drawing-room /
  my-room / pooja-room / connector is `invalid_holdout`, exit 2. T11 stays
  `doing` until Harsh shoots a new room.
- Next: Shoot kitchen/guest/bath at all three Route 2 tiers, tape it, then
  `make walkin`. Do not mix with `benchmark-*` or Route 1 RoomPlan.

## 2026-09-10 — T21h cable install, not TestFlight

- Context: User asked to work T21h. The app already runs on Harsh's iPhone.
  A paid Apple Developer Program team ($99) is not available and will not be
  purchased. TestFlight therefore cannot be used.
- Done: One-page Route 1 card (`docs/capture-route-route1.md`), one-command
  installer (`scripts/install-cozmo-capture.sh`), ADR that the official prompt
  accepts a 10-minute cable dev build, and a signed generic iPhoneOS rehearsal
  of **46 s**. Two tests pass. Route 2 remains the scored walk-in. No commit.
- Learned: Personal Team signing works without the $99 fee. Harsh's iPhone
  already has Developer Mode enabled. It was paired but USB-disconnected this
  session (`tunnel=disconnected`), so the `devicectl` copy was not timed. A
  Developer Mode restart on a phone that has never been used for development
  is the abort-to-Route-2 condition.
- Next: Plug in a phone and run `./scripts/install-cozmo-capture.sh`. Switch
  the scored route only if that run is under 10:00 on Cozmo's phone. Otherwise
  keep `docs/capture-route.md`. Do not follow the same-day TestFlight
  enrollment note; that path is unused.

## 2026-09-10 — T7/T8/T18 native video, EXIF photos, denser Magicplan

- Context: User asked to work T7 (no metric poses on native MP4s), T8
  (disconnected photo graphs), and T18 (Magicplan comparison only two
  ceilings). Session was interrupted once; this entry is the landed code.
- Done: Photo ingest/features apply EXIF display orientation. Video trajectories
  may use a real skip-span pose when an adjacent pair fails. Native MP4s can
  attempt a disclosed 1.45 m handheld-height scale (`imu_vo`) after unitless
  triangulation finds a floor. Magicplan my-room 4.20×3.29 m is encoded as
  four AABB walls; head-to-head also compares floor area. Pooja-room walls
  remain absent. Focused tests: 53 passed. Full pytest and `make benchmark`
  were not completed. No commit.
- Learned: `cv2.imread` ignores EXIF; several iPhone stills are orientation 6
  (doorway/through-door vs wall shots). Do not treat pre-EXIF 2/2/5/3
  component counts as current. Skip-span is a measured i→i+2 essential pose
  with step length = span, not interpolation across a rejected edge. Native
  rooms do not share a world frame; overlaying them would be a lie. Magicplan
  pooja-room perimeter+area is not a rectangle (negative discriminant); do not
  invent its walls. Pytest needs `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1`.
- Next: Run the test suite, remasure real photo overlap and native video,
  patch format/code-map/ADR docs, then `make benchmark` for the denser
  T18 table. T8c still waits on a connected graph. T21h now has a cable
  install path; TestFlight is not used.

## 2026-09-10 — TestFlight path (blocked on paid team)

- Context: Harsh asked how others can install Cozmo Capture via TestFlight.
- Done: Documented the App Store Connect / External Testing flow in
  `ios/CozmoCapture/README.md`. Set `ITSAppUsesNonExemptEncryption` to false
  so the first archive is not held on the export-compliance questionnaire.
- Learned: The current `DEVELOPMENT_TEAM` `PH4KQ4LY92` is a free Personal
  Team. It can Xcode-install on Harsh's phone and cannot upload to TestFlight.
  Cozmo testers are not on this App Store Connect account, so they need
  External Testing + Beta App Review, not Internal Testing.
- Next: Enroll in the Apple Developer Program, switch the Xcode team, create
  the app record, Archive, then invite testers. Keep Route 2 scored until that
  install is under 10 minutes on their phone.

## 2026-09-10 — T21g first Route 1 capture ingested

- Context: Harsh installed the app and shared `cozmo-capture-20260909-190805`.
- Done: Copied the job to `data/private/route1-roomplan/`. CLI reconstructed
  centimetres from RoomPlan JSON (`status=partial`). `.r3d` has 40 valid
  RGB-D frames. Track the AirDrop dump at repo-root `cozmo-capture/` (do not
  gitignore it).
- Learned: Wall loop was open (`incomplete_scan` / convex hull). Trajectory
  extent is ~0.4 m, so the scan was mostly in-place. Do not mix with Route 2
  Record3D under `data/private/benchmark-lidar/`.
- Next: Recapture walking the perimeter; then more rooms. T21h TestFlight or
  timed install on Cozmo's phone.

## 2026-09-09 — T21f CLI ZIP ingest

- Context: T21e packed a job ZIP but the CLI still required a directory.
- Done: `run` accepts a `.zip`, unpacks it, reconstructs RoomPlan JSON, and
  writes a structured failure for incomplete archives. First-flight iPhone
  install steps are in `ios/CozmoCapture/README.md`.
- Learned: Do not treat `.r3d` as a job ZIP (suffix must be `.zip`). RoomPlan
  JSON remains the wall source when both JSON and `.r3d` are present. The app
  cannot capture on the Simulator.
- Next: Harsh T21g signed install on the iPhone 17 Pro, then AirDrop the ZIP
  into `python -m cozmo_floorplan run`.

## 2026-09-09 — T21e capture job ZIP

- Context: T21c wrote loose `roomplan.json` plus `.r3d` files. T21e packages
  them into the CLI job-folder contract so AirDrop is one ZIP.
- Done: iOS `JobPackageBuilder` writes `manifest.yaml` + `lidar/` as a folder
  and ZIP; ShareLink shares the ZIP; Python `capture_package` inspects, rejects
  incomplete archives, and extracts into `load_job`. Simulator, unsigned
  iPhoneOS, and test-target builds succeed. Seven new Python tests pass.
- Learned: Keep the package builder in Export files, not capture-session
  types, so T21d/T21f can proceed in parallel. ZIP members are wrapped in
  `cozmo-capture-<timestamp>/`; Python strips that prefix. Rooms with no LiDAR
  frames omit `.r3d` rather than writing empty archives.
- Next: T21f CLI ZIP ingest / reconstruct round-trip. Harsh does T21g signed
  install, confirms LiDAR frame count, and unzips the job into
  `data/private/route1-roomplan/`.

## 2026-09-09 — T21c raw ARKit LiDAR recorder

- Context: T21b exported processed RoomPlan walls only. T21c logs the raw RGB,
  LiDAR depth, confidence, poses, intrinsics, resolution, and timestamps.
- Done: 2 Hz `ARSession.currentFrame` sampling during each named scan (max 90
  frames), JPEG plus LZFSE depth/confidence, XYZW camera-to-world poses,
  Record3D-compatible `.r3d` ZIP writer, live frame count, multi-file share,
  and archive contract tests. Simulator, unsigned iPhoneOS, and test-target
  builds succeed.
- Learned: RoomPlan does not expose an ARFrame delegate; polling
  `sceneDepth`/`smoothedSceneDepth` is the non-invasive hook. Frames without
  both depth and confidence are skipped rather than inventing values. The
  Python T6 adapter can read these archives without a new format.
- Next: review, then T21e job ZIP. Harsh does T21g signed install and checks
  that LiDAR frame count increments on the iPhone 17 Pro.

## 2026-09-09 — Real damage evidence classified

- Inspected the supplied my-room wide/close images and drawing-room close image.
  They show a hairline `crack` and localized `impact_damage`; the old water-stain
  and puncture placeholders were removed.
- Moved damage-only close-ups out of geometry room folders so drawing-room and
  my-room each remain within the official eight-photo maximum. Evidence now
  lives job-relative under `benchmark-photos/evidence/damage/` for later agent
  image loading.
- Updated `measurements.txt` with three evidence records and blank width,
  height, and wall fields for Harsh to measure/fill. No centimetres were inferred
  from unscaled photographs.
- Current photo counts are drawing-room 8, my-room 8, pooja-room 8, connector 1;
  the connector still needs at least one more photo.

## 2026-09-09 — T21b multi-room RoomPlan capture/export

- Context: T21a was the single-room exporter. T21b is named multi-room
  accumulation plus portable `rooms[]` export before raw ARKit logging.
- Done: session room names, retained `CapturedRoom`s, Apple `StructureBuilder`
  merge, `parentIdentifier` → `wallIdentifier`, shared-wall `roomIds` /
  `connectsRoomIds` annotation, merge-failure fallback, contract tests, bundle
  ID in Info.plist, operator README, code map, and device-matrix notes.
- Learned: Xcode 26.6 ships stub iOS platforms (~156 MB) until
  `xcodebuild -downloadPlatform iOS` installs the 8.52 GB iOS 26.5 simulator.
  After that, generic simulator and unsigned iPhoneOS builds succeed. XCTest
  compiled; first-boot simulator launch hung, so tests were not executed.
  RoomPlan capture still needs the LiDAR iPhone.
- Next: review this stage, then T21c raw ARKit logging. Harsh does T21g signed
  install and a real multi-room export into `data/private/route1-roomplan/`.

## 2026-09-09 — T3 clean upload layout prepared

- Removed the 23 WhatsApp photos and two MP4s from the active photo/video jobs;
  preserved them recoverably under
  `/private/tmp/assignment-cozmo-media-backup-20260909-1935`. The three existing
  Record3D `.r3d` archives were not changed.
- Rebuilt exact empty primary and repeat folders for four photo areas, a
  continuous property video, photo/video/LiDAR repeats, staged damage evidence,
  tape/laser evidence, magicplan raw exports, and isolated Route 1 RoomPlan JSON.
- Replaced `mytask.md` with one path-specific capture checklist and added
  fill-in measurement, damage, incumbent-notes, and manifest templates.
- `benchmark.yaml` now knows the optional photo/video repeats and the normalized
  magicplan output path. Template manifests intentionally remain named
  `manifest.TEMPLATE.yaml` until media exists, so readiness stays honest.
- Next: Harsh captures/transfers originals, fills the text templates, renames
  repeat manifests only after upload, and runs `make benchmark`.

## 2026-09-09 — T21a iOS RoomPlan exporter foundation complete

- Xcode 26.6 is now active at `/Applications/Xcode.app/Contents/Developer`.
- Added a modular iOS 17 SwiftUI app for one-room native RoomPlan capture,
  portable RoomPlan JSON v1 serialization, atomic local export, and system
  sharing. The JSON preserves metres and column-major transforms for the
  existing Python adapter.
- Added a shared Xcode scheme, explicit camera usage text, unsupported-device
  handling, repeat capture, compiled contract test, app README, device matrix,
  root README status, and complete `docs/code-map.md` entries.
- Verified Swift formatting; simulator app build, simulator test-target build,
  and unsigned generic iPhoneOS build all succeed. The host has no installed
  simulator runtime, so XCTest execution and real RoomPlan sensing wait on
  T21b device work.
- Next: review this stage, then T21b multi-room accumulation plus signed iPhone
  install/export/CLI round-trip and the under-10-minute install rehearsal.

## 2026-09-09 — T20c final benchmark runner complete

- Added a safe root-relative `benchmark.yaml` contract and separate config,
  manifest, readiness, report, and runner modules. Paths cannot escape the
  capture root.
- `python -m cozmo_floorplan benchmark CAPTURE_ROOT --out OUT` and
  `make benchmark` run every available primary/repeat job, preserve per-tier
  JSON/SVG/ablation/eval artifacts, and write both `benchmark-status.json` and
  `benchmark-summary.md`. The Make target defaults to live-capable `auto` agent
  mode and exposes an explicit fallback override for offline rehearsal.
- Missing jobs, tape truth, LiDAR repeat, incumbent, or staged damage evidence
  remain explicitly `pending`; a successful audit exits zero without converting
  missing proof into a numeric failure.
- Added a public template and preflight instructions. The private root now has
  its ignored manifest. Its real audit runs all three tiers: LiDAR is `partial`,
  photos/video are structured `failed`, and exactly four inputs remain pending:
  ground truth, repeat LiDAR, incumbent, and damage observations.
- Added pending-root, path-escape, complete mocked three-tier, and CLI tests.
  All 117 tests, Ruff, new-file formatting, compileall, synthetic
  reproduction, real partial benchmark, and `git diff --check` pass.
- Audited the remaining queue: photo SfM/stitch, real video metric output,
  LiDAR calibration/repeatability, incumbent comparison, report tables, and
  walk-in rehearsal all require new capture/evidence; T21 requires full Xcode.
- Next: no unblocked pre-shoot implementation remains. Complete T3, run
  `make benchmark`, and fix the worst measured result.

## 2026-09-09 — T7g conservative video FloorPlan complete

- Added rotated Manhattan yaw search and strict room qualification: supported
  floor and ceiling plus two wall bands on each planar axis must bracket the
  accepted metric camera path. Missing surfaces fail `low_confidence` rather
  than becoming dimensions.
- Added backward-compatible calibrated sidecar v1.2 with an explicit `world_frame_id` and
  `arkit_poses`/`arcore_poses` scale source. Multi-video rooms must share one
  tracking frame; unrelated coordinates are refused.
- Added separate room-fitting, video-measurement, and FloorPlan-conversion
  modules. Accepted geometry emits schema-valid partial rooms/walls with
  candidate-stage intervals, no invented openings, and full provenance.
- Fixed main-pipeline video dispatch so a successful adapter document is
  returned, drift-accounted, and agent-enriched instead of falling through to
  the generic unsupported result.
- Added rotated-room recovery, missing-ceiling refusal, backward-compatibility,
  schema/interval,
  coordinate-frame, adapter-success, and pipeline-routing tests. All 112 tests,
  Ruff, touched-file formatting, compileall, synthetic reproduction, private
  video smoke, and diff checks pass across 113 tests. Repository-wide format check still lists
  34 untouched pre-existing files; they were intentionally not reformatted.
- Current Camera-app MP4s remain `unsupported_tier` with zero rooms because
  they contain no calibrated sidecars. No metric claim was manufactured.
- Next: T20c one-command final evidence runner; T8c remains blocked on the
  overlapping photo reshoot.

## 2026-09-09 — T7f calibrated video triangulation complete

- Added pose-sidecar schema v1.1 with required display-oriented pinhole
  intrinsics and explicit `x_right_y_down_z_forward` camera axes. Existing v1.0
  sidecars remain valid for position alignment but cannot authorize metric
  triangulation.
- Added calibrated projection/triangulation only inside accepted metric-aligned
  trajectory segments. Exact source-frame/timestamp poses, positive bounded
  depth in both cameras, ≤2 px reprojection error, ≥1.5° ray angle, and 3 cm
  voxelization guard every output point.
- Added separate sparse surface diagnostics for supported y-up horizontal and
  vertical coordinate bands. They remain plane evidence, not wall dimensions
  or FloorPlan rooms.
- Added synthetic recovery, reprojection-outlier, calibration/accepted-segment,
  and floor/wall-support regressions. All 106 tests, Ruff, touched formatting,
  compileall, synthetic reproduction, private two-video smoke, and
  `git diff --check` pass. The private Camera-app MP4s still report
  `metric_alignment=not-available`; no centimetres were emitted.
- Locked the pre-upload sequence in `TASKS.md`: T7g, T8c, T8d, T8e, then T20c.
  Real accuracy, calibration, and evidence-driven fixes remain dependent on
  final media and ground truth.
- Next: stop for review, then T7g conservative video room/FloorPlan conversion.

## 2026-09-09 — T8b photo overlap graph complete

- Added separate immutable photo-overlap policy, reusable ORB/mutual-match
  feature utilities, and a graph algorithm for within-room connectivity and
  conservative cross-room connector candidates.
- Each pair records the stronger seeded homography/fundamental support plus
  match count, inlier ratio, spatial coverage, and named rejection reasons.
  Cross-room evidence uses stricter thresholds and never becomes adjacency by
  itself.
- Added synthetic tests for a connected transformed sequence, unrelated rooms,
  a featureless disconnected image, and the connected-graph metric boundary.
- Real result: drawing-room has 3/21 eligible edges and 4 components; my-room
  2/28 and 6; pooja-room 2/28 and 6. No room pair has a connector candidate.
  The CLI now returns actionable `insufficient_overlap` instead of proceeding
  to an unstable SfM model or inventing scale.
- All 100 tests, Ruff, touched-file formatting, compileall, synthetic
  reproduction, private 23-photo smoke, and `git diff --check` pass. No commit
  was made.
- Next: T7f can proceed synthetically; T8c metric SfM waits on an overlapping
  photo reshoot with intermediate and doorway/connector views.

## 2026-09-09 — T7e metric video-pose sidecar complete

- Extended normalized video samples with their exact encoded frame indices and
  clip-relative decode timestamps; display rotation does not erase identity.
- Added `video_poses.py`, a strict versioned metre/camera-to-world parser with
  coordinate convention, increasing frame/time, finite-position, and unit-XYZW
  quaternion validation. Malformed sidecars fail structurally.
- Added `video_pose_alignment.py`. It fits an orientation-preserving 3D
  similarity per local VO segment only after at least three exact frame/time
  matches, rejects degenerate motion and >15 cm RMSE, and reports scale and
  aligned metric camera positions without yet claiming walls.
- Synthetic tests recover a known 0.4 m/unit transform and reject wrong units,
  duplicate frames, invalid quaternions, and 100 ms timestamp shifts. The two
  private MP4s have no sidecars, report `metric_alignment=not-available`, and
  remain structurally unsupported rather than receiving guessed scale.
- All 96 tests, Ruff, touched-file formatting, compileall, synthetic
  reproduction, private two-video no-sidecar smoke, and `git diff --check` pass.
  No commit was made.
- Next: T7f sparse triangulation/plane diagnostics for sidecar-aligned segments,
  or T8b photo overlap graph against the uploaded images.

## 2026-09-09 — T7d scale-free video trajectory complete

- Refactored ORB extraction, ratio matching, and seeded fundamental estimation
  into `video_features.py`, shared by the T7c gate and T7d pose algorithm.
- Added essential-matrix relative-pose recovery with an explicit image-size
  focal prior. Translation directions are normalized and remain unitless.
- Failed feature or pose edges close the active local trajectory. Later valid
  evidence restarts at a new identity anchor; disconnected segments are not
  mislabeled as globally relocalized.
- Added deterministic two-view pose, segment-break/restart, and short-input
  tests. Real results: my-room recovers 21/89 edges in 10 segments; pooja-room
  recovers 17/89 in 9. The CLI remains `unsupported_tier` because no validated
  metric scale or room geometry exists.
- Next: T7e validate a metric per-video pose sidecar and align only proven
  frame/timestamp correspondences before any FloorPlan output.
- All 89 tests, Ruff, touched-file formatting, compileall, synthetic
  reproduction, private two-video trajectory smoke, and `git diff --check` pass.
  No commit was made.

## 2026-09-09 — T7c video feature-track gate complete

- Added a separate immutable tracking policy and `video_tracks.py` algorithm. It analyzes at most 60 evenly spaced adjacent sample pairs, bounds frames to 640 px, caches ORB features, applies Hamming ratio matching, and uses seeded fundamental/homography RANSAC.
- Every pair records keypoint, match, fundamental-inlier, motion, homography-residual parallax, and convex-hull coverage evidence. Low yield, weak geometry, stationary motion, homography dominance/pure rotation, and poor coverage are counted as explicit rejection reasons; a video needs 35% eligible pairs.
- Added deterministic tests where two-depth translational motion passes, a homography-only rotation sequence fails for low parallax, and blank frames fail without crashing.
- Real diagnostics: my-room passes 23/60 pairs with median 1,166 keypoints, 262 matches, 178 F-inliers, 78.28 px motion, 1.15 px parallax, and 23.5% coverage. Pooja-room passes 27/60 with 1,188, 257, 190, 93.41 px, 1.23 px, and 20.6%.
- Both videos are eligible for the next relative-VO stage. This does not establish metric scale, wall dimensions, or the official ±3% gate; the CLI still returns structured `unsupported_tier` after reporting the evidence.
- All 86 tests, Ruff, touched-file formatting, compileall, synthetic reproduction, private two-video feature smoke, and `git diff --check` pass. No commit was made.
- Next: T7d scale-free relative pose chaining with explicit segment breaks/relocalization. Do not assign metres without a validated pose sidecar or known length.

## 2026-09-09 — T7b multi-video orientation-aware ingest complete

- Refactored video ingest around immutable `VideoMetadata` and `SampledVideo` records. Every sorted room walkthrough is now sampled; the filename stem remains its stable identity instead of silently selecting only the first file.
- Added a capture-independent quarter-turn image utility. OpenCV backend auto-rotation is disabled, container rotation is normalized within a configured tolerance and applied once, and native/display sizes are recorded. Unsupported metadata or failure to disable auto-rotation becomes a structured capture error.
- Added stem-specific pose-sidecar names for multi-video jobs. The old global names remain valid for one video but are reported as ambiguous when several walkthroughs exist.
- Real results at about 2 Hz: `my-room.mp4` → 138 upright 720×1280 RGB samples over 68.56 s; `pooja-room.mp4` → 148 over 73.91 s. OpenCV reports both as 90° clockwise. These are ingest diagnostics, not metric geometry.
- Added three tests for multi-video identity/sidecars, explicit rotation application, and invalid non-quarter-turn rejection. All 83 tests, Ruff, touched-file formatting, compileall, synthetic reproduction, private two-video smoke, and `git diff --check` pass. No commit was made.
- Next: T7c deterministic feature-track, match/inlier, parallax, and coverage diagnostics. Continue refusing centimetres until metric pose/scale evidence exists.

## 2026-09-09 — T6b3 Record3D partial FloorPlan complete

- Added vectorized segment coordinates, separate opening-profile configuration/algorithm, Record3D-specific uncalibrated measurements, and a dedicated FloorPlan converter. The LiDAR adapter now orchestrates these modules instead of ending in `unsupported_tier`.
- Door candidates require floor-reaching sparse wall evidence plus a surviving lintel; windows require a sparse middle band plus surviving sill and lintel. Width/height ranges, wall-end margins, and short interruption handling are configurable. A solid-wall regression emits zero openings.
- Each accepted archive now yields a metric room polygon, four interval-bearing walls, ceiling height, area, supported openings, and capture provenance. Separate archives retain exported world coordinates but remain explicitly unregistered; no adjacency or transform is invented.
- The private run now emits a schema-valid `partial` JSON/SVG with 3 rooms, 12 walls, and 4 candidates: a 65 cm door in my-room and 110 cm, 95 cm, and 60 cm doors in pooja-room. These labels and dimensions are algorithm outputs pending tape-backed verification, not scored accuracy claims.
- Suppressed duplicate disconnected-room warnings when the reconstruction already disclosed missing registration. Rendered and visually inspected the private SVG; the three disjoint rooms and four opening marks are legible.
- Added four focused tests across opening detection/conversion. All 80 tests, Ruff, touched-file formatting, compileall, synthetic reproduction, private JSON/SVG smoke, and `git diff --check` pass. No commit was made.
- Next: T7b multi-walkthrough ingest and display-rotation normalization. T6 calibration, repeatability, and shared-opening association wait for the connector/repeat/tape capture.

## 2026-09-09 — T6b2 Record3D room-plane candidates complete

- Added a dedicated Record3D plane-policy config and a pure geometry module with immutable horizontal-level, wall-plane, and room-candidate results.
- The algorithm finds strong floor/ceiling y bands around the camera path, keeps only x-z columns spanning at least 1.5 m vertically, searches Manhattan yaw in 0.5-degree steps, and selects wall peaks that bracket the central camera trajectory. It never uses raw cloud extrema as room dimensions.
- Added four public-safe synthetic tests covering a rotated 4 m × 3 m room, a second room scale, rejection of low furniture, missing-ceiling refusal, and non-finite input refusal.
- Wired candidate extraction into the production Record3D branch. Real diagnostics: drawing-room 3.05 × 3.80 m with 2.95 m ceiling; my-room 3.25 × 3.70 m with 2.92 m ceiling; pooja-room 3.65 × 2.90 m with 2.93 m ceiling. These are not accuracy claims because tape/laser truth is still absent.
- The CLI continues to emit a schema-valid structured failure after this stage; it explicitly says opening extraction and FloorPlan conversion remain.
- All 76 tests, Ruff, touched-file formatting, compileall, one-command synthetic reproduction, private three-scan smoke, and `git diff --check` pass. No commit was made.
- Next: T6b3 supported opening-gap extraction and interval-bearing FloorPlan conversion with per-scan provenance. Do not score centimetre gates before ground truth arrives.

## 2026-09-09 — T6b1 Record3D metric world clouds complete

- Added separate deterministic sampling, quaternion rotation, point-cloud configuration, and Record3D back-projection modules. Depth is filtered to 0.10–8 m at medium/high confidence, projected with RGB intrinsics scaled to depth resolution, transformed through normalized XYZW camera-to-world poses, and averaged into 2.5 cm voxels.
- Confirmed the convention against the official Record3D structs/source and the real captures: OpenGL negative-Z is camera forward; confidence is low=0, medium=1, high=2. The correct convention produces strong paired horizontal floor/ceiling bands on every scan; reversing Z does not.
- Real results from 61 sampled frames each: drawing-room 664,570 accepted depth pixels → 252,694 voxels in 2.32 s; my-room 644,372 → 224,435 in 2.28 s; pooja-room 677,189 → 260,653 in 2.45 s.
- Wired metric-cloud construction into the production LiDAR path. The private three-capture command completes in about 8 s and reports auditable frame/voxel/world-bound diagnostics, then remains a structured failure because bounds include furniture/outliers and are not room dimensions.
- Added four focused tests covering inclusive sampling, normalized XYZW rotation, negative-Z metric projection, camera translation, voxel bounds, and invalid config. Updated code map, format/research notes, ADR, README, device/compliance status, roadmap, and tasks.
- All 72 tests, Ruff, touched-file formatting, compileall, synthetic reproduction, private three-scan smoke, and diff checks pass. The private command's exit 2 is intentional until planes become FloorPlan geometry.
- `mytask.md` remains untouched as Harsh's untracked human-capture checklist.
- Next: T6b2 horizontal floor/ceiling detection and Manhattan wall-plane extraction for one room, with diagnostic rejection before FloorPlan conversion.

## 2026-09-09 — T6a real Record3D decode and validation complete

- Inventoried the partial private upload: three genuine Record3D `.r3d` room archives, 23 unique decodable JPEGs across three room folders (8/8/7), and two valid H.264 1280×720 walkthroughs lasting 68.56 s and 73.91 s. The JPEGs have no EXIF after WhatsApp transfer; both MP4s carry a -90° display transform.
- Filled the three gitignored private manifests so each job now passes the production loader. The capture remains incomplete: drawing-room video, connector/hallway, repeat capture, tape/laser truth, staged-damage evidence, and two-room incumbent output are missing.
- Added separate Record3D archive I/O, validation config, bounded validation algorithm, and LZFSE utility modules. The reader validates matched JPEG/depth/confidence indices, timestamps, seven-value poses, four-value per-frame intrinsics, dimensions, and exact decompressed byte counts.
- The portable path uses `python-lzfse`; macOS can use Compression.framework when the package is absent. Three representative frames per real archive decoded successfully.
- Real evidence: drawing-room 4,045 frames / 87.44% sampled valid depth; my-room 4,057 / 85.38%; pooja-room 4,235 / 97.23%. These are integrity numbers, not wall-accuracy claims.
- The CLI now reports exactly what Record3D evidence validated, then stops with structured `unsupported_tier` until T6b fuses points and extracts floor/wall/opening planes.
- Added four focused tests and `docs/formats/record3d.md`; updated dependencies, code map, ADR, capture-tier docs, device matrix, README, and tasks. All 68 tests, Ruff, compileall, synthetic reproduction, and diff checks pass.
- Next: T6b metric point-cloud fusion and single-room plane extraction. Do not start benchmark scoring until tape ground truth arrives.

## 2026-09-09 — T20b compliance structure locked

- Audited the complete 27-row compliance matrix against the shipped code and artifacts without changing capture-dependent accuracy claims.
- Corrected R11 from the undocumented status `implemented` to `done`; the schema and contract tests already require intervals on every scalar measurement.
- Added a structural regression test that requires R1–R27 exactly once, in order, using only the matrix’s allowed status vocabulary.
- Verified all 64 tests, Ruff, compileall, fix-loop hashes, the one-command synthetic reproduction, and diff checks. No commit was made.
- Remaining partial/missing rows genuinely require photo/video/LiDAR, tape, incumbent, or walk-in evidence. No further metric stage is honest before T3 capture; T21 separately needs full Xcode.

## 2026-09-09 — T17a Route 2 protocol handoff complete

- Audited the promised walk-in handoff against the production job loader. The route referred to a manifest template that did not exist and could be read as claiming raw Record3D compatibility that has not shipped.
- Added separate photos, video, and LiDAR job templates under `data/templates/`, plus a contract test that loads every template and enforces distinct job ids/tier directories.
- Reduced `docs/capture-route.md` to a 469-word operator card with exact copy commands, eight-photo sequence, continuous-video route, LiDAR export checklist, and an explicit RoomPlan-JSON-versus-raw-Record3D boundary.
- Revised the device matrix to separate capture eligibility, currently accepted runtime inputs, and unmeasured accuracy. No centimetre result was invented.
- Full Xcode remains unavailable (`xcode-select` points to Command Line Tools; `xcodebuild` requires Xcode), so T21 remains blocked.
- All 63 tests pass with external pytest plugin autoload disabled; Ruff, compileall, synthetic reproduction, fix-loop verification, and `git diff --check` pass. T17 remains `doing` only for T3 walk-in validation and measured intervals.

### Next

- Capture T3 using one template per tier. Inventory the files before implementing raw Record3D, video VO, or photo SfM.

## 2026-09-09 — T20a clean-environment reproduction complete

- A fresh Python 3.12 virtual environment exposed a real README bug: installing only `requirements.txt` left `python -m cozmo_floorplan` unavailable. Added the missing `pip install --no-deps -e .` step and verified the same environment resolves the package.
- Measured the existing-checkout rehearsal on macOS arm64: venv 1.63 s, requirements 19.35 s, editable install 2.22 s, then-current 57 tests 2.98 s, run 1.02 s, eval 0.77 s, and fix-loop verification 0.40 s; total 28.37 s. Pip cache/network caveats are recorded.
- Added `make reproduce-synthetic` backed by separate reproduction config, subprocess utility, artifact verifier, runner, and tests. It forces deterministic mode, expects eval exit 3, validates schema/entity counts/gate states, verifies fix-loop hashes, and returns 0 on the complete expected contract.
- Fixed the README eval example to pass an output directory, ignored generated `out/`, documented exact evidence in `docs/reproduction.md`, and updated code map/setup/compliance.
- The exact Make target passes; the full suite is now 59 tests. Ruff, compileall, fix-loop verification, and diff checks pass.
- No capture media is present beyond `data/private/takehome.md`; full Xcode is still unavailable. T20 remains `doing` until the real benchmark reproduction bundle and full compliance coverage exist.

## 2026-09-09 — T10 technical report engineering draft complete

- Replaced the report stub with a compact 1,805-word draft covering architecture, all three tier designs and devices, drift/ablation, error budget, calibration, claims-agent boundaries, the shipped fix loop, and hostile-scene failure modes.
- Measured statements are tied to `data/fix-loop/after/eval.json`: 8 walls at 0 cm synthetic median/p95 error, 1/1 opening, 2/2 ceilings, and 15/15 interval coverage at 95% declared confidence.
- The report explicitly labels those values as synthetic contract evidence, distinguishes the injected 20 → 0 cm drift regression from an already-aligned ablation, and does not claim phone accuracy.
- Real LiDAR, video, photo, repeatability, multi-room, incumbent, calibration, and timing rows remain visibly pending T3 rather than estimated.
- Next media-independent stage: T20 clean-machine README/reproduction pass. T10 remains `doing` until real tables replace the pending cells.

## 2026-09-09 — T19b fallback-status fix shipped

- Reviewed and committed the checksum-locked T19a baseline as `3317339`; all 52 then-current tests and required checks passed.
- Shipped the declared status policy as `68acdf6`: explicit, successfully completed deterministic fallback preserves `status: ok`, while automatic missing-key fallback, provider failure, invalid observations, and pre-existing partial runs remain degraded.
- Generated the immutable after FloorPlan/SVG/ablation/eval artifacts from that code checkpoint. The CLI moved exit 2 → 0 and `pipeline_yield` moved fail/partial → pass/ok exactly as predicted.
- Kept the audit warning, 7 tool calls, claims output, geometry, drift result, interval coverage, and every non-target eval gate unchanged. Added verifier enforcement and a readable delta in `data/fix-loop/diff.md`.
- Verified the complete bundle, all 57 tests, `ruff check .`, compileall, and `git diff --check`.
- Next: T10 technical-report draft without invented benchmark numbers; T3 capture remains the human blocker for metric photo/video/LiDAR evaluation.

## 2026-09-09 — T19a fix-loop before bundle frozen

- Selected the worst measured current failure: `pipeline_yield=fail` because explicit, complete offline claims fallback changes the one-job prediction from `ok` to `partial` (0/1 successful yield).
- Wrote `docs/fix-loop.md` with evidence, root-cause hypothesis, intended fix, and a precise prediction: status `partial` → `ok`, yield 0% → 100%, while geometry and calibration metrics remain unchanged.
- Pinned the baseline to commit `523ceea11ba1bb405e3bc1c922447d1f427a0333` and stored `floorplan.json`, SVG, drift-off JSON, and `eval.json` under `data/fix-loop/before/`.
- Added a manifest with expected exit codes and SHA-256 hashes, a verifier command, isolated-worktree reproduction instructions, and tamper tests.
- Verified the frozen bundle, all 52 tests, `ruff check .`, compileall, and diff checks. No commit was made.
- The fix is intentionally not implemented in T19a. Next reviewable stage is T19b: ship only the declared status-semantics fix, generate `after/`, and produce a readable diff.

## 2026-09-09 — TASKS: what can ship without media

- Added a **Without media** section and a **Needs media?** column so agents do not wait on T3 for T19 / T21 / writeup draft.
- Next without uploads: T19 freeze fix-loop before on the synthetic RoomPlan job. T6/T7 VO/T8 SfM/T17/T18/T11 stay blocked on `data/private/`.

## 2026-09-09 — T8a photo-folder ingest complete

- Added separate photo ingest config, immutable I/O records, reconstruction boundary, generated-JPEG tests, and a public job-format document.
- The loader discovers room folders deterministically, enforces 2–8 images per room, decodes each supported file, rejects corrupt/undersized evidence, and records pixel dimensions.
- Multi-room photo evidence now reaches a structured `unsupported_tier` boundary that states exactly what was validated. It does not invent centimetres before SfM, adjacency, and a declared scale source exist.
- Updated `docs/code-map.md`, compliance, README, capture-tier notes, data drop instructions, and `TASKS.md`. T8a is done; full T8 remains blocked on real T3 media for metric reconstruction and calibrated intervals.
- Verified 50 tests, `ruff check .`, compileall, and the combined diff against HEAD. No commit was made.
- Next media-independent stage: T19 freeze the regenerable fix-loop “before” bundle.

## 2026-09-08 — T9 shared-wall fix + T7 video ingest

- Context: Harsh adds photos/video/LiDAR tomorrow. Tonight: finish work that does not need those files. T9’s injected 20 cm gap was not actually closing.
- Done: walls now take the pose of their first listed room, so shared `a_east` stays with room A while exclusive `b_west` moves. Gap 20 → 0 on the synthetic mutation. Tests treat pytest `agent_fallback` as `partial` (exit 2) and assert geometry `ok` before claims enrichment. Video ingest samples generated MP4s, mentions `poses.json` when present, and fails `unsupported_tier` instead of inventing centimetres.
- Learned: `_dominant_pose` (first non-identity room) moved shared walls with the neighbor, so both opening frames translated together and residual stayed 20 cm. `COZMO_AGENT_MODE=fallback` in `tests/conftest.py` makes enriched `run_job` `partial`; do not assert `status==ok` on that path.
- Next: T3 capture into `data/private/`. Without files, T8 photo ingest. With a walkthrough, T7 metric VO. T21 needs Xcode.app.

## 2026-09-09 — T9 stitch and drift ablation complete

- Full Xcode is unavailable (`xcodebuild` points at CommandLineTools), so the requested fallback stage was T9 rather than T21.
- Preserved and completed the already-staged T9 work: separate SE(2) utilities, drift config, opening constraints, room-pose traversal, geometry application, correction orchestration, CLI ablation output, and tests. File ownership is recorded in `docs/code-map.md`.
- Normal multi-room runs plane-anchor shared opening frames and write `floorplan.ablation-off.json`; `--no-drift-correction` regenerates the poses-as-is result. Before/after opening-gap residuals are stored as interval-bearing measurements.
- Tightened accountability so a job with no usable opening constraints reports correction disabled/method `none` rather than claiming a no-op correction.
- A synthetic RoomPlan mutation injects 20 cm drift into the second room; correction reduces the shared-opening gap from 20 cm to 0 cm. This is algorithm plumbing evidence only, not a real-capture accuracy claim.
- Verified the focused T9 suite (8 tests). The current full suite passes 45 tests, but that count includes concurrent untracked T7 video work that appeared during final verification and was not reviewed as part of this stage. `ruff check .`, compileall, and staged/unstaged `git diff --check` pass. No commit was made.
- Next unblocked work without captures: T19 freeze the fix-loop “before” bundle. T3 remains the human priority; T21 requires full Xcode.

## 2026-09-08 — T16 agent + tools complete

- Implemented a live OpenAI Responses API tool loop plus deterministic fallback for damage, concealed-rule flags, and scope.
- Split configuration, prompts, strict tool definitions, tool execution, provider/fallback agents, observations, bounded image encoding, environment loading, and orchestration into focused modules documented in `docs/code-map.md`.
- Metric damage extents enter through `damage_observations.json`; the model cannot pass quantities to `apply_damage`. Concealed rule ids and scope actions are policy-validated, and scope quantity is copied by tools.
- Live mutations are transactional. Provider failure or incomplete tool use discards the working copy and replays the same tools through deterministic rules with an `agent_fallback` warning.
- Added two explicitly synthetic observations to the RoomPlan fixture. No real-image accuracy claim is made.
- Verified 34 tests, ruff, compileall, and `git diff --check`. A real configured-key smoke test completed through `gpt-5-mini` with 7 tool calls, 2 damage regions, 1 concealed flag, 2 scope lines, `store: false`, and no fallback warning.
- Next: T21 if Xcode is installed. T6 raw Record3D and real damage validation still wait on T3 capture.

## 2026-09-08 — T15 whole-property SVG renderer

- Completed a deterministic, accessible SVG product surface for FloorPlan v0.2.
- Added separate modules for immutable render configuration, centimetre-to-canvas layout, SVG composition, and paired artifact persistence; recorded their roles in `docs/code-map.md`.
- The `run` command now emits `floorplan.json` and `floorplan.svg` for `ok`, `partial`, and structured-failure results. The SVG never derives new measurements: wall labels and confidence intervals come directly from the IR.
- The drawing includes room polygons and labels, walls, openings, a 100 cm scale bar, run status, counts, capture tier, scale source, and a failed-run placeholder.
- Verified the two-room RoomPlan output through the real CLI and macOS Quick Look. Automated result: 30 tests pass; ruff and compileall pass.
- Next: T16 agent + tools. Keep T6 raw Record3D blocked until a real capture exists.

---

## 2026-09-08 — T6 RoomPlan path complete; raw Record3D blocked

- Context: T14 is committed; no private sensor capture exists yet. The guaranteed Route 2 uses Record3D, so the whole LiDAR task cannot honestly be called done.
- Done: implemented portable RoomPlan JSON v1 ingestion with separate typed parsing, transform projection, wall polygonization, LiDAR uncertainty config, measurement construction, and FloorPlan assembly. Added a two-room metric fixture and six LiDAR tests.
- Output: the fixture produces 2 rooms, 8 walls, an 80×210 cm shared door, areas, ceilings, adjacency, intervals, and provenance. Multi-room status remains `partial` because T9 drift correction is deliberately not faked.
- Boundaries: `.r3d`/metadata and USDZ are detected and return structured unsupported warnings. T6 is blocked on T3 for real Record3D depth/pose files and later hardening.
- Verified: `make test` passes 27 tests; `ruff check src tests` and compileall pass. The CLI output has 0 synthetic wall/area/opening error on the shared truth fixture; repeat, drift, incumbent, and yield remain red/missing honestly.
- Next unblocked engineering task: T15 whole-property SVG renderer using the RoomPlan output.

---

## 2026-09-08 — T14 official-gate eval harness complete

- Context: T13 was committed; T14 was the highest unblocked engineering task.
- Done: added a modular eval package, official threshold config, ID-first/Hungarian matching, measurement and geometry utilities, deterministic report models, validated input/output I/O, and the `eval` CLI subcommand.
- Gates: pipeline yield, openings including miss/phantom denominator, ceiling accuracy/spread, repeatability, drift on/off evidence, photo adjacency/overlap/footprint, photo/video wall error, interval calibration, and LiDAR head-to-head.
- Behavior: missing repeat/ablation/incumbent inputs are explicit `missing_evidence`; non-applicable tier gates are distinct; failed reports exit 3 and invalid inputs exit 1.
- Verified: `make test` passes 20 tests; compileall passes; the installed command wrote a deterministic red `eval.json` from the T13 empty prediction.
- Next: T6 LiDAR export → FloorPlan. Human T3 capture remains parallel and urgent.

---

## 2026-09-08 — T13 modular CLI stub complete

- Context: T12 was committed; T13 was the highest unblocked engineering task.
- Done: added an installable `src/cozmo_floorplan` package with separate config, errors, job I/O, schema validation, atomic output, FloorPlan factory, pipeline, utilities, and CLI modules. Added `docs/code-map.md` to explain every code file.
- Behavior: `python -m cozmo_floorplan run JOB --out OUT` now validates the job layout and always writes a schema-valid structured failure while reconstruction adapters are unavailable. It returns exit code 2 for this expected incomplete state rather than fabricating geometry or returning only a traceback.
- Verified: `make test` passes 12 tests; compileall passes; editable install succeeded in a clean temporary venv; the exact installed module command wrote a v0.2 `floorplan.json` with the expected exit code 2.
- Next: T14 red evaluation harness for the official gates. Do not implement recon inside the eval task.

---

## 2026-09-08 — T12 FloorPlan schema v0.2 complete

- Context: T12 was the highest unblocked engineering task and gates the CLI/eval work.
- Done: bumped the shared IR to 0.2.0; every scalar dimension now carries `{value, unit, interval}`; required top-level damage, concealed flags, and scope arrays; added typed surface references and drift-correction metadata.
- Verified: migrated the synthetic two-room fixture and added positive/negative contract tests. `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m pytest -q` passes 8 tests. Plain pytest currently collides with an unrelated installed plugin that also registers `--output`.
- Next: T13 job layout + structured-failure CLI stub, then T14 official-gate eval harness.

---

## 2026-09-08 — Session brief for a replacement agent

Wrote `docs/prompts/session-brief.md` (paste-ready product + score + stack + next task). Point a new chat at that file plus `AGENTS.md`.

---

## 2026-09-08 — LLM tool calling required (Applied AI)

### Context

Harsh: the role is applied AI; we will use AI tool calling / an API, not a geometry-only pipeline.

### Done

- `docs/agent-layer.md` + ADR. Recon = centimetres. Agent = damage/scope/rules via tools. Disclosed public API; fallback if no key. No Redis/our servers.
- T16 retargeted. `.env.example` lists `OPENAI_API_KEY`.

### Learned

- Packet allows pretrained APIs with disclosure and forbids **our** infrastructure. OpenAI/Anthropic is in. LLM must not invent wall lengths.

### Next

- T12 schema. Then recon. Then T16 agent.

---

## 2026-09-08 — Max-score retarget

### Context

Harsh: stop hedging LiDAR-only / skip-photos / skip-app. Initially target everything that scores; cut tomorrow or tomorrow night if needed.

### Done

- ADR + `docs/cut-later.md`. Updated plan, roadmap, TASKS (T21), product, HANDOFF, README, AGENTS, capture protocol (8 photos, iPhone 17 Pro), eval gates, architecture, capture-route, cursor rules.
- Ingest leftover README/AGENTS status lines fixed (prompt is present).

### Learned

- Score policy is **full-score attempt**. Build order remains schema → LiDAR → stitch → video → photos. That is not a scope cut.
- Route 2 stays the guaranteed walk-in; Route 1 is parallel until 10-min install exists.
- Fix loop: freeze **before** as soon as eval exists.

### Next

- Code: **T12** schema. Human: **T3** capture on iPhone 17 Pro.

---

## 2026-09-08 — iPhone 17 Pro has LiDAR

- Harsh’s phone is an **iPhone 17 Pro**. GSMArena lists a rear **TOF 3D LiDAR scanner**. All three take-home tiers can run on this device. Walk-in may still be a non-Pro iPhone 15+ (photos/video only).
- Noted in `docs/device-matrix.md`.

---

## 2026-09-08 — Round 2 scoring vs app vs Round 1 reuse

### Context

Harsh asked: can Round 2 be maxed by implementing everything; is an iOS app required in Round 2; can Round 1 work be folded in later.

### Done

- Explained from `docs/takehome.md` only. No Round 1 packet exists in this repo.

### Learned (trust these)

- This packet *is* Round 2. It inherits the full Round 1 output contract and gates, then adds own-capture, three mandatory tiers, five extra gates, walk-in, fix loop, head-to-head.
- An iOS app is optional (Route 1). Route 2 is explicitly legitimate. App is 5% of score at most (capture route quality).
- Implementing every contract field does **not** certainly max the score: 30% is a cold walk-in; 15% is physics on their reproduction; 10% is beating magicplan/Polycam; 25% is a shipped fail→pass fix, not feature completeness.
- Round 1 *pipeline* (JSON contract, damage, scope, renderer, one command) is the Round 2 core and should be integrated now, not later. A Round 1 *app* can wait or be skipped.

### Next

- Ingest still pending. Capture on Harsh’s phone.

---

## 2026-09-08 — Explained official take-home (no ingest)

### Context

Harsh added the official Cozmo case study to `docs/takehome.md` and asked for an explanation: one route vs both, what each route requires, which is easier in <48 hours.

### Done

- Read the prompt. Did not implement reconstruction. Did not run full ingest (`docs/prompts/ingest-takehome.md`) because the asked deliverable was explanation.
- Marked T1 done. T4 (reconcile plan) is now unblocked but still todo.

### Learned (trust these; do not re-derive)

- Capture routes are **XOR**: Route 1 (own iOS app) **or** Route 2 (stock App Store tool + one-page protocol). Not both.
- Input tiers are **AND**: photos, video, and LiDAR are all mandatory, including photo-tier whole-property stitch from per-room folders.
- They provide **no captures**. You build the benchmark (3+ rooms + connector, furnished room with two damage classes, all three tiers on the same rooms, one repeat capture, laser/tape GT).
- Walk-in test is 30% of score; fix loop is 25%. Attachments: none (no published JSON schema in the packet).
- Route 2 is the 48-hour choice. Route 1 needs TestFlight/dev install on *their* phone in <10 minutes.

### Next

- Run ingest (`docs/prompts/ingest-takehome.md`): ADR, rescope `TASKS.md`/`plan.md`, extend schema for damage/scope/intervals.
- Human: pick Route 2, capture the benchmark set tonight if hardware exists (iPhone 15+; Pro for LiDAR).

---

## 2026-09-07 — Orchestration kit from an empty repo

### Context

Cloud Agent run on `github.com/harshsinha-12/assignment-cozmo` (private). User asked to spend the leftover session budget on README, `plan.md`, `roadmap.md`, `update.md`, and anything else needed to orchestrate later agents. Official take-home problems are **not** in the repo yet. Original files:

- `README.md` — `# assignment-cozmo`
- `discussion.md` — one-sentence problem
- `url.md` — `https://www.hellocozmo.ai/`
- `AI Backend Engineer\n.docx.pdf` — Brynz JD (filename contains a newline; 2 pages)

### Done

- Extracted the PDF with PyMuPDF; cleaned text lives in `docs/job-brief.md`; binary copy at `docs/briefs/ai-backend-engineer.pdf`.
- Wrote agent contract, handoff, plan, roadmap, setup, schema, capture protocol, research notes, interview notes.
- Added `.cursor/environment.json` + `requirements.txt` so the next Cloud Agent can install a small Python CV stack.
- Added paste-ready prompts under `docs/prompts/` and a human `START-TOMORROW.md`.
- Added FloorPlan JSON Schema + `data/fixtures/synthetic_two_room/` + `tests/test_schema.py`.

### Learned (trust these; do not re-derive)

- **Company.** Cozmo AI is a YC company (site says W25 in the JD; YC page also shows W22 / founded 2025 — treat branding as messy, not important). HQ San Francisco, role in-office New York 996 per the JD. Product: AI workforce for P&C claims. Agents answer the call, capture the loss, write into Xactimate/Cotality, dispatch contractors, draft estimates from field photos. Customers: restoration franchisors, TPAs, adjusting firms. Site: https://www.hellocozmo.ai/ — also `/see` for vision (photos, video, documents). Founders: Alok Kumar (CEO), Nuha Hashem (CTO). Recruiter: Brynz, saik@brynz.io, https://www.brynz.tech.
- **Role.** Title on the PDF: AI Backend Engineer. User’s note calls it Applied AI Engineer. JD emphasis: production agents (prompts, tools, routing, evals, fallbacks), reverse-engineering legacy claims software, data layer as moat, forward-deployed in customer ops, Python or TypeScript, 0–4 years, new grads OK. Interview: shortlist → **takehome** → technical discussion → culture fit → offer.
- **Problem we actually have.** Only this sentence: turn phone camera captures into dimensioned, stitched floor plans with cm-level accuracy across three input tiers (photos, video, LiDAR).
- **Physics.** Monocular SfM (COLMAP etc.) recovers structure **up to similarity** — no metric scale. Scale needs LiDAR/depth, known poses, IMU/VO, GPS (useless indoors), or a known length (door, tape, ceiling). Claiming cm-level from uncalibrated homeowner stills without a prior is a disqualifying mistake.
- **LiDAR on this VM.** Apple RoomPlan `CapturedRoom` is Codable: walls/doors/windows/openings/objects with dimensions in metres and 4×4 transforms. Multi-room merge is `StructureBuilder` / `CapturedStructure` (iOS 17+). Export JSON/USDZ on device; process on Linux. Do not try to compile RoomPlan here.
- **Claims output shape.** Xactimate consumes sketches; magicplan’s integration exports **ESX** (not a public nice JSON). We should emit a clean FloorPlan IR. Writing `.esx` is out of scope unless the prompt requires it.
- **Cloud Agent env.** This run’s environment is personal/runtime-forward-fill, no finished environment builds, egress not restricted. A committed `.cursor/environment.json` will override dashboard envs for future runs.

### Next

- Wait for or paste the official take-home into `docs/takehome.md`.
- Unblocked: synthetic fixture + optional real-room capture (`docs/capture-protocol.md`).
- Do not start the reconstruction implementation.

### Files added (map)

See `README.md` for the map. Do not delete the original PDF even though the filename is hostile; a clean copy exists under `docs/briefs/`.

## 2026-09-09 — T20d benchmark evidence activation and honest readiness

### Done

- Activated the supplied independent `my-room` photo and video repeats with
  primary-job and room linkage. The unsupported USD repeat remains preserved
  but is not mislabeled as a Record3D `.r3d` job.
- Corrected the primary manifests to describe the real 8/8/8/5 photos and four
  separate walkthrough clips.
- Normalized supplied tape measurements into an explicitly partial
  `ground_truth.json`; unmeasured connector width, property placement, opening
  support/offsets, and windows remain absent instead of invented.
- Normalized three measured crack/impact observations and their local evidence
  paths into `damage_observations.json`.
- Normalized Magicplan summaries for `my-room` and `pooja-room`. Display
  rounding is represented in intervals; individual wall lengths remain absent.
- Added separate `benchmark/repeat.py` and `benchmark/evidence.py` modules and
  documented their responsibilities in `docs/code-map.md`.
- Corrected readiness to accept any linked same-room, same-tier repeat and to
  semantically validate truth, two-room incumbent, and two-class damage inputs.
- Verification before final benchmark: 129 tests pass; Ruff, compileall, and
  `git diff --check` pass.

### Decision

- The official prompt does not require a LiDAR repeat. The active photo repeat
  satisfies capture eligibility; the numeric repeatability gate remains honest
  until both photo runs emit comparable wall measurements.

### Final benchmark

- `make benchmark` reports `status=complete` with zero pending input classes.
- The LiDAR head-to-head passes 2/2 shared ceiling dimensions. This is sparse
  evidence because the Magicplan screenshots do not expose individual walls.

### Next

- Review/commit this stage. Next implementation stage is evidence-driven
  photo-overlap work.

---

## 2026-09-10 — T8b2 robust indoor photo overlap

### Done

- Added a separate bounded grayscale loader, CLAHE-assisted SIFT extractor, and
  ORB/SIFT ensemble composition layer. SIFT is used as complementary evidence,
  not as an excuse to relax the pair gates.
- Matching is descriptor-norm aware and uses method-specific ratio/RANSAC
  settings. The 2.5 px SIFT reprojection threshold at 1,200 px is tighter in
  normalized coordinates than the existing 2 px ORB threshold at 900 px.
- Connected-component diagnostics now retain actual image membership and name
  isolated images in the structured failure warning.
- Added a deterministic low-contrast regression proving the SIFT fallback while
  retaining featureless-image rejection.

### Real evidence

- Before → after components: connector 5→2, drawing-room 6→2, my-room 7→5,
  pooja-room 7→3.
- Cross-room candidates improve from zero to two:
  connector↔my-room and connector↔pooja-room.
- All four room graphs remain disconnected, so the result still returns
  `insufficient_overlap` and emits no centimetres. T8c metric SfM remains
  blocked rather than consuming an unsafe graph.
- Full `make benchmark` completes with zero pending inputs after the change;
  photos/repeat photos and videos remain failed, while LiDAR remains partial.
- Verification: 130 tests pass; Ruff, compileall, and `git diff --check` pass.

### Next

- Review this stage. If capture replacement is possible, use the named
  components/isolates to replace weak photos with corner-transition views.
  Otherwise proceed to a different evidence-driven tier rather than weakening
  photo acceptance thresholds.

---

## 2026-09-10 — T6c frame-invariant LiDAR wall evaluation

### Done

- Added a dedicated wall matcher that first matches rooms, orders each room's
  single-owner walls around its centroid, and searches cyclic shifts plus
  reflection using side-length evidence.
- Generated wall ids no longer force long sides to compare with short sides
  when prediction and truth were numbered from different polygon origins.
- Added regressions for independent rotation/translation, reversed arrays, new
  ids, and reused-but-shifted generated ids.

### Real evidence

- Private LiDAR wall median changed from invalid 75 cm to 2.5 cm; p95 is 30 cm
  across 12 walls. Per-room absolute errors are drawing 12/12/0/0 cm,
  my-room 30/30/0/0 cm, and pooja-room 5/5/0/0 cm.
- Interval coverage is now 11/18 (61.1%) against 80% mean declared confidence,
  so calibration remains failed. Maximum ceiling error remains 5.41 cm.
- No reconstruction value or interval was tuned from ground truth. Cross-room
  registration and opening truth remain incomplete.
- Verification: 135 tests pass; Ruff, compileall, full private benchmark, and
  `git diff --check` pass.

### Next

- Review this stage. A following stage can diagnose Record3D wall/ceiling bias
  from point-support evidence, while T7 native videos and T8 disconnected photo
  graphs remain separate unresolved paths.

---

## 2026-09-10 — T6d support-conditioned Record3D intervals

### Done

- Inspected horizontal and vertical support in all three raw Record3D clouds.
  Every selected boundary has dense, room-spanning plane support, including the
  visible 3.70 m `my-room` span. The pipeline therefore does not add the
  unobserved 30 cm needed to match tape truth.
- Added a separate uncertainty policy and algorithm. Conservative p95 residuals
  around paired wall planes define span half-widths; floor plus ceiling
  residuals define height half-width; span bounds propagate into area.
- Wired those intervals through the raw Record3D reconstruction while retaining
  fixed candidate floors and unchanged opening bounds.
- Added focused algorithm tests and an integration test proving interval order
  reaches the correct polygon walls, ceiling, and area.

### Real evidence

- Wall and ceiling centre values are unchanged: wall median/p95 remains
  2.5/30 cm and maximum ceiling error remains 5.41 cm.
- Aggregate interval coverage improves 11/18 (61.1%) to 16/18 (88.9%) at 80%
  mean declared confidence. The internal calibration gate now passes.
- This is transparent development-benchmark calibration, not independent
  holdout validation. The two 30 cm `my-room` long-wall errors remain outside
  the reported intervals.

### Next

- Review this stage. Remaining T6 work requires opening truth and cross-room
  connector evidence. T7 native video and T8 photo SfM remain the next code
  tracks that can materially advance without inventing LiDAR geometry.

---

## 2026-09-10 — T7 video measurement config fix

- Fixed `video_measurements._measurement` so callers pass the configured method
  string explicitly instead of referencing an undefined `config` variable.
- Ruff and 12 focused video adapter/FloorPlan tests pass.
- Broader T7 native-scale work remains active in the shared worktree.
