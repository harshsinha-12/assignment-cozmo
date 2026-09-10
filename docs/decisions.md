# Decisions (ADR-lite)

Newest first. One decision per heading. Do not silently reverse a decision in code.

---

## 2026-09-10 — Accept semantic USD/USDZ without using tape as reconstruction input

**Context:** The independent walk-in capture was available only as a binary
USD crate; paid Record3D export capacity was exhausted. The crate contains
metric named Wall, Door, Window, and Floor meshes. Tape measurements were
provided separately.

**Decision:** Decode `.usd` and `.usdz` through `usdcat`, read `.usda` directly,
and convert named semantic mesh extents/transforms into the shared RoomPlan-like
surface representation. Ignore furniture. Treat confidence as medium because
the source carries no RoomPlan confidence label. Keep tape exclusively in
`ground_truth.json`; it is never read by reconstruction.

**Consequence:** The holdout now runs cold with geometry and `pending=0`, but
its open eight-segment wall loop and measured errors remain `partial` and
non-passing. Format support improved; accuracy was not relabeled.

---

## 2026-09-10 — Photo SfM after a connected graph; occupancy room fallback

**Context:** A walk-in that followed the eight-still protocol could connect and
still hit `unsupported_tier`. Video rooms failed when a plane peak was missing
even though points existed around the camera path.

**Decision:** After the overlap graph connects, run incremental SfM with
assumed intrinsics and the disclosed 1.45 m handheld-height prior. Keep T8b
gates unchanged. When wall plane peaks are missing, expand an occupancy
envelope that includes the camera path. Floor/ceiling fallback is the densest
Y-band, not a high percentile that follows outliers. Do not overlay
independently scaled photo/video rooms.

**Consequence:** Synthetic overlapping stills emit a partial FloorPlan. Author
photos stay `insufficient_overlap`. Native video on harsh-home-01 moved
failed→partial with 8 walls; centimetre gates are not claimed.

---

## 2026-09-10 — Walk-in rehearsal follows the evaluator-selected tier

**Context:** The defense selects one of photos, video, or LiDAR. The original
rehearsal always audited all three, so missing unselected media could leave the
walk-in `pending_inputs` even when the chosen path was ready. Failed geometry
also exposed warnings but no concise operator action.

**Decision:** Keep `all` as the full-rehearsal default and add an explicit
`--tier` / `WALKIN_TIER` selector. Input auditing, holdout collision checks,
execution, and evaluation apply only to selected tiers. Each timed run reports
whether rooms and walls were emitted, warning codes, and the next capture
action. A successful photo reconstruction is now forwarded through the shared
pipeline instead of falling through, while the photo adapter remains honest
about its still-unimplemented metric SfM boundary.

**Consequence:** The live harness now matches the examiner's chosen path and
can drive a fast recapture loop. This is an operational reliability improvement;
it does not turn a missing room or a non-passing centimetre gate into a pass.

## 2026-09-10 — Native video emits partial rooms; ±3% waits on tape

**Context:** Four Camera-app MP4s have no ARKit sidecars. A handheld-height
prior can scale unitless VO only after a triangulated floor exists. Requiring
every clip in the job to produce a four-wall room discarded connector/my-room
evidence that had already reached room fitting. Trajectory 10–90% bracketing
also failed when VO drift pushed cameras toward a wall. Official video walls
are ±3% with calibrated intervals; handheld intervals are intentionally wide.

**Decision:** Skip at most one failed adjacent VO edge with a measured i→i+2
pose (`maximum_edge_span=2`). Bracket walls about the median camera coordinate.
Emit a `partial` FloorPlan for rooms that pass floor/ceiling/wall support;
omit failed walkthroughs with warnings. Detect occupancy-profile openings
without inventing phantoms. Link openings for stitch only in a shared exported
world frame. Do not overlay independently scaled native rooms. Do not shrink
handheld intervals to the official ±3% row.

**Consequence:** A native job can return some rooms instead of `unsupported_tier`
when the connector clip is not a rectangle. ±3% remains a measured eval result,
not a reconstruction claim.

## 2026-09-10 — Walk-in rehearsal is a holdout folder, not the benchmark

**Context:** T11 is a cold rehearsal of the 30% defense: a room they have never
scored, all three tiers, one public `run` command, tape while it runs. The
Route 2 card previously told the operator to copy into `data/private/benchmark-*`
and run `make benchmark`, which would mix the walk-in with the author's
property.

**Decision:** Keep Route 2 as the scored capture protocol. Walk-in media goes in
`data/private/walkin/` from `data/templates/walkin`. `make walkin` times each
tier, crash-tests the official 2-still photo floor, and refuses room ids in
`drawing-room` / `my-room` / `pooja-room` / `connector`. The defense command
stays `python -m cozmo_floorplan run JOB --out OUT`. Route 1 remains optional
until a timed cable install on their phone (`docs/capture-route-route1.md`).

**Why:** The prompt scores systems that only work on the author's data. A
holdout folder plus an explicit collision check is the rehearsal of that exam.

**Consequence:** T11 is not done until holdout photos, video, LiDAR, and tape
exist. The harness can stay `pending_inputs` without treating that as a score.

---

## 2026-09-10 — T21h is a cable Personal-Team install, not TestFlight

**Context:** Route 1 must install on Cozmo's walk-in phone in under 10
minutes. TestFlight needs a paid Apple Developer Program team ($99/year).
The current `DEVELOPMENT_TEAM` `PH4KQ4LY92` is a free Personal Team and cannot
upload to App Store Connect. Harsh declined that fee. The app already runs on
Harsh's iPhone 17 Pro (T21g).

**Decision:** Use the official prompt's other option: a **dev build installed
by cable in under 10 minutes**. The walk-in card is
`docs/capture-route-route1.md`; the command is
`./scripts/install-cozmo-capture.sh`. Do not enroll in the paid program. Do
not switch the scored capture route to Route 1 until that same install is
timed on **their** phone. Developer Mode restart, a non-Mac laptop, or a
failed `ppq.apple.com` trust check aborts to Route 2.

**Why:** The prompt names TestFlight and a 10-minute cable install as equals.
A Personal Team is enough for Xcode/`devicectl` install. Paying $99 does not
change geometry quality.

**Consequence:** Personal-team apps expire after seven days. A new device must
be plugged in so Xcode can register its UDID. Route 2 (`docs/capture-route.md`)
stays the submitted walk-in protocol.

## 2026-09-09 — Version calibrated video output separately from triangulation

**Context:** Sidecar v1.1 already enables calibrated sparse triangulation, but
multi-room FloorPlan output also needs a declared metric provider and proof
that room coordinates share one tracking frame. Adding required fields to v1.1
would silently break its published contract.

**Decision:** Preserve v1.1 for intrinsics and camera axes. Sidecar v1.2 adds
required `scale_source` and `world_frame_id`. Only v1.2 may authorize video
FloorPlan output, and every video in one job must name the same world frame.

**Consequence:** Existing v1.1 inputs remain valid for diagnostics. Unrelated
room coordinates cannot be overlaid or mislabeled as a whole-property plan.

## 2026-09-09 — Refuse photo SfM before the evidence graph connects

**Context:** Passing the 2–8 file-count contract does not mean the views share
enough scene content for reconstruction. Starting SfM on isolated viewpoints
can yield separate models or false matches, while cross-room lookalikes are not
proof of adjacency.

**Decision:** Build an all-pairs bounded ORB graph first. Require mutual ratio
matches plus seeded homography/fundamental inliers and spatial coverage. Require
one connected component per room. Apply stricter thresholds across rooms and
label surviving links connector candidates only. Fail as
`insufficient_overlap` before metric reconstruction when these gates fail.

**Consequence:** All three current photo folders are disconnected (4, 6, and 6
components) and no cross-room candidate survives. This produces an actionable
reshoot request and prevents a flattering but unreproducible SfM claim.

## 2026-09-09 — Metric video poses require two correspondence keys

**Context:** A JSON list of positions beside a video is not enough to establish
which decoded image each pose describes. Attaching poses by array order can
silently scale the wrong frames, especially after bounded sampling or variable
frame timing.

**Decision:** Accept metric video poses only in a versioned per-video contract:
metres, camera-to-world, right-handed y-up, clip-relative timestamps, increasing
encoded frame indices, finite positions, and unit XYZW quaternions. Preserve
the sampled source-frame index and timestamp. Align each local VO segment only
with at least three exact frame matches whose timestamps agree within 25 ms;
reject degenerate paths and alignment RMSE above 15 cm.

**Consequence:** Synthetic alignment recovers known metric scale and positions,
while wrong units, duplicate frames, invalid rotations, and shifted timestamps
fail explicitly. The current Camera-app MP4s have no sidecars and remain
unitless; this stage does not claim video wall accuracy.

## 2026-09-09 — Split video trajectories instead of bridging failed edges

**Context:** A video can contain useful translational runs separated by blur,
pure rotation, featureless walls, or weak cheirality. Chaining across a rejected
edge would silently manufacture motion. Native MP4s also lack calibrated camera
intrinsics and metric scale.

**Decision:** Recover essential-matrix poses only for feature-eligible edges,
using a disclosed image-size focal prior. Normalize every translation to unit
length, close the active local segment on any failed edge, and restart later
evidence in a new identity-anchored segment. Do not claim those segments are
globally relocalized or metric.

**Consequence:** The two uploaded videos yield 21/89 and 17/89 accepted pose
edges across 10 and 9 local segments. This proves recoverable relative motion,
not room dimensions; T7e must validate a scale/alignment source before emitting
FloorPlan geometry.

## 2026-09-09 — Gate relative video motion before estimating a trajectory

**Context:** A large raw feature count does not establish usable camera motion.
Blur, blank paint, repeated texture, stationary frames, and pure rotation can
all produce misleading matches or a homography without translational parallax.

**Decision:** Before VO, analyze a bounded 60 adjacent-pair sample with ORB,
Hamming ratio matches, seeded fundamental/homography RANSAC, median image motion,
homography-residual parallax, and convex-hull image coverage. Record every failed
condition by name and require 35% of analyzed pairs to pass. Do not interpret
the relative motion as metres.

**Consequence:** Both current walkthroughs pass this internal trackability gate
with 23/60 and 27/60 eligible pairs. Synthetic pure rotation and blank frames
fail. T7d can work on a qualified feature graph, but scale and official ±3%
accuracy remain unproven.

## 2026-09-09 — Apply video display rotation exactly once

**Context:** Both uploaded iPhone MP4 files store 1280×720 encoded frames plus a
display transform. OpenCV reports `90` degrees clockwise and, by default, may
auto-rotate to 720×1280. Relying on backend defaults risks sideways frames on
one machine or double rotation on another.

**Decision:** Disable backend auto-rotation before decoding, normalize metadata
to a supported quarter turn, apply that transform explicitly, and record native
and display dimensions. Process every sorted video and bind pose sidecars by
filename stem; a global sidecar is ambiguous when multiple videos exist.

**Consequence:** The two real room videos deterministically produce upright
720×1280 RGB samples with separate identities. The adapter still refuses metric
geometry until tracking plus a validated scale/pose source exists.

## 2026-09-09 — Preserve separate Record3D world poses without claiming registration

**Context:** The upload contains one `.r3d` archive per room. Each archive has
metric ARKit poses, but the format provides no shared-session identifier and the
capture lacks a connector scan or labeled matching doorway. Translating rooms
into a neat layout would invent adjacency.

**Decision:** Emit every accepted room in its exported Record3D world-xz
coordinates, detect an opening only from a sparse wall band with surviving
sill/lintel evidence, and keep the multi-room result `partial` until a shared
opening association is proven. Use named, deliberately uncalibrated measurement
intervals rather than copying RoomPlan confidence widths.

**Consequence:** The real command now produces useful JSON/SVG geometry instead
of a failed stub, while duplicate disconnected warnings are suppressed. Four
opening candidates are visible for review, but neither they nor the inter-room
layout count as scored accuracy before tape, repeat, and connector evidence.

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
## 2026-09-09 — Repeatability accepts any one same-tier pair

**Context:** Earlier planning and readiness code required a LiDAR repeat, but the
official prompt says only: “At least one room captured twice at the same tier.”
Harsh supplied independent photo and video repeats; the additional Record3D free
plan is unavailable.

**Decision:** The benchmark accepts a correctly linked repeat at any declared
tier. The active evidence pair is `my-room` at the photo tier. Repeat manifests
must name `repeat_of_job_id` and at least one `repeat_room_ids` entry. A lone
folder or mismatched tier is not sufficient evidence.

**Consequences:** LiDAR repeat is no longer a readiness blocker. This changes
input eligibility only; the repeatability gate still fails honestly until both
runs emit comparable wall measurements within the official tolerance.

---
