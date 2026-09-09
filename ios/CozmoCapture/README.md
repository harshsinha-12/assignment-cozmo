# Cozmo Capture (T21)

Thin iPhone capture/export companion for the local Python pipeline. The top
segmented control switches **LiDAR**, **Photos**, and **Video**. Each mode
shares one CLI-ready job ZIP (`docs/formats/cozmo-capture-job.md`).

This is an **iPhone app**, not a Mac app. The Simulator can compile and show
the UI, but RoomPlan/LiDAR and a real camera need the iPhone 17 Pro.

Walk-in install (T21h): [`docs/capture-route-route1.md`](../../docs/capture-route-route1.md)
and `./scripts/install-cozmo-capture.sh`. A free Personal Team is enough. Do
not pay for the Apple Developer Program. Route 2 remains the scored protocol
until that cable install is timed on **their** phone.

## Compile on the Mac (no phone)

```bash
export DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer
xcodebuild \
  -project ios/CozmoCapture/CozmoCapture.xcodeproj \
  -scheme CozmoCapture \
  -destination 'generic/platform=iOS Simulator' \
  CODE_SIGNING_ALLOWED=NO build
```

## First flight on your iPhone (about 10 minutes)

Preferred, timed commands (from the repo root):

```bash
./scripts/install-cozmo-capture.sh
open -a Xcode ios/CozmoCapture/CozmoCapture.xcodeproj
```

Print [`docs/capture-route-route1.md`](../../docs/capture-route-route1.md).
Harsh's 2026-09-10 rehearsal: signed iPhoneOS binary **46 s**, device copy
**~18 s** ([`docs/t21h-install-rehearsal.md`](../../docs/t21h-install-rehearsal.md)).
`--open-xcode` only opens the project. Cursor will not. GUI steps below are
the fallback if the script cannot see the phone.

1. Unlock the iPhone, plug it into the Mac with a data cable, and tap **Trust**
   if asked. On the phone, Settings → Privacy & Security → **Developer Mode**
   → On, then restart if iOS asks.
2. From Terminal: `open -a Xcode ios/CozmoCapture/CozmoCapture.xcodeproj`
   (Cursor will not open the project by double-click).
3. Select the **CozmoCapture** target → **Signing & Capabilities**.
   - Check **Automatically manage signing**.
   - Team: your Apple ID (a free Personal Team is enough).
   - Confirm the bundle id stays `dev.harshsinha.assignmentcozmo.CozmoCapture`.
4. In the scheme toolbar, pick your **iPhone 17 Pro** (not a simulator).
5. Press **Run** (⌘R). Allow Camera (and Microphone for video).
6. If iOS blocks the developer: Settings → General → VPN & Device Management
   → **Trust**. The LiDAR tab should say **Ready**, not “RoomPlan unavailable”.
7. Capture:
   - **LiDAR:** name the room, Scan, watch LiDAR frames, Finish, repeat,
     Export capture job.
   - **Photos:** 2–8 overlapping stills per room, Finish room, Export photo job.
   - **Video:** one walkthrough per named room, Export video job.
8. AirDrop the ZIP and run:

```bash
python -m cozmo_floorplan run ~/Downloads/cozmo-capture-*.zip --out out/route1
```

Save Route 1 LiDAR under `data/private/route1-roomplan/` so it does not mix
with Route 2 Record3D captures.

## If iOS will not trust the developer app

The phone must ask Apple whether your personal-team certificate is valid. That
is a network check to `ppq.apple.com`, not an app bug. Tapping your email
address in Settings does **not** complete it.

Do this in order:

1. On the iPhone: Settings → Privacy & Security → **Developer Mode** → On.
   Restart if iOS asks, then unlock the phone.
2. Connect to **cellular data** (turn Wi‑Fi off) or a phone hotspot. Turn off
   VPN, iCloud Private Relay, and any DNS/content-blocker profile.
3. Safari on the phone: open `https://ppq.apple.com`. If it fails, verification
   cannot succeed until that host is reachable.
4. Settings → General → **VPN & Device Management**.
   Under **Developer App**, tap the **Apple Development** row (not the Mail
   app, not Settings → [your name]). Tap **Trust “Apple Development: …”**,
   then **Verify App**. Wait until it says Verified.
5. Return to Xcode and press Run again. Keep the phone unlocked.

If Verify App spins forever, delete **Cozmo Capture** from the home screen,
unplug/replug, and Run from Xcode on cellular. A free Personal Team is enough;
you do not need a paid Apple Developer Program membership for this install.

This app still does not replace the scored Route 2 capture protocol
(`docs/capture-route.md`) until a 10-minute install works on their phone.

## TestFlight is not used

The official prompt allows a TestFlight build **or** a cable dev build in
under 10 minutes. This submission uses the cable path so nobody pays $99.
A Personal Team cannot upload to App Store Connect anyway.

Print [`docs/capture-route-route1.md`](../../docs/capture-route-route1.md) for
the walk-in. If that install misses 10:00 or the defense laptop is not a Mac
with Xcode, follow [`docs/capture-route.md`](../../docs/capture-route.md).
