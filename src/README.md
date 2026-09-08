# Source package

`cozmo_floorplan` is the local CLI and processing package. T13 establishes the command, job loader, schema validation, atomic output, and orchestration boundary. Reconstruction is intentionally not stubbed with fake geometry: unavailable adapters emit schema-valid structured failures.

See `docs/code-map.md` for the responsibility of every implementation file. Add future `geom`, `recon`, `stitch`, `render`, `eval`, and `agent` modules only with working behavior; empty placeholder packages rot and confuse agents.
