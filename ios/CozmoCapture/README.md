# Cozmo Capture (T21)

Thin iPhone RoomPlan capture/export companion for the local Python pipeline.
It captures one room and shares `roomplan.json` in the portable contract defined
by `docs/formats/roomplan-json.md`.

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

## Hand off the export

After RoomPlan finishes processing, tap **Share roomplan.json** and save it as:

```text
<job>/lidar/roomplan.json
```

Then run the normal repository command against `<job>`. This first stage exports
one room. It does not yet merge several RoomPlan sessions or replace the scored
Route 2 capture protocol.
