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

## Current boundary

T6a validates and decodes RGB-D frames, poses, timestamps, and per-frame
intrinsics. It does not yet claim walls, openings, or ceiling dimensions from
raw Record3D points. The CLI reports a structured `unsupported_tier` result
after validation until the next T6 plane-extraction stage turns those metric
points into the shared FloorPlan IR.
