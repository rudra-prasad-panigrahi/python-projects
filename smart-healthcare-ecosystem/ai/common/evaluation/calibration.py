from __future__ import annotations

from sklearn.metrics import brier_score_loss


def brier_score(
    y_true: list[int],
    probabilities: list[float],
) -> float:
    if len(y_true) != len(probabilities):
        raise ValueError(
            "y_true and probabilities must have equal length."
        )

    return float(
        brier_score_loss(
            y_true,
            probabilities,
        )
    )