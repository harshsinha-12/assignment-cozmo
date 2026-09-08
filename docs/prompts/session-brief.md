# Paste-ready session brief (2026-09-08)

Give this whole file to a new agent if the previous chat died. Then follow `AGENTS.md` → `HANDOFF.md` → `TASKS.md`.

Official prompt (verbatim): `docs/takehome.md` (also `data/private/takehome.md`).

---

You are continuing **assignment-cozmo**, Harsh’s Cozmo AI (YC) take-home for **AI Backend / Applied AI Engineer**. Company: hellocozmo.ai, property claims OS. Recruiter: Brynz.

## What we are building (the product)

**Not a website, not Redis, not our servers, not magicplan.**

A **local Python CLI**:

```text
python -m cozmo_floorplan run path/to/job --out path/to/out
```

Phone folder in → `floorplan.json` (dimensioned stitched plan + damage + concealed-damage **rule ids** + scope + confidence intervals) + `floorplan.svg` (whole-property drawing).

Capture is **Route 2** (submit one route): iPhone Camera for photos/video; **Record3D** for LiDAR (depth+poses+intrinsics). One-pager they follow literally: `docs/capture-route.md` (exactly 8 JPEGs per room). Route 1 iOS app is **parallel T21** only; switch scored route iff 10-minute install exists.

Harsh’s phone: **iPhone 17 Pro** (TOF LiDAR). Walk-in may be non-Pro (photos/video only).

## How they score / test

| Weight | What |
| --- | --- |
| 30% | Walk-in: their iPhone 15+, their capture, our command, their laser. All 3 tiers ready. |
| 25% | Fix loop: worst failing gate, shipped fix, regenerable before/after |
| 15% | Benchmark accuracy all 3 tiers |
| 10% | Compliance matrix |
| 10% | Beat/tie Polycam or magicplan on ≥70% shared LiDAR dims, 2 rooms |
| 5% | Capture route quality |
| 5% | Git history (commit as you go; one dump at deadline = 0) |

They provide **no captures**. We build: 3+ rooms + hallway, all 3 tiers, two staged damage classes, repeat LiDAR scan, tape/laser GT.

**Gates (all pass targets — do not pre-concede):** openings ≤2 cm on ≥85% (miss/phantom = miss); ceiling ≤1.5 cm (recapture spread ≤1 cm); repeatability 1 cm or 0.5%/wall; drift ablation (poses-as-is = auto-fail); photo folders stitch, no overlap, footprint ±8%; photo walls ±8% with calibrated intervals; video walls ±3%.

**Score policy:** max every official row. Cuts only tomorrow night via `docs/cut-later.md`. LiDAR-first is **build order**, not scope.

## Architecture / stack

```text
job dir → normalizer → recon (LiDAR | video | photos) → FloorPlan numbers
       → stitch + drift fix
       → LLM agent + tools (damage, concealed rules, scope)
       → JSON + SVG + eval
```

- Python 3.11+, `requirements.txt`: numpy, opencv-headless, shapely, pillow, scipy, pyyaml, jsonschema, pytest, matplotlib. ffmpeg for video.
- **No** Redis, Postgres, S3, FastAPI, React, our GPU/proxy.
- Deploy = their laptop, 15 min README. Prompt: no calling **our** infrastructure.

## Applied AI layer (required)

`docs/agent-layer.md`. Disclosed OpenAI-compatible or Anthropic **tool calling**.

- LLM **must not** invent centimetres. Tools return recon numbers.
- LLM **does**: damage class (vision crops), `fire_concealed_rule`, `add_scope_line` (qty from geometry).
- `OPENAI_API_KEY` in `.env` (never commit). If missing/fail: **same tools**, rule fallback. Walk-in must not crash.

## Next work

**Code:** T12 schema and T13 CLI stub are complete. Next: T14 red eval for official gates. Then T6 LiDAR, T15 SVG, T9 stitch+ablation, T7 video, T8 photos, T16 agent.

**Human (Harsh):** T3 capture tonight (`docs/capture-protocol.md`).

**Do not:** website; ESX; LLM-guessed wall lengths; skip photos/video; fake cm; re-scrape hellocozmo.ai; re-extract the Brynz PDF; implement RoomPlan on Linux (ingest JSON/USDZ only).

End every session: update `HANDOFF.md`, append `update.md`, tick `TASKS.md`. Commit on existing branch.

State TASK id, then execute **one** unblocked task.
