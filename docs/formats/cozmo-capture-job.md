# Cozmo Capture job ZIP

The optional Route 1 iOS app exports one shareable ZIP that unpacks into the
same job-folder contract as `data/templates/lidar/`.

## Layout

```text
cozmo-capture-YYYYMMDD-HHmmss.zip
  cozmo-capture-YYYYMMDD-HHmmss/
    manifest.yaml
    lidar/
      roomplan.json
      <room>.r3d
```

`job_id` matches the folder name. `tier` is `lidar`. `capture_tool` is
`Cozmo Capture 0.1.0`. `capture_format` is `roomplan-json-v1+record3d-r3d`.
RoomPlan JSON is the wall source; `.r3d` files are raw ARKit RGB-D and are
omitted when a room recorded no depth frames.

Unzip, then run the normal CLI against the folder. Incomplete archives
(missing `manifest.yaml`, missing `lidar/roomplan.json`, empty `rooms[]`)
are rejected by `cozmo_floorplan.io.capture_package`.

This does not replace the scored Route 2 capture protocol.
