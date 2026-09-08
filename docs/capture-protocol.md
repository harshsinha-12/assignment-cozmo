# Capture protocol (phone)

Do this even before the official prompt. One real room with tape measures will dominate a synthetic-only submission.

## Privacy

Do not commit photos of other people’s faces, kids, documents, mail, or a space you do not want in a private GitHub. If in doubt: keep captures local and put only `manifest.yaml` + tape numbers in git. Note the local path in `HANDOFF.md`.

## What to capture (same room, same day)

1. **Tape sheet** — two long walls, one short wall, door width, optional diagonal. Photo of the tape against the door.
2. **Photos** — 20–40 stills, landscape, walk the perimeter, 60% overlap, extra frames through each door. Include corners. Turn off a wandering “cinematic” mode if it crops randomly. JPEG is easier than HEIC for Linux.
3. **Video** — 30–90 seconds, slow, hold the phone at chest height, pan walls, pause at corners, walk through the door if there is a second space. 1080p is enough. Avoid selfie camera.
4. **LiDAR** — if iPhone Pro / iPad Pro: RoomPlan or a Polycam/magicplan/KIRI export. We want **JSON** (`CapturedRoom`) plus USDZ if easy. Put JSON in `lidar/captured_room.json`.

## Folder to create

```text
data/fixtures/real_room_01/
  manifest.yaml
  photos/
  video/
  lidar/
  extras/tape.jpg
  ground_truth.json   # from the tape sheet, not from RoomPlan
  README.md
```

## `manifest.yaml` minimum

```yaml
job_id: real_room_01
tier: mixed
device: "iPhone ??"
ceiling_height_cm: 250
known_lengths_cm:
  - name: entry_door
    cm: 81
    kind: door_width
  - name: north_wall
    cm: 412
    kind: wall
  - name: east_wall
    cm: 305
    kind: wall
notes: "rectangular bedroom, one closet door ignored"
```

`ground_truth.json` should follow `docs/schemas/floorplan.schema.json` as soon as you are willing to type polygons. If not, keep the tape list in the manifest; an agent can turn it into JSON later.

## Shooting rules that save the photos tier

- Overlap is the feature. Artistic single shots are useless.
- Turn on lights. Night ISO noise kills matching.
- Do not use digital zoom.
- If a wall is blank, include the adjacent corner in the same frame so features exist.
- For stitch, shoot the doorway from both rooms.

## iOS export tips

RoomPlan sample apps and some third-party scanners can dump JSON. If the app only shares USDZ, still keep it; parsing USDZ is worse but recoverable. Do not spend the evening writing a Swift app unless the official prompt requires one.

## Cloud Agent upload

Keep fixtures small. Downscale JPEGs to ~1600 px on the long side if the repo would exceed a few tens of MB. Video: 720p is acceptable for a fixture. GitHub does not want 2 GB of 4K.
