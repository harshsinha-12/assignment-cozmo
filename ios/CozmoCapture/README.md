# Cozmo Capture (T21)

Thin iPhone capture/export companion for the local Python pipeline. The top
segmented control switches **LiDAR**, **Photos**, and **Video**. Each mode
shares one CLI-ready job ZIP (`docs/formats/cozmo-capture-job.md`).

This is an **iPhone app**, not a Mac app. The Simulator can compile and show
the UI, but RoomPlan/LiDAR and a real camera need the iPhone 17 Pro.

Route 2 (Camera + Record3D) remains the scored walk-in protocol until a
signed install on their phone is under 10 minutes.

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

## TestFlight (other people's phones)

A **free Personal Team** (`PH4KQ4LY92` in this project) can install on Harsh's
iPhone via Xcode. It **cannot** upload to App Store Connect or TestFlight.

1. Enroll in the [Apple Developer Program](https://developer.apple.com/programs/)
   ($99/year) with the same Apple ID. Identity review often takes 24–48 hours.
2. In Xcode → CozmoCapture target → **Signing & Capabilities**, switch **Team**
   from the Personal Team to the paid team. Leave the bundle id
   `dev.harshsinha.assignmentcozmo.CozmoCapture`.
3. At [App Store Connect](https://appstoreconnect.apple.com) → **Apps** → **+**
   → New App: iOS, name `Cozmo Capture`, bundle id as above, SKU any unique
   string (for example `cozmo-capture-t21`).
4. In Xcode, pick destination **Any iOS Device (arm64)** (not a simulator).
   **Product → Archive**. When Organizer opens: **Distribute App** →
   **App Store Connect** → **Upload**.
5. Wait until the build is **Ready to Test** (often 10–30 minutes) under
   TestFlight. Bump `CURRENT_PROJECT_VERSION` (the build number) for every
   new upload; Apple rejects duplicate build numbers.
6. **Cozmo / anyone not on your Apple team** needs **External Testing**, not
   Internal. Create an External group, add their emails or a public link, and
   submit the first build for **Beta App Review**. After that approval, new
   builds in the same group usually skip review.
7. Testers install Apple's **TestFlight** app, redeem the invite, and install
   Cozmo Capture. LiDAR still needs an iPhone Pro.

Do not use TestFlight as the scored walk-in path until that install is
rehearsed in under 10 minutes on **their** phone. The official prompt also
accepts a cable Xcode install; Route 2 (Camera + Record3D) stays the fallback.
