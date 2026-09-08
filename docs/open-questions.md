# Open questions

Answered items are struck. Remaining items go in the 6-page report if still unknown at submit.

## Assignment logistics

- [x] Timebox — Harsh: submit in < 48 hours; defense/walk-in later
- [ ] Submit via email, GitHub, recording, or live demo (repo is private GitHub)
- [x] Private GitHub — this repo already is
- [x] Internet / APIs — allowed with disclosure; **must not** call our infrastructure; walk-in needs a local path
- [x] Fixtures — they provide **none**; we build the specified benchmark

## Input contract

- [x] File types — photos JPEG/HEIC, video MP4/MOV, LiDAR JSON/USDZ/PLY + poses/intrinsics
- [x] Whole floor — 3+ rooms + connector; photo folders per room must stitch
- [x] Multi-storey — not required; warn if detected
- [x] All three tiers in **code**, not design-only
- [x] LiDAR must include depth, poses, intrinsics; photos explicitly **no** poses

## Output contract

- [ ] Schema mandated? Packet says “published schema”; **nothing attached**. We extend `docs/schemas/floorplan.schema.json` until they send one.
- [x] Rendered plan required (SVG)
- [x] ESX / SKX / DXF — not asked; out
- [x] Accuracy — official gate table in `docs/eval-and-accuracy.md`

## Constraints

- [x] Language — Python (JD: Python or TypeScript)
- [x] Banned libraries — none named; pretrained OK with disclosure
- [ ] Docker / their VM — unspecified; README 15 min on a clean machine
- [ ] Max runtime per job — unspecified; walk-in runs live while they laser

## Product

- [x] Damage overlay — **required**
- [x] Concealed-damage rules — **required** (rule that fired)
- [x] Scope line items — **required**
- [x] HITL UI — not asked; skip
- [ ] Room names from vision vs manifest — unspecified; manifest labels OK, vision later if time
