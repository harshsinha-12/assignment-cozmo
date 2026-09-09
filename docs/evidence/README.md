# Evidence for the README

Phone UI plus CLI output so a reviewer can see Route 1, Route 2, and the
synthetic fixture without opening `out/`.

## Cozmo Capture (Route 1)

Downsampled JPEGs. Full-res `IMG_*.PNG` stay on disk and are gitignored.

| File | What it shows |
| --- | --- |
| `app-lidar-scanning.jpg` | Live RoomPlan edges, LiDAR frames incrementing |
| `app-lidar-room.jpg` | On-device room mesh after the scan (IMG_0151) |
| `app-photos.jpg` | Photos tab, 2–8 overlapping stills |
| `app-video.jpg` | Video tab, one walkthrough per named room |
| `app-lidar-preview.jpg` | 1 room scanned, 68 frames, Scan Room 2 |
| `app-export-ready.jpg` | Share capture job ZIP for the CLI |
| `lidar/roomplan.json` | On-device RoomPlan export that the ZIP carries |
| `route1-cozmo-capture.svg` | CLI FloorPlan from that ZIP |
| `route1-cozmo-capture.json` | Compact status snippet |

`lidar/room-1.r3d` is local-only (34 MB). Same capture as
`cozmo-capture/cozmo-capture-20260909-190805/`.

## Route 2 and fixture

| File | What it shows |
| --- | --- |
| `route2-record3d.svg` / `.json` | Record3D three-room LiDAR FloorPlan |
| `synthetic-two-room.svg` / `.json` | `make reproduce-synthetic` (`status: ok`) |
