# Cozmo Capture (T21)

Thin iPhone RoomPlan capture/export companion for the local Python pipeline.
Name each room, scan several rooms, then share one job ZIP. Two or more rooms
are merged with Apple `StructureBuilder`. During each scan the app also samples
ARKit RGB, LiDAR depth, confidence, poses, and intrinsics into
Record3D-compatible `.r3d` files (`docs/formats/record3d.md`). The ZIP matches
the CLI lidar job layout (`docs/formats/cozmo-capture-job.md`).

## Build

```bash
xcodebuild \
  -project ios/CozmoCapture/CozmoCapture.xcodeproj \
  -scheme CozmoCapture \
  -destination 'generic/platform=iOS Simulator' \
  CODE_SIGNING_ALLOWED=NO build
```

The simulator build verifies compilation only. RoomPlan capture and LiDAR
logging require a LiDAR-equipped iPhone. To install, open the project in Xcode,
select a personal development team under Signing & Capabilities, connect the
phone, and Run.

## Capture several rooms

1. Enter a room name (defaults are `Room 1`, `Room 2`, …).
2. Tap **Scan**, start at the doorway, and slowly show every wall and opening.
3. Watch **LiDAR frames** increment. If it stays at 0, the device is not
   exposing `sceneDepth`; RoomPlan JSON is still exported.
4. Tap **Finish scan** and wait for RoomPlan to process.
5. Repeat for each additional room, walking through the connecting doorway.
6. Tap **Export capture job**. If merge fails, retry from the doorway or use
   **Export without merging**.
7. Share the ZIP, unzip it, and run the normal repository command against the
   unpacked folder. Expected members:

```text
<job>/manifest.yaml
<job>/lidar/roomplan.json
<job>/lidar/<room>.r3d
```

This stage does not replace the scored Route 2 capture protocol.
