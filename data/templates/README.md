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
media. RoomPlan JSON produces geometry using one of the names in
`docs/formats/roomplan-json.md`. Original `.r3d` archives are decoded and
validated as described in `docs/formats/record3d.md`; plane extraction remains
pending, so raw Record3D does not yet produce a FloorPlan.
