# Paste-ready: official take-home just arrived

Use this when Harsh pastes an email, PDF, Notion doc, or GitHub issue that *is* the assignment.

---

The official Cozmo take-home is now available. Your job this session is **ingest and rescope**, not a heroic implementation.

1. Write the full prompt verbatim into `docs/takehome.md` (replace the empty fenced block, keep the file’s instructions above it). Store extra files under `docs/briefs/` or `data/` as appropriate. If the user attached binaries, put them in `data/inbox/` and describe them in `docs/takehome.md`.
2. Read `plan.md`, `roadmap.md`, `docs/open-questions.md`, and `docs/schemas/floorplan.schema.json`.
3. Produce a short diff:
   - Requirements the official prompt adds
   - Requirements it removes or contradicts
   - Timebox and submission format
   - Input/output contract (file types, schema, accuracy target)
   - Libraries they ban or require
4. Update `docs/decisions.md` with one ADR: “Official prompt vs provisional plan.”
5. Rewrite `TASKS.md` so the next session can implement without re-reading the prompt. Kill tasks that the prompt makes irrelevant.
6. Update `HANDOFF.md` and `update.md`.
7. Only if time remains **and** the prompt is small (≤ a few hours of work) start Phase 2 (schema freeze + red eval). Do not jump to photos-tier SfM.

Do not start training models. Do not build a web app unless the prompt requires a UI. Do not claim you have centimetre accuracy.

When ingest is done, the README status line should no longer say the prompt is missing.
