# Start here (human)

Official prompt is in. We are targeting **max score**. Cuts only tomorrow night (`docs/cut-later.md`).

## Tomorrow (you)

Capture (`docs/capture-protocol.md`). Drop the files in gitignored `data/private/` — folder map in `data/README.md`.

1. 3+ rooms + hallway on the **iPhone 17 Pro**
2. Photos (8 JPEGs per room, folders), one walkthrough video, LiDAR (Record3D)
3. Repeat one room at LiDAR (second scan)
4. Stage two damage types in one furnished room
5. Tape/laser walls, doors, ceilings
6. Polycam or magicplan export on two rooms (not our capture app)

## Code (agent / you in Cursor)

T9 stitch is done. T7 samples video but does not invent centimetres. Next without files: T8 photo ingest. After capture: T7 VO, T8 SfM, T6 Record3D.

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
make test
```

## Read (15 minutes)

`docs/product.md` → `plan.md` → `TASKS.md` → `docs/cut-later.md`
