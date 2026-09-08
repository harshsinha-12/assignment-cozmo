# Damage observation input v1

`damage_observations.json` is the boundary between capture/CV preprocessing and the T16 claims agent. It is optional and lives at the job root.

Each observation supplies:

- a stable id and existing FloorPlan surface reference;
- evidence references, normally job-relative image or crop paths;
- a metric extent and interval produced by calibrated projection, segmentation, or a manual annotation;
- a local classifier candidate and confidence used by the deterministic fallback;
- an optional surface-local polygon.

The live OpenAI agent receives referenced local JPEG, PNG, or WebP images plus the observation ids, selects a damage class, then invokes mutation tools. It cannot submit an extent to `apply_damage`; that tool copies the observation measurement. The fallback uses the same mutation tools and the explicit `fallback_class`.

The included RoomPlan fixture uses `synthetic://` evidence references and `synthetic_surface_projection`. These are contract fixtures, not captured damage or accuracy evidence. Replace them with job-relative crop paths after the real benchmark capture.
