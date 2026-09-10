#!/usr/bin/env bash
# Install Cozmo Capture on a connected iPhone with a free Personal Team.
# Official T21h path: a cable "dev build" in under 10 minutes. No TestFlight.
set -euo pipefail

usage() {
  cat <<'EOF'
Install Cozmo Capture on a plugged-in iPhone (free Personal Team, no $99 fee).

Usage:
  ./scripts/install-cozmo-capture.sh
  DEVELOPMENT_TEAM=YOURTEAMID ./scripts/install-cozmo-capture.sh

Options:
  --help        Show this help
  --dry-run     Print destinations and commands; do not build or install
  --build-only  Signed generic iPhoneOS build only (no device install)
  --open-xcode  Open the project in Xcode.app (Cursor will not)

The 10-minute clock starts when this script starts. A Developer Mode restart,
missing Xcode, or an unreachable phone is an abort to Route 2
(docs/capture-route.md). After a successful install the script also opens
Xcode; pass --no-open to skip that.
EOF
}

MODE=install
OPEN_XCODE=1
for arg in "$@"; do
  case "$arg" in
    --help|-h)
      usage
      exit 0
      ;;
    --dry-run)
      MODE=dry-run
      ;;
    --build-only)
      MODE=build-only
      ;;
    --open-xcode)
      MODE=open-xcode
      ;;
    --no-open)
      OPEN_XCODE=0
      ;;
    *)
      echo "unknown argument: $arg" >&2
      usage >&2
      exit 2
      ;;
  esac
done

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
ROOT=$(cd "$SCRIPT_DIR/.." && pwd)
PROJECT="$ROOT/ios/CozmoCapture/CozmoCapture.xcodeproj"
SCHEME=CozmoCapture
TEAM="${DEVELOPMENT_TEAM:-PH4KQ4LY92}"
DERIVED="${COZMO_CAPTURE_DERIVED:-$ROOT/out/cozmo-capture-derived}"
APP="$DERIVED/Build/Products/Debug-iphoneos/CozmoCapture.app"
START_EPOCH=$(date +%s)

elapsed() {
  echo $(( $(date +%s) - START_EPOCH ))
}

fail() {
  echo "install-cozmo-capture: $* ($(elapsed)s elapsed)" >&2
  echo "Abort to Route 2: docs/capture-route.md" >&2
  exit 1
}

open_xcode() {
  if ! command -v open >/dev/null 2>&1; then
    echo "open -a Xcode is unavailable on this machine"
    return 1
  fi
  echo "Opening Xcode: $PROJECT"
  open -a Xcode "$PROJECT"
}

if [[ ! -f "$PROJECT/project.pbxproj" ]]; then
  fail "missing Xcode project at $PROJECT"
fi

if [[ "$MODE" == "open-xcode" ]]; then
  open_xcode || fail "could not open Xcode.app"
  echo "elapsed_s=$(elapsed)"
  exit 0
fi

if [[ "$MODE" == "dry-run" ]]; then
  echo "Cozmo Capture cable install"
  echo "  team: $TEAM"
  echo "  mode: $MODE"
  echo "  phone: not queried during dry-run"
  if ! command -v xcodebuild >/dev/null 2>&1; then
    echo "dry-run: xcodebuild not on PATH (ok)"
  fi
  echo "project: $PROJECT"
  echo "would build: xcodebuild -project ios/CozmoCapture/CozmoCapture.xcodeproj -scheme $SCHEME -destination 'generic/platform=iOS' -derivedDataPath out/cozmo-capture-derived -allowProvisioningUpdates DEVELOPMENT_TEAM=$TEAM build"
  echo "would install: xcrun devicectl device install app --device DEVICE_ID $APP"
  echo "would open: open -a Xcode ios/CozmoCapture/CozmoCapture.xcodeproj"
  echo "elapsed_s=$(elapsed)"
  exit 0
fi

if ! command -v xcodebuild >/dev/null 2>&1; then
  fail "xcodebuild not found; install Xcode.app"
fi

export DEVELOPER_DIR="${DEVELOPER_DIR:-/Applications/Xcode.app/Contents/Developer}"
if [[ ! -d "$DEVELOPER_DIR" ]]; then
  fail "Xcode.app not found at $DEVELOPER_DIR"
fi

pick_device() {
  python3 - "$1" <<'PY'
import json, sys

payload = json.loads(open(sys.argv[1], encoding="utf-8").read())
devices = payload.get("result", {}).get("devices", [])
iphones = []
for device in devices:
    hardware = device.get("hardwareProperties") or {}
    if hardware.get("deviceType") != "iPhone":
        continue
    if hardware.get("reality") not in (None, "physical"):
        continue
    connection = device.get("connectionProperties") or {}
    props = device.get("deviceProperties") or {}
    iphones.append(
        {
            "name": props.get("name") or "iPhone",
            "udid": hardware.get("udid") or "",
            "identifier": device.get("identifier") or "",
            "developer_mode": props.get("developerModeStatus") or "unknown",
            "tunnel": connection.get("tunnelState") or "unknown",
            "pairing": connection.get("pairingState") or "unknown",
        }
    )

reachable_states = {"connected", "available"}
reachable = [
    device
    for device in iphones
    if device["udid"] and device["tunnel"] in reachable_states
]
chosen = (reachable or iphones)[0] if (reachable or iphones) else None
print(json.dumps({"iphones": iphones, "chosen": chosen, "reachable": bool(reachable)}))
PY
}

DEVICES_JSON=$(mktemp -t cozmo-iphones)
trap 'rm -f "$DEVICES_JSON"' EXIT
xcrun devicectl list devices --json-output "$DEVICES_JSON" >/dev/null
SELECTION=$(pick_device "$DEVICES_JSON")
CHOSEN_UDID=$(python3 -c 'import json,sys; d=json.loads(sys.argv[1]); c=d.get("chosen") or {}; print(c.get("udid") or "")' "$SELECTION")
CHOSEN_ID=$(python3 -c 'import json,sys; d=json.loads(sys.argv[1]); c=d.get("chosen") or {}; print(c.get("identifier") or "")' "$SELECTION")
CHOSEN_NAME=$(python3 -c 'import json,sys; d=json.loads(sys.argv[1]); c=d.get("chosen") or {}; print(c.get("name") or "")' "$SELECTION")
DEV_MODE=$(python3 -c 'import json,sys; d=json.loads(sys.argv[1]); c=d.get("chosen") or {}; print(c.get("developer_mode") or "unknown")' "$SELECTION")
TUNNEL=$(python3 -c 'import json,sys; d=json.loads(sys.argv[1]); c=d.get("chosen") or {}; print(c.get("tunnel") or "unknown")' "$SELECTION")
REACHABLE=$(python3 -c 'import json,sys; print("yes" if json.loads(sys.argv[1]).get("reachable") else "no")' "$SELECTION")

echo "Cozmo Capture cable install"
echo "  team: $TEAM"
echo "  mode: $MODE"
if [[ -n "$CHOSEN_NAME" ]]; then
  echo "  phone: $CHOSEN_NAME"
  echo "  udid: $CHOSEN_UDID"
  echo "  developer mode: $DEV_MODE"
  echo "  tunnel: $TUNNEL"
  echo "  reachable: $REACHABLE"
else
  echo "  phone: none paired"
fi

if [[ "$DEV_MODE" == "disabled" ]]; then
  fail "Developer Mode is off; enabling it requires a restart. Use Route 2"
fi

xcode_build() {
  local destination="$1"
  xcodebuild \
    -project "$PROJECT" \
    -scheme "$SCHEME" \
    -configuration Debug \
    -destination "$destination" \
    -derivedDataPath "$DERIVED" \
    -allowProvisioningUpdates \
    DEVELOPMENT_TEAM="$TEAM" \
    CODE_SIGN_STYLE=Automatic \
    build
}

if [[ "$MODE" == "build-only" ]]; then
  echo "Building signed generic iPhoneOS binary…"
  xcode_build "generic/platform=iOS"
  echo "elapsed_s=$(elapsed)"
  echo "app: $APP"
  exit 0
fi

if [[ "$REACHABLE" != "yes" || -z "$CHOSEN_ID" ]]; then
  fail "no reachable iPhone. Unlock it, use a data cable, tap Trust, then retry"
fi

echo "Building for the connected iPhone…"
if ! xcode_build "id=$CHOSEN_UDID"; then
  echo "Direct-device destination failed; building generic iPhoneOS then installing…"
  xcode_build "generic/platform=iOS"
fi

if [[ ! -d "$APP" ]]; then
  fail "build succeeded but $APP is missing"
fi

echo "Installing onto the phone…"
xcrun devicectl device install app --device "$CHOSEN_ID" "$APP"

echo "elapsed_s=$(elapsed)"
if [[ "$OPEN_XCODE" == "1" ]]; then
  open_xcode || true
else
  echo "GUI fallback: open -a Xcode ios/CozmoCapture/CozmoCapture.xcodeproj"
fi
echo "Open Cozmo Capture on the phone. If iOS blocks it: Settings → General → VPN & Device Management → Trust Apple Development."
echo "Route 2 remains the scored walk-in until this install is timed on Cozmo's phone."
