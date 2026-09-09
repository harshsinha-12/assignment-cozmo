# Fix-loop readable diff

Case: `agent-fallback-yield`

Code checkpoint: `git diff 3317339..68acdf6 -- src/cozmo_floorplan/agent tests/test_agent.py tests/test_agent_status_policy.py`

## Shipped change

The old finalizer always changed an otherwise healthy FloorPlan from `ok` to `partial` when it recorded `agent_fallback`. The new `record_fallback` policy keeps the warning in every case, but accepts an explicit `degrade_status` decision from orchestration:

- Explicit `COZMO_AGENT_MODE=fallback`, after all deterministic tools complete: `degrade_status=False`.
- Automatic fallback because no API key is configured: `degrade_status=True`.
- Fallback after a live provider failure, or skipped invalid observations: `degrade_status=True`.
- An already `partial` plan is never upgraded.

## Measured artifact delta

| Field | Before | Predicted | After |
| --- | --- | --- | --- |
| CLI exit | 2 | 0 | 0 |
| FloorPlan status | `partial` | `ok` | `ok` |
| `pipeline_yield` | fail, 0/1 `ok` | pass, 1/1 `ok` | pass, 1/1 `ok` |
| Fallback warning | present | present | present |
| Claims tool calls | 7 | unchanged | 7 |
| Drift gate | pass | unchanged | pass |
| Interval coverage | 100% | unchanged | 100% |

The before and after FloorPlans are byte-equivalent as parsed JSON after removing only the top-level `status`. Every non-target eval gate is also identical. The overall eval command still exits 3 because repeatability and incumbent evidence are missing; that is outside this declared fix.
