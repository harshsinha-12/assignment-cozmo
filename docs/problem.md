# Problem

## Official requirements (Round 2)

Quoted from `docs/takehome.md`. We target **all** of these.

1. Own capture from the phone onward. One route: iOS app **or** stock protocol (we keep both tracks; submit one).
2. Three tiers, all mandatory: photos (2–8 stills, no depth/poses, per-room folders that still stitch), video, LiDAR (depth+poses+intrinsics on Pro).
3. Output per capture: dimensioned rooms (walls, ceiling, area, openings), stitched whole-property plan, damage regions, concealed-damage flags with rule ids, scope line items, CI on every measurement, one command, JSON, rendered plan.
4. Self-built benchmark: 3+ rooms + connector, staged two-class damage, all tiers, repeat capture, tape/laser GT.
5. Named gates: openings, ceiling, repeatability, drift ablation, photo stitch; photo ±8% / video ±3% walls with calibrated intervals.
6. Head-to-head vs Polycam or magicplan on 2 LiDAR rooms, ≥70% beat/tie.
7. Fix loop 25%: declaration, shipped fix, regenerable before/after.
8. Walk-in 30%: their iPhone 15+, their capture, our command, their laser.
9. No calling our infrastructure. Cover mirrors, glass, wet-look, low light.

## Confirmed product shape

Not a website. A **local pipeline** plus a capture protocol. See `docs/product.md`.

## Still open

- Exact deadline / submit channel (GitHub assumed; this repo is private)
- Cozmo “published schema” was not attached
- Round 1 gate list beyond the five additions
- Whether their walk-in phone is Pro (LiDAR) or not

## Non-goals (do not score)

- Photoreal 3D tour, ESX, training a foundation model, SaaS/accounts

## Success

Every compliance cell filled. Gate table filled by tier. Walk-in command runs. Fix loop regenerable. Intervals honest when a gate is missed.
