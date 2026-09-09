# Code map

This is the maintained guide to what each implementation file owns. Update it whenever a task adds, moves, or removes a code module. Architecture and scoring rationale stay in the other `docs/` files; this page answers “where does the code live?”

## Package and command

| File | Responsibility |
| --- | --- |
| `pyproject.toml` | Installable Python package metadata and the optional `cozmo-floorplan` console command. |
| `src/cozmo_floorplan/__main__.py` | Entry point for the required `python -m cozmo_floorplan ...` command. |
| `src/cozmo_floorplan/cli.py` | CLI arguments, exit codes, and the outer error boundary; writes the normal artifacts plus a regenerable correction-off JSON when stitching applies. |
| `src/cozmo_floorplan/pipeline.py` | Application orchestration boundary. Dispatches LiDAR reconstruction + drift correction/ablation, then claims enrichment; video jobs go through T7 ingest and fail structurally until metric VO exists. |
| `src/cozmo_floorplan/config.py` | Shared artifact filenames (including the drift-ablation filename), schema version, supported tiers, directory conventions, and exit-code constants. |
| `src/cozmo_floorplan/errors.py` | Expected domain exception types. Keeps error classification out of command and I/O code. |

## Contract and I/O

| File | Responsibility |
| --- | --- |
| `src/cozmo_floorplan/io/job.py` | Reads `manifest.yaml`, checks the tier-specific job directory, and produces immutable normalized job metadata. |
| `src/cozmo_floorplan/io/photos.py` | Discovers stable per-room image sets, decodes every supported image, and records immutable path/dimension metadata. |
| `src/cozmo_floorplan/io/video.py` | Discovers every MP4/MOV walkthrough, reads typed container/display metadata, disables backend auto-rotation, and returns bounded display-oriented RGB samples with stable video, source-frame, and timestamp identity. |
| `src/cozmo_floorplan/io/video_poses.py` | Strictly parses versioned metric camera-to-world sidecars: v1.1 adds display intrinsics/camera axes and v1.2 adds scale source/shared world-frame identity, while all versions validate frame/time keys, positions, and quaternions. |
| `src/cozmo_floorplan/io/record3d.py` | Validates `.r3d` ZIP members and metadata, indexes matched modalities, and decodes typed RGB/depth/confidence frames. |
| `src/cozmo_floorplan/io/output.py` | Reusable atomic UTF-8 text and JSON persistence, plus the compatibility `floorplan.json` writer. |
| `src/cozmo_floorplan/io/artifacts.py` | Validates once, renders in memory, and persists the paired `floorplan.json` and `floorplan.svg` run artifacts. |
| `src/cozmo_floorplan/floorplan.py` | Creates stable FloorPlan documents, including the schema-valid failed result used before adapters exist. |
| `src/cozmo_floorplan/schema.py` | Loads and compiles the canonical JSON Schema and validates generated documents. |
| `src/cozmo_floorplan/utils/paths.py` | Finds repository runtime assets and handles the explicit schema-path override. |
| `src/cozmo_floorplan/utils/env.py` | Loads simple local `.env` values without overriding variables already exported by the caller. |
| `src/cozmo_floorplan/utils/lzfse.py` | Decodes Record3D LZFSE blocks through python-lzfse or the macOS system Compression framework and enforces exact output sizes. |
| `src/cozmo_floorplan/utils/sampling.py` | Produces deterministic, inclusive evenly spaced frame indices without capture-specific policy. |
| `src/cozmo_floorplan/utils/images.py` | Applies explicit clockwise quarter-turn transformations to image arrays without capture-specific policy. |
| `docs/schemas/floorplan.schema.json` | Canonical external data contract. This remains the single schema source of truth. |

## Geometry and LiDAR reconstruction

| File | Responsibility |
| --- | --- |
| `src/cozmo_floorplan/geom/transforms.py` | Parses RoomPlan pose encodings and projects surface width axes onto the world x-z floor plane. |
| `src/cozmo_floorplan/geom/polygons.py` | Polygonizes unordered wall segments, with a reported convex-hull fallback for incomplete loops. |
| `src/cozmo_floorplan/geom/se2.py` | Reusable immutable SE(2) transforms, frame alignment, angles, and point distances for planar stitching. |
| `src/cozmo_floorplan/geom/rotations.py` | Normalizes Record3D XYZW quaternions and constructs camera-to-world 3D rotation matrices. |
| `src/cozmo_floorplan/geom/segments.py` | Projects batches of planar points into along-segment and normal coordinates for wall occupancy analysis. |
| `src/cozmo_floorplan/io/roomplan.py` | Parses the portable single- or multi-room RoomPlan JSON contract into typed immutable capture objects. |
| `src/cozmo_floorplan/recon/lidar_config.py` | LiDAR confidence scores, uncertainty widths, and recognized RoomPlan filenames. |
| `src/cozmo_floorplan/recon/measurements.py` | Builds interval-bearing LiDAR and derived diagnostic measurements without treating transforms as exact. |
| `src/cozmo_floorplan/recon/lidar.py` | Converts RoomPlan surfaces into FloorPlan v0.2 and orchestrates raw Record3D validation, metric clouds, plane fitting, supported openings, and partial IR conversion. |
| `src/cozmo_floorplan/recon/record3d_config.py` | Keeps Record3D validation, metric-cloud, plane, opening-profile, and uncalibrated output-interval policies out of I/O and algorithm code. |
| `src/cozmo_floorplan/recon/record3d_validation.py` | Decodes bounded representative RGB-D frames and reports valid-depth coverage, range, and camera-trajectory extent without claiming walls. |
| `src/cozmo_floorplan/recon/record3d_points.py` | Back-projects filtered depth along camera negative-Z, applies metric camera poses, and computes deterministic world-space voxel centroids with audit counts. |
| `src/cozmo_floorplan/recon/record3d_planes.py` | Detects floor/ceiling bands, rejects short vertical clutter, searches a Manhattan yaw, and selects four wall candidates that bracket the camera path. |
| `src/cozmo_floorplan/recon/record3d_openings.py` | Detects door/window candidates from sparse lower/middle wall occupancy only when sill or lintel support survives. |
| `src/cozmo_floorplan/recon/record3d_measurements.py` | Builds Record3D measurement objects with disclosed, deliberately uncalibrated candidate-stage intervals. |
| `src/cozmo_floorplan/recon/record3d_floorplan.py` | Converts per-archive room/opening candidates into shared FloorPlan rooms, walls, openings, provenance, and honest partial-state warnings. |
| `docs/formats/roomplan-json.md` | Public input contract for the tested RoomPlan JSON adapter. |
| `docs/formats/record3d.md` | Documents the tested raw Record3D archive contract, decompression path, and current plane-extraction boundary. |
| `src/cozmo_floorplan/recon/photos_config.py` | Official ingest limits plus immutable ORB, robust-geometry, within-room, and cross-room overlap thresholds. |
| `src/cozmo_floorplan/recon/photo_features.py` | Decodes and bounds photos, extracts ORB observations, retains mutual ratio matches, and measures seeded homography/fundamental support and spatial coverage. |
| `src/cozmo_floorplan/recon/photo_overlap.py` | Builds within-room connected components and conservative cross-room connector candidates with named pair-rejection evidence. |
| `src/cozmo_floorplan/recon/photos.py` | Photo-tier adapter: validates folders, runs the overlap graph, returns actionable `insufficient_overlap`, and refuses metric output until SfM, adjacency, and scale exist. |
| `docs/formats/photo-job.md` | Public per-room photo job layout and current metric-reconstruction boundary. |
| `src/cozmo_floorplan/recon/video_config.py` | Immutable video ingest, tracking, trajectory, sidecar alignment, triangulation, surface, room-envelope, and candidate-output policies. |
| `src/cozmo_floorplan/recon/video_features.py` | Shared bounded ORB extraction, Hamming ratio matching, and seeded fundamental-matrix correspondence utility used by tracking and pose recovery. |
| `src/cozmo_floorplan/recon/video_tracks.py` | Converts shared correspondences into motion, homography-residual parallax, spatial-coverage, and named track rejection diagnostics. |
| `src/cozmo_floorplan/recon/video_trajectory.py` | Recovers assumed-intrinsics essential-matrix poses, chains unitless camera steps, and explicitly splits/restarts trajectories across failed edges. |
| `src/cozmo_floorplan/recon/video_pose_alignment.py` | Fits an orientation-preserving 3D similarity per local trajectory segment using exact source-frame/timestamp matches and rejects sparse, degenerate, or high-RMSE alignments. |
| `src/cozmo_floorplan/recon/video_triangulation.py` | Triangulates robust correspondences only inside accepted metric segments using v1.1 calibrated projection matrices, then filters depth, reprojection error, ray angle, and voxel duplicates. |
| `src/cozmo_floorplan/recon/video_surfaces.py` | Finds support-qualified horizontal and vertical coordinate bands in sparse y-up video points. |
| `src/cozmo_floorplan/recon/video_rooms.py` | Searches Manhattan yaw and requires floor, ceiling, and two camera-bracketing wall candidates on each planar axis before defining a room envelope. |
| `src/cozmo_floorplan/recon/video_measurements.py` | Builds interval-bearing video lengths and areas with explicitly uncalibrated candidate-stage uncertainty. |
| `src/cozmo_floorplan/recon/video_floorplan.py` | Converts accepted calibrated video room evidence into schema-valid partial FloorPlan rooms/walls while enforcing one shared sidecar world frame and inventing no openings. |
| `src/cozmo_floorplan/utils/point_clouds.py` | Provides validated deterministic metric voxel centroids for sparse reconstruction outputs. |
| `src/cozmo_floorplan/recon/video.py` | Video-tier adapter: samples every walkthrough, runs tracking/alignment/triangulation/room fitting, returns the shared IR only after every metric gate succeeds, and otherwise returns an actionable structured refusal. |
| `docs/formats/video-job.md` | Public video job layout and metric boundary. |

## Stitching and drift correction

| File | Responsibility |
| --- | --- |
| `src/cozmo_floorplan/stitch/config.py` | Immutable plane-anchor method name and residual uncertainty settings. |
| `src/cozmo_floorplan/stitch/constraints.py` | Builds adjacent-room constraints from shared openings and the nearest corresponding room wall; measures opening-frame gaps. |
| `src/cozmo_floorplan/stitch/pose_graph.py` | Anchors the first room and accumulates reachable room poses across the opening-constraint graph. |
| `src/cozmo_floorplan/stitch/apply.py` | Applies each room’s SE(2) to its polygon; walls move with their first listed owner so shared surfaces stay with the root room. Rebuilds stitch-edge diagnostics. |
| `src/cozmo_floorplan/stitch/correct.py` | Orchestrates correction-on and poses-as-is modes, residual metadata, disconnected-room warnings, and honest no-constraint handling. |
| `src/cozmo_floorplan/stitch/__init__.py` | Exposes drift correction as the stitching package API. |

## Evaluation

| File | Responsibility |
| --- | --- |
| `src/cozmo_floorplan/eval/config.py` | Official numerical thresholds plus the explicitly labeled internal interval-calibration tolerance. |
| `src/cozmo_floorplan/eval/models.py` | Deterministic `GateResult` and `EvaluationReport` objects serialized into `eval.json`. |
| `src/cozmo_floorplan/eval/matching.py` | ID-first entity matching with Hungarian geometry fallbacks; keeps array order and arbitrary predicted IDs out of scoring. |
| `src/cozmo_floorplan/eval/measurements.py` | Reads v0.2 measurement values and computes confidence-interval coverage. |
| `src/cozmo_floorplan/eval/metrics.py` | Reusable absolute, relative, median, and p95 error calculations. |
| `src/cozmo_floorplan/eval/geometry.py` | Whole-property footprint, room-overlap, and adjacency calculations. |
| `src/cozmo_floorplan/eval/evaluator.py` | Composes official gates: openings, ceilings, repeatability, drift ablation, photo stitch, tier wall accuracy, calibration, yield, and head-to-head. |
| `src/cozmo_floorplan/eval/io.py` | Loads schema-valid FloorPlans and atomically writes `eval.json`. |

## Fix-loop evidence

| File | Responsibility |
| --- | --- |
| `src/cozmo_floorplan/fix_loop/config.py` | Required frozen before/after artifact names for the fix-loop bundle. |
| `src/cozmo_floorplan/fix_loop/verify.py` | Verifies safe bundle paths, SHA-256 hashes, the predicted gate delta, unchanged non-target gates, and status-only FloorPlan change; also provides a local verification command. |
| `src/cozmo_floorplan/fix_loop/__init__.py` | Declares the fix-loop verification package. |
| `data/fix-loop/manifest.json` | Pins the case id, source commit, expected exit codes, target gate/prediction, artifact hashes, and pending after state. |
| `data/fix-loop/before/` | Immutable baseline FloorPlan, SVG, drift-off ablation, and evaluation report. |
| `data/fix-loop/after/` | Immutable shipped-result FloorPlan, SVG, drift-off ablation, and evaluation report. |
| `data/fix-loop/diff.md` | Human-readable code-policy and measured before/predicted/after delta. |
| `data/fix-loop/README.md` | Verification and isolated-worktree regeneration commands for the frozen baseline. |
| `docs/fix-loop.md` | One-page declaration: worst gate, evidence-backed hypothesis, intended fix, prediction, and reproduction contract. |

## Rendering

| File | Responsibility |
| --- | --- |
| `src/cozmo_floorplan/render/config.py` | Immutable palette, spacing, stroke, and minimum-canvas settings for SVG output. |
| `src/cozmo_floorplan/render/layout.py` | Computes geometry bounds and maps centimetre floor coordinates into the y-down SVG canvas without changing scale. |
| `src/cozmo_floorplan/render/svg.py` | Builds the accessible, self-contained whole-property SVG: rooms, measured wall intervals, openings, scale bar, status, and provenance summary. |
| `src/cozmo_floorplan/render/__init__.py` | Exposes the renderer as a small package API. |

## Claims agent and tools

| File | Responsibility |
| --- | --- |
| `src/cozmo_floorplan/agent/config.py` | Provider environment settings, allowed damage classes, concealed-rule ids, and allowed scope actions. |
| `src/cozmo_floorplan/agent/prompts.py` | Versioned model instructions and the non-secret plan/observation context. |
| `src/cozmo_floorplan/agent/tool_definitions.py` | Strict OpenAI-compatible JSON schemas for every callable FloorPlan tool. |
| `src/cozmo_floorplan/agent/tools.py` | Validates tool arguments and exclusively owns claims mutations and metric quantity copying. |
| `src/cozmo_floorplan/agent/models.py` | Immutable damage-observation and agent-run records shared across implementations. |
| `src/cozmo_floorplan/agent/observations.py` | Parses and validates optional `damage_observations.json` metric proposals. |
| `src/cozmo_floorplan/agent/images.py` | Safely loads bounded job-relative image evidence for vision input. |
| `src/cozmo_floorplan/agent/openai_agent.py` | Stateless OpenAI Responses API function-calling loop with structured tool errors and `store: false`. |
| `src/cozmo_floorplan/agent/fallback_agent.py` | Deterministic rule agent that uses the exact same mutation tools without network access. |
| `src/cozmo_floorplan/agent/orchestrator.py` | Selects live/fallback mode transactionally, rolls back partial live mutations, validates output, and records audit metadata. |
| `src/cozmo_floorplan/agent/status_policy.py` | Separates fallback audit warnings from run-health semantics: explicit successful fallback preserves status, while automatic/provider fallback degrades it. |
| `src/cozmo_floorplan/agent/__init__.py` | Exposes claims enrichment to the main pipeline. |
| `docs/formats/damage-observations.md` | Input boundary between calibrated CV/manual proposals and agent classification/policy decisions. |

## Reproduction

| File | Responsibility |
| --- | --- |
| `src/cozmo_floorplan/reproduction/config.py` | Stable public fixture paths, required output names, and expected pass/missing-evidence gates. |
| `src/cozmo_floorplan/reproduction/commands.py` | Runs visible subprocesses and fails when a CLI exit differs from its documented contract. |
| `src/cozmo_floorplan/reproduction/verify.py` | Validates the generated FloorPlan, entity counts, artifact set, and expected synthetic gate states. |
| `src/cozmo_floorplan/reproduction/runner.py` | Orchestrates deterministic run, intentionally red overall eval, generated-artifact checks, fix-loop hash verification, and elapsed-time reporting. |
| `src/cozmo_floorplan/reproduction/__init__.py` | Declares the reproduction package. |
| `tests/test_reproduction.py` | Exercises the full public reproduction in a temporary output directory and rejects unexpected subprocess exits. |

## Final benchmark runner

| File | Responsibility |
| --- | --- |
| `src/cozmo_floorplan/benchmark/config.py` | Stable benchmark manifest/report names, tier order, and default capture-root paths. |
| `src/cozmo_floorplan/benchmark/manifest.py` | Loads path-only `benchmark.yaml`, preserves documented defaults when absent, and prevents paths escaping the capture root. |
| `src/cozmo_floorplan/benchmark/readiness.py` | Audits three tier jobs, tape truth, required LiDAR repeat, incumbent, and staged-damage evidence as ready or pending. |
| `src/cozmo_floorplan/benchmark/report.py` | Renders the machine-readable benchmark result as a concise Markdown checklist. |
| `src/cozmo_floorplan/benchmark/runner.py` | Runs available jobs/repeats, writes tier artifacts/evals, and emits one honest status bundle without treating absent evidence as zero. |
| `data/templates/benchmark.yaml` | Joins separate tier, truth, repeat, and incumbent inputs through safe capture-root-relative paths. |
| `tests/test_benchmark.py` | Tests pending roots, path containment, complete mocked three-tier orchestration, and successful pending-audit CLI behavior. |

## Tests and fixtures

| File | Responsibility |
| --- | --- |
| `tests/test_cli.py` | Tests job validation, structured failures, schema-valid output, and the exact module command. |
| `tests/test_eval.py` | Tests red empty predictions, detection misses/phantoms, repeatability evidence, photo stitching, head-to-head, and the eval command. |
| `tests/test_schema.py` | Tests the FloorPlan v0.2 contract and its required interval/claims fields. |
| `data/fixtures/synthetic_two_room/` | Small public-safe metric truth used by schema and later evaluation tests. |
| `data/fixtures/roomplan_two_room/` | Synthetic RoomPlan-format LiDAR job that reconstructs the same metric room dimensions. |
| `tests/test_lidar.py` | Tests single/multi-room discovery, RoomPlan conversion, intervals, metric gates, CLI output, and honest unsupported fallbacks. |
| `tests/test_record3d.py` | Tests Record3D metadata/index validation, typed RGB-D decoding, integrity summaries, and exact LZFSE output checks. |
| `tests/test_record3d_points.py` | Tests deterministic frame sampling, quaternion rotation, metric back-projection, pose application, voxel bounds, and invalid configuration. |
| `tests/test_record3d_planes.py` | Tests rotated-room floor/ceiling and wall fitting, low-furniture rejection, and malformed/incomplete geometry refusal. |
| `tests/test_record3d_openings.py` | Tests supported door/window gap detection and ensures solid walls do not create phantom openings. |
| `tests/test_record3d_floorplan.py` | Tests schema-valid interval-bearing Record3D conversion and explicit multi-archive registration warnings. |
| `tests/test_render.py` | Tests parseable whole-property SVG, dimensions, openings, deterministic output, XML escaping, and failed-run placeholders. |
| `tests/test_photos.py` | Tests room discovery, the official 2–8 count, corrupt-image rejection, multi-room ordering, and honest metric refusal using generated JPEGs. |
| `tests/test_fix_loop.py` | Validates the frozen failing gate and ensures checksum verification catches artifact tampering. |
| `tests/test_compliance.py` | Ensures all 27 compliance rows remain present, ordered, unique, and within the documented status vocabulary. |
| `tests/test_agent.py` | Tests fallback and mocked-live agents, metric ownership, rule validation, transactional rollback, and schema-valid claims output. |
| `tests/test_agent_status_policy.py` | Unit-tests explicit versus automatic fallback status semantics and ensures fallback never upgrades an already-partial run. |
| `tests/test_stitch.py` | Tests correction-on/off metadata, ablation artifacts, injected 20 cm opening-gap closure, and the drift eval gate. |
| `tests/test_video.py` | Tests empty/short jobs, multi-video identity, per-video versus ambiguous sidecars, display rotation, generated-MP4 sampling, honest refusal, and the mocked calibrated adapter success path. |
| `tests/test_video_tracks.py` | Tests accepted multi-depth motion, homography-dominant/pure-rotation rejection, and featureless-frame rejection without crashes. |
| `tests/test_video_trajectory.py` | Tests two-view rotation/translation-direction recovery, explicit graph breaks and local segment restarts, unitless chaining, and the too-short boundary. |
| `tests/test_video_pose_alignment.py` | Tests strict metric-sidecar parsing, units/frame/quaternion rejection, exact frame/time matching, similarity scale recovery, metric positions, and timestamp-mismatch refusal. |
| `tests/test_video_triangulation.py` | Tests calibrated world-point recovery, reprojection rejection, v1 calibration and accepted-segment guards, and sparse floor/wall candidate support. |
| `tests/test_video_rooms.py` | Tests rotated Manhattan room recovery and refusal when complete plane support is absent. |
| `tests/test_video_floorplan.py` | Tests schema-valid video measurements, shared-world-frame enforcement, and successful video-result routing through the main pipeline. |
| `tests/test_photo_overlap.py` | Tests connected transformed views, unrelated-room connector rejection, and featureless images remaining explicit disconnected components. |
| `tests/test_capture_templates.py` | Loads every public handoff template through the production job loader and checks that tiers use separate job ids/directories. |
| `tests/conftest.py` | Forces offline fallback during tests so local API keys are never used and tests never spend credits. |

## Planned modules

Later tasks add real modules only when they contain working behavior:

- Metric SfM, Manhattan regularization, scale, and calibrated intervals inside `recon/photos.py` once real capture evidence exists.
- Additional `geom/` modules — point-cloud and plane operations as required.

Do not create empty placeholders for these directories. Add each one with its implementing task and document its files here.
