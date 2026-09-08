# Setup

How a human or a Cloud Agent gets a machine that can work this repo.

There is **no application to boot** yet. Setup means: Python, a few CV libraries, ffmpeg when we start touching video, and a clear split between what runs in Linux vs what must happen on an iPhone.

## Local (laptop)

```bash
git clone git@github.com:harshsinha-12/assignment-cozmo.git
cd assignment-cozmo
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
make test
```

Python 3.11 or 3.12. System packages you will want before video work:

```bash
# Debian/Ubuntu
sudo apt-get update
sudo apt-get install -y ffmpeg libgl1
```

`opencv-python-headless` is pinned in `requirements.txt` so Cloud Agents do not pull a GUI OpenCV.

Optional later (not in the default install — they are large or fussy):

| Extra | Why | When to add |
| --- | --- | --- |
| `open3d` | Point clouds, plane fit | LiDAR PLY/PCD or dense recon |
| COLMAP | Production-grade SfM | Photos tier, if apt/binary is available |
| `pillow-heif` | iPhone HEIC | When fixtures include `.heic` |
| `pycolmap` | Python bindings | If COLMAP is already in the image |
| PyTorch | Learned detectors | Only if the official prompt forces it |

Do not add these to `requirements.txt` until a task needs them. Cloud Agent `install` should stay fast.

## Cloud Agents (Cursor)

Committed config: `.cursor/environment.json`.

That file **overrides** personal/team dashboard environments for new runs. Keep `install` idempotent and short. Do not start servers in `install`. There is nothing to put in `start` or `terminals` until a demo API exists.

This repository’s first Cloud Agent run (2026-09-07) booted from a personal environment with **no finished environment builds**. After this PR lands, new agents on this branch should pip-install from `requirements.txt`.

If an agent needs a heavier stack (COLMAP, Open3D):

1. Add the dependency in a follow-up commit.
2. Put slow OS packages in a Dockerfile under `.cursor/` rather than in `install`.
3. Do not `apt-get install colmap` on every boot “to be safe.”

Secrets: none required for the planned classical pipeline. If the official prompt requires a model API, put the key in Cloud Agent secrets and read it from the environment in code. Never commit `.env`. Template: `.env.example`.

## What cannot run here

| Thing | Where it runs | What Linux gets |
| --- | --- | --- |
| Apple RoomPlan / ARKit LiDAR session | iPhone/iPad Pro | `CapturedRoom` JSON, USDZ, optional mesh |
| ARCore recording | Android | Pose + optional depth sidecars |
| Tape measure | Physical room | Numbers in `manifest.yaml` |
| Xactimate desktop | Windows estimate machine | We emit IR, not ESX, unless the prompt says otherwise |

## Phone capture kit (human)

See `docs/capture-protocol.md`. Minimum useful kit:

- Any smartphone for photos + video
- iPhone 12 Pro or newer (or iPad Pro with LiDAR) for the third tier
- A tape measure or a known door height
- Good lighting, overlapping frames, walk the doorway

## Make targets

```text
make setup    # create .venv and install requirements
make test     # pytest
make fmt      # no-op until a formatter is chosen
```

## Sanity checks after setup

```bash
python -c "import numpy, cv2, shapely, yaml; print('ok', cv2.__version__)"
which ffmpeg || echo 'ffmpeg missing (only needed for video)'
```

## If setup fails

- Headless OpenCV import error about `libGL.so.1` → install `libgl1` or stay on `opencv-python-headless`.
- HEIC fails → `pillow-heif` or convert on the phone to JPEG before upload.
- Cloud Agent install timeout → you put COLMAP/Open3D in the default requirements. Revert.
