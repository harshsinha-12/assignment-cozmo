# Open questions

Answer these when the official prompt arrives. Anything still open at submission time should appear in the write-up as a limitation, not a surprise.

## Assignment logistics

- [ ] Timebox and deadline
- [ ] Submit via email, GitHub, recording, or live demo
- [ ] Whether a private GitHub is acceptable (this repo is already private)
- [ ] Whether internet / paid APIs are allowed during the attempt
- [ ] Whether they provide fixtures

## Input contract

- [ ] File types (JPEG, HEIC, MP4, MOV, USDZ, JSON, PLY)
- [ ] One room or whole floor
- [ ] Multi-storey
- [ ] Must we support all three tiers in code, or design + one implemented tier?
- [ ] Sidecar poses / IMU?

## Output contract

- [ ] Schema mandated?
- [ ] SVG/PDF required?
- [ ] ESX / SKX / DXF?
- [ ] Accuracy number they will grade (e.g. ≤ 5 cm)

## Constraints

- [ ] Languages (JD says Python or TypeScript — default Python)
- [ ] Banned libraries
- [ ] Must run in Docker / their VM
- [ ] Max runtime per job

## Product

- [ ] Names of rooms from vision vs `manifest.yaml`
- [ ] Furniture
- [ ] Damage overlay
- [ ] Human-in-the-loop correction UI

## When a question is answered

Move the answer into `docs/takehome.md` (quote) and `docs/decisions.md` (interpretation). Strike it here.
