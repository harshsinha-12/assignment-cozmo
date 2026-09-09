# Record3D `.r3d` input

Put complete, original Record3D archives in `job/lidar/*.r3d`. Do not export a
preview-only MP4, point-cloud screenshot, or mesh in place of the session.

## Validated archive contract

The adapter now reads the real September 9 captures and checks:

- ZIP container with a JSON `metadata` entry
- `w`, `h`, `dw`, `dh`, `fps`
- one timestamp, seven-value camera pose, and four-value intrinsic row per frame
- contiguous, matched `rgbd/<index>.jpg`, `.depth`, and `.conf` entries
- JPEG dimensions matching metadata
- LZFSE depth decoded as little-endian float32 metres at `dw × dh`
- LZFSE confidence decoded as uint8 at `dw × dh`, with values in `0..2`

The Python `lzfse` package is the portable decoder. On macOS, the reader also
uses the system Compression framework if the package is not installed.

## Metric point generation

T6b1 deterministically samples 61 frames, scales the RGB intrinsics to the depth
resolution, back-projects positive depth along OpenGL camera negative-Z, applies
the normalized XYZW camera-to-world pose, filters depth/confidence, and averages
points into 2.5 cm world-space voxels. Counts and bounds are diagnostic evidence;
they are not room measurements.

## Plane candidates

T6b2 detects strong horizontal floor/ceiling bands around the camera level,
retains x-z columns that span at least 1.5 m vertically, searches a 0.5-degree
Manhattan orientation, and selects two wall peaks per local axis that bracket
the observed camera trajectory. This prevents low furniture and raw cloud
outliers from becoming room bounds. All thresholds live in
`recon/record3d_config.py` and the geometry lives in
`recon/record3d_planes.py`.

The three current private scans all yield four-wall candidates and plausible
horizontal separation. These are diagnostics, not accuracy results: no official
gate is scored until tape/laser truth exists.

## Current boundary

RGB-D decoding, metric world-cloud generation, and conservative room-plane
candidates work on the real captures. The CLI still returns structured
`unsupported_tier` until opening extraction and FloorPlan IR conversion are
implemented.
