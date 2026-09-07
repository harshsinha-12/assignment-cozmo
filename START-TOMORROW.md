# Start tomorrow (human, 5 minutes)

You do not need to re-read the whole repo. Do **one** of these.

## A. The take-home email arrived

1. Open `docs/takehome.md` and paste the full prompt (and timebox).
2. Start a Cursor Cloud Agent on this repo with the text in `docs/prompts/ingest-takehome.md`.
3. Attach extra PDFs/zips if they sent data.

Do not start coding in a blank chat.

## B. Still no prompt, but you have 20 minutes

Capture one room: `docs/capture-protocol.md`.

Tape two walls and a door. Photos + a short video. LiDAR JSON if you have an iPhone Pro. Keep faces out of git.

## C. Still no prompt, you only have a Cloud Agent

Kickoff prompt: `docs/prompts/agent-kickoff.md`.

It should build on the synthetic fixture (`data/fixtures/synthetic_two_room/`) or wait. It must **not** start COLMAP.

## D. You want to run what exists locally

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
make test
```

Expected: schema tests pass. There is no reconstructor yet. That is correct.

## Reading if you are curious (20 minutes)

`README.md` → `plan.md` → `docs/eval-and-accuracy.md` → `docs/interview-prep.md`

Skip `docs/job-brief.md` unless you need the JD again. Skip hellocozmo.ai; it is already summarized in `docs/context.md`.
