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
