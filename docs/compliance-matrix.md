# Compliance matrix

Requirement → file path → artifact → status.

Status: `missing` | `partial` | `done`. Fill during implementation. This file is a scored deliverable (10%).

| ID | Requirement | File / command | Artifact | Status |
| --- | --- | --- | --- | --- |
| R1 | Choose one capture route | `docs/capture-route.md` + `data/templates/` | Route 2 operator card plus loader-checked per-tier handoff templates | partial (walk-in untested) |
| R2 | Device matrix | `docs/device-matrix.md` | Hardware eligibility separated from accepted runtime formats and measured accuracy | partial (measurements pending) |
| R3 | Photos tier, 2–8 stills, no depth/poses, per-room folders, whole-property stitch | `io/photos.py` + `recon/photos.py` | multi-room ingest/count/decode validation works; metric SfM and whole-property output pending | partial |
| R4 | Video tier, handheld walkthrough | `recon/video.py` + `io/video.py` | Frames sampled; metric VO pending capture | partial |
| R5 | LiDAR tier, depth+poses+intrinsics | `io/record3d.py`, `recon/record3d_points.py`, `recon/lidar.py` | RoomPlan JSON works; real Record3D emits partial metric rooms/walls/opening candidates, with calibration pending | partial |
| R6 | Per-room: walls, ceiling, area, openings | schema + lidar recon | RoomPlan fixture and raw Record3D path emit the shared fields; raw opening accuracy remains unmeasured | partial |
| R7 | Stitched multi-room adjacency | `stitch/constraints.py` + `stitch/pose_graph.py` | shared-opening graph + corrected whole-property SVG on synthetic RoomPlan | partial |
| R8 | Damage regions, class + metric extent | `agent/openai_agent.py` + `agent/tools.py` | live/fallback `damage[]` works on synthetic observations; real images pending | partial |
| R9 | Concealed-damage flags + rule id | `agent/tools.py::fire_concealed_rule` | policy-validated `concealed_flags[]` generated live and offline | done |
| R10 | Scope line items keyed to surfaces | `agent/tools.py::add_scope_line` | quantity copied from metric damage observation; generated live and offline | done |
| R11 | Confidence interval on every measurement | `docs/schemas/floorplan.schema.json` + `tests/test_schema.py` | v0.2 `{value, unit, interval}` measurement objects required and tested | done |
| R12 | One command per capture | `src/cozmo_floorplan/cli.py` | command runs and emits structured JSON; successful adapters pending | partial |
| R13 | JSON to published schema | `docs/schemas/floorplan.schema.json` | our IR until they attach one | partial |
| R14 | Rendered plan | `src/cozmo_floorplan/render/svg.py` + `src/cozmo_floorplan/io/artifacts.py` | CLI-generated `floorplan.svg`; synthetic visual QA passed | done |
| R15 | Benchmark: 3+ rooms + connector, all tiers, damage, repeat, tape GT | `data/fixtures/` | raw + GT | missing |
| R16 | Opening width gate | `eval/evaluator.py` | ≤2 cm, ≥85%, misses/phantoms scored; real data pending | partial |
| R17 | Ceiling height + repeatability gates | `eval/evaluator.py` | thresholds and missing-evidence reporting implemented; captures pending | partial |
| R18 | Drift ablation | `run` + `--no-drift-correction` + `eval --ablation-off` | corrected and poses-as-is artifacts, residuals, and eval gate pass on synthetic drift; real capture pending | partial |
| R19 | Photo-tier whole-property stitch ±8% | `eval/evaluator.py` | adjacency, overlap, footprint, and wall gates implemented; photos pending | partial |
| R20 | Head-to-head vs incumbent, 2 rooms, LiDAR | `eval --incumbent` | shared-dimension win-rate implemented; two-room exports pending | partial |
| R21 | Fix loop: declaration, before, after, diff | `docs/fix-loop.md` + `data/fix-loop/` | checksum-locked fail→pass bundle, pinned source commits, verifier, and readable diff | done |
| R22 | README 15 min clean machine | `README.md` + `docs/reproduction.md` | fresh Python 3.12 venv path verified on macOS arm64 in 28.37 s; full second-machine rehearsal pending | partial |
| R23 | Reproduction bundle | `make reproduce-synthetic` + `docs/reproduction.md` + `data/fix-loop/` | one-command schema/count/gate/artifact assertions plus checksum-locked fix-loop; real benchmark bundle pending | partial |
| R24 | Technical report ≤ 6 pages | `docs/writeup.md` | 1,805-word engineering draft; real benchmark tables pending | partial |
| R25 | Mirrors / glass / wet / low light | `docs/writeup.md` + capture protocol + structured warnings | mitigations and honest failure policy documented; stress captures pending | partial |
| R26 | No calls to our infrastructure | `agent/openai_agent.py` + fallback | local processing; disclosed direct OpenAI API or offline rules | done |
| R27 | Process evidence | git history | commits as we work | doing |
