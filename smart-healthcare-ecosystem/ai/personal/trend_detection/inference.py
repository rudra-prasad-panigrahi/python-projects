from __future__ import annotations

from typing import Any

from .features import (
    prepare_series,
    regression_features,
)
from .model import classify_trend


def analyze_trend(
    timestamps: list[str],
    values: list[float],
    metric_name: str,
) -> dict[str, Any]:
    series = prepare_series(
        timestamps,
        values,
    )

    features = regression_features(
        series
    )

    result = classify_trend(
        features["slope"],
        features["r_squared"],
    )

    latest_val = series[-1][1]
    first_val = series[0][1]

    # Calculate change
    absolute_change = latest_val - first_val
    percent_change = (absolute_change / first_val * 100.0) if abs(first_val) > 1e-9 else 0.0

    return {
        "metric": metric_name,
        "direction": result.direction,
        "strength": result.strength,
        "slope": round(result.slope, 6),
        "r_squared": round(result.r_squared, 4),
        "latest_value": round(latest_val, 2),
        "first_value": round(first_val, 2),
        "min_value": round(features["min"], 2),
        "max_value": round(features["max"], 2),
        "mean_value": round(features["mean"], 2),
        "absolute_change": round(absolute_change, 2),
        "percent_change": round(percent_change, 2),
        "observation_count": len(series),
        "method": "Ordinary Least Squares & Trend Classification",
        "model_version": "1.0.0-prototype",
        "informational_note": (
            f"An {result.direction} statistical trend was detected across {len(series)} observations. "
            "Trend detection identifies statistical movement in recorded measurements and does not establish a medical diagnosis."
        ),
    }