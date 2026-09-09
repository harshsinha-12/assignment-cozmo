# Fix-loop bundle

`before/` is the immutable T19a baseline described in `docs/fix-loop.md`. `manifest.json` pins its source commit, expected non-zero command exits, target gate, prediction, and SHA-256 hashes.

Verify the checked-in evidence:

```bash
PYTHONPATH=src python3 -m cozmo_floorplan.fix_loop.verify data/fix-loop
```

Regenerate it from the pinned code without changing the current checkout:

```bash
git worktree add --detach /tmp/cozmo-floorplan-before 523ceea11ba1bb405e3bc1c922447d1f427a0333
cd /tmp/cozmo-floorplan-before
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
PYTHONPATH=src COZMO_AGENT_MODE=fallback .venv/bin/python -m cozmo_floorplan run data/fixtures/roomplan_two_room --out /tmp/cozmo-floorplan-before-output
PYTHONPATH=src .venv/bin/python -m cozmo_floorplan eval --pred /tmp/cozmo-floorplan-before-output/floorplan.json --truth data/fixtures/synthetic_two_room/ground_truth.json --ablation-off /tmp/cozmo-floorplan-before-output/floorplan.ablation-off.json --out /tmp/cozmo-floorplan-before-output
```

The run and eval commands intentionally exit 2 and 3 because this is failing evidence. Compare the regenerated files with `before/`. Remove the temporary worktree after leaving it with `git worktree remove /tmp/cozmo-floorplan-before`.
