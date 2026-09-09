# Capture job templates

Copy exactly one template into the gitignored benchmark area, then replace every
`replace-me` value before capture:

```bash
cp -R data/templates/photos data/private/benchmark-photos
cp -R data/templates/video data/private/benchmark-video
cp -R data/templates/lidar data/private/benchmark-lidar
cp -R data/templates/photos-repeat data/private/benchmark-photos-repeat
cp data/templates/benchmark.yaml data/private/benchmark.yaml
```

Keep the three tiers in separate job directories. The empty input directories
are intentional; add the original capture files without committing private
media. RoomPlan JSON produces geometry using one of the names in
`docs/formats/roomplan-json.md`. Original `.r3d` archives produce partial metric
room geometry as described in `docs/formats/record3d.md`; calibration and
cross-room registration still require repeat/connector/tape evidence.

A **walk-in holdout** is a different folder. Copy `data/templates/walkin` into
`data/private/walkin` and follow `docs/walk-in.md`. Do not reuse
`drawing-room`, `my-room`, `pooja-room`, or `connector`.

The official prompt accepts a repeat at any one tier. The default template uses
photos; `repeat_of_job_id` must match the primary photo manifest and
`repeat_room_ids` must name at least one independently recaptured room.

Run `make benchmark` after copying new **benchmark** files. Run `make walkin`
after copying holdout files. Generated status JSON and Markdown distinguish
pending inputs from pipeline failures.
