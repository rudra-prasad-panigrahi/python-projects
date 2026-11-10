from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TrendResult:
    direction: str
    slope: float
    r_squared: float
    strength: str


def classify_trend(
    slope: float,
    r_squared: float,
) -> TrendResult:
    if abs(slope) < 1e-9:
        direction = "stable"
    elif slope > 0:
        direction = "increasing"
    else:
        direction = "decreasing"

    if r_squared >= 0.75:
        strength = "strong"
    elif r_squared >= 0.40:
        strength = "moderate"
    else:
        strength = "weak"

    return TrendResult(
        direction=direction,
        slope=slope,
        r_squared=r_squared,
        strength=strength,
    )