# roomplan_two_room

Synthetic LiDAR-tier job exercising the portable RoomPlan JSON adapter without claiming it came from a physical scan.

- Two globally positioned rectangular rooms
- Eight wall surfaces with metre dimensions and 4x4 column-major transforms
- One 80 cm × 210 cm shared door
- High RoomPlan confidence on every surface
- Two explicitly synthetic damage observations: a water stain and impact damage
- T9 plane-anchors the shared door; an injected 20 cm gap on room B closes to 0 cm
- Enriched CLI output may be `partial` under agent fallback even when stitch residuals are 0

Expected geometry matches `data/fixtures/synthetic_two_room/ground_truth.json` for wall lengths, room areas, ceiling heights, and the shared opening. `damage_observations.json` exercises the T16 agent/tool contract without pretending that real images have been captured. The fixture is an adapter contract, not accuracy evidence.
