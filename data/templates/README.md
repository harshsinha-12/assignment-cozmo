# Capture job templates

Copy exactly one template into the gitignored benchmark area, then replace every
`replace-me` value before capture:

```bash
cp -R data/templates/photos data/private/benchmark-photos
cp -R data/templates/video data/private/benchmark-video
cp -R data/templates/lidar data/private/benchmark-lidar
```

Keep the three tiers in separate job directories. The empty input directories
are intentional; add the original capture files without committing private
media. The LiDAR template is runnable only with one of the RoomPlan JSON names
listed in `docs/formats/roomplan-json.md`. Preserve raw Record3D exports too, but
the raw adapter remains blocked until it is tested against a real export.
