# Code map

This is the maintained guide to what each implementation file owns. Update it whenever a task adds, moves, or removes a code module. Architecture and scoring rationale stay in the other `docs/` files; this page answers “where does the code live?”

## Package and command

| File | Responsibility |
| --- | --- |
| `pyproject.toml` | Installable Python package metadata and the optional `cozmo-floorplan` console command. |
| `src/cozmo_floorplan/__main__.py` | Entry point for the required `python -m cozmo_floorplan ...` command. |
| `src/cozmo_floorplan/cli.py` | CLI arguments, exit codes, and the outer error boundary that guarantees structured output where the output directory is writable. |
| `src/cozmo_floorplan/pipeline.py` | Application orchestration boundary. Dispatches LiDAR jobs to T6 and returns honest structured failures for unavailable adapters/formats. |
| `src/cozmo_floorplan/config.py` | Shared filenames, schema version, supported tiers, directory conventions, and exit-code constants. |
| `src/cozmo_floorplan/errors.py` | Expected domain exception types. Keeps error classification out of command and I/O code. |

## Contract and I/O

| File | Responsibility |
| --- | --- |
| `src/cozmo_floorplan/io/job.py` | Reads `manifest.yaml`, checks the tier-specific job directory, and produces immutable normalized job metadata. |
| `src/cozmo_floorplan/io/output.py` | Validates and atomically writes `floorplan.json`, preventing partially-written artifacts. |
| `src/cozmo_floorplan/floorplan.py` | Creates stable FloorPlan documents, including the schema-valid failed result used before adapters exist. |
| `src/cozmo_floorplan/schema.py` | Loads and compiles the canonical JSON Schema and validates generated documents. |
| `src/cozmo_floorplan/utils/paths.py` | Finds repository runtime assets and handles the explicit schema-path override. |
| `docs/schemas/floorplan.schema.json` | Canonical external data contract. This remains the single schema source of truth. |

## Geometry and LiDAR reconstruction

| File | Responsibility |
| --- | --- |
| `src/cozmo_floorplan/geom/transforms.py` | Parses RoomPlan pose encodings and projects surface width axes onto the world x-z floor plane. |
| `src/cozmo_floorplan/geom/polygons.py` | Polygonizes unordered wall segments, with a reported convex-hull fallback for incomplete loops. |
| `src/cozmo_floorplan/io/roomplan.py` | Parses the portable single- or multi-room RoomPlan JSON contract into typed immutable capture objects. |
| `src/cozmo_floorplan/recon/lidar_config.py` | LiDAR confidence scores, uncertainty widths, and recognized RoomPlan filenames. |
| `src/cozmo_floorplan/recon/measurements.py` | Builds interval-bearing LiDAR and derived diagnostic measurements without treating transforms as exact. |
| `src/cozmo_floorplan/recon/lidar.py` | Converts RoomPlan rooms, walls, openings, and adjacency into FloorPlan v0.2; detects unsupported Record3D/USDZ inputs. |
| `docs/formats/roomplan-json.md` | Public input contract for the tested RoomPlan JSON adapter. |

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

## Tests and fixtures

| File | Responsibility |
| --- | --- |
| `tests/test_cli.py` | Tests job validation, structured failures, schema-valid output, and the exact module command. |
| `tests/test_eval.py` | Tests red empty predictions, detection misses/phantoms, repeatability evidence, photo stitching, head-to-head, and the eval command. |
| `tests/test_schema.py` | Tests the FloorPlan v0.2 contract and its required interval/claims fields. |
| `data/fixtures/synthetic_two_room/` | Small public-safe metric truth used by schema and later evaluation tests. |
| `data/fixtures/roomplan_two_room/` | Synthetic RoomPlan-format LiDAR job that reconstructs the same metric room dimensions. |
| `tests/test_lidar.py` | Tests single/multi-room discovery, RoomPlan conversion, intervals, metric gates, CLI output, and honest unsupported fallbacks. |

## Planned modules

Later tasks add real modules only when they contain working behavior:

- `recon/video.py` and `recon/photos.py` — video and photo adapters.
- Additional `geom/` modules — point-cloud, plane, and pose-graph operations as required.
- `stitch/` — room adjacency, pose graph, and drift correction.
- `render/` — whole-property SVG output.
- `agent/` — LLM tool calling plus deterministic damage/scope fallback.

Do not create empty placeholders for these directories. Add each one with its implementing task and document its files here.
