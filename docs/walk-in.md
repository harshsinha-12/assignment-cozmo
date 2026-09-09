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
| LiDAR | `data/private/walkin/walkin-lidar/lidar/` — original Record3D `.r3d` |

Tape every wall, the ceiling, and the door while the CLI would be running. Put centimetres in `data/private/walkin/measurements.txt`, then a schema-valid `ground_truth.json` before claiming a score. Do not mix this folder with `data/private/benchmark-*` or Route 1 `cozmo-capture-*` jobs.

## One command

```bash
make walkin
```

Same path without Make:

```bash
python -m cozmo_floorplan walkin data/private/walkin --out out/walkin
```

That times the public `run` path on every present tier, crash-tests the official **2-still** photo floor from the first two images, evaluates against tape when `ground_truth.json` exists, and refuses to score if the room ids collide with the benchmark. Open `out/walkin/walkin-summary.md`.

The defense command itself remains one job:

```bash
python -m cozmo_floorplan run path/to/job --out path/to/out
```

`make walkin` is the rehearsal harness. `make benchmark` is the author's property and must not be pointed at this folder.

## Status

Infrastructure is in place. Holdout photos, video, LiDAR, and tape are still missing, so a real timed rehearsal has not been scored. Pending inputs stay `pending`; they are never treated as zero.
