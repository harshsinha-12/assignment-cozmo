"""Build bounded local image inputs for the public vision API."""

import base64
import mimetypes
from pathlib import Path

from cozmo_floorplan.agent.models import DamageObservation

MAX_AGENT_IMAGES = 8
MAX_IMAGE_BYTES = 8 * 1024 * 1024
SUPPORTED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}


def image_inputs(job_root: Path, observations: tuple[DamageObservation, ...]) -> list[dict[str, str]]:
    """Encode referenced images under the job directory; ignore URIs and missing files."""

    inputs: list[dict[str, str]] = []
    seen: set[Path] = set()
    image_count = 0
    root = job_root.resolve()
    for observation in observations:
        for reference in observation.evidence_refs:
            path = _safe_local_path(root, reference)
            if path is None or path in seen:
                continue
            mime_type = mimetypes.guess_type(path.name)[0]
            if mime_type not in SUPPORTED_IMAGE_TYPES:
                continue
            try:
                if path.stat().st_size > MAX_IMAGE_BYTES:
                    continue
                encoded = base64.b64encode(path.read_bytes()).decode("ascii")
            except OSError:
                continue
            inputs.extend(
                (
                    {"type": "input_text", "text": f"Evidence image: {reference}"},
                    {"type": "input_image", "image_url": f"data:{mime_type};base64,{encoded}"},
                )
            )
            seen.add(path)
            image_count += 1
            if image_count >= MAX_AGENT_IMAGES:
                return inputs
    return inputs


def _safe_local_path(root: Path, reference: str) -> Path | None:
    if "://" in reference:
        return None
    candidate = (root / reference.split("#", 1)[0]).resolve()
    try:
        candidate.relative_to(root)
    except ValueError:
        return None
    return candidate if candidate.is_file() else None
