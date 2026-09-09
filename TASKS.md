# Task queue

Agents: pick the highest item whose status is `todo` and whose Blocked-by is empty or done. Check boxes in the same edit as the work. Move finished items to **Done** with a date.

Status key: `todo` · `doing` · `blocked` · `done`

Product: local CLI + **disclosed LLM tool-calling agent**. Score policy: max every official row (`docs/cut-later.md`). Route 2 walk-in; Route 1 parallel (T21). See `docs/product.md` and `docs/agent-layer.md`.

---

## Capture status (private upload arrived 2026-09-09)

Three room-level Record3D scans, 23 photos across three room folders, and two
room videos are now under gitignored `data/private/`. The pre-shoot code boundary
is complete. The capture is not complete: drawing-room video, a connector/hallway,
repeat captures, tape/laser ground truth, damage evidence, and incumbent exports
remain missing. Do **not** invent centimetres or mark a scored gate pass without
those eval inputs.

| ID | Can finish now? | What to do without uploads |
| --- | --- | --- |
| **T21** | **T21a done** | Thin iOS RoomPlan exporter. Xcode 26.6 is active; the single-room capture/export foundation builds. Device install and multi-room T21b remain. |
| **T10** | **Draft done** | Architecture, tier design, drift, error budget, calibration, agent, fix loop, and known failures are drafted. Final real benchmark tables wait on T3. |
| **T20** | **Pre-shoot code done** | T20a reproduction, T20b audit, and T20c one-command benchmark/readiness runner are verified; measured coverage remains T3-dependent. |
| **T17** | **Protocol stage done** | Route 2 operator card, loader-checked per-tier templates, and honest runtime/device matrix ship; measured intervals remain T3-dependent. |
| T8 remainder | Overlap measured | Current photo graphs fail connectivity. Metric SfM, scale, adjacency, and ±8% walls need overlapping reshoots. |
| T7 remainder | Calibrated path implemented | T7b–T7g can emit conservative rooms from calibrated v1.2 pose sidecars. Current Camera videos lack sidecars; openings, shared constraints, calibration, and ±3% eval need media. |

**Still evidence-blocked:** measured T17 intervals, T18 Polycam/magicplan,
repeatability gates, and T11 walk-in. T6 raw Record3D, T7 VO, and T8 SfM can now
advance against the partial upload.

---

## Now

| ID | Status | Task | Blocked-by | Needs media? | Notes |
| --- | --- | --- | --- | --- | --- |
| T0 | done | Orchestration kit | — | no | 2026-09-07 |
| T1 | done | Official prompt in `docs/takehome.md` | human | no | 2026-09-08 |
| T2 | done | Synthetic two-room fixture | — | no | 2026-09-07 |
| T4 | done | Reconcile plan with official prompt | T1 | no | 2026-09-08 ingest |
| T3 | doing | Human benchmark capture | human + Pro phone | **yes — partial upload present** | Three rooms present; missing connector, repeats, GT, incumbent, damage evidence, and one video |
| T6 | doing | LiDAR export → FloorPlan | — | **present** | T6a–T6b3 raw `.r3d` partial IR works; calibration, repeatability, shared-opening registration, and GT hardening remain |
| T9 | done | Stitch + drift correction + on/off ablation | T6 | no | 2026-09-08 plane-anchored snap; shared walls stay with first owner |
| T7 | doing | Video path | T6 | two of three room videos present | T7b–T7g calibrated room/FloorPlan path done; current videos lack sidecars, and openings/stitch/calibrated ±3% evidence remain |
| T8 | doing | Photos path, 2–8 stills, folder stitch | — | 23 photos present but overlap fails | T8a ingest + T8b overlap graph done; current rooms have 4/6/6 components and zero connector candidates; reshoot blocks SfM |
| T21 | doing | Route 1: thin iOS RoomPlan/ARKit exporter + 10-min install | — | no | T21a single-room portable JSON app builds; T21b multi-room + signed phone install remain. Scored route stays Route 2 until install works |
| T17 | doing | Device matrix + capture-route polish | T3 | **yes** (measured intervals) | T17a protocol/templates done; walk-in validation and measured rows wait on T3 |
| T18 | todo | Head-to-head vs Polycam or magicplan (2 rooms, LiDAR) | T3, T6 | **yes** | Beat/tie ≥ 70% shared dims |
| T10 | doing | Technical report ≤ 6 pages + benchmark tables | T19 | draft **no**; tables **yes** | 1,805-word engineering draft complete; real benchmark/repeat/incumbent/timing tables remain T3-dependent |
| T20 | doing | README 15 min + reproduction bundle + compliance matrix | T10 | partial **no**; measured rows **yes** | T20a–T20c code/docs done; final real bundle and coverage remain T3-dependent |
| T11 | todo | Walk-in rehearsal on a new room, all three tiers | T20 | **yes** | Follow submitted capture route |

---

## Unblocked detail

### T3 — benchmark capture (human, start now)

Not optional. Composition from the prompt:

- 3+ rooms plus a connector
- Same spaces at **photos, video, LiDAR**
- Photos = per-room folders, **8 stills** per room (protocol maximum — max-score capture)
- One furnished room with **two staged damage classes**
- One room **twice at LiDAR** (required). Also twice at photos and twice at video if time.
- Laser or tape on walls, openings, **ceilings**; photo of tape
- Polycam **or** magicplan export on two rooms (name version). Do not use that app as the capture route.

Protocol for *our* capture: `docs/capture-protocol.md`. Protocol *they* will use until T21 ships: `docs/capture-route.md`.

Hardware: Harsh has **iPhone 17 Pro** (LiDAR). Walk-in may still be non-Pro.

Privacy: no faces/docs in git. Large binaries: Git LFS or `data/private/` gitignored + note the path in `HANDOFF.md`.

### Next engineering task

**Pre-shoot Python boundary reached.** T21a is now complete because full Xcode
became available. The next media-independent stage is T21b multi-room capture
and a signed 10-minute phone-install rehearsal. Separately, complete T3 and run
`make benchmark` to unlock T6/T7/T8 calibration and the remaining scored
evidence. Do not loosen T8b thresholds to force the current photos to pass.

### Media-ready freeze sequence

These are the remaining code stages that can be prepared before the final
benchmark upload. Complete them one reviewable stage at a time; real accuracy
claims, threshold calibration, and final evidence still wait on T3 media and
ground truth.

1. **T7f (done)** — Calibrated sidecar-backed sparse metric triangulation and
   diagnostic floor/wall candidates.
2. **T7g (done)** — Convert accepted video surface evidence into conservative
   room geometry and the shared FloorPlan IR.
3. **T8c (blocked on photo reshoot)** — Incremental per-room photo SfM after
   every overlap graph connects.
4. **T8d (blocked on T8c + scale evidence)** — Photo Manhattan layout, metric
   scale, and calibrated uncertainty.
5. **T8e (blocked on connector evidence)** — Cross-room photo registration and
   connected whole-property stitch.
6. **T20c (done)** — One-command final benchmark/evidence runner with explicit
   pending results when required capture or ground truth is absent.

After these stages, remaining work is expected to be media ingestion, measured
evaluation/calibration, and evidence-driven fixes rather than planned feature
scaffolding. Minor fixes after real captures remain normal and allowed.

---

## Done

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
