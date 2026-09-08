# Task queue

Agents: pick the highest item whose status is `todo` and whose Blocked-by is empty or done. Check boxes in the same edit as the work. Move finished items to **Done** with a date.

Status key: `todo` · `doing` · `blocked` · `done`

Product: local CLI + **disclosed LLM tool-calling agent**. Score policy: max every official row (`docs/cut-later.md`). Route 2 walk-in; Route 1 parallel (T21). See `docs/product.md` and `docs/agent-layer.md`.

---

## Now

| ID | Status | Task | Blocked-by | Notes |
| --- | --- | --- | --- | --- |
| T0 | done | Orchestration kit | — | 2026-09-07 |
| T1 | done | Official prompt in `docs/takehome.md` | human | 2026-09-08 |
| T2 | done | Synthetic two-room fixture | — | 2026-09-07 |
| T4 | done | Reconcile plan with official prompt | T1 | 2026-09-08 ingest |
| T3 | todo | Human benchmark capture | human + Pro phone | See Unblocked; parallel with engineering |
| T6 | blocked | LiDAR export → FloorPlan | T3 real Record3D export | RoomPlan JSON works; raw Record3D/USDZ must be hardened on captured files |
| T9 | todo | Stitch + drift correction + on/off ablation | T6 | Auto-fail if poses used as-is |
| T7 | todo | Video path | T6 | ±3% walls with CIs |
| T8 | todo | Photos path, 2–8 stills, folder stitch | T9 | Target ±8% walls **and** opening/ceiling/detection gates |
| T16 | todo | Agent layer: LLM tool calling + fallback for damage / concealed / scope | T12 | `docs/agent-layer.md`. Numbers still from recon tools |
| T21 | todo | Route 1: thin iOS RoomPlan/ARKit exporter + 10-min install | — | Parallel. Scored route stays Route 2 until install works |
| T17 | todo | Device matrix + capture-route polish | T3 | Fill measured intervals after eval |
| T18 | todo | Head-to-head vs Polycam or magicplan (2 rooms, LiDAR) | T3, T6 | Beat/tie ≥ 70% shared dims |
| T19 | todo | Fix loop bundle | T14 | Freeze **before** as soon as eval runs; ship fail→pass |
| T10 | todo | Technical report ≤ 6 pages + benchmark tables | T19 | `docs/writeup.md` |
| T20 | todo | README 15 min + reproduction bundle + compliance matrix | T10 | 100% contract coverage |
| T11 | todo | Walk-in rehearsal on a new room, all three tiers | T20 | Follow submitted capture route |

---

## Unblocked detail

### T3 — benchmark capture (human, start now)

Not optional. Composition from the prompt:

- 3+ rooms plus a connector
- Same spaces at **photos, video, LiDAR**
- Photos = per-room folders, **8 stills** per room (protocol maximum — max-score capture)
- One furnished room with **two staged damage classes**
- One room **twice at LiDAR** (required). Also twice at photos and twice at video if time.
- Laser or tape on walls, openings, **ceilings**; photo of tape
- Polycam **or** magicplan export on two rooms (name version). Do not use that app as the capture route.

Protocol for *our* capture: `docs/capture-protocol.md`. Protocol *they* will use until T21 ships: `docs/capture-route.md`.

Hardware: Harsh has **iPhone 17 Pro** (LiDAR). Walk-in may still be non-Pro.

Privacy: no faces/docs in git. Large binaries: Git LFS or `data/private/` gitignored + note the path in `HANDOFF.md`.

### Next engineering task

**T16** agent + tools while T6 raw Record3D waits on human **T3**. The LLM classifies damage and selects rules/actions; geometry tools remain the only source of measured quantities. T21 only if Xcode exists.

---

## Done

- **2026-09-08 T15** — Deterministic whole-property SVG renderer, paired atomically-written JSON/SVG artifacts, measured wall intervals, openings, scale bar, status/provenance summary, and failed-run placeholder.
- **2026-09-08 T14** — Official-gate eval package and CLI: red empty predictions, openings, ceilings, repeatability, drift ablation, photo stitch, photo/video walls, calibration, yield, and LiDAR head-to-head.
- **2026-09-08 T13** — Modular installable CLI, normalized job loading, schema validation, atomic `floorplan.json`, structured failure paths, code map, and command tests.
- **2026-09-08 T12** — FloorPlan IR v0.2: required interval-bearing measurements, damage, concealed-rule flags, scope, drift metadata, fixture migration, and contract tests.
- **2026-09-08** — Max-score retarget: do not pre-concede tiers/gates; cuts only via `docs/cut-later.md`. T21 iOS exporter added as parallel track.
- **2026-09-08 T4** — Ingest: plan/roadmap/TASKS aligned; ADR; product/compliance/route/device docs.
- **2026-09-08 T1** — Official case study in `docs/takehome.md`.
- **2026-09-07 T0** — Orchestration kit.
- **2026-09-07 T2** — Synthetic two-room fixture + schema tests.
