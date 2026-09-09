# Cozmo Capture (T21)

Thin iPhone RoomPlan capture/export companion for the local Python pipeline.
Name each room, scan several rooms, then share one job ZIP. Two or more rooms
are merged with Apple `StructureBuilder`. During each scan the app also samples
ARKit RGB, LiDAR depth, confidence, poses, and intrinsics into
Record3D-compatible `.r3d` files (`docs/formats/record3d.md`). The ZIP matches
the CLI lidar job layout (`docs/formats/cozmo-capture-job.md`).

This is an **iPhone app**, not a Mac app. macOS is only the Xcode build host.
The iOS Simulator can compile and launch the UI, but RoomPlan and LiDAR are
unavailable there — first flight has to be a LiDAR iPhone (iPhone 17 Pro).

## Compile on the Mac (no phone)

```bash
export DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer
xcodebuild \
  -project ios/CozmoCapture/CozmoCapture.xcodeproj \
  -scheme CozmoCapture \
  -destination 'generic/platform=iOS Simulator' \
  CODE_SIGNING_ALLOWED=NO build
```

That only proves the project builds. It does not capture rooms.

## First flight on your iPhone (about 10 minutes)

1. Unlock the iPhone, plug it into the Mac with a data cable, and tap **Trust**
   if asked. On the phone, Settings → Privacy & Security → **Developer Mode**
   → On, then restart if iOS asks.
2. Open `ios/CozmoCapture/CozmoCapture.xcodeproj` in Xcode.
3. Select the **CozmoCapture** target → **Signing & Capabilities**.
   - Check **Automatically manage signing**.
   - Team: your Apple ID (a free Personal Team is enough). Xcode may prompt
     to add the account under Xcode → Settings → Accounts.
   - Confirm the bundle id stays `dev.harshsinha.assignmentcozmo.CozmoCapture`.
4. In the scheme toolbar, pick your **iPhone 17 Pro** (not a simulator).
5. Press **Run** (⌘R). The first install can take a few minutes while Xcode
   registers the device.
6. If the phone says the developer is untrusted: Settings → General → VPN &
   Device Management → your Apple ID → **Trust**. Then open **Cozmo Capture**.
7. Allow **Camera** when prompted. The screen should say **Ready**, not
   “RoomPlan unavailable”.
8. First scan:
   - Name the room (or keep `Room 1`).
   - Tap **Scan**, start at the doorway, slowly show every wall and opening.
   - Watch **LiDAR frames** increment. If it stays at 0, RoomPlan JSON still
     exports; note that in the share.
   - Tap **Finish scan**, wait for processing.
   - Repeat for a second room, walking through the connecting doorway.
   - Tap **Export capture job**, then **Share capture job ZIP** (AirDrop to
     the Mac, or Files).
9. On the Mac, run the ZIP through the CLI (unzipping is optional):

```bash
python -m cozmo_floorplan run ~/Downloads/cozmo-capture-*.zip --out out/route1
```

Save a copy under `data/private/route1-roomplan/` for the benchmark. This app
does not replace the scored Route 2 capture protocol.
