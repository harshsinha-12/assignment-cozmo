# Portable RoomPlan JSON v1

T6 accepts a small, explicit JSON interchange format derived from Apple RoomPlan surfaces. This avoids pretending that every app serializes Swift SIMD values identically. It is suitable for the optional T21 exporter and for adapting a captured `CapturedRoom` / `CapturedStructure` JSON file.

## File discovery

Put one of these files in `job/lidar/`:

- `roomplan.json`
- `captured_room.json`
- `captured_structure.json`

The root may be one room with `walls`, or a multi-room object with `rooms`.

## Surface contract

Each wall, door, window, or opening contains:

```json
{
  "identifier": "wall_1",
  "dimensions": [4.2, 2.5, 0.1],
  "transform": [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 2.1, 1.25, 0, 1],
  "confidence": "high"
}
```

- Dimensions are `[width, height, thickness]` in metres.
- A flat transform has 16 column-major values. Nested 4×4 row-major matrices are also accepted.
- For simpler exporters, `center: [x,y,z]` and `xAxis: [x,y,z]` may replace `transform`.
- The floor plane is world x-z and y is up.
- Confidence is `high`, `medium`, or `low`.
- An opening may provide `wallIdentifier` and `connectsRoomIds`.
- A wall may provide `roomIds` when it is shared.

See `data/fixtures/roomplan_two_room/lidar/roomplan.json` for the executable example.

## Current boundary

This is the tested RoomPlan surface adapter, not the raw `.r3d` or USDZ path.
Record3D archives have their own decoded input contract in
`docs/formats/record3d.md`, but still stop before plane extraction. USDZ remains
unsupported. Do not call Route 2 walk-in-ready until raw geometry and eval pass.
