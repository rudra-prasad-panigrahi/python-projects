from __future__ import annotations

import numpy as np
from scipy.stats import ks_2samp


def kolmogorov_smirnov_drift(
    reference: list[float],
    current: list[float],
    alpha: float = 0.05,
) -> dict[str, float | bool]:
    if not reference:
        raise ValueError("Reference data cannot be empty.")

    if not current:
        raise ValueError("Current data cannot be empty.")

    statistic, p_value = ks_2samp(
        np.asarray(reference, dtype=float),
        np.asarray(current, dtype=float),
    )

    return {
        "statistic": float(statistic),
        "p_value": float(p_value),
        "drift_detected": bool(
            p_value < alpha
        ),
        "alpha": float(alpha),
    }