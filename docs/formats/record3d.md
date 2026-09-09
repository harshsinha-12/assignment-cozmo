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

## T21 Cozmo Capture archives

The iOS app can write Record3D-compatible `.r3d` files from ARKit `sceneDepth`
while a RoomPlan scan is running. Those files ship inside the job ZIP next to
`roomplan.json` (`docs/formats/cozmo-capture-job.md`). Sampling is 2 Hz, at most
90 frames per room. Frames without depth and confidence are skipped. ZIP
members, LZFSE payloads, XYZW camera-to-world poses, and `fx, fy, cx, cy`
intrinsics match this adapter.

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

## Openings and FloorPlan output

T6b3 profiles points near each accepted wall. A floor-reaching sparse band is a
door candidate only when the wall has surviving lintel support; a middle sparse
band is a window candidate only when both sill and lintel support survive.
Floor-reaching gaps 1.40–2.40 m are `cased_opening` (wide entrance), not doors.
Each room keeps the strongest door and the strongest cased opening. Configured
width ranges, wall-end margins, short-gap bridging, and height-change evidence
reject unconstrained empty space. Solid-wall synthetic tests must yield zero
openings.

Accepted rooms now produce `floorplan.json` and `floorplan.svg` with metric room
polygons, four walls, ceiling height, area, and supported openings. T6d derives
each room's wall-span and ceiling half-widths from the conservative p95 residual
envelope around its fitted raw planes, then propagates span uncertainty into
area. Fixed configured widths remain minimum floors, and opening intervals
remain fixed candidates. The current partial tape benchmark covers 16/18
measurements (88.9%) against 80% mean declared confidence. This passes the
internal coverage policy on the development benchmark but is not independent
holdout calibration.

## Current boundary

Three separate archives currently produce three rooms, twelve walls, and
supported opening candidates. Frame-invariant evaluation reports **2.5 cm wall
median and 30 cm p95** across the twelve walls; the large residual is real. The
visible raw planes strongly support the 3.70 m `my-room` span, so the default
pipeline does not add an unobserved 30 cm correction. An optional clutter-band
outer-peak step exists for tall inward furniture (tested) but is **off by
default**: enabling it on this capture expanded drawing-room and pooja-room
through doorways into the next space.

The three `.r3d` files already share an ARKit world frame (camera paths occupy
different regions of one coordinate system). Openings are associated only when
centers are within 1.25 m and widths/heights agree; on the current scans no
pair meets that test, so rooms stay unregistered rather than snapping 80 cm
bedroom doors together across a missing connector.

Tape now includes entrance widths/heights in `data/private/ground_truth.json`
with `wall_id: unlocated` (supporting walls/offsets were not measured). Eval
matches those by kind and width. Connector LiDAR is still missing.

Ceiling densest-peak heights are about 292–295 cm against 290 cm tape (max
~5.4 cm). That remains above the 1.5 cm official ceiling gate.
