# synthetic_two_room

Hand-written metric fixture. No images. Used to lock the FloorPlan schema and (later) eval math.

| Room | Size (cm) | Area (cm²) |
| --- | --- | --- |
| A | 400 × 300 | 120000 |
| B | 350 × 280 | 98000 |

Shared door: 80 cm wide, 210 cm high, on A's east wall, center at (400, 150).

Room B is shifted +10 cm in y so the shared wall is not identical in length (300 vs 280). That is deliberate: stitch tests should not assume equal wall lengths.

Coordinates: origin at A's south-west corner, +x east, +y north, centimetres.
