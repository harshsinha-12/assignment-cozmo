# assignment-cozmo

Take-home for **Cozmo AI**: phone captures → **dimensioned, stitched floor plans** plus damage/scope JSON. Local CLI, not a website.

Official prompt: [`docs/takehome.md`](docs/takehome.md) (Round 2). What we are building: [`docs/product.md`](docs/product.md). **Score policy:** target every official row; cut only tomorrow night ([`docs/cut-later.md`](docs/cut-later.md)).

| Field | Value |
| --- | --- |
| Company | [Cozmo AI](https://www.hellocozmo.ai/) |
| Role | AI Backend Engineer |
| Recruiter | Brynz — saik@brynz.io |
| Capture phone | iPhone 17 Pro (LiDAR) |
| Official prompt | In repo — [`docs/takehome.md`](docs/takehome.md) |
| Agent contract | [`AGENTS.md`](AGENTS.md) |
| Current handoff | [`HANDOFF.md`](HANDOFF.md) |

## Start here

**Human (tomorrow):** capture the benchmark — [`docs/capture-protocol.md`](docs/capture-protocol.md). Drop files in gitignored `data/private/` ([`data/README.md`](data/README.md)). Short list: [`START-TOMORROW.md`](START-TOMORROW.md).

**Agent:** [`AGENTS.md`](AGENTS.md) → [`HANDOFF.md`](HANDOFF.md) → [`update.md`](update.md) → [`TASKS.md`](TASKS.md). T19, the T10 engineering report draft, and the media-independent T20a reproduction pass are complete. The benchmark capture is now the critical path; metric adapters wait on those files.

## Repo map

| File | Role |
| --- | --- |
| `AGENTS.md` | Operating contract |
| `HANDOFF.md` | Last session |
| `update.md` | Append-only log |
| `plan.md` | Technical plan (aligned) |
| `roadmap.md` | Phases |
| `TASKS.md` | Queue |
| `docs/product.md` | What we ship / how they test |
| `docs/code-map.md` | What each implementation file owns |
| `docs/agent-layer.md` | LLM tool calling (damage/scope) |
| `docs/cut-later.md` | Tomorrow-night defer list only |
| `docs/takehome.md` | Official case study |
| `docs/capture-route.md` | Walk-in protocol (Route 2) |
| `docs/compliance-matrix.md` | Scored coverage table |
| `docs/device-matrix.md` | Hardware × tier |
| `docs/writeup.md` | Six-page-cap technical report draft and evidence tables |
| `docs/reproduction.md` | Clean-environment commands, timings, assertions, and remaining proof |
| `docs/schemas/floorplan.schema.json` | Frozen v0.2 IR: interval measurements + claims objects |
| `src/` | Modular CLI, RoomPlan reconstruction, eval, and SVG rendering package |

## Current status

**Schema, CLI, eval, RoomPlan JSON LiDAR, T9 stitch/ablation, multi-video/photo ingest, paired JSON/SVG, T16 claims agent/tools, T19 fix loop, T10 report draft, and one-command synthetic reproduction work. Video now has orientation-aware ingest, ORB/geometric feature gates, segmented scale-free poses, and a strict metric-pose sidecar/alignment path; real Record3D emits partial metric geometry. Video surface extraction/FloorPlan output, cross-scan registration, calibration, and metric photos remain.**

See [`roadmap.md`](roadmap.md).

## Setup (short)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install --no-deps -e .
make test
```

This setup path was exercised on 2026-09-09 in a fresh Python 3.12 virtual environment on macOS arm64. Creating the environment, downloading/installing requirements, installing this package, running the then-current 57 tests, generating the synthetic plan/eval, and verifying the fix-loop bundle took 28.37 seconds on that machine. Network and package-cache conditions vary; this is evidence for the documented path, not a universal timing claim. Exact commands and timings: [`docs/reproduction.md`](docs/reproduction.md).

## First verified run

After setup, one command regenerates the public-safe synthetic RoomPlan job, evaluates it, verifies the expected gate states, and checks the frozen fix-loop bundle:

```bash
make reproduce-synthetic
```

Artifacts are written to `out/reproduction/`: `floorplan.json`, `floorplan.svg`, `floorplan.ablation-off.json`, and `eval.json`. The wrapper returns 0 only when the plan is schema-valid and `ok`, required counts match, the yield/opening/ceiling/drift/calibration gates pass, repeatability and incumbent gates remain explicitly `missing_evidence`, and fix-loop hashes are valid. The internal eval command exits 3 by design because those two inputs are absent; the wrapper verifies that expected exit instead of hiding it.

For live claims enrichment, copy `.env.example` to the ignored `.env` and set `OPENAI_API_KEY`. The default `COZMO_AGENT_MODE=auto` uses OpenAI when the key exists and the same deterministic tools otherwise. Set `COZMO_AGENT_MODE=fallback` to force an offline run. Never commit `.env`.

`run` emits `floorplan.json` and a self-contained `floorplan.svg`, including a readable placeholder for structured failures.

The synthetic RoomPlan job now emits dimensioned geometry:

```bash
python -m cozmo_floorplan run data/fixtures/roomplan_two_room --out out/roomplan_two_room
```

For multi-room jobs, the normal run plane-anchors shared openings and also writes `floorplan.ablation-off.json` with reconstructed poses preserved. Use `--no-drift-correction` to generate only that poses-as-is path. Explicit, successful deterministic-agent mode preserves healthy status; automatic missing-key or provider-failure fallback remains `partial`. Geometry correction status is recorded separately under `stitch.drift_correction`. The SVG shows room polygons, measured wall intervals, openings, a metric scale bar, and provenance summary. See `docs/formats/roomplan-json.md` and `docs/formats/record3d.md` for accepted inputs and current boundaries.

The optional `damage_observations.json` contract supplies surface-mapped metric extents to the claims stage. The LLM can select damage classes, concealed-rule ids, and allowed actions, but tools copy all quantities. See `docs/formats/damage-observations.md`.

Evaluate the pair with `python -m cozmo_floorplan eval --pred OUT/floorplan.json --truth TRUTH --ablation-off OUT/floorplan.ablation-off.json --out OUT`. Missing repeat, real-capture, and incumbent evidence stays visibly red.

Video jobs: put one MP4/MOV per room in `video/` (`docs/formats/video-job.md`). The CLI samples every file, preserves source-frame/timestamp identity, evaluates geometric tracks, and recovers segmented unitless poses. A versioned per-video sidecar can provide validated metric camera positions through exact frame/time matching; native MP4s still exit structurally rather than guessing centimetres.

Photo jobs: put 2–8 decodable images per room under `photos/<room_id>/` (`docs/formats/photo-job.md`). Ingest is ready; metric SfM, adjacency, and scale remain capture-dependent.

The completed fix-loop bundle is frozen under `data/fix-loop/` and verified with `PYTHONPATH=src python3 -m cozmo_floorplan.fix_loop.verify data/fix-loop`. Its declaration, exact fail→pass result, pinned before/after artifacts, and readable diff are in `docs/fix-loop.md` and `data/fix-loop/diff.md`.

## Design in one paragraph

One FloorPlan IR for photos, video, and LiDAR. One command emits JSON + SVG. Centimetres come from geometry. An **LLM agent with tools** fills damage, concealed-damage rules, and scope (disclosed public API + fallback). Eval reports official gates in centimetres.

## Ground rules

- Python 3.11+ (3.12 is fine).
- Deterministic jobs: same `job/` in, same JSON out.
- Headless tests (`opencv-python-headless`).
- No centimetre claims without eval numbers.
- No website, no Redis, no calls to **our** servers. Disclosed LLM API is required for the agent path (`docs/agent-layer.md`).
