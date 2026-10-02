"""Helpers the exploration and the search share."""

from __future__ import annotations

import math
from typing import Mapping


def objective_value(
    name: str, objective_key: str, params: Mapping[str, object], output: object
) -> float:
    """The value to rank one evaluation by.

    Raises `RuntimeError` if the result is not a mapping
    or lacks `objective_key`.
    Raises it as well if the value there does not convert to a float
    or is not finite.
    The message names what came back and at which point.
    """
    if not isinstance(output, Mapping):
        raise RuntimeError(
            f"{name}: objective returned {output!r} at {params}; "
            f"expected a mapping carrying an {objective_key!r} key"
        )
    if objective_key not in output:
        raise RuntimeError(
            f"{name}: objective returned keys {sorted(output)} "
            f"at {params}, with no {objective_key!r} among them"
        )

    try:
        value = float(output[objective_key])
    except (TypeError, ValueError) as e:
        raise RuntimeError(
            f"{name}: {objective_key!r} was {output[objective_key]!r} "
            f"at {params}, which is not a float"
        ) from e

    if not math.isfinite(value):
        raise RuntimeError(
            f"{name}: {objective_key!r} was {value} at {params}; "
            "a non-finite value can be neither ranked nor modelled"
        )

    return value


def floor_power_of_two(n: int) -> int:
    """The largest power of two <= n.

    Raises `ValueError` if `n` is below 1.
    """
    if n < 1:
        raise ValueError(f"expected a positive integer, got {n}")
    return 1 << (n.bit_length() - 1)


def index_width(count: int) -> int:
    """Digits needed to number `count` things, so that the numbers sort."""
    return len(str(max(count - 1, 0)))


def format_param(value: object) -> str:
    """Render one value for a progress line, floats to six significant digits."""
    return f"{value:.6g}" if isinstance(value, float) else str(value)


def format_mapping(mapping: Mapping[str, object]) -> str:
    """Render a whole mapping for a progress line."""
    return ", ".join(f"{k}={format_param(v)}" for k, v in mapping.items())
