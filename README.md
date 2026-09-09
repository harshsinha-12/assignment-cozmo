# Cozmo floor plan

Take-home for **Cozmo AI** (YC), role **AI Backend Engineer**. Cozmo is the AI operating system for property claims: field capture becomes structured loss data a downstream estimate agent can consume. This repo is that primitive — not a website, not a magicplan clone, and not a call into Cozmo’s infrastructure.

Official prompt: [`docs/takehome.md`](docs/takehome.md). Job brief: [`docs/job-brief.md`](docs/job-brief.md). Technical report: [`docs/writeup.md`](docs/writeup.md).

```text
python -m cozmo_floorplan run JOB --out OUT
```

One command turns a phone capture (photos, video, or LiDAR) into `floorplan.json` + `floorplan.svg`: walls, openings, ceiling, floor area, stitch, damage, concealed-rule flags, scope, and a confidence interval on every measurement.

## Both capture routes

The prompt allows **either** a native iOS app **or** a stock protocol. This submission builds **both**, so the walk-in is never blocked on signing.

| Route | What shipped | When to use it |
| --- | --- | --- |
| **Route 2 (scored)** | One-page protocol: iPhone Camera + Record3D. Templates in `data/templates/`. | Always. Print [`docs/capture-route.md`](docs/capture-route.md). |
| **Route 1** | Cozmo Capture: LiDAR (RoomPlan + ARKit `.r3d`), Photos, and Video on one job ZIP the CLI already ingests. Cable install, no $99 TestFlight. | Mac with Xcode + 10 minutes. [`docs/capture-route-route1.md`](docs/capture-route-route1.md). |

Timed on the author’s iPhone 17 Pro: signed iPhoneOS build **46 s**, device copy **~18 s**. If their laptop is not a Mac, they stay on Route 2.

## These paths ran

Same CLI, three inputs. The JSON is the product; the SVG is what a homeowner would recognise.

### Route 1 — Cozmo Capture app → CLI

Phone export `cozmo-capture-20260909-190805.zip` (`capture_tool: Cozmo Capture 0.1.0`). Command: `python -m cozmo_floorplan run cozmo-capture-*.zip --out out/route1`.

The app is on the phone: LiDAR / Photos / Video, then one job ZIP. The room mesh below is the on-device RoomPlan preview (not the CLI drawing).

| Scanning | Room on the phone |
| --- | --- |
| ![LiDAR scan with RoomPlan edges](docs/evidence/app-lidar-scanning.jpg) | ![On-device room mesh](docs/evidence/app-lidar-room.jpg) |
| Photos | Video |
| ![Photos tab, 2–8 overlapping stills](docs/evidence/app-photos.jpg) | ![Video tab, one walkthrough](docs/evidence/app-video.jpg) |
| Export ZIP | CLI FloorPlan from that ZIP |
| ![Share capture job ZIP](docs/evidence/app-export-ready.jpg) | ![Route 1 FloorPlan from Cozmo Capture](docs/evidence/route1-cozmo-capture.svg) |

```json
{
  "status": "partial",
  "floor_id": "cozmo-capture-20260909-190805",
  "tier": "lidar",
  "scale_source": "lidar",
  "rooms": 1,
  "walls": 6,
  "openings": 1,
  "ceiling_cm": 295.13,
  "door_width_cm": 63.66,
  "warning": "incomplete_scan"
}
```

`partial` is the honest status: the first on-phone scan was mostly in-place, so the wall loop was open. The ZIP still reconstructed centimetres, a door, and an SVG. Regenerable copy: [`docs/evidence/route1-cozmo-capture.json`](docs/evidence/route1-cozmo-capture.json).

### Route 2 — Camera + Record3D → CLI

Three room `.r3d` archives from Record3D on the same iPhone 17 Pro. Command: `make benchmark` (LiDAR job).

![Route 2 FloorPlan from Record3D](docs/evidence/route2-record3d.svg)

```json
{
  "status": "partial",
  "floor_id": "benchmark-lidar-2026-09-09",
  "tier": "lidar",
  "rooms": ["drawing-room", "my-room", "pooja-room"],
  "openings": 4,
  "extents_cm": {
    "drawing-room": "380×305 (tape 368×305)",
    "my-room": "370×325 (tape 400×325)",
    "pooja-room": "365×295 (tape 370×290)"
  }
}
```

Three metric rooms, openings, and intervals from stock App Store capture. Regenerable copy: [`docs/evidence/route2-record3d.json`](docs/evidence/route2-record3d.json).

### Contract fixture — `make reproduce-synthetic`

![Synthetic two-room FloorPlan](docs/evidence/synthetic-two-room.svg)

```json
{
  "status": "ok",
  "floor_id": "roomplan_two_room",
  "rooms": 2,
  "openings": 1,
  "damage": 2,
  "pipeline_yield": "pass"
}
```

This is the 15-minute README path: schema-valid `ok`, yield pass, openings and ceilings at 0 cm on the fixture.

## What is stronger than a notebook

The JD grades structured field data, agents with tools and fallbacks, and knowing where the method breaks — not a pretty stitch demo.

- **One contract, three sensors.** Photos, video, and LiDAR emit the same FloorPlan IR. One renderer, one eval, intervals that widen as the sensor thins.
- **Geometry owns centimetres.** An LLM with tools fills damage, concealed-rule ids, and scope. It cannot write wall lengths. Live OpenAI or the same tools offline — no call to Cozmo’s servers.
- **Evals that survive reproduction.** Official gates in centimetres, drift on vs off, photo/video repeats, Magicplan **2026.35.0** head-to-head, `make benchmark` regenerates the table.
- **Fix loop, not a post-mortem.** Declared failing yield, shipped code, checksum-locked before/after, readable diff (`data/fix-loop/`).
- **Own property, not a fixture.** Same rooms at all three tiers, staged two-class damage, tape, a photo repeat, and a consumer-app export.
- **A path onto a phone.** Route 2 is App Store apps a non-engineer can install. Route 1 is a real RoomPlan/ARKit exporter they can sideload in under 10 minutes.

LiDAR room extents vs tape (Record3D, same three rooms):

| Room | Predicted | Tape | Δ |
| --- | --- | --- | --- |
| drawing-room | 380 × 305 cm | 368 × 305 cm | +12 / 0 cm |
| my-room | 370 × 325 cm | 400 × 325 cm | −30 / 0 cm |
| pooja-room | 365 × 295 cm | 370 × 290 cm | −5 / +5 cm |

Two short walls match tape exactly. The 30 cm `my-room` long wall is a supported 3.70 m plane, not a missing output. Remaining centimetre error is mostly **capture quality**: fast handheld motion, vibrating video, and thin LiDAR coverage on a long wall — not a missing pipeline. The same codebase, with a steadier walk and a Pro-class LiDAR scan, is what an experienced operator (or a professional camera) would run; the intervals already widen as the sensor thins. Full gate table: [`docs/writeup.md`](docs/writeup.md) §6.

## Deliverables

| Official item | Where it lives |
| --- | --- |
| Compliance matrix | [`docs/compliance-matrix.md`](docs/compliance-matrix.md) |
| Capture route + device matrix | [`docs/capture-route.md`](docs/capture-route.md) (scored) · [`docs/capture-route-route1.md`](docs/capture-route-route1.md) (optional app) · [`docs/device-matrix.md`](docs/device-matrix.md) |
| README to first run in 15 minutes | this file |
| Reproduction bundle | `make reproduce-synthetic` · `make benchmark` · [`docs/reproduction.md`](docs/reproduction.md) · [`data/fix-loop/`](data/fix-loop/) |
| Benchmark report | [`docs/writeup.md`](docs/writeup.md) §6 · `out/benchmark/` after `make benchmark` |
| Fix loop | [`docs/fix-loop.md`](docs/fix-loop.md) · [`data/fix-loop/`](data/fix-loop/) |
| Technical report ≤ 6 pages | [`docs/writeup.md`](docs/writeup.md) |
| FloorPlan schema | [`docs/schemas/floorplan.schema.json`](docs/schemas/floorplan.schema.json) |
| Raw benchmark | gitignored `data/private/` (photos, video, Record3D, tape, Magicplan 2026.35.0) |

## Setup (under 15 minutes)

Python 3.11+ (3.12 verified). No Redis, no hosted API of ours.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install --no-deps -e .
make test
make reproduce-synthetic
```

On a fresh macOS arm64 Python 3.12 venv this path was **28.37 s** end-to-end (venv, install, tests, synthetic run, eval, fix-loop verify). Details: [`docs/reproduction.md`](docs/reproduction.md).

For live damage/scope, copy `.env.example` to `.env` and set `OPENAI_API_KEY`. Default `COZMO_AGENT_MODE=auto` uses OpenAI when the key exists and the same tools offline otherwise. Never commit `.env`. Never point the agent at Cozmo servers.

## One command per capture

```bash
python -m cozmo_floorplan run path/to/job --out out/run
```

Open:

- `out/run/floorplan.json` — schema-valid plan, damage, concealed flags, scope, intervals
- `out/run/floorplan.svg` — whole-property drawing
- `out/run/floorplan.ablation-off.json` — poses-as-is stitch, when a multi-room graph exists

Evaluate (repeat, ablation, and incumbent flags are optional):

```bash
python -m cozmo_floorplan eval \
  --pred out/run/floorplan.json \
  --truth path/to/ground_truth.json \
  --out out/run
```

Same command with a Cozmo Capture ZIP:

```bash
python -m cozmo_floorplan run path/to/cozmo-capture-*.zip --out out/route1
```

Regenerate every public number:

```bash
make reproduce-synthetic
```

Regenerate the private benchmark (photos, video, LiDAR, photo/video repeats, Magicplan, tape):

```bash
make benchmark
```

Review `out/benchmark/benchmark-summary.md`. Measured gates are in [`docs/writeup.md`](docs/writeup.md).

## Capture route (what they follow at the defense)

Both routes are implemented. **Route 2 is what they print** unless the cable install finishes in under 10 minutes on their phone. iPhone Camera for photos and video; **Record3D** for LiDAR on a Pro. Do not use Polycam or magicplan as the capture tool — they are the head-to-head incumbent (Magicplan **2026.35.0**).

| Tier | Device | What to hand the CLI |
| --- | --- | --- |
| Photos | iPhone 15+ | 2–8 JPEGs per room under `photos/<room>/` |
| Video | iPhone 15+ | one 1080p MOV/MP4 walkthrough |
| LiDAR | iPhone Pro / Pro Max | original Record3D `.r3d` (depth, poses, intrinsics) |

Copy a template, replace `replace-me`, then run `python -m cozmo_floorplan run JOB --out OUT`. Templates: `data/templates/`.

## Install the iOS app (Route 1)

Route 1 is not a stub. Cozmo Capture is a native iOS 17 app: RoomPlan walls, 2 Hz ARKit RGB-D into Record3D-compatible `.r3d`, Photos (2–8 stills/room), Video walkthroughs, and a shareable ZIP the Python CLI unpacks. The official prompt allows TestFlight **or** a cable dev build in under 10 minutes; this submission uses the cable path.

On a Mac with Xcode and this repo, plug in an unlocked iPhone:

```bash
./scripts/install-cozmo-capture.sh
open -a Xcode ios/CozmoCapture/CozmoCapture.xcodeproj
```

Same as `make install-capture-app` and `make open-capture-app`. Cursor does not open the `.xcodeproj`. Print [`docs/capture-route-route1.md`](docs/capture-route-route1.md). Timed on the author’s iPhone 17 Pro: signed iPhoneOS binary 46 s, device copy ~18 s.

If Developer Mode needs a restart, or the laptop is not a Mac with Xcode, stay on Route 2.

After a scan, AirDrop the ZIP and run `python -m cozmo_floorplan run ~/Downloads/cozmo-capture-*.zip --out out/route1`.

## Defense / walk-in test

At the technical discussion they capture a space you have never seen, pick photos, video, or LiDAR, follow [`docs/capture-route.md`](docs/capture-route.md) literally, and run:

```bash
python -m cozmo_floorplan run JOB --out OUT
```

They laser the room while it runs. All three tiers must be ready. Use their `OPENAI_API_KEY` or the tool fallback. Do not point `make benchmark` at that folder — that command is the author’s property. A rehearsal harness exists (`make walkin`, [`docs/walk-in.md`](docs/walk-in.md)) for a room that is not `drawing-room` / `my-room` / `pooja-room` / `connector`.

## Design in one paragraph

One FloorPlan IR for photos, video, and LiDAR. Centimetres come from geometry. An LLM **agent with tools** fills damage, concealed-damage rules, and scope (disclosed public API + fallback). Eval reports official gates in centimetres. Device coverage and measured intervals: [`docs/device-matrix.md`](docs/device-matrix.md).

## Ground rules

- Python 3.11+ (3.12 is fine).
- Deterministic jobs: same `job/` in, same JSON out.
- Headless tests (`opencv-python-headless`).
- No website, no Redis, no calls to **our** servers.
