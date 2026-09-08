# Agent layer (Applied AI)

Harsh 2026-09-08: this take-home must include **LLM tool calling / an AI API**, matching the AI Backend / Applied AI role. Geometry still does not come from the model.

Prompt allows “any pretrained model, dataset or API with disclosure” and forbids calling **our** infrastructure. OpenAI (or compatible) is a third party, disclosed in the write-up.

## Split of labour

| Layer | Owns | Must not do |
| --- | --- | --- |
| Classical recon | Walls, openings, ceiling, area, stitch, centimetres, intervals | Call an LLM to invent a length |
| Agent + tools | Damage class, concealed-damage **which rule**, scope wording, photo evidence routing | Overwrite a wall length without a tool that reads recon |

The model never types `342` as a wall length. It calls `get_wall(id)` and copies the tool result into the JSON.

## Runtime (still one CLI)

```text
recon → FloorPlan (numbers) → agent loop (tools + vision) → FloorPlan (damage/scope filled)
```

`python -m cozmo_floorplan run JOB --out OUT`

- If `OPENAI_API_KEY` (or `ANTHROPIC_API_KEY`) is set: live tool-calling agent + vision on damage crops.
- If unset or the API fails: **same tools**, rule-based fallback (JD: fallbacks). Geometry still emits. Walk-in does not crash.

Do not stand up our own GPU box or proxy. Weights/API are theirs or a public provider.

## Tools (v0)

| Tool | Returns | Side effect |
| --- | --- | --- |
| `get_plan` | rooms, walls, openings, stitch | none |
| `get_surface` | one wall/room + area/length + interval | none |
| `list_frames` | image paths for a room | none |
| `classify_damage` | class + bbox/extent proposal from a crop (vision) | none until apply |
| `apply_damage` | validated region on a surface | writes `damage[]` |
| `fire_concealed_rule` | rule id + evidence fields | writes `concealed_flags[]` |
| `add_scope_line` | qty from geometry × class | writes `scope[]` |

Invalid tool args → structured error, agent retries. Final JSON must still pass the schema.

## Disclosure (write-up)

- Provider + model name + that numbers come from tools
- Cached model outputs OK if deterministic replay + live path exists (prompt)
- Cost/rate limits: batch, timeout, fallback

## Eval

Agent quality is scored on damage/scope/concealed **contract**, not on chatting. Geometry gates stay classical eval vs tape.

## Implemented T16 runtime

The live path uses the OpenAI Responses API with `gpt-5-mini` by default, strict function definitions, sequential calls, stateless replay, and `store: false`. `COZMO_AGENT_MODEL` and `OPENAI_BASE_URL` are configurable. Official API references: [Responses create](https://developers.openai.com/api/reference/cli/resources/responses/methods/create) and [GPT-5 Mini](https://developers.openai.com/api/docs/models/gpt-5-mini).

`damage_observations.json` is the metric proposal boundary documented in `docs/formats/damage-observations.md`. The model cannot pass an extent to `apply_damage`; extra arguments are rejected. `fire_concealed_rule` accepts only the policy rule for the applied class, and `add_scope_line` copies its quantity from the stored damage extent.

Live calls mutate a private copy. A timeout, provider error, invalid tool sequence, or incomplete run discards that copy and reruns the deterministic agent through the same `FloorPlanTools`. Audit mode, provider, model, and successful tool-call count are appended to provenance. Tests force fallback mode even when a developer has a key in `.env`.
