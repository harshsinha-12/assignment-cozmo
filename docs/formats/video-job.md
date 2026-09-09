# Video job layout

T7 ingests a handheld walkthrough without inventing centimetres. Metric visual odometry still needs a real capture (or a metric pose sidecar plus reconstruction). Until that lands, the adapter samples frames and returns a structured failure.

## Directory

```text
job/
  manifest.yaml          # tier: video
  video/
    walkthrough.mp4      # or .mov / .m4v
    poses.json           # optional ARKit/ARCore cameras
```

Use one walkthrough file. Extra files are ignored for now; the first name in sorted order is sampled.

## Sampling

Frames are read with OpenCV at about 2 Hz, capped at 240 frames. A clip that yields fewer than 8 sampled frames is `incomplete_scan`.

## Metric boundary

Phone video has **no metric scale** unless camera poses are metric (ARKit/ARCore/Record3D) or a known length is supplied later. The adapter will not print centimetres from an uncalibrated MP4. A `poses.json` sidecar is detected and mentioned in the warning so tomorrow’s capture can plug into VO without a layout change.

Accepted sidecar names: `poses.json`, `arkit_poses.json`, `cameras.json`.
