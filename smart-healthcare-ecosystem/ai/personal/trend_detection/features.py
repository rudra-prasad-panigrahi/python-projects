from __future__ import annotations

import math
from datetime import datetime
from typing import Any


def parse_timestamp(ts: str) -> float:
    try:
        # Handle ISO formatted strings
        cleaned = ts.replace("Z", "+00:00")
        return datetime.fromisoformat(cleaned).timestamp()
    except Exception:
        # Fallback to numeric or index
        try:
            return float(ts)
        except Exception:
            return 0.0


def prepare_series(
    timestamps: list[str],
    values: list[float],
) -> list[tuple[float, float, str]]:
    if len(timestamps) != len(values):
        raise ValueError("timestamps and values must have equal length.")

    if not values:
        raise ValueError("At least one measurement is required.")

    valid_pairs = []
    for ts, val in zip(timestamps, values):
        if val is None:
            continue
        try:
            num_val = float(val)
            parsed_ts = parse_timestamp(ts)
            valid_pairs.append((parsed_ts, num_val, str(ts)))
        except (ValueError, TypeError):
            continue

    if not valid_pairs:
        raise ValueError("No valid measurements remain after cleaning.")

    # Sort by timestamp
    valid_pairs.sort(key=lambda item: item[0])
    return valid_pairs


def regression_features(
    series: list[tuple[float, float, str]],
) -> dict[str, float]:
    n = len(series)
    if n < 2:
        return {
            "slope": 0.0,
            "r_squared": 0.0,
            "mean": float(series[0][1]) if series else 0.0,
            "min": float(series[0][1]) if series else 0.0,
            "max": float(series[0][1]) if series else 0.0,
        }

    # Use index 0..n-1 for step-based regression or normalized time
    x = [float(i) for i in range(n)]
    y = [float(item[1]) for item in series]

    x_mean = sum(x) / n
    y_mean = sum(y) / n

    numerator = sum((xi - x_mean) * (yi - y_mean) for xi, yi in zip(x, y))
    denominator_x = sum((xi - x_mean) ** 2 for xi in x)
    denominator_y = sum((yi - y_mean) ** 2 for yi in y)

    if denominator_x <= 1e-12:
        slope = 0.0
    else:
        slope = numerator / denominator_x

    if denominator_x * denominator_y <= 1e-12:
        r_squared = 0.0
    else:
        r = numerator / math.sqrt(denominator_x * denominator_y)
        r_squared = min(1.0, max(0.0, r ** 2))

    return {
        "slope": float(slope),
        "r_squared": float(r_squared),
        "mean": float(y_mean),
        "min": float(min(y)),
        "max": float(max(y)),
    }