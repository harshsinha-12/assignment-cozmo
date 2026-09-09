# Cozmo Capture job ZIP

The optional Route 1 iOS app exports one shareable ZIP per capture tier. Each
unpacks into the same job-folder contract as `data/templates/<tier>/`.

## LiDAR

```text
cozmo-capture-YYYYMMDD-HHmmss.zip
  cozmo-capture-YYYYMMDD-HHmmss/
    manifest.yaml          # tier: lidar
    lidar/
      roomplan.json
      <room>.r3d
```

RoomPlan JSON is the wall source; `.r3d` files are raw ARKit RGB-D and are
omitted when a room recorded no depth frames.

## Photos

```text
    manifest.yaml          # tier: photos
    photos/
      <room>/
        01.jpg
        02.jpg
```

Each room folder must contain 2–8 JPEG stills.

## Video

```text
    manifest.yaml          # tier: video
    video/
      <room>.mp4
```

One walkthrough per named room. Metric centimetres still need a calibrated
pose sidecar (`docs/formats/video-job.md`).

Pass the ZIP to the CLI:

```bash
python -m cozmo_floorplan run cozmo-capture-YYYYMMDD-HHmmss.zip --out out/route1
```

Incomplete archives (wrong/missing `manifest.yaml`, missing tier files, empty
RoomPlan `rooms[]`, or photo counts outside 2–8) are rejected before
reconstruction.

This does not replace the scored Route 2 capture protocol.
