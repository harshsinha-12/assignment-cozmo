# assignment-cozmo

Take-home workspace for **Cozmo AI** — converting phone captures into **dimensioned, stitched floor plans**.

This repository is currently an **orchestration kit**. The official assignment prompt is not here yet. Planning, agent instructions, setup, and a frozen FloorPlan schema are. Reconstruction code is intentionally not.

| Field | Value |
| --- | --- |
| Company | [Cozmo AI](https://www.hellocozmo.ai/) |
| Role | AI Backend Engineer (JD); user note also says Applied AI Engineer |
| Recruiter | Brynz — saik@brynz.io |
| Problem we have | Photos / video / LiDAR → metric stitched floor plan, cm-level where physics allows |
| Official prompt | Missing — paste into [`docs/takehome.md`](docs/takehome.md) |
| Agent contract | [`AGENTS.md`](AGENTS.md) |
| Current handoff | [`HANDOFF.md`](HANDOFF.md) |

## Start here

**Human (you, tomorrow):**

1. If the take-home email arrived, paste it into `docs/takehome.md` and start a Cursor agent with [`docs/prompts/ingest-takehome.md`](docs/prompts/ingest-takehome.md).
2. If it did not, you can still capture a room ([`docs/capture-protocol.md`](docs/capture-protocol.md)) or leave the next agent on [`TASKS.md`](TASKS.md). Shorter checklist: [`START-TOMORROW.md`](START-TOMORROW.md).
3. Do not start from a blank chat. Point the agent at this repo and the kickoff prompt: [`docs/prompts/agent-kickoff.md`](docs/prompts/agent-kickoff.md).

**Agent:**

Read [`AGENTS.md`](AGENTS.md) → [`HANDOFF.md`](HANDOFF.md) → latest [`update.md`](update.md) → [`TASKS.md`](TASKS.md) → [`docs/takehome.md`](docs/takehome.md). Stop. Then do the top unblocked task.

## Repo map

| File | Role |
| --- | --- |
| `AGENTS.md` | Operating contract for Cursor agents |
| `HANDOFF.md` | What the last session left behind |
| `update.md` | Append-only log (research cache) |
| `plan.md` | Technical plan (provisional) |
| `roadmap.md` | Phased work, including what *not* to build |
| `TASKS.md` | Queue |
| `SETUP.md` | Local + Cloud Agent environment |
| `docs/takehome.md` | **Paste official prompt here** |
| `docs/job-brief.md` | Extracted Brynz JD |
| `docs/problem.md` | What we know vs what we are guessing |
| `docs/architecture.md` | System sketch |
| `docs/capture-tiers.md` | Photos / video / LiDAR methods |
| `docs/eval-and-accuracy.md` | How we will prove cm |
| `docs/research.md` | Libraries, papers, APIs (already researched) |
| `docs/claims-domain.md` | Why Cozmo cares (Xactimate, restoration) |
| `docs/capture-protocol.md` | How to shoot fixtures on a phone |
| `docs/open-questions.md` | Unknowns |
| `docs/decisions.md` | ADRs |
| `docs/interview-prep.md` | Technical discussion |
| `docs/schemas/floorplan.schema.json` | Intermediate representation |
| `docs/prompts/` | Paste-ready agent prompts |
| `.cursor/environment.json` | Cloud Agent install |
| `requirements.txt` | Python deps for later implementation |
| `data/fixtures/` | Ground-truth jobs (empty except README) |
| `src/` | Reserved for the package |

Original drop (kept):

- `discussion.md` — original one-line problem
- `url.md` — company URL
- `AI Backend Engineer\n.docx.pdf` — JD with a newline in the filename; prefer `docs/briefs/ai-backend-engineer.pdf`

## Current status

**Phase 0 complete. Synthetic fixture exists. Phase 1 blocked on the official prompt.**

See [`roadmap.md`](roadmap.md). Unblocked without the prompt: fixtures and a real-room capture.

## Setup (short)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
make test
```

Full notes, Cloud Agent caveats, and why LiDAR capture cannot happen in this VM: [`SETUP.md`](SETUP.md).

## Design in one paragraph

One FloorPlan intermediate representation for all tiers. LiDAR maps into it almost directly (Apple `CapturedRoom`). Video uses poses or visual odometry plus a scale source. Photos use SfM and **must not fake metric scale**. Rooms stitch through doorways as an SE(2) pose graph. Everything carries provenance. Eval reports wall error in centimetres on fixtures, not vibes.

## Ground rules for later code

- Python 3.11+ (3.12 is fine).
- Deterministic jobs: same `job/` directory in, same JSON out.
- Tests must run headless (OpenCV headless wheels, no GUI).
- No centimetre claims without numbers.
