# Device matrix

Hardware eligibility and runtime support are different claims. “Capture” means the protocol can collect the evidence; it does not mean the current CLI reconstructs that raw format. Real accuracy stays “not measured” until T3.

| Device | Photos capture | Video capture | LiDAR capture | Current accepted input | Measured accuracy |
| --- | --- | --- | --- | --- | --- |
| iPhone 15 / 16 non-Pro | yes | yes | no | JPEG; MOV/MP4 ingest | not measured |
| iPhone Pro / Pro Max with LiDAR | yes | yes | yes | JPEG; MOV/MP4 ingest; T21b exports accepted named multi-room RoomPlan JSON; `.r3d` emits partial metric IR | not measured |
| Harsh's iPhone 17 Pro | yes | yes | yes | Three real `.r3d` room captures produce partial rooms/walls/opening candidates; photos/video partial; T21b device install pending | not measured |
| LiDAR iPad Pro | possible, out of walk-in scope | possible, out of walk-in scope | possible | RoomPlan JSON only | not measured |
| Android | not claimed | not claimed | not claimed | out of scope | not measured |

Raw Record3D archives now pass structural/LZFSE validation, metric world-cloud generation, plane fitting, evidence-gated opening detection, and partial FloorPlan conversion. Separate capture registration and intervals remain unverified without connector/repeat/tape evidence. USDZ remains unsupported. None of this is an accuracy result.

## Accuracy we will claim (after eval)

Replace the TBD cells. Intervals are part of the score; do not tighten them to look good.

| Tier | Wall length | Openings | Ceiling | Stitched footprint | Scale source |
| --- | --- | --- | --- | --- | --- |
| LiDAR | not measured (gate: ±3 cm) | not measured (≤2 cm on ≥85%) | not measured (gate: 1.5 cm) | not measured | RoomPlan dimensions/poses; raw depth adapter pending |
| Video | not measured (gate: ±3%) | not measured | not measured | not measured | metric poses/VO required; plain video is unscaled |
| Photos | not measured (gate: ±8%) | not measured (≤2 cm chase; misses/phantoms scored) | not measured | not measured (gate: ±8%) | known length or calibrated prior required; monocular geometry is unscaled |

## Walk-in

They choose the tier on the day on **their** iPhone 15 or newer. A non-Pro phone supports photos/video, not LiDAR. Protocol: `docs/capture-route.md`; copyable manifests: `data/templates/`.
