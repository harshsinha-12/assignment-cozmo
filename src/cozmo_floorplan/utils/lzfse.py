"""Portable LZFSE decompression for Record3D payloads."""

from __future__ import annotations

import ctypes
import ctypes.util
import sys
from collections.abc import Callable


class LzfseDecodeError(RuntimeError):
    """Raised when an LZFSE payload cannot be decoded exactly."""


def decompress_lzfse(payload: bytes, *, expected_size: int) -> bytes:
    """Decode one LZFSE block using python-lzfse or macOS Compression.framework."""

    if expected_size <= 0:
        raise ValueError("expected_size must be positive")

    decoder = _python_lzfse_decoder()
    if decoder is not None:
        try:
            decoded = decoder(payload)
        except Exception as exc:
            raise LzfseDecodeError("python-lzfse rejected the payload.") from exc
    elif sys.platform == "darwin":
        decoded = _decode_with_apple_compression(payload, expected_size)
    else:
        raise LzfseDecodeError(
            "No LZFSE decoder is available. Install the 'lzfse' Python package."
        )

    if len(decoded) != expected_size:
        raise LzfseDecodeError(
            f"LZFSE decoded {len(decoded)} bytes; expected exactly {expected_size}."
        )
    return decoded


def _python_lzfse_decoder() -> Callable[[bytes], bytes] | None:
    try:
        import lzfse  # type: ignore[import-not-found]
    except ImportError:
        return None
    return lzfse.decompress


def _decode_with_apple_compression(payload: bytes, expected_size: int) -> bytes:
    library_name = (
        ctypes.util.find_library("compression") or "/usr/lib/libcompression.dylib"
    )
    try:
        library = ctypes.CDLL(library_name)
    except OSError as exc:
        raise LzfseDecodeError("Could not load macOS Compression.framework.") from exc

    decode = library.compression_decode_buffer
    decode.argtypes = [
        ctypes.c_void_p,
        ctypes.c_size_t,
        ctypes.c_void_p,
        ctypes.c_size_t,
        ctypes.c_void_p,
        ctypes.c_uint32,
    ]
    decode.restype = ctypes.c_size_t

    source = ctypes.create_string_buffer(payload)
    destination = ctypes.create_string_buffer(expected_size)
    compression_lzfse = 0x801
    written = decode(
        destination,
        expected_size,
        source,
        len(payload),
        None,
        compression_lzfse,
    )
    if written == 0:
        raise LzfseDecodeError(
            "macOS Compression.framework rejected the LZFSE payload."
        )
    return destination.raw[:written]
