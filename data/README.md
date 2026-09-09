# Fixtures

Ground-truth jobs for eval. Keep them small and public-safe.

| Dir | Kind | Images? |
| --- | --- | --- |
| `synthetic_two_room/` | Two rectangles + door | No |
| `roomplan_two_room/` | Portable RoomPlan JSON adapter fixture | No |

Add `real_room_01/` only if the capture is OK to live in this private repo. Protocol: `docs/capture-protocol.md`.

Large binaries: GitHub-friendly JPEGs, not 4K masters. Prefer gitignored `data/private/` for Record3D, MOV, and full-res LiDAR.

## Drop-in layout for tomorrow’s capture

Copy into `data/private/benchmark/` (gitignored). Then point the CLI at that folder.

```text
data/private/benchmark/
  manifest.yaml                 # job_id + tier: lidar | video | photos
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

Video contract: `docs/formats/video-job.md`. Photo folders: `docs/capture-protocol.md` and `docs/capture-route.md`. LiDAR JSON: `docs/formats/roomplan-json.md`.
