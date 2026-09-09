# Video job layout

T7 ingests handheld room walkthroughs without inventing centimetres. Metric visual odometry still needs a validated metric pose/scale path. Until that lands, the adapter samples every video, normalizes display orientation, recovers diagnostic scale-free pose segments, and returns a structured failure.

## Directory

```text
job/
  manifest.yaml          # tier: video
  video/
    drawing-room.mp4     # or .mov / .m4v
    drawing-room.poses.json  # optional matching ARKit/ARCore cameras
    my-room.mp4
    my-room.poses.json
```

Use one walkthrough per room. The filename stem is the stable room identifier,
and every supported file is sampled in sorted order. For a single video, the
global names `poses.json`, `arkit_poses.json`, and `cameras.json` remain accepted.
For multiple videos, use `<video-stem>.poses.json`,
`<video-stem>.arkit_poses.json`, or `<video-stem>.cameras.json`; a global
sidecar is reported as ambiguous rather than attached to every room.

## Sampling

Frames are read with OpenCV at about 2 Hz, capped at 240 frames per video. A clip
that yields fewer than 8 sampled frames is `incomplete_scan`.

Container display rotation is handled explicitly: backend auto-rotation is
disabled, the nearest supported quarter turn is applied once, and the resulting
RGB frame dimensions are recorded. Non-quarter-turn metadata or a backend that
cannot disable auto-rotation fails structurally instead of risking double
rotation. The two current iPhone videos report 90° clockwise and normalize to
720×1280 portrait frames.

## Metric boundary

Phone video has **no metric scale** unless camera poses are metric
(ARKit/ARCore/Record3D) or a known length is supplied later. The adapter will
not print centimetres from an uncalibrated MP4. Sidecars are detected and named
by video stem, strictly validated, and matched to decoded samples by both
encoded frame index and clip-relative timestamp.

Current private diagnostics: `my-room.mp4` → 138 samples / 68.56 s;
`pooja-room.mp4` → 148 samples / 73.91 s. These are ingest facts, not geometry
or accuracy results.

## Feature-track gate

T7c analyzes at most 60 evenly spaced adjacent sample pairs per room. Frames are
bounded to 640 px on the long edge, then ORB features use Hamming ratio matches,
a seeded fundamental-matrix RANSAC, and a homography residual. A pair is eligible
only when it has enough keypoints, matches, geometric inliers, image motion,
non-homographic parallax, and convex-hull coverage. Each failed condition is
counted by name. A walkthrough needs at least 35% eligible analyzed pairs before
relative VO can proceed.

Current real results:

| Room | Eligible pairs | Median keypoints | Matches | F inliers | Motion | Homography-residual parallax | Coverage |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| my-room | 23 / 60 | 1,166 | 262 | 178 | 78.28 px | 1.15 px | 23.5% |
| pooja-room | 27 / 60 | 1,188 | 257 | 190 | 93.41 px | 1.23 px | 20.6% |

Both pass this internal relative-VO eligibility gate. This proves trackable
image evidence, not metric scale, wall dimensions, or the official ±3% gate.

## Scale-free trajectory boundary

T7d selects at most 90 frames, reuses the same ORB/fundamental correspondences,
and estimates an essential matrix per eligible edge. Because native video does
not provide calibrated intrinsics here, the focal length is a disclosed
image-size prior (`0.9 × max(width, height)`). Each recovered translation is
normalized to a unit direction before chaining; the resulting coordinates are
therefore **unitless**, not metres or centimetres.

A rejected feature or pose edge closes the active trajectory segment. A later
accepted edge starts a new segment at a local identity pose. The adapter reports
break and restart counts but does not pretend those independent segments have
been globally relocalized. A validated metric pose sidecar or known-length
constraint must supply scale and segment alignment before room geometry can be
written to the FloorPlan IR.

Current real results: `my-room` recovers 21/89 edges in 10 local segments;
`pooja-room` recovers 17/89 in 9. Fragmentation is retained as evidence rather
than bridged with guessed motion.

## Metric pose sidecar v1

Use `<video-stem>.poses.json` for every multi-video job. A single-video job may
also use `poses.json`. The contract is deliberately explicit:

```json
{
  "schema_version": "1.0.0",
  "units": "m",
  "transform": "camera_to_world",
  "coordinate_system": "right_handed_y_up",
  "timestamp_origin": "video_start",
  "poses": [
    {
      "source_frame_index": 0,
      "timestamp_s": 0.0,
      "position_m": [0.0, 1.45, 0.0],
      "rotation_xyzw": [0.0, 0.0, 0.0, 1.0]
    }
  ]
}
```

Frame indices and timestamps must be unique and strictly increasing. Positions
must be finite metres and quaternions must have unit norm. The pipeline retains
each sampled frame's original encoded index and timestamp; an alignment match
requires the frame index to exist and its timestamp to agree within 25 ms.

Each local VO segment needs at least three matched poses and two-dimensional
trajectory spread. An orientation-preserving 3D similarity is accepted only at
≤0.15 m matched-position RMSE. These are conservative internal eligibility
thresholds, not the official ±3% wall gate. T7e alignment uses camera positions
only.

Schema `1.0.0` remains valid for position alignment, but it cannot authorize
triangulation because it has no calibrated camera model. Schema `1.1.0` adds
display-oriented intrinsics and explicit OpenCV camera axes for T7f sparse
triangulation. T7g FloorPlan output uses schema `1.2.0`, which also identifies
the metric source and shared world frame:

```json
{
  "schema_version": "1.2.0",
  "units": "m",
  "transform": "camera_to_world",
  "coordinate_system": "right_handed_y_up",
  "camera_axes": "x_right_y_down_z_forward",
  "world_frame_id": "walkthrough-session-a",
  "scale_source": "arkit_poses",
  "timestamp_origin": "video_start",
  "intrinsics": {
    "fx_px": 1060.2,
    "fy_px": 1058.9,
    "cx_px": 359.5,
    "cy_px": 639.5,
    "image_size_px": [720, 1280]
  },
  "poses": [
    {
      "source_frame_index": 0,
      "timestamp_s": 0.0,
      "position_m": [0.0, 1.45, 0.0],
      "rotation_xyzw": [0.0, 0.0, 0.0, 1.0]
    }
  ]
}
```

`image_size_px` must match the normalized display frame after container
rotation. Focal lengths must be positive and the principal point must lie in
the image. `scale_source` must be `arkit_poses` or `arcore_poses`.
In v1.2, `world_frame_id` identifies the uninterrupted exported tracking frame; every
room in a multi-video job must name the same frame. Values must come from the
capture API/export, not EXIF guesses.

## Sparse metric triangulation

T7f reuses robust fundamental-matrix inliers only inside a trajectory segment
whose metric alignment was accepted. Each adjacent frame must also have an
exact source-frame/timestamp pose. Calibrated projection matrices triangulate
world points, which are then filtered by positive 0.10–20 m depth in both
cameras, at most 2 px reprojection error, at least 1.5° ray angle, and 3 cm
voxelization.

## Conservative room conversion

T7g searches Manhattan yaw and requires supported floor and ceiling bands plus
two wall bands on each planar axis that bracket the accepted metric camera
path. Room spans and ceiling height must remain within configured residential
bounds. Only then does the adapter emit a four-wall room in the shared
FloorPlan IR.

Measurements include candidate-stage intervals and the output remains
`partial`: those intervals are not calibrated without tape/laser truth, and the
video path does not yet detect openings. Multiple video rooms may share their
exported coordinates only when all sidecars name one `world_frame_id`; even
then, adjacency and drift correction stay pending until a shared opening is
proven.

The two current native Camera-app MP4s do not have sidecars, so their diagnostic
output says `metric_alignment=not-available` and stays structurally unsupported.
