# T21h install rehearsal

**Date:** 2026-09-10  
**Path:** cable Personal-Team install (`scripts/install-cozmo-capture.sh`).  
**Not used:** TestFlight / Apple Developer Program ($99).

## What was timed

| Step | Result |
| --- | --- |
| Signed generic iPhoneOS build (`--build-only`) | **46 s** on Harsh's MacBook Air, Xcode 26.6, team `PH4KQ4LY92` |
| Copy onto Harsh's iPhone 17 Pro | **~18 s** (Developer Mode already enabled; app was already installed once as T21g) |
| Open Xcode GUI | `open -a Xcode ios/CozmoCapture/CozmoCapture.xcodeproj` |

Both numbers are well under the 10-minute budget. The script now opens Xcode
after a successful install; `--open-xcode` only opens the project.

## What this does not prove

It does not time Cozmo's phone. Developer Mode on a phone that has never been
used for development can require a restart and should abort to Route 2.
Route 2 (`docs/capture-route.md`) stays the scored capture route until they
run `./scripts/install-cozmo-capture.sh` in the room and it finishes under
10:00.
