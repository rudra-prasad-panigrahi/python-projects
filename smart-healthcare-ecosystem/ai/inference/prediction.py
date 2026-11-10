from __future__ import annotations

from typing import Any


def safe_probability(
    probability: Any,
) -> float:
    value = float(probability)

    if not 0.0 <= value <= 1.0:
        raise ValueError(
            "Probability must be between 0 and 1."
        )

    return value