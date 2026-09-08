# Decisions (ADR-lite)

Newest first. One decision per heading. Do not silently reverse a decision in code.

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
