# Reproduction evidence

## Clean-environment rehearsal — 2026-09-09

Scope: fresh Python virtual environment on the existing checkout. This is not yet a second-machine or fresh-clone rehearsal.

| Item | Observed |
| --- | --- |
| Host | macOS arm64 |
| Python | 3.12 |
| Environment | new `mktemp` directory and new virtual environment |
| Package install | `pip install -r requirements.txt`, then `pip install --no-deps -e .` |
| Network/cache caveat | wheels were downloaded; some metadata/wheels came from the local pip cache |

The first pass exposed a README defect: requirements installed successfully, but `python -m cozmo_floorplan` failed because the package itself had not been installed. The quickstart now includes the editable install and the same fresh environment resolved the module correctly.

## Timings

These numbers describe one machine and are not performance claims.

| Step | Wall time | Outcome |
| --- | ---: | --- |
| Create virtual environment | 1.63 s | pass |
| Install requirements | 19.35 s | pass |
| Install package editable | 2.22 s | pass |
| Run then-current 57 tests | 2.98 s | pass |
| Synthetic pipeline run | 1.02 s | exit 0, `status=ok` |
| Synthetic eval | 0.77 s | expected exit 3; report written |
| Fix-loop verification | 0.40 s | `pipeline_yield=fail->pass` |
| Total observed | 28.37 s | under the 15-minute README gate on this host |

The eval remains non-passing overall because repeatability and incumbent inputs are deliberately absent from this public fixture. The relevant synthetic yield, opening, ceiling, drift, and interval-calibration gates pass.

## Durable command

After README setup:

```bash
make reproduce-synthetic
```

This command forces deterministic agent mode, runs the public two-room RoomPlan fixture, evaluates it, expects the overall eval exit code 3, validates the FloorPlan schema and entity counts, asserts the expected pass and missing-evidence gates, verifies the checksum-locked fix-loop bundle, and returns 0 only if the complete contract holds. Generated files go to ignored `out/reproduction/`.

After adding the reproduction runner’s own tests, the full suite contains 59 tests and passes. The recorded 28.37-second total remains the exact initial clean-environment rehearsal rather than a retroactive estimate.

## Remaining reproduction work

- Repeat the README from a fresh clone on a second clean machine.
- Add raw benchmark captures, tape truth, repeat runs, and incumbent exports.
- Extend the reproduction entrypoint to regenerate every real table once those inputs exist.
- Time the cold walk-in command without a warmed environment.
