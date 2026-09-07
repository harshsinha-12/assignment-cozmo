# Architecture

Provisional. Implementation lives under `src/cozmo_floorplan/` only after `docs/takehome.md` is filled.

## Layers

```text
┌──────────────────────────────────────────────────────────┐
│  CLI / optional HTTP  (run job, emit JSON+SVG+eval)      │
├──────────────────────────────────────────────────────────┤
│  FloorPlan IR  (docs/schemas/floorplan.schema.json)      │
│  stitch · dimension · provenance · warnings              │
├─────────────┬──────────────┬─────────────────────────────┤
│ LiDAR map   │ Video recon  │ Photo SfM + scale policy    │
├─────────────┴──────────────┴─────────────────────────────┤
│  Capture normalizer  (job dir, manifest, ffmpeg, EXIF)   │
└──────────────────────────────────────────────────────────┘
                         │
                         ▼
                   eval vs fixtures
```

## Job directory

```text
job/
  manifest.yaml
  photos/
  video/
  lidar/
  extras/
```

`manifest.yaml` (draft):

```yaml
job_id: synthetic_two_room
tier: lidar | video | photos | synthetic | mixed
units_note: "tape measures in cm"
device: "iPhone 14 Pro"
ceiling_height_cm: 250
known_lengths_cm:
  - name: door_to_kitchen
    cm: 80
    kind: door_width
gravity: "device" | "unknown"
privacy: "no faces"
```

## Module sketch (do not create empty packages until Phase 2)

- `io.job` — load manifest + files
- `io.roomplan` — CapturedRoom JSON
- `geom` — SE(2), cm/m, polygons, wall snap
- `recon.lidar` / `recon.video` / `recon.photos`
- `extract.walls` — slice, RANSAC, Manhattan
- `stitch`
- `render.svg`
- `eval`

Public function:

```text
run_job(job_dir: Path, out_dir: Path) -> FloorPlan
```

## Error model

Never throw away a job with a generic exception if you can return a FloorPlan with `warnings` and `status: partial | failed`. Interviewers will ask what happens in a white bathroom with one photo. The answer is a structured failure, not a crash.

## Why not three apps

A LiDAR demo, a COLMAP demo, and a vanishing-point demo will not stitch and will not share evals. The IR is the take-home. Algorithms are adapters.

## Optional HTTP

Only if the prompt wants an API:

- `POST /jobs` multipart job dir or zip
- `GET /jobs/{id}` status
- `GET /jobs/{id}/floorplan.json`
- `GET /jobs/{id}/floorplan.svg`

Skip auth, skip queue, skip GPU workers unless they demand scale theatre.
