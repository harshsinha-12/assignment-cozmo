"""Read Record3D `.r3d` archives without inferring floor-plan geometry."""

from __future__ import annotations

import json
import math
from collections.abc import Callable
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path, PurePosixPath
from typing import Any
from zipfile import BadZipFile, ZipFile

import numpy as np
from PIL import Image, UnidentifiedImageError

from cozmo_floorplan.errors import ReconstructionError
from cozmo_floorplan.utils.lzfse import LzfseDecodeError, decompress_lzfse

LzfseDecoder = Callable[[bytes], bytes]


@dataclass(frozen=True, slots=True)
class Record3DMetadata:
    """Validated camera metadata required to fuse Record3D frames later."""

    color_width_px: int
    color_height_px: int
    depth_width_px: int
    depth_height_px: int
    fps: float
    timestamps_s: tuple[float, ...]
    poses: tuple[tuple[float, ...], ...]
    intrinsics: tuple[tuple[float, ...], ...]

    @property
    def frame_count(self) -> int:
        return len(self.poses)


@dataclass(frozen=True, slots=True)
class Record3DCapture:
    """One indexed Record3D archive and its validated metadata."""

    source: Path
    metadata: Record3DMetadata
    frame_indices: tuple[int, ...]


@dataclass(frozen=True, slots=True)
class Record3DFrame:
    """One decoded RGB-D frame in sensor-native coordinates."""

    index: int
    color_size_px: tuple[int, int]
    depth_m: np.ndarray
    confidence: np.ndarray


def discover_record3d_archives(lidar_dir: Path) -> tuple[Path, ...]:
    """Return `.r3d` files in a stable order."""

    return tuple(sorted(lidar_dir.glob("*.r3d"), key=lambda path: path.name.lower()))


def load_record3d_capture(path: Path) -> Record3DCapture:
    """Validate archive structure and metadata without decoding every frame."""

    try:
        with ZipFile(path) as archive:
            names = archive.namelist()
            _reject_unsafe_names(names, path)
            try:
                raw_metadata = json.loads(archive.read("metadata"))
            except KeyError as exc:
                raise ReconstructionError(
                    f"Record3D archive {path.name!r} has no metadata entry."
                ) from exc
    except (BadZipFile, OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ReconstructionError(
            f"Could not read Record3D archive {path.name!r}: {exc}"
        ) from exc

    metadata = _parse_metadata(raw_metadata, path)
    frame_indices = _validate_frame_index(names, metadata.frame_count, path)
    return Record3DCapture(source=path, metadata=metadata, frame_indices=frame_indices)


def read_record3d_frame(
    capture: Record3DCapture,
    index: int,
    *,
    decoder: LzfseDecoder | None = None,
) -> Record3DFrame:
    """Decode one matched JPEG, float32-depth, and uint8-confidence frame."""

    if index not in capture.frame_indices:
        raise ReconstructionError(
            f"Record3D frame {index} does not exist in {capture.source.name!r}."
        )
    metadata = capture.metadata
    depth_size = metadata.depth_width_px * metadata.depth_height_px * 4
    confidence_size = metadata.depth_width_px * metadata.depth_height_px
    try:
        with ZipFile(capture.source) as archive:
            color_payload = archive.read(f"rgbd/{index}.jpg")
            depth_payload = archive.read(f"rgbd/{index}.depth")
            confidence_payload = archive.read(f"rgbd/{index}.conf")
        with Image.open(BytesIO(color_payload)) as image:
            image.verify()
            color_size = image.size
        depth_bytes = _decode_payload(decoder, depth_payload, depth_size)
        confidence_bytes = _decode_payload(decoder, confidence_payload, confidence_size)
    except (
        BadZipFile,
        KeyError,
        OSError,
        UnidentifiedImageError,
        LzfseDecodeError,
    ) as exc:
        raise ReconstructionError(
            f"Could not decode Record3D frame {index} in {capture.source.name!r}: {exc}"
        ) from exc

    expected_color_size = (metadata.color_width_px, metadata.color_height_px)
    if color_size != expected_color_size:
        raise ReconstructionError(
            f"Record3D frame {index} JPEG is {color_size}; expected {expected_color_size}."
        )
    depth = np.frombuffer(depth_bytes, dtype="<f4").reshape(
        metadata.depth_height_px,
        metadata.depth_width_px,
    )
    confidence = np.frombuffer(confidence_bytes, dtype=np.uint8).reshape(
        metadata.depth_height_px,
        metadata.depth_width_px,
    )
    return Record3DFrame(
        index=index,
        color_size_px=color_size,
        depth_m=depth,
        confidence=confidence,
    )


def _decode_payload(
    decoder: LzfseDecoder | None,
    payload: bytes,
    expected_size: int,
) -> bytes:
    if decoder is None:
        return decompress_lzfse(payload, expected_size=expected_size)
    decoded = decoder(payload)
    if len(decoded) != expected_size:
        raise LzfseDecodeError(
            f"LZFSE decoded {len(decoded)} bytes; expected exactly {expected_size}."
        )
    return decoded


def _parse_metadata(value: Any, path: Path) -> Record3DMetadata:
    if not isinstance(value, dict):
        raise ReconstructionError(
            f"Record3D metadata in {path.name!r} must be an object."
        )

    width = _positive_int(value, "w", path)
    height = _positive_int(value, "h", path)
    depth_width = _positive_int(value, "dw", path)
    depth_height = _positive_int(value, "dh", path)
    fps = _positive_float(value, "fps", path)
    timestamps = _number_rows(value, "frameTimestamps", 1, path)
    poses = _number_rows(value, "poses", 7, path)
    intrinsics = _number_rows(value, "perFrameIntrinsicCoeffs", 4, path)
    counts = {len(timestamps), len(poses), len(intrinsics)}
    if len(counts) != 1 or not poses:
        raise ReconstructionError(
            f"Record3D metadata arrays in {path.name!r} must be non-empty and equal length."
        )
    return Record3DMetadata(
        color_width_px=width,
        color_height_px=height,
        depth_width_px=depth_width,
        depth_height_px=depth_height,
        fps=fps,
        timestamps_s=tuple(row[0] for row in timestamps),
        poses=poses,
        intrinsics=intrinsics,
    )


def _positive_int(value: dict[str, Any], key: str, path: Path) -> int:
    item = value.get(key)
    if not isinstance(item, int) or isinstance(item, bool) or item <= 0:
        raise ReconstructionError(
            f"Record3D metadata field {key!r} in {path.name!r} must be a positive integer."
        )
    return item


def _positive_float(value: dict[str, Any], key: str, path: Path) -> float:
    item = value.get(key)
    if not isinstance(item, (int, float)) or isinstance(item, bool) or item <= 0:
        raise ReconstructionError(
            f"Record3D metadata field {key!r} in {path.name!r} must be positive."
        )
    return float(item)


def _number_rows(
    value: dict[str, Any],
    key: str,
    width: int,
    path: Path,
) -> tuple[tuple[float, ...], ...]:
    rows = value.get(key)
    if not isinstance(rows, list):
        raise ReconstructionError(
            f"Record3D metadata field {key!r} in {path.name!r} must be an array."
        )
    if width == 1:
        rows = [[item] for item in rows]
    parsed: list[tuple[float, ...]] = []
    for row in rows:
        if not isinstance(row, list) or len(row) != width:
            raise ReconstructionError(
                f"Record3D metadata field {key!r} in {path.name!r} has invalid rows."
            )
        if any(
            not isinstance(item, (int, float))
            or isinstance(item, bool)
            or not math.isfinite(float(item))
            for item in row
        ):
            raise ReconstructionError(
                f"Record3D metadata field {key!r} in {path.name!r} must contain numbers."
            )
        parsed.append(tuple(float(item) for item in row))
    return tuple(parsed)


def _validate_frame_index(
    names: list[str],
    frame_count: int,
    path: Path,
) -> tuple[int, ...]:
    expected = set(range(frame_count))
    for suffix in ("jpg", "depth", "conf"):
        found: set[int] = set()
        for name in names:
            if not name.startswith("rgbd/") or not name.endswith(f".{suffix}"):
                continue
            try:
                found.add(int(PurePosixPath(name).stem))
            except ValueError as exc:
                raise ReconstructionError(
                    f"Record3D archive {path.name!r} has a non-numeric frame name {name!r}."
                ) from exc
        if found != expected:
            missing = sorted(expected - found)[:3]
            extra = sorted(found - expected)[:3]
            raise ReconstructionError(
                f"Record3D archive {path.name!r} has mismatched {suffix} frames "
                f"(missing={missing}, extra={extra})."
            )
    return tuple(range(frame_count))


def _reject_unsafe_names(names: list[str], path: Path) -> None:
    for name in names:
        parts = PurePosixPath(name).parts
        if name.startswith("/") or ".." in parts:
            raise ReconstructionError(
                f"Record3D archive {path.name!r} contains an unsafe member path."
            )
