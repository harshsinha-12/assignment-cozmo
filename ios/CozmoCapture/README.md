# Cozmo Capture (T21)

Thin iPhone RoomPlan capture/export companion for the local Python pipeline.
Name each room, scan several rooms, then share one `roomplan.json` in the
portable contract defined by `docs/formats/roomplan-json.md`. Two or more rooms
are merged with Apple `StructureBuilder` so the `rooms[]` array shares one
metric frame.

## Build

```bash
xcodebuild \
  -project ios/CozmoCapture/CozmoCapture.xcodeproj \
  -scheme CozmoCapture \
  -sdk iphonesimulator \
  -destination 'generic/platform=iOS Simulator' \
  CODE_SIGNING_ALLOWED=NO build
```

The simulator build verifies compilation only. RoomPlan capture requires a
LiDAR-equipped iPhone. To install, open the project in Xcode, select a personal
development team under Signing & Capabilities, connect the phone, and Run.

## Capture several rooms

1. Enter a room name (defaults are `Room 1`, `Room 2`, …).
2. Tap **Scan**, start at the doorway, and slowly show every wall and opening.
3. Tap **Finish scan** and wait for RoomPlan to process.
4. Repeat for each additional room, walking through the connecting doorway.
5. Tap **Export roomplan.json**. If merge fails, retry from the doorway or use
   **Export without merging**.
6. Share the file and save it as:

```text
<job>/lidar/roomplan.json
```

Then run the normal repository command against `<job>`. This stage exports one
or more named rooms. It does not yet log raw ARKit RGB-D frames or replace the
scored Route 2 capture protocol.
