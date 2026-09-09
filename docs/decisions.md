# Decisions (ADR-lite)

Newest first. One decision per heading. Do not silently reverse a decision in code.

---

## 2026-09-09 — Wall candidates must bracket the camera path

**Context:** Raw Record3D cloud bounds include furniture and isolated depth
outliers. Selecting extreme x-z points would turn clutter into walls, while a
dense short object can also create a strong vertical histogram peak.

**Decision:** Detect floor and ceiling independently in the gravity-aligned
y-axis, retain only x-z columns with at least 1.5 m of vertical support, search
the Manhattan yaw in 0.5-degree steps, and select the strongest low/high wall
peaks outside the central 80% of the camera trajectory. Keep this as a
diagnostic candidate until openings and a schema-valid room are constructed.

**Consequence:** All three private scans produce bounded four-wall candidates
without using raw cloud extrema. Their candidate dimensions and ceiling
separations are not accuracy claims; tape/laser truth is still required for
scoring and interval calibration.

## 2026-09-09 — Build bounded metric clouds before fitting Record3D planes

**Context:** The real scans contain roughly four thousand 60 fps frames each.
Fusing every depth pixel would add runtime and correlated samples before the
coordinate path itself was proven.

**Decision:** T6b1 samples 61 inclusive frames, accepts medium/high confidence
depth from 0.10–8 m, scales RGB intrinsics to depth resolution, back-projects
forward on OpenGL negative-Z, applies normalized XYZW camera-to-world poses, and
averages points into 2.5 cm voxels. Sampling, rotation, configuration, and the
point algorithm live in separate modules.

**Consequence:** Each real room produces 224k–261k deterministic metric voxels
in about 2.3–2.5 seconds locally. Bounds remain diagnostics—not wall lengths—so
T6b2 must reject furniture/outliers and fit physical planes before IR output.

## 2026-09-09 — Decode Record3D first; fit geometry in a separate stage

**Context:** Three real `.r3d` room captures are now available. Each is a ZIP
containing thousands of matched JPEG, LZFSE float-depth, and confidence frames,
plus timestamps, metric poses, and per-frame intrinsics.

**Decision:** T6a adds a typed archive/decompression boundary and bounded real
capture validation. T6b will own point-cloud fusion and plane extraction. The
CLI reports the validated evidence but remains structurally failed until T6b,
so decoded sensor data is not mislabeled as a dimensioned floor plan.

**Consequence:** Format uncertainty is removed and the guaranteed Route 2 input
is readable. No wall/opening/ceiling accuracy is claimed before tape-backed eval.

## 2026-09-09 — Plane-anchor shared openings; always emit a poses-as-is ablation

**Context:** The official drift gate rejects RoomPlan poses used unchanged. No real repeated capture exists yet, but the synthetic two-room RoomPlan fixture can carry a controlled transform error.

**Decision:** Fix the first room as the floor-plan frame, derive SE(2) constraints from shared opening frames, and rigidly align each reachable neighboring room. The normal CLI emits corrected geometry and `floorplan.ablation-off.json`; `--no-drift-correction` regenerates only the poses-as-is path. Record before/after opening-gap residuals with intervals. If there are no usable constraints, report method `none` instead of claiming a no-op correction.

**Consequence:** T9 is implemented and testable on a synthetic 20 cm drift injection, including the existing eval gate. This proves algorithm and artifact plumbing, not real-world centimetre accuracy or loop-closure quality; those claims remain blocked on T3 captures.

---

## 2026-09-08 — Normalize RoomPlan JSON; do not guess raw Record3D bytes

**Context:** No real LiDAR capture exists yet. Apple exposes metric RoomPlan surfaces but does not define one universal third-party JSON layout. Record3D exposes depth, confidence, intrinsics, and poses, while the on-disk `.r3d` path needs a captured fixture to validate decompression and frame conventions.

**Decision:** T6 implements and tests a portable RoomPlan JSON v1 contract (`docs/formats/roomplan-json.md`) with metric surface dimensions and transforms. The adapter accepts single- and multi-room wrappers and produces FloorPlan v0.2. Raw Record3D metadata/depth and USDZ are detected but return structured unsupported warnings until Harsh supplies real exports.

**Consequence:** RoomPlan geometry is usable now for the renderer and eval. The guaranteed Route 2 LiDAR path is not called complete or walk-in-ready. T6 remains blocked on T3 for raw Record3D hardening.

---

## 2026-09-08 — FloorPlan IR v0.2 uses interval-bearing measurement objects

**Context:** The official contract requires a confidence interval on every measurement. The provisional v0.1 schema used bare numeric dimensions and only offered an optional wall `error_interval`.

**Decision:** Version 0.2 represents every reported scalar dimension as `{value, unit, interval}`. The interval requires `low`, `high`, and a coverage `confidence`. This applies to room height/area, wall dimensions, opening dimensions, stitch transforms/residuals, damage extent, and scope quantity. Polygon vertices remain the canonical geometry coordinates rather than duplicate scalar reports. Public output units are centimetres; area measurements identify `cm2` explicitly.

The top-level `damage`, `concealed_flags`, and `scope` arrays are required even when empty. Claims objects reference typed surfaces; concealed flags require the fired `rule_id`; scope lines require an interval-bearing quantity and its source. Stitch output records the drift-correction method for the named ablation gate.

**Compatibility:** This intentionally breaks the provisional 0.1 fixture. The schema version and fixture both move to `0.2.0` before reconstruction code exists.

---

## 2026-09-08 — LLM tool calling for claims objects; geometry stays classical

**Context:** Role is AI Backend / Applied AI. Harsh: we **will** use AI tool calling / an API, not a geometry-only CLI.

**Decision:** Add an **agent layer** (`docs/agent-layer.md`) after reconstruction. Disclosed OpenAI-compatible (or Anthropic) API with tools. The model classifies damage, selects concealed-damage **rules**, and writes scope lines. Wall lengths, openings, ceilings, stitch, and intervals come **only** from recon tools.

**Constraints from the packet:**

- No calls to **our** servers. Public API + local fallback is allowed.
- Walk-in: `OPENAI_API_KEY` on their machine, or fallback so `run` still exits with valid JSON.
- Do not let the LLM invent centimetres.

**Rejected:** LLM-only floor plans; a chat UI; hosting our own inference infra.

---

## 2026-09-08 — Target maximum score; cut only tomorrow night

**Context:** Earlier notes hedged (“LiDAR maybe”, “photos will miss 2 cm”, “skip the iOS app”). Harsh: initially target **everything** that scores; revisit cuts tomorrow / tomorrow night if time is gone.

**Decision:** The plan is a **full-score attempt**. Every official gate, all three tiers, full Round 1 output contract, head-to-head, fix loop, walk-in hardening, and a Route 1 app **in parallel** until time forces a cut. Build *order* is still schema → LiDAR → stitch → video → photos (dependencies), not “only LiDAR counts.”

**Cut policy:** `docs/cut-later.md`. Agents must not mark photo/video/damage/app as out of scope today.

**Fix loop:** Freeze a regenerable **before** run as soon as eval exists, even if later runs are better. Full marks need fail→pass, not a perfect first shot with no delta.

**Capture route:** Submit **one** route. Default scored route remains Route 2 so the walk-in always has a protocol. Promote Route 1 only if a 10-minute install build actually exists before the defense. Until then, both tracks stay in `TASKS.md`.

---

## 2026-09-08 — Official prompt vs provisional plan

**Context:** Round 2 case study (`docs/takehome.md`) is in repo. Provisional plan assumed geometry-only, optional real capture, photos may emit `units: relative`, iOS app out of scope, no website.

**Decision:** Align to the prompt. Keep three-adapters-one-IR. Change product and gates as below.

| Topic | Provisional | Official | We do |
| --- | --- | --- | --- |
| Capture data | Optional one room | None from them; we build a specified benchmark | Human capture T3 now |
| Capture app | Out of scope | Route 1 **or** Route 2 | Route 2 guaranteed; Route 1 parallel (T21) |
| Tiers | Design all; LiDAR first | All three mandatory, including photo stitch | All three |
| Output | Walls/rooms/openings/SVG | Plus damage, concealed flags+rule, scope, CI on every number | Extend schema |
| Photos scale | `relative` + `missing_scale` if no prior | Metric ±8% with **calibrated intervals**; opening/ceiling gates listed without a tier exemption | Target every numbered gate on every tier; intervals stay honest |
| Website / HTTP | Optional later | Not asked | Do not build (does not score) |
| ESX | Out | Still not asked | Out |
| Eval | Our internal cm targets | Named gates + walk-in + fix loop 25% + head-to-head | Official gates win |
| Timebox | Unknown | User: < 48 hours + later defense | Full target; cuts only via `docs/cut-later.md` |

**Rejected:** Pre-conceding photo centimetre gates in the plan; skipping damage/scope; building a website first. **Superseded on app/hedging:** see 2026-09-08 max-score ADR.

**Consequences:** Next session is T12 schema freeze, not SfM. Photos policy in `.cursor/rules/01-assignment.mdc` updated.

---

## 2026-09-08 — Route 2 is the guaranteed walk-in; Route 1 is a max-score parallel track

**Decision:** Keep a one-page stock protocol (`docs/capture-route.md`) as the route they can always follow. Also build a thin RoomPlan/ARKit exporter (T21) if a Mac/Xcode path exists. Only **one** route is submitted. Switch the scored route to the app if and only if install on their phone is under 10 minutes.

**Why:** User asked to target max score. Route 1 can improve LiDAR walk-in quality; Route 2 protects the 30% if TestFlight slips.

**Supersedes:** “do not start an iOS app” as a standing rule. Cut T21 only via `docs/cut-later.md`.

---

## 2026-09-08 — Photos emit centimetres with wide intervals

**Decision:** Public `units` stay `cm`. Photo-tier measurements carry wide confidence intervals (the v0.2 `interval` object). Do not use `units: relative` as the graded output.

**Why:** Official photo gate is wall lengths within ±8% with calibrated intervals. Relative units would fail the contract. Physics is unchanged: scale is weak; honesty lives in the interval, not in a fake point estimate.

---

## 2026-09-07 — Orchestration before implementation

**Context:** Official take-home not in repo. User asked for README, plan, roadmap, update, and agent-orchestration files.

**Decision:** Ship documentation, schema, setup, and prompts. Do not implement reconstruction.

**Consequences:** Next session can code within hours of a prompt paste. Risk: plan may be wrong. Mitigated by `docs/prompts/ingest-takehome.md`.

---

## 2026-09-07 — One FloorPlan IR, three adapters

**Decision:** Shared JSON schema; tier-specific frontends.

**Rejected:** Three independent demos; LLM-only dimension guessing.

---

## 2026-09-07 — Python, classical CV, Cloud-Agent-light deps

**Decision:** Python 3.11+, numpy/opencv/shapely first. COLMAP/Open3D/PyTorch optional later.

**Why:** JD allows Python or TypeScript; Cloud Agents are Linux; install time matters; interview wants evals more than a 2 GB model dump.

---

## 2026-09-07 — No ESX writer unless required

**Decision:** Emit FloorPlan JSON + SVG. Xactimate ESX is explicitly later.

**Why:** ESX is proprietary-ish, easy to waste the whole timebox, weak signal vs IR + eval.

---

## 2026-09-07 — Refuse fake centimetres

**Decision:** Photos without a scale prior return relative units + warning, not invented cm.

**Why:** Matches SfM physics and Cozmo’s “don’t invent a price or a scope” product ethic.

---

## 2026-09-07 — Committed `.cursor/environment.json`

**Decision:** Repo-managed Cloud Agent install from `requirements.txt`.

**Why:** User asked for setup files; committed env overrides dashboard and makes the next agent reproducible. Keep install small so we do not trap the project in a 20-minute COLMAP image.
