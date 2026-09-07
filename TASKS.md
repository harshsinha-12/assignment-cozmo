# Task queue

Agents: pick the highest item whose status is `todo` and whose Blocked-by is empty or done. Check boxes in the same edit as the work. Move finished items to **Done** with a date.

Status key: `todo` · `doing` · `blocked` · `done`

---

## Now

| ID | Status | Task | Blocked-by | Notes |
| --- | --- | --- | --- | --- |
| T0 | done | Orchestration kit (README, AGENTS, plan, roadmap, update, setup, schema, prompts) | — | 2026-09-07 |
| T1 | todo | Paste official take-home into `docs/takehome.md` when it arrives | human | Then run ingest prompt |
| T2 | done | Synthetic two-room fixture + ground-truth FloorPlan JSON | — | 2026-09-07 `data/fixtures/synthetic_two_room/` |
| T3 | todo | Optional real-room capture (photos + video + LiDAR if hardware exists) | human + phone | `docs/capture-protocol.md` |
| T4 | blocked | Reconcile plan with official prompt | T1 | `docs/prompts/ingest-takehome.md` |
| T5 | blocked | Freeze schema + red eval harness (`make test` fails honestly) | T4 | |
| T6 | blocked | LiDAR `CapturedRoom` → FloorPlan | T5 | First implementation |
| T7 | blocked | Video path | T6 | |
| T8 | blocked | Photos path with honest scale | T7 | |
| T9 | blocked | Stitch + SVG + eval table | T6 (can start after LiDAR) | |
| T10 | blocked | Write-up `docs/writeup.md` | T9 | |
| T11 | blocked | Interview drill from the actual submission | T10 | |

---

## Unblocked detail

### T3 — real capture

Only if Harsh has 20 minutes and a phone. Follow `docs/capture-protocol.md`. Check data into `data/fixtures/real_room_01/` **only if** it does not include other people’s faces, documents, or a home you do not want in git. Otherwise keep it local and note the path in `HANDOFF.md`.

---

## Done

- **2026-09-07 T0** — Agent orchestration kit committed on `cursor/agent-orchestration-docs-4470`.
- **2026-09-07 T2** — Synthetic two-room fixture + schema tests.
