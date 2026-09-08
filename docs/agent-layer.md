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
