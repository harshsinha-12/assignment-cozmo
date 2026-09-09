# Capture route (Route 1) — 10-minute cable install

**Status:** optional. The scored walk-in stays Route 2 (`docs/capture-route.md`)
until this page is timed on **Cozmo's** phone. TestFlight is not used: a paid
Apple Developer Program team is not required and is not enrolled.

The official prompt accepts “a TestFlight build **or** a dev build we can
install on our device in under 10 minutes.” This page is the dev-build path.

| Need | What |
| --- | --- |
| Mac | This repo already cloned; Xcode already installed and signed in |
| Phone | Unlocked iPhone 15+ (Pro for LiDAR). USB-C **data** cable |
| Clock | Starts when the cable is in your hand. Target **&lt; 10:00** |

## Abort and use Route 2 if

- The laptop is not a Mac with Xcode, **or**
- Settings → Privacy & Security → Developer Mode is Off and iOS asks for a
  restart (the restart alone can blow the budget), **or**
- Trust App cannot finish (phone must reach `https://ppq.apple.com`).

A free Personal Team is enough. Do not enroll in the $99 program for this.

## Install

Plug in the phone, tap **Trust** if asked, then:

```bash
./scripts/install-cozmo-capture.sh
```

Using your own Apple ID instead of the repo team:

```bash
DEVELOPMENT_TEAM=YOURTEAMID ./scripts/install-cozmo-capture.sh
```

If iOS blocks the app: Settings → General → VPN & Device Management → Trust
**Apple Development**, then Verify App. Open **Cozmo Capture**. Allow Camera.

The script prints elapsed seconds. If the total is over 10:00, stop and
follow `docs/capture-route.md` instead.

## Capture (after the app is open)

Lights on. Rear camera. No zoom, Portrait, or cinematic mode.

- **LiDAR (Pro):** name the room, Scan, walk the perimeter, Finish. Repeat for
  every room plus the connector. Export capture job.
- **Photos:** 2–8 overlapping stills per named room (doorway, walls, through
  door, ceiling–wall). Finish room, Export photo job.
- **Video:** one walkthrough per named room, chest height, Export video job.

AirDrop the ZIP. On the laptop:

```bash
python -m cozmo_floorplan run ~/Downloads/cozmo-capture-*.zip --out out/route1
```

## Handoff check

- Elapsed install time is written on this page if you timed it.
- ZIP opens; `manifest.yaml` plus the matching `lidar/`, `photos/`, or
  `video/` folder is present.
- Personal-team apps expire after seven days; re-run the script if iOS says
  the developer certificate expired.
