# Update log

Append-only. Newest entry at the top. This is the cache that stops agents from repeating web research and PDF extraction.

Format:

```text
## YYYY-MM-DD — short title

- Context
- Done
- Learned (facts the next agent should trust)
- Next
```

## 2026-09-09 — T8b photo overlap graph complete

- Added separate immutable photo-overlap policy, reusable ORB/mutual-match
  feature utilities, and a graph algorithm for within-room connectivity and
  conservative cross-room connector candidates.
- Each pair records the stronger seeded homography/fundamental support plus
  match count, inlier ratio, spatial coverage, and named rejection reasons.
  Cross-room evidence uses stricter thresholds and never becomes adjacency by
  itself.
- Added synthetic tests for a connected transformed sequence, unrelated rooms,
  a featureless disconnected image, and the connected-graph metric boundary.
- Real result: drawing-room has 3/21 eligible edges and 4 components; my-room
  2/28 and 6; pooja-room 2/28 and 6. No room pair has a connector candidate.
  The CLI now returns actionable `insufficient_overlap` instead of proceeding
  to an unstable SfM model or inventing scale.
- All 100 tests, Ruff, touched-file formatting, compileall, synthetic
  reproduction, private 23-photo smoke, and `git diff --check` pass. No commit
  was made.
- Next: T7f can proceed synthetically; T8c metric SfM waits on an overlapping
  photo reshoot with intermediate and doorway/connector views.

## 2026-09-09 — T7e metric video-pose sidecar complete

- Extended normalized video samples with their exact encoded frame indices and
  clip-relative decode timestamps; display rotation does not erase identity.
- Added `video_poses.py`, a strict versioned metre/camera-to-world parser with
  coordinate convention, increasing frame/time, finite-position, and unit-XYZW
  quaternion validation. Malformed sidecars fail structurally.
- Added `video_pose_alignment.py`. It fits an orientation-preserving 3D
  similarity per local VO segment only after at least three exact frame/time
  matches, rejects degenerate motion and >15 cm RMSE, and reports scale and
  aligned metric camera positions without yet claiming walls.
- Synthetic tests recover a known 0.4 m/unit transform and reject wrong units,
  duplicate frames, invalid quaternions, and 100 ms timestamp shifts. The two
  private MP4s have no sidecars, report `metric_alignment=not-available`, and
  remain structurally unsupported rather than receiving guessed scale.
- All 96 tests, Ruff, touched-file formatting, compileall, synthetic
  reproduction, private two-video no-sidecar smoke, and `git diff --check` pass.
  No commit was made.
- Next: T7f sparse triangulation/plane diagnostics for sidecar-aligned segments,
  or T8b photo overlap graph against the uploaded images.

## 2026-09-09 — T7d scale-free video trajectory complete

- Refactored ORB extraction, ratio matching, and seeded fundamental estimation
  into `video_features.py`, shared by the T7c gate and T7d pose algorithm.
- Added essential-matrix relative-pose recovery with an explicit image-size
  focal prior. Translation directions are normalized and remain unitless.
- Failed feature or pose edges close the active local trajectory. Later valid
  evidence restarts at a new identity anchor; disconnected segments are not
  mislabeled as globally relocalized.
- Added deterministic two-view pose, segment-break/restart, and short-input
  tests. Real results: my-room recovers 21/89 edges in 10 segments; pooja-room
  recovers 17/89 in 9. The CLI remains `unsupported_tier` because no validated
  metric scale or room geometry exists.
- Next: T7e validate a metric per-video pose sidecar and align only proven
  frame/timestamp correspondences before any FloorPlan output.
- All 89 tests, Ruff, touched-file formatting, compileall, synthetic
  reproduction, private two-video trajectory smoke, and `git diff --check` pass.
  No commit was made.

## 2026-09-09 — T7c video feature-track gate complete

- Added a separate immutable tracking policy and `video_tracks.py` algorithm. It analyzes at most 60 evenly spaced adjacent sample pairs, bounds frames to 640 px, caches ORB features, applies Hamming ratio matching, and uses seeded fundamental/homography RANSAC.
- Every pair records keypoint, match, fundamental-inlier, motion, homography-residual parallax, and convex-hull coverage evidence. Low yield, weak geometry, stationary motion, homography dominance/pure rotation, and poor coverage are counted as explicit rejection reasons; a video needs 35% eligible pairs.
- Added deterministic tests where two-depth translational motion passes, a homography-only rotation sequence fails for low parallax, and blank frames fail without crashing.
- Real diagnostics: my-room passes 23/60 pairs with median 1,166 keypoints, 262 matches, 178 F-inliers, 78.28 px motion, 1.15 px parallax, and 23.5% coverage. Pooja-room passes 27/60 with 1,188, 257, 190, 93.41 px, 1.23 px, and 20.6%.
- Both videos are eligible for the next relative-VO stage. This does not establish metric scale, wall dimensions, or the official ±3% gate; the CLI still returns structured `unsupported_tier` after reporting the evidence.
- All 86 tests, Ruff, touched-file formatting, compileall, synthetic reproduction, private two-video feature smoke, and `git diff --check` pass. No commit was made.
- Next: T7d scale-free relative pose chaining with explicit segment breaks/relocalization. Do not assign metres without a validated pose sidecar or known length.

## 2026-09-09 — T7b multi-video orientation-aware ingest complete

- Refactored video ingest around immutable `VideoMetadata` and `SampledVideo` records. Every sorted room walkthrough is now sampled; the filename stem remains its stable identity instead of silently selecting only the first file.
- Added a capture-independent quarter-turn image utility. OpenCV backend auto-rotation is disabled, container rotation is normalized within a configured tolerance and applied once, and native/display sizes are recorded. Unsupported metadata or failure to disable auto-rotation becomes a structured capture error.
- Added stem-specific pose-sidecar names for multi-video jobs. The old global names remain valid for one video but are reported as ambiguous when several walkthroughs exist.
- Real results at about 2 Hz: `my-room.mp4` → 138 upright 720×1280 RGB samples over 68.56 s; `pooja-room.mp4` → 148 over 73.91 s. OpenCV reports both as 90° clockwise. These are ingest diagnostics, not metric geometry.
- Added three tests for multi-video identity/sidecars, explicit rotation application, and invalid non-quarter-turn rejection. All 83 tests, Ruff, touched-file formatting, compileall, synthetic reproduction, private two-video smoke, and `git diff --check` pass. No commit was made.
- Next: T7c deterministic feature-track, match/inlier, parallax, and coverage diagnostics. Continue refusing centimetres until metric pose/scale evidence exists.

## 2026-09-09 — T6b3 Record3D partial FloorPlan complete

- Added vectorized segment coordinates, separate opening-profile configuration/algorithm, Record3D-specific uncalibrated measurements, and a dedicated FloorPlan converter. The LiDAR adapter now orchestrates these modules instead of ending in `unsupported_tier`.
- Door candidates require floor-reaching sparse wall evidence plus a surviving lintel; windows require a sparse middle band plus surviving sill and lintel. Width/height ranges, wall-end margins, and short interruption handling are configurable. A solid-wall regression emits zero openings.
- Each accepted archive now yields a metric room polygon, four interval-bearing walls, ceiling height, area, supported openings, and capture provenance. Separate archives retain exported world coordinates but remain explicitly unregistered; no adjacency or transform is invented.
- The private run now emits a schema-valid `partial` JSON/SVG with 3 rooms, 12 walls, and 4 candidates: a 65 cm door in my-room and 110 cm, 95 cm, and 60 cm doors in pooja-room. These labels and dimensions are algorithm outputs pending tape-backed verification, not scored accuracy claims.
- Suppressed duplicate disconnected-room warnings when the reconstruction already disclosed missing registration. Rendered and visually inspected the private SVG; the three disjoint rooms and four opening marks are legible.
- Added four focused tests across opening detection/conversion. All 80 tests, Ruff, touched-file formatting, compileall, synthetic reproduction, private JSON/SVG smoke, and `git diff --check` pass. No commit was made.
- Next: T7b multi-walkthrough ingest and display-rotation normalization. T6 calibration, repeatability, and shared-opening association wait for the connector/repeat/tape capture.

## 2026-09-09 — T6b2 Record3D room-plane candidates complete

- Added a dedicated Record3D plane-policy config and a pure geometry module with immutable horizontal-level, wall-plane, and room-candidate results.
- The algorithm finds strong floor/ceiling y bands around the camera path, keeps only x-z columns spanning at least 1.5 m vertically, searches Manhattan yaw in 0.5-degree steps, and selects wall peaks that bracket the central camera trajectory. It never uses raw cloud extrema as room dimensions.
- Added four public-safe synthetic tests covering a rotated 4 m × 3 m room, a second room scale, rejection of low furniture, missing-ceiling refusal, and non-finite input refusal.
- Wired candidate extraction into the production Record3D branch. Real diagnostics: drawing-room 3.05 × 3.80 m with 2.95 m ceiling; my-room 3.25 × 3.70 m with 2.92 m ceiling; pooja-room 3.65 × 2.90 m with 2.93 m ceiling. These are not accuracy claims because tape/laser truth is still absent.
- The CLI continues to emit a schema-valid structured failure after this stage; it explicitly says opening extraction and FloorPlan conversion remain.
- All 76 tests, Ruff, touched-file formatting, compileall, one-command synthetic reproduction, private three-scan smoke, and `git diff --check` pass. No commit was made.
- Next: T6b3 supported opening-gap extraction and interval-bearing FloorPlan conversion with per-scan provenance. Do not score centimetre gates before ground truth arrives.

## 2026-09-09 — T6b1 Record3D metric world clouds complete

- Added separate deterministic sampling, quaternion rotation, point-cloud configuration, and Record3D back-projection modules. Depth is filtered to 0.10–8 m at medium/high confidence, projected with RGB intrinsics scaled to depth resolution, transformed through normalized XYZW camera-to-world poses, and averaged into 2.5 cm voxels.
- Confirmed the convention against the official Record3D structs/source and the real captures: OpenGL negative-Z is camera forward; confidence is low=0, medium=1, high=2. The correct convention produces strong paired horizontal floor/ceiling bands on every scan; reversing Z does not.
- Real results from 61 sampled frames each: drawing-room 664,570 accepted depth pixels → 252,694 voxels in 2.32 s; my-room 644,372 → 224,435 in 2.28 s; pooja-room 677,189 → 260,653 in 2.45 s.
- Wired metric-cloud construction into the production LiDAR path. The private three-capture command completes in about 8 s and reports auditable frame/voxel/world-bound diagnostics, then remains a structured failure because bounds include furniture/outliers and are not room dimensions.
- Added four focused tests covering inclusive sampling, normalized XYZW rotation, negative-Z metric projection, camera translation, voxel bounds, and invalid config. Updated code map, format/research notes, ADR, README, device/compliance status, roadmap, and tasks.
- All 72 tests, Ruff, touched-file formatting, compileall, synthetic reproduction, private three-scan smoke, and diff checks pass. The private command's exit 2 is intentional until planes become FloorPlan geometry.
- `mytask.md` remains untouched as Harsh's untracked human-capture checklist.
- Next: T6b2 horizontal floor/ceiling detection and Manhattan wall-plane extraction for one room, with diagnostic rejection before FloorPlan conversion.

## 2026-09-09 — T6a real Record3D decode and validation complete

- Inventoried the partial private upload: three genuine Record3D `.r3d` room archives, 23 unique decodable JPEGs across three room folders (8/8/7), and two valid H.264 1280×720 walkthroughs lasting 68.56 s and 73.91 s. The JPEGs have no EXIF after WhatsApp transfer; both MP4s carry a -90° display transform.
- Filled the three gitignored private manifests so each job now passes the production loader. The capture remains incomplete: drawing-room video, connector/hallway, repeat capture, tape/laser truth, staged-damage evidence, and two-room incumbent output are missing.
- Added separate Record3D archive I/O, validation config, bounded validation algorithm, and LZFSE utility modules. The reader validates matched JPEG/depth/confidence indices, timestamps, seven-value poses, four-value per-frame intrinsics, dimensions, and exact decompressed byte counts.
- The portable path uses `python-lzfse`; macOS can use Compression.framework when the package is absent. Three representative frames per real archive decoded successfully.
- Real evidence: drawing-room 4,045 frames / 87.44% sampled valid depth; my-room 4,057 / 85.38%; pooja-room 4,235 / 97.23%. These are integrity numbers, not wall-accuracy claims.
- The CLI now reports exactly what Record3D evidence validated, then stops with structured `unsupported_tier` until T6b fuses points and extracts floor/wall/opening planes.
- Added four focused tests and `docs/formats/record3d.md`; updated dependencies, code map, ADR, capture-tier docs, device matrix, README, and tasks. All 68 tests, Ruff, compileall, synthetic reproduction, and diff checks pass.
- Next: T6b metric point-cloud fusion and single-room plane extraction. Do not start benchmark scoring until tape ground truth arrives.

## 2026-09-09 — T20b compliance structure locked

- Audited the complete 27-row compliance matrix against the shipped code and artifacts without changing capture-dependent accuracy claims.
- Corrected R11 from the undocumented status `implemented` to `done`; the schema and contract tests already require intervals on every scalar measurement.
- Added a structural regression test that requires R1–R27 exactly once, in order, using only the matrix’s allowed status vocabulary.
- Verified all 64 tests, Ruff, compileall, fix-loop hashes, the one-command synthetic reproduction, and diff checks. No commit was made.
- Remaining partial/missing rows genuinely require photo/video/LiDAR, tape, incumbent, or walk-in evidence. No further metric stage is honest before T3 capture; T21 separately needs full Xcode.

## 2026-09-09 — T17a Route 2 protocol handoff complete

- Audited the promised walk-in handoff against the production job loader. The route referred to a manifest template that did not exist and could be read as claiming raw Record3D compatibility that has not shipped.
- Added separate photos, video, and LiDAR job templates under `data/templates/`, plus a contract test that loads every template and enforces distinct job ids/tier directories.
- Reduced `docs/capture-route.md` to a 469-word operator card with exact copy commands, eight-photo sequence, continuous-video route, LiDAR export checklist, and an explicit RoomPlan-JSON-versus-raw-Record3D boundary.
- Revised the device matrix to separate capture eligibility, currently accepted runtime inputs, and unmeasured accuracy. No centimetre result was invented.
- Full Xcode remains unavailable (`xcode-select` points to Command Line Tools; `xcodebuild` requires Xcode), so T21 remains blocked.
- All 63 tests pass with external pytest plugin autoload disabled; Ruff, compileall, synthetic reproduction, fix-loop verification, and `git diff --check` pass. T17 remains `doing` only for T3 walk-in validation and measured intervals.

### Next

- Capture T3 using one template per tier. Inventory the files before implementing raw Record3D, video VO, or photo SfM.

## 2026-09-09 — T20a clean-environment reproduction complete

- A fresh Python 3.12 virtual environment exposed a real README bug: installing only `requirements.txt` left `python -m cozmo_floorplan` unavailable. Added the missing `pip install --no-deps -e .` step and verified the same environment resolves the package.
- Measured the existing-checkout rehearsal on macOS arm64: venv 1.63 s, requirements 19.35 s, editable install 2.22 s, then-current 57 tests 2.98 s, run 1.02 s, eval 0.77 s, and fix-loop verification 0.40 s; total 28.37 s. Pip cache/network caveats are recorded.
- Added `make reproduce-synthetic` backed by separate reproduction config, subprocess utility, artifact verifier, runner, and tests. It forces deterministic mode, expects eval exit 3, validates schema/entity counts/gate states, verifies fix-loop hashes, and returns 0 on the complete expected contract.
- Fixed the README eval example to pass an output directory, ignored generated `out/`, documented exact evidence in `docs/reproduction.md`, and updated code map/setup/compliance.
- The exact Make target passes; the full suite is now 59 tests. Ruff, compileall, fix-loop verification, and diff checks pass.
- No capture media is present beyond `data/private/takehome.md`; full Xcode is still unavailable. T20 remains `doing` until the real benchmark reproduction bundle and full compliance coverage exist.

## 2026-09-09 — T10 technical report engineering draft complete

- Replaced the report stub with a compact 1,805-word draft covering architecture, all three tier designs and devices, drift/ablation, error budget, calibration, claims-agent boundaries, the shipped fix loop, and hostile-scene failure modes.
- Measured statements are tied to `data/fix-loop/after/eval.json`: 8 walls at 0 cm synthetic median/p95 error, 1/1 opening, 2/2 ceilings, and 15/15 interval coverage at 95% declared confidence.
- The report explicitly labels those values as synthetic contract evidence, distinguishes the injected 20 → 0 cm drift regression from an already-aligned ablation, and does not claim phone accuracy.
- Real LiDAR, video, photo, repeatability, multi-room, incumbent, calibration, and timing rows remain visibly pending T3 rather than estimated.
- Next media-independent stage: T20 clean-machine README/reproduction pass. T10 remains `doing` until real tables replace the pending cells.

## 2026-09-09 — T19b fallback-status fix shipped

- Reviewed and committed the checksum-locked T19a baseline as `3317339`; all 52 then-current tests and required checks passed.
- Shipped the declared status policy as `68acdf6`: explicit, successfully completed deterministic fallback preserves `status: ok`, while automatic missing-key fallback, provider failure, invalid observations, and pre-existing partial runs remain degraded.
- Generated the immutable after FloorPlan/SVG/ablation/eval artifacts from that code checkpoint. The CLI moved exit 2 → 0 and `pipeline_yield` moved fail/partial → pass/ok exactly as predicted.
- Kept the audit warning, 7 tool calls, claims output, geometry, drift result, interval coverage, and every non-target eval gate unchanged. Added verifier enforcement and a readable delta in `data/fix-loop/diff.md`.
- Verified the complete bundle, all 57 tests, `ruff check .`, compileall, and `git diff --check`.
- Next: T10 technical-report draft without invented benchmark numbers; T3 capture remains the human blocker for metric photo/video/LiDAR evaluation.

## 2026-09-09 — T19a fix-loop before bundle frozen

- Selected the worst measured current failure: `pipeline_yield=fail` because explicit, complete offline claims fallback changes the one-job prediction from `ok` to `partial` (0/1 successful yield).
- Wrote `docs/fix-loop.md` with evidence, root-cause hypothesis, intended fix, and a precise prediction: status `partial` → `ok`, yield 0% → 100%, while geometry and calibration metrics remain unchanged.
- Pinned the baseline to commit `523ceea11ba1bb405e3bc1c922447d1f427a0333` and stored `floorplan.json`, SVG, drift-off JSON, and `eval.json` under `data/fix-loop/before/`.
- Added a manifest with expected exit codes and SHA-256 hashes, a verifier command, isolated-worktree reproduction instructions, and tamper tests.
- Verified the frozen bundle, all 52 tests, `ruff check .`, compileall, and diff checks. No commit was made.
- The fix is intentionally not implemented in T19a. Next reviewable stage is T19b: ship only the declared status-semantics fix, generate `after/`, and produce a readable diff.

## 2026-09-09 — TASKS: what can ship without media

- Added a **Without media** section and a **Needs media?** column so agents do not wait on T3 for T19 / T21 / writeup draft.
- Next without uploads: T19 freeze fix-loop before on the synthetic RoomPlan job. T6/T7 VO/T8 SfM/T17/T18/T11 stay blocked on `data/private/`.

## 2026-09-09 — T8a photo-folder ingest complete

- Added separate photo ingest config, immutable I/O records, reconstruction boundary, generated-JPEG tests, and a public job-format document.
- The loader discovers room folders deterministically, enforces 2–8 images per room, decodes each supported file, rejects corrupt/undersized evidence, and records pixel dimensions.
- Multi-room photo evidence now reaches a structured `unsupported_tier` boundary that states exactly what was validated. It does not invent centimetres before SfM, adjacency, and a declared scale source exist.
- Updated `docs/code-map.md`, compliance, README, capture-tier notes, data drop instructions, and `TASKS.md`. T8a is done; full T8 remains blocked on real T3 media for metric reconstruction and calibrated intervals.
- Verified 50 tests, `ruff check .`, compileall, and the combined diff against HEAD. No commit was made.
- Next media-independent stage: T19 freeze the regenerable fix-loop “before” bundle.

## 2026-09-08 — T9 shared-wall fix + T7 video ingest

- Context: Harsh adds photos/video/LiDAR tomorrow. Tonight: finish work that does not need those files. T9’s injected 20 cm gap was not actually closing.
- Done: walls now take the pose of their first listed room, so shared `a_east` stays with room A while exclusive `b_west` moves. Gap 20 → 0 on the synthetic mutation. Tests treat pytest `agent_fallback` as `partial` (exit 2) and assert geometry `ok` before claims enrichment. Video ingest samples generated MP4s, mentions `poses.json` when present, and fails `unsupported_tier` instead of inventing centimetres.
- Learned: `_dominant_pose` (first non-identity room) moved shared walls with the neighbor, so both opening frames translated together and residual stayed 20 cm. `COZMO_AGENT_MODE=fallback` in `tests/conftest.py` makes enriched `run_job` `partial`; do not assert `status==ok` on that path.
- Next: T3 capture into `data/private/`. Without files, T8 photo ingest. With a walkthrough, T7 metric VO. T21 needs Xcode.app.

## 2026-09-09 — T9 stitch and drift ablation complete

- Full Xcode is unavailable (`xcodebuild` points at CommandLineTools), so the requested fallback stage was T9 rather than T21.
- Preserved and completed the already-staged T9 work: separate SE(2) utilities, drift config, opening constraints, room-pose traversal, geometry application, correction orchestration, CLI ablation output, and tests. File ownership is recorded in `docs/code-map.md`.
- Normal multi-room runs plane-anchor shared opening frames and write `floorplan.ablation-off.json`; `--no-drift-correction` regenerates the poses-as-is result. Before/after opening-gap residuals are stored as interval-bearing measurements.
- Tightened accountability so a job with no usable opening constraints reports correction disabled/method `none` rather than claiming a no-op correction.
- A synthetic RoomPlan mutation injects 20 cm drift into the second room; correction reduces the shared-opening gap from 20 cm to 0 cm. This is algorithm plumbing evidence only, not a real-capture accuracy claim.
- Verified the focused T9 suite (8 tests). The current full suite passes 45 tests, but that count includes concurrent untracked T7 video work that appeared during final verification and was not reviewed as part of this stage. `ruff check .`, compileall, and staged/unstaged `git diff --check` pass. No commit was made.
- Next unblocked work without captures: T19 freeze the fix-loop “before” bundle. T3 remains the human priority; T21 requires full Xcode.

## 2026-09-08 — T16 agent + tools complete

- Implemented a live OpenAI Responses API tool loop plus deterministic fallback for damage, concealed-rule flags, and scope.
- Split configuration, prompts, strict tool definitions, tool execution, provider/fallback agents, observations, bounded image encoding, environment loading, and orchestration into focused modules documented in `docs/code-map.md`.
- Metric damage extents enter through `damage_observations.json`; the model cannot pass quantities to `apply_damage`. Concealed rule ids and scope actions are policy-validated, and scope quantity is copied by tools.
- Live mutations are transactional. Provider failure or incomplete tool use discards the working copy and replays the same tools through deterministic rules with an `agent_fallback` warning.
- Added two explicitly synthetic observations to the RoomPlan fixture. No real-image accuracy claim is made.
- Verified 34 tests, ruff, compileall, and `git diff --check`. A real configured-key smoke test completed through `gpt-5-mini` with 7 tool calls, 2 damage regions, 1 concealed flag, 2 scope lines, `store: false`, and no fallback warning.
- Next: T21 if Xcode is installed. T6 raw Record3D and real damage validation still wait on T3 capture.

## 2026-09-08 — T15 whole-property SVG renderer

- Completed a deterministic, accessible SVG product surface for FloorPlan v0.2.
- Added separate modules for immutable render configuration, centimetre-to-canvas layout, SVG composition, and paired artifact persistence; recorded their roles in `docs/code-map.md`.
- The `run` command now emits `floorplan.json` and `floorplan.svg` for `ok`, `partial`, and structured-failure results. The SVG never derives new measurements: wall labels and confidence intervals come directly from the IR.
- The drawing includes room polygons and labels, walls, openings, a 100 cm scale bar, run status, counts, capture tier, scale source, and a failed-run placeholder.
- Verified the two-room RoomPlan output through the real CLI and macOS Quick Look. Automated result: 30 tests pass; ruff and compileall pass.
- Next: T16 agent + tools. Keep T6 raw Record3D blocked until a real capture exists.

---

## 2026-09-08 — T6 RoomPlan path complete; raw Record3D blocked

- Context: T14 is committed; no private sensor capture exists yet. The guaranteed Route 2 uses Record3D, so the whole LiDAR task cannot honestly be called done.
- Done: implemented portable RoomPlan JSON v1 ingestion with separate typed parsing, transform projection, wall polygonization, LiDAR uncertainty config, measurement construction, and FloorPlan assembly. Added a two-room metric fixture and six LiDAR tests.
- Output: the fixture produces 2 rooms, 8 walls, an 80×210 cm shared door, areas, ceilings, adjacency, intervals, and provenance. Multi-room status remains `partial` because T9 drift correction is deliberately not faked.
- Boundaries: `.r3d`/metadata and USDZ are detected and return structured unsupported warnings. T6 is blocked on T3 for real Record3D depth/pose files and later hardening.
- Verified: `make test` passes 27 tests; `ruff check src tests` and compileall pass. The CLI output has 0 synthetic wall/area/opening error on the shared truth fixture; repeat, drift, incumbent, and yield remain red/missing honestly.
- Next unblocked engineering task: T15 whole-property SVG renderer using the RoomPlan output.

---

## 2026-09-08 — T14 official-gate eval harness complete

- Context: T13 was committed; T14 was the highest unblocked engineering task.
- Done: added a modular eval package, official threshold config, ID-first/Hungarian matching, measurement and geometry utilities, deterministic report models, validated input/output I/O, and the `eval` CLI subcommand.
- Gates: pipeline yield, openings including miss/phantom denominator, ceiling accuracy/spread, repeatability, drift on/off evidence, photo adjacency/overlap/footprint, photo/video wall error, interval calibration, and LiDAR head-to-head.
- Behavior: missing repeat/ablation/incumbent inputs are explicit `missing_evidence`; non-applicable tier gates are distinct; failed reports exit 3 and invalid inputs exit 1.
- Verified: `make test` passes 20 tests; compileall passes; the installed command wrote a deterministic red `eval.json` from the T13 empty prediction.
- Next: T6 LiDAR export → FloorPlan. Human T3 capture remains parallel and urgent.

---

## 2026-09-08 — T13 modular CLI stub complete

- Context: T12 was committed; T13 was the highest unblocked engineering task.
- Done: added an installable `src/cozmo_floorplan` package with separate config, errors, job I/O, schema validation, atomic output, FloorPlan factory, pipeline, utilities, and CLI modules. Added `docs/code-map.md` to explain every code file.
- Behavior: `python -m cozmo_floorplan run JOB --out OUT` now validates the job layout and always writes a schema-valid structured failure while reconstruction adapters are unavailable. It returns exit code 2 for this expected incomplete state rather than fabricating geometry or returning only a traceback.
- Verified: `make test` passes 12 tests; compileall passes; editable install succeeded in a clean temporary venv; the exact installed module command wrote a v0.2 `floorplan.json` with the expected exit code 2.
- Next: T14 red evaluation harness for the official gates. Do not implement recon inside the eval task.

---

## 2026-09-08 — T12 FloorPlan schema v0.2 complete

- Context: T12 was the highest unblocked engineering task and gates the CLI/eval work.
- Done: bumped the shared IR to 0.2.0; every scalar dimension now carries `{value, unit, interval}`; required top-level damage, concealed flags, and scope arrays; added typed surface references and drift-correction metadata.
- Verified: migrated the synthetic two-room fixture and added positive/negative contract tests. `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m pytest -q` passes 8 tests. Plain pytest currently collides with an unrelated installed plugin that also registers `--output`.
- Next: T13 job layout + structured-failure CLI stub, then T14 official-gate eval harness.

---

## 2026-09-08 — Session brief for a replacement agent

Wrote `docs/prompts/session-brief.md` (paste-ready product + score + stack + next task). Point a new chat at that file plus `AGENTS.md`.

---

## 2026-09-08 — LLM tool calling required (Applied AI)

### Context

Harsh: the role is applied AI; we will use AI tool calling / an API, not a geometry-only pipeline.

### Done

- `docs/agent-layer.md` + ADR. Recon = centimetres. Agent = damage/scope/rules via tools. Disclosed public API; fallback if no key. No Redis/our servers.
- T16 retargeted. `.env.example` lists `OPENAI_API_KEY`.

### Learned

- Packet allows pretrained APIs with disclosure and forbids **our** infrastructure. OpenAI/Anthropic is in. LLM must not invent wall lengths.

### Next

- T12 schema. Then recon. Then T16 agent.

---

## 2026-09-08 — Max-score retarget

### Context

Harsh: stop hedging LiDAR-only / skip-photos / skip-app. Initially target everything that scores; cut tomorrow or tomorrow night if needed.

### Done

- ADR + `docs/cut-later.md`. Updated plan, roadmap, TASKS (T21), product, HANDOFF, README, AGENTS, capture protocol (8 photos, iPhone 17 Pro), eval gates, architecture, capture-route, cursor rules.
- Ingest leftover README/AGENTS status lines fixed (prompt is present).

### Learned

- Score policy is **full-score attempt**. Build order remains schema → LiDAR → stitch → video → photos. That is not a scope cut.
- Route 2 stays the guaranteed walk-in; Route 1 is parallel until 10-min install exists.
- Fix loop: freeze **before** as soon as eval exists.

### Next

- Code: **T12** schema. Human: **T3** capture on iPhone 17 Pro.

---

## 2026-09-08 — iPhone 17 Pro has LiDAR

- Harsh’s phone is an **iPhone 17 Pro**. GSMArena lists a rear **TOF 3D LiDAR scanner**. All three take-home tiers can run on this device. Walk-in may still be a non-Pro iPhone 15+ (photos/video only).
- Noted in `docs/device-matrix.md`.

---

## 2026-09-08 — Round 2 scoring vs app vs Round 1 reuse

### Context

Harsh asked: can Round 2 be maxed by implementing everything; is an iOS app required in Round 2; can Round 1 work be folded in later.

### Done

- Explained from `docs/takehome.md` only. No Round 1 packet exists in this repo.

### Learned (trust these)

- This packet *is* Round 2. It inherits the full Round 1 output contract and gates, then adds own-capture, three mandatory tiers, five extra gates, walk-in, fix loop, head-to-head.
- An iOS app is optional (Route 1). Route 2 is explicitly legitimate. App is 5% of score at most (capture route quality).
- Implementing every contract field does **not** certainly max the score: 30% is a cold walk-in; 15% is physics on their reproduction; 10% is beating magicplan/Polycam; 25% is a shipped fail→pass fix, not feature completeness.
- Round 1 *pipeline* (JSON contract, damage, scope, renderer, one command) is the Round 2 core and should be integrated now, not later. A Round 1 *app* can wait or be skipped.

### Next

- Ingest still pending. Capture on Harsh’s phone.

---

## 2026-09-08 — Explained official take-home (no ingest)

### Context

Harsh added the official Cozmo case study to `docs/takehome.md` and asked for an explanation: one route vs both, what each route requires, which is easier in <48 hours.

### Done

- Read the prompt. Did not implement reconstruction. Did not run full ingest (`docs/prompts/ingest-takehome.md`) because the asked deliverable was explanation.
- Marked T1 done. T4 (reconcile plan) is now unblocked but still todo.

### Learned (trust these; do not re-derive)

- Capture routes are **XOR**: Route 1 (own iOS app) **or** Route 2 (stock App Store tool + one-page protocol). Not both.
- Input tiers are **AND**: photos, video, and LiDAR are all mandatory, including photo-tier whole-property stitch from per-room folders.
- They provide **no captures**. You build the benchmark (3+ rooms + connector, furnished room with two damage classes, all three tiers on the same rooms, one repeat capture, laser/tape GT).
- Walk-in test is 30% of score; fix loop is 25%. Attachments: none (no published JSON schema in the packet).
- Route 2 is the 48-hour choice. Route 1 needs TestFlight/dev install on *their* phone in <10 minutes.

### Next

- Run ingest (`docs/prompts/ingest-takehome.md`): ADR, rescope `TASKS.md`/`plan.md`, extend schema for damage/scope/intervals.
- Human: pick Route 2, capture the benchmark set tonight if hardware exists (iPhone 15+; Pro for LiDAR).

---

## 2026-09-07 — Orchestration kit from an empty repo

### Context

Cloud Agent run on `github.com/harshsinha-12/assignment-cozmo` (private). User asked to spend the leftover session budget on README, `plan.md`, `roadmap.md`, `update.md`, and anything else needed to orchestrate later agents. Official take-home problems are **not** in the repo yet. Original files:

- `README.md` — `# assignment-cozmo`
- `discussion.md` — one-sentence problem
- `url.md` — `https://www.hellocozmo.ai/`
- `AI Backend Engineer\n.docx.pdf` — Brynz JD (filename contains a newline; 2 pages)

### Done

- Extracted the PDF with PyMuPDF; cleaned text lives in `docs/job-brief.md`; binary copy at `docs/briefs/ai-backend-engineer.pdf`.
- Wrote agent contract, handoff, plan, roadmap, setup, schema, capture protocol, research notes, interview notes.
- Added `.cursor/environment.json` + `requirements.txt` so the next Cloud Agent can install a small Python CV stack.
- Added paste-ready prompts under `docs/prompts/` and a human `START-TOMORROW.md`.
- Added FloorPlan JSON Schema + `data/fixtures/synthetic_two_room/` + `tests/test_schema.py`.

### Learned (trust these; do not re-derive)

- **Company.** Cozmo AI is a YC company (site says W25 in the JD; YC page also shows W22 / founded 2025 — treat branding as messy, not important). HQ San Francisco, role in-office New York 996 per the JD. Product: AI workforce for P&C claims. Agents answer the call, capture the loss, write into Xactimate/Cotality, dispatch contractors, draft estimates from field photos. Customers: restoration franchisors, TPAs, adjusting firms. Site: https://www.hellocozmo.ai/ — also `/see` for vision (photos, video, documents). Founders: Alok Kumar (CEO), Nuha Hashem (CTO). Recruiter: Brynz, saik@brynz.io, https://www.brynz.tech.
- **Role.** Title on the PDF: AI Backend Engineer. User’s note calls it Applied AI Engineer. JD emphasis: production agents (prompts, tools, routing, evals, fallbacks), reverse-engineering legacy claims software, data layer as moat, forward-deployed in customer ops, Python or TypeScript, 0–4 years, new grads OK. Interview: shortlist → **takehome** → technical discussion → culture fit → offer.
- **Problem we actually have.** Only this sentence: turn phone camera captures into dimensioned, stitched floor plans with cm-level accuracy across three input tiers (photos, video, LiDAR).
- **Physics.** Monocular SfM (COLMAP etc.) recovers structure **up to similarity** — no metric scale. Scale needs LiDAR/depth, known poses, IMU/VO, GPS (useless indoors), or a known length (door, tape, ceiling). Claiming cm-level from uncalibrated homeowner stills without a prior is a disqualifying mistake.
- **LiDAR on this VM.** Apple RoomPlan `CapturedRoom` is Codable: walls/doors/windows/openings/objects with dimensions in metres and 4×4 transforms. Multi-room merge is `StructureBuilder` / `CapturedStructure` (iOS 17+). Export JSON/USDZ on device; process on Linux. Do not try to compile RoomPlan here.
- **Claims output shape.** Xactimate consumes sketches; magicplan’s integration exports **ESX** (not a public nice JSON). We should emit a clean FloorPlan IR. Writing `.esx` is out of scope unless the prompt requires it.
- **Cloud Agent env.** This run’s environment is personal/runtime-forward-fill, no finished environment builds, egress not restricted. A committed `.cursor/environment.json` will override dashboard envs for future runs.

### Next

- Wait for or paste the official take-home into `docs/takehome.md`.
- Unblocked: synthetic fixture + optional real-room capture (`docs/capture-protocol.md`).
- Do not start the reconstruction implementation.

### Files added (map)

See `README.md` for the map. Do not delete the original PDF even though the filename is hostile; a clean copy exists under `docs/briefs/`.
