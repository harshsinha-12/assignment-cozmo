# Device matrix

Hardware eligibility and runtime support are different claims. “Capture” means the protocol can collect the evidence; it does not mean the current CLI reconstructs that raw format. Measurements below are specific to the current private benchmark, not a device-wide guarantee.

| Device | Photos capture | Video capture | LiDAR capture | Current accepted input | Measured accuracy |
| --- | --- | --- | --- | --- | --- |
| iPhone 15 / 16 non-Pro | yes | yes | no | JPEG; MOV/MP4 ingest | not measured |
| iPhone Pro / Pro Max with LiDAR | yes | yes | yes | JPEG; MOV/MP4 ingest; T21e exports a job ZIP with RoomPlan JSON plus Record3D-compatible `.r3d` from ARKit depth; `.r3d` emits partial metric IR | see tested iPhone row only |
| Harsh's iPhone 17 Pro | yes | yes | yes | Cozmo Capture installed (T21g). CLI accepts the job ZIP (RoomPlan JSON + `.r3d`). Route 2 Record3D rooms also produce partial IR | LiDAR walls: 2.5 cm median / 30 cm p95 over 12; intervals cover 16/18 at 80% declared confidence |
| LiDAR iPad Pro | possible, out of walk-in scope | possible, out of walk-in scope | possible | RoomPlan JSON only | not measured |
| Android | not claimed | not claimed | not claimed | out of scope | not measured |

Raw Record3D archives now pass structural/LZFSE validation, metric world-cloud generation, plane fitting, evidence-gated opening detection, support-conditioned intervals, and partial FloorPlan conversion. Separate capture registration, opening truth, and holdout calibration remain unavailable. USDZ remains unsupported.

## Accuracy we will claim (after eval)

Replace the TBD cells. Intervals are part of the score; do not tighten them to look good.

| Tier | Wall length | Openings | Ceiling | Stitched footprint | Scale source |
| --- | --- | --- | --- | --- | --- |
| LiDAR | 2.5 cm median / 30 cm p95, n=12 | unavailable: no truth openings; four predictions | 5.41 cm max error, n=3 | unavailable: scans disconnected | Record3D depth + intrinsics + metric poses |
| Video | not measured (gate: ±3%) | not measured | not measured | not measured | metric poses/VO required; plain video is unscaled |
| Photos | not measured (gate: ±8%) | not measured (≤2 cm chase; misses/phantoms scored) | not measured | not measured (gate: ±8%) | known length or calibrated prior required; monocular geometry is unscaled |

## Walk-in

They choose the tier on the day on **their** iPhone 15 or newer. A non-Pro phone supports photos/video, not LiDAR. Scored protocol: `docs/capture-route.md`. Optional Route 1 cable install: `docs/capture-route-route1.md` (no paid Apple team). Copyable manifests: `data/templates/`.
