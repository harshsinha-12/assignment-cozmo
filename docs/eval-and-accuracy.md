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

1. **Hungarian match** walls by midpoint + direction (or by id if synthetic).
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

## Targets (internal, until the prompt gives numbers)

These are goals for us, not claims on the README:

- LiDAR vs tape: median wall error **≤ 3 cm** on a simple rectangular room if the scan is complete
- Video with metric poses: **≤ 5–8 cm** median on the same room
- Photos with a measured door prior: **≤ 10–15 cm** median, p95 can be worse
- Photos with no prior: no metric target; only shape IoU after scale-normalized alignment

If reality is worse, publish the number. Cozmo ships to operators; they already know rooms are messy.

## Eval CLI (planned)

```text
python -m cozmo_floorplan eval --pred out/floorplan.json --truth data/fixtures/.../ground_truth.json
```

Writes `eval.json`. `make test` runs this on synthetic data.

## Calibration honesty

Phone LiDAR and RoomPlan are not survey instruments. Apple does not advertise millimetre CAD. Our write-up should say: centimetre-level means **good enough for drywall quantities**, not as-built BIM. That sentence will play well in the technical discussion.
