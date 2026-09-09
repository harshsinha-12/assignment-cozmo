# Video job layout

T7 ingests handheld room walkthroughs without inventing centimetres. Metric visual odometry still needs a validated metric pose/scale path. Until that lands, the adapter samples every video, normalizes display orientation, and returns a structured failure.

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
in the diagnostic so metric pose parsing can plug in without changing the job
layout.

Current private diagnostics: `my-room.mp4` → 138 samples / 68.56 s;
`pooja-room.mp4` → 148 samples / 73.91 s. These are ingest facts, not geometry
or accuracy results.
