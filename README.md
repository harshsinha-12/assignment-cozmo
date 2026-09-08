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

**Human (tonight):** capture the benchmark — [`docs/capture-protocol.md`](docs/capture-protocol.md). 3+ rooms + hallway, photos/video/LiDAR, two damage classes, tape, Polycam or magicplan on two rooms. Short list: [`START-TOMORROW.md`](START-TOMORROW.md).

**Agent:** [`AGENTS.md`](AGENTS.md) → [`HANDOFF.md`](HANDOFF.md) → [`update.md`](update.md) → [`TASKS.md`](TASKS.md). Top unblocked code task is **T21** (thin iOS exporter, if Xcode is available). T6 raw Record3D waits on a real capture.

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

**Schema, CLI, eval, RoomPlan JSON LiDAR, paired JSON/SVG output, and T16 claims agent/tools work. Raw Record3D/USDZ and real damage images await capture.**

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

It returns `partial` until T9 adds multi-room drift correction. The SVG shows room polygons, measured wall intervals, openings, a metric scale bar, and provenance summary. See `docs/formats/roomplan-json.md` for accepted input and current Record3D/USDZ boundaries.

The optional `damage_observations.json` contract supplies surface-mapped metric extents to the claims stage. The LLM can select damage classes, concealed-rule ids, and allowed actions, but tools copy all quantities. See `docs/formats/damage-observations.md`.

Evaluate any output with `python -m cozmo_floorplan eval --pred PRED --truth TRUTH --out OUT`. Missing repeat and drift-ablation evidence stays visibly red.

## Design in one paragraph

One FloorPlan IR for photos, video, and LiDAR. One command emits JSON + SVG. Centimetres come from geometry. An **LLM agent with tools** fills damage, concealed-damage rules, and scope (disclosed public API + fallback). Eval reports official gates in centimetres.

## Ground rules

- Python 3.11+ (3.12 is fine).
- Deterministic jobs: same `job/` in, same JSON out.
- Headless tests (`opencv-python-headless`).
- No centimetre claims without eval numbers.
- No website, no Redis, no calls to **our** servers. Disclosed LLM API is required for the agent path (`docs/agent-layer.md`).
