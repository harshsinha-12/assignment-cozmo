# Task queue

Agents: pick the highest item whose status is `todo` and whose Blocked-by is empty or done. Check boxes in the same edit as the work. Move finished items to **Done** with a date.

Status key: `todo` · `doing` · `blocked` · `done`

Product: local CLI + **disclosed LLM tool-calling agent**. Score policy: max every official row (`docs/cut-later.md`). Route 2 walk-in; Route 1 parallel (T21). See `docs/product.md` and `docs/agent-layer.md`.

---

## Without media (do these while T3 is empty)

Harsh’s photos / video / LiDAR are **not** required for the rows below. Use generated fixtures and the RoomPlan two-room job. Do **not** invent centimetres or mark a scored gate pass without eval numbers.

| ID | Can finish now? | What to do without uploads |
| --- | --- | --- |
| **T21** | Yes, if Xcode.app | Thin iOS RoomPlan exporter. Blocked on full Xcode, **not** on captures. Command Line Tools only → skip. |
| **T10** | **Draft next** | Architecture, tier design, drift write-up, error-budget narrative in `docs/writeup.md`. Leave numbered benchmark tables blank until T3 eval. |
| **T20** | Partial | Clean-machine README command, compliance-matrix file paths, synthetic reproduction. Do not fill measured device intervals. |
| T8 remainder | Ingest only (done) | Folder discovery / 2–8 JPEG checks already ship. Metric SfM, scale, adjacency, ±8% walls need T3 photos. |
| T7 remainder | Ingest only (done) | Frame sampling already ships. Metric VO / ±3% walls need T3 walkthrough. |

**Do not start without media:** T3 itself, T6 raw Record3D/USDZ, T7 VO, T8 SfM, T17 measured intervals, T18 Polycam/magicplan, T11 walk-in.

---

## Now

| ID | Status | Task | Blocked-by | Needs media? | Notes |
| --- | --- | --- | --- | --- | --- |
| T0 | done | Orchestration kit | — | no | 2026-09-07 |
| T1 | done | Official prompt in `docs/takehome.md` | human | no | 2026-09-08 |
| T2 | done | Synthetic two-room fixture | — | no | 2026-09-07 |
| T4 | done | Reconcile plan with official prompt | T1 | no | 2026-09-08 ingest |
| T3 | todo | Human benchmark capture | human + Pro phone | **yes — this is the upload** | See Unblocked |
| T6 | blocked | LiDAR export → FloorPlan | T3 real Record3D export | **yes** (raw Record3D/USDZ) | RoomPlan JSON path already works on the synthetic fixture |
| T9 | done | Stitch + drift correction + on/off ablation | T6 | no | 2026-09-08 plane-anchored snap; shared walls stay with first owner |
| T7 | todo | Video path | T6 | ingest **no**; metric VO **yes** | Sampling shipped; ±3% walls need T3 walkthrough |
| T8 | todo | Photos path, 2–8 stills, folder stitch | T3 media | ingest **no**; SfM/scale **yes** | T8a ingest done. Target ±8% walls plus opening/ceiling/detection gates |
| T21 | todo | Route 1: thin iOS RoomPlan/ARKit exporter + 10-min install | Xcode.app | no | Parallel. Scored route stays Route 2 until install works |
| T17 | todo | Device matrix + capture-route polish | T3 | **yes** (measured intervals) | Protocol text can be edited now; numbers wait on eval |
| T18 | todo | Head-to-head vs Polycam or magicplan (2 rooms, LiDAR) | T3, T6 | **yes** | Beat/tie ≥ 70% shared dims |
| T10 | todo | Technical report ≤ 6 pages + benchmark tables | T19 | draft **no**; tables **yes** | `docs/writeup.md` |
| T20 | todo | README 15 min + reproduction bundle + compliance matrix | T10 | partial **no**; measured rows **yes** | 100% contract coverage |
| T11 | todo | Walk-in rehearsal on a new room, all three tiers | T20 | **yes** | Follow submitted capture route |

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

See **Without media** above. Next fully unblocked: **T10 report draft**. **T21** if Xcode.app exists. Do not start T6 raw Record3D, T7 VO, T8 SfM, T17 numbers, T18, or T11 until files are in `data/private/`.

---

## Done

- **2026-09-09 T19 fix loop** — Frozen checksum-locked before and after bundles around one declared status-semantics fix; `pipeline_yield` moved exactly as predicted from fail/partial to pass/ok, with unchanged non-target gates and a readable diff.
- **2026-09-09 T19a before freeze** — Declared the failing `pipeline_yield` gate, hypothesis, fix, and numeric prediction; pinned commit `523ceea`; stored JSON/SVG/ablation/eval artifacts with SHA-256 verification and isolated-worktree reproduction commands.
- **2026-09-09 T8a ingest** — Stable per-room photo discovery, official 2–8 count enforcement, real decode/size validation, generated-JPEG tests, and structured refusal until metric SfM/scale/adjacency exist.
- **2026-09-08 T7 ingest** — Video job sampling (OpenCV, ~2 Hz) and pose-sidecar detection. Structured failure until metric VO; no guessed centimetres. Generated mp4 tests, no private capture required.
- **2026-09-09 T9** — Plane-anchored shared-opening drift correction, SE(2) constraint graph, correction-on/poses-as-is CLI artifacts, residual metadata, eval wiring, and synthetic 20 cm drift regression. Shared walls stay with the originating room so the gap actually closes.
- **2026-09-08 T16** — Live OpenAI Responses tool-calling agent plus transactional deterministic fallback; strict damage, concealed-rule, and scope tools; metric observation contract; live synthetic smoke test.
- **2026-09-08 T15** — Deterministic whole-property SVG renderer, paired atomically-written JSON/SVG artifacts, measured wall intervals, openings, scale bar, status/provenance summary, and failed-run placeholder.
- **2026-09-08 T14** — Official-gate eval package and CLI: red empty predictions, openings, ceilings, repeatability, drift ablation, photo stitch, photo/video walls, calibration, yield, and LiDAR head-to-head.
- **2026-09-08 T13** — Modular installable CLI, normalized job loading, schema validation, atomic `floorplan.json`, structured failure paths, code map, and command tests.
- **2026-09-08 T12** — FloorPlan IR v0.2: required interval-bearing measurements, damage, concealed-rule flags, scope, drift metadata, fixture migration, and contract tests.
- **2026-09-08** — Max-score retarget: do not pre-concede tiers/gates; cuts only via `docs/cut-later.md`. T21 iOS exporter added as parallel track.
- **2026-09-08 T4** — Ingest: plan/roadmap/TASKS aligned; ADR; product/compliance/route/device docs.
- **2026-09-08 T1** — Official case study in `docs/takehome.md`.
- **2026-09-07 T0** — Orchestration kit.
- **2026-09-07 T2** — Synthetic two-room fixture + schema tests.
