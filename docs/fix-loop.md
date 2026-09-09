# Fix declaration — offline fallback yield

Status: **fix shipped; predicted fail → pass reproduced**. Case id: `agent-fallback-yield`. Frozen evidence: `data/fix-loop/`.

## Worst observed gate

The synthetic two-room LiDAR run’s worst measured failing gate is `pipeline_yield`: **fail**, because `prediction_status=partial` (0 of 1 benchmark runs finish `ok`). Opening width, ceiling height, drift accountability, and interval calibration pass. Repeatability and incumbent comparison are missing evidence, not measured failures.

## Root-cause hypothesis and evidence

The deterministic offline claims agent completes all requested work—2 damage records, 1 concealed flag, and 2 scope lines—but `_with_fallback_warning` changes an otherwise `ok` document to `partial` solely because fallback mode was selected. The pipeline-yield evaluator correctly treats every `partial` result as failure. Geometry is not the cause: wall/opening errors are 0 cm on this synthetic contract fixture and the corrected stitch residual is 0 cm.

Hypothesis: expected, successful offline execution is being represented as degraded reconstruction health. The warning should remain auditable, but an explicitly selected and complete fallback should not downgrade an otherwise successful FloorPlan. Provider failure that triggers fallback may remain a distinct degraded condition.

## Intended fix and prediction

Change claims finalization so **explicit deterministic fallback with complete tool execution preserves `status: ok`**, while retaining provenance that fallback ran. Do not alter geometry, intervals, damage quantities, drift correction, or eval thresholds.

Prediction: `pipeline_yield` moves from **fail (`partial`) to pass (`ok`)**, or from 0% to 100% on this one-job baseline. Opening median error remains 0 cm, ceiling maximum error remains 0 cm, interval coverage remains 100%, and drift accountability remains pass. A geometry-metric change would contradict the hypothesis.

## Reproduction contract

The before artifacts are pinned to commit `523ceea11ba1bb405e3bc1c922447d1f427a0333`. The shipped status-policy code is pinned to `68acdf66c9d2f17870241d321e93243d50382538`. Both runs use `COZMO_AGENT_MODE=fallback` and are checksum-locked in `data/fix-loop/manifest.json`. `data/fix-loop/README.md` contains isolated-worktree reproduction commands, and `data/fix-loop/diff.md` explains the code and artifact delta.

## Result

The prediction was exact: the CLI moved from exit 2 / `status: partial` to exit 0 / `status: ok`, and `pipeline_yield` moved from fail to pass. The fallback warning, 7 claims tool calls, damage/scope output, geometry, drift gate, and 100% interval coverage were unchanged. Parsed before/after FloorPlans differ only in top-level `status`; every non-target eval gate is identical. The overall eval remains red only because unrelated repeatability and incumbent inputs are still missing.
