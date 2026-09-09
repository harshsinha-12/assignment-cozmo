# Harsh's final capture and upload checklist

Use the same room names everywhere:

- `drawing-room`
- `my-room`
- `pooja-room`
- `connector` — the real doorway, lobby, landing, or transition between rooms;
  it does not need to be a hallway.

Use `my-room` as both the staged-damage room and repeat-capture room. Keep
furniture and staged damage unchanged across all tiers. Transfer originals by
AirDrop, USB/Image Capture, iCloud Drive, or Files—not WhatsApp.

## 1. Photo capture

Settings: rear 1x camera, landscape, ordinary Photo mode, Most Compatible
(JPEG), lights on, no Portrait/Live/filters/digital zoom.

Put exactly eight original JPEGs in each primary folder:

```text
data/private/benchmark-photos/photos/
  drawing-room/
  my-room/
  pooja-room/
  connector/
```

Use these filenames in every room folder:

```text
01-doorway.jpg
02-wall-a.jpg
03-wall-b.jpg
04-wall-c.jpg
05-wall-d.jpg
06-through-door.jpg
07-ceiling-wall.jpg
08-overlap-or-damage.jpg
```

Photo sequence: full doorway; four clockwise walls with both corners visible;
through-door view; ceiling-wall junction; overlapping corner view. Each image
must overlap the previous and next one. For `connector`, photograph both sides
of the doorway, threshold, side edges, and wide views tying the rooms together.

Repeat `my-room` independently with another eight JPEGs in:

```text
data/private/benchmark-photos-repeat/photos/my-room/
```

After copying the repeat photos, rename
`data/private/benchmark-photos-repeat/manifest.TEMPLATE.yaml` to
`manifest.yaml`.

## 2. Video capture

Use the Camera app, rear 1x lens, landscape, ordinary Video mode, 1080p/30 fps,
chest height, lights on. Record one continuous 60–180 second walkthrough:

1. Begin at the drawing-room entrance and show the complete doorway.
2. Walk its perimeter slowly and pause two seconds at every corner.
3. Show floor and ceiling briefly.
4. Cross the real connector without stopping.
5. Cover `my-room`, including a wide view of both staged damage regions.
6. Continue to `pooja-room`, cover its walls, and finish at its doorway.

Save the untouched original as:

```text
data/private/benchmark-video/video/whole-property.mov
```

Make a separate independent repeat video of `my-room` and save it as:

```text
data/private/benchmark-video-repeat/video/my-room-repeat.mov
```

Then rename `benchmark-video-repeat/manifest.TEMPLATE.yaml` to `manifest.yaml`.
A Camera MOV does not contain the calibrated ARKit pose sidecar; do not invent
or manually create one.

## 3. Route 2 LiDAR capture (Record3D)

Keep the existing three `.r3d` room scans. In Record3D, record one continuous
scan that crosses a real doorway, covers all walls, floor, ceiling, openings,
and connector. Export **Shareable/Internal format (.r3d)** with depth, poses,
and intrinsics intact. Save it as:

```text
data/private/benchmark-lidar/lidar/property-connector.r3d
```

Create a completely new Record3D session for the repeat room and save it as:

```text
data/private/benchmark-lidar-repeat/lidar/my-room-repeat.r3d
```

Then rename `benchmark-lidar-repeat/manifest.TEMPLATE.yaml` to `manifest.yaml`
and replace the Record3D version placeholder.

## 4. Route 1 Xcode/RoomPlan JSON

Do not mix Route 1 output with the Record3D Route 2 job. Follow
`ios/CozmoCapture/README.md` to install on the iPhone. After you AirDrop the
job ZIP, either save it here unpacked or run the ZIP directly:

```text
data/private/route1-roomplan/manifest.yaml
data/private/route1-roomplan/lidar/roomplan.json
data/private/route1-roomplan/lidar/<room>.r3d
```

```bash
python -m cozmo_floorplan run ~/Downloads/cozmo-capture-*.zip --out out/route1
```

## 5. Safe staged damage

Tape two removable mock regions to one wall in `my-room`; do not damage or wet
the real wall:

- Water stain: irregular brown/yellow mark on paper, roughly 20–40 cm.
- Puncture/tear: torn cardboard, roughly 10–25 cm.

Keep both in place during photos, video, and LiDAR. Add these evidence photos:

```text
data/private/benchmark-photos/evidence/damage/
  my-room-crack-wide.JPG
  my-room-impact-damage-close.JPG
  drawing-room-impact-damage-close.JPG
  measurements.txt
```

The current images are classified as a `crack` plus `impact_damage`; no water
stain is claimed. Fill the blank width, height, and surface fields in the
supplied `measurements.txt`. After upload, the agent will create the validated
job-root `damage_observations.json`; you do not need to write that JSON.

## 6. Tape/laser ground truth

From each doorway, label walls clockwise as `wall-a`, `wall-b`, `wall-c`, and
`wall-d`. Measure in centimetres:

- Every wall
- Every door width and height
- Every window width and height
- Ceiling height
- One floor diagonal per room
- Both staged-damage widths and heights

Fill:

```text
data/private/benchmark-ground-truth/measurements.txt
```

Put photographs showing tape/laser readings in:

```text
data/private/benchmark-ground-truth/photos/
```

Do not manually create `ground_truth.json`. After the notes and evidence arrive,
the agent will create and validate it at:

```text
data/private/ground_truth.json
```

## 7. magicplan comparison

Use magicplan on the same two rooms: `drawing-room` and `my-room`. Record the
exact app version and phone model. Export whatever the free tier permits:

- Dimensioned floor-plan PDF
- CSV/statistics export
- PNG/SVG plan
- Measurement screenshots
- Share link

Put the raw files here, replacing `magicplan-version-here` with the real version:

```text
data/private/benchmark-incumbent/raw/magicplan-version-here/
  exports/
  screenshots/
  notes.txt
```

Do not purchase an export solely for this task. Screenshots showing every wall
measurement plus the version/share link are an acceptable raw fallback. After
upload, the agent will normalize the shared dimensions into:

```text
data/private/benchmark-incumbent/floorplan.json
```

That normalized JSON—not the PDF—is what `make benchmark` evaluates.

## 8. Final confirmation

- [ ] Four primary photo folders, exactly eight original JPEGs each
- [ ] Independent eight-photo `my-room` repeat
- [ ] Continuous whole-property 1080p/30 video
- [ ] Independent `my-room` repeat video
- [ ] Existing three room `.r3d` files preserved
- [ ] Continuous Record3D connector scan
- [ ] Independent `my-room` repeat `.r3d`
- [ ] Two damage classes (`crack` and `impact_damage`) with filled measurements
- [ ] All wall/opening/ceiling/diagonal measurements and evidence photographs
- [ ] magicplan raw output for `drawing-room` and `my-room`, including version
- [ ] Originals transferred without WhatsApp compression
- [ ] Repeat template manifests renamed only after their media is present

When complete, run `make benchmark` or tell the agent that the upload is ready.
