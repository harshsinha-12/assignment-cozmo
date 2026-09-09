# Task queue

Agents: pick the highest item whose status is `todo` and whose Blocked-by is empty or done. Check boxes in the same edit as the work. Move finished items to **Done** with a date.

Status key: `todo` · `doing` · `blocked` · `done`

Product: local CLI + **disclosed LLM tool-calling agent**. Score policy: max every official row (`docs/cut-later.md`). Route 2 walk-in; Route 1 parallel (T21). See `docs/product.md` and `docs/agent-layer.md`.

---

## Capture status (reshoot layout prepared 2026-09-09)

The active private benchmark now has 8/8/8/5 decodable primary photos, four
primary videos, three room-level Record3D scans, an 8-photo `my-room` repeat, a
repeat video, normalized tape measurements, and two-class damage evidence.
Magicplan evidence covers `my-room` and `pooja-room`. My-room has AABB walls
from displayed 4.20×3.29 m. Pooja-room has six screenshot-traced Manhattan
walls scaled to 12.04 m². App version is App Store **2026.35.0**. Connector
LiDAR and measured whole-property placement/opening offsets remain unavailable.
Do **not** invent centimetres.

| ID | Can finish now? | What to do without uploads |
| --- | --- | --- |
| **T21** | **T21h cable path shipped; scored route still Route 2** | App runs on Harsh's phone. Walk-in install is `./scripts/install-cozmo-capture.sh` then `open -a Xcode ios/CozmoCapture/CozmoCapture.xcodeproj`. Free Personal Team; TestFlight not used. Harsh timed device copy **~18 s** (signed build 46 s). Cozmo's phone is still untimed. |
| **T10** | **Tables filled 2026-09-10** | `docs/writeup.md` §6 has the `make benchmark` gate table (LiDAR 12.5/25 cm, 5/12 head-to-head, photo/video 0 walls). |
| **T20** | **README + compliance filled** | Submission README: deliverables, 15-min setup, one command, app install, defense test. Compliance matrix uses measured artifacts. |
| **T17** | **Measured matrix filled** | `docs/device-matrix.md` uses harsh-home-01 numbers, not TBD. |
| **T11** | **Harness done; media pending** | `make walkin` times a holdout room, crash-tests 2 stills, and refuses benchmark-room reuse. Shoot kitchen/guest/bath — not drawing-room/my-room/pooja-room/connector. |
| T8 remainder | Full count present | EXIF orientation applied. `make benchmark` photo graphs still connector/drawing/my/pooja = **2/2/5/3**. Do not loosen gates. T8c waits on a connected graph. |
| T7 remainder | Four MP4s smoked | Native handheld-height scale works on all four clips after display-K fix. 0/4 complete rooms (missing wall/floor/ceiling bands). Openings/stitch coded; ±3% not claimed. |

**Still evidence-blocked:** T11 holdout media (harness is ready; Harsh is not shooting it). T18 Magicplan 2026.35.0 scores **5/12 (41.7%)** on the latest `make benchmark`. T6/T7/T8 can still advance against uploaded media.

---

## Now

| ID | Status | Task | Blocked-by | Needs media? | Notes |
| --- | --- | --- | --- | --- | --- |
| T0 | done | Orchestration kit | — | no | 2026-09-07 |
| T1 | done | Official prompt in `docs/takehome.md` | human | no | 2026-09-08 |
| T2 | done | Synthetic two-room fixture | — | no | 2026-09-07 |
| T4 | done | Reconcile plan with official prompt | T1 | no | 2026-09-08 ingest |
| T3 | doing | Human benchmark capture | human + Pro phone | **yes — active** | Primary/repeat photos and videos, three room `.r3d`, measurements, damage, and two-room Magicplan summaries are active. Connector LiDAR and measured property placement remain unavailable |
| T6 | doing | LiDAR export → FloorPlan | — | **present** | T6a–T6e. Walls unchanged (densest peaks). Openings vs tape **5/10/15 cm** (195/70/95 vs 200/80/80). Shared-world pairing coded; nearest pair **5.08 m**. Ceiling max **5.4 cm**. Official opening ≤2 cm and ceiling ≤1.5 cm not claimed. Last `make benchmark` wall row 12.5/25 cm is pre-opening-detector |
| T9 | done | Stitch + drift correction + on/off ablation | T6 | no | 2026-09-08 plane-anchored snap; shared walls stay with first owner |
| T7 | doing | Video path | T6 | four MP4s present | T7b–T7h + openings/stitch code. Native scale 4/4; complete rooms 0/4. ±3% not claimed |
| T8 | doing | Photos path, 2–8 stills, folder stitch | — | present | T8a–T8b3 done. T8c SfM still blocked until post-EXIF overlap is measured and connected |
| T21 | doing | Route 1: thin iOS RoomPlan/ARKit exporter + 10-min install | — | no | T21a–T21g done on Harsh's iPhone 17 Pro. T21h cable card+script done; Harsh device copy **~18 s**. TestFlight declined. Scored route stays Route 2 until the same install is timed on *their* phone |
| T17 | done | Device matrix + capture-route polish | T3 | measured | 2026-09-10 measured harsh-home-01 intervals in `docs/device-matrix.md` |
| T18 | doing | Head-to-head vs Polycam or magicplan (2 rooms, LiDAR) | T3, T6 | evidence present | Magicplan 2026.35.0; my-room AABB + 6 pooja traced walls. Latest `make benchmark` LiDAR **5/12 (41.7%)**, fail vs ≥70% |
| T10 | done | Technical report ≤ 6 pages + benchmark tables | T19 | no | 2026-09-10: 1,889-word report with regenerable gate table |
| T20 | done | README 15 min + reproduction bundle + compliance matrix | T10 | no | 2026-09-10 submission README + measured compliance artifacts |
| T11 | doing | Walk-in rehearsal on a new room, all three tiers | T20 | **yes** | Harness shipped (`make walkin`, `docs/walk-in.md`). Media still needed: eight JPEGs, one MP4, Record3D `.r3d`, tape. Forbidden rooms: drawing-room, my-room, pooja-room, connector |

---

## Unblocked detail

### T3 — benchmark capture (human, start now)

Not optional. Composition from the prompt:

- 3+ rooms plus a connector
- Same spaces at **photos, video, LiDAR**
- Photos = per-room folders, **8 stills** per room (protocol maximum — max-score capture)
- One furnished room with **two staged damage classes**
- One room captured twice at the **same tier**. The active official pair is the independent `my-room` photo repeat; video repeat is extra evidence.
- Laser or tape on walls, openings, **ceilings**; photo of tape
- Polycam **or** magicplan export on two rooms (name version). Do not use that app as the capture route.

Protocol for *our* capture: `docs/capture-protocol.md`. Protocol *they* will use until T21 ships: `docs/capture-route.md`.

Hardware: Harsh has **iPhone 17 Pro** (LiDAR). Walk-in may still be non-Pro.

Privacy: no faces/docs in git. Large binaries: Git LFS or `data/private/` gitignored + note the path in `HANDOFF.md`.

### Next engineering task

T8c: photo SfM after a connected overlap graph. Do not loosen T8b gates
(current components 2/2/5/3). T10/T17/T20 measured docs are filled. Harsh is
not shooting T11. Route 2 stays the scored walk-in.

### Media-ready freeze sequence

These are the remaining code stages that can be prepared before the final
benchmark upload. Complete them one reviewable stage at a time; real accuracy
claims, threshold calibration, and final evidence still wait on T3 media and
ground truth.

1. **T7f (done)** — Calibrated sidecar-backed sparse metric triangulation and
   diagnostic floor/wall candidates.
2. **T7g (done)** — Convert accepted video surface evidence into conservative
   room geometry and the shared FloorPlan IR.
3. **T8b2 (done)** — Bounded CLAHE+SIFT fallback, named components, real
   before/after graph evidence, and exact isolated-image diagnostics.
4. **T8b3 (done)** — EXIF display orientation on photo ingest/features. 53
   focused tests pass. Remeasure private overlap before claiming connectivity.
5. **T7h (done)** — Skip-span VO edges and handheld-height metric fallback
   for native Camera video. Display-space sidecar K. Real smoke: 4/4 scaled,
   0/4 complete rooms. Occupancy openings + shared-world stitch pairing
   exist; ±3% not claimed.
6. **T8c (blocked on connected evidence)** — Incremental per-room photo SfM
   after every overlap graph connects.
7. **T8d (blocked on T8c + scale evidence)** — Photo Manhattan layout, metric
   scale, and calibrated uncertainty.
8. **T8e (blocked on connector evidence)** — Cross-room photo registration and
   connected whole-property stitch.
9. **T20c (done)** — One-command final benchmark/evidence runner with explicit
   pending results when required capture or ground truth is absent.

After these stages, remaining work is expected to be media ingestion, measured
evaluation/calibration, and evidence-driven fixes rather than planned feature
scaffolding. Minor fixes after real captures remain normal and allowed.

---

## Done

- **2026-09-10 T6e openings + shared-world registration + honest wall/ceiling bias** — Cased openings (door max exclusive at 1.40 m), corner-door margin extension, emptiest-gap ranking so furniture-dense spans lose, tape door widths in private GT with `wall_id: unlocated`. Record3D archives already share an ARKit frame; nearest opening pair is 5.08 m so rooms stay unregistered. Optional 32 cm clutter-band outer walls stay off. Private opening width errors 5/10/15 cm; ceiling max 5.4 cm; wall centres unchanged (last `make benchmark` 12.5/25 cm). Official ≤2 cm opening and ≤1.5 cm ceiling gates not claimed. Focused Record3D/eval tests pass.
- **2026-09-10 T10/T17/T20 measured docs** — Filled `docs/writeup.md` §6, `docs/device-matrix.md`, and `docs/compliance-matrix.md` from `make benchmark` 2026-09-10. Rewrote `README.md` as the submission guide (deliverables, 15-min setup, one command, cable app install, defense test). No new captures.

- **2026-09-10 T18 remainder Magicplan pooja walls + named version + benchmark** — Pooja-room inspector still has no L×W; six Manhattan inner walls traced from the 2D screenshot and scaled to displayed 12.04 m². App Store version **2026.35.0** (released 2026-09-02; Settings not screenshotted). `make benchmark` complete, pending=0. LiDAR head-to-head **5/12 (41.7%)**, fail vs ≥70%. Photo graphs remain 2/2/5/3 after EXIF.
- **2026-09-10 T7 remainder native MP4 smoke + openings/stitch** — Smoked all four Camera MP4s. Display-space native sidecar K unblocked triangulation: 4/4 floor-supported handheld scale, 0/4 complete rooms (connector/pooja missing x-high wall, drawing missing ceiling, my-room missing floor). Occupancy openings reuse Record3D profiles; shared-world coinciding openings can constrain stitch; native rooms stay disconnected. Partial FloorPlan keeps successful rooms. ±3% not claimed. 25 focused tests pass.

- **2026-09-10 T11a walk-in harness** — Separate holdout folder, timed three-tier `walkin` CLI, automatic 2-still photo crash test, and refusal to score drawing-room/my-room/pooja-room/connector recaptures. Empty templates stay `pending_inputs`. Holdout media and tape are still missing, so T11 remains `doing`.

- **2026-09-10 T21h cable install (not TestFlight)** — Official prompt allows a 10-minute cable dev build. Added `docs/capture-route-route1.md`, `scripts/install-cozmo-capture.sh`, and `open -a Xcode ios/CozmoCapture/CozmoCapture.xcodeproj`. Harsh timed device copy **~18 s** (signed build 46 s). Paid Apple Developer Program is not used. Cozmo's phone is still untimed, so the scored walk-in stays Route 2.

- **2026-09-10 T18 Magicplan AABB + area head-to-head** — Encoded my-room displayed 4.20×3.29 m as four bounding-box walls; left pooja-room walls absent. Head-to-head now compares floor area as well as walls/openings/ceilings. App version still unrecorded. Focused tests pass; `make benchmark` not re-run.
- **2026-09-10 T7h native video skip-span + handheld height** — Alternative real i→i+2 poses when adjacent tracking fails; disclosed 1.45 m camera-height prior (`imu_vo`) after floor-supported triangulation. Independent native rooms are not overlaid. Focused tests pass; private MP4 smoke not run.
- **2026-09-10 T8b3 EXIF photo orientation** — Display-oriented JPEG decode for ingest and overlap features. Focused tests pass. Real private overlap not remeasured; do not keep quoting 2/2/5/3 as current.
- **2026-09-10 T6d support-conditioned Record3D intervals** — Diagnosed all selected planes against raw support, refused an unobserved 30 cm correction, and derived per-room wall/ceiling/area bounds from conservative p95 plane residuals. Centre errors are unchanged; private interval coverage moves 61.1%→88.9% (16/18) and the internal calibration gate passes, with holdout validation still explicitly pending.
- **2026-09-10 T6c frame-invariant wall evaluation** — Replaced unsafe generated-ID wall pairing with room-local cyclic matching across translated/rotated/reflected scan frames. Private LiDAR wall median changed from invalid 75 cm to honest 2.5 cm (p95 30 cm); interval coverage is 61.1%, so calibration remains failed rather than tuned on the benchmark.
- **2026-09-10 T8b2 robust photo overlap** — Added bounded CLAHE+SIFT fallback without lowering normalized acceptance gates, exposed named components/isolated images, and improved real connector/drawing/my/pooja graphs from 5/6/7/7 to 2/2/5/3 components with two conservative cross-room candidates. Metric SfM remains blocked honestly.
- **2026-09-09 T20d evidence activation/readiness** — Activated photo/video repeat manifests, corrected primary manifest descriptions, normalized supplied tape measurements and two-class damage records, encoded two-room Magicplan summary evidence without inventing walls, and aligned readiness with the official any-tier repeat rule. The real benchmark now has zero pending input classes.

- **2026-09-09 T21f CLI ZIP ingest** — `python -m cozmo_floorplan run` accepts a Cozmo Capture `.zip`, unpacks it, reconstructs RoomPlan JSON, and writes a structured failure for incomplete archives. Signed install remains T21g.

- **2026-09-09 T21e capture job ZIP** — App writes `manifest.yaml` + `lidar/roomplan.json` + per-room `.r3d` as a folder and shareable ZIP; Python inspects, rejects incomplete archives, and extracts into `load_job`. Simulator, unsigned iPhoneOS, and test-target builds succeed. Signed install remains T21g.

- **2026-09-09 T21c raw ARKit LiDAR recorder** — 2 Hz `sceneDepth` sampling during RoomPlan scans, JPEG RGB plus LZFSE depth/confidence, XYZW camera-to-world poses, Record3D-compatible `.r3d` ZIP writer, live frame count, multi-file share, and archive contract tests. Simulator, unsigned iPhoneOS, and test-target builds succeed. Signed install remains T21g.

- **2026-09-09 T21b multi-room RoomPlan capture/export** — Named session accumulation, Apple `StructureBuilder` merge, portable `rooms[]` export with shared-wall/`connectsRoomIds` annotation, merge-failure fallback, contract tests, bundle-id Info.plist, and operator README. Simulator and unsigned generic iPhoneOS builds succeed. Signed install remains T21g.
- **2026-09-09 T21a iOS RoomPlan exporter foundation** — Buildable iOS 17 SwiftUI app, native RoomPlan capture, explicit portable JSON v1 conversion, atomic local export/system share, unsupported-device guard, compiled contract test, operator README, and code map. Simulator app and test targets compile; on-phone sensing/install remains T21b.
- **2026-09-09 T20c final benchmark runner** — Safe root-relative benchmark manifest, three-tier/repeat orchestration, per-tier JSON/SVG/eval output, readiness checks for truth/repeat/incumbent/damage, JSON and Markdown status artifacts, CLI/Make target, templates, and pending/complete tests. Current private audit runs all three tiers and reports exactly four missing evidence classes.
- **2026-09-09 T7g conservative video FloorPlan** — Backward-compatible sidecar v1.2, rotated Manhattan yaw search, floor/ceiling and camera-bracketing wall qualification, shared-world-frame enforcement, candidate-stage intervals, schema-valid room/wall conversion, main-pipeline return/enrichment, and synthetic rejection/integration tests. Openings, adjacency, interval calibration, and real ±3% evidence remain media-dependent.
- **2026-09-09 T7f calibrated video triangulation** — Sidecar v1.1 display intrinsics and camera-axis contract, accepted-segment/exact-pose guards, calibrated two-view metric triangulation, depth/reprojection/ray-angle filters, voxelization, sparse floor/wall support diagnostics, and synthetic metric regressions. Schema v1.0 and current native MP4s remain uncalibrated; no wall dimensions emitted.
- **2026-09-09 T8b photo overlap graph** — Bounded ORB features, mutual matching, seeded homography/fundamental support, spatial-coverage gates, within-room components, conservative cross-room candidates, synthetic graph tests, and measured real-capture refusal. Current rooms have 4/6/6 components and no connector candidate; no metric claim.
- **2026-09-09 T7e metric pose sidecar/alignment** — Exact sampled source-frame/timestamp identity, strict versioned metre/camera-to-world sidecars, unit-quaternion validation, per-segment 3D similarity alignment, degeneracy/RMSE rejection, and synthetic metric recovery tests. Current MP4s remain unitless because no sidecars exist.
- **2026-09-09 T7d scale-free video trajectory** — Shared ORB/fundamental correspondences, assumed-intrinsics essential poses, unit-normalized translation directions, explicit segment breaks/restarts, two-view and graph-break tests, and real two-video diagnostics. No metric claim.
- **2026-09-09 T7c video feature-track gate** — Bounded ORB extraction, ratio matching, seeded fundamental/homography RANSAC, motion/parallax/coverage gates, named rejection counts, accepted multi-depth synthetic motion, rejected pure rotation/blank frames, and real two-video diagnostics. No metric claim.
- **2026-09-09 T7b multi-video orientation-aware ingest** — All room walkthroughs sampled in stable order, filename-stem identity, explicit quarter-turn normalization, per-video sidecars, ambiguous global-sidecar refusal, real duration/frame diagnostics, and three added tests. No metric geometry inferred.
- **2026-09-09 T6b3 Record3D partial FloorPlan** — Evidence-gated door/window occupancy profiles, schema-valid rooms/walls/ceilings/areas/openings, deliberately uncalibrated intervals, per-scan provenance, disconnected registration warnings, real JSON/SVG output, and four focused tests. Ground-truth hardening remains T6.
- **2026-09-09 T6b2 Record3D room-plane candidates** — Horizontal floor/ceiling bands, vertically persistent clutter rejection, 0.5-degree Manhattan yaw search, camera-bracketing wall peaks, real three-scan diagnostics, and four synthetic regression tests. No accuracy claim without tape truth.
- **2026-09-09 T6b1 Record3D metric world clouds** — Deterministic frame sampling, RGB-to-depth intrinsic scaling, OpenGL camera back-projection, normalized XYZW pose rotation, camera-to-world transformation, confidence/depth filtering, 2.5 cm voxel centroids, real-capture diagnostics, and four focused tests.
- **2026-09-09 T6a Record3D decode/validation** — Real `.r3d` ZIP indexing, metadata validation, portable/macOS LZFSE decoding, typed RGB-D frames, bounded integrity summaries, private manifests, and four tests. Three uploaded scans validate; raw plane extraction remains T6b.
- **2026-09-09 T20b compliance audit** — Normalized the interval-contract row to `done` and added a test that locks all 27 requirement ids, ordering, uniqueness, and allowed statuses.
- **2026-09-09 T17a protocol handoff** — One-page Route 2 operator card, copyable per-tier manifests checked through the production loader, and a device matrix that separates capture eligibility from current format support and measured accuracy.
- **2026-09-09 T19 fix loop** — Frozen checksum-locked before and after bundles around one declared status-semantics fix; `pipeline_yield` moved exactly as predicted from fail/partial to pass/ok, with unchanged non-target gates and a readable diff.
- **2026-09-09 T19a before freeze** — Declared the failing `pipeline_yield` gate, hypothesis, fix, and numeric prediction; pinned commit `523ceea`; stored JSON/SVG/ablation/eval artifacts with SHA-256 verification and isolated-worktree reproduction commands.
- **2026-09-09 T8a ingest** — Stable per-room photo discovery, official 2–8 count enforcement, real decode/size validation, generated-JPEG tests, and structured refusal until metric SfM/scale/adjacency exist.
- **2026-09-08 T7 ingest** — Video job sampling (OpenCV, ~2 Hz) and pose-sidecar detection. Structured failure until metric VO; no guessed centimetres. Generated mp4 tests, no private capture required.
- **2026-09-09 T9** — Plane-anchored shared-opening drift correction, SE(2) constraint graph, correction-on/poses-as-is CLI artifacts, residual metadata, eval wiring, and synthetic 20 cm drift regression. Shared walls stay with the originating room so the gap actually closes.
- **2026-09-08 T16** — Live OpenAI Responses tool-calling agent plus transactional deterministic fallback; strict damage, concealed-rule, and scope tools; metric observation contract; live synthetic smoke test.
- **2026-09-08 T15** — Deterministic whole-property SVG renderer, paired atomically-written JSON/SVG artifacts, measured wall intervals, openings, scale bar, status/provenance summary, and failed-run placeholder.
- **2026-09-08 T14** — Official-gate eval package and CLI: red empty predictions, openings, ceilings, repeatability, drift ablation, photo stitch, photo/video walls, calibration, yield, and LiDAR head-to-head.
- **2026-09-08 T13** — Modular installable CLI, normalized job loading, schema validation, atomic `floorplan.json`, structured failure paths, code map, and command tests.
- **2026-09-08 T12** — FloorPlan IR v0.2: required interval-bearing measurements, damage, concealed-rule flags, scope, drift metadata, fixture migration, and contract tests.
- **2026-09-08** — Max-score retarget: do not pre-concede tiers/gates; cuts only via `docs/cut-later.md`. T21 iOS exporter added as parallel track.
- **2026-09-08 T4** — Ingest: plan/roadmap/TASKS aligned; ADR; product/compliance/route/device docs.
- **2026-09-08 T1** — Official case study in `docs/takehome.md`.
- **2026-09-07 T0** — Orchestration kit.
- **2026-09-07 T2** — Synthetic two-room fixture + schema tests.
