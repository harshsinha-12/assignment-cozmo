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
in the diagnostic so metric pose parsing can plug in without changing the job
layout.

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
