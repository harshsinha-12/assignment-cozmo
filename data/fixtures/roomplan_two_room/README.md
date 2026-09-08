# roomplan_two_room

Synthetic LiDAR-tier job exercising the portable RoomPlan JSON adapter without claiming it came from a physical scan.

- Two globally positioned rectangular rooms
- Eight wall surfaces with metre dimensions and 4x4 column-major transforms
- One 80 cm × 210 cm shared door
- High RoomPlan confidence on every surface
- Multi-room output intentionally remains `partial` until T9 adds drift correction

Expected geometry matches `data/fixtures/synthetic_two_room/ground_truth.json` for wall lengths, room areas, ceiling heights, and the shared opening. The fixture is an adapter contract, not accuracy evidence.
