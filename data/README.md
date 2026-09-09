# Fixtures

Ground-truth jobs for eval. Keep them small and public-safe.

| Dir | Kind | Images? |
| --- | --- | --- |
| `synthetic_two_room/` | Two rectangles + door | No |
| `roomplan_two_room/` | Portable RoomPlan JSON adapter fixture | No |

Add `real_room_01/` only if the capture is OK to live in this private repo. Protocol: `docs/capture-protocol.md`.

Large binaries: GitHub-friendly JPEGs, not 4K masters. Prefer gitignored `data/private/` for Record3D, MOV, and full-res LiDAR.

## Drop-in layout for tomorrow’s capture

Copy one tracked template per tier into `data/private/` (gitignored), replace its
`replace-me` manifest values, then add the capture files:

```bash
cp -R data/templates/photos data/private/benchmark-photos
cp -R data/templates/video data/private/benchmark-video
cp -R data/templates/lidar data/private/benchmark-lidar
```

Do not put all tiers in one job. The combined tree below is an inventory guide,
not a single runnable job.

```text
data/private/benchmark/
  manifest.yaml                 # exact job id, tier, device, app/version
  damage_observations.json      # optional; after staging damage
  photos/
    room_a/  (exactly 8 JPEGs)
    room_b/
    hallway/
  video/
    walkthrough.mp4             # or .mov
    poses.json                  # optional ARKit/Record3D cameras
  lidar/
    roomplan.json               # if an exporter exists
    # else Record3D: metadata.json, depth, .r3d — still a structured fail until T6
  extras/
    tape.jpg                    # photo of laser/tape on a wall
```

Video contract: `docs/formats/video-job.md`. Photo contract: `docs/formats/photo-job.md`; capture instructions remain in `docs/capture-protocol.md` and `docs/capture-route.md`. LiDAR JSON: `docs/formats/roomplan-json.md`.
