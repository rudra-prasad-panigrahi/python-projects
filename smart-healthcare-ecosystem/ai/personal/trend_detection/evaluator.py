from __future__ import annotations

from sklearn.metrics import accuracy_score


def evaluate_direction(
    expected: list[str],
    predicted: list[str],
) -> float:
    if len(expected) != len(predicted):
        raise ValueError(
            "Expected and predicted lengths must match."
        )

    if not expected:
        return 1.0

    return float(
        accuracy_score(
            expected,
            predicted,
        )
    )