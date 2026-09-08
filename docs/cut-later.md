# Cut later (not now)

Harsh’s rule 2026-09-08: **target maximum score on every official row.** Do not pre-concede photos, openings, or the iOS app. This file is the ordered **defer list for tomorrow night**, if and only if calendar time is gone.

Until then, agents treat every `todo` in `TASKS.md` as in-scope.

## Never cut (these *are* the score)

| Weight | Keep even if ugly |
| --- | --- |
| 30% | Walk-in: all three tiers run cold, JSON+SVG, intervals; agent fallback if no API key |
| 25% | Fix loop: frozen before, shipped fix, regenerable after |
| 15% | Benchmark numbers on **photos, video, and LiDAR** |
| 10% | Compliance: damage, concealed+rule, scope, CIs, one command, renderer |
| 10% | Head-to-head vs Polycam/magicplan |
| 5% | Capture route they can follow in 10 minutes |
| 5% | Commit history |
| (role) | Disclosed LLM **tool calling** for damage/scope (`docs/agent-layer.md`) — Harsh required |

## Cut last → first (tomorrow night only)

1. Pretty SVG polish / optional HTML viewer  
2. Extra damage classes beyond two  
3. Chasing ≤2 cm openings on **photos** after LiDAR already passes that gate (photo wall gate is ±8%)  
4. Route 1 iOS/TestFlight app if Route 2 protocol already works  
5. Video ±3% last centimetre after the tier produces a stitched plan  
6. Multi-storey / stairs as geometry (warn instead)

Do **not** cut the agent layer down to “rules only with no API path” unless the walk-in machine cannot have a key **and** time is gone — even then keep the **tool interface** so the write-up still shows an agent.

## Do not cut these thinking they are optional

- Photo-tier **whole-property stitch** (named gate)  
- Drift ablation (named auto-fail if skipped)  
- Repeatability capture (do it at LiDAR; also recapture photos/video if time)  
- Concealed-damage **rule ids**  
- Device matrix with measured intervals  
- Tool-calling agent (or identical tools in fallback)

## Not on the scoreboard (never start)

Website/SaaS, accounts, Redis/Postgres, **our** servers, ESX, training a foundation model. Public LLM API is allowed.
