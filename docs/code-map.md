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
| `src/cozmo_floorplan/io/video.py` | Discovers MP4/MOV walkthroughs and samples RGB frames with OpenCV at a bounded rate. |
| `src/cozmo_floorplan/io/output.py` | Reusable atomic UTF-8 text and JSON persistence, plus the compatibility `floorplan.json` writer. |
| `src/cozmo_floorplan/io/artifacts.py` | Validates once, renders in memory, and persists the paired `floorplan.json` and `floorplan.svg` run artifacts. |
| `src/cozmo_floorplan/floorplan.py` | Creates stable FloorPlan documents, including the schema-valid failed result used before adapters exist. |
| `src/cozmo_floorplan/schema.py` | Loads and compiles the canonical JSON Schema and validates generated documents. |
| `src/cozmo_floorplan/utils/paths.py` | Finds repository runtime assets and handles the explicit schema-path override. |
| `src/cozmo_floorplan/utils/env.py` | Loads simple local `.env` values without overriding variables already exported by the caller. |
| `docs/schemas/floorplan.schema.json` | Canonical external data contract. This remains the single schema source of truth. |

## Geometry and LiDAR reconstruction

| File | Responsibility |
| --- | --- |
| `src/cozmo_floorplan/geom/transforms.py` | Parses RoomPlan pose encodings and projects surface width axes onto the world x-z floor plane. |
| `src/cozmo_floorplan/geom/polygons.py` | Polygonizes unordered wall segments, with a reported convex-hull fallback for incomplete loops. |
| `src/cozmo_floorplan/geom/se2.py` | Reusable immutable SE(2) transforms, frame alignment, angles, and point distances for planar stitching. |
| `src/cozmo_floorplan/io/roomplan.py` | Parses the portable single- or multi-room RoomPlan JSON contract into typed immutable capture objects. |
| `src/cozmo_floorplan/recon/lidar_config.py` | LiDAR confidence scores, uncertainty widths, and recognized RoomPlan filenames. |
| `src/cozmo_floorplan/recon/measurements.py` | Builds interval-bearing LiDAR and derived diagnostic measurements without treating transforms as exact. |
| `src/cozmo_floorplan/recon/lidar.py` | Converts RoomPlan rooms, walls, openings, and adjacency into FloorPlan v0.2; detects unsupported Record3D/USDZ inputs. |
| `docs/formats/roomplan-json.md` | Public input contract for the tested RoomPlan JSON adapter. |
| `src/cozmo_floorplan/recon/photos_config.py` | Official 2–8 photo count, accepted extensions, and minimum image-size settings. |
| `src/cozmo_floorplan/recon/photos.py` | Photo-tier boundary: validates every room folder and refuses metric output until SfM, adjacency, and scale exist. |
| `docs/formats/photo-job.md` | Public per-room photo job layout and current metric-reconstruction boundary. |
| `src/cozmo_floorplan/recon/video_config.py` | Sample rate, frame caps, extensions, and pose-sidecar filenames. |
| `src/cozmo_floorplan/recon/video.py` | Video-tier adapter: samples a walkthrough, detects pose sidecars, refuses uncalibrated centimetres. |
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
| `src/cozmo_floorplan/agent/__init__.py` | Exposes claims enrichment to the main pipeline. |
| `docs/formats/damage-observations.md` | Input boundary between calibrated CV/manual proposals and agent classification/policy decisions. |

## Tests and fixtures

| File | Responsibility |
| --- | --- |
| `tests/test_cli.py` | Tests job validation, structured failures, schema-valid output, and the exact module command. |
| `tests/test_eval.py` | Tests red empty predictions, detection misses/phantoms, repeatability evidence, photo stitching, head-to-head, and the eval command. |
| `tests/test_schema.py` | Tests the FloorPlan v0.2 contract and its required interval/claims fields. |
| `data/fixtures/synthetic_two_room/` | Small public-safe metric truth used by schema and later evaluation tests. |
| `data/fixtures/roomplan_two_room/` | Synthetic RoomPlan-format LiDAR job that reconstructs the same metric room dimensions. |
| `tests/test_lidar.py` | Tests single/multi-room discovery, RoomPlan conversion, intervals, metric gates, CLI output, and honest unsupported fallbacks. |
| `tests/test_render.py` | Tests parseable whole-property SVG, dimensions, openings, deterministic output, XML escaping, and failed-run placeholders. |
| `tests/test_photos.py` | Tests room discovery, the official 2–8 count, corrupt-image rejection, multi-room ordering, and honest metric refusal using generated JPEGs. |
| `tests/test_agent.py` | Tests fallback and mocked-live agents, metric ownership, rule validation, transactional rollback, and schema-valid claims output. |
| `tests/test_stitch.py` | Tests correction-on/off metadata, ablation artifacts, injected 20 cm opening-gap closure, and the drift eval gate. |
| `tests/test_video.py` | Tests empty video jobs, generated-mp4 frame sampling, pose-sidecar mention, and honest metric refusal. |
| `tests/conftest.py` | Forces offline fallback during tests so local API keys are never used and tests never spend credits. |

## Planned modules

Later tasks add real modules only when they contain working behavior:

- Metric SfM, Manhattan regularization, scale, and calibrated intervals inside `recon/photos.py` once real capture evidence exists.
- Metric visual odometry inside `recon/video.py` once a real walkthrough exists.
- Additional `geom/` modules — point-cloud and plane operations as required.

Do not create empty placeholders for these directories. Add each one with its implementing task and document its files here.
