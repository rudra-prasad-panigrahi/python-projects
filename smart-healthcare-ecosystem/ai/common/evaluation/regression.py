from __future__ import annotations

from typing import Any

from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
)


def evaluate_regression(
    y_true: list[float],
    y_pred: list[float],
) -> dict[str, Any]:
    if len(y_true) != len(y_pred):
        raise ValueError("y_true and y_pred must have equal length.")

    mse = mean_squared_error(
        y_true,
        y_pred,
    )

    return {
        "mae": float(
            mean_absolute_error(
                y_true,
                y_pred,
            )
        ),
        "mse": float(mse),
        "rmse": float(mse**0.5),
        "r2": float(
            r2_score(
                y_true,
                y_pred,
            )
        ),
    }