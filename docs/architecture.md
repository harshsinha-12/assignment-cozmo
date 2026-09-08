# Architecture

Aligned with Round 2. T12 froze the schema; implementation starts in `src/cozmo_floorplan/` with T13. Not a website — CLI + JSON + SVG. Optional HTTP only if leftover and JSON already works.

## Layers

```text
┌──────────────────────────────────────────────────────────┐
│  CLI  python -m cozmo_floorplan run JOB --out OUT        │
├──────────────────────────────────────────────────────────┤
│  Agent + tools  (disclosed LLM API)                      │
│  damage class · concealed rule ids · scope lines         │
│  fallback: same tools, no API                            │
├──────────────────────────────────────────────────────────┤
│  FloorPlan IR  walls · openings · stitch · intervals     │
│  (numbers come from recon, not from the model)           │
├─────────────┬──────────────┬─────────────────────────────┤
│ LiDAR map   │ Video recon  │ Photo recon + scale/CIs     │
├─────────────┴──────────────┴─────────────────────────────┤
│  Capture normalizer  (job dir, manifest, ffmpeg, EXIF)   │
└──────────────────────────────────────────────────────────┘
                         │
                         ▼
              eval (official gates) vs tape GT
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
- `agent` — tool-calling loop + fallback (`docs/agent-layer.md`)
- `render.svg`
- `eval`

Public function:

```text
run_job(job_dir: Path, out_dir: Path) -> FloorPlan
```

Scalar dimensions in FloorPlan v0.2 are not bare numbers. They use
`{"value": 342, "unit": "cm", "interval": {"low": 340, "high": 344, "confidence": 0.95}}`.
This keeps the point estimate and its calibrated uncertainty inseparable through recon, agent tools, rendering, and eval.

## Error model

Never throw away a job with a generic exception if you can return a FloorPlan with `warnings` and `status: partial | failed`. Interviewers will ask what happens in a white bathroom with one photo. The answer is a structured failure, not a crash.

## Why not three apps

A LiDAR demo, a COLMAP demo, and a vanishing-point demo will not stitch and will not share evals. The IR is the take-home. Algorithms are adapters.

## Optional HTTP

Not required. Do not add Redis, Postgres, or our own API. The walk-in is this CLI on their laptop. LLM calls go to a **disclosed public provider**, not to us.
