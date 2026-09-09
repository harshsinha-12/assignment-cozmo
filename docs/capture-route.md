# Capture route (Route 2) — walk-in card

**Status:** protocol-ready; accuracy remains unclaimed until measured. Print this page for the operator. We use one route: built-in **Camera** for photos/video and **Record3D** for LiDAR. Do not use Polycam or magicplan; they are comparison incumbents. Do not drop files into an existing benchmark folder.

| Tier | Phone | Handoff |
| --- | --- | --- |
| Photos | Any iPhone 15+ | Eight JPEG stills per room |
| Video | Any iPhone 15+ | One 1080p MOV/MP4 |
| LiDAR | Pro / Pro Max with LiDAR | Complete Record3D depth + poses + intrinsics export |

## Before walking

Copy **one** job template into a **new** folder and replace every `replace-me` manifest value. Use the walk-in templates if this is not the author's benchmark property:

```bash
cp -R data/templates/walkin/walkin-photos JOB   # or walkin-video / walkin-lidar
```

Name the room something other than `drawing-room`, `my-room`, `pooja-room`, or `connector`. One job contains one tier. Turn on lights; use the rear camera with no flash, zoom, portrait, or cinematic mode. Clear people and pets when possible. Walk slowly and pause at corners and doors.

## Photos — exactly eight per room

Put each room in `photos/<room_label>/`. Shoot landscape at chest height:

- **1:** From the doorway, facing inward with the full frame visible.
- **2–5:** One view per wall, including both corners.
- **6:** Through the doorway toward the next room or hallway.
- **7:** The ceiling–wall junction on the longest wall.
- **8:** One overlapping corner view, or a damage close-up in the staged room.

For a non-four-wall room, retain the doorway, through-door, and ceiling views and allocate the remaining frames to walls. If eight cannot cover it, start a second job; the loader accepts at most eight per room. Two stills is the pipeline floor and is not the capture target.

## Video — one continuous clip

Start at the entry at chest height. Walk each room perimeter, pause two seconds at every corner, and keep recording through each doorway. Give a connector/hallway its own slow pass. Stop after the final room. Target 60–180 seconds; do not run or use the selfie camera. Save as `video/walkthrough.mov` or `.mp4`.

**Current metric boundary:** the built-in Camera file carries no ARKit poses or
calibrated intrinsics, so it exercises ingest/tracking but cannot by itself
authorize centimetres. If a capture tool supplies the v1.2 sidecar documented
in `docs/formats/video-job.md`, preserve it beside the matching video. Do not
manufacture that sidecar from timestamps or EXIF.

## LiDAR — one complete export

In Record3D, cover every wall, the waist-height floor band, and every opening. Keep one session while moving between rooms when possible; otherwise use ordered room names. AirDrop the complete original session into `lidar/`, record the app version/export format, and keep depth, camera poses, and intrinsics—not preview images alone.

If a RoomPlan JSON export is available, name it `roomplan.json` and follow `docs/formats/roomplan-json.md`. **Current boundary:** the CLI reconstructs RoomPlan JSON and emits partial metric FloorPlan geometry from original Record3D `.r3d` archives. Raw `.r3d` intervals and cross-room registration remain unverified until tape/repeat/connector evidence is supplied.

## Handoff

AirDrop the job folder (or a ZIP of that folder). Originals must open on the laptop.

- Exact device and app/version are in `manifest.yaml`; deviations are in `notes`.
- Every expected room/connector is present.
- Mirrors, glass, glossy floors, and case lips blocking LiDAR are avoided.
- More overlap and a slower walk are the safe defaults.

On the laptop we run **one command per job** while you laser the room:

```bash
python -m cozmo_floorplan run path/to/job --out path/to/out
```

Do not run `make benchmark` on a walk-in folder. After our own holdout capture, `make walkin` times all three tiers; that rehearsal is documented in `docs/walk-in.md`.
