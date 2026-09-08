# Device matrix

Fill with real hardware after capture. Claims without eval numbers stay as “target, not measured.”

| Device | LiDAR hardware | Photos tier | Video tier | LiDAR tier | Notes |
| --- | --- | --- | --- | --- | --- |
| iPhone 15 / 16 (non-Pro) | no | yes | yes | no | Walk-in photos/video possible |
| iPhone 15 Pro / 16 Pro / 17 Pro / Pro Max | yes | yes | yes | yes | Harsh’s capture phone: **iPhone 17 Pro** (TOF LiDAR). Required for LiDAR gates |
| iPad Pro with LiDAR | yes | possible | possible | yes | Not the walk-in device they named |
| Android | varies | not claimed | not claimed | not claimed | Out of walk-in scope |

## Accuracy we will claim (after eval)

Replace the TBD cells. Intervals are part of the score; do not tighten them to look good.

| Tier | Wall length | Openings | Ceiling | Stitched footprint | Scale source |
| --- | --- | --- | --- | --- | --- |
| LiDAR | TBD cm (target: tight, openings ≤ 2 cm on ≥ 85%) | TBD | TBD (gate 1.5 cm) | TBD | depth + metric poses |
| Video | TBD (gate ±3% with calibrated interval) | TBD | TBD | TBD | VO / poses if present, else prior |
| Photos | TBD (gate ±8% with calibrated intervals) | TBD (chase ≤2 cm; miss/phantom scored) | TBD | ±8% footprint | door-in-frame + VP; CIs must cover error |

## Walk-in

They choose the tier on the day on **their** iPhone 15 or newer. Non-Pro ⇒ photos or video only. Protocol: `docs/capture-route.md`.
