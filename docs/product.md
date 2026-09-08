# What we are building

This is not a website, not a hosted app, and not a magicplan clone with accounts. Round 2 is a **local capture-to-plan pipeline** plus a **one-page phone protocol**. Cozmo runs it on their laptop at the defense.

Canonical prompt: `docs/takehome.md`. **Score policy:** pass every official row. Cut only tomorrow night (`docs/cut-later.md`). Capture: Route 2 protocol always ready; Route 1 app in parallel (`TASKS.md` T21).

---

## One sentence

A field phone captures a property (photos, a video, or LiDAR). One command on a laptop turns that folder into a **dimensioned, stitched floor plan** plus **damage/scope JSON** a claims agent could consume.

---

## What the user (adjuster / Cozmo interviewer) does

```text
1. Follow docs/capture-route.md on an iPhone 15+ (Camera + named LiDAR logger).
2. Copy the files into a job folder (one folder per capture; photos are one folder per room).
3. On a clean machine:

     python -m cozmo_floorplan run path/to/job --out path/to/out

4. Open:
     out/floorplan.json     structured plan + damage + scope + intervals
     out/floorplan.svg      the product surface: whole-property drawing
     out/report.md          optional human summary
```

That is the entire product surface. No login. No cloud of ours. No React app unless time is leftover and the JSON already works.

---

## What the software does

| Stage | What happens |
| --- | --- |
| Ingest | Read the job folder. Detect tier (photos / video / LiDAR) from `manifest.yaml` and files. |
| Reconstruct | Build per-room walls, openings, ceiling height, floor area. LiDAR uses depth+poses; video uses the walkthrough; photos use 2–8 stills with **no** depth or poses. |
| Stitch | Place rooms next to each other through doors/hallways. Correct drift. Do not leave a pile of disconnected rectangles. |
| Damage / scope | Agent calls tools (vision + rules). Concealed flags cite **rule ids**. Scope qty from geometry. LLM does not invent wall cm. |
| Calibrate | Every number gets a confidence interval. Intervals **widen** as sensors thin (LiDAR tight, video medium, photos widest). |
| Render | One whole-property plan a homeowner would recognise from Polycam / magicplan. |
| Eval | Compare to tape/laser ground truth. Print gate table. |

Same JSON schema from every tier. Same command. Same renderer. **Agent + tools** fill damage/scope (Applied AI). Geometry stays classical. That is the Cozmo-shaped part.

---

## What we are not building

- A website or SaaS (does not score)
- User accounts, a queue, Redis, or our own servers (forbidden: “runs without calling your infrastructure”). A **disclosed public LLM API** is in-scope.
- Xactimate `.esx` export
- A photoreal 3D tour

A Route 1 iOS capture app **is in scope** until a tomorrow-night cut. The walk-in always has Route 2 as backup. If a static HTML page later displays the SVG, that is a viewer, not the product.

---

## How they test it

Three exams, in this order of score:

### 1. Walk-in (30%) — live, cold

At the technical discussion they take **their** iPhone 15 or newer into a space you have never seen. They pick photos, video, or LiDAR that day. They follow `docs/capture-route.md` **literally**. You run the one command on that folder (their `OPENAI_API_KEY` or the tool fallback). They laser the room while it runs and score your JSON/SVG against those measurements on the spot. All three tiers must be ready. If the protocol is ambiguous, the capture you get is your fault.

### 2. Fix loop (25%) — your benchmark, before vs after

You capture the specified property yourself. You run the pipeline. You write a one-page declaration of the **worst failing gate**, the cause, the fix, and the predicted number. You ship the fix. They regenerate **before** and **after** from raw files plus a readable diff. Analysis with no code change is zero.

### 3. Reproduction + paper (the rest)

On a clean machine, from the repo + raw benchmark:

- 15-minute README to first successful `run`
- Compliance matrix: every requirement → file → artifact → status (10%)
- Gate table at all three tiers, repeatability, head-to-head vs Polycam or magicplan on two LiDAR rooms (15% + 10%)
- Capture protocol quality (5%)
- Git history that looks like a person built it (5%)
- Technical report, **max 6 pages**

They do **not** grade a URL. They grade a command, a JSON, a drawing, and a live room.

---

## What you personally do vs what the code does

| You (human) | The pipeline |
| --- | --- |
| Capture 3+ rooms + hallway, all three tiers, tape/laser GT | Turn those folders into JSON + SVG |
| Stage two damage classes in one furnished room | Detect / rule-flag damage and emit scope lines |
| Recapture one room at the same tier | Repeatability table |
| Export Polycam or magicplan on two rooms | Head-to-head table |
| Write the one-page protocol they will follow | Survive their walk-in capture |
| Commit as you go | Stay regenerable |

---

## Device reality

- Harsh’s capture phone: **iPhone 17 Pro** (TOF LiDAR) — all three tiers.
- Walk-in photos/video: any iPhone 15 or newer (may be non-Pro).
- Walk-in LiDAR: only if **they** have a Pro. Protocol and pipeline must still be ready.
- Submit `docs/device-matrix.md` with **measured** intervals after eval, targeting every official gate.
