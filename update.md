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
