# Capture tiers

How each tier becomes a FloorPlan. Details and citations: `docs/research.md`.

## Shared rules

- Internal geometry may use metres. The IR emits **centimetres**.
- Record `scale_source` always.
- Prefer gravity from the device. If missing, fit the dominant floor plane and assume the smallest room dimension is not “up.”
- Regularize walls. Raw traces are not a floor plan.

## Tier L — LiDAR

**Best path for centimetre talk.**

On iPhone Pro, Apple RoomPlan already returns parametric walls and openings with metric dimensions. Our work is not “detect a wall.” It is:

1. Ingest `CapturedRoom` / `CapturedStructure` JSON (and USDZ only if JSON is missing)
2. Drop to 2D using the scan’s up axis
3. Join rooms on shared openings
4. Copy confidence into the IR
5. Eval against tape or against the JSON itself (consistency) plus one independent tape measure if we have a real room

Android: there is no RoomPlan. Depth + ARCore poses or a PLY from a third-party scanner. Treat as point-cloud path (same as a meshed USDZ).

**Failure modes:** glass, mirrors, incomplete loops if the user did not scan a wall, furniture as false walls if we slice badly. Mitigate with the 10–120 cm slice and RoomPlan categories (prefer `walls` over `objects`).

## Tier V — Video

Sample frames (`ffmpeg`, 2–5 Hz, higher on rotation). Two sub-paths:

1. **Poses included** (ARKit/ARCore dump, some `.mov` metadata): treat cameras as known. Triangulate or back-project if depth exists. Scale from poses if they are metric.
2. **Poses missing:** track features, essential/homography, integrate a trajectory, align up using IMU if the file has it, else assume handheld with gravity ≈ image down at rest frames.

Floor extraction: accumulate a point cloud or occupancy from tracked wall/floor features, then the same 2D regularizer as LiDAR.

**Failure modes:** motion blur, rolling shutter, pure rotation, featureless paint, people walking through. Fallback: tell the user to re-walk slower; return partial rooms.

**Current implementation:** T7b discovers every room video, keeps filename-stem
identity, samples each at about 2 Hz, disables OpenCV auto-rotation, and applies
the container quarter-turn exactly once. Per-video pose sidecars are associated
by stem; global sidecars are accepted only for a single walkthrough. T7c adds a
deterministic ORB/fundamental-matrix track gate with motion, homography-residual
parallax, coverage, and named rejection reasons. Both current videos pass the
internal relative-VO eligibility ratio. Relative trajectory, metric scale, and
FloorPlan output remain.

## Tier P — Photos

Hardest. Needs overlap (rule of thumb: 60%+ , ring around the room, shots through doorways for stitch).

Pipeline: features (SIFT/ORB) → matching → incremental SfM → sparse cloud → (optional dense) → same floor slice.

**Scale is not optional to “cm-level.”** Acceptable priors, in order:

1. Mixed job that also has LiDAR
2. ARCore/ARKit camera origins in extras
3. A tape length in the manifest that we can identify (two clicked points, or a detected door compared to `known_lengths_cm`)
4. Standard door 80 cm / 32 in as a **weak** prior, labelled as such, with a wide interval

If none exist: output a unitless plan (`units: "relative"`) and a warning. Do **not** pick a scale factor of 1.0 and print centimetres.

**Failure modes:** two photos of opposite corners with no overlap, HDR ghosts, HEIC orientation, wide-angle distortion. Fail early with `insufficient_overlap`.

## Mixed jobs

A restoration walk is often LiDAR on the adjuster’s iPhone plus homeowner JPEGs. Design the normalizer so a job can list `tier: mixed` and the stitcher can use LiDAR as the metric scaffold and photos as texture/evidence only (even if we never implement texture).

## What we will implement first

LiDAR JSON → IR → SVG → eval. Everything else reuses extract + stitch.

**Current implementation:** portable RoomPlan JSON v1 → FloorPlan works against `data/fixtures/roomplan_two_room`. T9 plane-anchors shared openings (shared walls stay with the first owner room) and writes a poses-as-is ablation. See `docs/formats/roomplan-json.md`. T6a validates and decodes real Record3D archives; T6b1 builds deterministic metric world clouds; T6b2 detects floor/ceiling levels and four conservative Manhattan wall candidates; T6b3 adds evidence-gated openings and partial FloorPlan conversion (`docs/formats/record3d.md`). Separate archives are not called registered or accurate without connector and tape evidence. USDZ remains unsupported.

Video: frames are sampled from `video/*.mp4` (`docs/formats/video-job.md`). Metric VO is not implemented; uncalibrated walkthroughs do not emit centimetres.

Photos: per-room folders and 2–8 decodable images per room are validated (`docs/formats/photo-job.md`). Metric SfM, adjacency inference, and calibrated scale still wait on real captures; ingest does not emit invented centimetres.
