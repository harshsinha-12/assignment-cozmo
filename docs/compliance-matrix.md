# Compliance matrix

Requirement → file path → artifact → status.

Status: `missing` | `partial` | `done`. Fill during implementation. This file is a scored deliverable (10%).

| ID | Requirement | File / command | Artifact | Status |
| --- | --- | --- | --- | --- |
| R1 | Choose one capture route | `docs/capture-route.md` + `docs/capture-route-route1.md` + `data/templates/` | Route 2 operator card (Camera + Record3D). Route 1 cable install without TestFlight | done |
| R2 | Device matrix | `docs/device-matrix.md` | Hardware eligibility plus measured harsh-home-01 intervals (2026-09-10) | done |
| R3 | Photos tier, 2–8 stills, no depth/poses, per-room folders, whole-property stitch | `io/photos.py` + `recon/photo_overlap.py` + `recon/photo_sfm.py` + `recon/photos.py` | Ingest, overlap graph, incremental SfM on connected graphs; author 2/2/5/3 still disconnected | partial |
| R4 | Video tier, handheld walkthrough | `recon/video.py` + `recon/video_native_scale.py` + `recon/video_rooms.py` | Native scale 4/4; occupancy envelopes emit drawing+pooja rooms (`partial`); ±3% not claimed | partial |
| R5 | LiDAR tier, depth+poses+intrinsics | `io/record3d.py` + `io/usd_mesh.py` + `recon/lidar.py` | Record3D and semantic USD/USDZ → metric FloorPlan; benchmark walls 7.5/30 cm; independent USD holdout emits geometry | partial |
| R6 | Per-room: walls, ceiling, area, openings | schema + lidar recon | LiDAR emits walls, ceilings, areas, opening candidates on the current scans | partial |
| R7 | Stitched multi-room adjacency | `stitch/constraints.py` + `stitch/pose_graph.py` | Shared-opening SE(2) snap + ablation on RoomPlan; LiDAR rooms share an ARKit frame when openings face | partial |
| R8 | Damage regions, class + metric extent | `agent/openai_agent.py` + `agent/tools.py` | Live/fallback `damage[]`; staged two-class observations on my-room | done |
| R9 | Concealed-damage flags + rule id | `agent/tools.py::fire_concealed_rule` | Policy-validated `concealed_flags[]` live and offline | done |
| R10 | Scope line items keyed to surfaces | `agent/tools.py::add_scope_line` | Quantity copied from metric damage observation | done |
| R11 | Confidence interval on every measurement | `docs/schemas/floorplan.schema.json` | v0.2 `{value, unit, interval}` required and tested | done |
| R12 | One command per capture | `src/cozmo_floorplan/cli.py` | `python -m cozmo_floorplan run JOB --out OUT` for a folder or Cozmo Capture ZIP | done |
| R13 | JSON to published schema | `docs/schemas/floorplan.schema.json` | FloorPlan v0.2; CLI validates before write | done |
| R14 | Rendered plan | `src/cozmo_floorplan/render/svg.py` | Paired `floorplan.svg` | done |
| R15 | Benchmark: 3+ rooms + connector, all tiers, damage, repeat, tape GT | `data/private/` + `make benchmark` | Photos, video, three room `.r3d`, tape, damage, photo/video repeats, Magicplan 2026.35.0; connector LiDAR not in the bundle | partial |
| R16 | Opening width gate | `eval/evaluator.py` + `out/benchmark/lidar/eval.json` | LiDAR: 3 matched, median 5 cm; photos/video: 0 predictions | partial |
| R17 | Ceiling height + repeatability gates | `eval/evaluator.py` | LiDAR ceiling max 5.41 cm, n=3; photo/video repeats present | partial |
| R18 | Drift ablation | `run` + `--no-drift-correction` | Synthetic 20 cm gap closes; LiDAR ablation artifacts present | partial |
| R19 | Photo-tier whole-property stitch ±8% | `eval/evaluator.py` | Gate implemented; overlap graphs 2/2/5/3 | partial |
| R20 | Head-to-head vs incumbent, 2 rooms, LiDAR | `eval --incumbent` | Magicplan 2026.35.0; 9 of 12 shared dimensions (75%), passing ≥70% | done |
| R21 | Fix loop: declaration, before, after, diff | `docs/fix-loop.md` + `data/fix-loop/` | Checksum-locked yield fail→pass, regenerable | done |
| R22 | README 15 min clean machine | `README.md` + `docs/reproduction.md` | Fresh Python 3.12 venv path 28.37 s on macOS arm64 | done |
| R23 | Reproduction bundle | `make reproduce-synthetic` + `make benchmark` + `data/fix-loop/` | Synthetic + private three-tier runner; `pending_inputs` empty | done |
| R24 | Technical report ≤ 6 pages | `docs/writeup.md` | Architecture, tiers, drift, intervals, agent, fix loop, measured tables | done |
| R25 | Mirrors / glass / wet / low light | `docs/writeup.md` §7 + capture route | Capture guidance and structured incomplete-scan warnings | done |
| R26 | No calls to our infrastructure | `agent/openai_agent.py` | Local processing; disclosed OpenAI or offline tools | done |
| R27 | Process evidence | git history | Incremental commits across schema, CLI, adapters, eval, iOS, evidence, and final benchmark hardening | done |
