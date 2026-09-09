"""Deterministic sampling helpers shared by capture adapters."""


def evenly_spaced_indices(total: int, requested: int) -> tuple[int, ...]:
    """Return stable inclusive indices without duplicates."""

    if total <= 0 or requested <= 0:
        return ()
    count = min(total, requested)
    if count == 1:
        return (0,)
    return tuple(
        round(position * (total - 1) / (count - 1)) for position in range(count)
    )
