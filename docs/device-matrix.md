# Device matrix

Hardware eligibility and runtime support are different claims. “Capture” means the protocol can collect the evidence. Measurements below are from private benchmark `harsh-home-01` on Harsh's **iPhone 17 Pro**, 2026-09-10 (`make benchmark`). They are not a device-wide guarantee.

| Device | Photos | Video | LiDAR | Accepted input |
| --- | --- | --- | --- | --- |
| iPhone 15 / 16 (non-Pro) | yes | yes | no | JPEG; MOV/MP4 |
| iPhone Pro / Pro Max | yes | yes | yes | JPEG; MOV/MP4; Record3D `.r3d`; RoomPlan JSON; semantic USD/USDA/USDZ; Cozmo Capture ZIP |
| Harsh's iPhone 17 Pro | yes | yes | yes | Same; Cozmo Capture installed (cable ~18 s) |
| LiDAR iPad Pro | possible, out of walk-in scope | possible, out of walk-in scope | possible | RoomPlan JSON |
| Android | — | — | — | out of scope |

## Measured intervals (harsh-home-01)

| Tier | Wall length | Openings | Ceiling | Stitch / footprint | Scale source | Intervals |
| --- | --- | --- | --- | --- | --- | --- |
| LiDAR | 7.5 cm median / 30 cm p95, n=12 | 3 matched of 3 truth, 4 predictions; median 5 cm, p95 10 cm | max 5.41 cm, n=3 | rooms not registered (no connector scan); area median rel. error 6.6% | Record3D depth + intrinsics + metric poses | 19/24 covered (79.2%) at 80% declared confidence |
| Video | 8 matched walls; 356 cm median / 783 cm p95 (gate ±3%) | 0 predictions vs 3 truth | 2/3 rooms; ceiling max error 30.3 cm | native rooms independently placed; area median rel. error 322.6% | 1.45 m handheld height after floor band (`known_length`); 4/4 clips scaled | 4/12 covered (33.3%) at 55% declared confidence |
| Photos | 0 reconstructed walls vs tape (gate ±8%) | 0 vs tape | 0 rooms vs tape | overlap graphs 2/2/5/3 components; footprint rel. error 1.0 | unscaled until a connected graph + known length | 0 measurements in eval |

LiDAR room extents vs tape:

| Room | Predicted | Tape | Δ L / Δ W |
| --- | --- | --- | --- |
| drawing-room | 380 × 315 cm | 368 × 305 cm | +12 / +10 cm |
| my-room | 370 × 325 cm | 400 × 325 cm | −30 / 0 cm |
| pooja-room | 370 × 295 cm | 370 × 290 cm | 0 / +5 cm |

Remaining centimetre error is mostly capture quality: fast handheld motion, vibrating video, and thin LiDAR coverage — not a missing pipeline. An experienced operator or a professional camera would get a tighter result from the same software.

Head-to-head (LiDAR vs Magicplan **2026.35.0**, two rooms): **9/12 (75%)** shared dimensions, passing the official ≥70% row.

LiDAR repeat is not in the bundle (repeatability `missing_evidence` on that tier). Photo and video repeats exist; they currently match 0 walls because the primary jobs have not emitted walls.

## Walk-in

They choose the tier on the day on **their** iPhone 15 or newer. Non-Pro: photos and video. Pro: all three. Scored protocol: `docs/capture-route.md`. Optional Route 1 cable install: `docs/capture-route-route1.md`.

Independent rehearsal evidence: `mummy-room` semantic USD on an iPhone Pro
(exact model unrecorded) ran in 0.106 seconds and emitted geometry. It is format
compatibility evidence, not device-wide accuracy: wall 16.1 cm on one match,
door 4.17 cm, ceiling 7 cm, and area 48.2% errors all miss their gates.
