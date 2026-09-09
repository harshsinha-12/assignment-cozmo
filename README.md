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

**Agent:** [`AGENTS.md`](AGENTS.md) → [`HANDOFF.md`](HANDOFF.md) → [`update.md`](update.md) → [`TASKS.md`](TASKS.md). T9 stitch works. Next without captures: **T8 photo ingest**. T6 raw Record3D and T7 metric VO wait on tomorrow’s files.

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
| `docs/schemas/floorplan.schema.json` | Frozen v0.2 IR: interval measurements + claims objects |
| `src/` | Modular CLI, RoomPlan reconstruction, eval, and SVG rendering package |

## Current status

**Schema, CLI, eval, RoomPlan JSON LiDAR, T9 stitch/ablation, T7 video ingest, paired JSON/SVG, and T16 claims agent/tools work. Metric video/photos and raw Record3D await capture.**

See [`roadmap.md`](roadmap.md).

## Setup (short)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
make test
```

For live claims enrichment, copy `.env.example` to the ignored `.env` and set `OPENAI_API_KEY`. The default `COZMO_AGENT_MODE=auto` uses OpenAI when the key exists and the same deterministic tools otherwise. Set `COZMO_AGENT_MODE=fallback` to force an offline run. Never commit `.env`.

`run` emits `floorplan.json` and a self-contained `floorplan.svg`, including a readable placeholder for structured failures.

The synthetic RoomPlan job now emits dimensioned geometry:

```bash
python -m cozmo_floorplan run data/fixtures/roomplan_two_room --out out/roomplan_two_room
```

For multi-room jobs, the normal run plane-anchors shared openings and also writes `floorplan.ablation-off.json` with reconstructed poses preserved. Use `--no-drift-correction` to generate only that poses-as-is path. The overall result may still be `partial` when the claims layer uses its disclosed fallback; geometry correction status is recorded separately under `stitch.drift_correction`. The SVG shows room polygons, measured wall intervals, openings, a metric scale bar, and provenance summary. See `docs/formats/roomplan-json.md` for accepted input and current Record3D/USDZ boundaries.

The optional `damage_observations.json` contract supplies surface-mapped metric extents to the claims stage. The LLM can select damage classes, concealed-rule ids, and allowed actions, but tools copy all quantities. See `docs/formats/damage-observations.md`.

Evaluate the pair with `python -m cozmo_floorplan eval --pred OUT/floorplan.json --truth TRUTH --ablation-off OUT/floorplan.ablation-off.json --out OUT/eval.json`. Missing repeat, real-capture, and incumbent evidence stays visibly red.

Video jobs: put one MP4/MOV in `video/` (`docs/formats/video-job.md`). The CLI samples frames and currently exits with a structured failure rather than guessing centimetres.

## Design in one paragraph

One FloorPlan IR for photos, video, and LiDAR. One command emits JSON + SVG. Centimetres come from geometry. An **LLM agent with tools** fills damage, concealed-damage rules, and scope (disclosed public API + fallback). Eval reports official gates in centimetres.

## Ground rules

- Python 3.11+ (3.12 is fine).
- Deterministic jobs: same `job/` in, same JSON out.
- Headless tests (`opencv-python-headless`).
- No centimetre claims without eval numbers.
- No website, no Redis, no calls to **our** servers. Disclosed LLM API is required for the agent path (`docs/agent-layer.md`).
