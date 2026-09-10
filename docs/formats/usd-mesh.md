# Semantic USD room-mesh input

Put one `.usd`, `.usda`, or `.usdz` file in `job/lidar/`. The job manifest
remains `tier: lidar` and should name exactly one room in `rooms`.

The adapter reads meshes whose names begin with `Wall`, `Door`, or `Window`.
It uses each mesh's metric `extent` and `xformOp:transform`, projects the local
width axis into world x-z, and then passes the surfaces through the same
FloorPlan IR builder used by portable RoomPlan JSON. Furniture/object meshes
are ignored. No tape value or official threshold enters reconstruction.

ASCII `.usda` is read directly. Binary `.usd` crates and `.usdz` packages are
converted in memory with Pixar `usdcat`, which is included in the macOS USD
toolchain. When `usdcat` is unavailable, the CLI returns an explicit
`unsupported_tier` warning rather than inventing geometry. Source meshes do not
carry RoomPlan confidence labels, so output measurements use the existing
medium-confidence LiDAR intervals.

Measured holdout: `mummy-room` produced one room, eight wall segments, two
doors, one window, and an SVG in 0.106 seconds. The open wall loop produced a
`partial` result. Against independent 300 × 360 × 290 cm truth, the current
errors are 16.1 cm for one matched wall, 4.17 cm for the closest door, 7 cm for
ceiling, and 48.2% for area. None is presented as a passing gate.
