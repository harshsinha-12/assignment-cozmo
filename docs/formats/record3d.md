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

## Current boundary

RGB-D decoding and metric world-cloud generation work on the real captures.
The CLI still returns structured `unsupported_tier` until T6b2 fits
floor/ceiling/wall/opening planes and converts them to the shared FloorPlan IR.
