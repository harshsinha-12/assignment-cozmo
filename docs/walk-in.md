# Walk-in rehearsal (T11)

The defense is a **cold room**: they capture a space that is not in our benchmark, follow `docs/capture-route.md` literally, and score `python -m cozmo_floorplan run` against a laser while it runs. All three tiers must be ready. This page is **our** rehearsal of that exam, not the operator card they print.

Holdout rooms are **not** `drawing-room`, `my-room`, `pooja-room`, or `connector`. Kitchen, guest room, bathroom, or any other labeled space is eligible.

## Setup once

```bash
cp -R data/templates/walkin data/private/walkin
```

Edit `data/private/walkin/walkin.yaml` so `room_id` is the new room. Replace every `replace-me` device string in the three job manifests. Keep one tier per job.

## Capture (Route 2)

Follow `docs/capture-route.md` on that one room:

| Tier | Drop files here |
| --- | --- |
| Photos | `data/private/walkin/walkin-photos/photos/<room_id>/` — eight JPEGs |
| Video | `data/private/walkin/walkin-video/video/walkthrough.mp4` |
| LiDAR | `data/private/walkin/walkin-lidar/lidar/` — Record3D `.r3d`, RoomPlan JSON, or semantic USD/USDZ |

Tape every wall, the ceiling, and the door while the CLI would be running. Put centimetres in `data/private/walkin/measurements.txt`, then a schema-valid `ground_truth.json` before claiming a score. Do not mix this folder with `data/private/benchmark-*` or Route 1 `cozmo-capture-*` jobs.

## One command

For a full three-tier rehearsal:

```bash
make walkin
```

Same path without Make:

```bash
python -m cozmo_floorplan walkin data/private/walkin --out out/walkin
```

On evaluator day, rehearse only the tier they selected so absent, unselected media
cannot obscure the result:

```bash
make walkin WALKIN_TIER=video
# Equivalent:
python -m cozmo_floorplan walkin data/private/walkin --out out/walkin --tier video
```

Use `photos`, `video`, `lidar`, or `all`. The harness times the same public
`run` path, evaluates against tape when `ground_truth.json` exists, and refuses
to score if a selected job reuses a benchmark room. Photo selection also
crash-tests the official **2-still** floor. Open
`out/walkin/walkin-summary.md`: **Geometry ready** is the fast go/no-go signal,
and **Immediate actions** translates warnings into a concrete recapture.

The defense command itself remains one job:

```bash
python -m cozmo_floorplan run path/to/job --out path/to/out
```

`make walkin` is the rehearsal harness. `make benchmark` is the author's property and must not be pointed at this folder.

## Status

Selected-tier infrastructure is in place. The independent `mummy-room` LiDAR
rehearsal uses a semantic USD crate plus user-supplied tape truth. It completed
with `pending=0` in 0.106 seconds and emitted one room, eight wall segments,
two doors, one window, and an SVG. The scan remained `partial` because its wall
loop was open. Against 300 × 360 cm tape truth: one wall matched at 16.1 cm
error, the closest door missed by 4.17 cm, ceiling missed by 7 cm, and footprint
area missed by 48.2%. These are non-passing gates, not a claimed accuracy win.
Photo and video holdout media remain absent.
