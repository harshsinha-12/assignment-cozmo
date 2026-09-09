# Capture protocol (our benchmark — max score)

This is what **Harsh** shoots for the submission. The walk-in follows `docs/capture-route.md` (stricter, shorter). Shoot richer than the walk-in so eval can pass gates; the pipeline must still work on the walk-in budget (2–8 photos). A rehearsal on a room **not** in this benchmark lives under `data/private/walkin/` (`docs/walk-in.md`).

Hardware: **iPhone 17 Pro** (LiDAR). Tape or laser everything.

## Privacy

Do not commit faces, kids, documents, mail, or a space you do not want in git. Otherwise: `data/private/` gitignored and note the path in `HANDOFF.md`.

## Composition (prompt-mandated)

- 3+ rooms **plus a connector** (hallway)
- Same spaces at **photos, video, and LiDAR**
- One furnished room with **two staged damage classes** (e.g. water stain + hole/tear). Photograph the staging.
- One room captured **twice at LiDAR**. Also twice at photos and twice at video if you have time (repeatability gate).
- Laser/tape: every wall used in eval, every opening width, every ceiling, at least one diagonal per room
- Incumbent: Polycam **or** magicplan free tier, named version, **two rooms**, export submitted. Do not use that app as our capture route.

## Photos (8 stills per room — protocol max)

Folder `photos/<room_label>/`. JPEG, rear camera, no Live/Portrait/Cinematic, no zoom, lights on.

Per room, 8 frames:

1. In the doorway facing in (full door frame — scale prior)
2–5. One per wall, both corners in frame
6. Through the door into the next room (stitch)
7. Ceiling–wall junction on the longest wall
8. Damage close-up if this is the staged room; otherwise a second corner/overlap shot

Also keep a **2-photo subset** listed in the manifest so we can crash-test the walk-in floor (2 stills). `make walkin` now builds that subset automatically from the first two stills in the holdout photo job.

## Video

One clip per property (and a second clip of the repeat room if time). Chest height, 1080p, slow, pause 2s at corners, walk the hallway. 60–180s.

## LiDAR

Record3D (depth+poses+intrinsics) and, if easy, a RoomPlan JSON. Continuous scan through rooms if the app allows. Repeat the same room in a second session for repeatability. Export into `lidar/` including intrinsics. Case must not cover the LiDAR window.

## Folder

```text
data/fixtures/benchmark_home_01/
  manifest.yaml
  photos/<room>/
  video/
  lidar/
  incumbent/<app-version>/
  extras/tape_*.jpg
  ground_truth.json
  README.md
```

## `manifest.yaml` minimum

```yaml
job_id: benchmark_home_01
device: "iPhone 17 Pro"
rooms: [living, hallway, kitchen, bedroom]
repeat_room: kitchen
damage_room: kitchen
damage_classes: [water_stain, puncture]
known_lengths_cm:
  - {name: kitchen_door, cm: 81, kind: door_width}
ceiling_height_cm_by_room:
  kitchen: 250
```

Ground truth is **tape/laser**, never RoomPlan or Polycam.

## Avoid

Mirrors dead-on as the only wall evidence, shooting through glass, wet glossy floors as the only floor, digital zoom, other people’s faces.

## Preflight after copying files

Copy `data/templates/benchmark.yaml` to `data/private/benchmark.yaml`, edit only
its relative paths, then run `make benchmark`. Review:

- `out/benchmark/benchmark-summary.md` — human checklist and tier outcomes;
- `out/benchmark/benchmark-status.json` — machine-readable pending/run/eval state.

The command exits successfully when the audit runs even if evidence is pending.
Pipeline failures remain visible per tier and are not reclassified as scores.
