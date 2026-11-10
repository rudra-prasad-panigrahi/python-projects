from __future__ import annotations

from typing import Any

from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)


def evaluate_classification(
    y_true: list[int],
    y_pred: list[int],
    y_probability: list[float] | None = None,
) -> dict[str, Any]:
    if len(y_true) != len(y_pred):
        raise ValueError("y_true and y_pred must have equal length.")

    result: dict[str, Any] = {
        "accuracy": float(
            accuracy_score(y_true, y_pred)
        ),
        "precision": float(
            precision_score(
                y_true,
                y_pred,
                zero_division=0,
            )
        ),
        "recall": float(
            recall_score(
                y_true,
                y_pred,
                zero_division=0,
            )
        ),
        "f1": float(
            f1_score(
                y_true,
                y_pred,
                zero_division=0,
            )
        ),
        "confusion_matrix": confusion_matrix(
            y_true,
            y_pred,
        ).tolist(),
    }

    if y_probability is not None:
        if len(y_probability) != len(y_true):
            raise ValueError(
                "y_probability must have same length as y_true."
            )

        # ROC-AUC only applies when both classes exist.
        if len(set(y_true)) == 2:
            result["roc_auc"] = float(
                roc_auc_score(
                    y_true,
                    y_probability,
                )
            )

    return result