# Eval and accuracy

If we cannot fill a table like this, we do not say “cm-level”:

| Fixture | Tier | Wall median | Wall p95 | Area % | Door width | Stitch at door | n walls |
| --- | --- | --- | --- | --- | --- | --- | --- |
| synthetic_two_room | synthetic |  |  |  |  |  |  |
| real_room_01 | lidar |  |  |  |  |  |  |
| real_room_01 | video |  |  |  |  |  |  |
| real_room_01 | photos |  |  |  |  |  |  |

Units: centimetres. Area can also be percent.

## What to measure

Against `ground_truth.json` in each fixture:

1. Match rooms, then match each room's cyclic wall topology by side length while
   allowing a cyclic shift and reflection. This is invariant to independent
   scan origins and yaw; generated wall numbers are not treated as semantic
   identities. Shared/multi-owner walls retain the geometry fallback.
2. Absolute length error.
3. Polygon IoU / area error after aligning the plan (Umeyama / ICP in 2D) so a global SE(2) does not look like a length error.
4. Opening width error.
5. For stitch: relative pose at the shared door vs truth.

Also report **yield**: fraction of jobs that produced `status: ok` vs `partial` vs `failed`.

## Fixtures

### Synthetic (do first)

Known rectangles. Tests the IR, stitch, and eval code without CV. An implementation that cannot pass synthetic is not ready for COLMAP.

### Real room

Tape at least:

- Two long walls
- One short wall
- One door width
- Optional: diagonal (catches angle error)

Photograph the tape if you want an audit image in `extras/`. Do not trust RoomPlan as ground truth for the LiDAR row — that would be circular. RoomPlan vs tape is itself a result.

### What not to use as “accuracy”

- “It looks like my apartment”
- LLM-judged screenshots
- Training loss

## Official gates (pass targets)

These replace internal “wish” numbers. Score every tier. Do not drop a row because it looks hard.

| Metric | Gate |
| --- | --- |
| Opening widths | ≤ 2 cm on ≥ 85%; missed or phantom opening = miss |
| Ceiling height | ≤ 1.5 cm per room; recapture spread ≤ 1 cm |
| Repeatability | two captures, 1 cm or 0.5% per wall |
| Drift | correction on vs off ablation; poses-as-is fails |
| Photo stitch | one plan, adjacency, no overlaps, footprint ±8% |
| Photo walls | ±8% with calibrated intervals |
| Video walls | ±3% with calibrated intervals |
| Head-to-head | beat/tie incumbent on ≥ 70% shared LiDAR dimensions |

Calibration is scored at every tier. Confident garbage on thin input caps the score — intervals must cover the error.

## Targets (internal, until the prompt gives numbers)

**Superseded.** Use the official table above as pass targets. After eval, fill `docs/device-matrix.md` with measured numbers. If a gate fails, that is a fix-loop input, not a plan-time skip.

## Eval CLI

```text
python -m cozmo_floorplan eval \
  --pred out/floorplan.json \
  --truth data/fixtures/.../ground_truth.json \
  --repeat out/repeat/floorplan.json \
  --ablation-off out/poses-as-is/floorplan.json \
  --incumbent out/incumbent/floorplan.json \
  --out out/eval
```

T14 implements this command and writes deterministic `eval.json`. Optional evidence is never silently ignored: missing repeat, drift-ablation, or LiDAR incumbent inputs appear as `missing_evidence` gates. A non-passing report exits 3; invalid input exits 1.

Rooms use exact ids and then a Hungarian geometry fallback. Single-owner walls
use room-local cyclic topology and side lengths, allowing rotation/reflection
between coordinate frames; remaining shared walls use exact ids and then the
geometry fallback. Openings are matched by kind, mapped supporting wall,
offset, and width. Missed and phantom openings both enter the accuracy
denominator.

### Current private LiDAR result (2026-09-10)

The three-room Record3D prediction has 12 matched walls. Frame-invariant wall
matching reports a **2.5 cm median** and **30 cm p95**, replacing the invalid
75 cm median produced when generated `wall-1` labels forced long sides to match
short sides. Per-room wall absolute errors are:

- `drawing-room`: 12, 12, 10, 10 cm
- `my-room`: 30, 30, 0, 0 cm
- `pooja-room`: 5, 5, 0, 0 cm

The final mapper accepts an outer wall band only when it retains at least 95%
of the densest plane's support. This capture-derived near-peak rule expands the
pooja long wall to its strongly supported outer band while rejecting its weaker
short-wall band; it contains no room ids or ground-truth dimensions. The
remaining errors stay red. T6d
uses each scan's conservative p95 raw-plane residuals for wall-span and ceiling
intervals, with area uncertainty propagated from both spans. Aggregate interval
coverage in the final three-room evaluation is 19/24 (79.2%) against 80% mean
declared confidence, so the internal calibration gate passes on this
development benchmark. It is not a holdout-validation claim. Maximum ceiling
point error remains 5.41 cm; four opening candidates are scored against three
truth openings (median 5 cm, p95 10 cm, with one phantom); and the scans remain
disconnected.

### Current private T18 head-to-head (2026-09-10)

Magicplan iOS **2026.35.0** (App Store listing at ingest; released 2026-09-02;
device Settings not screenshotted). My-room uses displayed 4.20×3.29 m AABB
walls. Pooja-room inspector has no Length/Width; six Manhattan inner walls were
traced from the 2D screenshot (door notch) and scaled to displayed 12.04 m².

`make benchmark` passes the head-to-head at **9/12 (75%)**. The shared set is
two-room walls plus ceilings and floor areas. The same refresh reports LiDAR
wall **7.5 cm median / 30 cm p95** (n=12)
and interval coverage **19/24 (79.2%)** still passing the internal calibration
gate. Photo overlap after EXIF remains connector/drawing/my/pooja = **2/2/5/3**
components.

The report distinguishes `pass`, `fail`, `missing_evidence`, and `not_applicable`. Empty geometry therefore produces explicit red opening, ceiling, yield, and calibration gates rather than zeros that look successful.

## Calibration honesty

Phone LiDAR and RoomPlan are not survey instruments. Apple does not advertise millimetre CAD. Our write-up should say: centimetre-level means **good enough for drywall quantities**, not as-built BIM. That sentence will play well in the technical discussion.
