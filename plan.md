# Plan (provisional)

Status: **provisional** until `docs/takehome.md` contains the official prompt.  
Last updated: 2026-09-07.

This is the working technical plan for the Cozmo take-home as we understand it today. When the official packet arrives, reconcile it here in one pass (`docs/prompts/ingest-takehome.md`). Do not fork a second plan in chat.

## 1. What we are actually being asked

Not “make a floor-plan picture.”

Produce a **metric, stitched, structured floor plan** from a phone, with accuracy that can be discussed in centimetres, across three capture qualities:

| Tier | Typical capture | What physics you get | Honest accuracy |
| --- | --- | --- | --- |
| LiDAR | iPhone Pro RoomPlan / ARKit mesh, or Android depth where it exists | Metric scale almost for free | Target **cm-level** on walls that were scanned |
| Video | Handheld walkthrough MP4, maybe IMU / ARKit poses in the container | Scale from VO+IMU or from a calibrated camera + known height | Often **2–10 cm** on clean Manhattan rooms if scale is good; worse on textureless walls |
| Photos | Burst of stills, possibly from a homeowner, possibly no overlap | SfM up to similarity (no scale) unless you add a prior | **Do not claim cm** without a scale prior + overlap. Report intervals |

Cozmo’s real product need (why this is not a random CV puzzle): a restoration crew or a homeowner at 2am sends visual evidence, and the desk still has to **sketch rooms in Xactimate** before line items can be written. Dimensions drive drywall, baseboard, flooring, and paint. Wrong walls waste an adjuster’s hour and fail carrier review.

## 2. Design thesis

**Three frontends, one intermediate representation, one eval.**

```text
photos ─┐
video  ─┼─► Capture Normalizer ─► Reconstruction ─► FloorPlan IR ─► stitch ─► render + eval
lidar  ─┘         │                      │
                  ▼                      ▼
            provenance              scale + gravity
```

If the take-home is a weekend packet, this thesis still wins the technical discussion: you show you can degrade gracefully instead of building three disconnected demos.

## 3. FloorPlan IR (the actual product)

Canonical schema: `docs/schemas/floorplan.schema.json`.

Minimum contents:

- **Units:** centimetres in the public API, metres internally if a library demands it. Convert at the boundary. Never mix.
- **Rooms:** id, label, polygon on a floor plane, ceiling height if known, area.
- **Walls:** id, room ids, start/end in floor coordinates, length_cm, thickness if known, confidence.
- **Openings:** doors, windows, cased openings; parent wall; width_cm; offset along wall.
- **Stitch graph:** rooms as nodes, openings/shared walls as edges, SE(2) transforms.
- **Provenance:** tier, scale source, gravity source, input hashes, algorithm versions, per-measurement error if computed.
- **Warnings:** missing scale, non-Manhattan, disconnected components, walls below confidence.

Downstream (even if we never emit ESX): this is the shape of data you would hand to an estimate agent. That is the Cozmo-shaped part.

## 4. Pipeline by stage

### 4.1 Capture normalizer

Accept a job directory, not a single file:

```text
job/
  manifest.yaml          # tier, device, claimed ceiling height, tape measures
  photos/                # jpg/heic
  video/                 # mp4/mov
  lidar/                 # captured_room.json, usdz, ply, pcd
  extras/                # arkit poses, imu csv, known-object notes
```

Emit a `NormalizedCapture` object: frames (timestamp, image path, optional pose, optional depth), intrinsics, gravity if any, LiDAR primitives if any.

HEIC and iPhone `.MOV` with spatial metadata are likely. Cloud Agents should use `pillow`/`opencv` plus `ffmpeg`; add `pillow-heif` only if fixtures need it.

### 4.2 Reconstruction (tier-specific)

**LiDAR (do this first once coding starts).**  
Parse Apple `CapturedRoom` JSON: `walls`, `doors`, `windows`, `openings`, `objects`, each with `dimensions` (metres) and a 4×4 `transform`. Project wall segments onto the floor plane (gravity = scan up vector). This already *is* a floor plan. Work is: schema mapping, multi-room `CapturedStructure` merge, confidence filtering, export.

**Video.**  
Preferred path if poses exist: use them, do not re-solve SfM from scratch.  
Fallback: ORB-SLAM-style or OpenCV + sequential SfM on sampled frames, then floor-plane fit using gravity (IMU) or the largest horizontal plane. Scale from (in order): LiDAR hybrid, ARKit/ARCore poses, IMU, known door/ceiling, user tape measure in `manifest.yaml`.

**Photos.**  
Classical SfM (COLMAP when the environment can bear it; OpenCV incremental SfM as the Cloud-Agent-friendly fallback). Recover Manhattan vanishing points for wall directions. Scale is mandatory and usually missing — require `manifest.yaml` scale priors or refuse metric output and return **unitless + warning**.

### 4.3 Floor extraction

Once you have a metric point cloud or wall primitives:

1. Estimate gravity / floor plane.
2. Slice a band at ~10–120 cm above floor (skip clutter, skip ceiling).
3. Project to 2D occupancy or line primitives.
4. Fit Manhattan (or piecewise-linear) wall loops with RANSAC.
5. Detect openings as gaps in walls or as LiDAR opening primitives.
6. Regularize: right angles, snap near-collinear segments, close loops.

Do not skip regularization. Raw SfM walls look drunk and will lose the interview.

### 4.4 Stitch

Rooms are not a slideshow. Build a pose graph:

- LiDAR: use RoomPlan structure builder / shared-wall identities when present.
- Video: time-ordered loop closures when the camera re-enters a doorway.
- Photos: match openings by width + visual overlap, or require a capture protocol (“leave the previous room through the door, shoot the frame”).

Optimize SE(2) on the floor plane. Report residual error in cm.

### 4.5 Dimensioning

For every wall: Euclidean length in cm, rounded **after** eval, not before.  
Carry a confidence interval when the scale source is weak (photos + assumed 80 cm door).  
Ceiling height: LiDAR dimensions, or video/photo if vertical VP + known door height.

## 5. Eval (non-negotiable)

`docs/eval-and-accuracy.md` is the full write-up. The plan in one sentence: **synthetic rooms first, one real taped room second, never screenshots alone.**

Metrics, all in cm:

- Wall length absolute error (median, p95)
- Room area error (cm² and %)
- Opening width error
- Stitch translation error at doorways
- Failure rate (no plan produced)

Gate: LiDAR fixture should be clearly better than video, video better than photos, or we explain why the fixture is too easy.

## 6. What we will ship as a repo (predicted)

Until the prompt says otherwise:

- `src/cozmo_floorplan/` Python package
- CLI: `python -m cozmo_floorplan run path/to/job --out path/to/out`
- JSON FloorPlan + SVG overlay + `eval.json`
- `make test` on synthetic fixtures (Cloud Agent friendly)
- A 1–3 page write-up in `docs/writeup.md` (create when coding starts)

Optional, only if time remains: FastAPI job endpoint, simple static SVG viewer. Not the main act.

Out of scope unless the prompt demands it: training nets, ESX binary export, full Matterport clone, iOS app, realtime AR.

## 7. Risks

| Risk | Why it kills take-homes | Mitigation |
| --- | --- | --- |
| No official spec | Overbuilding the wrong output | IR + eval first; adapters later |
| Scale blindness | “cm-level” from monocular photos | Provenance + refuse metric if no prior |
| COLMAP too heavy for Cloud Agents | Env install never finishes | OpenCV path default; COLMAP optional extra |
| Textureless indoor walls | SfM fails in bathrooms / painted drywall | LiDAR/video first; photos need overlap instructions |
| Non-Manhattan / curves | Regularizer invents wrong walls | Detect, warn, keep polylines |
| Timebox | Perfect photos tier, nothing runnable | LiDAR → eval → video → photos |

## 8. Decision policy

When two designs are equal, pick the one that is:

1. Explainable in the technical discussion
2. Runnable on a Linux Cloud Agent
3. Degradable across tiers
4. Closer to structured claims data

Record the choice in `docs/decisions.md`.
